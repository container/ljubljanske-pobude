#!/usr/bin/env python3
"""Embed theme map data and initiative texts into the map page."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'analysis/teme'
SITE = ROOT / 'app/source'
data = json.loads((T / 'karta_podatki.json').read_text())
rec = {r['id']: r for r in json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())}
clean = lambda s: re.sub(r'\n\s*\n+', '\n', s or '').strip()
tx = {p['id']: {'pobuda': clean(rec[p['id']]['initiative_text']), 'odgovor': clean(rec[p['id']]['response_text']), 'odgovor_datum': rec[p['id']]['last_response_date'],
               'odgovoril': re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', rec[p['id']]['respondents_text'] or ''),
               'lat': round(rec[p['id']]['geometry_wgs84']['y'], 6), 'lon': round(rec[p['id']]['geometry_wgs84']['x'], 6)} for p in data['tocke']}
old = [r for r in rec.values() if r['reported_date'] and r['reported_date'] < '2023-09-29']
stare = [{'id': r['id'], 'la': round(r['geometry_wgs84']['y'], 6), 'lo': round(r['geometry_wgs84']['x'], 6), 'd': r['reported_date'], 'n': (r['title'] or '').strip()} for r in old]
for r in old:
    tx[r['id']] = {'pobuda': clean(r['initiative_text'])[:1500], 'odgovor': clean(r['response_text'])[:1500], 'odgovor_datum': r['last_response_date'],
                   'odgovoril': re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', r['respondents_text'] or ''),
                   'lat': round(r['geometry_wgs84']['y'], 6), 'lon': round(r['geometry_wgs84']['x'], 6)}
data['stare'] = stare
from datetime import datetime, timezone
VRSTA = {'V1':'Okvara, poškodba','V2':'Ponavljajoče vzdrževanje','V3':'Kršitve in nadzor','V4':'Manjša ureditev','V5':'Večja investicija, prenova','V6':'Nova storitev, predlog','V7':'Vprašanje, informacija','V8':'Pritožba na delo služb','V9':'Zunaj pristojnosti MOL'}
STANJE = {'S0':'Brez odgovora','S1':'Zavrnjeno ali odloženo brez roka','S2':'Zunaj pristojnosti MOL','S3':'Odgovor brez zaveze','S4':'Nedoločena obljuba','S5':'Konkretna napoved','S6':'Izvedba po navedbi MOL','SV':'Vprašanje vsebinsko odgovorjeno'}
OBSEG = {'tocka':'Točka','odsek':'Odsek ulice','soseska':'Soseska','vic':'Cel Vič','mol':'Cela MOL'}
LOK = {'ok':'Na Viču','tocka':'Točka napačna, zadeva na Viču','izven':'Ni v ČS Vič','brez':'Ni vezana na lokacijo'}
TEME = {'ceste':'Dotrajane ceste','signalizacija':'Semaforji, znaki, preglednost','pesci':'Pešci in pločniki','parkiranje':'Parkiranje','kolo':'Kolesarji','hitrost':'Hitrost in tranzit skozi soseske','sola':'Šolske poti','jpp':'Javni promet','gradbisca':'Gradbišča in zapore','odpadki':'Odpadki in čistoča','zelenje':'Drevesa in zelenje','igrisca':'Igrišča in druženje','javni_prostor':'Javni prostor','zimska':'Zimska služba','hrup':'Hrup in tresenje','lastnistvo':'Lastništvo zemljišč','razsvetljava':'Javna razsvetljava','vode':'Vode in poplave','azil':'Azilni dom','delo_mol':'Delovanje MOL','javni_red':'Javni red','drugo':'Drugo'}
AK = {'aktualno':'Prijavljeno v zadnjih 12 mesecih','ponavlja':'Starejše, problem se še prijavlja','utihnilo':'Utihnilo, ni prijav v zadnjem letu'}
labels = {l['id']: l for l in json.loads((T / 'teme_oznake.json').read_text())}
akt = {p['id']: p['ak'] for p in data['tocke']}
ms = lambda v: datetime.fromtimestamp(v / 1000, timezone.utc).strftime('%Y-%m-%d') if v else ''
def portal(r):
    g = r.get('gis_attributes') or {}
    rows = [['Status na portalu', r['portal_status']], ['Četrtna skupnost', r['district'] or ''],
            ['Kategorija portala', r['category'] or (f"šifra {r['category_id']} (naziv ni znan)" if r['category_id'] else '')],
            ['Prijava', r['reported_date'] or ''], ['Objava', r['published_date'] or ''], ['Zadnji odgovor', r['last_response_date'] or ''],
            ['Rok za odgovor (portal)', ms(g.get('DATUM_DO_ODGOVORA'))], ['Obravnava več oddelkov', 'da' if g.get('OBRAVNAVA_VEC_ODDELKOV') else 'ne'],
            ['Odgovoril', re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', r['respondents_text'] or '')]]
    return [[k, v] for k, v in rows if v]
def ozn(l, i):
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
for i, v in tx.items():
    r = rec[i]
    v['portal'] = portal(r)
    v['priloge'] = [a['url'] for a in (r.get('attachment_links') or []) if a.get('url')]
    if i in labels: v['oznake'] = ozn(labels[i], i)
esc = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
html = (T / 'karta_template.html').read_text().replace('/*DATA*/', esc(data)).replace('/*TEKSTI*/', esc(tx)).replace('/*LEAFLETCSS*/', (SITE / 'leaflet.css').read_text()).replace('/*STAT*/', esc(json.loads((T / 'statistika.json').read_text()))).replace('/*ABOUT*/', (T / 'o_strani.html').read_text())
google_tag = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-G2VT3SQV11"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-G2VT3SQV11');
</script>
'''
(T / 'perece_teme_vic.html').write_text('<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + google_tag + '</head><body style="margin:0">' + html + '</body></html>')
print(round(len(html) / 1e6, 2), 'MB')
