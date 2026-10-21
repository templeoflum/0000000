import unittest
import heart

class RangeStartTests(unittest.TestCase):
 def slot(self):
  s=heart.Slot('Num X',False);s.index=0;s.cfg=dict(manual=15/99999,ratio='1:1',mult=1.,offset=0.,shape=1,lo=0.,hi=1.)
  g=dict(pattern=0,seed=0,spread=1,depth=1.,fm=0.)
  s.retarget(g,0);return s,g
 def test_start_uses_new_limits_without_wide_range_excursion(self):
  s,g=self.slot();s.cfg.update(lo=7/99999,hi=31/99999);s.retarget(g,1)
  s.drive=True;s.retarget(g,1.001)
  values=[]
  for i in range(301):
   e=s.step(.002,1.001+i*.01);values.append(1+99999*s.value(e))
  self.assertGreaterEqual(min(values),8-1e-6);self.assertLessEqual(max(values),32+1e-6)
  self.assertAlmostEqual(values[0],16.)
 def test_running_range_still_morphs_continuously(self):
  s,g=self.slot();s.drive=True;s.retarget(g,0);s.prev=s.target;s.phi=.25
  before=s.value(s.blend(4));s.cfg.update(lo=.2,hi=.3);s.retarget(g,4)
  self.assertAlmostEqual(s.value(s.blend(4)),before)
  self.assertAlmostEqual(s.blend(7)['hi'],.3)
 def test_fading_drive_off_does_not_snap_limits(self):
  s,g=self.slot();s.drive=True;s.retarget(g,0);s.prev=s.target
  s.drive=False;s.retarget(g,4);s.cfg.update(lo=.1,hi=.2);s.retarget(g,4.1)
  self.assertGreater(s.prev['drive'],0);self.assertGreater(s.prev['hi'],.9)
