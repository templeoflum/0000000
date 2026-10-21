import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=10))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv());assert state['arena_connected'];initial=state
  async def read():
   nonlocal state
   async for m in w:state=json.loads(m)
  reader=asyncio.create_task(read());records=[];motion=None
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  async def cap(label):
   await asyncio.sleep(2);await asyncio.to_thread(snap,label);records.append(dict(label=label,layers=state['layers'],fx=state['fx']));(P/'remaining-routes.json').write_text(json.dumps(records))
  c=next(c for c in state['clips'] if c['layer']==5 and c['col']==73);a=dict(layer=5,col=73,instance=c['instance'])
  delay=next(f for f in state['fx'] if f['scope']=='K' and f['layer']==4 and f['name']=='SP Delay Chain');d=dict(key=delay['key'],instance=delay['instance'])
  try:
   await send('play_all',action='settle');await asyncio.sleep(4)
   for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i'] in [4,5]))
   async def move():
    t=time.monotonic()
    while True:
     await send('manual',**a,slot='Turn',value=((time.monotonic()-t)/3)%1);await asyncio.sleep(.08)
   motion=asyncio.create_task(move());await cap('delay-route-off')
   await send('fx_direction',**d,value=1);await asyncio.sleep(6);await cap('delay-route-on')
   await send('fx_amount',**d,value=0);await cap('delay-route-cleared')
   await send('opacity',layer=4,value=0);await send('opacity',layer=1,value=.85);await asyncio.sleep(4);await cap('feedback-seeded')
   await send('opacity',layer=5,value=0);await cap('feedback-history')
   await send('opacity',layer=1,value=0);await cap('feedback-off')
  finally:
   if motion:motion.cancel()
   await send('fx_amount',**d,value=0);await send('play_all',action='settle');await send('home',**a,factory=True)
   for l in initial['layers']:await send('opacity',layer=l['i'],value=int(l['i']==5))
   await asyncio.sleep(4);(P/'remaining-final.json').write_text(json.dumps(state));reader.cancel()
asyncio.run(main())
