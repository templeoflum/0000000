"""Exercise restored output shaping through Heart; return all effects to bypass."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
async def main():
 report=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  async def state():return json.loads(await asyncio.wait_for(ws.recv(),5))
  s=await state();fx=[e for e in s['fx'] if e['layer']==1 and e['name'] in ['Invert RGB','Blur','Sharpen']]
  assert len(fx)==3,[(e['name'],e['key']) for e in fx]
  keys=[e['key'] for e in fx];pair=[e['key'] for e in fx if e['name'] in ['Blur','Sharpen']]
  async def settle(on,selected):
   end=time.monotonic()+5
   while time.monotonic()<end:
    s=await state();rows=[e for e in s['fx'] if e['key'] in selected]
    if len(rows)==len(selected) and all(abs(e['env']-on)<.001 and e['bypassed']==(not on) for e in rows):return rows
   raise RuntimeError('Effect did not settle')
  try:
   for e in fx:
    await ws.send(json.dumps({'cmd':'fx_amount','key':e['key'],'value':1}));await settle(1,[e['key']])
    report.append({'name':e['name'],'on_verified':True})
    await ws.send(json.dumps({'cmd':'fx_amount','key':e['key'],'value':0}));await settle(0,[e['key']])
   await ws.send(json.dumps({'cmd':'fx_pair','keys':pair}));await settle(1,pair)
   await ws.send(json.dumps({'cmd':'fx_pair','keys':pair}));await settle(0,pair)
   report.append({'linked_pair_on_off':True})
  finally:
   for key in keys:await ws.send(json.dumps({'cmd':'fx_amount','key':key,'value':0}))
   await settle(0,keys)
  await ws.send(json.dumps({'cmd':'patch_save','name':'Feedback shaping'}));busy=False;end=time.monotonic()+30
  while time.monotonic()<end:
   s=await state();op=s['patch_operation'];busy|=op['active']
   if busy and not op['active']:
    assert op['stage']=='Ready',op;break
  else:raise RuntimeError('Save unconfirmed')
 Path('sp/design/heart-performance-plan/feedback-instrument/shaping-live-checks.json').write_text(json.dumps(report,indent=2));print(report)
asyncio.run(main())
