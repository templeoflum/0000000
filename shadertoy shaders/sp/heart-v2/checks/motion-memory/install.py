"""Carry existing motion preferences into the first persistent Heart runtime."""
import asyncio,json,os,signal,subprocess,sys,time
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from server import Engine,NUM
from motion_memory import MotionMemory,identity,contract,slot_settings
from catalog_updates import apply_patch

async def snapshot(ws,complete=True,timeout=25):
 c=None;s=None;watched=None
 await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
 async with asyncio.timeout(timeout):
  while True:
   m=json.loads(await ws.recv())
   if m['type']=='catalog':c=m
   elif m['type']=='catalog_patch' and c:c=apply_patch(c,m['patch'])
   elif m['type']=='state':s=m
   if not c or not c.get('native_phase_mode'):continue
   targets={t['id'] for t in c['targets'] if any(p['type'] in NUM for p in t['params'])}
   if complete and watched!=targets:
    watched=targets;s=None;await ws.send(json.dumps(dict(cmd='watch',targets=sorted(targets),native_ids=[])));continue
   pids={str(p['id']) for t in c['targets'] if t['id'] in targets for p in t['params']}
   if s and s['connected'] and (not complete or (pids.issubset(s['values']) and targets.issubset(s['groups']))):return dict(catalog=c,state=s)

async def until_state(ws,predicate,seconds=20):
 async with asyncio.timeout(seconds):
  while True:
   s=json.loads(await ws.recv())
   if s['type']=='state' and predicate(s):return s

async def main():
 rows=[r.split(None,2) for r in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()]
 servers=[int(pid) for pid,ppid,cmd in rows if cmd.endswith(str(ROOT/'server.py'))];assert len(servers)==1,servers
 children=[int(pid) for pid,ppid,cmd in rows if int(ppid)==servers[0] and any(cmd.endswith(str(ROOT/name)) for name in ('bridge.py','discovery.py','scan.py'))]
 assert any(cmd==str(ROOT/'Heart Surface.app/Contents/MacOS/HeartSurface') for pid,ppid,cmd in rows),'Standalone Heart must remain open'
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  before=await snapshot(ws);c=before['catalog'];s=before['state'];(OUT/'before-heart.json').write_text(json.dumps(before))
  e=Engine();e.rack_config=c.get('effect_rack',{});e.reconcile(c)
  for tid,g in s['groups'].items():
   if tid in e.groups:e.groups[tid].update(g)
  for pid,sl in e.slots.items():
   v=s['values'].get(str(pid))
   if not v or not v.get('motion'):continue
   sl.cfg.update(slot_settings(v['motion']),lock=v.get('locked',False))
   if v.get('native_phase'):sl.drive_intent=v['drive']
  # Current source families are per-slot. The old runtime did not expose hidden
  # family positions, so reject an ambiguous migration instead of guessing.
  assert all(g.get('pattern',0)==0 or all('family_slot' in (s['values'].get(str(p['id']),{}).get('motion') or {}) for p in t['params'] if s['values'].get(str(p['id']),{}).get('drive')) for t in c['targets'] if (g:=s['groups'].get(t['id']))),'Capture of an older hidden family assignment is required'
  assert all(row.get('pattern') in (None,0) for row in s['stage_motion']),'Capture of an older stage family assignment is required'
  e.motion_multipliers={k:dict(value=v,**{'from':v},started=0.,seconds=0.) for k,v in s['motion_multipliers'].items()}
  e.motion_memory.capture(e)
  path=ROOT/'motion-settings.json'
  if path.exists():(OUT/'before-motion-settings.json').write_bytes(path.read_bytes())
  MotionMemory.write(path,e.motion_memory.data)
  (OUT/'seed-motion-settings.json').write_bytes(path.read_bytes())
  await ws.send(json.dumps(dict(cmd='arm',on=False)));await until_state(ws,lambda x:not x['armed'])
 for pid in servers+children:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 await asyncio.sleep(.5)
 with (OUT/'server.log').open('a') as log:
  child=subprocess.Popen([str(ROOT.parent/'engine/.venv/bin/python'),str(ROOT/'server.py')],cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
 (OUT/'installed-pid.txt').write_text(str(child.pid))
 await asyncio.sleep(1)
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  fresh=await snapshot(ws);assert fresh['catalog']['epoch']==c['epoch'],'Composition changed during reload'
  targets={t['id'] for t in fresh['catalog']['targets']}
  if s['selected'] in targets:await ws.send(json.dumps(dict(cmd='select',target=s['selected'])))
  if s['armed']:
   for attempt in range(6):
    await ws.send(json.dumps(dict(cmd='arm',on=True)))
    try:await until_state(ws,lambda x:x['armed'],3);break
    except TimeoutError:
     if attempt==5:raise
   if s['hold']:await ws.send(json.dumps(dict(cmd='hold',on=True)))
  await asyncio.sleep(1)
  # A new observer obtains the latest native identities without a full native scan.
  async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as read:
   after=await snapshot(read)
  (OUT/'after-heart.json').write_text(json.dumps(after));new=after['state'];newtargets={t['id']:t for t in after['catalog']['targets']}
  checked=0;prepared=0;failures=[]
  for t in c['targets']:
   nt=newtargets.get(t['id'])
   if not nt or identity(t)!=identity(nt):continue
   np={p['id']:p for p in nt['params']}
   for p in t['params']:
    pid=p['id'];old=s['values'].get(str(pid));v=new['values'].get(str(pid))
    if not old or not old.get('motion') or not v or pid not in np or contract(p)!=contract(np[pid]):continue
    expected=slot_settings(old['motion']);actual=slot_settings(v['motion'])
    if any(actual.get(k)!=value for k,value in expected.items()):failures.append([pid,'motion',expected,actual])
    if v['locked']!=old['locked']:failures.append([pid,'lock'])
    if old.get('native_phase') and v.get('native_phase'):
     prepared+=1
     if s['armed'] and old['drive']!=v['drive']:failures.append([pid,'drive'])
    checked+=1
   if t['id'] in s['groups'] and new['groups'].get(t['id'])!=s['groups'][t['id']]:failures.append([t['id'],'group'])
  result=dict(checked=checked,prepared=prepared,failures=failures,armed=new['armed'],hold=new['hold'],bpm=new['bpm'],error=new['error'],metrics=new['metrics'])
  (OUT/'installed-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not failures,failures
asyncio.run(main())
