import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=15))
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('launch',layer=3,col=38)
  for _ in range(40):
   await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==3 and c['col']==38 and c.get('slots')),None)
   if c:break
  assert c
  a=dict(layer=3,col=38,instance=c['instance']);p=(await asyncio.to_thread(get,'/composition/layers/3/clips/38'))['video']['sourceparams']['Radius'];old=(p['value']-p['min'])/(p['max']-p['min'])
  await send('drive',**a,slot='Radius',on=False);await asyncio.sleep(.3);await send('manual',**a,slot='Radius',value=.7);want=p['min']+.7*(p['max']-p['min'])
  for _ in range(20):
   await asyncio.sleep(.15);actual=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value']
   if abs(actual-want)<.001:break
  result=dict(requested=want,observed=actual,ok=abs(actual-want)<.001);(P/'retry.json').write_text(json.dumps(result,indent=2));print(result)
  await send('manual',**a,slot='Radius',value=old);await send('launch',layer=3,col=51);t.cancel()
asyncio.run(main())
