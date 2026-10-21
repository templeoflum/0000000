"""Validate the saved running controls and restore through Heart's normal protocol.

No native writes, launches, range changes or native program resets. Heart range
commands below restore only the ten existing LinearCloner motion windows.
"""
import asyncio, json, sys, time
from pathlib import Path
import websockets
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from server import Engine

def contract(t,p):
 return (t['id'],t['kind'],t.get('layer_id'),t.get('clip_id'),p['id'],p['name'],p['type'],p['min'],p['max'])

def commands(saved,current):
 live={p['id']:(t,p) for t in current['targets'] for p in t['params']}
 old={p['id']:(t,p) for t in saved['catalog']['targets'] for p in t['params']}
 result=[];groups=set();drives=[]
 for key,value in saved['state']['values'].items():
  if not value['drive']:continue
  pid=int(key);t,p=old[pid]
  if pid not in live or contract(t,p)!=contract(*live[pid]):raise ValueError('Saved drive identity changed: '+p['name'])
  if value.get('rate_scale',1)!=1 or value.get('intensity_scale',1)!=1:raise ValueError('Additional musical scaling needs explicit restoration')
  if t['id'] not in groups:
   groups.add(t['id']);g=saved['state']['groups'][t['id']]
   result.extend([dict(cmd='settings',target=t['id'],amount=g['depth'],rate=g['speed']),dict(cmd='relationship',target=t['id'],seconds=0,**{k:g[k] for k in ('pattern','spread','seed','fm')})])
  result.extend([dict(cmd='range',id=pid,lo=value['lo'],hi=value['hi']),dict(cmd='parameter_motion',id=pid,seconds=0,**{k:value['motion'][k] for k in ('ratio','mult','offset','shape')}),dict(cmd='parameter_lock',epoch=current['epoch'],id=pid,on=value['locked'])])
  drives.append(dict(cmd='drive',id=pid,on=True))
 return result+drives

def verify(saved,actual):
 for pid,v in saved['state']['values'].items():
  if not v['drive']:continue
  now=actual['values'][pid]
  for k in ('drive','locked','lo','hi','rate_scale','intensity_scale'):
   assert now[k]==v[k],(pid,k,now[k],v[k])
  for k in ('ratio','mult','offset','shape'):assert now['motion'][k]==v['motion'][k],(pid,k)
 for tid,g in saved['state']['groups'].items():
  if any(v['drive'] and any(str(p['id'])==pid for t in saved['catalog']['targets'] if t['id']==tid for p in t['params']) for pid,v in saved['state']['values'].items()):
   for k in ('pattern','spread','seed','depth','fm','speed'):assert actual['groups'][tid][k]==g[k],(tid,k)

def offline(saved,current):
 plan=commands(saved,current);e=Engine();e.reconcile(current);e.armed=e.connected=True;e.watched=set(e.groups)
 for d in plan:
  if d['cmd']=='settings':e.settings(d['target'],d)
  elif d['cmd']=='relationship':e.relationship(d['target'],d)
  elif d['cmd']=='range':e.param_range(d['id'],d['lo'],d['hi'])
  elif d['cmd']=='parameter_motion':e.parameter_motion(d['id'],d)
  elif d['cmd']=='parameter_lock':e.parameter_lock(d)
  elif d['cmd']=='drive':e.drive(d['id'],d['on'])
 state=json.loads(json.dumps(e.state()));verify(saved,state)
 (HERE/'restoration-plan.json').write_text(json.dumps(plan,indent=2))
 return dict(verified=True,drives=sum(d['cmd']=='drive' for d in plan),commands=len(plan))

async def live():
 saved=json.loads((HERE/'before-heart.json').read_text())
 async with websockets.connect('ws://127.0.0.1:8876') as ws:
  catalog=None
  async with asyncio.timeout(15):
   while True:
    m=json.loads(await ws.recv())
    if m.get('type')=='catalog':catalog=m;await ws.send(json.dumps(dict(cmd='watch',targets=[t['id'] for t in catalog['targets']],native_ids=[])))
    if m.get('type')=='state' and catalog and len(m['groups'])==len(catalog['targets']) and m['connected']:break
  if '--restore' not in sys.argv:
   result=offline(saved,catalog);result.update(current_armed=m['armed'],current_owned=m['metrics']['owned']);(HERE/'restoration-proof.json').write_text(json.dumps(result,indent=2));print(result);return
  assert any(t.get('native_phase_clip') for t in catalog['targets']),'Candidate phase server not installed'
  plan=commands(saved,catalog)
  await ws.send(json.dumps(dict(cmd='arm',on=True,autostart=[1788149968226])))
  await asyncio.sleep(.15)
  for d in plan:await ws.send(json.dumps(d))
  await ws.send(json.dumps(dict(cmd='select',target='source:1788149968226')))
  async with asyncio.timeout(12):
   while True:
    m=json.loads(await ws.recv())
    if m.get('type')!='state' or len(m['groups'])!=len(catalog['targets']):continue
    try:verify(saved,m)
    except (KeyError,AssertionError):continue
    prepared=[p['id'] for t in catalog['targets'] for p in t['params'] if p.get('native_phase')]
    if all(m['values'][str(pid)]['drive'] for pid in prepared):break
  (HERE/'restored-heart.json').write_text(json.dumps(dict(catalog=catalog,state=m),indent=2));print(dict(restored=10,shell_drives=len(prepared),armed=m['armed'],error=m['error']))

if __name__=='__main__':asyncio.run(live())
