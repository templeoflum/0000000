import copy,time,unittest
from scan import discover
from server import Engine
from test_launch import catalog

class PlayingTests(unittest.TestCase):
 def test_drive_starts_at_native_value_and_stops_at_scaled_output(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True;pid=201;sl=e.slots[pid]
  e.native_values(e.epoch,[(pid,.76)]);e.param_range(pid,.2,.8);e.drive(pid,True)
  self.assertAlmostEqual(sl.cfg['manual'],.76);self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(.2,.8))
  e.intensity_scale[pid]=.35;e.tick(.04,time.perf_counter()+1);last=e.lastout[pid];e.drive(pid,False)
  self.assertAlmostEqual(sl.cfg['manual'],last);e.tick(.04,time.perf_counter()+2);self.assertAlmostEqual(e.lastout[pid],last)
  e.native_values(e.epoch,[(pid,.32)]);e.drive(pid,True);self.assertAlmostEqual(sl.cfg['manual'],.32)
 def test_motion_readout_uses_effective_family_rate_and_musical_scale(self):
  e=Engine();e.reconcile(catalog());e.selected=e.params[201][0];e.relationship(e.selected,dict(pattern=1,seconds=0));e.settings(e.selected,dict(rate=2));e.parameter_motion(201,dict(mult=-2,seconds=0));e.rate_scale[201]=4
  self.assertAlmostEqual(e.state()['values'][201]['motion']['cycles_per_beat'],-.5)
 def test_native_values_follow_external_edits_and_reject_old_bindings(self):
  e=Engine();e.reconcile(catalog());e.watched={e.params[201][0]};old=e.epoch
  e.native_values(old,[(201,.72)]);self.assertEqual(e.state()['values'][201]['value'],.72)
  e.native_values('stale',[(201,.01)]);self.assertEqual(e.state()['values'][201]['value'],.72)
  e.manual(201,.4);e.native_values(e.epoch,[(201,.61)]);self.assertEqual(e.state()['values'][201]['value'],.61)
  changed=catalog();next(p for t in changed['targets'] for p in t['params'] if p['id']==201)['name']='Replacement'
  e.reconcile(changed);self.assertNotIn(201,e.observed);e.native_values(old,[(201,.99)]);self.assertNotIn(201,e.observed)
 def test_amount_and_rate_preserve_individual_ranges(self):
  e=Engine();e.reconcile(catalog());e.param_range(201,.2,.6);target=e.params[201][0]
  e.settings(target,dict(amount=.5,rate=2));self.assertEqual((e.slots[201].cfg['lo'],e.slots[201].cfg['hi']),(.2,.6))
  e.settings(target,dict(hi=.8));self.assertEqual(e.slots[201].cfg['lo'],.2)
  with self.assertRaises(ValueError):e.settings(target,dict(lo=.9,amount=.1))
  self.assertEqual(e.groups[target]['depth'],.5)
 def test_nullable_source_and_authoritative_active_clip(self):
  level=lambda i:dict(id=i,valuetype='ParamRange',min=0,max=1,value=.5)
  clips=[dict(id=i,name={'value':str(i)},connected={'value':'Connected'},video={'opacity':level(i+10),'sourceparams':None,'effects':None}) for i in (1,2)]
  composition={'name':{'id':90},'video':None,'layergroups':None,'layers':[{'id':30,'name':{'value':'Layer'},'video':{'opacity':level(99)},'clips':clips,'active_clip':clips[0]}]}
  result=discover(composition)
  self.assertEqual(result['layers'][0]['active'],1)
  self.assertIn('clip:1',[t['id'] for t in result['targets']]);self.assertNotIn('clip:2',[t['id'] for t in result['targets']])
  composition['layers'][0]['active_clip']=None
  self.assertEqual(discover(composition)['layers'][0]['active'],0)
 def test_colors_are_typed_preserve_alpha_and_reject_invalid_values(self):
  c=catalog();c['targets'][0]['params'].append(dict(id=99,name='Color',type='ParamColor',value='#11223344',min=0,max=1,options=[]))
  e=Engine();e.reconcile(c)
  self.assertEqual(e.manual(99,'#abcdef'),'#abcdef44');self.assertNotIn(99,e.slots)
  self.assertEqual(e.manual(99,'#abcdef88'),'#abcdef88')
  for bad in ('red','#gggggg',True,4):
   with self.assertRaises(ValueError):e.manual(99,bad)
 def test_eject_handoff_retains_other_layer_motion_and_waits_for_native_clear(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True;e.manual(11,.3);e.slots[11].drive=True;e.manual(201,.6)
  e.begin_launch(1,0);self.assertNotIn(101,e.params);self.assertIn(201,e.params)
  e.reconcile(catalog());self.assertNotIn(101,e.params);self.assertEqual(e.catalog['layers'][0]['pending_clip'],0)
  cleared=catalog();cleared['layers'][0]['active']=0;cleared['targets']=[t for t in cleared['targets'] if not(t.get('scope')=='clip' and t.get('layer')==1)]
  e.reconcile(cleared);self.assertFalse(e.launches);self.assertTrue(e.slots[11].drive);self.assertIn(201,e.owned)
 def test_relationship_changes_preserve_phase_and_authored_ranges(self):
  e=Engine();e.reconcile(catalog());sl=e.slots[201];sl.phi=.73;e.param_range(201,.2,.6);before=copy.deepcopy(sl.cfg)
  e.relationship(e.params[201][0],dict(pattern=10,spread=2,seed=3,fm=.4))
  self.assertEqual(sl.phi,.73);self.assertEqual(sl.cfg,before)
  e.parameter_motion(201,dict(ratio='3:2',mult=-2,offset=.25,shape=.4))
  self.assertEqual(sl.phi,.73);self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(.2,.6));self.assertEqual(sl.cfg['mult'],-2)
  with self.assertRaises(ValueError):e.relationship(e.params[201][0],dict(spread=.5))
  with self.assertRaises(ValueError):e.parameter_motion(201,dict(ratio='unknown'))
 def test_momentary_link_release_cannot_overwrite_newer_intent(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True
  e.play_actions.begin('window','linked',[111,201]);e.manual(111,.4)
  releases=e.play_actions.release('window','linked');self.assertEqual([a['id'] for a in releases],[201])
  self.assertEqual(e.play_actions.release('window','linked'),[])
  e.play_actions.begin('window','linked',[111,201]);e.begin_launch(1,2)
  releases=e.play_actions.release('window',immediate=True);self.assertEqual([a['id'] for a in releases],[201]);self.assertEqual(releases[0]['cmd'],'manual');self.assertEqual(releases[0]['value'],0)
 def test_link_validation_is_all_or_nothing(self):
  e=Engine();e.reconcile(catalog())
  with self.assertRaises(ValueError):e.play_actions.begin('w','link',[111,999999])
  self.assertFalse(e.envelopes);self.assertFalse(e.play_actions.held)
