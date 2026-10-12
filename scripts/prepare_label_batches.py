#!/usr/bin/env python3
"""Split the recent-frame initiatives into batches for labelling (calibration set excluded)."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/oznacevanje/paketi'
OUT.mkdir(parents=True, exist_ok=True)
records = json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())
calib = {r['id'] for r in json.loads((ROOT / 'analysis/oznacevanje/kalibracija_50_vir.json').read_text())}
clean = lambda s: re.sub(r'\n\s*\n+', '\n', s or '').strip()
recent = sorted([r for r in records if r['reported_date'] and '2023-09-29' <= r['reported_date'] <= '2026-09-29' and r['id'] not in calib], key=lambda r: (r['reported_date'], r['id']))
rows = [{'id': r['id'], 'naslov': r['title'].strip(), 'prijava': r['reported_date'], 'odgovor_datum': r['last_response_date'], 'kategorija': r.get('category'), 'odgovoril': r['respondents_text'], 'pobuda': clean(r['initiative_text']), 'odgovor': clean(r['response_text'])} for r in recent]
size = 50
for i in range(0, len(rows), size):
    (OUT / f'paket_{i // size + 1:02d}.json').write_text(json.dumps(rows[i:i + size], ensure_ascii=False, indent=1))
print(len(rows), 'pobud v', (len(rows) + size - 1) // size, 'paketih')
