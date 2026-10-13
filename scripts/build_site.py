#!/usr/bin/env python3
"""Build the multi-district site "Ljubljanske pobude" into deploy/site/.

Districts come from data/cetrti.json. Each gets d/<id>.json (map points, theme stats, boundary, statistics)
and d/<id>/tx/<n>.json (initiative texts, bucketed by id and fetched on click). Districts with our labels
(currently Vič) reuse the theme pipeline output; the others show portal fields only.
Run build_stats.py --district <id> (and for Vič build_theme_map_data.py) first."""
import json, math, re, shutil
from datetime import datetime, timezone
from pathlib import Path
from check_repeat_clusters import check as check_repeat_clusters

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'analysis/teme'
SITE = ROOT / 'analysis/site'
OUT = ROOT / 'deploy/site'
CETRTI = json.loads((ROOT / 'data/cetrti.json').read_text())
BOUNDS = {f['attributes']['CETRT']: f['geometry']['rings'] for f in json.loads((ROOT / 'data/meje/cetrtne_skupnosti.json').read_text())['features']}

clean = lambda s: re.sub(r'\n\s*\n+', '\n', s or '').strip()
who = lambda r: re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', r['respondents_text'] or '')
ms = lambda v: datetime.fromtimestamp(v / 1000, timezone.utc).strftime('%Y-%m-%d') if v else ''
esc = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

VRSTA = {'V1':'Okvara, poškodba','V2':'Ponavljajoče vzdrževanje','V3':'Kršitve in nadzor','V4':'Manjša ureditev','V5':'Večja investicija, prenova','V6':'Nova storitev, predlog','V7':'Vprašanje, informacija','V8':'Pritožba na delo služb','V9':'Zunaj pristojnosti MOL'}
STANJE = {'S0':'Brez odgovora','S1':'Zavrnjeno ali odloženo brez roka','S2':'Zunaj pristojnosti MOL','S3':'Odgovor brez zaveze','S4':'Nedoločena obljuba','S5':'Konkretna napoved','S6':'Izvedba po navedbi MOL','SV':'Vprašanje vsebinsko odgovorjeno'}
OBSEG = {'tocka':'Točka','odsek':'Odsek ulice','soseska':'Soseska','vic':'Cel Vič','mol':'Cela MOL'}
LOK = {'ok':'Na Viču','tocka':'Točka napačna, zadeva na Viču','izven':'Ni v ČS Vič','brez':'Ni vezana na lokacijo'}
TEME = {'ceste':'Dotrajane ceste','signalizacija':'Semaforji, znaki, preglednost','pesci':'Pešci in pločniki','parkiranje':'Parkiranje','kolo':'Kolesarji','hitrost':'Hitrost in tranzit skozi soseske','sola':'Šolske poti','jpp':'Javni promet','gradbisca':'Gradbišča in zapore','odpadki':'Odpadki in čistoča','zelenje':'Drevesa in zelenje','igrisca':'Igrišča in druženje','javni_prostor':'Javni prostor','zimska':'Zimska služba','hrup':'Hrup in tresenje','lastnistvo':'Lastništvo zemljišč','razsvetljava':'Javna razsvetljava','vode':'Vode in poplave','azil':'Azilni dom','delo_mol':'Delovanje MOL','javni_red':'Javni red','drugo':'Drugo'}

def late(r):
    dl = ms((r.get('gis_attributes') or {}).get('DATUM_DO_ODGOVORA')); lr = r['last_response_date']
    return None if not (dl and lr) else lr > dl

def portal(r):
    g = r.get('gis_attributes') or {}
    rows = [['Status na portalu', r['portal_status']], ['Četrtna skupnost', r['district'] or ''],
            ['Kategorija portala', r['category'] or (f"šifra {r['category_id']} (naziv ni znan)" if r['category_id'] else '')],
            ['Prijava', r['reported_date'] or ''], ['Objava', r['published_date'] or ''], ['Zadnji odgovor', r['last_response_date'] or ''],
            ['Rok za odgovor (portal)', ms(g.get('DATUM_DO_ODGOVORA'))], ['Obravnava več oddelkov', 'da' if g.get('OBRAVNAVA_VEC_ODDELKOV') else 'ne'],
            ['Odgovoril', who(r)]]
    return [[k, v] for k, v in rows if v]

def ozn(l):
    rows = [['Tema', TEME.get(l.get('tema2', ''), l.get('tema2', ''))], ['Na kratko', l.get('podrobno', '')], ['Vrsta', f"{l['vrsta']} · {VRSTA.get(l['vrsta'], '')}"],
            ['Stanje po odgovoru', f"{l['stanje']} · {STANJE.get(l['stanje'], '')}" + (' (pravilo: splošna obljuba)' if l.get('stanje_pravilo') else '')],
            ['Dokaz za stanje', l.get('dokaz', '')], ['Relevanca', l['relevanca']], ['Varnost', l['varnost']], ['Zadeva prebivalcev ČS', l['koga']],
            ['Obseg', OBSEG.get(l['obseg'], l['obseg'])], ['Lokacija', LOK.get(l['lokacija'], l['lokacija'])], ['Najbližja ulica', l.get('ulica_mol', '')],
            ['Izvajalec', l['izvajalec']], ['Zadeva (ključ)', l.get('zadeva', '')],
            ['Dni do odgovora', str(l.get('dni_do_odgovora', ''))], ['Dni brez odgovora', str(l.get('dni_brez_odgovora', ''))],
            ['Prepozen odgovor', l.get('prepozen_odgovor', '')], ['Odgovor brez vsebine', l.get('odgovor_brez_vsebine', '')],
            ['Besedilo omenja ponavljanje', l.get('besedilo_ponovitev', '')], ['Pritožba na izvedeno prenovo', l.get('prenova', '')],
            ['Znanje s terena', {'reseno': 'rešeno', 'nereseno': 'ni rešeno', 'delno': 'delno', 'nevem': 'ne vem'}.get(l.get('teren', ''), '')],
            ['Gotovost oznak', l.get('gotovost', '')], ['Vir oznak', 'pregledano ročno' if l.get('vir') == 'pregledano' else 'strojno'], ['Opomba', l.get('opomba', '')]]
    return [[k, v] for k, v in rows if v not in ('', None)]

def ozn_vs(l):
    rows = [['Vrsta', f"{l['vrsta']} · {VRSTA.get(l['vrsta'], '')}" if l['vrsta'] else ''], ['Stanje po odgovoru', f"{l['stanje']} · {STANJE.get(l['stanje'], '')}"],
            ['Dokaz za stanje', l.get('dokaz', '')], ['Gotovost oznak', l.get('gotovost', '')], ['Vir oznak', {'samodejno': 'samodejno (neodgovorjena)', 'strojno': 'strojno'}.get(l.get('vir'), '')],
            ['Opomba', l.get('opomba', '')]]
    return [[k, v] for k, v in rows if v not in ('', None)]

def text(r, labels):
    g = r['geometry_wgs84']
    v = {'pobuda': clean(r['initiative_text']), 'odgovor': clean(r['response_text']), 'odgovor_datum': r['last_response_date'], 'odgovoril': who(r),
         'lat': round(g['y'], 6), 'lon': round(g['x'], 6), 'portal': portal(r), 'priloge': [a['url'] for a in (r.get('attachment_links') or []) if a.get('url')]}
    if r['id'] in labels: v['oznake'] = ozn(labels[r['id']]) if 'relevanca' in labels[r['id']] else ozn_vs(labels[r['id']])
    return v

def pstat(r):
    """Portal-only response class for districts without labels."""
    if r['portal_status'] != 'odgovorjena': return 'neodg'
    lt = late(r)
    return 'brez_roka' if lt is None else ('zamujeno' if lt else 'pravocasno')

nf = lambda n: f'{n:,}'.replace(',', '.')
def dmy(d): y, m, dd = d.split('-'); return f'{int(dd)}. {int(m)}. {y}'

def district_clusters(district, records, labels):
    folder = ROOT / 'analysis/cetrti' / district / 'clusters'
    selection = folder / 'selection.json'
    if not selection.exists() and district == 'vic':
        selection = ROOT / 'analysis/clusters_100m_2026-10-12/selection.json'
    if not selection.exists():
        return [], {}
    clusters = []
    for group in json.loads(selection.read_text()):
        members = [records[i] for i in dict.fromkeys(group['ids'])]
        if len(members) < 3:
            continue
        dates = sorted(r['reported_date'] for r in members if r.get('reported_date'))
        marked = [labels[r['id']] for r in members if r['id'] in labels]
        safety_count = len(set(group['safety_ids']) & set(group['ids'])) if 'safety_ids' in group else sum(l.get('varnost') == 'da' for l in marked)
        years = (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days / 365.25
        clusters.append({
            'name': group['name'], 'ids': [r['id'] for r in members], 'count': len(members),
            'la': round(sum(r['geometry_wgs84']['y'] for r in members) / len(members), 6),
            'lo': round(sum(r['geometry_wgs84']['x'] for r in members) / len(members), 6),
            'first': dates[0], 'last': dates[-1], 'years': round(years, 1),
            'safety_count': safety_count, 'label_count': len(members) if 'safety_ids' in group else len(marked),
            'score': round(min(1, (len(members)-1)/19)*50 + min(1, years/10)*25 + (25 if safety_count else 0)),
            'category': group.get('category', ''), 'note': group.get('review_note', ''),
            'members': [{'id': r['id'], 'date': r.get('reported_date') or '', 'title': (r.get('title') or '').strip(),
                         'la': round(r['geometry_wgs84']['y'], 6), 'lo': round(r['geometry_wgs84']['x'], 6)}
                        for r in sorted(members, key=lambda r: (r.get('reported_date') or '', r['id']), reverse=True)]
        })
    clusters.sort(key=lambda c: (c['score'], c['count']), reverse=True)
    info = json.loads((folder / 'review.json').read_text())['meta'] if (folder / 'review.json').exists() else {}
    return clusters, info

for C in CETRTI:
    if (ROOT / 'analysis/cetrti' / C['id'] / 'clusters/review.json').exists():
        check_repeat_clusters(C['id'])

if OUT.exists():
    for p in ('d', 'fonts', 'index.html', 'cetrti.json'):
        q = OUT / p
        shutil.rmtree(q) if q.is_dir() else q.unlink(missing_ok=True)
(OUT / 'd').mkdir(parents=True, exist_ok=True)

registry, zajemi, vse_skupine, delno, info = [], [], [], set(), {}
for C in CETRTI:
    R = json.loads((ROOT / C['mapa'] / f"pobude_{C['id']}.json").read_text())
    rec = {r['id']: r for r in R}
    S = json.loads((ROOT / 'analysis/cetrti' / C['id'] / 'statistika.json').read_text())
    labels = {}
    meja = [[[round(y, 5), round(x, 5)] for x, y in ring] for ring in BOUNDS[C['oznaka']]]
    if C['oznake']:
        D = json.loads((T / 'karta_podatki.json').read_text())
        labels = {l['id']: l for l in json.loads((T / 'teme_oznake.json').read_text())}
    else:
        vs = ROOT / 'analysis/cetrti' / C['id'] / 'oznake_vrsta_stanje.json'
        if vs.exists(): labels = {l['id']: l for l in json.loads(vs.read_text())}
        D = {'tocke': [{'id': r['id'], 'la': round(r['geometry_wgs84']['y'], 6), 'lo': round(r['geometry_wgs84']['x'], 6), 'd': r['reported_date'],
                        'n': (r['title'] or '').strip(), 'ps': pstat(r), 'sl': who(r)}
                       | ({'s': labels[r['id']]['stanje'], 'v': labels[r['id']]['vrsta']} if r['id'] in labels else {})
                       for r in R if r['reported_date'] >= (S['vs']['od'] if 'vs' in S else S['od1'] if labels else S['od3'])], 'teme': {}, 'podlaga': {'meja': meja}}
    # Always use the canonical district layer, including districts whose point
    # and theme data were built earlier and contain an older cached outline.
    D.setdefault('podlaga', {})['meja'] = meja
    shown = {p['id'] for p in D['tocke']}
    D['stare'] = [{'id': r['id'], 'la': round(r['geometry_wgs84']['y'], 6), 'lo': round(r['geometry_wgs84']['x'], 6), 'd': r['reported_date'], 'n': (r['title'] or '').strip()}
                  for r in R if r['reported_date'] and r['id'] not in shown and (r['reported_date'] < S['od3'] or (labels and not C['oznake']))]
    n_tx = max(1, math.ceil(len(R) / 400))
    buckets = [{} for _ in range(n_tx)]
    for r in R: buckets[r['id'] % n_tx][r['id']] = text(r, labels)
    (OUT / 'd' / C['id'] / 'tx').mkdir(parents=True, exist_ok=True)
    for i, b in enumerate(buckets): (OUT / 'd' / C['id'] / 'tx' / f'{i}.json').write_text(esc(b))
    meta = {k: C[k] for k in ('id', 'ime', 'kje', 'oznaka', 'zajem', 'oznake')} | {'vs': bool(labels) and not C['oznake'], 'n_tx': n_tx, 'od3': S['od3'], 'od1': S['od1'], 'do': S['do'],
                                                                                        'odvs': S['vs']['od'] if 'vs' in S else S['od1'], 'vsobd': f"{12 * C.get('oznake_let', 1)} mesecev"}
    clusters, cluster_info = district_clusters(C['id'], rec, labels)
    (OUT / 'd' / f"{C['id']}.json").write_text(esc({'meta': meta, 'D': D, 'STAT': S, 'CLUSTERS': clusters, 'cluster_info': cluster_info}))
    info[C['id']] = {k: cluster_info[k] for k in ('records', 'seeds', 'spatial_pairs', 'strong_pairs', 'candidate_groups', 'reviewed_candidates') if k in cluster_info}
    if cluster_info.get('reviewed_candidates', 0) < cluster_info.get('candidate_groups', 0):
        delno.add(C['id'])
    vse_skupine += [c | {'did': C['id'], 'dime': C['ime']} for c in clusters]
    registry.append({k: C[k] for k in ('id', 'ime')} | {'n_tx': n_tx, 'meja': [[[round(y, 4), round(x, 4)] for x, y in ring] for ring in BOUNDS[C['oznaka']]]})
    odg = S['odgovorjenih']
    zajemi.append(f"<li><b>{C['ime']}</b>: zajem {dmy(C['zajem'])}, filter »{C['oznaka']}«. {nf(S['skupaj'])} pobud od {dmy(S['od'])} do {dmy(S['do'])} "
                  f"({nf(odg)} odgovorjenih, {nf(S['skupaj'] - odg)} neodgovorjenih), od tega {nf(S['tri_leta'])} v zadnjih treh letih."
                  + (' Za to četrt so narejene tudi teme in oznake.' if C['oznake'] else (f" Pobude iz zadnjih {12 * C.get('oznake_let', 1)} mesecev ({nf(len(labels))}) imajo oznaki Vrsta in Stanje po odgovoru." if labels else ' Samo podatki portala, brez naših oznak.')) + '</li>')
    print(C['id'], 'točk', len(D['tocke']), 'starih', len(D['stare']), 'paketov besedil', n_tx, f"{(OUT / 'd' / (C['id'] + '.json')).stat().st_size / 1e6:.2f} MB")

vse_skupine.sort(key=lambda c: (c['score'], c['count']), reverse=True)
(OUT / 'd' / 'vse.json').write_text(esc({'CLUSTERS': vse_skupine, 'districts': [{'id': i, 'ime': n, 'n': sum(c['did'] == i for c in vse_skupine), 'delno': i in delno, 'info': info[i]}
                                                                        for i, n in dict.fromkeys((c['did'], c['dime']) for c in vse_skupine)]}))
print('vse skupine', len(vse_skupine))

about = (SITE / 'o_strani.html').read_text().replace('<!--ZAJEMI-->', '\n'.join(zajemi))
google_tag = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-G2VT3SQV11"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-G2VT3SQV11');
</script>
'''
shutil.copytree(ROOT / 'design-library/assets/fonts', OUT / 'fonts')
fonts = (ROOT / 'design-library/fonts.css').read_text().replace('url(assets/fonts/', 'url(fonts/')
html = (SITE / 'template.html').read_text().replace('/*CETRTI*/', esc(registry)).replace('/*LEAFLETCSS*/', (T / 'leaflet.css').read_text()).replace('/*ABOUT*/', about).replace('/*FONTS*/', fonts)
(OUT / 'index.html').write_text('<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + google_tag + '</head><body style="margin:0">' + html + '</body></html>')
(OUT / 'cetrti.json').write_text(esc(registry))
print('index.html', round(len(html) / 1e3), 'kB')
