#!/usr/bin/env python3
"""Embed the calibration set and proposed labels into the review page."""
import json
import re
from pathlib import Path

D = Path(__file__).resolve().parents[1] / 'analysis/oznacevanje'
src = {r['id']: r for r in json.loads((D / 'kalibracija_50_vir.json').read_text())}
props = json.loads((D / 'kalibracija_50_predlog.json').read_text())
rows = []
for p in props:
    p['izvajalec'] = p['izvajalec'].replace('š', 's')
    r = dict(src[p['id']]); r['initiative_text'], r['response_text'] = (re.sub(r'\n\s*\n+', '\n', (r[k] or '')).strip() for k in ('initiative_text', 'response_text'))
    r['p'] = {k: v for k, v in p.items() if k != 'id'}
    rows.append(r)
rows.sort(key=lambda r: (r['reported_date'], r['id']))
data = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
html = (D / 'pregled_template.html').read_text().replace('/*DATA*/', data)
(D / 'pregled_50.html').write_text(html)
print(len(rows), len(html))
