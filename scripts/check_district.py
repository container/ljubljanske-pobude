#!/usr/bin/env python3
"""Assign each captured point to the canonical MOL district polygons (see data/meje/boundary_source.json)."""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
polys = [(f['attributes']['CETRT'], f['geometry']['rings']) for f in json.loads((ROOT / 'data/meje/cetrtne_skupnosti.json').read_text())['features'] if f.get('geometry')]

def inside(x, y, rings):  # even-odd over all rings handles holes
    c = False
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c

def district(g):
    hits = [n for n, r in polys if inside(g['x'], g['y'], r)]
    return hits[0] if hits else 'izven MOL'

records = json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())
out = {r['id']: district(r['geometry_wgs84']) for r in records}
recent = {r['id'] for r in records if r['reported_date'] and r['reported_date'] >= '2023-09-29'}
(ROOT / 'analysis/oznacevanje/cetrt_po_tocki.json').write_text(json.dumps(out, ensure_ascii=False, indent=0))
print('vse:', Counter(out.values()).most_common())
print('zadnja 3 leta:', Counter(out[i] for i in recent).most_common())
