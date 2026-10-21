import json,time,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get():return json.load(urllib.request.urlopen(B+'/composition',timeout=20))
def select(i):urllib.request.urlopen(urllib.request.Request(B+f'/composition/decks/{i}/select',data=b'',method='POST'),timeout=10).close()
original=get();selected=next(i for i,d in enumerate(original['decks'],1) if d['selected']['value']);atoms=json.loads((P.parents[1]/'engine/atoms.json').read_text());rows=[];counts=[]
try:
 for i,d in enumerate(original['decks'],1):
  if i!=selected:select(i);time.sleep(.8)
  c=get();(P/f'deck-{i}.json').write_text(json.dumps(c));n=0
  for l,layer in enumerate(c['layers'],1):
   for col,cl in enumerate(layer['clips'],1):
    v=cl.get('video') or {};desc=v.get('description')
    if not desc:continue
    p=v.get('sourceparams') or {};numeric={k:x for k,x in p.items() if isinstance(x,dict) and x.get('valuetype') in ('ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice')}
    legacy=any(k.endswith(' Drive') for k in p)
    rows.append(dict(deck=i,deck_name=d['name']['value'],layer=l,col=col,name=cl['name']['value'],source=desc,controls=numeric,other_controls={k:x.get('valuetype') for k,x in p.items() if isinstance(x,dict) and k not in numeric},heart_registered=desc in atoms or legacy,rendered_status='not assessed in this census'));n+=1
  counts.append(dict(deck=i,name=d['name']['value'],clips=n))
finally:select(selected)
(P/'coverage.json').write_text(json.dumps(dict(decks=counts,clips=rows),indent=2));print(json.dumps(counts));print('total',len(rows),'unique sources',len({r['source'] for r in rows}))
