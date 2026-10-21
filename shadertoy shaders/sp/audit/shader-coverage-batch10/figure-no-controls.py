import asyncio,json,urllib.request,sys
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'shader-progress'));from update import publish
B='http://localhost:8080/api/v1'
def get(p):return json.load(urllib.request.urlopen(B+p,timeout=15))
def post(p):urllib.request.urlopen(urllib.request.Request(B+p,b'',method='POST'),timeout=15).close()
def snap(n):P.joinpath(n+'.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=15).read())
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   async for m in w:pass
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  for l in state['layers']:await send('opacity',layer=l['i'],value=int(l['i']==5))
  rows=[]
  for col in [40,44]:
   publish(f'Checking Figure L5C{col}: source has no numeric controls in census.',phase='Working',record={'id':f'D1 L5C{col}','status':'Checking','note':'Render-only check; no numeric controls in census.'})
   await asyncio.to_thread(post,f'/composition/layers/5/clips/{col}/connect');await asyncio.sleep(1.5)
   native=await asyncio.to_thread(get,f'/composition/layers/5/clips/{col}');rows.append(dict(col=col,source=native['video']['description'],sourceparams=native['video'].get('sourceparams',{})))
   for i in [0,1]:await asyncio.to_thread(snap,f'no-controls-L5C{col}-{i}');await asyncio.sleep(.6)
   (P/'figure-no-controls.json').write_text(json.dumps(rows,indent=2));print(rows[-1],flush=True)
  t.cancel()
asyncio.run(main())
