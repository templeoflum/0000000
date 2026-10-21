exec(open('sp/experiments/corpus-toys/live/audition.py').read().split('async def main():')[0])
async def main():
 comp=await asyncio.to_thread(get,'/composition');levels=[l['video']['opacity'] for l in comp['layers']];old=next((i+1 for i,c in enumerate(comp['layers'][4]['clips']) if c.get('connected',{}).get('value')=='Connected'),None)
 async with websockets.connect('ws://localhost:8766',max_size=20000000) as w:
  s=json.loads(await w.recv())
  async def drain():
   nonlocal s
   async for m in w:s=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  f=next(x for x in s['fx'] if x['key']=='layer/figure~1/effect/Transform~1');a=dict(effect=f['key'],instance=f['instance']);sl=next(x for x in f['motion']['slots'] if x['name']=='Scale');saved=dict(sl)
  try:
   await send('launch',layer=5,col=76);await asyncio.sleep(2)
   c=next(x for x in s['clips'] if x.get('layer')==5 and x.get('col')==76);await send('home',layer=5,col=76,instance=c['instance'],factory=True)
   for i,p in enumerate(levels):await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",1. if i==4 else 0.)
   span=sl['max']-sl['min']
   for k,v in [('Lo',(85-sl['min'])/span),('Hi',(100-sl['min'])/span),('Ratio','1:1'),('Mult',4),('Shape','sway')]:await send('slot_cfg',**a,slot='Scale',key=k,value=v)
   await send('drive',**a,slot='Scale',on=True);await asyncio.sleep(4)
   vals=[]
   for i in range(3):
    vals.append(next(x for x in s['fx'] if x['key']==f['key'])['motion']);await asyncio.to_thread(snap,f'pinna-breathe-{i}');await asyncio.sleep(.45)
   P.joinpath('pinna-breathe.json').write_text(json.dumps(vals));print('Pinna native Scale motion captured')
  finally:
   await send('drive',**a,slot='Scale',on=False)
   for k,key in [('Lo','lo'),('Hi','hi'),('Ratio','ratio'),('Mult','mult'),('Shape','shape')]:await send('slot_cfg',**a,slot='Scale',key=k,value=('sway' if saved[key] else 'loop') if k=='Shape' else saved[key])
   await send('manual',**a,slot='Scale',value=saved['v']);await send('drive',**a,slot='Scale',on=saved['drive'])
   if old:await send('launch',layer=5,col=old)
   for p in levels:await asyncio.to_thread(put,f"/parameter/by-id/{p['id']}",p['value'])
   t.cancel()
asyncio.run(main())
