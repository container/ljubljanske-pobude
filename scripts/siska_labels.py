"""Read or write Šiška label batches in analysis/cetrti/siska/oznacevanje/paketi.
Usage: python3 scripts/siska_labels.py read 1
Write (overwrites the label file): python3 scripts/siska_labels.py write 1 < decisions.txt
Each input line: ID V1 S5|verbatim evidence|optional note. See README.md.
"""
import json, re, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'analysis/cetrti/siska/oznacevanje/paketi'
norm=lambda s: re.sub(r'\s+',' ',s).strip()
batch=int(sys.argv[2]); src=BASE/f'paket_{batch:02d}.json'
rows=json.loads(src.read_text())
if sys.argv[1]=='read':
    for r in rows:
        t=norm(r['odgovor'])
        t=re.sub(r'^.*?Posredujemo vam odgovor gospoda župana:\s*','',t)
        t=re.sub(r'\s*Lep pozdrav[,.!]?\s*(Mestna uprava|Odsek za pobude|$).*$', '',t)
        t=re.sub(r'^Spoštovani[,!]\s*','',t)
        print(f"{r['id']} {r['naslov']} | {norm(r['pobuda'])}\n>{t}")
else:
    decisions={}
    for line in sys.stdin:
        if not line.strip(): continue
        parts=line.rstrip('\n').split('|')
        id_,v,s=parts[0].split(); quote=parts[1].strip()
        note=parts[2].strip() if len(parts)>2 else ''
        decisions[int(id_)]=(v,s,quote,note)
    assert set(decisions)=={r['id'] for r in rows},(set(decisions)^{r['id'] for r in rows})
    out=[]
    for r in rows:
        v,s,q,note=decisions[r['id']]
        assert q and q in norm(r['odgovor']),(r['id'],q)
        assert len(q.split())<=25,(r['id'],'quote too long')
        assert v in {f'V{i}' for i in range(1,10)}
        assert s in {'S1','S2','S3','S4','S5','S6','SV'}
        assert s!='SV' or v=='V7'
        out.append(dict(id=r['id'],vrsta=v,stanje=s,dokaz=q,gotovost='nizka' if note else 'visoka',opomba=note))
    dest=src.with_name(src.stem+'_oznake.json')
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n')
    print('Saved',len(out),'labels:',dest.name)
