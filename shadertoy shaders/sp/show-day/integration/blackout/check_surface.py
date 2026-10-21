import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=5))
def post(d):
 r=urllib.request.Request('http://localhost:8765/blackout',json.dumps(d).encode(),{'Content-Type':'application/json'},method='POST');return json.load(urllib.request.urlopen(r,timeout=5))
def levels(c):return [(l['id'],l['video']['opacity']['value']) for l in c['layers']]
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());b=s['blackout'];assert b['available'];initial=get('/composition');records=[]
  try:
   for on in [True,False]:
    start=time.perf_counter();r=await asyncio.to_thread(post,{'on':on,'parameter_id':b['parameter_id']});elapsed=time.perf_counter()-start
    assert r['on']==on;native=await asyncio.to_thread(get,'/composition');assert native['bypassed']['value']==on;assert levels(native)==levels(initial)
    records.append(dict(on=on,seconds=elapsed,state=r));print(on,round(elapsed*1000),'ms request/readback',flush=True)
  finally:await asyncio.to_thread(post,{'on':b['on'],'parameter_id':b['parameter_id']})
  (P/'surface-live.json').write_text(json.dumps(records,indent=2))
asyncio.run(main())
