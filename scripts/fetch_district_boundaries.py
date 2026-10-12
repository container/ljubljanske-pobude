#!/usr/bin/env python3
"""Fetch district outlines from MOL's D96/TM layer, not the shifted legacy layer."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data/meje'
SOURCE = 'https://pobude.ljubljana.si/arcgis/rest/services/mol_ulice/ulice_mol_interni/MapServer/31'


def fetch(path, params):
    url = SOURCE + path + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read()
    result = json.loads(body)
    if 'error' in result:
        raise ValueError(result['error'])
    return url, body, result


def main():
    metadata = fetch('', {'f': 'json'})
    if metadata[2]['sourceSpatialReference']['wkid'] != 3794:
        raise ValueError('Expected MOL boundary source in D96/TM (EPSG:3794)')
    params = {'where': '1=1', 'outFields': 'CETRT,STEVILKA,IME,OZNAKA',
              'returnGeometry': 'true', 'f': 'json'}
    native = fetch('/query', params)
    wgs84 = fetch('/query', dict(params, outSR='4326'))
    for response in (native, wgs84):
        data = response[2]
        names = [f['attributes']['CETRT'] for f in data['features']]
        if data.get('exceededTransferLimit') or len(names) != 17 or len(set(names)) != 17:
            raise ValueError('Expected all 17 unique districts without a transfer limit')
        if not {'VIČ', 'CENTER'}.issubset(names):
            raise ValueError('Vič or Center missing')
        for feature in data['features']:
            for ring in feature['geometry']['rings']:
                if len(ring) < 4 or ring[0] != ring[-1]:
                    raise ValueError('Invalid polygon ring')
    if wgs84[2]['spatialReference']['wkid'] != 4326:
        raise ValueError('Expected WGS84 output')
    raw = FOLDER / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    report = {'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'source': SOURCE, 'source_crs': 'EPSG:3794', 'output_crs': 'EPSG:4326',
              'district_count': 17, 'manual_offset_applied': False, 'requests': []}
    for name, response in [('metadata', metadata), ('3794', native), ('4326', wgs84)]:
        filename = 'mol_ulice_cetrtne_skupnosti_' + name + '.json'
        (raw / filename).write_bytes(response[1])
        report['requests'].append({'url': response[0], 'path': 'raw/' + filename,
                                   'sha256': hashlib.sha256(response[1]).hexdigest()})
    (FOLDER / 'cetrtne_skupnosti.json').write_bytes(wgs84[1])
    vic = next(f for f in wgs84[2]['features'] if f['attributes']['CETRT'] == 'VIČ')
    (FOLDER / 'vic.json').write_text(json.dumps(vic, ensure_ascii=False, indent=2))
    (FOLDER / 'boundary_source.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
