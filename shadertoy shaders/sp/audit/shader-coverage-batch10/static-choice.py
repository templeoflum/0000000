import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent

def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=15))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen('http://localhost:8080/api/v1/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('launch',layer=8,col=15)
  for _ in range(40):
   await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==8 and c['col']==15 and c.get('slots')),None)
   if c:break
  assert c
  a=dict(layer=8,col=15,instance=c['instance']);p=(await asyncio.to_thread(get,'/composition/layers/8/clips/15'))['video']['sourceparams']['Mode'];rows=[]
  await send('drive',**a,slot='Mode',on=False)
  for idx in [0,2]:
   await send('manual',**a,slot='Mode',value=idx/(len(p['options'])-1))
   for _ in range(15):
    await asyncio.sleep(.2);v=await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}")
    if v.get('index')==idx:break
   rows.append(dict(requested=p['options'][idx],observed=v.get('value'),ok=v.get('index')==idx));await asyncio.to_thread(snap,f'static-mode-{idx}')
  await send('manual',**a,slot='Mode',value=p['index']/(len(p['options'])-1));await send('launch',layer=8,col=18);t.cancel()
 (P/'static-choice.json').write_text(json.dumps(rows,indent=2));print(rows)
asyncio.run(main())
