#!/usr/bin/env python3
"""Split answered initiatives of one district from the last N years into batches of 50 for labelling vrsta + stanje.
Unanswered ones get S0 automatically and are not batched. Usage: prepare_vrsta_stanje.py --district center --years 1"""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument('--district', default='center'); ap.add_argument('--years', type=int, default=1); a = ap.parse_args()
C = next(c for c in json.loads((ROOT / 'data/cetrti.json').read_text()) if c['id'] == a.district)
R = json.loads((ROOT / C['mapa'] / f"pobude_{C['id']}.json").read_text())
od = f"{int(C['zajem'][:4]) - a.years}{C['zajem'][4:]}"
OUT = ROOT / 'analysis/cetrti' / C['id'] / 'oznacevanje'
(OUT / 'paketi').mkdir(parents=True, exist_ok=True)
clean = lambda s: re.sub(r'\n\s*\n+', '\n', s or '').strip()
g = sorted([r for r in R if r['reported_date'] >= od], key=lambda r: (r['reported_date'], r['id']))
s0 = [{'id': r['id'], 'vrsta': '', 'stanje': 'S0', 'dokaz': '', 'gotovost': 'visoka', 'opomba': 'neodgovorjena na portalu', 'vir': 'samodejno'} for r in g if r['portal_status'] != 'odgovorjena']
rows = [{'id': r['id'], 'naslov': (r['title'] or '').strip(), 'prijava': r['reported_date'], 'odgovor_datum': r['last_response_date'], 'kategorija': r.get('category'),
         'odgovoril': r['respondents_text'], 'pobuda': clean(r['initiative_text']), 'odgovor': clean(r['response_text'])} for r in g if r['portal_status'] == 'odgovorjena']
# Extending the window (--years 2 after 1) keeps existing batches and appends only new initiatives after them.
old = sorted((OUT / 'paketi').glob('paket_[0-9][0-9].json'))
done = {x['id'] for f in old for x in json.loads(f.read_text())}
rows = [x for x in rows if x['id'] not in done]
for i in range(0, len(rows), 50):
    p = OUT / 'paketi' / f'paket_{len(old) + i // 50 + 1:02d}.json'
    if not p.exists(): p.write_text(json.dumps(rows[i:i + 50], ensure_ascii=False, indent=1))
(OUT / 'samodejno_s0.json').write_text(json.dumps(s0, ensure_ascii=False, indent=1))
print(od, len(g), 'pobud,', len(s0), 'samodejno S0,', len(rows), 'novih v', (len(rows) + 49) // 50, 'paketih od', len(old) + 1)
