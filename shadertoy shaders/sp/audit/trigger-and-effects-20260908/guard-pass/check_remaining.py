import asyncio,json,time,urllib.request,sys
from pathlib import Path
import websockets
P=Path(__file__).parent;sys.path.insert(0,str(P.resolve().parents[2]/'engine'));import targets
B='http://localhost:8080/api/v1'
def req(path,method='GET',data=None):
 raw=None if data is None else (json.dumps(data) if not isinstance(data,str) else data).encode();h={'Content-Type':'text/plain' if isinstance(data,str) else 'application/json'}
 with urllib.request.urlopen(urllib.request.Request(B+path,data=raw,method=method,headers=h),timeout=6) as r:
  out=r.read();return json.loads(out) if out else None
def put(pid,value):return req('/parameter/by-id/'+str(pid),'PUT',{'value':value})
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as ws:
  latest=json.loads(await ws.recv())
  async def consume():
   nonlocal latest
   async for m in ws:latest=json.loads(m)
  task=asyncio.create_task(consume());before=json.loads(json.dumps(latest));comp=req('/composition');made=[];results=[]
  P.joinpath('before-heart.json').write_text(json.dumps(before,indent=2));P.joinpath('before-native.json').write_text(json.dumps(comp,indent=2))
  muted=[f for f in before['fx'] if f.get('has_amount') and (f['scope']=='C' or (f['scope']=='L' and f['layer'] in (1,2,5)))]
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  async def amount(f,value):
   live=next((x for x in latest['fx'] if x['key']==f['key']),None)
   if live:await send('fx_amount',key=live['key'],instance=live['instance'],value=value)
  async def snap(label):
   for attempt in range(3):
    try:
     data=await asyncio.to_thread(lambda:urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=4).read());P.joinpath(label+'.png').write_bytes(data);return
    except TimeoutError:
     if attempt==2:raise
  try:
   await send('hold',on=True)
   for f in muted:
    await send('fx_cfg',key=f['key'],instance=f['instance'],cfg={'attack':.05,'release':.05});await amount(f,0)
   for i,l in enumerate(comp['layers'],1):
    await send('opacity',layer=i,value=0);await asyncio.to_thread(put,l['solo']['id'],False)
   await asyncio.sleep(1.5)
   for layer in (5,1,2):
    l=comp['layers'][layer-1];col=next(i+1 for i,c in enumerate(l['clips']) if not c.get('video') and not c.get('audio'))
    path=f'/composition/layers/{layer}/clips/{col}';fresh=await asyncio.to_thread(req,path);assert not fresh.get('video') and not fresh.get('audio')
    made.append((layer,col));await asyncio.to_thread(req,path+'/open','POST',P.joinpath('diagnostic.png').resolve().as_uri())
    await asyncio.to_thread(req,path+'/connect','POST','');await asyncio.to_thread(put,l['bypassed']['id'],False);await send('opacity',layer=layer,value=1);await asyncio.sleep(1)
    fxs=[f for f in latest['fx'] if f.get('has_amount') and ((layer==5 and (f['name'] in ('Iterate','Linear Cloner','Radial Cloner') or f['scope']=='C' and any(x in f['key'] for x in ('MTK_PXLMELT','lut_corrupt')))) or layer in (1,2) and f['layer']==layer and f['name'] in ('Invert RGB','Hue Rotate','Delay RGB'))]
    for f in fxs:
     index=len(results);await snap(f'{index}-before');guard=f['name'] in ('Iterate','Linear Cloner','Radial Cloner')
     if guard:
      await send('open',effect=f['key'],instance=f['instance']);await send('hold',on=False)
     else:await amount(f,1)
     await asyncio.sleep(1.2)
     for name,param in f['params'].items():
      if param.get('valuetype') in ('ParamEvent','ParamTrigger'):
       await send('fx_param',key=f['key'],instance=f['instance'],name=name,value=True);await asyncio.sleep(.25)
     if guard:
      for n in range(4):await snap(f'{index}-motion-{n}');await asyncio.sleep(1)

     for n in range(2):await snap(f'{index}-on-{n}');await asyncio.sleep(.2)
     c=await asyncio.to_thread(req,'/composition');native=next(e for k,_,_,_,e in targets.effects(c) if k==f['key']);h=next(x for x in latest['fx'] if x['key']==f['key'])
     item={'index':index,'key':f['key'],'name':f['name'],'layer':layer,'opacity':native['params']['Opacity']['value'],'bypassed':native['bypassed']['value'],'params':native['params'],'heart_amount':h['observed_amount']};results.append(item)
     if guard:
      await send('undo',effect=f['key'],instance=f['instance']);await send('hold',on=True)
     await amount(f,0);await asyncio.sleep(1.2);await snap(f'{index}-off');P.joinpath('results.json').write_text(json.dumps(results,indent=2));print(layer,f['name'],item['opacity'],item['bypassed'],flush=True)
    await send('opacity',layer=layer,value=0)
  finally:
   for layer,col in made:
    old=next(x for x in before['layers'] if x['i']==layer)
    await send('launch',layer=layer,col=old['ccol']) if old.get('ccol') else await send('clear',layer=layer)
   await asyncio.sleep(1)
   for layer,col in made:
    c=await asyncio.to_thread(req,f'/composition/layers/{layer}/clips/{col}')
    if 'diagnostic' in str(c.get('video',{})):
     await asyncio.to_thread(req,f'/composition/layers/{layer}/clips/{col}/clear','POST','')
   for i,l in enumerate(comp['layers'],1):
    await send('opacity',layer=i,value=l['video']['opacity']['value'])
    for field in ('solo','bypassed'):await asyncio.to_thread(put,l[field]['id'],l[field]['value'])
   for f in muted:await amount(f,f['target'])
   await asyncio.sleep(1.5)
   current={k:e for k,_,_,_,e in targets.effects(await asyncio.to_thread(req,'/composition'))}
   for k,_,_,_,e in targets.effects(comp):
    if k not in {f['key'] for f in muted} or k not in current:continue
    for param in ('Opacity',):
     if param in e.get('params',{}):await asyncio.to_thread(put,current[k]['params'][param]['id'],e['params'][param]['value'])
    await asyncio.to_thread(put,current[k]['bypassed']['id'],e['bypassed']['value'])
   for f in muted:
    live=next((x for x in latest['fx'] if x['key']==f['key']),None)
    if live:await send('fx_cfg',key=f['key'],instance=live['instance'],cfg=f['cfg'])
   await send('hold',on=before['hold']);await asyncio.sleep(.5)
   P.joinpath('after-heart.json').write_text(json.dumps(latest,indent=2));P.joinpath('after-native.json').write_text(json.dumps(await asyncio.to_thread(req,'/composition'),indent=2));P.joinpath('scratch.json').write_text(json.dumps(made));task.cancel();print('Restored original clips, faders, effects and hold; scratch slots cleared',flush=True)
asyncio.run(main())
