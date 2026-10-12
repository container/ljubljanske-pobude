#!/usr/bin/env python3
"""Read-only, resumable capture of public Ljubljana initiatives by district dropdown."""
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://pobude.ljubljana.si/'
PAGES = {'odgovorjena': 'PregledOdgovorjenihPobud.aspx', 'neodgovorjena': 'PregledObjavljenihPobud.aspx'}
DISTRICTS = {'vic': ('VIČ', '15'), 'center': ('CENTER', '11'), 'siska': ('ŠIŠKA', '8')}
SERVICE = BASE + 'arcgis/rest/services/MolPobudeSQL_L/MolPobudeTemePublic/MapServer/0'
MONTHS = dict(zip('januar februar marec april maj junij julij avgust september oktober november december'.split(), range(1, 13)))

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden, self.text, self.links = {}, [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('type') == 'hidden' and 'name' in a:
            self.hidden[a['name']] = a.get('value', '')
        if tag in ('br', 'p', 'div', 'li', 'tr', 'h3'):
            self.text.append('\n')
        for key in ('href', 'src'):
            if a.get(key) and not a[key].startswith(('javascript:', '#', 'data:')):
                self.links.append({'tag': tag, 'attribute': key, 'url': urllib.parse.urljoin(BASE, a[key])})
    def handle_endtag(self, tag):
        if tag in ('p', 'div', 'li', 'tr', 'h3'):
            self.text.append('\n')
    def handle_data(self, text):
        self.text.append(text)

def decoded(value):
    for _ in range(3):
        next_value = html.unescape(value)
        if next_value == value:
            break
        value = next_value
    return value

def plaintext(value):
    p = Markup(); p.feed(decoded(value))
    return re.sub(r'\n\s*\n+', '\n\n', ''.join(p.text)).strip()

def date_iso(value):
    value = plaintext(value).strip()
    if not value:
        return None
    m = re.fullmatch(r'(\d+)\.\s+(\w+)\s+(\d{4})', value)
    if not m or m[2] not in MONTHS:
        raise ValueError('Unknown date: ' + value)
    return dt.date(int(m[3]), MONTHS[m[2]], int(m[1])).isoformat()

class Client:
    def __init__(self, folder, district='vic'):
        self.folder = folder
        self.district = district
        self.district_label, self.district_value = DISTRICTS[district]
        self.last = 0
        self.opener = urllib.request.build_opener()
    def request(self, url, data=None):
        for attempt in range(5):
            time.sleep(max(0, .20 - (time.monotonic() - self.last)))
            self.last = time.monotonic()
            try:
                req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                    headers={'User-Agent': 'LjubljanaPublicInitiativesResearch/1.0 (read-only; sequential capture)'})
                with self.opener.open(req, timeout=45) as response:
                    return response.read().decode('utf-8-sig')
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
    def form(self, status, suffix=''):
        path = self.folder / 'raw' / (status + suffix + '_page.html')
        body = self.request(BASE + PAGES[status]); path.write_text(body, encoding='utf-8')
        p = Markup(); p.feed(body)
        # Verify the exact dropdown option rather than inferring a spatial boundary.
        select = re.search(r'<select[^>]*id="ddlCetrtnaSkupnost"[^>]*>(.*?)</select>', body, re.S)
        if not select or not re.search(r'<option\s+value="' + re.escape(self.district_value) + '">' + re.escape(self.district_label) + '</option>', select[1]):
            raise ValueError(self.district_label + ' dropdown value has changed')
        p.hidden.update({'__CALLBACKID': '__Page', 'ddlVrstaPobude': '0', 'ddlCetrtnaSkupnost': self.district_value, 'rbDatum': '0'})
        return p.hidden
    def callback(self, status, form, argument):
        return self.request(BASE + PAGES[status], dict(form, __CALLBACKPARAM=argument))
    def gis(self, params):
        url = BASE + 'gdi_proxy/proxy.ashx?' + SERVICE + '/query?' + urllib.parse.urlencode(params)
        result = json.loads(self.request(url))
        if 'error' in result:
            raise ValueError(result['error'])
        return result

def parse_list(body, status):
    body = body.replace('\\"', '"')
    count = re.search(r'Število pobud:.*?>(\d+)</span>', body)
    rows = re.findall(r"<tr><td><span[^>]*>(.*?)</span></td><td>(.*?)</td><td><a onclick='pobudePrikazi\((\d+)\)'", body, re.S)
    result = [{'id': int(i), 'portal_status': status, 'list_date': date_iso(d), 'list_title': html.unescape(t)} for d,t,i in rows]
    if not count or len(result) != int(count[1]) or len({r['id'] for r in result}) != len(result):
        raise ValueError(f'List count mismatch for {status}: {len(result)}')
    return result

def parse_detail(body, row):
    match = re.search(r'setPobudaInfo\((.*?)\);(?=\\*"\s*\})', body, re.S)
    if not match:
        raise ValueError('Missing setPobudaInfo')
    args = re.split(r"',\s*'", match[1][1:-1])
    if row['portal_status'] == 'neodgovorjena' and len(args) == 9:
        args = args[:7] + ['', '', ''] + args[7:]
    if len(args) != 12:
        raise ValueError(f'Expected 12 detail arguments, got {len(args)}')
    names = ['reported_date_raw', 'district', 'title', 'initiative_html', 'initiative_attachments_html',
             'published_date_raw', 'respondents_html', 'last_response_date_raw', 'responses_html',
             'response_attachments_html', 'source_x_raw', 'source_y_raw']
    item = dict(row, **dict(zip(names, args)))
    for field in ('district', 'title', 'initiative_html', 'initiative_attachments_html', 'respondents_html', 'responses_html', 'response_attachments_html'):
        item[field] = decoded(item[field])
    item.update(reported_date=date_iso(args[0]), published_date=date_iso(args[5]), last_response_date=date_iso(args[7]),
                initiative_text=plaintext(args[3]), response_text=plaintext(args[8]), respondents_text=plaintext(args[6]))
    item['source_x'] = float(args[10]) if args[10] else None
    item['source_y'] = float(args[11]) if args[11] else None
    links = []
    for field in ('initiative_attachments_html', 'response_attachments_html'):
        p = Markup(); p.feed(item[field])
        links += [dict(link, source_field=field) for link in p.links]
    item['attachment_links'] = links
    item['source_page'] = BASE + PAGES[row['portal_status']]
    item['source_callback_argument'] = str(item['id']) + '::::getpobudatext'
    item['raw_detail_path'] = 'raw/details/' + str(item['id']) + '.txt'
    item['raw_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    return item

def newest_first(rows, geometry):
    """Interleave both statuses by GIS entry time, with undated rows last."""
    def key(row):
        feature = geometry.get(str(row['id'])) or {}
        timestamp = (feature.get('attributes') or {}).get('DATUM_VNOSA')
        return (timestamp is not None, timestamp if timestamp is not None else 0, row['id'])
    return sorted(rows, key=key, reverse=True)

def priority_rows(rows, geometry, since):
    selected = []
    for row in rows:
        timestamp = ((geometry.get(str(row['id'])) or {}).get('attributes') or {}).get('DATUM_VNOSA')
        if timestamp is None:
            raise ValueError(f"Cannot determine priority period for initiative {row['id']}")
        # The service encodes the portal's calendar date in the UTC date portion.
        date = dt.datetime.fromtimestamp(timestamp / 1000, dt.timezone.utc).date()
        if date >= since:
            selected.append(row)
    return selected

def checkpoint_priority(folder, selected, all_rows, geometry, started, district, since):
    """Write and validate a self-contained recent-period capture before older details."""
    target = folder / 'zadnja_3_leta'
    (target / 'raw/details').mkdir(parents=True, exist_ok=True)
    for row in selected:
        name = str(row['id']) + '.txt'
        body = (folder / 'raw/details' / name).read_text(encoding='utf-8')
        record = parse_detail(body, row)
        if not record['reported_date'] or record['reported_date'] < since.isoformat():
            raise ValueError(f"GIS/detail date discrepancy at priority boundary: {row['id']}")
        shutil.copy2(folder / 'raw/details' / name, target / 'raw/details' / name)
    for path in (folder / 'raw').glob('*'):
        if path.is_file():
            shutil.copy2(path, target / 'raw' / path.name)
    shutil.copy2(folder / 'capture_config.json', target / 'capture_config.json')
    save_json(target / 'index.json', selected)
    save_json(target / 'full_source_index.json', all_rows)
    save_json(target / 'geometry.json', {str(r['id']): geometry[str(r['id'])] for r in selected})
    save_json(target / 'capture_scope.json', {'scope': 'reported_since', 'reported_since_inclusive': since.isoformat(),
        'full_source_count': len(all_rows), 'selected_count': len(selected)})
    if not export(target, selected, geometry, [], started, district):
        raise ValueError('Priority capture export failed')
    for script in ('verify_source_lists.py', 'package_capture.py'):
        args = [sys.executable, '-B', str(ROOT / 'scripts' / script), '--folder', str(target)]
        if script == 'package_capture.py':
            args.append('--validate-only')
        subprocess.run(args, check=True)
    print(f'PRIORITY VERIFIED {len(selected)} records since {since}: {target}', flush=True)

def export(folder, rows, geometry, errors, started, district='vic'):
    district_label, district_value = DISTRICTS[district]
    basename = 'pobude_' + district
    records, parse_errors = [], []
    page = (folder / 'raw/odgovorjena_page.html').read_text(encoding='utf-8')
    select = re.search(r'<select[^>]*id="ddlVrstaPobude"[^>]*>(.*?)</select>', page, re.S)
    categories = {int(i): html.unescape(label) for i, label in re.findall(r'<option[^>]*value="(\d+)"[^>]*>(.*?)</option>', select[1])}
    save_json(folder / 'categories.json', categories)
    for row in rows:
        path = folder / 'raw/details' / (str(row['id']) + '.txt')
        try:
            item = parse_detail(path.read_text(encoding='utf-8'), row)
            item['captured_at'] = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()
            feature = geometry.get(str(row['id']))
            item['gis_attributes'] = feature.get('attributes') if feature else None
            item['category_id'] = item['gis_attributes'].get('MOL_VRSTE_POBUD_ID') if feature else None
            item['category'] = categories.get(item['category_id'])
            item['geometry_wgs84'] = feature.get('geometry') if feature else None
            item['geometry_status'] = 'available' if item['geometry_wgs84'] else 'missing'
            records.append(item)
        except Exception as e:
            parse_errors.append({'id': row['id'], 'error': str(e)})
    records.sort(key=lambda r: (r['reported_date'] or '', r['id']), reverse=True)
    save_json(folder / (basename + '.json'), records)
    with (folder / (basename + '.jsonl')).open('w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    features = []
    for record in records:
        geom = record['geometry_wgs84']
        features.append({'type': 'Feature', 'id': record['id'], 'geometry': {'type': 'Point', 'coordinates': [geom['x'], geom['y']]} if geom else None,
                         'properties': {key: record[key] for key in ('id', 'portal_status', 'district', 'category_id', 'category', 'title', 'reported_date', 'published_date', 'last_response_date', 'initiative_text', 'response_text', 'respondents_text', 'source_page', 'geometry_status')}})
    save_json(folder / (basename + '.geojson'), {'type': 'FeatureCollection', 'features': features})
    db = sqlite3.connect(folder / (basename + '.sqlite'))
    db.execute('CREATE TABLE IF NOT EXISTS initiatives (id INTEGER PRIMARY KEY, portal_status TEXT, district TEXT, title TEXT, reported_date TEXT, published_date TEXT, last_response_date TEXT, initiative_text TEXT, response_text TEXT, respondents_text TEXT, longitude REAL, latitude REAL, record_json TEXT)')
    db.execute('DELETE FROM initiatives')
    for r in records:
        g = r['geometry_wgs84'] or {}
        db.execute('INSERT OR REPLACE INTO initiatives VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (r['id'],r['portal_status'],r['district'],r['title'],r['reported_date'],r['published_date'],r['last_response_date'],r['initiative_text'],r['response_text'],r['respondents_text'],g.get('x'),g.get('y'),json.dumps(r,ensure_ascii=False)))
    db.commit(); db.close()
    report = {'started_at': started, 'finished_at': now(), 'filter': {'district_label':district_label,'district_value':district_value,'category':'Vse pobude','period':'Vse','spatial_reclassification':False},
              'expected':len(rows),'captured':len(records),'by_status':{s:sum(r['portal_status']==s for r in records) for s in PAGES},
              'record_order':'reported_date_desc_id_desc',
              'with_geometry':sum(bool(r['geometry_wgs84']) for r in records),
              'without_geometry':[r['id'] for r in records if not r['geometry_wgs84']],
              'district_mismatches':[r['id'] for r in records if r['district']!=district_label],
              'answered_without_response_text':[r['id'] for r in records if r['portal_status']=='odgovorjena' and not r['response_text']],
              'attachment_link_count':sum(len(r['attachment_links']) for r in records),
              'with_attachment_links':sum(bool(r['attachment_links']) for r in records),
              'reported_date_min':min((r['reported_date'] for r in records if r['reported_date']),default=None),
              'reported_date_max':max((r['reported_date'] for r in records if r['reported_date']),default=None),
              'first_detail_captured_at':min((r['captured_at'] for r in records),default=None),
              'last_detail_captured_at':max((r['captured_at'] for r in records),default=None),
              'category_ids_without_label':sorted({r['category_id'] for r in records if r['category_id'] is not None and not r['category']}),
              'network_errors':errors, 'parse_errors':parse_errors,
              'notes':['Only dropdown membership determines inclusion.','Portal status is response status, not verified resolution.','All response HTML returned by the public detail is preserved; last_response_date is not necessarily first response.','Attachment links retained; binary attachments not downloaded.','WGS84 returned by source GIS; no spatial filtering or reassignment.']}
    if (folder / 'capture_scope.json').exists():
        report['scope'] = json.loads((folder / 'capture_scope.json').read_text())
    save_json(folder / 'capture_report.json', report)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return not errors and not parse_errors and len(records)==len(rows)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--folder'); parser.add_argument('--district', choices=DISTRICTS, default='vic'); parser.add_argument('--limit',type=int); parser.add_argument('--export-only',action='store_true')
    parser.add_argument('--priority-since', type=dt.date.fromisoformat,
        help='Validate a separate capture from this reported date before downloading older details')
    options = parser.parse_args()
    if options.priority_since and (options.limit or options.export_only):
        parser.error('--priority-since cannot be combined with --limit or --export-only')
    folder = ROOT / (options.folder or ('data/' + options.district + '_' + dt.date.today().isoformat()))
    (folder / 'raw/details').mkdir(parents=True, exist_ok=True)
    started = now(); client = Client(folder, options.district); errors=[]
    metadata_path = folder / 'capture_config.json'
    config = {'district': options.district, 'district_label': client.district_label, 'district_value': client.district_value}
    if metadata_path.exists() and json.loads(metadata_path.read_text()) != config:
        raise ValueError('Capture folder belongs to a different district')
    if (folder / 'capture_report.json').exists():
        previous = json.loads((folder / 'capture_report.json').read_text())
        if previous['filter']['district_value'] != client.district_value:
            raise ValueError('Capture folder belongs to a different district')
    save_json(metadata_path, config)
    if options.export_only:
        rows = json.loads((folder/'index.json').read_text()); geometry=json.loads((folder/'geometry.json').read_text())
        if (folder/'capture_report.json').exists():
            started = json.loads((folder/'capture_report.json').read_text()).get('started_at', started)
    else:
        previous_index = folder / 'index.json'
        previous_rows = {r['id']: r for r in json.loads(previous_index.read_text())} if previous_index.exists() else {}
        forms = {status:client.form(status) for status in PAGES}
        rows=[]
        for status in PAGES:
            response=client.callback(status, forms[status], '0::::' + client.district_value + '::::0::::getpobudaid')
            (folder/'raw'/(status+'_list.txt')).write_text(response,encoding='utf-8')
            part=parse_list(response,status); rows+=part
            print(f'INDEX {status}: {len(part)}',flush=True)
        if len({r['id'] for r in rows})!=len(rows):
            raise ValueError('Overlap between status lists: refresh needed')
        # Invalidate changed cached details before replacing the index, so an
        # interrupted refresh cannot silently reuse a detail from an older row.
        for row in rows:
            path = folder / 'raw/details' / (str(row['id']) + '.txt')
            if path.exists() and previous_rows.get(row['id']) != row:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                backup = folder / 'raw/superseded_details' / (str(row['id']) + '_' + digest + '.txt')
                backup.parent.mkdir(parents=True, exist_ok=True)
                path.replace(backup)
        save_json(folder/'index.json',rows)
        geometry={}
        fields='OBJECTID,MOL_VNESENE_POBUDE_FC_ID,NASLOV_POBUDE,STATUS_POBUDE,MOL_VRSTE_POBUD_ID,DATUM_VNOSA,DATUM_OBRAVNAVE,DATUM_ZADNJEGA_ODGOVORA,DATUM_KONCA_AKTUALNOSTI,DATUM_DO_ODGOVORA,OBRAVNAVA_VEC_ODDELKOV'
        for start in range(0,len(rows),200):
            ids=','.join(str(r['id']) for r in rows[start:start+200])
            result=client.gis({'where':f'MOL_VNESENE_POBUDE_FC_ID IN ({ids})','outFields':fields,'returnGeometry':'true','outSR':'4326','f':'json'})
            save_json(folder/'raw'/f'geometry_{start:04d}.json',result)
            if result.get('exceededTransferLimit'):
                raise ValueError('GIS transfer limit exceeded')
            for feature in result.get('features',[]):
                key=str(feature['attributes']['MOL_VNESENE_POBUDE_FC_ID'])
                if key in geometry:
                    raise ValueError('Duplicate GIS initiative '+key)
                geometry[key]=feature
        save_json(folder/'geometry.json',geometry)
        print(f'GEOMETRY {len(geometry)}/{len(rows)}',flush=True)
        rows = newest_first(rows, geometry)
        save_json(folder/'index.json', rows)
        save_json(folder/'capture_order.json', {
            'order': 'DATUM_VNOSA_desc_id_desc',
            'missing_entry_date_ids': [r['id'] for r in rows if
                ((geometry.get(str(r['id'])) or {}).get('attributes') or {}).get('DATUM_VNOSA') is None],
            'notes': 'Both statuses interleaved; undated records last. Cached details are reused when resuming.',
        })
        selected=rows[:options.limit] if options.limit else rows
        priority = priority_rows(rows, geometry, options.priority_since) if options.priority_since else []
        if options.priority_since:
            print(f'PRIORITY {len(priority)}/{len(rows)} since {options.priority_since}', flush=True)
            if not priority:
                checkpoint_priority(folder, priority, rows, geometry, started, options.district, options.priority_since)
        for n,row in enumerate(selected,1):
            path=folder/'raw/details'/(str(row['id'])+'.txt')
            try:
                if not path.exists():
                    body=client.callback(row['portal_status'],forms[row['portal_status']],str(row['id'])+'::::getpobudatext')
                    if 'setPobudaInfo(' not in body:
                        raise ValueError('Invalid detail response')
                    path.write_text(body,encoding='utf-8')
                if n%100==0 or n==len(selected):
                    print(f'DETAIL {n}/{len(selected)} at {now()}',flush=True)
            except Exception as e:
                errors.append({'id':row['id'],'error':str(e)}); print(f'ERROR {row["id"]}: {e}',flush=True)
            if priority and n == len(priority):
                if errors:
                    raise ValueError('Priority download has errors; resume before fetching older details')
                checkpoint_priority(folder, priority, rows, geometry, started, options.district, options.priority_since)
        if options.limit:
            rows=selected
    if not export(folder,rows,geometry,errors,started,options.district):
        raise SystemExit(1)

if __name__=='__main__':
    main()
