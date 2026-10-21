import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent

def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=15))
async def main():
 rows=json.loads((P/'live-results.json').read_text());results=[]
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  for r in rows:
   if all(c['ok'] for c in r['checks']):continue
   col=r['col'];layer=r['layer'];key=r['probe'];await send('launch',layer=layer,col=col);c=None
   for _ in range(40):
    await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==layer and c['col']==col and c.get('slots')),None)
    if c:break
   assert c
   a=dict(layer=layer,col=col,instance=c['instance']);p=(await asyncio.to_thread(get,f'/composition/layers/{layer}/clips/{col}'))['video']['sourceparams'][key];old=(p['value']-p['min'])/(p['max']-p['min'])
   await send('drive',**a,slot=key,on=False);await asyncio.sleep(.3)
   for ch in r['checks']:
    if ch['ok']:continue
    want=ch['requested'];await send('manual',**a,slot=key,value=(want-p['min'])/(p['max']-p['min']))
    for _ in range(20):
     await asyncio.sleep(.15);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value']
     if abs(actual-want)<.001:break
    results.append(dict(layer=layer,col=col,probe=key,requested=want,observed=actual,ok=abs(actual-want)<.001))
   await send('manual',**a,slot=key,value=old)
  await send('launch',layer=3,col=108);t.cancel()
 (P/'retry.json').write_text(json.dumps(results,indent=2));print(results)
asyncio.run(main())
