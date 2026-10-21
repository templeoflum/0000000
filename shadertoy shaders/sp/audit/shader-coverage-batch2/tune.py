import asyncio,json,urllib.request,time,shutil
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
PLANS={
17:({'tile':12,'offset':.5,'stroke width':.55,'gradient':.025,'even rows':1,'odd rows':2,'rotate':0,'warp':1,'x':.5,'y':.5},{'warp':(.8,1.2),'rotate':(.1,.35)}),
18:({'grid x':24,'grid y':32,'grid2 x':6,'grid2 y':24,'center x':0,'center y':0,'curve x':0,'curve y':0,'shift':.4,'density':400,'rate':.08,'seed':71.34,'offset':.2},{'shift':(.25,.55),'density':(350,600)}),
28:({'intensity':.6,'speed':.18,'curve1':.5,'curve1 freq':.25,'curve2':.5,'curve2 freq':.25,'color mix':0},{'curve1':(.4,.6),'intensity':(.45,.65)}),
31:({'offset x':.5,'offset y':.5,'matrix x':.2,'matrix y':.4,'size':.28,'speed':.08,'hue':.5,'saturation':.65},{'hue':(.35,.65),'saturation':(.4,.8)}),
32:({'rate':.12,'scrolls y':.5,'scroll x':.5,'intensity':.5,'seed1':.5,'seed2':.5,'zoom':.35,'tint':.5,'sat':.5},{'intensity':(.35,.6),'tint':(.35,.65)}),
33:({'spin x':.05,'spin y':.05,'seed x':.18,'seed y':.54,'edge':.58,'glow':.65,'freq':.9,'pulse':.25,'pulse rate':.1,'thickness':.5,'scale':.3},{'thickness':(.4,.6),'glow':(.45,.7)})}
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=15))
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 home=P.parents[1]/'engine/home.json'
 if not (P/'homes-before.json').exists():shutil.copy2(home,P/'homes-before.json')
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain());results=[]
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('hold',on=True)
  for col,(base,drives) in PLANS.items():
   await send('launch',layer=3,col=col);clip=None
   for _ in range(40):
    await asyncio.sleep(.25);clip=next((c for c in state.get('clips',[]) if c['layer']==3 and c['col']==col),None)
    if clip:break
   if not clip:raise RuntimeError('Discovery failed '+str(col))
   addr=dict(layer=3,col=col,instance=clip['instance']);native=await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}');params=native['video']['sourceparams'];checks=[]
   await send('auto',**addr,bars=0);await send('morph',**addr,seconds=1.5)
   for s in clip['slots']:await send('drive',**addr,slot=s['name'],on=False)
   await asyncio.sleep(.5)
   async def manual(name,value):
    p=params[name];n=(value-p['min'])/(p['max']-p['min']);tolerance=max(.001,(p['max']-p['min'])*.01)
    for attempt in range(3):
     await send('manual',**addr,slot=name,value=n)
     for _ in range(12):
      await asyncio.sleep(.15);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value']
      if abs(actual-value)<tolerance:checks.append(dict(control=name,requested=value,observed=actual,attempts=attempt+1));return
    raise RuntimeError(f'{col}/{name} did not acknowledge {value}: {actual}')
   # Targeted retests preserve the original misses in live-results.json.
   if col==28:await manual('curve1 freq',.75)
   if col==31:await manual('size',.25)
   for name,value in base.items():await manual(name,value)
   await asyncio.sleep(.5);await asyncio.to_thread(snap,f'tuned-{col}-home')
   await send('home_set',**addr);await asyncio.sleep(.5)
   for key,value in [('Pattern',0),('Spread',1),('Depth',1),('FM',0)]:await send('global_cfg',**addr,key=key,value=value)
   await send('speed',**addr,value=1)
   for j,(name,(low,high)) in enumerate(drives.items()):
    p=params[name]
    for key,value in [('Ratio','1:1' if j==0 else '1:2'),('Mult',1),('Offset',0 if j==0 else .25),('Shape','sway'),('Lo',(low-p['min'])/(p['max']-p['min'])),('Hi',(high-p['min'])/(p['max']-p['min']))]:await send('slot_cfg',**addr,slot=name,key=key,value=value)
    await send('drive',**addr,slot=name,on=True)
   await send('hold',on=False);await asyncio.sleep(2)
   samples=[]
   for i in range(3):
    await asyncio.to_thread(snap,f'tuned-{col}-motion-{i}');n=await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}');samples.append({k:n['video']['sourceparams'][k]['value'] for k in drives});await asyncio.sleep(1)
   # Home must stop both Heart drives and return the complete tested pose.
   await send('home',**addr);await asyncio.sleep(2)
   n=await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}');homecheck={k:abs(n['video']['sourceparams'][k]['value']-v)<max(.001,(params[k]['max']-params[k]['min'])*.01) for k,v in base.items()}
   active=next(c for c in state['clips'] if c['layer']==3 and c['col']==col);off=all(not s.get('drive') for s in active['slots'])
   row=dict(col=col,source=native['video']['description'],home_native=base,drives_native=drives,checks=checks,drive_samples=samples,home_return_checks=homecheck,slots_after_home=active['slots']);results.append(row)
   (P/'tuning-results.json').write_text(json.dumps(results,indent=2));print(col,'Home',sum(homecheck.values()),'/',len(homecheck),'manual retries',sum(x['attempts']-1 for x in checks),flush=True)
   # Leave the recommended pair active; rest pose remains on the Home button.
   for name in drives:await send('drive',**addr,slot=name,on=True)
   if col!=33:await send('hold',on=True)
  (P/'heart-after-tuning.json').write_text(json.dumps(state));task.cancel()
if __name__=='__main__':asyncio.run(main())
