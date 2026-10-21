"""Bounded live pilot; preserves clip parameters, active clips, solo/faders and Heart setup."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).parent;BASE='http://127.0.0.1:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(BASE+path,timeout=8))
def put(pid,v):
 req=urllib.request.Request(BASE+'/parameter/by-id/'+str(pid),data=json.dumps({'value':v}).encode(),headers={'Content-Type':'application/json'},method='PUT');urllib.request.urlopen(req,timeout=8).read()
async def main():
 async with websockets.connect('ws://127.0.0.1:8766',max_size=10000000) as ws:
  latest={}
  async def consume():
   nonlocal latest
   async for m in ws:latest=json.loads(m)
  task=asyncio.create_task(consume())
  async def send(cmd,**args):await ws.send(json.dumps(dict(cmd=cmd,**args)))
  async def wait(pred,limit=20):
   end=time.monotonic()+limit
   while time.monotonic()<end:
    if pred(latest):return
    await asyncio.sleep(.1)
   raise RuntimeError('Timeout awaiting Heart')
  await wait(lambda s:s.get('arena_connected'))
  before=json.loads(json.dumps(latest));comp=await asyncio.to_thread(get,'/composition')
  (P/'before-heart.json').write_text(json.dumps(before,indent=2));(P/'before-composition.json').write_text(json.dumps(comp,indent=2))
  recovery='Before live inventory '+time.strftime('%H%M%S');(P/'recovery-name.txt').write_text(recovery)
  await send('performance_save',name=recovery);await wait(lambda s:recovery in s.get('performance_presets',[]))
  changed=[];results=[];touched=set()
  try:
   await send('hold',on=True)
   for f in before['fx']:await send('fx_amount',key=f['key'],value=0,instance=f['instance'])
   await asyncio.sleep(4)
   for layer,col,names in [(6,40,['rate','radius','roto']),(5,39,['Speed','Zoom','Wave Count']),(5,65,['speed','offset','columns'])]:
    touched.add(layer)
    for i,l in enumerate(comp['layers'],1):await asyncio.to_thread(put,l['solo']['id'],i==layer)
    await send('opacity',layer=layer,value=1)
    await send('launch',layer=layer,col=col);await asyncio.sleep(2)
    cj=await asyncio.to_thread(get,f'/composition/layers/{layer}/clips/{col}');params=cj['video'].get('sourceparams') or {}
    item={'address':f'L{layer}C{col}','name':cj['name']['value'],'source':cj['video']['description'],'source_parameters':params,'clip_effects':cj['video'].get('effects',[]),'samples':[]};results.append(item)
    async def sample(label,n=5):
     for k in range(n):
      await asyncio.sleep(.5)
      filename=f'L{layer}C{col}-{label}-{k}.png'
      data=await asyncio.to_thread(lambda:urllib.request.urlopen(BASE+'/composition/monitors/1/snapshot.png',timeout=8).read());(P/filename).write_bytes(data)
      telemetry=json.loads(Path('sp/monitor/telemetry.json').read_text())
      item['samples'].append({'phase':label,'frame':filename,'time':time.time(),'fps':telemetry.get('fps'),'gpu':telemetry.get('gpu'),'telemetry_age':time.time()-telemetry.get('timestamp',0),'queue':latest.get('queue')})
    await sample('baseline')
    for name in names:
     p=params.get(name)
     if not p or p.get('valuetype') not in ('ParamRange','ParamInt','ParamNumber'):continue
     changed.append((p['id'],p['value']))
     for fraction,label in ((.25,'quarter'),(.75,'threequarters')):
      value=p['min']+(p['max']-p['min'])*fraction
      if p['valuetype'] in ('ParamInt','ParamNumber') or p.get('view',{}).get('display_units')=='integer':value=round(value)
      await asyncio.to_thread(put,p['id'],value);await sample(name.replace(' ','_')+'-'+label,3)
     await asyncio.to_thread(put,p['id'],p['value']);changed.pop()
    print(item['address'],item['name'],len(item['samples']),'live frames',flush=True)
    (P/'evidence.json').write_text(json.dumps(results,indent=2))
  finally:
   for pid,value in changed:await asyncio.to_thread(put,pid,value)
   for layer in touched:
    l=next(l for l in before['layers'] if l['i']==layer)
    if l.get('ccol'):await send('launch',layer=layer,col=l['ccol'])
    else:await send('clear',layer=layer)
   await asyncio.sleep(3)
   for l in before['layers']:await send('opacity',layer=l['i'],value=l['opacity'])
   for l in comp['layers']:await asyncio.to_thread(put,l['solo']['id'],l['solo']['value'])
   await send('performance_load',name=recovery,seconds=1);await asyncio.sleep(3)
   await send('hold',on=before.get('hold',False));await asyncio.sleep(.3)
   (P/'after-heart.json').write_text(json.dumps(latest,indent=2));(P/'after-composition.json').write_text(json.dumps(await asyncio.to_thread(get,'/composition'),indent=2))
   (P/'evidence.json').write_text(json.dumps(results,indent=2));print('Restoration attempted; readback saved',flush=True);task.cancel()
asyncio.run(main())
