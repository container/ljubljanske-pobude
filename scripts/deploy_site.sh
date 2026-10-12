#!/bin/sh
# Rebuild "Ljubljanske pobude" for every district in data/cetrti.json and publish it to Railway (project "Vič", workspace guitwist).
set -e
cd "$(dirname "$0")/.."
python3 scripts/build_theme_map_data.py >/dev/null
for d in $(python3 -c "import json; print(' '.join(c['id'] for c in json.load(open('data/cetrti.json'))))"); do
  python3 scripts/build_stats.py --district "$d"
done
python3 scripts/build_site.py
cd deploy/site && railway up --detach -p 7b50d5d2-730a-4525-9552-12b99d4fbdd6 -e 9c31bcbf-a61d-4303-a081-4cee315e361c -s c5637d79-d871-468d-9f5c-7fd11a3f4d0f -m "Ljubljanske pobude: posodobitev"
echo "https://ljubljanske-pobude.up.railway.app"
