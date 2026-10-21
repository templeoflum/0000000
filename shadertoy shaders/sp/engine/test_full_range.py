import unittest,copy
from unittest.mock import patch
import heart
from test_performance_motion import EffectMotionTests
class FullRangeTests(unittest.TestCase):
 def setUp(self):
  f=EffectMotionTests();f.setUp();self.addCleanup(f.doCleanups);self.c=f.c;self.fx=f.fx;self.fx.bypassed=True
  p=patch.object(heart,'current_controller',return_value=True);p.start();self.addCleanup(p.stop)
 def test_full_range_preserves_motion_ownership_and_effect(self):
  sl,discrete=self.c.slots;sl.cfg.update(lo=.3,hi=.6,lock=True);sl.phi=.42;sl.drive=False
  before=copy.deepcopy(sl.cfg);discrete_before=copy.deepcopy(discrete.cfg);effect=(self.fx.target,self.fx.env,self.fx.bypassed)
  heart.full_range([self.c])
  self.assertEqual(sl.cfg,dict(before,lo=0.,hi=1.));self.assertFalse(sl.drive);self.assertEqual(sl.phi,.42);self.assertEqual(sl.owner,'unverified')
  self.assertEqual(discrete.cfg,discrete_before);self.assertEqual((self.fx.target,self.fx.env,self.fx.bypassed),effect)
  self.c.refresh(self.fx);self.assertEqual((self.c.slots[0].cfg['lo'],self.c.slots[0].cfg['hi']),(0.,1.))
 def test_open_starts_all_numeric_drives_without_enabling_effect(self):
  sl=self.c.slots[0];sl.cfg.update(lo=.2,hi=.4);heart.open_motion(self.c)
  self.assertTrue(all(x.drive for x in self.c.slots));self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(0.,1.));self.assertTrue(self.fx.bypassed)
 def test_shared_range_and_shuffle_preserve_drive_and_effect_state(self):
  sl=self.c.slots[0];sl.drive=True
  heart.live_gesture([self.c],'range',[.2,.8]);self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(.2,.8))
  heart.live_gesture([self.c],'shuffle','unison');self.assertEqual(sl.cfg['ratio'],'1:1');self.assertTrue(sl.drive);self.assertTrue(self.fx.bypassed)
 def test_home_rests_without_recalling_a_clip_recipe(self):
  sl=self.c.slots[0];sl.drive=True;sl.retarget(self.c.g,0)
  with patch.object(heart,'home_profile',side_effect=AssertionError('recipe read')):
   heart.live_gesture([self.c],'home')
  self.assertFalse(sl.drive)
 def test_geometry_guard_only_on_figure_transform(self):
  self.c.effect_key=heart.figure_guard.CLONER;self.assertIsNone(heart.guard_context(self.c))
if __name__=='__main__':unittest.main()
