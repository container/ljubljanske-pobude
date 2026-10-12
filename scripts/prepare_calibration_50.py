#!/usr/bin/env python3
"""Calibration set of 50 recent initiatives for manual labelling (stratified by respondent, seeded)."""
import json, random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/oznacevanje'
records = json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())
recent = [r for r in records if r['reported_date'] and '2023-09-29' <= r['reported_date'] <= '2026-09-29']
# Known cases with field knowledge from the user: Vrhovnikova (unresolved), Jamova kindergarten (resolved), traffic light.
anchors = [70927, 86041, 73605, 81348, 75814, 80633, 80840, 82472]
rng = random.Random(20260930)
by_resp = defaultdict(list)
for r in recent:
    if r['id'] not in anchors:
        by_resp[(r['respondents_text'] or '').split(':')[-1].strip()].append(r)
quota = {k: max(1, round(42 * len(v) / (len(recent) - len(anchors)))) for k, v in by_resp.items()}
while sum(quota.values()) > 42:
    quota[max(quota, key=quota.get)] -= 1
picked = set(anchors)
for k, v in by_resp.items():
    picked |= {r['id'] for r in rng.sample(v, min(quota[k], len(v)))}
sample = sorted([r for r in recent if r['id'] in picked], key=lambda r: (r['reported_date'], r['id']))
keep = ['id', 'title', 'portal_status', 'reported_date', 'last_response_date', 'initiative_text', 'respondents_text', 'response_text', 'category', 'geometry_wgs84']
out = [{k: r.get(k) for k in keep} | {'anchor': r['id'] in anchors} for r in sample]
(OUT / 'kalibracija_50_vir.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(len(out), sum(quota.values()), quota)
