exec(open('sp/show-day/content/original-six/check_live.py').read().split('async def main():')[0])
import argparse
parser=argparse.ArgumentParser(description='Live original-source audition using existing Heart controls')
parser.add_argument('--columns',type=int,nargs='+',required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
if any(c<1 or c==14 for c in args.columns):parser.error("Columns must be positive and exclude the parked reference clip14")
P=args.output.resolve();P.mkdir(parents=True,exist_ok=True)
if P.joinpath('live-results.json').exists():raise SystemExit('Use a fresh output folder to preserve prior evidence')
async def main():
 comp=await asyncio.to_thread(get,'/composition');levels=[l['video']['opacity'] for l in comp['layers']];previous=next((i+1 for i,c in enumerate(comp['layers'][2]['clips']) if c['connected']['value'].startswith('Connected')),None);results=[]
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  try:
   for i,p in enumerate(levels):await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",1. if i==2 else 0.)
   for col in args.columns:
    try:
     await send('launch',layer=3,col=col)
     for _ in range(50):
      await asyncio.sleep(.2);c=next((x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col),None)
      if c and c.get('slots'):break
     assert c and c.get('slots');a=dict(layer=3,col=col,instance=c['instance']);delay=max(1,c.get('morph',3))+.8
     await send('home',**a,factory=True);await asyncio.sleep(delay)
     before=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams'];await asyncio.to_thread(snapshot,f'{col}-home')
     await send('open',**a);await asyncio.sleep(delay)
     active=next(x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col);driven=[s['name'] for s in active['slots'] if s['drive']]
     assert 1<=len(driven)<=3,(col,driven)
     assert not any(n.lower() in ['rate','count','speed','time','seed'] for n in driven),driven
     samples=[]
     for _ in range(3):
      native=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams'];samples.append({n:native[n]['value'] for n in driven});await asyncio.sleep(.65)
     assert any(max(s[n] for s in samples)-min(s[n] for s in samples)>1e-5 for n in driven),(col,samples)
     await asyncio.to_thread(snapshot,f'{col}-open')
     await send('timing',**a,mode='harmonic');await asyncio.sleep(delay)
     await asyncio.to_thread(snapshot,f'{col}-shuffle')
     await send('home',**a,factory=True);await asyncio.sleep(delay)
     final=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams'];active=next(x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col)
     assert not any(s['drive'] for s in active['slots'])
     errors={n:(v['value'],final[n]['value']) for n,v in before.items() if v.get('valuetype')=='ParamRange' and abs(v['value']-final[n]['value'])>max(.001,(v['max']-v['min'])*.003)};assert not errors,(col,errors)
     await send('launch',layer=3,col=14);await asyncio.sleep(1.5)
     await send('launch',layer=3,col=col)
     for _ in range(50):
      await asyncio.sleep(.2);again=next((x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col),None)
      if again and again.get('instance')!=a['instance'] and again.get('slots'):break
     assert again and again.get('instance')!=a['instance'],('No relaunch discovery',col)
     await asyncio.sleep(delay)
     assert not any(s['drive'] for s in again['slots']),('Relaunch re-enabled drives',col)
     returned=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams']
     assert all(abs(v['value']-returned[n]['value'])<=max(.001,(v['max']-v['min'])*.003) for n,v in final.items() if v.get('valuetype')=='ParamRange'),('Relaunch changed pose',col)
     results.append(dict(shuffle_checked=True,relaunch_checked=True,source=c['name'],col=col,driven=driven,samples=samples,home_recovered=True));P.joinpath('live-results.json').write_text(json.dumps(results,indent=2));print('PASS',c['name'],driven,flush=True)
    except Exception as exc:
     results.append(dict(col=col,error=str(exc)));P.joinpath('live-results.json').write_text(json.dumps(results,indent=2));print('REVIEW',col,str(exc),flush=True)
     current=next((x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col),None)
     if current:
      await send('home',layer=3,col=col,instance=current['instance'],factory=True);await asyncio.sleep(2)
  finally:
   if previous:await send('launch',layer=3,col=previous)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   t.cancel()
asyncio.run(main())
