"""Reversible native animation takeover check on the playing feedback candidate."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
BASE='http://127.0.0.1:8080/api/v1'
def req(path,method='GET',body=None):
 r=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body else None,method=method,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=5) as f:
  raw=f.read();return json.loads(raw) if raw else None
def find(x):
 if isinstance(x,dict):
  if 'Loop Hue' in x:return x['Loop Hue']['id']
  for v in x.values():
   hit=find(v)
   if hit:return hit
 if isinstance(x,list):
  for v in x:
   hit=find(v)
   if hit:return hit
async def main():
 report={}
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  async def slot():
   s=json.loads(await asyncio.wait_for(ws.recv(),5))
   c=next(c for c in s['clips'] if c['layer']==1 and c['col']==6)
   return next(x for x in c['slots'] if x['name']=='Loop Hue')
  before=await slot();assert before['drive'] and before['owner']=='heart',before
  pid=await asyncio.to_thread(lambda:find(req('/composition/layers/1/clips/6')))
  path=f'/parameter/by-id/{pid}/phase-source'
  try:
   await asyncio.to_thread(req,path,'PUT',{'phase_source':'timeline'})
   start=time.monotonic()
   while time.monotonic()-start<20:
    current=await slot()
    if current['owner']=='resolume' and not current['drive']:break
   else:raise AssertionError('Native ownership was not detected')
   report['release_seconds']=round(time.monotonic()-start,3);report['released']=current
   await asyncio.to_thread(req,path,'DELETE')
   until=time.monotonic()+2
   while time.monotonic()<until:current=await slot()
   assert current['owner']=='resolume' and not current['drive'],current
   report['static_does_not_reclaim']=True
  finally:
   await asyncio.to_thread(req,path,'DELETE')
   await ws.send(json.dumps({'cmd':'home','layer':1,'col':6,'factory':True}))
   until=time.monotonic()+10
   while time.monotonic()<until:
    current=await slot()
    if current['owner']=='heart' and current['drive']:break
   else:raise AssertionError('Home did not reclaim')
   report['home_reclaimed']=current
   report['native_after']=await asyncio.to_thread(req,path)
 Path('sp/design/heart-performance-plan/ownership-live.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
asyncio.run(main())
