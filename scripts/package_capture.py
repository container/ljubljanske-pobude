#!/usr/bin/env python3
"""Validate and package the captured dataset without making network requests."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--folder', default='data/vic_2026-09-29')
parser.add_argument('--validate-only', action='store_true', help='Validate and write checksums without creating a ZIP archive')
options = parser.parse_args()
folder = root / options.folder
config_path = folder / 'capture_config.json'
district = json.loads(config_path.read_text())['district'] if config_path.exists() else 'vic'
basename = 'pobude_' + district
records = json.loads((folder / (basename + '.json')).read_text())
index = json.loads((folder / 'index.json').read_text())
report = json.loads((folder / 'capture_report.json').read_text())
source_check = json.loads((folder / 'source_list_verification.json').read_text())
assert source_check['unchanged']
geojson = json.loads((folder / (basename + '.geojson')).read_text())
expected_ids = {r['id'] for r in index}
assert len(records) == len(expected_ids) == report['expected'] == report['captured']
assert {r['id'] for r in records} == expected_ids
assert not report['network_errors'] and not report['parse_errors']
assert {f['id'] for f in geojson['features']} == expected_ids
jsonl = [json.loads(line) for line in (folder / (basename + '.jsonl')).read_text().splitlines()]
assert jsonl == records
connection = sqlite3.connect(folder / (basename + '.sqlite'))
db_records = {row[0]: json.loads(row[1]) for row in connection.execute('SELECT id, record_json FROM initiatives')}
connection.close()
assert db_records == {r['id']: r for r in records}
for record in records:
    raw = (folder / record['raw_detail_path']).read_text()
    assert hashlib.sha256(raw.encode()).hexdigest() == record['raw_sha256']
    attrs = record['gis_attributes']
    assert attrs['MOL_VNESENE_POBUDE_FC_ID'] == record['id']
    assert attrs['NASLOV_POBUDE'] == record['title']
    assert attrs['STATUS_POBUDE'] == {'odgovorjena': 2, 'neodgovorjena': 1}[record['portal_status']]
for feature in geojson['features']:
    source = db_records[feature['id']]['geometry_wgs84']
    if source:
        assert feature['geometry']['coordinates'] == [source['x'], source['y']]

(folder / 'validation_report.json').write_text(json.dumps({
    'validated_records': len(records), 'all_id_sets_match': True,
    'json_jsonl_sqlite_records_match': True, 'raw_sha256_checks_pass': True,
    'gis_titles_and_statuses_match_details': True, 'geojson_coordinates_match_source': True,
    'source_lists_unchanged_after_capture': True,
    'category_label_missing_count': sum(r['category'] is None for r in records)
}, ensure_ascii=False, indent=2), encoding='utf-8')

manifest = []
for path in sorted(folder.rglob('*')):
    if path.is_file() and path.name != 'checksums.sha256':
        manifest.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + str(path.relative_to(folder)))
(folder / 'checksums.sha256').write_text('\n'.join(manifest) + '\n')
if options.validate_only:
    print(json.dumps({'validated_records': len(records), 'files_hashed': len(manifest), 'archive_created': False}, ensure_ascii=False))
    sys.exit(0)
output = root / ('outputs/pobude_' + folder.name + '.zip')
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    readme = folder / 'README.md' if (folder / 'README.md').exists() else root / 'README.md'
    archive.write(readme, 'README.md')
    for name in ('capture_pobude.py', 'verify_source_lists.py', 'package_capture.py'):
        path = root / 'scripts' / name
        archive.write(path, path.relative_to(root))
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            archive.write(path, path.relative_to(root))
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
print(json.dumps({'validated_records': len(records), 'files_hashed': len(manifest), 'archive': str(output), 'archive_bytes': output.stat().st_size}, ensure_ascii=False))
