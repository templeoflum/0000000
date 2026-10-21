exec(open('sp/experiments/corpus-toys/live/audition.py').read().split('async def main():')[0])
async def main():
 comp=await asyncio.to_thread(get,'/composition');levels=[l['video']['opacity'] for l in comp['layers']];previous=next((i+1 for i,c in enumerate(comp['layers'][2]['clips']) if c.get('connected',{}).get('value')=='Connected'),None)
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  try:
   await send('launch',layer=3,col=14)
   for _ in range(60):
    await asyncio.sleep(.25);c=next((x for x in state['clips'] if x.get('layer')==3 and x.get('col')==14),None)
    if c:break
   a=dict(layer=3,col=14,instance=c['instance'])
   for i,p in enumerate(levels):await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",1. if i==2 else 0.)
   await send('home',**a,factory=True);await asyncio.sleep(6)
   for k,v in [('Ratio','1:1'),('Mult',16.),('Shape','rotate')]:await send('slot_cfg',**a,slot='Phase',key=k,value=v)
   await send('drive',**a,slot='Phase',on=True);await asyncio.sleep(4)
   samples=[]
   for i in range(3):
    samples.append((await asyncio.to_thread(get,'/composition/layers/3/clips/14'))['video']['sourceparams']);await asyncio.to_thread(snap,f'barber-moving-{i}');await asyncio.sleep(.21)
   P.joinpath('barber-moving.json').write_text(json.dumps(samples));print({k:[s[k]['value'] for s in samples] for k in ['Phase','Aperture','Contrast']})
  finally:
   if previous and previous!=14:await send('launch',layer=3,col=previous)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   task.cancel()
asyncio.run(main())
