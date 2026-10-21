import asyncio,json,time,urllib.request,sys
from pathlib import Path
import websockets
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'engine'));import targets
P=Path(__file__).parent/'lower-layers';P.mkdir(exist_ok=True);B='http://localhost:8080/api/v1'
def get(path='/composition'):return json.load(urllib.request.urlopen(B+path,timeout=6))
def put(pid,v):urllib.request.urlopen(urllib.request.Request(B+'/parameter/by-id/'+str(pid),data=json.dumps({'value':v}).encode(),headers={'Content-Type':'application/json'},method='PUT'),timeout=6).read()
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as ws:
  latest=json.loads(await ws.recv())
  async def consume():
   nonlocal latest
   async for m in ws:latest=json.loads(m)
  reader=asyncio.create_task(consume())
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  before=json.loads(json.dumps(latest));comp=get();native={e['id']:e for e in comp['video']['effects']};fxs=[f for f in before['fx'] if f['scope']=='L' and f['layer'] in (1,2)];muted=fxs+[f for f in before['fx'] if f['scope']=='C']
  P.joinpath('before-heart.json').write_text(json.dumps(before,indent=2));P.joinpath('before-composition.json').write_text(json.dumps(comp,indent=2));results=[]
  async def snapshot(label):
   data=await asyncio.to_thread(lambda:urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=6).read());P.joinpath(label+'.png').write_bytes(data)
  try:
   await send('hold',on=True)
   for f in muted:await send('fx_amount',key=f['key'],instance=f['instance'],value=0)
   await asyncio.sleep(2)
   for i,f in enumerate(fxs):
    await snapshot(f'{i}-before')
    await send('fx_press',key=f['key'],instance=f['instance']);await send('fx_release',key=f['key'],instance=f['instance'])
    await asyncio.sleep(1)
    samples=[]
    for n in range(3):
     await snapshot(f'{i}-on-{n}')
     c=await asyncio.to_thread(get);e=next(e for key,_,_,_,e in targets.effects(c) if key==f['key']);h=next(x for x in latest['fx'] if x['key']==f['key'])
     samples.append({'bypass':e['bypassed']['value'],'amount':e['params']['Opacity']['value'],'heart':{k:h.get(k) for k in ('env','target','observed_amount','observed_bypassed')},'params':e['params']});await asyncio.sleep(.3)
    await send('fx_amount',key=f['key'],instance=f['instance'],value=0);await asyncio.sleep(1.3);await snapshot(f'{i}-off')
    results.append({'index':i,'name':f['name'],'key':f['key'],'samples':samples});P.joinpath('results.json').write_text(json.dumps(results,indent=2));print(f['name'],[(s['bypass'],round(s['amount'],3)) for s in samples],flush=True)
  finally:
   for f in muted:await send('fx_amount',key=f['key'],instance=f['instance'],value=f['target'])
   await asyncio.sleep(1.5)
   for e in comp['video']['effects']+comp['layers'][0]['video']['effects']+comp['layers'][1]['video']['effects']:
    if e['name']=='Transform':continue
    for p in (e['params']['Opacity'],e['bypassed']):await asyncio.to_thread(put,p['id'],p['value'])
   await send('hold',on=before['hold']);await asyncio.sleep(.5)
   P.joinpath('after-heart.json').write_text(json.dumps(latest,indent=2));P.joinpath('after-composition.json').write_text(json.dumps(await asyncio.to_thread(get),indent=2));reader.cancel();print('Restored original composition effect state and hold',flush=True)
asyncio.run(main())
