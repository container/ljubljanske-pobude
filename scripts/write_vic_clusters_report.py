#!/usr/bin/env python3
"""Render the manually reviewed 100 m Vič problem-cluster selection as Markdown."""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/clusters_100m_2026-10-12'
RECORDS = {r['id']: r for r in json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())}
LABELS = {r['id']: r for r in json.loads((ROOT / 'analysis/oznacevanje/oznake_544.json').read_text())}
GROUPS = json.loads((OUT / 'selection.json').read_text())
CUTOFF = '2024-10-12'


def distance(a, b):
    x, y = a['geometry_wgs84'], b['geometry_wgs84']
    lat = math.radians((x['y'] + y['y']) / 2)
    return math.hypot((x['x'] - y['x']) * 111320 * math.cos(lat), (x['y'] - y['y']) * 111320)


def link(i):
    return f'[{i}](../../data/vic_2026-09-29/raw/details/{i}.txt)'


lines = [
    '# Pobude, podobne znotraj 100 m — ČS Vič',
    '',
    'Delovni seznam vsebinsko pregledanih skupin. Podatkovni posnetek: **29. 9. 2026**. '
    'Izhodiščne pobude so od **12. 10. 2024** dalje in niso označene kot vprašanja (V7). '
    'Starejše pobude so dodane kot zgodovinski kandidati. Število pobud ni število različnih oseb ali dogodkov.',
    '',
    'Merilo prostora: pobude smo povezali, kadar sta lokaciji največ 100 m narazen in besedilo opisuje isti konkreten problem. '
    'Povezava se lahko nadaljuje prek več bližnjih pobud, zato se lahko dolga ulica razteza čez več kot 100 m. '
    'Vsebino in odgovor smo pregledali ročno; semantični zadetki sami niso bili dovolj za vključitev.',
    '',
    'Urejeno po pomenu za lokalni življenjski prostor. Med zapisi so tudi ožje vzdrževalne težave, prijave z navedeno izvedbo in predlogi za P+R; '
    'ti niso samodejno razglašeni za nerešene ali prednostne. Status »odgovorjeno« sam po sebi ne potrjuje odprave.',
    '',
    '## Ponavljajoče se lokalne težave',
    '',
    '| # | Problem | Novejše + starejše pobude | Obdobje | Pobude (novejše prve) |',
    '|---:|---|---:|---|---|',
]

total_seeds = set()
total_members = set()
for n, g in enumerate(GROUPS, 1):
    rows = [RECORDS[i] for i in g['ids']]
    seeds = [r for r in rows if r['reported_date'] >= CUTOFF and LABELS[r['id']]['vrsta'] != 'V7']
    older = [r for r in rows if r['reported_date'] < CUTOFF]
    assert seeds, f"No recent seed in group {g['name']}"
    # Every older historical addition must be near at least one qualifying recent seed.
    too_far = [(r['id'], min(distance(r, s) for s in seeds)) for r in older
               if min(distance(r, s) for s in seeds) > 100]
    assert not too_far, (g['name'], too_far)
    assert len(rows) == len(set(g['ids']))
    total_seeds.update(r['id'] for r in seeds)
    total_members.update(g['ids'])
    newest = max(r['reported_date'] for r in rows)
    oldest = min(r['reported_date'] for r in rows)
    sorted_rows = sorted(rows, key=lambda r: (r['reported_date'] < CUTOFF, r['reported_date'], r['id']), reverse=True)
    ids = ', '.join(link(r['id']) for r in sorted_rows)
    category = f"; **{g['category']}**" if g['category'] != 'lokalni problem' else ''
    lines.append(f"| {n} | {g['name']}{category} | {len(seeds)} + {len(older)} | {oldest}–{newest} | {ids} |")

recent_total = sum(1 for r in RECORDS.values() if r['reported_date'] >= CUTOFF and LABELS[r['id']]['vrsta'] != 'V7')
lines += [
    '',
    '## Opombe k združevanju in stanju',
    '',
]
for n, g in enumerate(GROUPS, 1):
    lines.append(f"**{n}. {g['name']}** — {g['review_note']}")
lines += [
    '',
    '## Meje tega pregleda',
    '',
    f"V skupine je vključenih **{len(total_members)} različnih pobud** izmed {recent_total} novejših izhodiščnih pobud. "
    f"Skupine vsebujejo {len(total_seeds)} različnih novejših izhodiščnih pobud; neuvrščene izhodiščne pobude nimajo dovolj jasnega, bližnjega vsebinskega ujemanja za varen ročni spoj.",
    '',
    'Filter V7 temelji na oznakah iz vsebinskega označevanja (50 pregledanih, preostale strojne oznake). '
    'Lahko vsebuje napačno izključene ali vključene pobude. Starejši portalni zapisi so dodani po bližini in ročno presojeni; '
    'daljša časovna vrzel ne dokazuje, da se težava vmes ni odpravila in znova pojavila. Pri nekaterih parih je možnost podvojene objave. '
    'Priloge in fotografije niso bile pregledane, odgovori pa niso neodvisen pregled stanja na terenu.',
    '',
    'Vir vseh ID-jev so surova besedila iz zajema portala. Povezave v tabeli odpirajo pobudo in odgovor po ID-ju.',
    '',
]
(OUT / 'clusters.md').write_text('\n'.join(lines), encoding='utf-8')
print(f"Wrote {OUT / 'clusters.md'}: {len(GROUPS)} groups, {len(total_members)} distinct records, {len(total_seeds)} seeds")
