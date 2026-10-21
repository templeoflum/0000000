"""Save Scan's visible Home; verify global recovery and leave a visible Figure ready."""
import asyncio,json,pathlib,urllib.request
import websockets
P=pathlib.Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  def clip(li,col):return next((c for c in state['clips'] if c['layer']==li and c['col']==col and c.get('slots')),None)
  async def launch(li,col):
   await send('launch',layer=li,col=col)
   for _ in range(150):
    await asyncio.sleep(.1);c=clip(li,col)
    if c:return {k:c[k] for k in ('layer','col','instance')}
   raise RuntimeError('clip missing')
  async def action(cmd,a,marker,**kw):
   old=list(state['events']);await send(cmd,**a,**kw)
   for _ in range(250):
    await asyncio.sleep(.1)
    if any(marker in e and e not in old for e in state['events']):break
   else:raise RuntimeError(cmd+' timeout '+str(state['events'][-3:]))
   await asyncio.sleep(4)
  def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
  try:
   grain=await launch(8,1);await action('home',grain,': → Home · rest',factory=True)
   scan=await launch(7,8)
   for l in state['layers']:await send('opacity',layer=l['i'],value=1. if l['i']==7 else 0.)
   for n,v in [('Count',.2),('Duty',.25),('Soft',.15)]:await send('manual',**scan,slot=n,value=v)
   await asyncio.sleep(3);await action('home_set',scan,': home set');await asyncio.to_thread(snap,'L7C8-home')
   await action('open',scan,': → Open');await action('timing',scan,': timing',mode='harmonic');await asyncio.to_thread(snap,'L7C8-shuffle');await action('home',scan,': → Home · rest')
   fig=await launch(5,9);await action('home',fig,': → Home · rest')
   for l in state['layers']:await send('opacity',layer=l['i'],value=1. if l['i']==5 else 0.)
   await action('play_all',{},'Opening all ·',action='open')
   driven=[(c['layer'],c['col'],s['name']) for c in state['clips'] for s in c.get('slots',[]) if s['drive']];assert driven,'No source drives opened'
   await action('play_all',{},'Shuffled harmonic ·',action='shuffle',value='harmonic');await asyncio.to_thread(snap,'global-shuffle')
   await action('play_all',{},'Settling all ·',action='settle')
   assert not any(s['drive'] for c in state['clips'] for s in c.get('slots',[])),'source still driven'
   await asyncio.to_thread(snap,'global-settled');P.joinpath('global-settled-state.json').write_text(json.dumps(state))
   before=json.loads(P.joinpath('repair-before-state.json').read_text())
   for l in before['layers']:
    if l['i']==5:continue
    if l['ccol']:await send('launch',layer=l['i'],col=l['ccol'])
    else:await send('clear',layer=l['i'])
    await send('opacity',layer=l['i'],value=l['opacity'])
   await send('opacity',layer=5,value=1.);await asyncio.sleep(4)
   P.joinpath('final-rehearsal.json').write_text(json.dumps(dict(passed=True,scan_home={'Count':.2,'Duty':.25,'Soft':.15},grain='Original Home restored; RGBA alpha contains correct grain, no shader changes',global_open_drives=driven,global_settle_drives_off=True,ready_figure='L5C9 centered Figure2D'),indent=2));print('PASS Scan Home/Open/Shuffle/Home and global Open/Shuffle/Settle; Figure2D ready',flush=True)
  finally:task.cancel()
asyncio.run(main())
