#!/usr/bin/env python3
"""Merge batch labels and the reviewed calibration set; add machine fields (response delay, late-answer flag)."""
import csv, glob, json, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'analysis/oznacevanje'
CAPTURE = date(2026, 9, 29)
LATE_DAYS = 30
LATE_TEXT = re.compile(r'minilo že dalj časa|najverjetneje že obravnavan|ali je (glede .{0,40})?še vedno težava|ponovno oddate pobudo|obžalujemo pozen odgovor|nismo mogli odgovoriti v predvidenem roku', re.I)
BOILER = re.compile(r'Spoštovani!?,?|Zahvaljujemo se (vam )?za (posredovano sporočilo|vaše sporočilo|vašo pobudo)\.?|Hvala za (vašo pobudo|posredovano sporočilo)\.?|Posredujemo vam odgovor gospoda župana:|Prijazen pozdrav\.?|Lep pozdrav,?.*$|Mestna občina Ljubljana.*$', re.S)
VAGUE = re.compile(r'preverili bomo|preverimo|bomo preverili|dodatno preverili|po potrebi|skladno s pristojnostmi|skladno z možnostmi|v okviru (svojih )?pristojnosti|posredoval|obvestili|odstopili|predali v reševanje|naročili, da preverijo', re.I)
CONCRETE = re.compile(r'naročil[ie]? (smo )?(že )?(popravilo|sanacijo|obrez|namestitev|postavitev|zamenjavo)|bomo (obrezali|namestili|postavili|sanirali|zamenjali|dopolnili|zagotovili|odstranili)|uvrstili|v plan del|nadzor', re.I)

FIELDS = ['id', 'vrsta', 'obseg', 'lokacija', 'koga', 'varnost', 'izvajalec', 'stanje', 'relevanca', 'dokaz', 'besedilo_ponovitev', 'zadeva', 'tema', 'gotovost', 'opomba']

records = {r['id']: r for r in json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())}
labels = {}
for f in sorted(glob.glob(str(D / 'paketi/paket_*_oznake.json'))):
    for l in json.loads(Path(f).read_text()):
        l['id'] = int(l['id']); labels[l['id']] = {**l, 'vir': 'strojno'}

prop = {p['id']: p for p in json.loads((D / 'kalibracija_50_predlog.json').read_text())}
zad = json.loads((D / 'kalibracija_50_zadeve.json').read_text())
for f in glob.glob(str(D / 'pregled_db/pregled/*.json')):
    doc = json.loads(Path(f).read_text()); rev = doc.get('data', doc); i = int(rev['id']); p = prop[i]
    l = {k: rev.get(k, p.get(k)) for k in ['vrsta', 'obseg', 'lokacija', 'koga', 'varnost', 'izvajalec', 'stanje', 'relevanca']}
    l['koga'] = {'prebivalci': 'da', 'otroci': 'da', 'ranljivi': 'da', 'obiskovalci': 'ne'}.get(l['koga'], l['koga'])
    l['izvajalec'] = l['izvajalec'].replace('š', 's')
    if i == 73605: l['stanje'] = 'S3'  # rule agreed after review: "Preverimo." is not a commitment
    dokaz = '' if p['dokaz'].startswith('(') else p['dokaz']
    labels[i] = {'id': i, **l, 'dokaz': dokaz, 'besedilo_ponovitev': p['ponovitev'], 'zadeva': zad[str(i)][0], 'tema': zad[str(i)][1],
                 'gotovost': 'visoka', 'opomba': ' '.join(x for x in [p['opomba'], rev.get('opomba', '')] if x), 'teren': rev.get('teren', ''), 'vir': 'pregledano'}

rows = []
for i, l in labels.items():
    txt = records[i]['response_text'] or ''
    # Rule agreed 2026-09-30: "we will check and act within our competence" names no concrete action -> S3
    if l['stanje'] == 'S4' and VAGUE.search(txt) and not CONCRETE.search(txt):
        l['stanje'] = 'S3'; l['stanje_pravilo'] = 'S4→S3 (splošna obljuba)'
    r = records[i]
    rep = date.fromisoformat(r['reported_date'])
    resp = date.fromisoformat(r['last_response_date']) if r['last_response_date'] else None
    core = BOILER.sub(' ', r['response_text'] or '').strip()
    l.update({
        'naslov': r['title'].strip(), 'prijava': r['reported_date'], 'odgovor_datum': r['last_response_date'] or '',
        'dni_do_odgovora': (resp - rep).days if resp else '',
        'dni_brez_odgovora': (CAPTURE - rep).days if not resp else '',
        'prepozen_odgovor': 'da' if (resp and (resp - rep).days > LATE_DAYS) or LATE_TEXT.search(r['response_text'] or '') else 'ne',
        'odgovor_brez_vsebine': 'da' if r['response_text'] and len(core) < 60 else 'ne',
        'lat': r['geometry_wgs84']['y'], 'lon': r['geometry_wgs84']['x'], 'odgovoril': r['respondents_text'],
        'teren': l.get('teren', ''),
    })
    rows.append(l)
rows.sort(key=lambda l: (l['prijava'], l['id']))
(D / 'oznake_544.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1))
cols = ['id', 'naslov', 'prijava', 'odgovor_datum', 'dni_do_odgovora', 'dni_brez_odgovora'] + FIELDS[1:] + ['prepozen_odgovor', 'odgovor_brez_vsebine', 'teren', 'vir', 'lat', 'lon']
with open(D / 'oznake_544.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
print(len(rows), 'oznak;', sum(l['vir'] == 'pregledano' for l in rows), 'pregledanih')
