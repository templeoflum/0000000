"""Measure cleared composition, then restore the already-saved Feedback performance patch."""
import asyncio,json,time
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[1]
async def main():
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  before=json.loads(await ws.recv());expected={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in before['clips']}
  assert 'Feedback performance' in before['patches']
  try:
   for layer in range(1,9):await ws.send(json.dumps({'cmd':'clear','layer':layer}))
   end=time.monotonic()+12
   while time.monotonic()<end:
    s=json.loads(await ws.recv())
    if not s['clips']:break
   else:raise RuntimeError('Layers did not clear')
   child=await asyncio.create_subprocess_exec(str(ROOT/'engine/.venv/bin/python'),str(ROOT/'qa/sample_performance.py'),'all-layers-idle','60')
   while child.returncode is None:
    try:await asyncio.wait_for(ws.recv(),1)
    except asyncio.TimeoutError:pass
   if await child.wait():raise RuntimeError('Idle sample failed')
  finally:
   await ws.send(json.dumps({'cmd':'patch_recall','name':'Feedback performance'}));busy=False;end=time.monotonic()+40
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(ws.recv(),4));op=s.get('patch_operation',{});busy|=op.get('active',False)
    if busy and not op.get('active'):
     actual={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in s['clips']}
     assert op['stage']=='Ready' and actual==expected,(op,actual,expected)
     print('Empty-scene recall restored all instruments and drives',flush=True);break
   else:raise RuntimeError('Restore not confirmed')
asyncio.run(main())
