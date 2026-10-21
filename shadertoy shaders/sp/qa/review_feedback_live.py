"""Exercise only the already-playing feedback candidate; record real card state and snapshots."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/heart-performance-plan/feedback-instrument'
async def main():
 report=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  s=json.loads(await ws.recv());assert any(c['layer']==1 and c['col']==6 and c['name']=='heart feedback' for c in s['clips'])
  for name in ['Drift','Breathe','Fold','Turn']:
   await ws.send(json.dumps({'cmd':'feedback_behavior','name':name,'layer':1,'col':6}))
   until=time.monotonic()+7
   while time.monotonic()<until:s=json.loads(await ws.recv())
   c=next(c for c in s['clips'] if c['layer']==1 and c['col']==6)
   image=await asyncio.to_thread(lambda:urllib.request.urlopen('http://127.0.0.1:8080/api/v1/composition/monitors/1/snapshot.png',timeout=5).read())
   (OUT/(name.lower()+'-live.png')).write_bytes(image)
   row={'behavior':name,'drives':[(x['name'],x['v']) for x in c['slots'] if x['drive']],'delivery':s.get('delivery')};report.append(row);print(json.dumps(row),flush=True)
  await ws.send(json.dumps({'cmd':'feedback_reset','layer':1,'col':6}))
  until=time.monotonic()+2
  while time.monotonic()<until:s=json.loads(await ws.recv())
  print('Reset command sent to playing instrument; final card:',next(c['name'] for c in s['clips'] if c['layer']==1),flush=True)
 (OUT/'behavior-live-checks.json').write_text(json.dumps(report,indent=2))
asyncio.run(main())
