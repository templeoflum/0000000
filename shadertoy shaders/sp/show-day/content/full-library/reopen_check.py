"""Reopen the newly saved pair and check actual runtime/native state."""
import asyncio,json,time,urllib.request,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT/'sp/engine'));from patches import composition_signature
report=json.loads((ROOT/'sp/show-day/integration/rehearsal/departure-verified.json').read_text());saved=json.loads(Path(report['avc']).with_suffix('.json').read_text());name=saved['name']
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv());assert state['arena_connected'] and not state['patch_operation']['active'];start=time.monotonic();await w.send(json.dumps({'cmd':'patch_recall','name':name}));stage=None
  while time.monotonic()-start<180:
   state=json.loads(await asyncio.wait_for(w.recv(),25));op=state['patch_operation'];now=op.get('stage')
   if now!=stage:print('Reopen',now,flush=True);stage=now
   if any('Recalled patch '+name in e for e in state['events']) and not op['active']:break
   if not op['active'] and time.monotonic()-start>3 and ('fail' in str(op).lower() or 'error' in str(op).lower()):raise RuntimeError(str(op))
  else:raise RuntimeError('Reopen incomplete: '+str(state['patch_operation']))
  end=time.monotonic()+4
  while time.monotonic()<end:state=json.loads(await asyncio.wait_for(w.recv(),10))
  comp=json.load(urllib.request.urlopen('http://localhost:8080/api/v1/composition',timeout=15));assert json.loads(json.dumps(composition_signature(comp)))==saved['signature']
  layers={l['name']:l for l in state['layers']}
  for role,v in saved['layers'].items():
   l=layers[role];assert l['clip']==(v['clip'] or '') and abs(l['opacity']-v['level'])<.005 and l['bypass']==v['bypass'],role
  for key,h in saved['instruments'].items():
   role,clip=key.split('/',1);c=next(c for c in state['clips'] if c['name']==clip and c['layer']==layers[role]['i']);slots={s['name']:s for s in c['slots']}
   for n,v in h['slots'].items():assert slots[n]['drive']==v['drive'],key+'/'+n
  assert state['bars']==saved['bars'] and state['hold']==saved['hold']
  P.joinpath('reopened.png').write_bytes(urllib.request.urlopen('http://localhost:8080/api/v1/composition/monitors/1/snapshot.png',timeout=15).read())
  P.joinpath('reopen-result.json').write_text(json.dumps(dict(name=name,passed=True,elapsed_s=round(time.monotonic()-start,2),checked=['composition signature','active clips','layer levels/bypasses','source drive flags','phrase and Hold','actual output capture']),indent=2));print('PASS reopened',name,flush=True)
asyncio.run(main())
