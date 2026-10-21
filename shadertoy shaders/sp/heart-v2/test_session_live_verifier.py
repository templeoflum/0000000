"""Offline safety tests for the opt-in live verification helper."""
import copy, importlib.util, json, io, urllib.error
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('verify_session_live',ROOT/'checks/verify_session_live.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)

class Plans(unittest.TestCase):
 def setUp(self):
  self.catalog=json.loads((ROOT/'checks/session-runtime-before.json').read_text())['catalog']
  self.motion=json.loads((ROOT/'checks/session-starting-motion.json').read_text())
 def test_nine_actual_clips_and_native_identity_guard(self):
  plan,skipped=verify.make_plan(self.catalog,self.motion,'exercise')
  self.assertFalse(skipped);self.assertEqual([p['name']for p in plan],list(verify.CORE))
  self.assertEqual(sum(len(p['controls'])for p in plan),20)
  first=plan[0];layer=next(l for l in self.catalog['layers']if l['id']==first['layer_id'])
  next(c for c in layer['clips']if c['id']==first['clip_id'])['name']='Replaced'
  with self.assertRaisesRegex(ValueError,'identity changed'):verify.make_plan(self.catalog,self.motion,'exercise')
 def test_combination_does_not_invent_empty_glyph_slot(self):
  plan,skipped=verify.make_plan(self.catalog,self.motion,'load','ground')
  self.assertEqual({p['layer']for p in plan},{'figure','field','feedback','delay'})
  self.assertEqual(next(p['name']for p in plan if p['layer']=='field'),'ground')
  self.assertEqual([s['layer']for s in skipped],['glyph'])
  self.assertTrue(all(any(c['id']==p['clip_id']for l in self.catalog['layers']if l['id']==p['layer_id']for c in l['clips'])for p in plan))
 def test_observation_batched_below_broad_subscription_cap(self):
  batches=verify.target_batches(self.catalog)
  self.assertEqual(sum(len(b)for b in batches),len(self.catalog['targets']))
  self.assertTrue(all(sum(len(t['params'])for t in b)<=20 or len(b)==1 and len(b[0]['params'])<=200 for b in batches))

class CaptureCleanup(unittest.IsolatedAsyncioTestCase):
 async def test_state_watch_never_requests_native_subscriptions(self):
  heart=verify.Heart(None);heart.state={'error':''};sent=[]
  class Socket:
   async def send(self,payload):
    sent.append(json.loads(payload));heart.serial+=1
  heart.ws=Socket()
  await heart.send('watch',targets=['effect:20'])
  self.assertEqual(sent,[dict(cmd='watch',targets=['effect:20'],native_ids=[])])
  await heart.send('watch',targets=[])
  self.assertEqual(sent[-1],dict(cmd='watch',targets=[],native_ids=[]))
 async def test_scope_is_cleared_on_success_and_failure(self):
  saved=Restoration().saved()
  for fail in (False, True):
   heart=verify.Heart(None);heart.catalog=copy.deepcopy(saved['catalog']);heart.state=copy.deepcopy(saved['state']);calls=[]
   async def send(cmd,predicate=None,**data):
    calls.append(dict(cmd=cmd,**data))
    if fail and data.get('targets'):raise RuntimeError('Capture failed')
   heart.send=send
   if fail:
    with self.assertRaisesRegex(RuntimeError,'Capture failed'):await heart.snapshot()
   else:
    result=await heart.snapshot();self.assertEqual(result['state']['values'],saved['state']['values'])
   self.assertEqual(calls[-1],dict(cmd='watch',targets=[]))

class FakeHeart:
 def __init__(self,saved):
  self.catalog=copy.deepcopy(saved['catalog']);self.state=copy.deepcopy(saved['state']);self.commands=[]
  self.catalog['layers'][0]['active']=1
  self.state['values']['1']['value']=.7;self.state['values']['1']['owned']=True
 async def send(self,cmd,predicate=None,**data):
  self.commands.append(dict(cmd=cmd,**data))
  if cmd=='hold':self.state['hold']=data['on']
  if cmd=='manual':self.state['values'][str(data['id'])]['value']=data['value']
  if cmd=='select':self.state['selected']=data['target']
 async def launch(self,row,epoch):
  self.commands.append(dict(cmd='launch',**row))
  l=next(l for l in self.catalog['layers']if l['id']==row['layer_id'])
  l['active']=next((c['col']for c in l['clips']if c['id']==row['clip_id']),0)
 async def animation(self,pid,**data):
  self.commands.append(dict(cmd='animation_set',id=int(pid),**data))
  self.state['values'][str(pid)]['owned']=False
 async def snapshot(self):return dict(catalog=copy.deepcopy(self.catalog),state=copy.deepcopy(self.state))

class Restoration(unittest.IsolatedAsyncioTestCase):
 async def test_required_native_read_failure_includes_id_and_url(self):
  url='http://127.0.0.1:8080/api/v1/parameter/by-id/345'
  error=urllib.error.HTTPError(url,404,'Not Found',{},io.BytesIO(b'No native parameter'))
  with patch.object(verify.urllib.request,'urlopen',side_effect=error):
   with self.assertRaisesRegex(RuntimeError,r'parameter 345 read failed \(HTTP 404\).*parameter/by-id/345'):
    await verify.native_values([345])
 def test_untouched_native_clip_settings_are_excluded_without_omitting_owned_controls(self):
  saved=self.saved();p=dict(id=3,name='autopilot · target',type='ParamChoice',min=0,max=1,value='Other')
  q=dict(id=4,name='Level',type='ParamRange',min=0,max=1,value=.6)
  source=dict(id=5,name='Lens',type='ParamChoice',min=0,max=1,value='rectilinear')
  saved['catalog']['targets'] += [dict(id='clip:100',kind='clip',scope='clip',layer_id=10,clip_id=100,params=[p,q]),dict(id='source:100',kind='source',scope='clip',layer_id=10,clip_id=100,params=[source])]
  saved['state']['values'].update({'3':{'owned':False},'4':{'owned':True},'5':{'owned':False}})
  self.assertEqual(verify.restoration_ids(saved['catalog'],saved['state'],{10},{1}),{'1','4','5'})
  saved['state']['values']['4']['owned']=False
  self.assertEqual(verify.restoration_ids(saved['catalog'],saved['state'],{10},{1}),{'1','5'})
 def saved(self):
  level=dict(id=1,name='Level',type='ParamRange',min=0,max=1,value=0)
  drive=dict(id=2,name='Rotate',type='ParamRange',min=-180,max=180,value=3)
  catalog=dict(epoch='same',layers=[dict(id=10,name='figure',active=0,clips=[dict(id=100,col=1,name='4d',description='SP Atom 4D')])],targets=[dict(id='layer:10',kind='layer',scope='layer',layer_id=10,params=[level]),dict(id='effect:20',kind='effect',scope='layer',layer_id=10,effect_name='LinearCloner',params=[drive])])
  motion=dict(ratio='1:1',mult=1,offset=.2,shape=.8)
  value=dict(value=0,owned=False,drive=False,locked=False,lo=0,hi=1,rate_scale=1,intensity_scale=1,motion=motion)
  state=dict(hold=True,bpm=74,selected='effect:20',groups={},values={'1':copy.deepcopy(value),'2':dict(value,value=3,drive=True,owned=True,lo=.2,hi=.8)})
  return dict(catalog=catalog,state=state,original_hold=False,animations={'1':dict(phase_source='static',parameters={},parameter=level)})
 async def test_finally_restores_only_changed_scope_and_keeps_shared_drives(self):
  saved=self.saved();heart=FakeHeart(saved);report={}
  with patch.object(verify,'native_values',new=AsyncMock(return_value={'1':{'value':0}})):
   await verify.restore(heart,saved,{10},{1},report)
  self.assertTrue(report['restoration']['complete']);self.assertEqual(report['restoration']['retained_drives'],1)
  self.assertFalse(heart.state['hold']);self.assertEqual(heart.state['values']['1']['value'],0)
  self.assertFalse(heart.state['values']['1']['owned']);self.assertEqual(heart.catalog['layers'][0]['active'],0)
  self.assertFalse(any(c['cmd'] in ('tempo','tap_tempo','downbeat','arm')for c in heart.commands))
  self.assertFalse(any(c.get('id')==2 for c in heart.commands))
 async def test_native_handoff_waits_for_output_tick_and_scalar_settlement(self):
  saved=self.saved();heart=FakeHeart(saved);report={};reads=0;native=0.7;original_animation=heart.animation
  async def delayed_values(ids):
   nonlocal reads,native
   self.assertFalse(heart.state['hold'], 'Numeric writes cannot settle while Heart remains held')
   reads+=1;native=0 if reads>=3 else .7
   return {'1':{'value':native}}
  async def handoff(pid,**data):
   self.assertEqual(native,0,'Ownership released before the queued manual reached native')
   await original_animation(pid,**data)
  heart.animation=handoff
  async def final_values(ids):
   if any(c['cmd']=='animation_set' for c in heart.commands):return {'1':{'value':native}}
   return await delayed_values(ids)
  with patch.object(verify,'native_values',new=final_values):
   await verify.restore(heart,saved,{10},{1},report)
  self.assertEqual(reads,3);self.assertEqual(report['restoration']['scalar_values_settled'],1)
  self.assertEqual(report['restoration']['native_programs_restored'],1)
  self.assertTrue(report['restoration']['complete'])
 async def test_native_animation_is_not_compared_to_an_old_scalar_after_handoff(self):
  saved=self.saved();saved['animations']['1']['phase_source']='timeline'
  heart=FakeHeart(saved);report={};handed_off=False;original_animation=heart.animation
  async def values(ids):
   self.assertFalse(handed_off,'Running native animation must not be checked against a frozen value')
   return {'1':{'value':0}}
  async def animation(pid,**data):
   nonlocal handed_off
   await original_animation(pid,**data);handed_off=True
  heart.animation=animation
  with patch.object(verify,'native_values',new=values):
   await verify.restore(heart,saved,{10},{1},report)
  self.assertTrue(report['restoration']['complete']);self.assertEqual(report['restoration']['level_readback'],{})
 async def test_failed_settlement_keeps_ownership_and_restores_original_hold(self):
  saved=self.saved();saved['original_hold']=True;heart=FakeHeart(saved)
  with patch.object(verify,'native_values',new=AsyncMock(side_effect=RuntimeError('Read interrupted'))):
   with self.assertRaisesRegex(RuntimeError,'Read interrupted'):
    await verify.restore(heart,saved,{10},{1},{})
  self.assertFalse(any(c['cmd']=='animation_set'for c in heart.commands))
  self.assertTrue(heart.state['hold'])
 async def test_stale_epoch_has_no_writes(self):
  saved=self.saved();heart=FakeHeart(saved);heart.catalog['epoch']='replacement'
  with self.assertRaisesRegex(RuntimeError,'stale restoration'):await verify.restore(heart,saved,{10},{1},{})
  self.assertEqual(heart.commands,[])
 async def test_changed_retained_drive_is_reported(self):
  saved=self.saved();heart=FakeHeart(saved);heart.state['values']['2']['hi']=.9
  with patch.object(verify,'native_values',new=AsyncMock(return_value={'1':{'value':0}})):
   with self.assertRaisesRegex(RuntimeError,'Retained drive changed'):await verify.restore(heart,saved,{10},{1},{})

if __name__=='__main__':unittest.main()
