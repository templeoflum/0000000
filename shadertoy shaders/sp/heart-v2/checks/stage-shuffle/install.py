"""Reload Heart with the stage panel, retaining current per-parameter motion settings."""
import asyncio,json,os,signal,subprocess,time
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
async def receive(ws,predicate,seconds=30):
 latest={};end=time.monotonic()+seconds
 while time.monotonic()<end:
  m=json.loads(await asyncio.wait_for(ws.recv(),seconds));latest[m['type']]=m
  if predicate(latest):return latest
 raise RuntimeError('Heart did not reach expected state')
def parameters(c):return {p['id']:p for t in c['targets'] for p in t['params']}
async def main():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  snap=await receive(ws,lambda x:'state' in x and 'catalog' in x)
  await ws.send(json.dumps(dict(cmd='watch',targets=[t['id'] for t in snap['catalog']['targets']],native_ids=[])))
  state=(await receive(ws,lambda x:'state' in x and len(x['state']['values'])>=len(parameters(snap['catalog']))))['state']
  snap['state']=state;(OUT/'preinstall-heart.json').write_text(json.dumps(snap,indent=2))
  await ws.send(json.dumps(dict(cmd='arm',on=False)));await receive(ws,lambda x:x.get('state',{}).get('armed') is False)
 rows=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()
 servers=[int(r.split(None,2)[0]) for r in rows if r.strip().endswith(str(ROOT/'server.py'))];assert len(servers)==1,servers
 children=[int(r.split(None,2)[0]) for r in rows if int(r.split(None,2)[1])==servers[0] and r.strip().endswith(str(ROOT/'bridge.py'))]
 for pid in servers+children:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 await asyncio.sleep(.5)
 log=open(OUT/'server.log','a');child=subprocess.Popen([str(ROOT.parent/'engine/.venv/bin/python'),str(ROOT/'server.py')],cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
 (OUT/'installed-pid.txt').write_text(str(child.pid));await asyncio.sleep(2)
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  await ws.send(json.dumps(dict(cmd='select',target=state['selected'])))
  wanted={int(pid) for pid,v in state['values'].items() if v.get('native_phase')};before=parameters(snap['catalog'])
  def discovered(x):
   if 'catalog' not in x or not x.get('state',{}).get('connected'):return False
   ps=parameters(x['catalog']);return all(ps[pid].get('_phase_checked') for pid in wanted&ps.keys())
  fresh=await receive(ws,discovered);assert fresh['catalog']['epoch']==snap['catalog']['epoch'];ps=parameters(fresh['catalog'])
  same={pid for pid,p in ps.items() if pid in before and all(p.get(k)==before[pid].get(k) for k in ('name','type','min','max'))}
  if state['armed']:
   await ws.send(json.dumps(dict(cmd='arm',on=True)));await ws.send(json.dumps(dict(cmd='hold',on=True)))
   targets={t['id'] for t in fresh['catalog']['targets']}
   for target,g in state.get('groups',{}).items():
    if target not in targets:continue
    await ws.send(json.dumps(dict(cmd='relationship',target=target,seconds=0,**{k:g[k] for k in ('pattern','spread','seed','fm')})))
    await ws.send(json.dumps(dict(cmd='settings',target=target,amount=g['depth'],rate=g['speed'])))
   for key,v in state['values'].items():
    pid=int(key)
    if pid not in same:continue
    if v.get('motion'):await ws.send(json.dumps(dict(cmd='parameter_motion',id=pid,seconds=0,**{k:v['motion'][k] for k in ('ratio','mult','offset','shape')})))
    if ps[pid].get('native_phase') and v.get('native_phase'):await ws.send(json.dumps(dict(cmd='drive',id=pid,on=v['drive'])))
    if v.get('locked'):await ws.send(json.dumps(dict(cmd='parameter_lock',id=pid,on=True)))
   await ws.send(json.dumps(dict(cmd='hold',on=state['hold'])))
  watch=[t['id'] for t in fresh['catalog']['targets'] if any(p['id'] in wanted for p in t['params'])]
  await ws.send(json.dumps(dict(cmd='watch',targets=watch,native_ids=[])))
  driven={pid:v for pid,v in state['values'].items() if v.get('drive') and int(pid) in same and ps[int(pid)].get('native_phase')}
  def restored(x):
   s=x.get('state',{})
   return s.get('armed')==state['armed'] and s.get('hold')==state['hold'] and all(s.get('values',{}).get(pid,{}).get('drive') and all(s['values'][pid]['motion'][k]==v['motion'][k] for k in ('ratio','mult','offset','shape')) for pid,v in driven.items())
  final=(await receive(ws,restored))['state'];(OUT/'installed-state.json').write_text(json.dumps(final,indent=2))
  print('Restored motion settings for',len(driven),'active prepared parameters.')
  print('Stage motion:',[(s['label'],s['prepared'],s['driven']) for s in final['stage_motion']]);print('Error:',final['error'])
asyncio.run(main())
