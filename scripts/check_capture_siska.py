"""Live end-to-end check on 20 answered and 10 unanswered Šiška initiatives.
Uses the same client, parser, exports and validation as a full capture.
Usage: python3 scripts/check_capture_siska.py --folder tmp/siska_check_NEW
The output folder must be new; its contents are a test sample, not a full capture.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from capture_pobude import Client, PAGES, export, now, parse_list, save_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--folder', required=True, help='New folder for the test sample; never use a full capture folder')
options = parser.parse_args()
folder = ROOT / options.folder
folder.mkdir(parents=True, exist_ok=False)
(folder / 'raw/details').mkdir(parents=True)
client = Client(folder, 'siska')
started = now()
save_json(folder / 'capture_config.json', {
    'district': 'siska', 'district_label': 'ŠIŠKA', 'district_value': '8',
})
forms = {status: client.form(status) for status in PAGES}
all_rows, selected = [], []
for status in PAGES:
    body = client.callback(status, forms[status], '0::::8::::0::::getpobudaid')
    (folder / 'raw' / (status + '_list.txt')).write_text(body, encoding='utf-8')
    rows = parse_list(body, status)
    all_rows.extend(rows)
    count = min(len(rows), 20 if status == 'odgovorjena' else 10)
    assert count >= 2, 'Need both ends of each status list for this test'
    selected.extend(rows[round(i * (len(rows) - 1) / (count - 1))] for i in range(count))
    print(f'{status}: source={len(rows)}, sample={count}', flush=True)
assert len({r['id'] for r in all_rows}) == len(all_rows)
assert len({r['id'] for r in selected}) == len(selected)
save_json(folder / 'full_source_index.json', all_rows)
save_json(folder / 'index.json', selected)
save_json(folder / 'sample_manifest.json', {
    'scope': 'test_sample_only', 'source_count': len(all_rows),
    'sample_count': len(selected),
    'selection': '20 answered and 10 unanswered, evenly spaced over each portal list, including first and last',
    'ids': [r['id'] for r in selected],
})
fields = 'OBJECTID,MOL_VNESENE_POBUDE_FC_ID,NASLOV_POBUDE,STATUS_POBUDE,MOL_VRSTE_POBUD_ID,DATUM_VNOSA,DATUM_OBRAVNAVE,DATUM_ZADNJEGA_ODGOVORA,DATUM_KONCA_AKTUALNOSTI,DATUM_DO_ODGOVORA,OBRAVNAVA_VEC_ODDELKOV'
ids = ','.join(str(r['id']) for r in selected)
result = client.gis({'where': f'MOL_VNESENE_POBUDE_FC_ID IN ({ids})',
    'outFields': fields, 'returnGeometry': 'true', 'outSR': '4326', 'f': 'json'})
save_json(folder / 'raw/geometry_0000.json', result)
assert not result.get('exceededTransferLimit')
geometry = {str(f['attributes']['MOL_VNESENE_POBUDE_FC_ID']): f for f in result['features']}
assert len(geometry) == len(result['features']) == len(selected)
save_json(folder / 'geometry.json', geometry)
for n, row in enumerate(selected, 1):
    body = client.callback(row['portal_status'], forms[row['portal_status']], str(row['id']) + '::::getpobudatext')
    assert 'setPobudaInfo(' in body
    (folder / 'raw/details' / (str(row['id']) + '.txt')).write_text(body, encoding='utf-8')
    if n % 10 == 0:
        print(f'DETAIL {n}/{len(selected)}', flush=True)
assert export(folder, selected, geometry, [], started, 'siska')
latest = []
for status in PAGES:
    form = client.form(status, suffix='_verification')
    body = client.callback(status, form, '0::::8::::0::::getpobudaid')
    (folder / 'raw' / (status + '_verification_list.txt')).write_text(body, encoding='utf-8')
    latest.extend(parse_list(body, status))
before, after = ({r['id']: r for r in rows} for rows in (all_rows, latest))
assert len(after) == len(latest)
check = {'checked_at': now(), 'scope': 'full_source_lists_for_test_sample',
    'original_count': len(before), 'latest_count': len(after),
    'added_ids': sorted(after.keys() - before.keys()),
    'removed_ids': sorted(before.keys() - after.keys()),
    'changed_list_rows': sorted(i for i in before.keys() & after.keys() if before[i] != after[i])}
check['unchanged'] = not (check['added_ids'] or check['removed_ids'] or check['changed_list_rows'])
save_json(folder / 'source_list_verification.json', check)
assert check['unchanged'], 'Portal lists changed during the test'
records = json.loads((folder / 'pobude_siska.json').read_text())
assert all(r['district'] == 'ŠIŠKA' and r['initiative_text'] and r['reported_date'] for r in records)
assert all(13 < r['geometry_wgs84']['x'] < 17 and 45 < r['geometry_wgs84']['y'] < 47 for r in records)
report = json.loads((folder / 'capture_report.json').read_text())
report['scope'] = 'test_sample_only'
report['full_source_count'] = len(all_rows)
save_json(folder / 'capture_report.json', report)
subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/package_capture.py'),
    '--folder', str(folder), '--validate-only'], check=True)
print('TEST PASSED: ' + str(folder), flush=True)
