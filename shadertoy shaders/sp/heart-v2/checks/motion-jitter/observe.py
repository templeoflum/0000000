"""Cached Heart metrics and bounded native observation, no native mutations."""
import asyncio,json,time,urllib.request,statistics,sys
from pathlib import Path
import websockets
OUT=Path(__file__).parent
async def main():
 states=[];samples=[];catalog=None
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
  while catalog is None:
   m=json.loads(await ws.recv())
   if m['type']=='catalog':catalog=m
  start=time.perf_counter()
  while time.perf_counter()-start<15:
   m=json.loads(await ws.recv())
   if m['type']=='state':states.append(dict(received=time.perf_counter(),**m))
  final=states[-1];metrics=[s['metrics'] for s in states];delivered=[m['delivery'] for m in metrics if m.get('delivery')]
  def stats(xs):return dict(p50=statistics.median(xs),p95=sorted(xs)[int((len(xs)-1)*.95)],max=max(xs)) if xs else {}
  result=dict(states=len(states),armed=final['armed'],bpm=final['bpm'],owned=metrics[-1]['owned'],tick_p95=stats([m['tick_p95_ms'] for m in metrics]),frame_age=stats([d['age_ms'] for d in delivered]),waiting=stats([d['waiting'] for d in delivered]),errors=sorted({s['error'] for s in states if s['error']}),report_gaps=stats([(b['received']-a['received'])*1000 for a,b in zip(states,states[1:])]))
  (OUT/'before.json').write_text(json.dumps(dict(summary=result,catalog=catalog,states=states)))
  print(json.dumps(result))
asyncio.run(main())
