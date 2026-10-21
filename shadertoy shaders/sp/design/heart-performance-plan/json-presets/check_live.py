import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
OUT=Path(__file__).parent
async def main():
 async with websockets.connect('ws://127.0.0.1:8766',max_size=8000000) as ws:
  async def get():return json.loads(await asyncio.wait_for(ws.recv(),5))
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  async def wait(test):
   end=time.monotonic()+15
   while time.monotonic()<end:
    s=await get()
    if test(s):return s
   raise RuntimeError('Timed out '+str(s.get('events',[])[-3:]))
  def comp():return json.load(urllib.request.urlopen('http://127.0.0.1:8080/api/v1/composition'))
  before=await get();native_before=await asyncio.to_thread(comp)
  name='Live warp'
  await send('performance_save',name=name);await wait(lambda s:s.get('performance_status')=='Saved '+name)
  fx=next(e for e in before['fx'] if e['name']=='Linear Cloner' and e.get('motion'))
  slot=next(sl for sl in fx['motion']['slots'] if sl['name']=='End Scale');old=slot['hi']
  await send('slot_cfg',effect=fx['key'],instance=fx['instance'],slot='End Scale',key='Hi',value=max(slot['lo'],old-.02))
  await wait(lambda s:any(e['key']==fx['key'] and any(x['name']=='End Scale' and abs(x['hi']-old)>.001 for x in e.get('motion',{}).get('slots',[])) for e in s['fx']))
  started=time.monotonic();await send('performance_load',name=name,seconds=1)
  observed=[]
  while time.monotonic()-started<2:
   s=await get();observed.append(s)
  applied=next(s for s in observed if s.get('performance_status','').startswith('Applied '+name))
  native_after=await asyncio.to_thread(comp)
  report={'preset':name,'composition_identity_unchanged':native_before['name']==native_after['name'],'connected_throughout':all(s['arena_connected'] for s in observed),'no_setup_operation':all(not s['patch_operation']['active'] for s in observed),'turns_advanced':observed[-1]['H']-observed[0]['H'],'restored_hi':next(x['hi'] for e in applied['fx'] if e['key']==fx['key'] for x in e['motion']['slots'] if x['name']=='End Scale'),'expected_hi':old,'samples':len(observed),'status':applied['performance_status']}
  (OUT/'live.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
asyncio.run(main())
