#!/usr/bin/env python3
"""Merge fine themes into labels, assign nearest MOL street to each point, compute theme stats, and write compact map data."""
import glob, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / 'data/meje'
T = ROOT / 'analysis/teme'
L = {l['id']: l for l in json.loads((ROOT / 'analysis/oznacevanje/oznake_544.json').read_text())}
rec = {r['id']: r for r in json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())}
for f in sorted(glob.glob(str(T / 'teme_izhod_*.json'))):
    for t in json.loads(Path(f).read_text()):
        L[int(t['id'])].update({'tema2': t['tema'], 'prenova': t['prenova'], 'podrobno': t['podrobno']})
assert all('tema2' in l for l in L.values())

LAT0 = 46.02
KX, KY = 111320 * math.cos(math.radians(LAT0)), 111320
proj = lambda lon, lat: (round((lon - 14.42) * KX, 1), round((46.06 - lat) * KY, 1))  # metres, y down

def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)

streets = []
for f in json.loads((M / 'ulice_vic.json').read_text()):
    for path in f['geometry']['paths']:
        streets.append((f['attributes']['GURS_UL_IME'], [proj(*p) for p in path]))
def nearest(p):
    best = (1e9, '')
    for name, pts in streets:
        for a, b in zip(pts, pts[1:]):
            d = seg_dist(p, a, b)
            if d < best[0]: best = (d, name)
    return best[1] if best[0] < 120 else ''

RECENT, MID = '2025-09-29', '2024-09-29'
pts = []
for i, l in L.items():
    p = proj(l['lon'], l['lat'])
    l['ulica_mol'] = nearest(p)
    pts.append({'id': i, 'la': round(l['lat'], 6), 'lo': round(l['lon'], 6), 't': l['tema2'], 'd': l['prijava'], 's': l['stanje'], 'v': l['varnost'], 'k': l['koga'],
                'lok': l['lokacija'], 'r': l['relevanca'], 'pr': l['prenova'], 'u': l['ulica_mol'], 'n': l['naslov'], 'po': l['podrobno']})

# Silent locations: street+theme pairs whose reports all predate the last 12 months
last = defaultdict(str)
for q in pts:
    last[(q['u'], q['t'])] = max(last[(q['u'], q['t'])], q['d'])
for q in pts:
    q['ak'] = 'aktualno' if q['d'] >= RECENT else ('utihnilo' if last[(q['u'], q['t'])] < RECENT else 'ponavlja')

stats = {}
for t in {q['t'] for q in pts}:
    g = [q for q in pts if q['t'] == t and q['k'] == 'da' and q['lok'] != 'izven']
    if not g: continue
    yrs = [sum(1 for q in g if lo <= q['d'] < hi) for lo, hi in [('2023-09-29', MID), (MID, RECENT), (RECENT, '2026-09-30')]]
    st = Counter(q['s'] for q in g)
    ul = Counter(q['u'] for q in g if q['u'])
    stats[t] = {'n': len(g), 'leta': yrs, 'varnost': sum(q['v'] == 'da' for q in g), 'ulic': len(ul), 'top_ulice': ul.most_common(5),
                'neodziv': st['S1'] + st['S3'] + st['S0'], 'zavrnjeno': st['S1'], 'brez_zaveze': st['S3'], 'izvedeno': st['S6'] + st['S5'],
                'prenova': sum(q['pr'] == 'da' for q in g), 'visoka': sum(q['r'] == 'visoka' for q in g)}
    s = stats[t]
    s['perecnost'] = round(1.6 * yrs[2] + 0.6 * yrs[1] + 0.3 * yrs[0] + 0.8 * s['varnost'] + 0.6 * s['neodziv'] + 0.5 * s['ulic'] + 0.5 * s['visoka'], 1)

vic = json.loads((M / 'vic.json').read_text())
base = {'meja': [[[round(y, 5), round(x, 5)] for x, y in ring] for ring in vic['geometry']['rings']]}
(T / 'teme_oznake.json').write_text(json.dumps(list(L.values()), ensure_ascii=False, indent=1))
(T / 'karta_podatki.json').write_text(json.dumps({'tocke': pts, 'teme': stats, 'podlaga': base}, ensure_ascii=False))
for t, s in sorted(stats.items(), key=lambda kv: -kv[1]['perecnost']):
    print(f"{t:14} {s['perecnost']:6} n={s['n']:3} leta={s['leta']} varn={s['varnost']:3} neodziv={s['neodziv']:3} ulic={s['ulic']:3} top={[u for u,_ in s['top_ulice'][:3]]}")
print(Counter(q['ak'] for q in pts), 'brez ulice:', sum(1 for q in pts if not q['u']))
