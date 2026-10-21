import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=10))
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain());rows=[]
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  for col in [72]:
   await send('launch',layer=5,col=col);await asyncio.sleep(1)
   c=next(c for c in state['clips'] if c['layer']==5 and c['col']==col);a=dict(layer=5,col=col,instance=c['instance']);params=(await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}'))['video']['sourceparams']
   for s in c['slots']:
    name=s['name'];p=params[name];orig=(p['value']-p['min'])/(p['max']-p['min']);await send('drive',**a,slot=name,on=False)
    for v in [.3,.7]:
     await send('manual',**a,slot=name,value=v);await asyncio.sleep(.22);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];want=p['min']+v*(p['max']-p['min']);rows.append(dict(col=col,control=name,want=want,actual=actual,ok=abs(actual-want)<.001))
    await send('manual',**a,slot=name,value=orig)
  (P/'all-controls.json').write_text(json.dumps(rows,indent=2));print('passed',sum(r['ok'] for r in rows),'/',len(rows));t.cancel()
asyncio.run(main())
