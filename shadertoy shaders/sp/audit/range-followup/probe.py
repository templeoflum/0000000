import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
def get(p):return json.load(urllib.request.urlopen('http://localhost:8080/api/v1'+p,timeout=10))
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain());rows=[]
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  col=97
  await send('launch',layer=3,col=col)
  for _ in range(50):
   await asyncio.sleep(.2);c=next((c for c in state['clips'] if c['layer']==3 and c['col']==col),None)
   if c:break
  a=dict(layer=3,col=col,instance=c['instance']);p=(await asyncio.to_thread(get,f'/composition/layers/3/clips/{col}'))['video']['sourceparams']['Num X'];span=p['max']-p['min']
  await send('drive',**a,slot='Num X',on=False);await send('manual',**a,slot='Num X',value=(16-p['min'])/span)
  for k,v in [('Lo',(8-p['min'])/span),('Hi',(32-p['min'])/span),('Ratio','1:1'),('Shape','sway')]:await send('slot_cfg',**a,slot='Num X',key=k,value=v)
  await send('drive',**a,slot='Num X',on=True);await send('hold',on=False)
  for i in range(40):
   await asyncio.sleep(.2);c=next(c for c in state['clips'] if c['layer']==3 and c['col']==col);sl=next(s for s in c['slots'] if s['name']=='Num X');v=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];rows.append(dict(t=i*.2,native=v,slot=sl))
  await send('drive',**a,slot='Num X',on=False);await send('manual',**a,slot='Num X',value=(16-p['min'])/span)
  (P/'before.json').write_text(json.dumps(dict(parameter=p,rows=rows),indent=2));print([(r['t'],round(r['native'],2),r['slot']['lo'],r['slot']['hi']) for r in rows[::5]]);t.cancel()
asyncio.run(main())
