import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
async def main():
 results=[]
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());e=next(e for e in s['fx'] if e['key']=='composition/effect/MTK_PXLMELT~1');assert e['observed_amount']==0
  a=dict(key=e['key'],instance=e['instance'],name='MELT_LOCK');pid=e['params']['MELT_LOCK']['id']
  async def drain():
   async for m in w:pass
  t=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**a,**kw)))
  def read():return json.load(urllib.request.urlopen(f'http://localhost:8080/api/v1/parameter/by-id/{pid}',timeout=3))['value']
  async def check(label,want):
   for _ in range(20):
    await asyncio.sleep(.1);v=await asyncio.to_thread(read)
    if v==want:break
   results.append(dict(label=label,want=want,actual=v));assert v==want,(label,v)
  try:
   await send('fx_param',value=False);await check('initial off',False)
   await send('fx_bool_press');await check('hold on',True)
   await send('fx_bool_release');await check('release off',False)
   await send('fx_param',value=True);await check('latch on',True)
   await send('fx_bool_press');await send('fx_bool_release');await check('hold preserves latch',True)
   await send('fx_param',value=False);await check('latch off',False)
   await send('fx_bool_press');await check('second hold',True)
   await send('fx_param',value=False);await send('fx_bool_release');await check('new edit beats release',False)
   await send('fx_bool_press');await check('disconnect setup',True)
  finally:t.cancel()
 await check('disconnect clears hold',False)
 (P/'live.json').write_text(json.dumps(results,indent=2));print(len(results),'native checks passed')
asyncio.run(main())
