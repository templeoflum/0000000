import unittest
from unittest.mock import patch
import heart
from effect_test_support import ClaimedExecutor
class StrobeTests(unittest.TestCase):
 def setUp(self):
  with patch.object(heart,'load_fx',return_value={}):self.fx=heart.Effect('test','C',None,1,'Strobe',1,2,1)
  for p in (patch.object(heart,'MUTATIONS',ClaimedExecutor()),patch.object(heart,'put')):p.start();self.addCleanup(p.stop)
 def test_hold_is_immediate_and_release_stops_even_with_old_latch_settings(self):
  self.fx.cfg.update(mode='latch',attack=8,release=8);self.fx.press(0,'mouse');self.fx.step(.01,0)
  self.assertEqual(self.fx.env,1);self.assertTrue(self.fx.held)
  self.fx.release('mouse');self.fx.step(.01,0);self.assertEqual(self.fx.env,0);self.assertEqual(self.fx.target,0)
 def test_last_owner_release_stops_and_disconnect_releases(self):
  self.fx.press(0,'a');self.fx.press(0,'b');self.fx.release('a');self.assertEqual(self.fx.target,1)
  self.fx.release();self.assertEqual(self.fx.target,0);self.assertFalse(self.fx.held)
 def test_release_before_claim_finishes_never_flashes_later(self):
  self.fx.press(0,'a');self.fx.release('a');self.fx.step(.01,0);self.assertEqual(self.fx.env,0)
