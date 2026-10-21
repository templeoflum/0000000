import asyncio,json,pathlib,urllib.request
import websockets
P=pathlib.Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  def active(li,col):return next((c for c in state['clips'] if c['layer']==li and c['col']==col and c.get('slots')),None)
  async def wait(li,col):
   for _ in range(100):
    await asyncio.sleep(.1);c=active(li,col)
    if c:return dict(layer=li,col=col,instance=c['instance'])
   raise RuntimeError('not ready')
  async def action(cmd,a,marker,**kw):
   old=list(state['events']);await send(cmd,**a,**kw)
   for _ in range(250):
    await asyncio.sleep(.1)
    if any(marker in e and e not in old for e in state['events']):break
   else:raise RuntimeError(cmd+' timeout')
   await asyncio.sleep(3.5)
  try:
   a=await wait(5,9);await action('home_set',a,': home set');await asyncio.to_thread(snap,'L5C9-home')
   await action('open',a,': → Open');await action('timing',a,': timing',mode='harmonic');await asyncio.to_thread(snap,'L5C9-shuffle');await action('home',a,': → Home · rest')
   for li,col in [(7,8),(8,1)]:
    for l in state['layers']:await send('opacity',layer=l['i'],value=1. if l['i']==li else 0.)
    await send('launch',layer=li,col=col);a=await wait(li,col);await action('home',a,': → Home · rest',factory=True);await asyncio.to_thread(snap,f'L{li}C{col}-isolated-home')
    P.joinpath(f'L{li}C{col}-isolated-state.json').write_text(json.dumps(state))
    if li==7:
     for n,v in [('Count',.2),('Duty',.25),('Soft',.15)]:await send('manual',**a,slot=n,value=v)
    else:
     for n,v in [('Amount',.5),('Size',.2),('Level',.5)]:await send('manual',**a,slot=n,value=v)
    await asyncio.sleep(2);await asyncio.to_thread(snap,f'L{li}C{col}-candidate')
   print('2D Home saved/tested; flat-output diagnostic captures ready',flush=True)
  finally:t.cancel()
asyncio.run(main())
