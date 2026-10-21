import asyncio,json,urllib.request,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=10))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  c=next(c for c in state['clips'] if c['layer']==5 and c['col']==73);a=dict(layer=5,col=73,instance=c['instance'])
  try:
   for layer in [5,2,4,1]:
    for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==layer))
    for i,v in enumerate([.15,.45]):
     await send('manual',**a,slot='Turn',value=v);await asyncio.sleep(2);await asyncio.to_thread(snap,f'route-L{layer}-{i}')
    print('route layer',layer,'captured',flush=True)
  finally:
   await send('home',**a,factory=True)
   for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==5))
   await asyncio.sleep(4);(P/'route-final-heart.json').write_text(json.dumps(state));t.cancel()
asyncio.run(main())
