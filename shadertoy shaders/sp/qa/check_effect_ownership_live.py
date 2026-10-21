"""Live two-client momentary/reconnect check, restoring original effect config/amount."""
import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
async def main():
 report=[]
 async with websockets.connect('ws://127.0.0.1:8766') as a,websockets.connect('ws://127.0.0.1:8766') as b:
  s=json.loads(await a.recv());await b.recv()
  async def drain_b():
   async for _ in b:pass
  draining=asyncio.create_task(drain_b())
  fx=next(e for e in s['fx'] if e['layer']==1 and e['name']=='Blur');key=fx['key'];cfg=fx['cfg'].copy();original=fx['target']
  async def send(w,cmd,**kw):await w.send(json.dumps({'cmd':cmd,**kw}))
  async def wait(value,check_native=False):
   end=time.monotonic()+12
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(a.recv(),5));rows=[e for e in s['fx'] if e['key']==key]
    if rows and abs(rows[0]['env']-value)<.002 and abs(rows[0]['target']-value)<.002:
     if check_native:
      pid=rows[0]['params']['Opacity']['id']
      def get():return json.load(urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}',timeout=3))['value']
      native=await asyncio.to_thread(get)
      if abs(native-value)>.01:continue
     return rows[0]
   raise RuntimeError(f'Effect failed to settle at {value}')
  try:
   await send(a,'fx_cfg',key=key,cfg={**cfg,'mode':'momentary','quant':0})
   await send(a,'fx_amount',key=key,value=.35);await wait(.35,True)
   await send(a,'fx_press',key=key);await send(b,'fx_press',key=key);await wait(1,True)
   await send(a,'fx_release',key=key);await asyncio.sleep(.3);await wait(1,True)
   await send(b,'fx_release',key=key);await wait(.35,True);report.append('Overlapping clients restore nonzero baseline after last release')
   await send(a,'fx_press',key=key);await wait(1)
   await send(b,'fx_amount',key=key,value=.7);await send(a,'fx_release',key=key);await wait(.7,True);report.append('New manual amount survives late release')
   await send(a,'fx_amount',key=key,value=.35);await wait(.35)
   await send(b,'fx_press',key=key);await wait(1);await b.close();await wait(.35,True);report.append('Client disconnect restores held baseline')
   await send(a,'fx_press',key=key);await wait(1);await send(a,'reconnect');await asyncio.sleep(.5);await wait(.35,True);report.append('Reconnect restores held baseline')
  finally:
   await send(a,'fx_release',key=key)
   await send(a,'fx_cfg',key=key,cfg=cfg)
   await send(a,'fx_amount',key=key,value=original);await wait(original,True)
   draining.cancel()
 Path('sp/design/heart-performance-plan/effect-ownership-live.json').write_text(json.dumps(report,indent=2));print(report)
asyncio.run(main())
