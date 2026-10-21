"""Read-only acceptance after clearing the reproduced stale-phase worker stall."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
OUT=Path(__file__).parent
PID=1789181905216

def read(path):
 with urllib.request.urlopen('http://127.0.0.1:8080/api/v1'+path,timeout=2) as r:return json.load(r)
async def main():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8000000) as ws:
  snap={}
  while 'state' not in snap or 'catalog' not in snap:
   m=json.loads(await ws.recv());snap[m['type']]=m
  before=snap['state'];samples=[];program=read(f'/parameter/by-id/{PID}/phase-source')
  for _ in range(24):
   n=read(f'/parameter/by-id/{PID}');samples.append(n['value']);await asyncio.sleep(.1)
  end=time.monotonic()+2;after=before
  while time.monotonic()<end:
   m=json.loads(await ws.recv())
   if m['type']=='state':after=m
  after_program=read(f'/parameter/by-id/{PID}/phase-source')
  r=dict(error=after['error'],armed=after['armed'],hold=after['hold'],bpm=after['bpm'],capabilities={k:k in after['capabilities'] for k in ['stage_family','stage_shuffle','motion_multiplier']},multipliers=after['motion_multipliers'],stage_motion=after['stage_motion'],metrics=after['metrics'],native_output=dict(parameter=PID,span=max(samples)-min(samples),within_bounds=all(min(n['in'],n['out'])-1e-5<=v<=max(n['in'],n['out'])+1e-5 for v in samples),program_preserved=program==after_program,samples=samples),sent_during_check=after['metrics']['sent']-before['metrics']['sent'])
  (OUT/'after-worker-fix.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('stage_motion','native_output')}));print('Native Rings span',r['native_output']['span'],'program preserved',r['native_output']['program_preserved'])
  assert r['sent_during_check']>0 and r['native_output']['span']>.0001 and r['native_output']['within_bounds'] and r['native_output']['program_preserved'],r
asyncio.run(main())
