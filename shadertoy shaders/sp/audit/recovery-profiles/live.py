import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1';profiles=json.loads((P/'profiles.json').read_text());rests={r['source']:r['static'] for r in profiles if 'static'in r}
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=15))
def snap(name):P.joinpath(name+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain());rows=[]
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('play_all',action='settle');await asyncio.sleep(4)
  for l,col in [(3,4),(5,71),(5,72)]:
   for layer in state['layers']:await send('opacity',layer=layer['i'],value=int(layer['i']==l))
   await send('launch',layer=l,col=col)
   for _ in range(60):
    await asyncio.sleep(.2);c=next((x for x in state['clips'] if x['layer']==l and x['col']==col),None)
    if c:break
   assert c;a=dict(layer=l,col=col,instance=c['instance']);native=await asyncio.to_thread(get,f'/composition/layers/{l}/clips/{col}');source=native['video']['description'];expected=rests[source]
   for sl in c['slots']:await send('manual',**a,slot=sl['name'],value=.7)
   await send('home',**a,factory=True);await asyncio.sleep(4)
   native=await asyncio.to_thread(get,f'/composition/layers/{l}/clips/{col}');checks=[]
   for n,p in native['video']['sourceparams'].items():
    if n in expected:checks.append(dict(name=n,want=expected[n],actual=(p['value']-p['min'])/(p['max']-p['min'])))
   await asyncio.to_thread(snap,f'L{l}C{col}-home')
   await send('open',**a);await asyncio.sleep(1.5);c=next(x for x in state['clips'] if x['layer']==l and x['col']==col);opened=sum(s['drive'] for s in c['slots'])
   await send('home',**a,factory=True);await asyncio.sleep(4);c=next(x for x in state['clips'] if x['layer']==l and x['col']==col)
   r=dict(source=source,checks=checks,opened=opened,rest_drives=sum(s['drive'] for s in c['slots']),effects_on=[f['key'] for f in state['fx'] if f['has_amount'] and (f['target']>.001 or (f.get('observed_amount')or 0)>.01)])
   rows.append(r);(P/'live.json').write_text(json.dumps(rows,indent=2));print(source,'targets',sum(abs(x['want']-x['actual'])<.001 for x in checks),'/',len(checks),'open',opened,'rest',r['rest_drives'],'effects_on',r['effects_on'],flush=True)
  assert all(all(abs(x['want']-x['actual'])<.001 for x in r['checks']) and r['opened'] and not r['rest_drives'] and not r['effects_on'] for r in rows);t.cancel()
asyncio.run(main())
