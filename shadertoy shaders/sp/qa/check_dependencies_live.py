"""Checked save and repeated recall; preserve previous named revisions."""
import asyncio,json,time
from pathlib import Path
import websockets
async def main():
 report=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  before=json.loads(await ws.recv());expected={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in before['clips']}
  for command in ['patch_save','patch_recall','patch_recall']:
   await ws.send(json.dumps({'cmd':command,'name':'Feedback checked'}));busy=False;end=time.monotonic()+50;start=time.monotonic();stages=[]
   while time.monotonic()<end:
    s=json.loads(await asyncio.wait_for(ws.recv(),5));op=s['patch_operation'];busy|=op['active']
    if not stages or stages[-1]!=op['stage']:stages.append(op['stage'])
    if busy and not op['active']:
     assert op['stage']=='Ready',op
     actual={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in s['clips']};assert actual==expected,(actual,expected)
     report.append({'command':command,'seconds':round(time.monotonic()-start,3),'stages':stages,'instruments':[[*k,v] for k,v in actual.items()]});print(report[-1],flush=True);break
   else:raise RuntimeError('Operation not confirmed')
 Path('sp/design/heart-performance-plan/dependency-live-checks.json').write_text(json.dumps(report,indent=2))
asyncio.run(main())
