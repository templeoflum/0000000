import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent

def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=15))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen('http://localhost:8080/api/v1/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 rows=[]
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  for col,key in [(93,'Type'),(100,'Type'),(106,'Mode')]:
   await send('launch',layer=3,col=col)
   for _ in range(40):
    await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==3 and c['col']==col and c.get('slots')),None)
    if c:break
   assert c
   a=dict(layer=3,col=col,instance=c['instance']);native=await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}');p=native['video']['sourceparams'][key];checks=[]
   await send('drive',**a,slot=key,on=False)
   for idx in [0,2]:
    await send('manual',**a,slot=key,value=idx/(len(p['options'])-1))
    for _ in range(15):
     await asyncio.sleep(.2);v=await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}")
     if v.get('index')==idx:break
    checks.append(dict(requested=p['options'][idx],observed=v.get('value'),ok=v.get('index')==idx));await asyncio.to_thread(snap,f'choice-L3C{col}-{idx}')
   await send('manual',**a,slot=key,value=p['index']/(len(p['options'])-1));rows.append(dict(col=col,source=native['video']['description'],probe=key,checks=checks))
   (P/'choices.json').write_text(json.dumps(rows,indent=2));print(rows[-1],flush=True)
  await send('launch',layer=3,col=108);t.cancel()
asyncio.run(main())
