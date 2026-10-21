"""Bounded Heart action-path exercise during independent sustained acquisition sampling."""
import asyncio,json,time
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/heart-performance-plan/performance/action-exercise.json'
class Suspended(Exception):pass
async def main():
 log=[];saved=False;suspended=False
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  state=json.loads(await ws.recv())
  expected={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in state['clips']}
  async def read():
   nonlocal state
   state=json.loads(await asyncio.wait_for(ws.recv(),5))
   t=json.loads((ROOT/'monitor/telemetry.json').read_text())
   if t.get('suspended'):raise Suspended('Mac session suspended; no automatic resume or recall')
   return state
  def record(value):
   log.append({'time':time.time(),**value});OUT.write_text(json.dumps(log,indent=2));print(value,flush=True)
  async def send(cmd):
   await ws.send(json.dumps(cmd));record({'command':cmd})
  async def observe(seconds):
   end=time.monotonic()+seconds
   while time.monotonic()<end:await read()
  async def patch(cmd,name):
   await send({'cmd':cmd,'name':name});busy=False;end=time.monotonic()+45
   while time.monotonic()<end:
    s=await read();op=s['patch_operation'];busy|=op['active']
    if busy and not op['active']:
     assert op['stage']=='Ready',op
     record({'operation':cmd,'stage':'Ready'});return
   raise RuntimeError('Patch did not complete')
  try:
   await patch('patch_save','Before endurance');saved=True
   await send({'cmd':'hold','on':True});await observe(3)
   h=state['H'];await observe(2);assert state['hold'] and abs(state['H']-h)<.01
   await send({'cmd':'hold','on':False});await observe(3);assert not state['hold'] and state['H']>h
   for layer in range(8,0,-1):
    await send({'cmd':'clip_nav','dir':'next','layer':layer});await observe(8)
    record({'layer':layer,'after_next':[(c['col'],c['name']) for c in state['clips'] if c['layer']==layer]})
    await send({'cmd':'clip_nav','dir':'prev','layer':layer});await observe(8)
    record({'layer':layer,'after_prev':[(c['col'],c['name']) for c in state['clips'] if c['layer']==layer]})
    await patch('patch_recall','Before endurance');await observe(6)
   for behavior in ['Drift','Breathe','Fold','Turn']:
    await send({'cmd':'feedback_behavior','name':behavior,'layer':1,'col':6});await observe(15)
   await send({'cmd':'bars','bars':4});await observe(15)
   await send({'cmd':'home','factory':True,'layer':1,'col':6});await observe(15)
   fx=[e for e in state['fx'] if e['layer']==1 and e['name'] in ['Invert RGB','Blur','Sharpen','Delay RGB']]
   for effect in fx:
    await send({'cmd':'fx_amount','key':effect['key'],'value':1});await observe(8)
    await send({'cmd':'fx_amount','key':effect['key'],'value':0});await observe(5)
   await send({'cmd':'feedback_reset','layer':1,'col':6});await observe(8)
   await send({'cmd':'reconnect'});await observe(12);assert state['arena_connected']
   await patch('patch_recall','Before endurance');await observe(8)
   actual={(c['layer'],c['name']):sum(x['drive'] for x in c['slots']) for c in state['clips']};assert actual==expected,(actual,expected)
   record({'result':'passed','note':'Heart command path exercised; not a trackpad/focus GUI acceptance claim'})
  except Suspended as e:
   suspended=True;record({'result':'suspended','reason':str(e)});raise
  except Exception as e:
   record({'result':'failed','reason':str(e)});raise
  finally:
   if saved and not suspended:await patch('patch_recall','Before endurance')
asyncio.run(main())
