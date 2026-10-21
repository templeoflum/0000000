import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent; B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=10))
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=10).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  for l,c,values in [(8,1,{'Amount':.5,'Size':.2,'Flicker':.5,'Level':.5}),(3,8,{'Scale':.5,'Drift':.5,'Contrast':.5,'Level':.5})]:
   await send('hold',on=True)
   for layer in state['layers']:await send('opacity',layer=layer['i'],value=int(layer['i']==l))
   await send('launch',layer=l,col=c);await asyncio.sleep(2)
   clip=next(x for x in state['clips'] if x['layer']==l and x['col']==c);a=dict(layer=l,col=c,instance=clip['instance'])
   for s in clip['slots']:await send('drive',**a,slot=s['name'],on=False)
   for name,v in values.items():await send('manual',**a,slot=name,value=v)
   await asyncio.sleep(1);await asyncio.to_thread(snap,f'L{l}C{c}-neutral')
   native=await asyncio.to_thread(get,f'/composition/layers/{l}/clips/{c}');P.joinpath(f'L{l}C{c}.json').write_text(json.dumps(native,indent=2))
   print(l,c,{k:v.get('value') for k,v in native['video']['sourceparams'].items() if k in values},flush=True)
  t.cancel()
asyncio.run(main())
