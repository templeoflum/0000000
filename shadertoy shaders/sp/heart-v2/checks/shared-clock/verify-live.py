"""Read current delivery status and one stable prepared native parameter."""
import asyncio,json,time,urllib.request,statistics
from pathlib import Path
import websockets
OUT=Path(__file__).parent
async def main():
 states=[];samples=[]
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
  while True:
   m=json.loads(await ws.recv())
   if m['type']=='catalog':catalog=m;break
  candidates=[(t,p) for t in catalog['targets'] if t.get('stage') and t.get('scope')!='clip' for p in t['params'] if p.get('native_phase')]
  if not candidates:raise RuntimeError('No stable prepared stage parameter to sample')
  target,p=candidates[0];pid=p['id']
  def read(suffix=''):
   with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}'+suffix,timeout=1) as r:return json.load(r)
  before=await asyncio.to_thread(read,'/phase-source')
  async def sample():
   for i in range(30):
    r=await asyncio.to_thread(read);samples.append(dict(t=time.perf_counter(),**{k:r.get(k) for k in ('id','value','in','out')}));await asyncio.sleep(.1)
  task=asyncio.create_task(sample());end=time.perf_counter()+8
  while time.perf_counter()<end:
   m=json.loads(await asyncio.wait_for(ws.recv(),2))
   if m['type']=='state':states.append(m)
  await task;after=await asyncio.to_thread(read,'/phase-source')
 ages=[s['metrics']['delivery'].get('age_ms',0) for s in states if s['metrics'].get('delivery')]
 vals=[s['value'] for s in samples];final=states[-1]
 result=dict(native=dict(target=target['label'],parameter=pid,name=p['name'],span=max(vals)-min(vals),program_before=before,program_after=after,samples=samples),summary=dict(states=len(states),armed=final['armed'],hold=final['hold'],bpm=final['bpm'],tick_p95_ms=final['metrics']['tick_p95_ms'],work_p95_ms=final['metrics']['work_p95_ms'],frame_age_p95_ms=sorted(ages)[int((len(ages)-1)*.95)],max_waiting=max(s['metrics'].get('delivery',{}).get('waiting',0) for s in states),sent=final['metrics']['sent']-states[0]['metrics']['sent'],errors=sorted({s['error'] for s in states if s['error']})),states=states)
 (OUT/'live-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['summary']));print('Native span:',result['native']['span'],'Program unchanged:',before==after)
 assert final['armed'] and not final['error'];assert result['native']['span']>1e-7;assert before==after
asyncio.run(main())
