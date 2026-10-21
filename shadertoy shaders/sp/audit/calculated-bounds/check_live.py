import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).parent;B='http://localhost:8080/api/v1'
def get(path='/composition'):return json.load(urllib.request.urlopen(B+path,timeout=7))
def put(pid,v):return urllib.request.urlopen(urllib.request.Request(B+'/parameter/by-id/'+str(pid),data=json.dumps({'value':v}).encode(),method='PUT',headers={'Content-Type':'application/json'}),timeout=7).read()
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=7).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as ws:
  latest=json.loads(await ws.recv());P.joinpath('before-heart.json').write_text(json.dumps(latest,indent=2));comp=get();P.joinpath('before-native.json').write_text(json.dumps(comp,indent=2))
  async def consume():
   nonlocal latest
   async for msg in ws:latest=json.loads(msg)
  task=asyncio.create_task(consume());records=[];T='layer/figure~1/effect/Transform~1';L='layer/figure~1/effect/LinearCloner~1'
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  def fx(key):return next(x for x in latest['fx'] if x['key']==key)
  async def par(key,vals):
   for name,value in vals.items():await send('fx_param',key=key,instance=fx(key)['instance'],name=name,value=value)
  async def amount(key,v):await send('fx_amount',key=key,instance=fx(key)['instance'],value=v)
  async def record(label):
   await asyncio.sleep(1);await asyncio.to_thread(snap,label);c=get();p={e['name']:e for e in c['layers'][4]['video']['effects']};records.append({'label':label,'frame':[c['video']['width']['value'],c['video']['height']['value']],'transform':{n:x['value'] for n,x in c['layers'][4]['video']['effects'][0]['params'].items()},'cloner':{n:x['value'] for n,x in p['LinearCloner']['params'].items()},'guards':[fx(k)['motion'].get('guard') for k in (T,L)]});P.joinpath('results.json').write_text(json.dumps(records,indent=2));print(label,records[-1]['guards'],flush=True)
  try:
   await send('hold',on=True)
   for l in latest['layers']:await send('opacity',layer=l['i'],value=1 if l['i']==5 else 0)
   for f in latest['fx']:
    if f['has_amount'] and (f['scope']=='C' or f['layer']==5):await amount(f['key'],1 if f['key']==T else 0)
   await par(T,{'Scale':100,'Position X':0,'Position Y':0});await par(L,{'Clones':1,'Center':0,'Start Scale':100,'Tail Length':1,'Master Rotation':0,'Delay Enabled':False,'Reverse':False});await asyncio.sleep(2)
   for w,h in [(1920,1080),(1080,1920),(1024,1024)]:
    for _ in range(2):
     for obj in (comp['video'],comp['layers'][4]['clips'][6]['video']):
      await asyncio.to_thread(put,obj['height']['id'],h);await asyncio.to_thread(put,obj['width']['id'],w)
    await asyncio.sleep(4)
    await amount(L,0);await par(T,{'Scale':1000,'Scale W':1000,'Scale H':1000,'Position X':16384,'Position Y':-16384,'Rotation X':90,'Rotation Y':90,'Rotation Z':70,'Anchor X':8192})
    await record(f'{w}-{h}-extreme-transform')
    await par(T,{'Scale':60,'Scale W':100,'Scale H':100,'Position X':200,'Position Y':100,'Rotation Z':40});await amount(L,1)
    await par(L,{'Center':1,'Master Rotation':90,'Start Scale':100,'Distortion':100,'Delay Amount':1});await record(f'{w}-{h}-anchor')
    for k in (T,L):await send('open',effect=k,instance=fx(k)['instance']);await send('speed',effect=k,instance=fx(k)['instance'],value=2)
    await send('hold',on=False)
    for i in range(3):await asyncio.sleep(.7);await record(f'{w}-{h}-open-{i}')
    for k in (T,L):await send('fire',effect=k,instance=fx(k)['instance'])
    await record(f'{w}-{h}-shuffle');await send('hold',on=True)
   await par(L,{'Clones':7,'Center':0,'Tail Length':1});await record('tail-allowed-outside')
  finally:
   for _ in range(2):
    for obj in (comp['video'],comp['layers'][4]['clips'][6]['video']):
     await asyncio.to_thread(put,obj['height']['id'],1080);await asyncio.to_thread(put,obj['width']['id'],1920)
   await asyncio.sleep(3);await par(T,{'Scale':70,'Scale W':100,'Scale H':100,'Position X':0,'Position Y':0,'Rotation Z':0});await par(L,{'Clones':7,'Center':0,'Tail Length':.5,'Start Scale':80,'End Scale':45,'Master Rotation':0});await send('hold',on=False);task.cancel()
asyncio.run(main())
