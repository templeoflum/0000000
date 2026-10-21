"""User-authorized pilot switching; restore freshly saved scene in finally."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
OUT=Path(__file__).parent/'fluid-warp';OUT.mkdir(exist_ok=True)
NAME='Before pilot refinement '+time.strftime('%Y%m%d-%H%M%S')
async def main():
 async with websockets.connect('ws://127.0.0.1:8766',max_size=8_000_000) as ws:
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  async def wait(pred,timeout=70):
   end=time.monotonic()+timeout
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(ws.recv(),8))
    if pred(s):return s
   raise RuntimeError('Timeout '+str(s.get('patch_operation')))
  async def op(cmd,name):
   await send(cmd,name=name)
   await wait(lambda s:s.get('patch_operation',{}).get('active'))
   s=await wait(lambda s:not s.get('patch_operation',{}).get('active') and (s.get('patch_status')=='Ready' or s.get('patch_status','').startswith('Failed:')))
   if s.get('patch_status')!='Ready':raise RuntimeError(str(s.get('patch_operation')))
   print(cmd,name,'Ready',flush=True);return s
  before=await wait(lambda s:s.get('arena_connected'))
  (OUT/'before.json').write_text(json.dumps(before,indent=2))
  await op('patch_save',NAME)
  (OUT/'recovery-name.txt').write_text(NAME)
  result={'recovery':NAME,'pilots':[]}
  try:
   s=await op('patch_recall','Figure depth')
   for fx in s['fx']:
    if fx.get('has_amount') and fx['name'] not in ['SP Study Level','Linear Cloner']:
     await send('fx_amount',key=fx['key'],instance=fx['instance'],value=0)
   # Rest shaping and feedback before deliberately enabling a small relationship set.
   for layer in (1,2):await send('home',layer=layer,col=1,factory=True)
   await send('opacity',layer=1,value=.35)
   await send('opacity',layer=2,value=1)
   await send('opacity',layer=5,value=.65)
   for col,names in [(3,['Tumble','Morph','Hue']),(5,['Turn','Spin','Hue']),(16,['rot angle','mx','my'])]:
    await send('launch',layer=5,col=col)
    s=await wait(lambda s:any(c['layer']==5 and c['col']==col for c in s['clips']))
    # Clip activation can replace the first discovered controller instance.
    settle=time.monotonic()+2
    while time.monotonic()<settle:
     s=json.loads(await asyncio.wait_for(ws.recv(),8))
    c=next(c for c in s['clips'] if c['layer']==5 and c['col']==col)
    target=dict(layer=5,col=col,instance=c['instance'])
    await send('home',**target,factory=True)
    await send('hold',on=False)
    await send('morph',**target,seconds=.5)
    wanted=names or [sl['name'] for sl in c['slots'] if sl.get('name') in ['Zoom','Rotation','Rotate','Hue','Shape','Speed']][:3]
    if not wanted:wanted=[sl['name'] for sl in c['slots'] if sl['name'] not in ['Size','X','Y']][:2]
    await send('speed',**target,value=1)
    for name in wanted:await send('drive',**target,slot=name,on=True)
    # Source choices and density stay still; animate depth, rotation and spacing.
    fx=next(e for e in s['fx'] if e['name']=='Linear Cloner' and e['layer']==5)
    et=dict(effect=fx['key'],instance=fx['instance'])
    await send('home',**et)
    for name,value in [('Clones',9),('Tails',2),('Start Scale',100),('End Scale',18),('Distribution',65),('Distortion',0),('Tail Rotation',0),('Tail Length',-.18),('Start Rotation',0),('End Rotation',35),('Master Rotation',0)]:
     await send('fx_param',key=fx['key'],instance=fx['instance'],name=name,value=value)
    await send('morph',**et,seconds=.5)
    await send('speed',**et,value=1)
    for name,lo,hi,ratio,offset in [('End Scale',.12,.38,'1:1',0),('Tail Length',.22,.48,'1:1',.25),('Master Rotation',.32,.68,'1:1',.5),('End Rotation',.04,.32,'2:3',.75)]:
     for key,value in [('Lo',lo),('Hi',hi),('Ratio',ratio),('Offset',offset),('Shape',1),('Mult',1)]:await send('slot_cfg',**et,slot=name,key=key,value=value)
     await send('drive',**et,slot=name,on=True)
    await send('fx_amount',key=fx['key'],instance=fx['instance'],value=1)
    for name in ['Zoom','Rotate']:await send('drive',layer=1,col=1,slot=name,on=True)
    samples=[];end=time.monotonic()+10
    while time.monotonic()<end:
     s=json.loads(await asyncio.wait_for(ws.recv(),8));c=next((c for c in s['clips'] if c['layer']==5 and c['col']==col),None)
     if c:samples.append({'time':time.monotonic(),'queue':s['queue'],'effect':{sl['name']:sl['v'] for e in s['fx'] if e['name']=='Linear Cloner' and e.get('motion') for sl in e['motion']['slots'] if sl['drive']},'values':{sl['name']:sl['v'] for sl in c['slots'] if sl['name'] in wanted}})
    (OUT/f'samples-{col}.json').write_text(json.dumps(samples))
    ranges={n:[min(x['values'][n] for x in samples),max(x['values'][n] for x in samples)] for n in wanted}
    result['pilots'].append({'col':col,'name':c['name'],'ranges':ranges,'max_queue':max(x['queue'] for x in samples)})
    (OUT/f'pilot-{col}.json').write_text(json.dumps(s,indent=2))
    img=await asyncio.to_thread(lambda:urllib.request.urlopen('http://127.0.0.1:8080/api/v1/composition/monitors/1/snapshot.png',timeout=5).read())
    (OUT/f'pilot-{col}.png').write_bytes(img)
    await op('patch_save',{3:'Fluid warp - 3D',5:'Fluid warp - Shell',16:'Fluid warp - Seed'}[col])
    print('Pilot',c['name'],ranges,flush=True)
  finally:
   restored=await op('patch_recall',NAME)
   (OUT/'restored.json').write_text(json.dumps(restored,indent=2))
   result['restored']=True
   (OUT/'result.json').write_text(json.dumps(result,indent=2))
asyncio.run(main())
