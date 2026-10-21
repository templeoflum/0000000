"""Exhaustive existing-source smoke/recovery pass. One live writer; resumable evidence.
Short test morph is restored before switching. This does not certify smoothness.
"""
import asyncio,json,pathlib,urllib.request,sys,time
import websockets
ROOT=pathlib.Path(__file__).resolve().parents[2];P=ROOT/'sp/show-day/content/full-library';P.mkdir(exist_ok=True)
B='http://localhost:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=10))
def put(path,value):urllib.request.urlopen(urllib.request.Request(B+path,json.dumps(value).encode(),{'Content-Type':'application/json'},method='PUT'),timeout=10).close()
def snapshot(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
def native(clip):return {n:p for n,p in (clip['video'].get('sourceparams') or {}).items() if isinstance(p,dict)}
def numeric(p):return isinstance(p.get('value'),(int,float)) and not isinstance(p.get('value'),bool) and 'min' in p and 'max' in p
sys.path.insert(0,str(ROOT/'sp/audit/shader-progress'));from update import publish
async def main():
 comp=await asyncio.to_thread(get,'/composition');
 if not P.joinpath('before.json').exists():P.joinpath('before.json').write_text(json.dumps(comp))
 levels=[l['video']['opacity'] for l in comp['layers']]
 previous={i+1:next((j+1 for j,c in enumerate(l['clips']) if str(c.get('connected',{}).get('value','')).startswith('Connected')),None) for i,l in enumerate(comp['layers'])}
 old=set()
 for folder in ['adaptive-pass','adaptive-batch2','adaptive-batch3','adaptive-batch4','original-six']:
  f=P.parent/folder/'live-results.json'
  if f.exists():
   for r in json.loads(f.read_text()):
    if 'error' not in r:old.add((3,r['col']))
 rows=[];seen={};routed=[]
 for li,l in enumerate(comp['layers'],1):
  if li==6:continue
  for col,c in enumerate(l['clips'],1):
   v=c.get('video') or {};source=v.get('description')
   if not source:continue
   params=v.get('sourceparams')or{};sig=(li,source,json.dumps([(n,p.get('valuetype'),p.get('min'),p.get('max')) for n,p in params.items() if isinstance(p,dict)],sort_keys=True))
   row=dict(layer=li,col=col,source=source,name=c['name']['value'])
   if source in ('Video Router','Feedback'):routed.append(dict(row,status='routing; covered by separate routing rehearsal'));continue
   if sig in seen:rows.append(dict(row,status='duplicate schema',representative=seen[sig]));continue
   seen[sig]=[li,col]
   if (li,col) in old:rows.append(dict(row,status='previously checked'));continue
   rows.append(row)
 P.joinpath('inventory.json').write_text(json.dumps(dict(rows=rows,routing=routed,glyph='deferred per user'),indent=2))
 results=json.loads(P.joinpath('results.json').read_text()) if P.joinpath('results.json').exists() else []
 done={(r['layer'],r['col']) for r in results};todo=[r for r in rows if 'status' not in r and (r['layer'],r['col']) not in done]
 print('QUEUE',len(todo),'previous',len(old),'duplicates',sum(r.get('status')=='duplicate schema' for r in rows),'routing',len(routed),flush=True)
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  def active(li,col):return next((c for c in state.get('clips',[]) if c.get('layer')==li and c.get('col')==col),None)
  async def waitclip(li,col,oldinstance=None):
   for _ in range(35):
    await asyncio.sleep(.15);c=active(li,col)
    if c and c.get('slots') and (not oldinstance or c['instance']!=oldinstance):return c
   return None
  async def clear(li):await asyncio.to_thread(put,f'/composition/layers/{li}/clear',True)
  async def action(cmd,a,marker,**kw):
   old_events=list(state.get('events',[]));await send(cmd,**a,**kw)
   for _ in range(250):
    await asyncio.sleep(.1)
    if any(marker in e and e not in old_events for e in state.get('events',[])):break
   else:raise RuntimeError('Command completion timed out: '+cmd)
   for _ in range(100):
    await asyncio.sleep(.1);c=active(a['layer'],a['col'])
    if c and not any(s.get('morphing') for s in c['slots']):break
   await asyncio.sleep(.25)
  current_layer=None
  try:
   for row in todo:
    if P.joinpath('PAUSE').exists():print('Paused at source boundary',flush=True);break
    li,col=row['layer'],row['col'];key=f'L{li}C{col}';result=dict(row);a=None;oldmorph=3
    try:
     if current_layer!=li:
      for idx,p in enumerate(levels,1):await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",1. if idx==li else 0.)
      current_layer=li
     await send('launch',layer=li,col=col);c=await waitclip(li,col)
     if not c:
      clip=await asyncio.to_thread(get,f'/composition/layers/{li}/clips/{col}')
      assert str(clip['connected']['value']).startswith('Connected'),'Native launch failed'
      await asyncio.to_thread(snapshot,key+'-home');await asyncio.sleep(.8);await asyncio.to_thread(snapshot,key+'-shuffle')
      result.update(status='render-only',reason='No Heart numeric slots; no invented controls',parameters=list(native(clip)))
     else:
      a=dict(layer=li,col=col,instance=c['instance']);oldmorph=c['morph'];await send('morph',**a,seconds=.35)
      await action('home',a,': → Home · rest',factory=True)
      before=native(await asyncio.to_thread(get,f'/composition/layers/{li}/clips/{col}'));await asyncio.to_thread(snapshot,key+'-home')
      slots={s['name']:s for s in active(li,col)['slots']};missing=[n for n,p in before.items() if numeric(p) and not n.endswith((' Drive',' Lock',' Ratio',' Mult',' Offset',' Shape',' Lo',' Hi')) and n not in slots]
      await action('open',a,': → Open');opened=active(li,col);driven=[s['name'] for s in opened['slots'] if s['drive']]
      samples=[]
      for _ in range(3):
       ns=native(await asyncio.to_thread(get,f'/composition/layers/{li}/clips/{col}'));samples.append({n:ns[n]['value'] for n in driven if n in ns and numeric(ns[n])});await asyncio.sleep(.4)
      motions=[n for n in driven if all(n in s for s in samples) and max(s[n] for s in samples)-min(s[n] for s in samples)>1e-5]
      await action('timing',a,'timing',mode='harmonic');await asyncio.to_thread(snapshot,key+'-shuffle')
      await action('home',a,': → Home · rest',factory=True)
      settled=active(li,col);final=native(await asyncio.to_thread(get,f'/composition/layers/{li}/clips/{col}'))
      errors={n:[p['value'],final[n]['value']] for n,p in before.items() if n in slots and numeric(p) and n in final and abs(p['value']-final[n]['value'])>max(.002,(p['max']-p['min'])*.004)}
      if any(s['drive'] for s in settled['slots']):errors['drives']='not settled'
      await send('morph',**a,seconds=oldmorph)
      # Switch to another occupied source, then back, to exercise actual rediscovery.
      ref=next(j+1 for j,x in enumerate(comp['layers'][li-1]['clips']) if j+1!=col and x.get('video'))
      await send('launch',layer=li,col=ref)
      for _ in range(100):
       await asyncio.sleep(.1)
       if not active(li,col):break
      else:raise RuntimeError('Previous controller did not release before relaunch')
      await send('launch',layer=li,col=col);again=await waitclip(li,col,a['instance']);await asyncio.sleep(3.25)
      if not again:errors['relaunch']='controller not rediscovered'
      else:
       again=active(li,col)
       if any(s['drive'] for s in again['slots']):errors['relaunch_drive']='re-enabled'
       returned=native(await asyncio.to_thread(get,f'/composition/layers/{li}/clips/{col}'))
       re={n:[p['value'],returned[n]['value']] for n,p in final.items() if n in slots and numeric(p) and n in returned and abs(p['value']-returned[n]['value'])>max(.002,(p['max']-p['min'])*.004)}
       if re:errors['relaunch_values']=re
      if driven and not motions:errors['motion']='No native motion observed in short sample'
      result.update(status='review' if errors else 'pass' if driven else 'manual-only',driven=driven,moving=motions,errors=errors,slots=len(slots),source_numeric_not_slots=missing,adaptation=opened.get('adaptation'),samples=samples,home_recovered=not errors,test_morph_seconds=.35)
    except Exception as exc:result.update(status='error',error=str(exc))
    finally:
     if a and result.get('status') in ('error','review'):
      c=active(li,col)
      if c:
       try:
        await send('home',layer=li,col=col,instance=c['instance'],factory=True);await send('morph',layer=li,col=col,instance=c['instance'],seconds=oldmorph)
       except Exception:pass
    results.append(result);P.joinpath('results.json').write_text(json.dumps(results,indent=2))
    counts={s:sum(r['status']==s for r in results) for s in ('pass','manual-only','render-only','review','error')}
    msg=f"Full library {len(results)}/{len(todo)+len(done)}: {key} {row['source']} — {result['status']}. {counts}"
    print(msg,flush=True);publish(msg,phase='Building')
   if not P.joinpath('PAUSE').exists():P.joinpath('finished.json').write_text(json.dumps(dict(completed=True,counts=counts,total=len(results),scope='All unique non-Glyph existing source schemas; prior checked sources and routers listed separately.'),indent=2))
  finally:
   for li,col in previous.items():
    if col:await send('launch',layer=li,col=col)
    elif li in (3,5,7,8):await send('clear',layer=li)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   task.cancel()
asyncio.run(main())
