import asyncio,json
from pathlib import Path
import websockets
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**k):await w.send(json.dumps(dict(cmd=cmd,**k)))
  l=next(l for l in state['layers'] if l['i']==5);assert len(l['explore'])>=12,l
  old=state['surface'].get('banks',{});await send('surface_cfg',value={'banks':dict(old,**{l['name']:'explore'})});await asyncio.sleep(1)
  allowed=[c['col'] for c in l['explore']];seen=[]
  for direction in ['next','prev']:
   await send('clip_nav',layer=5,dir=direction);await asyncio.sleep(4)
   l=next(l for l in state['layers'] if l['i']==5);assert l['ccol'] in allowed;seen.append(l['ccol'])
  await send('surface_cfg',value={'banks':dict(old,**{l['name']:old.get(l['name'],'heart')})})
  Path(__file__).with_name('live.json').write_text(json.dumps(dict(candidates=l['explore'],visited=seen),indent=2));print('Candidates',len(allowed),'next/prev',seen);t.cancel()
asyncio.run(main())
