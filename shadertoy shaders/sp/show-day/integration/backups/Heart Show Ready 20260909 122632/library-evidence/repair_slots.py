"""Use installed working versions in two obsolete Soup slots; center old 2D SP."""
import asyncio,json,pathlib,urllib.request,urllib.parse
import websockets
P=pathlib.Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=15))
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
def source(col,old,new):
 path=f'/composition/layers/5/clips/{col}';c=get(path);P.joinpath(f'L5C{col}-before-replacement.json').write_text(json.dumps(c,indent=2))
 assert c['video']['description']==old,(col,c['video']['description'])
 urllib.request.urlopen(urllib.request.Request(B+path+'/open',('source:///video/'+urllib.parse.quote(new)).encode(),{'Content-Type':'text/plain'},method='POST'),timeout=15).close()
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv());P.joinpath('repair-before-state.json').write_text(json.dumps(state));results=[]
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  def active(col):return next((c for c in state['clips'] if c['layer']==5 and c['col']==col and c.get('slots')),None)
  async def ready(col):
   for _ in range(100):
    await asyncio.sleep(.1);c=active(col)
    if c:return c
   raise RuntimeError('No controller '+str(col))
  async def action(cmd,a,marker,**kw):
   old=list(state['events']);await send(cmd,**a,**kw)
   for _ in range(250):
    await asyncio.sleep(.1)
    if any(marker in e and e not in old for e in state['events']):break
   else:raise RuntimeError('No completion '+cmd)
   await asyncio.sleep(3.5)
  try:
   for l in state['layers']:await send('opacity',layer=l['i'],value=1. if l['i']==5 else 0.)
   for col,old,new in [(28,'HypnoWorm','Heart HypnoWorm'),(40,'Torus thingy','Heart Torus')]:
    await asyncio.to_thread(source,col,old,new);await send('launch',layer=5,col=col);c=await ready(col);a=dict(layer=5,col=col,instance=c['instance'])
    await action('home',a,': → Home · rest',factory=True);await asyncio.to_thread(snap,f'L5C{col}-home')
    await action('open',a,': → Open');await action('timing',a,': timing',mode='harmonic');await asyncio.to_thread(snap,f'L5C{col}-shuffle')
    driven=[s['name'] for s in active(col)['slots'] if s['drive']];assert driven
    await action('home',a,': → Home · rest',factory=True);assert not any(s['drive'] for s in active(col)['slots'])
    results.append(dict(layer=5,col=col,old_source=old,source=new,status='replaced with already-installed working Heart version',driven=driven,home_recovered=True));P.joinpath('repairs.json').write_text(json.dumps(results,indent=2))
   await send('launch',layer=5,col=9);c=await ready(9);a=dict(layer=5,col=9,instance=c['instance']);await action('home',a,': → Home · rest',factory=True)
   for name in ['X','Y']:await send('manual',**a,slot=name,value=.5)
   await send('manual',**a,slot='Spin',value=0.);await asyncio.sleep(1.5);await asyncio.to_thread(snap,'L5C9-centered-candidate')
   P.joinpath('center-candidate.json').write_text(json.dumps(dict(target=a,values={s['name']:s['v'] for s in active(9)['slots']}),indent=2));print('Replacements exercised; 2D center candidate ready for visual review',flush=True)
  finally:task.cancel()
asyncio.run(main())
