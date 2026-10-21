import asyncio,json,time
from pathlib import Path
import websockets
async def main():
 events=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  async def wait_for(test,seconds=25):
   end=time.monotonic()+seconds
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(ws.recv(),3));events.append({'t':time.time(),'patch':s.get('patch_status'),'ready':s.get('arena_connected'),'clips':[c['name'] for c in s['clips']]})
    if test(s):return s
   raise RuntimeError(str(events[-3:]))
  s=await wait_for(lambda s:s.get('arena_connected'))
  assert [c['name'] for c in s['clips']]==['map'], 'Test requires only map active'
  await ws.send(json.dumps({'cmd':'patch_save','name':'Connection check'}))
  await wait_for(lambda s:'Connection check' in s.get('patches',[]) and s.get('patch_status')=='Ready')
  await ws.send(json.dumps({'cmd':'clear','layer':1}))
  await wait_for(lambda s:not s['clips'])
  await ws.send(json.dumps({'cmd':'patch_recall','name':'Connection check'}))
  result=await wait_for(lambda s:s.get('patch_status')=='Ready' and [c['name'] for c in s['clips']]==['map'])
  print('Recall passed: map restored, connected',result['arena_connected'],'effects',len(result['fx']))
 Path(__file__).with_name('recall-live.json').write_text(json.dumps(events,indent=2))
asyncio.run(main())
