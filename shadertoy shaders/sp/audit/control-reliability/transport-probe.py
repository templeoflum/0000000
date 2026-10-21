import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=10))
def put(pid,v):return urllib.request.urlopen(urllib.request.Request(B+f'/parameter/by-id/{pid}',json.dumps({'value':v}).encode(),{'Content-Type':'application/json'},method='PUT'),timeout=10).read()
async def main():
 p=(await asyncio.to_thread(get,'/composition/layers/3/clips/21'))['video']['sourceparams']['scale'];rows=[]
 async with websockets.connect('ws://localhost:8080/api/v1',max_size=None) as w:
  async def drain():
   async for m in w:pass
  t=asyncio.create_task(drain())
  for mode in ['ws','http']:
   for i in range(50):
    v=[.27,.73,.44,.86][i%4]
    if mode=='ws':await w.send(json.dumps({'action':'set','parameter':f"/parameter/by-id/{p['id']}",'value':v}))
    else:await asyncio.to_thread(put,p['id'],v)
    await asyncio.sleep(.1);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];rows.append(dict(mode=mode,i=i,want=v,actual=actual,ok=abs(actual-v)<.001))
   print(mode,sum(r['ok'] for r in rows if r['mode']==mode),'/50',flush=True)
  t.cancel()
 (P/'transport.json').write_text(json.dumps(rows,indent=2))
asyncio.run(main())
