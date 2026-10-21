"""Sample existing RGB-delay cost, restoring its amount even if sampling fails."""
import asyncio,json,sys
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[1]
async def main():
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  s=json.loads(await ws.recv());fx=next(e for e in s['fx'] if e['key']=='layer/feedback~1/effect/DelayRGB~1');before=fx['target']
  try:
   await ws.send(json.dumps({'cmd':'fx_amount','key':fx['key'],'value':1}))
   for _ in range(30):await ws.recv()
   child=await asyncio.create_subprocess_exec(str(ROOT/'engine/.venv/bin/python'),str(ROOT/'qa/sample_performance.py'),'feedback-rgb-delay','60')
   # Drain the status channel while the independent read-only sampler runs.
   while child.returncode is None:
    try:await asyncio.wait_for(ws.recv(),1)
    except asyncio.TimeoutError:pass
    if child.returncode is not None:break
   if await child.wait():raise RuntimeError('Performance sample failed')
  finally:
   await ws.send(json.dumps({'cmd':'fx_amount','key':fx['key'],'value':before}))
   for _ in range(20):s=json.loads(await ws.recv())
   print('RGB delay amount restored to',before,flush=True)
asyncio.run(main())
