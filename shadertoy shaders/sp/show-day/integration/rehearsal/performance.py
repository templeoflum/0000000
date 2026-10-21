import asyncio,json,time,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());assert s['arena_connected'];initial=s;records=[]
  async def read():
   nonlocal s
   async for m in w:s=json.loads(m)
  reader=asyncio.create_task(read())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  def layer():return next(l for l in s['layers'] if l['i']==5)
  async def until(fn):
   for _ in range(100):
    await asyncio.sleep(.15)
    if fn():return
   raise AssertionError('Timed out awaiting state')
  def record(label):
   records.append(dict(label=label,time=time.time(),state=s));(P/'performance-results.json').write_text(json.dumps(records))
  try:
   await send('play_all',action='settle');await asyncio.sleep(4)
   await send('surface_cfg',value={'banks':{**s['surface'].get('banks',{}),'figure':'heart'}});await until(lambda:layer()['bank']=='heart')
   cols=[c['col'] for c in layer()['heart_copies']];assert len(cols)>2
   start=layer()['ccol'];assert start in cols
   for direction in ['next','prev','rand']:
    before=layer()['ccol'];expected=cols[(cols.index(before)+(1 if direction=='next' else -1))%len(cols)] if direction!='rand' else None
    await send('clip_nav',layer=5,dir=direction);await until(lambda:layer()['ccol']!=before)
    assert layer()['ccol'] in cols and (expected is None or layer()['ccol']==expected)
    await asyncio.sleep(1);record('nav-'+direction)
   await send('launch',layer=5,col=73);await until(lambda:layer()['ccol']==73 and any(c['layer']==5 and c['col']==73 for c in s['clips']))
   await send('play_all',action='settle');await asyncio.sleep(4)
   parked={f['key'] for f in s['fx'] if f.get('has_amount') and f.get('observed_amount',f['env'])<=.001}
   await send('play_all',action='open');await asyncio.sleep(4)
   c=next(c for c in s['clips'] if c['layer']==5);assert sum(bool(v['drive']) for v in c['slots'])>0
   v0={x['name']:x['v'] for x in c['slots']};record('open')
   await asyncio.sleep(1)
   c=next(c for c in s['clips'] if c['layer']==5);assert any(abs(x['v']-v0[x['name']])>.0001 for x in c['slots'])
   assert all(f.get('observed_amount',f['env'])<=.001 for f in s['fx'] if f['key'] in parked)
   await send('play_all',action='shuffle',value='harmonic');await asyncio.sleep(4);record('shuffle')
   assert next(c for c in s['clips'] if c['layer']==5)['g']['timing_mode']=='harmonic'
   await send('play_all',action='settle');await asyncio.sleep(5)
   assert all(not x['drive'] for c in s['clips'] for x in c['slots'] if x.get('owner')=='heart')
   assert all(f.get('observed_amount',f['env'])<=.001 for f in s['fx'] if f.get('has_amount'))
   record('settled');print('PASS Heart bank next / previous / random, live motion, parked effects unchanged by Open, musical shuffle, settled drives and effects',flush=True)
  finally:
   await send('play_all',action='settle');await send('launch',layer=5,col=73)
   await asyncio.sleep(4);reader.cancel()
asyncio.run(main())
