import asyncio,json,time,urllib.request,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;R=P.parents[3];sys.path.insert(0,str(R/'sp/engine'));from patches import composition_signature
report=json.loads((P/'departure-verified.json').read_text());saved=json.loads(Path(report['avc']).with_suffix('.json').read_text());name=saved['name']
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv());assert state['arena_connected'] and not state['patch_operation']['active'];start=time.monotonic();await w.send(json.dumps({'cmd':'patch_recall','name':name}));stage=None
  while time.monotonic()-start<150:
   state=json.loads(await asyncio.wait_for(w.recv(),20));op=state['patch_operation'];now=op.get('stage')
   if now!=stage:print(now,flush=True);stage=now
   if any('Recalled patch '+name in e for e in state['events']) and not op['active']:break
   if not op['active'] and time.monotonic()-start>3 and ('fail' in str(op).lower() or 'error' in str(op).lower()):raise RuntimeError(str(op))
  else:raise RuntimeError('Reopen incomplete: '+str(state['patch_operation']))
  await asyncio.sleep(3)
  for _ in range(3):state=json.loads(await w.recv())
  comp=json.load(urllib.request.urlopen('http://localhost:8080/api/v1/composition',timeout=10));assert json.loads(json.dumps(composition_signature(comp)))==saved['signature']
  layers={l['name']:l for l in state['layers']}
  for role,v in saved['layers'].items():
   l=layers[role];assert l['clip']==(v['clip'] or '') and abs(l['opacity']-v['level'])<.005 and l['bypass']==v['bypass'],role
  for key,h in saved['instruments'].items():
   role,clip=key.split('/',1);c=next(c for c in state['clips'] if c['name']==clip and c['layer']==layers[role]['i']);slots={s['name']:s for s in c['slots']}
   for n,v in h['slots'].items():assert slots[n]['drive']==v['drive'],key+'/'+n
  delay=layers['delay']['i'];local=[f for f in state['fx'] if f['layer']==delay and f['scope']=='L'];assert any('/ColourLoop~' in f['key'] for f in local) and any('/DelayRGB~' in f['key'] for f in local)
  dc=next(c for c in state['clips'] if c['layer']==delay);assert {'R','G','B'}<={s['name'] for s in dc['slots']}
  assert state['bars']==saved['bars'] and state['hold']==saved['hold']
  (P/'reopen-state.json').write_text(json.dumps(state));(P/'reopen-native.json').write_text(json.dumps(comp));(P/'reopen-result.json').write_text(json.dumps({'name':name,'passed':True,'elapsed_s':round(time.monotonic()-start,2),'checked':['composition signature','active clips','layer levels/bypasses','source drive flags','phrase and Hold','both RGB stages']}));print('PASS saved setup reopened with both RGB stages and source drive flags restored',flush=True)
asyncio.run(main())
