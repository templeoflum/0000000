import unittest
from unittest.mock import patch
import heart
from effect_test_support import ClaimedExecutor
class DirectionTests(unittest.TestCase):
 def setUp(self):
  with patch.object(heart,'load_fx',return_value={}):self.fx=heart.Effect('test','C',None,1,'test',1,2,1)
  for p in (patch.object(heart,'MUTATIONS',ClaimedExecutor()),patch.object(heart,'put')):p.start();self.addCleanup(p.stop)
 def finish(self):
  for _ in range(250):self.fx.step(.01,0)
 def test_in_holds_even_with_old_oneshot_config(self):
  self.fx.cfg['mode']='oneshot';self.fx.direction(1);self.finish();self.assertEqual((self.fx.env,self.fx.target),(1,1));self.assertIsNone(self.fx.pulse_state)
 def test_out_holds_zero(self):
  self.fx.env=self.fx.target=1;self.fx.direction(0);self.finish();self.assertEqual((self.fx.env,self.fx.target),(0,0))
 def test_same_direction_retriggers_from_opposite_endpoint(self):
  for value in (0,1):
   self.fx.env=self.fx.target=value;self.fx.direction(value);self.assertEqual(self.fx.env,1-value);self.finish();self.assertEqual(self.fx.env,value)
 def test_midfade_reverse_keeps_current_level(self):
  self.fx.env=.4;self.fx.target=1;self.fx.direction(0);self.assertEqual(self.fx.env,.4);self.assertEqual(self.fx.target,0)
 def test_same_direction_during_fade_does_not_jump(self):
  self.fx.env=.4;self.fx.target=1;self.fx.direction(1);self.assertEqual(self.fx.env,.4)
