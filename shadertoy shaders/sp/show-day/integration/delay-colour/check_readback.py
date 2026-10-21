import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=8))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def read():
   nonlocal state
   async for m in w:state=json.loads(m)
  reader=asyncio.create_task(read());fx=[]
  for _ in range(50):
   fx=[f for f in state['fx'] if f['scope']=='L' and f['layer']==4 and f['name'] in ['ColourLoop','Delay RGB']]
   if len(fx)==2:break
   await asyncio.sleep(.2)
  assert len(fx)==2
  async def send(f,cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,key=f['key'],instance=f['instance'],**kw)))
  try:
   pass
   for f in fx:
    assert len(f['motion']['slots'])==(5 if f['name']=='ColourLoop' else 3)
    await send(f,'fx_amount',value=1);await asyncio.sleep(3)
    actual=await asyncio.to_thread(get,'/parameter/by-id/'+str(f['params']['Opacity']['id']));assert actual['value']>.99
    await send(f,'fx_amount',value=0);await asyncio.sleep(.5)
   P.joinpath('heart-controls.json').write_text(json.dumps(fx,indent=2));print('PASS independent Delay ColourLoop (5 drives), DelayRGB (3 drives), native amount response')
  finally:
   for f in fx:await send(f,'fx_amount',value=0)
   await asyncio.sleep(1);reader.cancel()
asyncio.run(main())
