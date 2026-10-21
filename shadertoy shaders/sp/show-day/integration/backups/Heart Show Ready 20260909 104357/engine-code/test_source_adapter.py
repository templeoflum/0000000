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
