import asyncio,json,urllib.request,urllib.parse,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent; B='http://localhost:8080/api/v1'
sys.path.insert(0,str(P.parent/'shader-progress'));from update import publish

def get(p):return json.load(urllib.request.urlopen(B+p,timeout=15))
def open_source(col,name):
 p=f'/composition/layers/5/clips/{col}';c=get(p);d=(c.get('video') or {}).get('description');assert d in (None,name),f'Occupied {col}: {d}'
 if not d:urllib.request.urlopen(urllib.request.Request(B+p+'/open',('source:///video/'+urllib.parse.quote(name)).encode(),{'Content-Type':'text/plain'},method='POST'),timeout=15).close()
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 for col,name in [(11,'SP Figure Spike Source'),(12,'SP Figure Crystal Source')]:await asyncio.to_thread(open_source,col,name)
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv());(P/'heart-before.json').write_text(json.dumps(state))
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  results=[]
  for layer,col,preferred in [(5,11,'Spike Sharpness'),(5,12,'Refraction'),(3,21,'scale'),(3,23,'Speed'),(3,24,'Speed'),(3,25,'density'),(3,29,'Speed'),(3,34,'width')]:
   publish(f'Checking live Heart control and rendered output: L{layer}C{col}.',record={'id':f'D1 L{layer}C{col}','status':'Checking','note':'Live sample in progress.'})
   await send('hold',on=True)
   for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==layer))
   for f in state['fx']:
    if f.get('has_amount') and (f['scope']=='C' or f.get('layer')==layer):
     await send('fx_cfg',key=f['key'],instance=f['instance'],cfg={'attack':.05,'release':.05});await send('fx_amount',key=f['key'],instance=f['instance'],value=0)
   await send('launch',layer=layer,col=col);clip=None
   for _ in range(40):
    await asyncio.sleep(.25);clip=next((c for c in state['clips'] if c['layer']==layer and c['col']==col and c.get('slots')),None)
    if clip:break
   assert clip,f'Not discovered L{layer}C{col}'
   a=dict(layer=layer,col=col,instance=clip['instance']);native=await asyncio.to_thread(get,f'/composition/layers/{layer}/clips/{col}');params=native['video']['sourceparams'];numeric={k:p for k,p in params.items() if p.get('valuetype')=='ParamRange'}
   probe=next((k for k in numeric if k.lower()==preferred.lower()),None);assert probe,(preferred,list(numeric))
   for s in clip['slots']:await send('drive',**a,slot=s['name'],on=False)
   p=numeric[probe];original=(p['value']-p['min'])/(p['max']-p['min']);checks=[]
   for v in [.3,.7]:
    await send('manual',**a,slot=probe,value=v);want=p['min']+(p['max']-p['min'])*v
    for _ in range(15):
     await asyncio.sleep(.15);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value']
     if abs(actual-want)<max(.001,(p['max']-p['min'])*.01):break
    checks.append(dict(requested=want,observed=actual,ok=abs(actual-want)<max(.001,(p['max']-p['min'])*.01)))
   await send('manual',**a,slot=probe,value=original)
   for k,v in [('Lo',.3),('Hi',.7),('Ratio','1:1'),('Shape','sway')]:await send('slot_cfg',**a,slot=probe,key=k,value=v)
   await send('drive',**a,slot=probe,on=True);await send('hold',on=False);samples=[]
   for i in range(4):
    await asyncio.sleep(.5);samples.append((await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'])
    if i in (0,3):await asyncio.to_thread(snap,f'L{layer}C{col}-motion-{i}')
   await send('drive',**a,slot=probe,on=False);await send('manual',**a,slot=probe,value=original)
   row=dict(layer=layer,col=col,source=native['video']['description'],controls=list(numeric),discovered=[s['name'] for s in clip['slots']],probe=probe,checks=checks,samples=samples,drive_varied=max(samples)-min(samples)>.001)
   results.append(row);(P/'live-results.json').write_text(json.dumps(results,indent=2));print(row,flush=True)
   if layer==5:
    lp=P.parent/'shader-coverage-batch1/coverage.json';ledger=json.loads(lp.read_text())
    if not any(c['deck']==1 and c['layer']==layer and c['col']==col for c in ledger['clips']):
     ledger['clips'].append(dict(deck=1,deck_name='Gradient',layer=layer,col=col,name=row['source'],source=row['source'],controls=numeric,other_controls={},heart_registered=True,enrolled_now=True,rendered_status='batch4: live control sampled; visual review pending'));ledger['decks'][0]['clips']+=1;lp.write_text(json.dumps(ledger,indent=2))
   publish(f"{row['source']}: control sample captured; reviewing full output next.",record={'id':f'D1 L{layer}C{col}','status':'Checking','note':f'{probe}: native readback and motion samples captured; visual review pending.'})
  task.cancel()
asyncio.run(main())
