import asyncio,json
from pathlib import Path
import websockets
from tune import PLANS,get,snap
P=Path(__file__).resolve().parent
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  async def launch(col):
   await send('launch',layer=3,col=col)
   for _ in range(40):
    await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==3 and c['col']==col),None)
    if c:return dict(layer=3,col=col,instance=c['instance'])
   raise RuntimeError('Launch timeout')
  await send('hold',on=True)
  for col,(base,drives) in PLANS.items():
   a=await launch(col);await send('home',**a);await asyncio.sleep(2)
   if col==33:
    base['thickness']=.32;base['glow']=.75;drives['thickness']=(.22,.42);drives['glow']=(.6,.85)
    for name in ['thickness','glow']:await send('manual',**a,slot=name,value=base[name])
    await asyncio.sleep(.6);native=await asyncio.to_thread(get,'/composition/layers/3/clips/33')
    assert all(abs(native['video']['sourceparams'][k]['value']-base[k])<.01 for k in ['thickness','glow'])
    await send('home_set',**a);await asyncio.sleep(.5);await asyncio.to_thread(snap,'tuned-33-final-home')
   for key,value in [('Pattern',0),('Spread',1),('Depth',1),('FM',0)]:await send('global_cfg',**a,key=key,value=value)
   # Persist enrollment-specific drive choices through existing per-clip Smart Params config.
   c=next(c for c in state['clips'] if c['layer']==3 and c['col']==col)
   for sl in c['slots']:
    await send('slot_cfg',**a,slot=sl['name'],key='Drive',value=sl['name'] in drives)
    await send('drive',**a,slot=sl['name'],on=sl['name'] in drives)
   if col==33:
    for name,(lo,hi) in drives.items():
     await send('slot_cfg',**a,slot=name,key='Lo',value=lo);await send('slot_cfg',**a,slot=name,key='Hi',value=hi)
   await asyncio.sleep(.5)
  results=[]
  await send('hold',on=False)
  for col,(base,drives) in PLANS.items():
   a=await launch(col);await asyncio.sleep(.6)
   c=next(c for c in state['clips'] if c['layer']==3 and c['col']==col)
   active=[s['name'] for s in c['slots'] if s['drive']];ok=set(active)==set(drives)
   results.append(dict(col=col,active=active,expected=list(drives),ok=ok,g=c['g'],home=base,drives=drives))
   print(col,'relaunch',active,ok,flush=True)
  await asyncio.sleep(2);await asyncio.to_thread(snap,'tuned-33-final-motion')
  (P/'relaunch-results.json').write_text(json.dumps(results,indent=2));(P/'heart-final.json').write_text(json.dumps(state,indent=2));t.cancel();assert all(r['ok'] for r in results)
asyncio.run(main())
