#!/usr/bin/env python3
"""Download CARTO light basemap tiles (OpenStreetMap data) for ČS Vič once, to ship with the map page.
z12–16 cover the whole district; z17 only tiles around initiative points."""
import json, math, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/teme/tiles'
W, S, E, N = 14.427, 45.991, 14.504, 46.054
def tile(lon, lat, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
want = set()
for z in range(12, 17):
    x0, y0 = tile(W, N, z); x1, y1 = tile(E, S, z)
    want |= {(z, x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
for p in json.loads((ROOT / 'analysis/oznacevanje/oznake_544.json').read_text()):
    x, y = tile(p['lon'], p['lat'], 17)
    want |= {(17, x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
got = 0
for z, x, y in sorted(want):
    f = OUT / f'{z}/{x}/{y}.png'
    if f.exists(): continue
    f.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(f'https://{"abcd"[(x + y) % 4]}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', headers={'User-Agent': 'vic-pobude-analysis/1.0'})
    f.write_bytes(urllib.request.urlopen(req, timeout=30).read()); got += 1
    time.sleep(0.05)
print(len(want), 'ploščic,', got, 'novih')
