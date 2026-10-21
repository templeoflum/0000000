"""Actual Arena feedback schema, portable behavior bounds, and one-shot reset delivery."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import heart,feedback
from motion import animated_home

FIXTURE=Path(__file__).resolve().parents[1]/'design/heart-performance-plan/feedback-instrument/arena-candidate.json'
class FeedbackIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.raw=json.loads(FIXTURE.read_text())
  self.c=heart.Clip(0,5,self.raw);self.c.refresh(self.raw)
 def test_real_trigger_is_available_but_not_driven(self):
  self.assertEqual(self.c.atom,'SPHeartFeedback')
  p=self.c.sp['Reset trails'];self.assertEqual(p['valuetype'],'ParamEvent')
  self.assertNotIn('Reset trails',[s.name for s in self.c.slots])
  with patch.object(heart,'arena_post') as post,patch.object(heart,'put') as put:
   heart.manual_parameter(p,True);heart.manual_parameter(p,False)
   post.assert_called_once_with(f"/parameter/by-id/{p['id']}/trigger");put.assert_not_called()
 def test_recreated_effect_uses_new_trigger_id(self):
  for e in self.raw['video']['effects']:
   if e['name']=='SPHeartFeedback':e['params']['Reset trails']['id']=919191
  rebuilt=heart.Clip(0,5,self.raw)
  self.assertEqual(rebuilt.sp['Reset trails']['id'],919191)
 def test_behaviors_stay_in_native_bounds_after_parameter_reordering(self):
  before=heart.capture_state(self.c)
  for name in feedback.BEHAVIORS:
   with self.subTest(name=name):
    profile=feedback.get(name);home=animated_home(before,profile)
    reordered=copy.deepcopy(before);reordered['slots']=dict(reversed(list(reordered['slots'].items())))
    reordered['slots']['Future control']={'config':{'manual':.3},'drive':True,'pose':.3}
    other=animated_home(reordered,profile)
    for sl in self.c.slots:
     item=home['slots'][sl.name];self.assertEqual(item,other['slots'][sl.name])
     self.assertEqual(item['drive'],sl.name in profile['bindings'])
     values=profile['bindings'][sl.name]['range'] if item['drive'] else [item['pose']]
     for value in values:
      actual=heart.slot_out(sl,value)
      self.assertGreaterEqual(actual,sl.pmin);self.assertLessEqual(actual,sl.pmax)
    self.assertFalse(other['slots']['Future control']['drive'])
    self.assertEqual(other['slots']['Future control']['pose'],.3)
    self.assertGreaterEqual(sum(v['drive'] for v in home['slots'].values()),3)

if __name__=='__main__':unittest.main()
