"""User-authorized pilot switching; restore freshly saved scene in finally."""
import asyncio,json,time
from pathlib import Path
import websockets
OUT=Path(__file__).parent
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
   await wait(lambda s:s.get('patch_operation',{}).get('active') or s.get('patch_status')=='Ready')
   s=await wait(lambda s:not s.get('patch_operation',{}).get('active') and (s.get('patch_status')=='Ready' or s.get('patch_status','').startswith('Failed:')))
   if s.get('patch_status')!='Ready':raise RuntimeError(str(s.get('patch_operation')))
   print(cmd,name,'Ready',flush=True);return s
  before=await wait(lambda s:s.get('arena_connected'))
  (OUT/'before.json').write_text(json.dumps(before,indent=2))
  await op('patch_save',NAME)
  (OUT/'recovery-name.txt').write_text(NAME)
  result={'recovery':NAME,'pilots':[]}
  try:
   await op('patch_recall','Figure depth')
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
    for name in wanted:await send('drive',**target,slot=name,on=True)
    samples=[];end=time.monotonic()+12
    while time.monotonic()<end:
     s=json.loads(await asyncio.wait_for(ws.recv(),8));c=next((c for c in s['clips'] if c['layer']==5 and c['col']==col),None)
     if c:samples.append({'queue':s['queue'],'values':{sl['name']:sl['v'] for sl in c['slots'] if sl['name'] in wanted}})
    ranges={n:[min(x['values'][n] for x in samples),max(x['values'][n] for x in samples)] for n in wanted}
    result['pilots'].append({'col':col,'name':c['name'],'ranges':ranges,'max_queue':max(x['queue'] for x in samples)})
    (OUT/f'pilot-{col}.json').write_text(json.dumps(s,indent=2))
    print('Pilot',c['name'],ranges,flush=True)
  finally:
   restored=await op('patch_recall',NAME)
   (OUT/'restored.json').write_text(json.dumps(restored,indent=2))
   result['restored']=True
   (OUT/'result.json').write_text(json.dumps(result,indent=2))
asyncio.run(main())
