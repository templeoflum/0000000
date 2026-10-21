import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path('sp/audit/figure-transform-pilot');B='http://localhost:8080/api/v1'
def req(path):return json.load(urllib.request.urlopen(B+path,timeout=6))
def snapshot(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=6).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv())
  async def drain():
   async for _ in w:pass
  task=asyncio.create_task(drain())
  async def send(cmd,**args):await w.send(json.dumps(dict(cmd=cmd,**args)))
  fx={f['key']:f for f in s['fx']};transform=fx['layer/figure~1/effect/Transform~1'];source=next(c for c in s['clips'] if c['layer']==5)
  await send('hold',on=True)
  for l in s['layers']:await send('opacity',layer=l['i'],value=1 if l['i']==5 else 0)
  for f in s['fx']:
   if f.get('has_amount') and (f['scope']=='C' or f['layer']==5):
    await send('fx_cfg',key=f['key'],instance=f['instance'],cfg={'attack':.15,'release':.15});await send('fx_amount',key=f['key'],instance=f['instance'],value=0)
  await send('home',layer=5,col=source['col'],instance=source['instance']);await asyncio.sleep(5)
  async def settransform(**params):
   for name,value in params.items():await send('fx_param',key=transform['key'],instance=transform['instance'],name=name,value=value)
   await asyncio.sleep(1.2)
  await settransform(**{'Position X':0,'Position Y':0,'Scale':100,'Scale W':100,'Scale H':100,'Rotation X':0,'Rotation Y':0,'Rotation Z':0,'Anchor X':0,'Anchor Y':0,'Anchor Z':0});await asyncio.to_thread(snapshot,'live-source')
  before=req(f"/composition/layers/5/clips/{source['col']}")['video']['sourceparams']
  await settransform(**{'Position X':192,'Position Y':108,'Scale':75,'Rotation Z':20});await asyncio.to_thread(snapshot,'live-transformed')
  after=req(f"/composition/layers/5/clips/{source['col']}")['video']['sourceparams'];P.joinpath('source-comparison.json').write_text(json.dumps({'before':before,'after':after},indent=2));assert before==after,'Source changed during Transform test'
  f=fx['layer/figure~1/effect/LinearCloner~1'];await send('fx_amount',key=f['key'],instance=f['instance'],value=.65);await asyncio.sleep(1.2);await asyncio.to_thread(snapshot,'live-cloned')
  await settransform(**{'Position X':0,'Position Y':0,'Scale':100,'Rotation Z':0})
  for slot in ('Tumble','Morph','Hue'):await send('drive',layer=5,col=source['col'],instance=source['instance'],slot=slot,on=True)
  await send('hold',on=False);await asyncio.sleep(.5);P.joinpath('live-verification.json').write_text(json.dumps({'source_parameters_unchanged_by_transform':before==after,'transform_first':req('/composition')['layers'][4]['video']['effects'][0]['name']=='Transform','figure_slot':source['col'],'demo':'Figure source + shared Transform + Linear Cloner 65%; Tumble Morph Hue driven'},indent=2));task.cancel();print('Source -> Transform -> Linear Cloner verified; pilot left running')
asyncio.run(main())
