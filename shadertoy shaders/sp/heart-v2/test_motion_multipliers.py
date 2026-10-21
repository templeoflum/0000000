import copy,math,time,unittest
from unittest.mock import patch
from test_stage_motion import engine

class MotionMultiplierTests(unittest.TestCase):
 def set(self,e,scope,value,**identity):e.motion_multiplier(dict(epoch=e.catalog['epoch'],scope=scope,value=value,**identity))
 def test_independent_scopes_multiply_and_preserve_fine_source_setting(self):
  e=engine();before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};bpm=e.bpm
  for scope,value,identity in [('target',.025,{'target':'target:1'}),('global',2,{}),('group',.5,{'group_id':100}),('layer',4,{'layer_id':20}),('stage',.25,{'group_id':100,'section':'rings'})]:self.set(e,scope,value,seconds=0,**identity)
  now=time.perf_counter()+1
  self.assertEqual(e.motion_factor('target:1',now),1)
  self.assertEqual(e.motion_factor('target:2',now),.25)
  self.assertEqual(e.motion_factor('target:3',now),1)
  self.assertEqual(e.motion_factor('target:5',now),2)
  self.assertEqual(e.groups['target:1']['speed'],.025);self.assertEqual(e.bpm,bpm)
  self.assertEqual({pid:sl.cfg for pid,sl in e.slots.items()},before)
  e.selected='target:1';self.assertAlmostEqual(e.state()['values'][1]['motion']['cycles_per_beat'],.025*.025/32)
 def test_one_beat_ease_reverses_from_current_speed_without_phase_reset(self):
  e=engine();e.bpm=120;sl=e.slots[1];sl.phi=.731
  with patch('server.time.perf_counter',return_value=100):self.set(e,'global',4)
  self.assertEqual(e.multiplier_value('global',100),1);self.assertAlmostEqual(e.multiplier_value('global',100.25),2.5);self.assertEqual(e.multiplier_value('global',100.5),4)
  with patch('server.time.perf_counter',return_value=100.25):self.set(e,'global',.025)
  self.assertAlmostEqual(e.multiplier_value('global',100.25),2.5);self.assertEqual(e.multiplier_value('global',100.75),.025);self.assertEqual(sl.phi,.731)
 def test_source_retarget_uses_current_blend_even_when_old_duration_differs(self):
  e=engine();sl=e.slots[1];start=time.perf_counter()+5
  with patch('server.time.perf_counter',return_value=start):self.set(e,'target',4,target='target:1',seconds=2)
  middle=e.source_rate('target:1',start+.5)*sl.blend(start+.5)['x'];phase=sl.phi
  with patch('server.time.perf_counter',return_value=start+.5):self.set(e,'target',.025,target='target:1')
  self.assertAlmostEqual(e.source_rate('target:1',start+.5)*sl.blend(start+.5)['x'],middle);self.assertAlmostEqual(e.source_rate('target:1',start+1)*sl.blend(start+1)['x'],.025*sl.cfg['mult']);self.assertEqual(sl.phi,phase)
 def test_tick_scales_actual_phase_without_scaling_native_ranges_or_hold(self):
  e=engine();now=time.perf_counter()+5;self.set(e,'stage',.025,group_id=100,section='rings',seconds=0)
  before={pid:sl.phi for pid,sl in e.slots.items()};x=e.slots[2].blend(now)['x'];catalog=copy.deepcopy(e.catalog)
  out=e.tick(.01,now)
  self.assertAlmostEqual(e.slots[2].phi-before[2],x*.01*e.bpm/60/32*.025)
  self.assertAlmostEqual(e.slots[3].phi-before[3],e.slots[3].blend(now)['x']*.01*e.bpm/60/32)
  self.assertTrue(all(isinstance(value,dict) and 0<=value['phase']<=1 for pid,value in out));self.assertEqual(e.catalog,catalog)
  phase=e.slots[2].phi;e.hold=True;e.tick(.01,now+.01);self.assertEqual(e.slots[2].phi,phase)
 def test_membership_survives_clip_change_and_reset_on_composition_change(self):
  e=engine();self.set(e,'stage',.5,group_id=100,seconds=0);self.set(e,'layer',.025,layer_id=20,seconds=0)
  c=copy.deepcopy(e.catalog);t=copy.deepcopy(c['targets'][0]);t['id']='new-source';t['kind']='source';t['params'][0]['id']=101;c['targets'].append(t);e.reconcile(c)
  self.assertEqual(e.motion_factor('new-source',time.perf_counter()),.5*.025)
  self.assertEqual(e.motion_scale_keys['new-source'].count('group:100'),1)
  c['epoch']='new';e.reconcile(c);self.assertEqual(e.motion_multipliers,{})
 def test_stale_and_missing_scope_reject_without_changes(self):
  for data in [dict(scope='stage',group_id=100,section='missing'),dict(scope='layer',layer_id=999),dict(scope='group',group_id=999),dict(scope='target',target='missing'),dict(scope='global',epoch='old'),dict(scope='global',value=float('nan'))]:
   e=engine();before=copy.deepcopy(e.groups)
   with self.assertRaises(ValueError):e.motion_multiplier(dict(epoch='stage-test',value=.025)|data)
   self.assertEqual(e.groups,before);self.assertEqual(e.motion_multipliers,{})
  e=engine();e.catalog['groups'][0]['members'].remove(21)
  with self.assertRaises(ValueError):self.set(e,'stage',.5,group_id=100,section='rings')

class StageFamilyTests(unittest.TestCase):
 def family(self,e,pattern,section=None):e.stage_family(dict(epoch=e.catalog['epoch'],group_id=100,section=section,pattern=pattern))
 def test_family_spans_members_preserves_locked_idle_and_manual_parameters(self):
  e=engine();cfg={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};groups=copy.deepcopy(e.groups);catalog=copy.deepcopy(e.catalog)
  self.family(e,3,'rings')
  self.assertEqual([e.slots[pid].cfg['scope_family']['slot'] for pid in (1,2)],[0,1]);self.assertEqual(e.slots[2].target['x'],.5)
  for pid,sl in e.slots.items():
   self.assertEqual({k:v for k,v in sl.cfg.items() if k!='scope_family'},cfg[pid])
   if pid not in (1,2):self.assertNotIn('scope_family',sl.cfg)
  self.assertEqual(e.groups,groups);self.assertEqual(e.catalog,catalog)
  rows={r['section']:r for r in e.stage_motion_state() if r['group_id']==100};self.assertEqual(rows['rings']['pattern'],3);self.assertIsNone(rows[None]['pattern'])
 def test_whole_stage_then_section_family_and_shuffle_preserve_scope(self):
  e=engine();self.family(e,7);self.family(e,3,'rings');before=copy.deepcopy(e.slots[3].cfg)
  with patch('server.random.shuffle',side_effect=lambda xs:xs.reverse()):e.stage_shuffle(dict(epoch='stage-test',group_id=100,section='rings'))
  self.assertEqual([e.slots[pid].cfg['scope_family']['slot'] for pid in (1,2)],[1,0]);self.assertEqual(e.slots[3].cfg,before)
  e.stage_shuffle(dict(epoch='stage-test',group_id=100));self.assertEqual(e.slots[1].cfg['scope_family']['pattern'],3);self.assertEqual(e.slots[3].cfg['scope_family']['pattern'],7)
  self.assertEqual(e.slots[1].cfg['mult'],.025)
 def test_per_parameter_does_not_change_target_family_or_locked_siblings(self):
  e=engine();e.relationship('target:1',dict(pattern=7,seconds=0));before=copy.deepcopy(e.groups);self.family(e,0,'rings')
  self.assertEqual(e.groups,before);self.assertEqual(e.slots[1].cfg['scope_family']['pattern'],0)
  self.assertEqual(e.slots[1].target['x'],e.slots[1].cfg['mult'])
 def test_explicit_source_family_replaces_scope_override_and_exposes_state(self):
  e=engine();self.family(e,7,'rings');e.selected='target:1';self.assertEqual(e.state()['values'][1]['motion']['scope_family']['pattern'],7)
  e.relationship('target:1',dict(pattern=3,seconds=0));self.assertNotIn('scope_family',e.slots[1].cfg);self.assertEqual(e.slots[2].cfg['scope_family']['pattern'],7)
 def test_stale_family_rejects_without_mutation(self):
  e=engine();before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()}
  for data in [dict(epoch='old'),dict(section='missing'),dict(pattern=1.5)]:
   with self.assertRaises(ValueError):e.stage_family(dict(epoch='stage-test',group_id=100,section='rings',pattern=3)|data)
  self.assertEqual({pid:sl.cfg for pid,sl in e.slots.items()},before)

if __name__=='__main__':unittest.main()
