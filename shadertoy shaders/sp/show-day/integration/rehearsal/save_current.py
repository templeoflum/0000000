import asyncio,json,time,urllib.request,sys
from datetime import datetime
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;ROOT=P.parents[3];ENGINE=ROOT/'sp/engine';sys.path.insert(0,str(ROOT/'sp/show-day/recovery'))
from verify_show_pair import verify
B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=10))
async def main():
 name='Heart Show Ready '+datetime.now().strftime('%Y%m%d %H%M%S');avc=ENGINE/'patches'/(name+'.avc')
 for f in [avc,avc.with_suffix('.json'),avc.with_suffix('.json.tmp')]:assert not f.exists()
 c=get('/composition/layers/2/clips/108');assert c.get('video') is None,'Scratch not empty'
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());assert s['arena_connected'] and not s['patch_operation']['active']
  start=time.time();await w.send(json.dumps({'cmd':'patch_save','name':name}))
  while time.time()-start<100:
   s=json.loads(await asyncio.wait_for(w.recv(),15))
   if avc.with_suffix('.json').exists() and not s['patch_operation']['active']:break
  else:raise RuntimeError('Save timed out: '+str(s.get('patch_operation')))
  assert any('Saved patch '+name in e for e in s['events']),str(s['events'][-5:])
  evidence={k:get('/'+endpoint) for k,endpoint in [('sources','sources'),('effects','effects'),('composition','composition')]}
  for k,v in evidence.items():(P/('departure-'+k+'.json')).write_text(json.dumps(v))
  report=verify(avc,evidence['sources'],evidence['effects'],evidence['composition'],start)
  report.update(name=name,avc=str(avc),save_start=start)
  (P/'departure-verified.json').write_text(json.dumps(report,indent=2));print(json.dumps({'name':name,'avc':str(avc),'result':report['result']}),flush=True)
asyncio.run(main())
