import tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as N
import source_adapter as a

def slot(name,**kw):return N(name=name,**dict(dict(kind='ParamRange',pmin=0.,pmax=1.,owner='heart'),**kw))
def clip(*slots,role='field'):return N(name='Example',atom=None,role=role,layer=3,col=20,slots=list(slots))
class AdapterTests(unittest.TestCase):
 def test_selection_skips_dangerous_and_external_inputs(self):
  c=clip(slot('seed'),slot('Speed'),slot('Camera Distance'),slot('warp'),slot('glow'),slot('width'),slot('offset'),slot('morph',owner='resolume'))
  self.assertEqual(a.selected(c),{'warp','glow','width'})
 def test_figure_placement_stays_external(self):
  c=clip(slot('Scale'),slot('X'),slot('morph'),role='figure');self.assertEqual(a.selected(c),{'morph'})
 def test_native_ranges_do_not_change_relationship_settings(self):
  s=slot('warp',pmin=-900,pmax=1800);c=clip(s);r=a.settings(c,s,.02)
  self.assertEqual(r['lo'],0);self.assertAlmostEqual(r['hi'],.17)
  self.assertFalse({'ratio','mult','shape','offset'} & r.keys())
 def test_speed_only_does_not_fake_structural_motion(self):
  s=slot('Speed');self.assertFalse(a.settings(clip(s),s,.3)['drive'])
 def test_saved_pose_survives_reload_but_schema_changes_do_not_reuse_it(self):
  with tempfile.TemporaryDirectory() as d:
   p=str(Path(d)/'homes.json');c=clip(slot('warp'));h=a.Homes(p)
   self.assertTrue(h.remember(c,{'slots':{'warp':{'pose':.4}}}))
   self.assertFalse(h.remember(c,{'slots':{'warp':{'pose':.8}}}))
   self.assertEqual(a.Homes(p).profile(c),{'warp':.4})
   c.slots[0].pmax=2;self.assertEqual(h.profile(c),{})
 def test_invalid_and_integer_controls_are_parked(self):
  for s in [slot('density',integer=True),slot('width',pmax=float('nan')),slot('toggle',kind='ParamBoolean')]:self.assertFalse(a.settings(clip(s),s,.4)['drive'])
 def test_events_and_non_scalar_parameters_cannot_displace_numeric_controls(self):
  c=clip(slot('Shuffle Timing',kind='ParamEvent'),slot('Color 1',kind='ParamColor'),slot('warp',kind='ParamText'),slot('width'),slot('hue',kind='ParamFloat'),slot('offset'))
  self.assertEqual(a.selected(c),{'width','hue','offset'})
  self.assertEqual(a.classify(c.slots[0]),'discrete')
  for s in c.slots[1:3]:
   self.assertEqual(a.classify(s),'unsupported')
   self.assertEqual(a.settings(c,s,.4),{'drive':False,'manual':.4})
 def test_legacy_untyped_and_native_scalar_slots_keep_their_selection(self):
  legacy=N(name='morph',pmin=0.,pmax=1.,owner='heart')
  self.assertEqual(a.selected(clip(legacy,slot('glow',kind='ParamFloat'),slot('offset',kind=''))),{'morph','glow','offset'})
 def test_camel_case_and_numbered_clocks_and_cameras_stay_parked(self):
  for name in ('spinRate','foldRate','animationSpeed','speed2','time2Scale'):
   self.assertEqual(a.classify(slot(name)),'clock',name)
  for name in ('camX','camY','camZ','camera2Position','FOV2','cam2X'):
   self.assertEqual(a.classify(slot(name)),'framing',name)
  for name in ('sizeOffset','torusSize'):
   self.assertEqual(a.classify(slot(name),'figure'),'framing',name)
 def test_tokenization_preserves_structural_offsets_and_quaternion_controls(self):
  c=clip(slot('spinRate'),slot('camX'),slot('sizeOffset'),slot('offset'),slot('Quat W'),slot('foldAmount2'),role='figure')
  self.assertEqual(a.selected(c),{'offset','Quat W','foldAmount2'})
  for name in ('offset','offset2','Quat W','QuatW'):
   self.assertEqual(a.classify(slot(name),'figure'),'continuous',name)
