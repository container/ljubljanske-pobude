#!/usr/bin/env python3
"""Prepare cached 100 m comparison candidates; no pair or group is accepted automatically."""
import argparse
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--district", required=True)
parser.add_argument("--cutoff", required=True)
args = parser.parse_args()
district = next(c for c in json.loads((ROOT / "data/cetrti.json").read_text()) if c["id"] == args.district)
out = ROOT / "analysis/cetrti" / args.district / "clusters"
out.mkdir(parents=True, exist_ok=True)
records = json.loads((ROOT / district["mapa"] / ("pobude_" + args.district + ".json")).read_text())
records = {r["id"]: r for r in records}
labels = {l["id"]: l for l in json.loads((ROOT / "analysis/cetrti" / args.district / "oznake_vrsta_stanje.json").read_text())}
overrides_path = out / "seed_type_overrides.json"
overrides = {x["id"]: x for x in json.loads(overrides_path.read_text())} if overrides_path.exists() else {}
stop = set(("prosim spostovani pozdravljeni pozdrav lep lepo hvala odgovor pobuda pobude pobudi "
            "obcina ljubljana mol mesto urejanje ureditev urediti predlagam treba potrebna potrebno "
            "ulica ulice ulici cesti cesta ceste promet prometa varnost varno nevarno "
            "ter tudi kjer zato tako samo saj kjer sicer ali kot ki ker da se in na je so za "
            "pri po do iz ob od ne bi bo vse ni gre sem smo ste nas vam vas nam jih "
            "ze bila bili bilo biti ima imajo pa kar ce naj sedaj vedno ponovno").split())

def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if not unicodedata.combining(c))

def tokens(s):
    return [w[:6] for w in re.findall(r"[a-z]{3,}", fold(s)) if w not in stop]

terms, title_terms, df = {}, {}, Counter()
for i, r in records.items():
    t = Counter(tokens(r["title"]))
    title_terms[i] = t
    terms[i] = Counter(tokens(r["initiative_text"])) + Counter({k: v * 3 for k, v in t.items()})
    df.update(terms[i].keys())
idf = {w: math.log((len(records) + 1) / (n + 1)) + 1 for w, n in df.items()}
vectors, norms, title_vectors, title_norms = {}, {}, {}, {}
for i in records:
    for counts, target, norm in [(terms[i], vectors, norms), (title_terms[i], title_vectors, title_norms)]:
        v = {w: math.sqrt(n) * idf[w] for w, n in counts.items()}
        target[i] = v
        norm[i] = math.sqrt(sum(x * x for x in v.values())) or 1

def cosine(i, j, v, n):
    a, b = v[i], v[j]
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(w, 0) for w, x in a.items()) / (n[i] * n[j])

def digest(r):
    content = {k: r.get(k) for k in ("title", "initiative_text", "response_text", "reported_date", "geometry_wgs84")}
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

hashes = {i: digest(r) for i, r in records.items()}
seeds, missing_types = [], []
for i, r in records.items():
    if not r["reported_date"] or r["reported_date"] < args.cutoff:
        continue
    kind = overrides.get(i, labels.get(i, {})).get("vrsta", "")
    if not kind:
        missing_types.append(i)
    if kind != "V7":  # Keep uncertain / missing types for review rather than silently excluding them.
        seeds.append(i)
seed_set = set(seeds)
kx = 111320 * math.cos(math.radians(46.06))
xy = {i: (r["geometry_wgs84"]["x"] * kx, r["geometry_wgs84"]["y"] * 111320)
      for i, r in records.items() if r.get("geometry_wgs84")}
grid = defaultdict(list)
for i, (x, y) in xy.items():
    grid[(int(x // 100), int(y // 100))].append(i)
pairs, seen = [], set()
for i in seeds:
    if i not in xy:
        continue
    x, y = xy[i]
    gx, gy = int(x // 100), int(y // 100)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for j in grid[(gx + dx, gy + dy)]:
                key = tuple(sorted((i, j)))
                if i == j or key in seen:
                    continue
                seen.add(key)
                distance = math.hypot(x - xy[j][0], y - xy[j][1])
                if distance > 100:
                    continue
                sim = cosine(i, j, vectors, norms)
                title_sim = cosine(i, j, title_vectors, title_norms)
                refs_i = set(re.findall(r"\b\d{4,5}\b", records[i]["initiative_text"] or ""))
                refs_j = set(re.findall(r"\b\d{4,5}\b", records[j]["initiative_text"] or ""))
                referenced = str(j) in refs_i or str(i) in refs_j
                pairs.append({"ids": list(key), "distance_m": round(distance, 1), "similarity": round(sim, 4),
                              "title_similarity": round(title_sim, 4), "explicit_reference": referenced,
                              "hashes": [hashes[key[0]], hashes[key[1]]]})
pairs.sort(key=lambda p: (p["explicit_reference"], p["similarity"]), reverse=True)
parent = {}
def root(i):
    parent.setdefault(i, i)
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
strong = [p for p in pairs if p["explicit_reference"] or p["similarity"] >= .26 or p["title_similarity"] >= .8]
for p in strong:
    i, j = map(root, p["ids"])
    parent[j] = i
components = defaultdict(set)
for i in parent:
    components[root(i)].add(i)
groups = []
for ids in components.values():
    if len(ids) < 3:
        continue
    members = sorted(ids, key=lambda i: (records[i]["reported_date"], i), reverse=True)
    groups.append({"ids": members, "seeds": sorted(ids & seed_set),
                   "first": min(records[i]["reported_date"] for i in ids),
                   "last": max(records[i]["reported_date"] for i in ids)})
groups.sort(key=lambda g: len(g["ids"]), reverse=True)
metadata = {"district": args.district, "snapshot": district["zajem"], "cutoff": args.cutoff, "radius_m": 100,
            "records": len(records), "seeds": len(seeds), "missing_seed_types": missing_types,
            "spatial_pairs": len(pairs), "strong_pairs": len(strong), "candidate_groups": len(groups),
            "ranking": "stemmed title + full initiative TF-IDF cosine; candidate discovery only",
            "notice": "Connected candidates are not accepted clusters. All spatial pairs remain available for recall auditing."}
(out / "candidates.json").write_text(json.dumps({"meta": metadata, "groups": groups, "pairs": pairs}, ensure_ascii=False, separators=(",", ":")))
(out / "record_hashes.json").write_text(json.dumps(hashes, sort_keys=True))
lines = []
for n, g in enumerate(groups, 1):
    lines.append(f"\nGROUP {n}: {len(g['ids'])} records, {len(g['seeds'])} recent seeds, {g['first']}–{g['last']}")
    for i in g["ids"]:
        r = records[i]
        lines.append(f"{i}{'*' if i in seed_set else ' '} {r['reported_date']} {r['title']}")
(out / "candidate_index.txt").write_text("\n".join(lines))
print(json.dumps(metadata, ensure_ascii=False, indent=2))
