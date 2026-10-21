import unittest
from types import SimpleNamespace as N
from unittest.mock import patch
import heart
class HomeFeedbackTests(unittest.TestCase):
 def test_destinations_and_cached_reads(self):
  cases=[(None,{'_adaptive':True,'static':{}},'not captured yet'),(None,{'_adaptive':True,'static':{'Warp':.4}},'captured before Open'),(None,{'static':{'Warp':.4}},'authored rest'),({'sweet_home':True},{'_adaptive':True,'static':{}},'your saved pose')]
  for home,profile,label in cases:
   c=N(home=home)
   with patch.object(heart,'home_profile',return_value=profile) as p:
    self.assertIn(label,heart.home_feedback(c)['label']);heart.home_feedback(c);self.assertEqual(p.call_count,1)
