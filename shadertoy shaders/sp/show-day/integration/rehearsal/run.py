import asyncio,json,time,urllib.request,urllib.parse,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[2]/'engine'));import targets
B='http://localhost:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=10))
def post(path,data):return urllib.request.urlopen(urllib.request.Request(B+path,data.encode(),{'Content-Type':'text/plain'},method='POST'),timeout=10).read()
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv());assert state['arena_connected'];initial=state
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  reader=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  native=await asyncio.to_thread(get,'/composition');entries=list(targets.effects(native));selected=[]
  for name,scope,layer in [('MTK_PXLMELT','C',None),('DelayRGB','L',2)]:
   matches=[e for e in entries if e[1]==scope and e[2]==layer and e[4]['name']==name];assert len(matches)==1
   e=matches[0];f=next(f for f in state['fx'] if f['key']==e[0]);assert f['binding'][1]==e[4]['id'];selected.append((e,f))
  px,delay=[dict(key=f['key'],instance=f['instance']) for e,f in selected]
  async def valid():
   for e,f in selected:
    now=next(x for x in state['fx'] if x['key']==f['key']);assert now['instance']==f['instance'] and now['binding']==f['binding']
  async def param(f,n,v):
   await valid();await send('fx_param',**f,name=n,value=v)
  records=[];motion=None;started=False
  try:
   await send('play_all',action='settle');await asyncio.sleep(4)
   c=await asyncio.to_thread(get,'/composition/layers/2/clips/108');assert not c.get('video'),'scratch slot occupied'
   await asyncio.to_thread(post,'/composition/layers/2/clips/108/open','source:///video/Heart%20Capsule');started=True
   await send('launch',layer=2,col=108)
   for _ in range(60):
    await asyncio.sleep(.2);c=next((c for c in state['clips'] if c['layer']==2 and c['col']==108),None)
    if c:break
   assert c;a=dict(layer=2,col=108,instance=c['instance']);await send('home',**a,factory=True);await asyncio.sleep(4)
   for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==2))
   async def move():
    t=time.monotonic()
    while True:
     await send('manual',**a,slot='Turn',value=((time.monotonic()-t)/3)%1);await asyncio.sleep(.08)
   motion=asyncio.create_task(move())
   async def capture(label):
    await valid()
    for i in range(8):
     await asyncio.sleep(.5);await asyncio.to_thread(snap,f'{label}-{i}')
    cur=await asyncio.to_thread(get,'/composition');es={e[0]:e[4] for e in targets.effects(cur)}
    for e,f in selected:assert es[e[0]]['id']==e[4]['id']
    records.append(dict(label=label,effects={k:es[k] for k in [px['key'],delay['key']]}));(P/'results.json').write_text(json.dumps(records,indent=2));print(label,'captured',flush=True)
   await capture('baseline')
   await send('fx_direction',**px,value=1);await asyncio.sleep(1);await capture('melt-before-trigger')
   await param(px,'MELT_TRIGGER',True);await capture('melt-triggered')
   await send('fx_direction',**px,value=0);await asyncio.sleep(1)
   for n in ['R delay','G delay','B delay']:await param(delay,n,0)
   await send('fx_direction',**delay,value=1);await asyncio.sleep(2);await capture('rgb-zero')
   await param(delay,'G delay',.15);await param(delay,'B delay',.3);await capture('rgb-offset')
   await param(delay,'G delay',0);await param(delay,'B delay',0);await asyncio.sleep(2);await capture('rgb-cleared')
  finally:
   if motion:motion.cancel()
   await valid()
   for (e,f),a_fx in zip(selected,[px,delay]):
    await send('fx_amount',**a_fx,value=0)
    if a_fx==delay:
     for n in ['R delay','G delay','B delay']:await param(a_fx,n,e[4]['params'][n]['value'])
   if started:await send('launch',layer=2,col=1)
   await send('play_all',action='settle')
   for l in initial['layers']:await send('opacity',layer=l['i'],value=l['opacity'])
   await asyncio.sleep(4);(P/'after-heart.json').write_text(json.dumps(state));(P/'after-native.json').write_text(json.dumps(await asyncio.to_thread(get,'/composition')))
   reader.cancel()
asyncio.run(main())
