import asyncio,json,pathlib,urllib.request
import websockets
P=pathlib.Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=6))
def put(path,value):urllib.request.urlopen(urllib.request.Request(B+path,json.dumps(value).encode(),{'Content-Type':'application/json'},method='PUT'),timeout=6).close()
def snapshot(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=8).read())
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
   for recipe in json.loads(P.joinpath('recipes.json').read_text()):
    col=recipe['col'];await send('launch',layer=3,col=col)
    for _ in range(50):
     await asyncio.sleep(.2);c=next((x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col),None)
     if c and c.get('slots'):break
    assert c and c.get('slots'),recipe['source']+' not discovered'
    a=dict(layer=3,col=col,instance=c['instance']);delay=max(1,c.get('morph',3))+.8
    await send('home',**a,factory=True);await asyncio.sleep(delay)
    home=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams']
    errors={n:(v,home[n]['value']) for n,v in recipe['home'].items() if abs(v-home[n]['value'])>max(.001,(home[n]['max']-home[n]['min'])*.002)}
    assert not errors,('Home',recipe['source'],errors)
    await asyncio.to_thread(snapshot,f'{col}-home')
    await send('open',**a);await asyncio.sleep(delay);samples=[]
    for _ in range(3):
     native=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams'];samples.append({n:native[n]['value'] for n in recipe['drives']});await asyncio.sleep(.6)
    for n,(lo,hi) in recipe['drives'].items():
     vals=[s[n] for s in samples];assert max(vals)-min(vals)>1e-5,('No motion',n,vals);assert all(lo-.001<=v<=hi+.001 for v in vals),('Range',n,vals)
    await asyncio.to_thread(snapshot,f'{col}-open')
    await send('home',**a,factory=True);await asyncio.sleep(delay)
    c=next(x for x in state['clips'] if x.get('layer')==3 and x.get('col')==col);assert not any(s['drive'] for s in c['slots']),('Drive still on',col)
    final=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams']
    assert all(abs(v-final[n]['value'])<=max(.001,(final[n]['max']-final[n]['min'])*.002) for n,v in recipe['home'].items()),('Home recovery',col)
    results.append(dict(source=recipe['source'],col=col,home=True,open=samples,recovered=True));P.joinpath('live-results.json').write_text(json.dumps(results,indent=2));print('PASS',recipe['source'],flush=True)
  finally:
   if previous:await send('launch',layer=3,col=previous)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   t.cancel()
asyncio.run(main())
