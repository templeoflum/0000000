import asyncio,json,urllib.request,time
from pathlib import Path
import websockets,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"shader-progress"))
from update import publish
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=15))
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv());(P/'heart-before.json').write_text(json.dumps(state))
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('hold',on=True)
  for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==5))
  for f in state['fx']:
   if f.get('has_amount') and (f['scope']=='C' or f.get('layer')==5):
    await send('fx_cfg',key=f['key'],instance=f['instance'],cfg={'attack':.05,'release':.05});await send('fx_amount',key=f['key'],instance=f['instance'],value=0)
  results=[]
  for col,probe in [(20,'thickness'),(25,'Refraction'),(38,'Spike Sharpness')]:
   publish(f'Figure L5C{col}: checking native controls and rendered frame boundaries.',record={'id':f'D1 L5C{col}','status':'Checking','note':'Live checks running; no containment decision yet.'})
   clip=None
   await send('launch',layer=5,col=col)
   for _ in range(30):
    await asyncio.sleep(.3)
    clip=next((c for c in state.get('clips',[]) if c['layer']==5 and c['col']==col),None)
    if clip:break
   if not clip:raise RuntimeError('No discovered clip '+str(col))
   addr=dict(layer=5,col=col,instance=clip['instance']);native=await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}');params=native['video']['sourceparams'];numeric={k:p for k,p in params.items() if p.get('valuetype')=='ParamRange'}
   for name,p in numeric.items():
    await send('drive',**addr,slot=name,on=False)
   await asyncio.sleep(.6)
   (P/f'{col}-before.json').write_text(json.dumps(native,indent=2))
   await asyncio.to_thread(snap,f'{col}-baseline')
   row={'col':col,'source':native['video']['description'],'expected_controls':list(numeric),'discovered_controls':[s['name'] for s in clip['slots']],'checks':[]}
   for name,p in numeric.items():
    original=(p['value']-p['min'])/(p['max']-p['min'])
    await send('drive',**addr,slot=name,on=False)
    for value in [.25,.75]:
     await send('manual',**addr,slot=name,value=value);await asyncio.sleep(.3)
     observed=await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}")
     for retry in range(12):
      want=p['min']+(p['max']-p['min'])*value
      if abs(observed['value']-want)<max(.001,abs(p['max']-p['min'])*.01):break
      await asyncio.sleep(.15);observed=await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}")
     want=p['min']+(p['max']-p['min'])*value;actual=observed['value']
     row['checks'].append({'control':name,'requested':want,'observed':actual,'ok':abs(actual-want)<max(.001,abs(p['max']-p['min'])*.01)})
     await asyncio.to_thread(snap,f'{col}-{name}-{value}')
    await send('manual',**addr,slot=name,value=original)
   await send('slot_cfg',**addr,slot=probe,key='Ratio',value='1:1');await send('slot_cfg',**addr,slot=probe,key='Lo',value=.25);await send('slot_cfg',**addr,slot=probe,key='Hi',value=.75)
   await send('drive',**addr,slot=probe,on=True);await send('hold',on=False)
   samples=[]
   for i in range(5):
    await asyncio.sleep(.45);p=await asyncio.to_thread(get,f"/parameter/by-id/{numeric[probe]['id']}");samples.append(p['value'])
    if i in (0,4):await asyncio.to_thread(snap,f'{col}-drive-{i}')
   row['drive_samples']=samples;row['drive_varied']=max(samples)-min(samples)>.001;results.append(row)
   (P/'live-results.json').write_text(json.dumps(results,indent=2));print(row['source'],len(row['checks']),sum(c['ok'] for c in row['checks']),samples,flush=True)
   publish(f"{row['source']}: numeric pass captured; awaiting rendered review.",record={'id':f'D1 L5C{col}','status':'Checking','note':'Control samples captured; visual review pending.'})
   if col!=38:await send('hold',on=True)
  (P/'heart-after.json').write_text(json.dumps(state));task.cancel()
asyncio.run(main())
