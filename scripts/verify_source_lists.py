#!/usr/bin/env python3
"""Recheck the portal dropdown lists after capture to detect changes during the run."""
import argparse
import json
from capture_pobude import ROOT, PAGES, Client, parse_list, save_json, now

parser = argparse.ArgumentParser()
parser.add_argument('--folder', default='data/vic_2026-09-29')
options = parser.parse_args()
folder = ROOT / options.folder
config_path = folder / 'capture_config.json'
district = json.loads(config_path.read_text())['district'] if config_path.exists() else 'vic'
client = Client(folder, district)
source_index = folder / 'full_source_index.json'
original = json.loads((source_index if source_index.exists() else folder / 'index.json').read_text())
latest = []
for status, page in PAGES.items():
    form = client.form(status, suffix='_verification')
    response = client.callback(status, form, '0::::' + client.district_value + '::::0::::getpobudaid')
    (folder / 'raw' / (status + '_verification_list.txt')).write_text(response, encoding='utf-8')
    latest.extend(parse_list(response, status))
before = {row['id']: row for row in original}
after = {row['id']: row for row in latest}
if len(after) != len(latest):
    raise ValueError('Overlap between status lists: refresh needed')
result = {'checked_at': now(), 'original_count': len(before), 'latest_count': len(after),
          'added_ids': sorted(after.keys() - before.keys()), 'removed_ids': sorted(before.keys() - after.keys()),
          'changed_list_rows': sorted(i for i in before.keys() & after.keys() if before[i] != after[i])}
result['unchanged'] = not (result['added_ids'] or result['removed_ids'] or result['changed_list_rows'])
if source_index.exists():
    result['scope'] = 'full_source_lists_for_period_subset'
save_json(folder / 'source_list_verification.json', result)
print(json.dumps(result, ensure_ascii=False))
if not result['unchanged']:
    raise SystemExit(1)
