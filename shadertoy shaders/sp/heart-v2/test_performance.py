import copy,tempfile,time,unittest
from pathlib import Path
from server import Engine
from performance import Performance,RATES
from test_launch import catalog

class PerformanceTests(unittest.TestCase):
 def engine(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True;return e
 def layout(self,**control):
  c=dict(id='level',label='Content',kind='continuous',members=[dict(id=10,weight=1),dict(id=11,weight=.5)])
  c.update(control)
  return dict(id='test',name='Performance',controls=[c],inputs=[dict(device='faders',control='one',slot='level')])
 def setup(self,**control):
  e=self.engine();p=e.performance;p.save(self.layout(**control));p.grab('test');return e,p
 def apply(self,e,commands):
  for d in commands:
   if d['cmd']=='manual':e.manual(d['id'],d['value'],owner=d.get('_owner'),duration=d.get('_duration',0))
   elif d['cmd']=='envelope':e.envelope(d['id'],d['direction'],owner=d.get('_owner'))
  e.tick(.016,time.perf_counter()+.05)
 def test_weighted_group_does_not_capture_transient_zero(self):
  e,p=self.setup();e.params[10][1]['value']=e.params[11][1]['value']=0
  self.apply(e,p.event('pad','level','begin',.8));self.assertAlmostEqual(e.lastout[10],.8);self.assertAlmostEqual(e.lastout[11],.4)
  with self.assertRaises(ValueError):p.save(self.layout(members=[dict(id=10),dict(id=11)]))
 def test_pickup_crossing_and_relative_entry(self):
  e,p=self.setup(entry='pickup');self.assertEqual(p.event('midi','level','move',0),[])
  self.apply(e,p.event('midi','level','move',.8));self.assertAlmostEqual(e.lastout[10],.8)
  p.save(self.layout(entry='relative'));p.grab('test');self.apply(e,p.event('pad','level','begin',.1));self.assertAlmostEqual(e.lastout[10],.8)
  self.apply(e,p.event('pad','level','move',.2));self.assertAlmostEqual(e.lastout[10],.9)
 def test_old_spring_cannot_overwrite_new_mouse_or_other_fader(self):
  e,p=self.setup(release='zero',release_time=1)
  self.apply(e,p.event('pad','level','begin',.8));p.event('pad','level','end');e.tick(.1,time.perf_counter()+.1)
  e.manual(10,.9,duration=0);e.tick(.1,time.perf_counter()+.2)
  self.assertAlmostEqual(e.lastout[10],.9);self.assertLess(e.lastout[11],.4)
  self.apply(e,p.event('midi','level','move',.7));e.tick(.5,time.perf_counter()+1);self.assertAlmostEqual(e.lastout[10],.7);self.assertAlmostEqual(e.lastout[11],.35)
 def test_follow_selection_freezes_until_gesture_release(self):
  e,p=self.setup(members=[dict(follow='selection',name='Level')]);e.selected='layer:10'
  self.apply(e,p.event('pad','level','begin',.8));e.selected='source:1';self.apply(e,p.event('pad','level','move',.5));self.assertAlmostEqual(e.lastout[10],.5);self.assertNotIn(101,e.owned)
  p.event('pad','level','end');self.apply(e,p.event('pad','level','begin',.6));self.assertAlmostEqual(e.lastout[101],.6)
 def test_replacement_stays_unresolved_and_blocks_held_contact(self):
  e,p=self.setup(members=[dict(id=101)]);self.apply(e,p.event('pad','level','begin',.8));e.begin_launch(1,2)
  self.assertFalse(p.state()['controls'][0]['ready']);self.assertFalse(p.gestures)
  e.reconcile(catalog(2))
  self.assertEqual(p.event('pad','level','move',.5),[]);self.assertNotIn(102,e.owned)
 def test_button_edges_and_new_owner_prevent_old_release(self):
  e,p=self.setup(kind='button',press=dict(cmd='envelope',id=201,direction='in'),release=dict(cmd='envelope',id=201,direction='out'))
  self.apply(e,p.event('ps4','level','begin',1));self.assertEqual(p.event('ps4','level','move',1),[])
  e.manual(201,.3,duration=0);self.assertEqual(p.event('ps4','level','end'),[])
  self.apply(e,p.event('ps4','level','begin',1));p.grab('test');self.assertEqual(p.event('ps4','level','begin',1),[])
  p.event('ps4','level','end');self.assertTrue(p.event('ps4','level','begin',1))
 def test_save_reopen_keeps_binding_without_a_catalog(self):
  e=self.engine()
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'layouts.json';p=Performance(e,path)
   r=self.layout(kind='button',press=dict(cmd='envelope',id=201,direction='in'));p.save(r)
   blank=Engine();restored=Performance(blank,path);self.assertIn('test',restored.layouts);restored.grab('test');self.assertFalse(restored.state()['controls'][0]['ready'])
   blank.reconcile(catalog());restored.grab('test');self.assertTrue(restored.state()['controls'][0]['ready'])
 def test_rate_intensity_keep_authored_settings_and_phase(self):
  e,p=self.setup(kind='rate',members=[dict(id=11)]);e.slots[11].drive=True;e.owned.add(11);e.slots[11].phi=.7;e.slots[11].cfg.update(lo=.2,hi=.8);e.slots[11].retarget(e.groups['effect:layer'],time.perf_counter())
  cfg=copy.deepcopy(e.slots[11].cfg);group=copy.deepcopy(e.groups['effect:layer']);phase=e.slots[11].phi
  p.event('knob','level','begin',.8);self.assertEqual(e.rate_scale[11],4);self.assertEqual(e.slots[11].phi,phase)
  p.save(self.layout(kind='intensity',members=[dict(id=11)]));p.grab('test');p.event('knob','level','begin',.3)
  self.assertEqual(e.intensity_scale[11],.3);self.assertEqual(e.slots[11].cfg,cfg);self.assertEqual(e.groups['effect:layer'],group)
 def test_multiple_device_bindings_and_disconnect_are_scoped(self):
  e,p=self.setup(release='zero');r=self.layout(release='zero');r['inputs'].append(dict(device='trackpad',control='lane1',slot='level'));p.save(r);p.grab('test')
  self.apply(e,p.input('window',dict(device='faders',control='one',phase='move',value=.7)))
  self.apply(e,p.input('other',dict(device='trackpad',control='lane1',phase='begin',value=.4)))
  p.cancel('window');e.tick(.2,time.perf_counter()+1);self.assertAlmostEqual(e.lastout[10],.4)
  p.cancel('other');e.tick(.2,time.perf_counter()+2);self.assertAlmostEqual(e.lastout[10],0)
 def test_global_hold_new_intent_and_momentary_scope_validation(self):
  e,p=self.setup(kind='button',press=dict(cmd='hold',on=True),release=dict(cmd='hold',on=False))
  action=p.event('ps4','level','begin',1)[0];e.set_hold(action['on'],action['_owner']);e.set_hold(True)
  self.assertEqual(p.event('ps4','level','end'),[])
  action=p.event('ps4','level','begin',1)[0];e.set_hold(action['on'],action['_owner']);self.assertEqual(p.event('ps4','level','end')[0]['on'],False)
  with self.assertRaisesRegex(ValueError,'same control'):p.save(self.layout(kind='button',press=dict(cmd='envelope',id=201,direction='in'),release=dict(cmd='envelope',id=11,direction='out')))
 def test_final_disconnect_finishes_owned_release_endpoints(self):
  e,p=self.setup(kind='button',press=dict(cmd='envelope',id=201,direction='in'),release=dict(cmd='envelope',id=201,direction='out'))
  self.apply(e,p.event('ps4','level','begin',1));commands=p.cancel('ps4',immediate=True);self.assertEqual(commands[0]['cmd'],'manual');self.apply(e,commands);self.assertEqual(e.lastout[201],0)
  e,p=self.setup(release='zero',release_time=1);self.apply(e,p.event('pad','level','begin',.8));p.event('pad','level','end')
  e.manual(10,.6,duration=0);self.apply(e,p.cancel('pad',immediate=True));self.assertEqual(e.lastout[10],.6);self.assertEqual(e.lastout[11],0)
 def test_numeric_toggle_uses_native_endpoints(self):
  e,p=self.setup(kind='button',press=dict(cmd='toggle',id=10));self.apply(e,p.event('ps4','level','begin',1));self.assertEqual(e.lastout[10],1)
  p.event('ps4','level','end');self.apply(e,p.event('ps4','level','begin',1));self.assertEqual(e.lastout[10],0)
