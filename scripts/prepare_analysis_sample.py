#!/usr/bin/env python3
"""Reproducible exploratory sample; no prevalence estimates or automatic resolution labels."""
import json
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/vic_pilot'
OUT.mkdir(parents=True, exist_ok=True)
all_records = json.loads((ROOT / 'data/vic_2026-09-29/pobude_vic.json').read_text())
recent = [r for r in all_records if r['reported_date'] and '2023-09-29' <= r['reported_date'] <= '2026-09-29']
groups = {
    'glinska_oslavijska': [78454, 78529, 81438, 84715, 83805],
    'jamova_vrtec_klancine': [73605, 76835, 81348],
    'jadranska_jamova_semafor': [75814, 80633],
    'vrhovnikova_pesci': [70927, 76834, 77952, 79303, 81574, 86025, 86027, 86041],
    'gorice_ciscenje': [71215, 70231, 83644],
    'gorice_rastje': [74182, 74946],
    'gorice_prehodi': [78011, 83643, 84907],
    'dolgi_most_wc': [67748, 68016, 68829, 82472],
    'nahlikova_parkiranje': [80840, 82046],
    'zabojniki_robidovje': [74102, 74496],
    'pot_pst_odpadki': [68857, 71553],
}
core_ids = {i for ids in groups.values() for i in ids}
assert core_ids <= {r['id'] for r in recent}
remaining = sorted([r for r in recent if r['id'] not in core_ids], key=lambda r: (r['reported_date'], r['id']))
n = 100 - len(core_ids)
context_ids = {remaining[round(i*(len(remaining)-1)/(n-1))]['id'] for i in range(n)}
sample = sorted([r for r in recent if r['id'] in core_ids | context_ids], key=lambda r:(r['reported_date'],r['id']))
assert len(sample) == 100
for r in sample:
    r['sample_role'] = 'targeted_followup' if r['id'] in core_ids else 'systematic_time_context'
    r['candidate_groups'] = [name for name, ids in groups.items() if r['id'] in ids]
(OUT / 'sample_100.json').write_text(json.dumps(sample, ensure_ascii=False, indent=2))
(OUT / 'sample_method.json').write_text(json.dumps({'source_records':len(all_records),'recent_frame':len(recent),'period':['2023-09-29','2026-09-29'], 'targeted_records':len(core_ids),'context_records':len(context_ids),'sample_size':len(sample),'candidate_groups':groups,'selection':'36 targeted follow-up records from text screening of 544 recent initiatives, plus 64 systematically spaced chronological context records from the remainder. Purposive exploratory design; not a representative sample.'},ensure_ascii=False,indent=2))
text=['# Viri za pilotno analizo – vzorec 100 pobud', '', 'Posnetek portala: 29. september 2026. ID omogoča povezavo z izvirnim zajemom. Datum odgovora je datum zadnjega odgovora v posnetku, ne dokaz izvedbe.','']
for r in sample:
    g=r['geometry_wgs84']
    text += [f"## Pobuda {r['id']}: {r['title'].strip()}",'',f"Prijava: {r['reported_date']}; zadnji odgovor: {r['last_response_date'] or 'brez odgovora'}; status: {r['portal_status']}.",f"Točka portala: {g['y']:.6f}, {g['x']:.6f}. Vzorec: {r['sample_role']}.",f"Izvirnik: [odziv portala](../../data/vic_2026-09-29/{r['raw_detail_path']}).",'','**Pobuda**','',r['initiative_text'],'','**Odgovor**','',r['respondents_text'],r['response_text'] or '(V posnetku ni odgovora.)','']
(OUT/'viri_100.md').write_text('\n'.join(text),encoding='utf-8')
def distance(a,b):
    a,b=a['geometry_wgs84'],b['geometry_wgs84']; lat=math.radians((a['y']+b['y'])/2)
    return math.hypot((a['x']-b['x'])*111320*math.cos(lat),(a['y']-b['y'])*111320)
byid={r['id']:r for r in sample}
for group,ids in groups.items():
    points=[byid[i] for i in ids]
    print(group, len(ids), 'max_point_separation_m',round(max(distance(a,b) for a in points for b in points)))
print('Sample:',len(sample),'Targeted:',len(core_ids),'Context:',len(context_ids))
