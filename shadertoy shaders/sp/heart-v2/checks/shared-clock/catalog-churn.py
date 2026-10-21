import asyncio,json
from pathlib import Path
import websockets
async def main():
 rows=[]
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  async with asyncio.timeout(5):
   while len(rows)<6:
    m=json.loads(await ws.recv())
    if m['type']=='catalog':rows.append(m)
 def structural(t):return {k:v for k,v in t.items() if k!='params'}|dict(params=[{k:v for k,v in p.items() if k not in ('value','_phase_checked')} for p in t['params']])
 for a,b in zip(rows,rows[1:]):
  x={t['id']:structural(t) for t in a['targets']};y={t['id']:structural(t) for t in b['targets']}
  print('Layers',[(l['name'],l['active']) for l in b['layers'] if l not in a['layers']])
  for tid in x.keys()|y.keys():
   if x.get(tid)!=y.get(tid):
    aa,bb=x.get(tid,{}),y.get(tid,{})
    print('Changed',tid,{k:(aa.get(k),bb.get(k)) for k in aa.keys()|bb.keys() if aa.get(k)!=bb.get(k)})
 (Path(__file__).parent/'catalog-churn.json').write_text(json.dumps(rows))
asyncio.run(main())
