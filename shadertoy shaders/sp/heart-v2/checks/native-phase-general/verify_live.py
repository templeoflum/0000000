"""Bounded native acceptance for the prepared Figure Transform; restore test edits."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets

ROOT=Path(__file__).parent
BASE='http://127.0.0.1:8080/api/v1'
EFFECT=1789344968199
SCALE=1789344968183
PREPARED=('Position X','Position Y','Scale')
def native(path,value=None):
 request=urllib.request.Request(BASE+path,data=None if value is None else json.dumps({'value':value}).encode(),method='GET' if value is None else 'PUT',headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(request,timeout=3) as f:
  raw=f.read();return json.loads(raw) if raw else None
def snapshot():
 result={}
 for eid in (1788149968455,EFFECT):
  effect=native(f'/composition/effects/by-id/{eid}')
  result[str(eid)]={'effect':effect,'programs':{key:native(f"/parameter/by-id/{p['id']}/phase-source") for key,p in effect['params'].items() if p.get('valuetype') in ('ParamRange','ParamNumber','ParamFloat','ParamInt')}}
 return result
def program(p):
 return {'source':p['phase_source'],'fields':{k:v for k,v in p.get('parameters',{}).items() if k!='Finished'}}
async def main():
 before=json.loads((ROOT/'preinstall-native.json').read_text());report={};latest={}
 async with websockets.connect('ws://127.0.0.1:8876',max_size=4*1024*1024) as ws:
  async def send(**data):await ws.send(json.dumps(data))
  async def wait(predicate,seconds=8):
   deadline=time.monotonic()+seconds
   while time.monotonic()<deadline:
    m=json.loads(await asyncio.wait_for(ws.recv(),seconds));latest[m['type']]=m
    if predicate(latest):return
   raise AssertionError('Heart state did not converge')
  async def drain(seconds):
   deadline=time.monotonic()+seconds
   while time.monotonic()<deadline:
    m=json.loads(await asyncio.wait_for(ws.recv(),seconds+1));latest[m['type']]=m
  def scale_drive(on):return lambda x:x.get('state',{}).get('values',{}).get(str(SCALE),{}).get('drive') is on
  def scale_prepared(on):
   return lambda x:any(p['id']==SCALE and bool(p.get('native_phase')) is on for t in x.get('catalog',{}).get('targets',[]) for p in t['params'])
  await wait(scale_drive(True));await send(cmd='select',target=f'effect:{EFFECT}')
  await send(cmd='drive',id=SCALE,on=False);await wait(scale_drive(False));await drain(3.5)
  report['drive_off_survives_detection']=scale_drive(False)(latest)
  assert report['drive_off_survives_detection']
  await send(cmd='drive',id=SCALE,on=True);await wait(scale_drive(True))
  phase=native(f'/parameter/by-id/{SCALE}/phase-source');direction=phase['parameters']['PlayDirection'];started=time.monotonic()
  try:
   native(f"/parameter/by-id/{direction['id']}",'>')
   await wait(scale_prepared(False));await wait(scale_drive(False))
   report['running_timeline_released_seconds']=time.monotonic()-started
  finally:native(f"/parameter/by-id/{direction['id']}",direction['value'])
  started=time.monotonic();await wait(scale_prepared(True));await wait(scale_drive(True))
  report['paused_timeline_autostart_seconds']=time.monotonic()-started
  p=native(f'/composition/effects/by-id/{EFFECT}')['params']['Rotation Z'];value=min(p['max'],p['value']+.25)
  try:
   await send(cmd='manual',id=p['id'],value=value);await drain(.5)
   actual=native(f"/parameter/by-id/{p['id']}")['value'];report['static_manual_value']=actual
   assert abs(actual-value)<1e-4
   assert not latest['state']['values'][str(p['id'])]['drive']
  finally:await send(cmd='manual',id=p['id'],value=p['value']);await drain(.5)
  samples=[];started=time.monotonic()
  for _ in range(60):
   fx=native(f'/composition/effects/by-id/{EFFECT}');samples.append({key:fx['params'][key]['value'] for key in PREPARED});await asyncio.sleep(.025)
  report['native_movement']={key:max(s[key] for s in samples)-min(s[key] for s in samples) for key in PREPARED}
  for key in PREPARED:
   p=before[str(EFFECT)]['effect']['params'][key];lo,hi=sorted((p['in'],p['out']))
   assert all(lo-1e-4<=s[key]<=hi+1e-4 for s in samples);assert report['native_movement'][key]>.01
  after=snapshot();(ROOT/'after-native.json').write_text(json.dumps(after,indent=2))
  report['native_programs_preserved']={eid:{key:program(p)==program(after[eid]['programs'][key]) for key,p in entry['programs'].items()} for eid,entry in before.items()}
  report['static_values_preserved']={eid:{key:p['value']==after[eid]['effect']['params'][key]['value'] for key,p in entry['effect']['params'].items() if eid!=str(EFFECT) or key not in PREPARED} for eid,entry in before.items()}
  report['ranges_preserved']={eid:{key:all(p.get(k)==after[eid]['effect']['params'][key].get(k) for k in ('in','out','min','max')) for key,p in entry['effect']['params'].items()} for eid,entry in before.items()}
  for key in ('native_programs_preserved','static_values_preserved','ranges_preserved'):assert all(all(v.values()) for v in report[key].values()),(key,report[key])
  await drain(.5);report['state']={k:v for k,v in latest['state'].items() if k not in ('values','drive_bank','groups','rack','performance','session','controllers','selected_clip','effect_rack')}
  (ROOT/'live-verification.json').write_text(json.dumps(report,indent=2))
  print(json.dumps({k:v for k,v in report.items() if k not in ('native_programs_preserved','static_values_preserved','ranges_preserved','state')},indent=2))
  print('All native programs, static values and ranges preserved; three Transform drives running.')
asyncio.run(main())
