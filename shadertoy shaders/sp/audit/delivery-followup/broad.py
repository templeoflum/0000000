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
  for col in [9,10,11,12]*2:
   await send('launch',layer=3,col=col)
   for _ in range(60):
    await asyncio.sleep(.2)
    if any(x['layer']==3 and x['col']==col for x in state['clips']):break
   c=next(c for c in state['clips'] if c['layer']==3 and c['col']==col);a=dict(layer=3,col=col,instance=c['instance']);params=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams']
   for s in c['slots']:
    name=s['name'];p=params[name];orig=(p['value']-p['min'])/(p['max']-p['min']);await send('drive',**a,slot=name,on=False)
    for v in [.3,.7]:
     await send('manual',**a,slot=name,value=v);await asyncio.sleep(.22);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];want=p['min']+v*(p['max']-p['min']);rows.append(dict(col=col,control=name,want=want,actual=actual,ok=abs(actual-want)<.001))
     if not rows[-1]['ok']:
      rows[-1]['heart']=next((x for x in state['clips'] if x['layer']==3 and x['col']==col),{});await asyncio.sleep(1);rows[-1]['late']=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];print('MISS',col,name,want,actual,rows[-1]['late'],[(x['name'],x['base'],x['v'],x['owner']) for x in rows[-1]['heart'].get('slots',[]) if x['name']==name],flush=True)
     (P/'broad.json').write_text(json.dumps(rows,indent=2))
    await send('manual',**a,slot=name,value=orig)
  (P/'broad.json').write_text(json.dumps(rows,indent=2));print('passed',sum(r['ok'] for r in rows),'/',len(rows));t.cancel()
asyncio.run(main())
