import asyncio,json,sys,shutil
from pathlib import Path
import websockets
P=Path(__file__).parent
async def main():
 shutil.copy2(P.resolve().parents[1]/'engine/home.json',P/'home-before-final-repairs.json')
 keys={x['key'] for file in ('remaining-repair.json','factory-repair.json') for x in json.loads(P.joinpath(file).read_text())['changes']}
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());fx={f['key']:f for f in s['fx']}
  async def drain():
   async for _ in w:pass
  t=asyncio.create_task(drain())
  for key in keys:
   f=fx.get(key)
   if f and f.get('motion'):
    await w.send(json.dumps({'cmd':'home_set','effect':key,'instance':f['instance']}));await asyncio.sleep(.15)
  await asyncio.sleep(.5);t.cancel();print('Updated repair Home poses:',len(keys))
asyncio.run(main())
