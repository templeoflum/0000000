"""Isolated live Field checks; restore faders and previous Field clip in finally."""
import asyncio,json,pathlib,urllib.request
import websockets
P=pathlib.Path(__file__).resolve().parent/'pinna';P.mkdir(exist_ok=True);B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=12))
def put(p,v):urllib.request.urlopen(urllib.request.Request(B+p,json.dumps(v).encode(),{'Content-Type':'application/json'},method='PUT'),timeout=12).close()
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=12).read())
async def main():
 comp=await asyncio.to_thread(get,'/composition');P.joinpath('audition-before.json').write_text(json.dumps(comp))
 levels=[l['video']['opacity'] for l in comp['layers']]
 previous=next((i+1 for i,c in enumerate(comp['layers'][4]['clips']) if c.get('connected',{}).get('value')=='Connected'),None)
 results=[]
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  try:
   for i,p in enumerate(levels):await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",1. if i==4 else 0.)
   for col,name in [(76,'Heart Pinna Brelstaff Figure')]:
    await send('launch',layer=5,col=col);c=None
    for _ in range(60):
     await asyncio.sleep(.25);c=next((x for x in state['clips'] if x.get('layer')==5 and x.get('col')==col),None)
     if c and c.get('slots'):break
    assert c and c['slots'],f'Undiscovered: {name}'
    a=dict(layer=5,col=col,instance=c['instance']);delay=max(1.,c.get('morph',3.))+.75
    print(name,[s['name'] for s in c['slots']],flush=True)
    await send('home',**a,factory=True);await asyncio.sleep(delay)
    h=await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}');await asyncio.to_thread(snap,f'{col}-home')
    for value in [.25,.75]:
     await send('manual',**a,slot='Tilt',value=value);await asyncio.sleep(delay)
     await asyncio.to_thread(snap,f'{col}-phase-{value}')
    await send('open',**a);await asyncio.sleep(delay);samples=[]
    for _ in range(3):
     samples.append((await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}'))['video']['sourceparams']);await asyncio.sleep(.6)
    assert len({round(s['Tilt']['value'],5) for s in samples})>1,'Tilt not moving'
    await asyncio.to_thread(snap,f'{col}-open')
    await send('home',**a,factory=True);await asyncio.sleep(delay)
    final=await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}')
    current=next(x for x in state['clips'] if x.get('layer')==5 and x.get('col')==col)
    assert not any(s.get('drive') for s in current['slots']),'Home drives active'
    results.append(dict(name=name,col=col,home=h['video']['sourceparams'],samples=samples,final=final['video']['sourceparams']))
    P.joinpath('results.json').write_text(json.dumps(results));print('Controls and Home passed',name,flush=True)
  finally:
   if previous:await send('launch',layer=5,col=previous)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   await asyncio.sleep(.5);task.cancel()
asyncio.run(main())
