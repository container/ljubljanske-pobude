#!/usr/bin/env python3
"""Check reviewed clusters against their source snapshot and the recent-seed/100 m rule.

Run after preparing candidates and reviewing selection.json, before build_site.py.
Changed source texts invalidate the recorded review; similarity alone never approves a group.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(district):
    config = next(c for c in json.loads((ROOT / 'data/cetrti.json').read_text()) if c['id'] == district)
    folder = ROOT / 'analysis/cetrti' / district / 'clusters'
    review = json.loads((folder / 'review.json').read_text())
    selection = json.loads((folder / 'selection.json').read_text())
    records = {r['id']: r for r in json.loads((ROOT / config['mapa'] / f'pobude_{district}.json').read_text())}
    labels = {r['id']: r for r in json.loads((folder.parent / 'oznake_vrsta_stanje.json').read_text())}
    overrides = folder / 'seed_type_overrides.json'
    if overrides.exists():
        labels.update({r['id']: r for r in json.loads(overrides.read_text())})
    cutoff = review['meta']['cutoff']
    errors, all_ids, max_distance = [], set(), 0
    kx = 111320 * math.cos(math.radians(46.06))
    for group in selection:
        ids = group['ids']
        name = group['name']
        if len(set(ids)) < 3 or len(set(ids)) != len(ids):
            errors.append(f'{name}: fewer than 3 distinct report IDs or duplicate ID')
        if any(i not in records for i in ids):
            errors.append(f'{name}: missing source record')
            continue
        if all_ids & set(ids):
            errors.append(f'{name}: report reused across groups; split or explicitly review membership')
        all_ids.update(ids)
        if not set(group.get('safety_ids', [])) <= set(ids):
            errors.append(f'{name}: safety ID outside group')
        seeds = [i for i in ids if records[i]['reported_date'] >= cutoff and labels.get(i, {}).get('vrsta') not in ('', None, 'V7')]
        if not seeds:
            errors.append(f'{name}: no classified recent non-question seed')
        for i in ids:
            r = records[i]
            content = {k: r.get(k) for k in ('title', 'initiative_text', 'response_text', 'reported_date', 'geometry_wgs84')}
            digest = hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if group.get('reviewed_hashes', {}).get(str(i)) != digest:
                errors.append(f'{name}: #{i} changed or lacks recorded review hash')
            if not r.get('geometry_wgs84'):
                errors.append(f'{name}: #{i} has no geometry')
                continue
            if seeds:
                a = r['geometry_wgs84']
                distances = [math.hypot((a['x']-records[j]['geometry_wgs84']['x'])*kx,
                                       (a['y']-records[j]['geometry_wgs84']['y'])*111320) for j in seeds]
                distance = min(distances)
                max_distance = max(max_distance, distance)
                if distance > review['meta']['radius_m']:
                    errors.append(f'{name}: #{i} is {distance:.1f} m from closest recent seed')
    if review['meta']['accepted_clusters'] != len(selection) or review['meta']['accepted_reports'] != len(all_ids):
        errors.append('Review totals differ from selection')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'district': district, 'clusters': len(selection), 'reports': len(all_ids),
            'max_distance_to_recent_seed_m': round(max_distance, 1), 'review_hashes': 'unchanged'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--district', required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.district), ensure_ascii=False, indent=2))
