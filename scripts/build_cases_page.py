#!/usr/bin/env python3
"""Embed cases and member initiatives into the case review page."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'analysis/oznacevanje'
Z = json.loads((D / 'zadeve.json').read_text())
L = {l['id']: l for l in json.loads((D / 'oznake_544.json').read_text())}
rec = {r['id']: r for r in json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())}
clean = lambda s: re.sub(r'\n\s*\n+', '\n', s or '').strip()
P = {i: {'naslov': l['naslov'], 'prijava': l['prijava'], 'odgovor_datum': l['odgovor_datum'], 'dni': l['dni_do_odgovora'], 'stanje': l['stanje'],
         'prepozen': l['prepozen_odgovor'], 'lokacija': l['lokacija'], 'dokaz': l['dokaz'], 'opomba': l['opomba'],
         'odgovoril': re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', rec[i]['respondents_text'] or ''),
         'pobuda': clean(rec[i]['initiative_text']), 'odgovor': clean(rec[i]['response_text']), 'lat': round(l['lat'], 6), 'lon': round(l['lon'], 6)} for i, l in L.items()}
hist_ids = {h['id'] for c in Z for h in c['zgodovina_pred_2023']}
H = {i: {'pobuda': clean(rec[i]['initiative_text']), 'odgovor': clean(rec[i]['response_text']), 'odgovor_datum': rec[i]['last_response_date'], 'lat': round(rec[i]['geometry_wgs84']['y'], 6), 'lon': round(rec[i]['geometry_wgs84']['x'], 6),
         'odgovoril': re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', rec[i]['respondents_text'] or '')} for i in hist_ids}
keep = ['zadeva_id', 'ids', 'n', 'naslov', 'prioriteta', 'relevanca', 'varnost', 'koga', 'lokacija_izven', 'stanja', 'izvajalci', 'prva_prijava_vse', 'zadnja_prijava', 'zgodovina_pred_2023']
z = [{k: c[k] for k in keep} for c in Z]
esc = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
html = (D / 'zadeve_template.html').read_text().replace('/*ZADEVE*/', esc(z)).replace('/*POBUDE*/', esc(P)).replace('/*ZGODOVINA*/', esc(H))
(D / 'zadeve_vic.html').write_text(html)
print(len(z), 'zadev,', round(len(html) / 1e6, 2), 'MB')
