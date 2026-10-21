import asyncio,json,urllib.request,sys
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
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  await send('launch',layer=3,col=21)
  for _ in range(40):
   await asyncio.sleep(.25);c=next((c for c in state['clips'] if c['layer']==3 and c['col']==21 and c.get('slots')),None)
   if c:break
  a=dict(layer=3,col=21,instance=c['instance']);p=(await asyncio.to_thread(get,'/composition/layers/3/clips/21'))['video']['sourceparams']['scale'];await send('drive',**a,slot='scale',on=False);rows=[]
  for i in range(100):
   want=[.23,.68,.41,.81][i%4];await send('manual',**a,slot='scale',value=want);await asyncio.sleep(.18)
   native=await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}");actual=native['value'];cl=next((c for c in state['clips'] if c['layer']==3 and c['col']==21),{});sl=next((s for s in cl.get('slots',[]) if s['name']=='scale'),{})
   row=dict(i=i,want=want,actual=actual,ok=abs(actual-want)<.001,slot=sl)
   if not row['ok']:
    await asyncio.sleep(.5);row['late']=(await asyncio.to_thread(get,f"/parameter/by-id/{p['id']}"))['value'];row['events']=state.get('events',[])[-5:];print(row,flush=True)
   rows.append(row)
  out=P/(sys.argv[1] if len(sys.argv)>1 else 'before.json');out.write_text(json.dumps(rows,indent=2));print('passes',sum(r['ok'] for r in rows),'/',len(rows),flush=True);t.cancel()
asyncio.run(main())
