import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch
import heart
from delivery import LatestValues

class ScanDeliveryTests(unittest.TestCase):
 def test_unchanged_scan_preserves_pending_manual_and_generation(self):
  s=NS(ids={'':42},_lastv=.7,_lastout=.7);c=NS(slots=[s]);out=LatestValues();out.put((42,.7))
  with patch.object(heart,'CLIPS',{(0,0):c}),patch.object(heart,'OUT',out),patch.object(heart,'FX',{}),patch.object(heart,'SLOT_WRITERS',{}):
   heart.publish_discovered_clips({(0,0):c})
   self.assertEqual(out.generation,0);self.assertEqual(out.take(),[(42,.7)])
   self.assertIs(heart.CLIPS[(0,0)],c)
 def test_replacement_discards_stale_but_invalidates_survivor_cache(self):
  s=NS(ids={'':42},_lastv=.7,_lastout=.7);survivor=NS(slots=[s]);old=NS(slots=[NS(ids={'':43})]);new=NS(slots=[NS(ids={'':44})]);out=LatestValues();out.put((42,.7));out.put((43,.9))
  with patch.object(heart,'CLIPS',{(0,0):survivor,(1,0):old}),patch.object(heart,'OUT',out),patch.object(heart,'FX',{}),patch.object(heart,'SLOT_WRITERS',{}):
   heart.publish_discovered_clips({(0,0):survivor,(1,0):new})
   self.assertEqual(out.generation,1);self.assertEqual(out.take(),[])
   self.assertIsNone(s._lastout);self.assertEqual(s._lastv,9.)
   self.assertNotIn(43,heart.SLOT_WRITERS);self.assertIn(44,heart.SLOT_WRITERS)
