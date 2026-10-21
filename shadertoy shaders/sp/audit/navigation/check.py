import asyncio,json
from pathlib import Path
import websockets
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain());banks=dict(state.get('surface',{}).get('banks',{}))
  for l in state['layers']:
   if l.get('heart_copies'):banks[l['name']]='heart'
  await w.send(json.dumps(dict(cmd='surface_cfg',value={'banks':banks})))
  for _ in range(50):
   await asyncio.sleep(.2)
   l=next(l for l in state['layers'] if l['i']==3)
   if l['bank']=='heart':break
  assert l['bank']=='heart';allowed=[c['col'] for c in l['heart_copies']];rows=[]
  for direction in ['next','prev','rand']:
   old=l.get('ccol');await w.send(json.dumps(dict(cmd='clip_nav',layer=3,dir=direction)))
   for _ in range(60):
    await asyncio.sleep(.2);l=next(l for l in state['layers'] if l['i']==3)
    if l.get('ccol')!=old:break
   rows.append(dict(direction=direction,col=l.get('ccol'),allowed=allowed));assert l.get('ccol') in allowed
  Path('sp/audit/navigation/live.json').write_text(json.dumps(rows,indent=2));print(rows);t.cancel()
asyncio.run(main())
