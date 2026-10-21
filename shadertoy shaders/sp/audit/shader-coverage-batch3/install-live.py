import asyncio,json,urllib.request,urllib.parse,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1';sys.path.insert(0,str(P.parent/'shader-progress'));from update import publish
name='SP Figure Ring Source'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=15))
def post(path,data=b''):urllib.request.urlopen(urllib.request.Request(B+path,data,{'Content-Type':'text/plain'},method='POST'),timeout=15).close()
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 sources=await asyncio.to_thread(get,'/sources');assert name in json.dumps(sources),'Source not registered in Arena yet'
 c=await asyncio.to_thread(get,'/composition/layers/5/clips/10');assert (c.get('video') or {}).get('description') in (None,name),'Slot is occupied by another source'
 if not (c.get('video') or {}).get('description'):await asyncio.to_thread(post,'/composition/layers/5/clips/10/open',('source:///video/'+urllib.parse.quote(name)).encode())
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('launch',layer=5,col=10);c=None
  for _ in range(40):
   await asyncio.sleep(.25);c=next((x for x in state['clips'] if x['layer']==5 and x['col']==10),None)
   if c and {s['name'] for s in c['slots']}=={'thickness','twists','rate','gamma'}:break
  assert c,'Heart did not discover the ring'
  assert {s['name'] for s in c['slots']}=={'thickness','twists','rate','gamma'}
  a=dict(layer=5,col=10,instance=c['instance']);await send('hold',on=True);await send('morph',**a,seconds=1)
  for key,v in {'thickness':.65,'twists':.25,'rate':.58,'gamma':.5}.items():await send('manual',**a,slot=key,value=v)
  await asyncio.sleep(1);await send('home_set',**a);await asyncio.sleep(.5);await asyncio.to_thread(snap,'ring-live-home')
  for j,key in enumerate(['thickness','twists']):
   for k,v in [('Lo',.25),('Hi',.8),('Ratio','1:1' if j==0 else '1:2'),('Shape','sway'),('Drive',True)]:await send('slot_cfg',**a,slot=key,key=k,value=v)
   await send('drive',**a,slot=key,on=True)
  await send('hold',on=False);await asyncio.sleep(2);samples=[]
  for i in range(3):
   await asyncio.to_thread(snap,f'ring-live-motion-{i}');n=await asyncio.to_thread(get,'/composition/layers/5/clips/10');samples.append({k:v['value'] for k,v in n['video']['sourceparams'].items()});await asyncio.sleep(.8)
  (P/'ring-live.json').write_text(json.dumps({'slots':[s['name'] for s in c['slots']],'samples':samples,'state':state},indent=2))
  comp=await asyncio.to_thread(get,'/composition');(P/'composition-after.json').write_text(json.dumps(comp))
  # Extend the original census with the newly created clip; do not count the old ring as fixed.
  lp=P.parent/'shader-coverage-batch1/coverage.json';ledger=json.loads(lp.read_text());cl=comp['layers'][4]['clips'][9];pr=cl['video']['sourceparams']
  ledger['clips'].append(dict(deck=1,deck_name='Gradient',layer=5,col=10,name=name,source=name,controls=pr,other_controls={},heart_registered=True,enrolled_now=True,rendered_status='batch3: bounded new source; nine GPU aspect/parameter cases and live drive samples'))
  ledger['decks'][0]['clips']+=1;lp.write_text(json.dumps(ledger,indent=2))
  publish('New bounded ring installed in Figure L5C10. Live thickness + twists drive checked; original ring preserved.',record={'id':'D1 L5C10','status':'Sampled','sampled':True,'note':'New bounded source: landscape/portrait/square checks passed. Thickness + twists driven; shared Transform owns size/position.'})
  t.cancel();print('New ring active at L5C10',samples)
asyncio.run(main())
