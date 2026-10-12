#!/usr/bin/env python3
"""Group labelled initiatives into cases (zadeve) by street key, theme and distance; attach older history candidates."""
import json, math, re, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'analysis/oznacevanje'
L = json.loads((D / 'oznake_544.json').read_text())
ALL = json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())
UNKNOWN = {'', '?', 'neznano', 'neznana lokacija', 'neznana ulica', 'neznana cesta', 'mol', 'ljubljana', 'vic', 'mol ogdp', 'lpp'}

def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

def street(zadeva):
    loc = zadeva.split('|')[0]
    first = re.split(r'[×,(]| x | pri | ob ', loc)[0]
    k = fold(re.sub(r'\d+[a-zA-Z]?(–\d+)?', '', first)).strip(' -.')
    k = re.sub(r'\b(ulica|ul\.)$', '', k).strip()
    return '' if k in UNKNOWN or k.startswith('nezna') else k

def dist(a, b):
    lat = math.radians((a['lat'] + b['lat']) / 2)
    return math.hypot((a['lon'] - b['lon']) * 111320 * math.cos(lat), (a['lat'] - b['lat']) * 111320)

for l in L:
    l['ulica'] = street(l['zadeva'])
# Leader clustering: a record joins the earliest case of the same street and theme whose first point is within RADIUS,
# or any case with a point within NEAR metres and the same theme. Avoids chaining along long streets.
RADIUS, NEAR = 220, 40
cases_tmp = []
for l in sorted(L, key=lambda l: (l['prijava'], l['id'])):
    home = None
    for c in cases_tmp:
        lead = c[0]
        same_theme = l['tema'] and l['tema'] == lead['tema'] and l['tema'] != 'drugo'
        same_street = l['ulica'] and l['ulica'] == lead['ulica']
        if (same_street and same_theme and dist(l, lead) < RADIUS) or (same_street and not l['tema'] and not lead['tema'] and dist(l, lead) < NEAR) \
           or (same_theme and (not l['ulica'] or not lead['ulica'] or same_street) and any(dist(l, m) < NEAR for m in c)):
            home = c; break
    (home.append(l) if home else cases_tmp.append([l]))
groups = {i: c for i, c in enumerate(cases_tmp)}

GENERIC = {'ulica', 'cesta', 'ceste', 'predl', 'uredi', 'preho', 'pesce', 'pesci', 'parki', 'vozni', 'varno', 'promet', 'prome', 'skozi', 'pelje', 'otrok', 'nevar', 'jamov', 'trzas', 'obnov', 'dotra', 'izbri'}
RANK = {'visoka': 3, 'srednja': 2, 'nizka': 1}
older = [r for r in ALL if r['reported_date'] < '2023-09-29']
cases = []
for members in groups.values():
    members.sort(key=lambda l: l['prijava'])
    lat = sum(m['lat'] for m in members) / len(members); lon = sum(m['lon'] for m in members) / len(members)
    streets = [m['ulica'] for m in members if m['ulica']]
    keys = {max(set(streets), key=streets.count)} if streets else set()
    stems = {w[:5] for m in members for w in re.findall(r'\w{5,}', fold(m['zadeva'].split('|')[-1])) if w[:5] not in GENERIC}
    hist = []
    for r in older:
        g = r['geometry_wgs84']
        if min(dist(m, {'lat': g['y'], 'lon': g['x']}) for m in members) < 150:
            txt = fold((r['title'] or '') + ' ' + (r['initiative_text'] or ''))
            if any(k[:7] in txt for k in keys) and sum(st in txt for st in stems) >= 1 and any(fold(r['title'] or '').find(k[:6]) >= 0 for k in keys):
                hist.append({'id': r['id'], 'prijava': r['reported_date'], 'naslov': r['title'].strip()})
    first = min([m['prijava'] for m in members] + [h['prijava'] for h in hist])
    stanja = [m['stanje'] for m in members]
    c = {
        'ids': [m['id'] for m in members], 'n': len(members),
        'naslov': max(members, key=lambda m: (RANK[m['relevanca']], m['prijava']))['zadeva'],
        'tema': max(set(m['tema'] for m in members), key=[m['tema'] for m in members].count),
        'prva_prijava_3l': members[0]['prijava'], 'zadnja_prijava': members[-1]['prijava'],
        'zgodovina_pred_2023': sorted(hist, key=lambda h: h['prijava']), 'prva_prijava_vse': first,
        'let_odprto': round((29 + 9 * 30.4 + 2026 * 365.25 - (int(first[:4]) * 365.25 + int(first[5:7]) * 30.4 + int(first[8:]))) / 365.25, 1),
        'relevanca': max((m['relevanca'] for m in members), key=RANK.get),
        'varnost': 'da' if any(m['varnost'] == 'da' for m in members) else 'ne',
        'koga': 'da' if any(m['koga'] == 'da' for m in members) else 'ne',
        'lokacija_izven': any(m['lokacija'] == 'izven' for m in members),
        'stanja': stanja, 'zadnje_stanje': members[-1]['stanje'],
        'zavrnjeno': stanja.count('S1'), 'brez_zaveze': stanja.count('S3'), 'izvedeno': stanja.count('S6'),
        'prepozni': sum(m['prepozen_odgovor'] == 'da' for m in members),
        'izvajalci': sorted({m['izvajalec'] for m in members}),
        'teren': [m['teren'] for m in members if m.get('teren')],
        'lat': lat, 'lon': lon,
    }
    rep = c['n'] + min(len(hist), 6) / 2
    c['prioriteta'] = round(RANK[c['relevanca']] * 2 + (2 if c['varnost'] == 'da' else 0) + math.log2(rep) * 1.5 + min(c['let_odprto'], 15) / 3
                            + (1.5 if c['zavrnjeno'] else 0) + (1 if c['brez_zaveze'] or c['prepozni'] else 0)
                            - (3 if c['koga'] == 'ne' else 0) - (4 if c['lokacija_izven'] else 0) - (2 if c['zadnje_stanje'] == 'S6' else 0), 1)
    cases.append(c)
cases.sort(key=lambda c: -c['prioriteta'])
for c in cases:  # stable across priority changes: named after the earliest member
    c['zadeva_id'] = f"Z{c['ids'][0]}"
(D / 'zadeve.json').write_text(json.dumps(cases, ensure_ascii=False, indent=1))
multi = [c for c in cases if c['n'] + len(c['zgodovina_pred_2023']) > 1]
print(len(cases), 'zadev;', len(multi), 's ponovitvami;', max(c['n'] for c in cases), 'največ pobud v zadevi')
for c in cases[:40]:
    print(c['zadeva_id'], c['prioriteta'], c['n'], '+', len(c['zgodovina_pred_2023']), c['prva_prijava_vse'][:4], c['relevanca'][0], c['varnost'], ''.join(s[-1] for s in c['stanja']), '|', c['naslov'][:75])
