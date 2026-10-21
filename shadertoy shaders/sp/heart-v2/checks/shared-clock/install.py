"""Reload Heart only, restoring current motion against unchanged native identities."""
import asyncio,json,os,signal,subprocess,time,shutil
from pathlib import Path
import websockets,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from catalog_updates import apply_patch
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
async def receive(ws,predicate,seconds=30):
 latest={}
 async with asyncio.timeout(seconds):
  while True:
   m=json.loads(await ws.recv())
   if m['type']=='catalog_patch' and 'catalog' in latest:latest['catalog']=apply_patch(latest['catalog'],m['patch'])
   else:latest[m['type']]=m
   if predicate(latest):return latest

def contracts(c):
 return {p['id']:(t['id'],t.get('kind'),t.get('scope'),t.get('layer_id'),t.get('clip_id'),p['name'],p['type'],p['min'],p['max'],p.get('native_phase')) for t in c['targets'] for p in t['params']}

async def main():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  snap=await receive(ws,lambda x:'catalog' in x and 'state' in x);watched=None
  async with asyncio.timeout(10):
   while True:
    c=snap['catalog'];s=snap['state'];targets={t['id'] for t in c['targets'] if t['id']==s['selected'] or any(p.get('native_phase') for p in t['params'])}
    wanted={str(p['id']) for t in c['targets'] if t['id'] in targets for p in t['params']}
    if watched==targets and wanted.issubset(s['values']):break
    if watched!=targets:await ws.send(json.dumps(dict(cmd='watch',targets=sorted(targets),native_ids=[])));watched=targets
    m=json.loads(await ws.recv());snap[m['type']]=m
  (OUT/'preinstall-heart-reload.json').write_text(json.dumps(snap,indent=2));before=contracts(c);state=s
  original=json.loads((OUT/'preinstall-heart.json').read_text())
  if original['catalog']['epoch']==c['epoch']:
   before=contracts(original['catalog']);state=original['state']
  await ws.send(json.dumps(dict(cmd='arm',on=False)));await receive(ws,lambda x:x.get('state',{}).get('armed') is False)
 rows=[r.split(None,2) for r in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()]
 servers=[int(pid) for pid,ppid,cmd in rows if cmd.endswith(str(ROOT/'server.py'))];assert len(servers)==1,servers
 children=[int(pid) for pid,ppid,cmd in rows if int(ppid)==servers[0] and any(cmd.endswith(str(ROOT/name)) for name in ('bridge.py','discovery.py','scan.py'))]
 surfaces=[int(pid) for pid,ppid,cmd in rows if cmd==str(ROOT/'Heart Surface.app/Contents/MacOS/HeartSurface')]
 for pid in surfaces:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 for name in ('playing.js','playing.css','index.html','index.next.html'):shutil.copy(OUT/'surface'/name,ROOT/name)
 for pid in servers+children:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 await asyncio.sleep(.5)
 with (OUT/'server.log').open('a') as log:
  child=subprocess.Popen([str(ROOT.parent/'engine/.venv/bin/python'),str(ROOT/'server.py')],cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
 (OUT/'installed-pid.txt').write_text(str(child.pid))
 await asyncio.sleep(2)
 subprocess.run(['open','-g',str(ROOT/'Heart Surface.app')],check=True)
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  fresh=await receive(ws,lambda x:x.get('state',{}).get('connected') and x.get('catalog',{}).get('native_phase_mode'))
  assert fresh['catalog']['epoch']==c['epoch'],'Composition changed; keep the new session disarmed'
  # Give the existing standalone window time to reload its updated assets and
  # finish the existing two-second reload lease before restoring motion.
  await asyncio.sleep(2)
  await ws.send(json.dumps(dict(cmd='watch',targets=sorted(watched),native_ids=[])))
  wanted_prepared={int(pid) for pid,v in state['values'].items() if v.get('native_phase')}
  def prepared(x):
   c=x.get('catalog')
   if not c:return False
   ps={p['id']:p for t in c['targets'] for p in t['params']}
   return all(ps[pid].get('_phase_checked') for pid in wanted_prepared&ps.keys())
  fresh=await receive(ws,prepared);current=fresh['catalog']
  if not current:
   await ws.send(json.dumps(dict(cmd='refresh',warm=True)))
   # A new read-only client receives the current catalogue without native IO.
   async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as read:
    current=(await receive(read,lambda x:'catalog' in x))['catalog']
  after=contracts(current);same={pid for pid,contract in after.items() if before.get(pid)==contract};targets={t['id'] for t in current['targets']}
  if state['selected'] in targets:await ws.send(json.dumps(dict(cmd='select',target=state['selected'])))
  if state['armed']:
   
   for attempt in range(6):
    await ws.send(json.dumps(dict(cmd='arm',on=True)))
    try:
     await receive(ws,lambda x:x.get('state',{}).get('armed'),3);break
    except TimeoutError:
     if attempt==5:raise
   await ws.send(json.dumps(dict(cmd='hold',on=True)))
   for target,g in state.get('groups',{}).items():
    if target in targets:
     await ws.send(json.dumps(dict(cmd='relationship',target=target,seconds=0,**{k:g[k] for k in ('pattern','spread','seed','fm')})))
     await ws.send(json.dumps(dict(cmd='settings',target=target,amount=g['depth'],rate=g['speed'],seconds=0)))
   for key,value in state.get('motion_multipliers',{}).items():
    if key=='global':data=dict(scope='global')
    elif key.startswith('group:'):data=dict(scope='group',group_id=int(key.split(':')[1]))
    elif key.startswith('layer:'):data=dict(scope='layer',layer_id=int(key.split(':')[1]))
    elif key.startswith('stage:'):
     _,gid,section=key.split(':',2);data=dict(scope='stage',group_id=int(gid),section=section)
    else:continue
    await ws.send(json.dumps(dict(cmd='motion_multiplier',epoch=current['epoch'],value=value,seconds=0,**data)))
   for key,v in state['values'].items():
    pid=int(key)
    if pid not in same or not v.get('native_phase'):continue
    motion={k:value for k,value in (v.get('motion') or {}).items() if k in ('ratio','mult','offset','shape','amount','range_offset','scope_family')}
    await ws.send(json.dumps(dict(cmd='parameter_motion',id=pid,seconds=0,**motion)))
    await ws.send(json.dumps(dict(cmd='drive',id=pid,on=v['drive'])))
    await ws.send(json.dumps(dict(cmd='parameter_lock',epoch=current['epoch'],id=pid,on=v.get('locked',False))))
   await ws.send(json.dumps(dict(cmd='hold',on=state['hold'])))
  expected={pid:v for pid,v in state['values'].items() if int(pid) in same and v.get('native_phase')}
  def restored(x):
   s=x.get('state',{});return s.get('armed')==state['armed'] and s.get('hold')==state['hold'] and all(s.get('values',{}).get(pid,{}).get('drive')==v['drive'] and all(s['values'][pid]['motion'].get(k)==value for k,value in v['motion'].items() if k in ('ratio','mult','offset','shape','scope_family')) for pid,v in expected.items())
  final=await receive(ws,restored);(OUT/'installed-state.json').write_text(json.dumps(final,indent=2))
  print(json.dumps(dict(restored=len(expected),armed=final['state']['armed'],hold=final['state']['hold'],bpm=final['state']['bpm'],metrics=final['state']['metrics'],error=final['state']['error'])))
asyncio.run(main())
