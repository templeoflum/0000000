import asyncio,json,sys,urllib.request,time
from pathlib import Path
from urllib.parse import unquote
import websockets
P=Path(__file__).parent;sys.path.insert(0,str(P.resolve().parents[1]/'engine'));import targets
B='http://localhost:8080/api/v1'
def get(path='/composition'):return json.load(urllib.request.urlopen(B+path,timeout=5))
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w,websockets.connect('ws://localhost:8080/api/v1',max_size=None) as arena:
  state=json.loads(await w.recv());before=get();P.joinpath('factory-before-heart.json').write_text(json.dumps(state,indent=2));P.joinpath('factory-before-native.json').write_text(json.dumps(before,indent=2))
  fx={f['key']:f for f in state['fx']};effects={k:e for k,_,_,_,e in targets.effects(before)};changes=[];skips=[]
  async def drain(ws):
   async for _ in ws:pass
  tasks=[asyncio.create_task(drain(ws)) for ws in (w,arena)]
  async def setparam(key,name,value,source):
   if key not in fx or name not in effects[key]['params']:skips.append([key,name]);return
   p=effects[key]['params'][name]
   if p['valuetype'] in ('ParamEvent','ParamTrigger'):skips.append([key,name,'event']);return
   if p['valuetype']=='ParamChoice':
    if isinstance(value,(float,int)) and int(value)==value:value=p['options'][int(value)]
    elif value not in p['options']:skips.append([key,name,'unmatched choice']);return
   value=targets.convert(p,value)
   await w.send(json.dumps({'cmd':'fx_param','key':key,'instance':fx[key]['instance'],'name':name,'value':value}))
   changes.append({'key':key,'name':name,'before':p.get('value'),'after':value,'source':source});await asyncio.sleep(.035)
  await w.send(json.dumps({'cmd':'hold','on':True}))
  try:
   for key,e in effects.items():
    if not key.startswith(('layer/feedback~1/effect/','layer/sculpt~1/effect/')):continue
    for name,p in e.get('params',{}).items():
     if name=='Opacity' or p.get('valuetype') not in ('ParamRange','ParamFloat'):continue
     if abs(float(p['value'])-.0267525866572923)>.00000001:continue
     await arena.send(json.dumps({'action':'reset','parameter':f"/parameter/by-id/{p['id']}"}));await asyncio.sleep(.15)
     await setparam(key,name,get(f"/parameter/by-id/{p['id']}")['value'],'native factory reset of repeated corrupt value')
   await asyncio.sleep(2)
   after=get();out={k:e for k,_,_,_,e in targets.effects(after)}
   for row in changes:
    actual=out[row['key']]['params'][row['name']]['value'];row['readback']=actual
    row['verified']=actual==row['after'] if not isinstance(actual,(int,float)) else abs(actual-row['after'])<.001
   P.joinpath('factory-repair.json').write_text(json.dumps({'changes':changes,'skipped':skips},indent=2))
   print('Changes',len(changes),'verified',sum(r['verified'] for r in changes),'skipped',skips)
  finally:
   await w.send(json.dumps({'cmd':'hold','on':state['hold']}))
   for t in tasks:t.cancel()
asyncio.run(main())
