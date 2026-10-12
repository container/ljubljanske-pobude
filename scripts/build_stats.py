#!/usr/bin/env python3
"""Statistics for the Statistika tab of one district: all initiatives since 2008, the last three years and,
where the district has our labels, the labelled set. Usage: build_stats.py --district vic"""
import argparse, json, re, statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument('--district', default='vic'); a = ap.parse_args()
C = next(c for c in json.loads((ROOT / 'data/cetrti.json').read_text()) if c['id'] == a.district)
R = json.loads((ROOT / C['mapa'] / f"pobude_{C['id']}.json").read_text())
Y = int(C['zajem'][:4])
OD3 = f"{Y - 3}{C['zajem'][4:]}"   # start of the three-year frame
OD1 = f"{Y - 1}{C['zajem'][4:]}"   # start of the last 12 months
ODVS = f"{Y - C.get('oznake_let', 1)}{C['zajem'][4:]}"   # start of the vrsta + stanje labelled window
day = lambda s: datetime.fromisoformat(s).date()
ms = lambda v: datetime.fromtimestamp(v / 1000, timezone.utc).date() if v else None
def late(r):
    dl = ms((r.get('gis_attributes') or {}).get('DATUM_DO_ODGOVORA')); lr = r['last_response_date']
    return None if not (dl and lr) else day(lr) > dl
def delay(r):
    return (day(r['last_response_date']) - day(r['reported_date'])).days if r['last_response_date'] else None
med = lambda xs: round(statistics.median(xs), 1) if xs else None
pct = lambda a, b: round(100 * a / b) if b else None
serv = lambda s: re.sub(r'^Odgovor (pripravil|v pripravi)\s*:\s*', '', s or '') or '—'

years = []
for y in range(2008, Y + 1):
    g = [r for r in R if r['reported_date'][:4] == str(y)]
    lt = [late(r) for r in g if late(r) is not None]
    years.append({'leto': y, 'n': len(g), 'odgovorjenih': sum(r['portal_status'] == 'odgovorjena' for r in g),
                  'z_rokom': len(lt), 'zamujeno_pct': pct(sum(lt), len(lt)) if len(lt) >= 50 else None,
                  'mediana_dni': med([d for d in map(delay, g) if d is not None])})

rec = {r['id']: r for r in R}
all3 = [r for r in R if r['reported_date'] >= OD3]
lt3 = [late(r) for r in all3 if late(r) is not None]
ltall = [late(r) for r in R if late(r) is not None]
stats = {
    'vse_zamujeno_pct': pct(sum(ltall), len(ltall)), 'vse_z_rokom': len(ltall), 'vse_mediana': med([d for d in map(delay, R) if d is not None]),
    'skupaj': len(R), 'odgovorjenih': sum(r['portal_status'] == 'odgovorjena' for r in R), 'od': min(r['reported_date'] for r in R),
    'do': max(r['reported_date'] for r in R), 'od3': OD3, 'od1': OD1, 'zajem': C['zajem'],
    'tri_leta': len(all3), 'zamujeno3_pct': pct(sum(lt3), len(lt3)),
    'mediana3': med([d for d in map(delay, all3) if d is not None]), 'leta': years,
}

def group(items, key, recs, labelled):
    out = defaultdict(list)
    for x in items: out[key(x)].append(x)
    rows = []
    for k, g in out.items():
        rs = [recs(x) for x in g]; lt = [late(r) for r in rs if late(r) is not None]
        row = {'k': k, 'n': len(g), 'zamujeno_pct': pct(sum(lt), len(lt)), 'mediana_dni': med([d for d in map(delay, rs) if d is not None])}
        if labelled:
            st = Counter(l['stanje'] for l in g)
            row.update({'leto12': sum(l['prijava'] >= OD1 for l in g), 'varnost': sum(l['varnost'] == 'da' for l in g),
                        'stanja': dict(st), 'brez_odziva_pct': pct(st['S0'] + st['S1'] + st['S3'], len(g))})
            row = {k2: row[k2] for k2 in ('k', 'n', 'leto12', 'varnost', 'stanja', 'brez_odziva_pct', 'zamujeno_pct', 'mediana_dni')}
        else:
            row['leto12'] = sum(r['reported_date'] >= OD1 for r in rs)
            row['neodgovorjenih'] = sum(r['portal_status'] != 'odgovorjena' for r in rs)
        rows.append(row)
    return sorted(rows, key=lambda r: -r['n'])

if C['oznake']:
    L = {l['id']: l for l in json.loads((ROOT / 'analysis/teme/teme_oznake.json').read_text())}
    lab = [l for l in L.values() if l['koga'] == 'da' and l['lokacija'] != 'izven']
    labr = [rec[l['id']] for l in lab]
    ltl = [late(r) for r in labr if late(r) is not None]
    stats.update({
        'lok_zamujeno_pct': pct(sum(ltl), len(ltl)), 'lok_mediana': med([d for d in map(delay, labr) if d is not None]),
        'lok_zavrnjeno_pct': pct(sum(1 for l in lab if l['stanje'] in ('S0', 'S1', 'S2')), len(lab)), 'lokalnih': len(lab),
        'stanja': dict(Counter(l['stanje'] for l in lab)),
        'teme': group(lab, lambda l: l['tema2'], lambda l: rec[l['id']], True),
        'sluzbe': [s for s in group(lab, lambda l: serv(l['odgovoril']), lambda l: rec[l['id']], True) if s['n'] >= 3],
    })
else:
    stats['neodgovorjenih3'] = sum(r['portal_status'] != 'odgovorjena' for r in all3)
    stats['sluzbe'] = [s for s in group(all3, lambda r: serv(r['respondents_text']), lambda r: r, False) if s['n'] >= 10]
    stats['kategorije'] = group(all3, lambda r: r['category'] or ('Šifra ' + str(r['category_id']) + ', naziv ni znan' if r['category_id'] else 'Brez kategorije'), lambda r: r, False)
    vs = ROOT / 'analysis/cetrti' / C['id'] / 'oznake_vrsta_stanje.json'
    if vs.exists():  # vrsta + stanje labels for the last oznake_let years
        V = json.loads(vs.read_text())
        for v in V: v['prijava'] = rec[v['id']]['reported_date']; v['varnost'] = ''
        rv = [rec[v['id']] for v in V]; ltv = [late(r) for r in rv if late(r) is not None]
        stats['vs'] = {'n': len(V), 'od': ODVS, 'stanja': dict(Counter(v['stanje'] for v in V)),
                       'zavrnjeno_pct': pct(sum(1 for v in V if v['stanje'] in ('S0', 'S1', 'S2')), len(V)),
                       'brez_zaveze_pct': pct(sum(1 for v in V if v['stanje'] in ('S0', 'S1', 'S3')), len(V)),
                       'zaveza_pct': pct(sum(1 for v in V if v['stanje'] in ('S5', 'S6')), len(V)), 'zamujeno_pct': pct(sum(ltv), len(ltv)),
                       'vrste': group([v for v in V if v['vrsta']], lambda v: v['vrsta'], lambda v: rec[v['id']], True),
                       'sluzbe': [x for x in group(V, lambda v: serv(rec[v['id']]['respondents_text']), lambda v: rec[v['id']], True) if x['n'] >= 5]}

out = ROOT / 'analysis/cetrti' / C['id'] / 'statistika.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(stats, ensure_ascii=False, indent=1))
print(C['id'], json.dumps({k: stats.get(k) for k in ('skupaj', 'odgovorjenih', 'tri_leta', 'lokalnih', 'zamujeno3_pct', 'mediana3')}))
