#!/usr/bin/env python3
"""Merge vrsta + stanje batch labels of one district with the automatic S0 labels and validate them.
Writes analysis/cetrti/<id>/oznake_vrsta_stanje.json. Usage: merge_vrsta_stanje.py --district center"""
import argparse, glob, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument('--district', default='center'); a = ap.parse_args()
D = ROOT / 'analysis/cetrti' / a.district
norm = lambda s: re.sub(r'\s+', ' ', s or '').strip()
out, problems = list(json.loads((D / 'oznacevanje/samodejno_s0.json').read_text())), []
for f in sorted(glob.glob(str(D / 'oznacevanje/paketi/paket_[0-9][0-9].json'))):
    src = json.loads(Path(f).read_text()); lf = Path(f.replace('.json', '_oznake.json'))
    if not lf.exists(): problems.append(f'manjka {lf.name}'); continue
    lab = json.loads(lf.read_text())
    if [x['id'] for x in src] != [int(x['id']) for x in lab]: problems.append(f'{lf.name}: id-ji se ne ujemajo')
    for s, l in zip(src, lab):
        if l['vrsta'] not in {f'V{i}' for i in range(1, 10)} or l['stanje'] not in {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'SV'}:
            problems.append(f"{s['id']}: neveljavna šifra {l['vrsta']} {l['stanje']}")
        if norm(l['dokaz']) not in norm(s['odgovor']): problems.append(f"{s['id']}: dokaz ni dobeseden")
        out.append({'id': s['id'], 'vrsta': l['vrsta'], 'stanje': l['stanje'], 'dokaz': l['dokaz'], 'gotovost': l['gotovost'], 'opomba': l.get('opomba', ''), 'vir': 'strojno'})
(D / 'oznake_vrsta_stanje.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), 'oznak', dict(Counter(x['stanje'] for x in out)), dict(Counter(x['vrsta'] for x in out)), 'nizka:', sum(x['gotovost'] == 'nizka' for x in out))
print('težave:', problems or 'nobenih')
