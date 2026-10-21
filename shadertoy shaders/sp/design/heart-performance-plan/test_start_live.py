"""Authorized working-composition test: assemble candidate, save, clear and recall."""
import asyncio,json,time,sys
from pathlib import Path
import websockets
OUT=Path(__file__).parent
NAME=sys.argv[1] if len(sys.argv)>1 else "Studio start"
async def main():
 trace=[]
 async with websockets.connect('ws://127.0.0.1:8766',max_size=8_000_000) as ws:
  async def send(cmd,**kw):await ws.send(json.dumps(dict(cmd=cmd,**kw)))
  async def wait(test,seconds=35):
   end=time.monotonic()+seconds
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(ws.recv(),4))
    if test(s):return s
   raise RuntimeError('Timed out: '+str(s.get('patch_status')))
  s=await wait(lambda s:s.get('arena_connected'))
  for l,c in [(1,1),(2,1),(3,1),(5,5)]:await send('launch',layer=l,col=c)
  wanted={'map','level','ground','shell'}
  await wait(lambda s:{c['name'] for c in s['clips']}==wanted)
  for l,v in enumerate([.6,1.,.45,0.,.65,0.,0.,0.],1):await send('opacity',layer=l,value=v)
  for l,c in [(1,1),(2,1),(3,1),(5,5)]:await send('home',layer=l,col=c,factory=True)
  await send('hold',on=False)
  await send('bars',bars=8)
  s=await wait(lambda s:sum(sum(x['drive'] for x in c['slots']) for c in s['clips'])>40)
  await send('patch_save',name=NAME)
  await wait(lambda s:s.get('patch_status') in ('Queued','Applying'))
  s=await wait(lambda s:s.get('patch_status')=='Ready')
  trace.append({'step':'saved','clips':[(c['name'],sum(x['drive'] for x in c['slots'])) for c in s['clips']]})
  for l in range(1,9):await send('clear',layer=l)
  await wait(lambda s:not s['clips'])
  await send('patch_recall',name=NAME)
  await wait(lambda s:s.get('patch_status') in ('Queued','Applying'))
  s=await wait(lambda s:s.get('patch_status')=='Ready' and {c['name'] for c in s['clips']}==wanted)
  trace.append({'step':'recalled','ready':s['arena_connected'],'clips':[(c['name'],sum(x['drive'] for x in c['slots'])) for c in s['clips']],'queue':s['queue']})
  await send('reconnect')
  await wait(lambda s:not s.get('arena_connected'))
  s=await wait(lambda s:s.get('arena_connected') and {c['name'] for c in s['clips']}==wanted)
  trace.append({'step':'reconnected','queue':s['queue']})
 (OUT/'start-live.json').write_text(json.dumps(trace,indent=2))
 print(json.dumps(trace))
asyncio.run(main())
