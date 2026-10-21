import asyncio,json,time
from pathlib import Path
import websockets
OUT=Path(__file__).resolve().parents[1]/'design/heart-performance-plan/feedback-instrument'
async def main():
 results=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  s=json.loads(await ws.recv())
  expected={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in s['clips']}
  for cmd in ['patch_save','patch_recall','patch_recall']:
   await ws.send(json.dumps({'cmd':cmd,'name':'Feedback performance'}));start=time.monotonic();saw_busy=False;stages=[]
   while time.monotonic()-start<40:
    s=json.loads(await asyncio.wait_for(ws.recv(),4));op=s.get('patch_operation',{});stage=op.get('stage')
    if not stages or stage!=stages[-1]:stages.append(stage)
    if op.get('active'):saw_busy=True
    if (saw_busy or cmd=='patch_save' and 'Feedback performance' in s.get('patches',[])) and not op.get('active'):
     if stage!='Ready':raise RuntimeError(str(op))
     actual={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in s['clips']}
     assert actual==expected,(actual,expected)
     row={'command':cmd,'seconds':round(time.monotonic()-start,2),'stages':stages,'instruments':[[*k,v] for k,v in actual.items()]};results.append(row);print(json.dumps(row),flush=True);break
   else:raise RuntimeError('Patch operation timed out')
 (OUT/'repeated-recall-live.json').write_text(json.dumps(results,indent=2))
asyncio.run(main())
