import unittest
from types import SimpleNamespace
from boolean_hold import BooleanHolds
class HoldTests(unittest.TestCase):
 def setUp(self):
  self.p=dict(id=7,valuetype='ParamBoolean',value=False);self.fx=SimpleNamespace(params={'MELT_LOCK':self.p});self.valid=True;self.writes=[]
  self.h=BooleanHolds(lambda f,p:self.valid,lambda p,v:self.writes.append(v))
 def test_hold_and_release(self):
  self.h.press(self.fx,'MELT_LOCK',1);self.h.release(7,1);self.assertEqual(self.writes,[True,False])
 def test_latched_baseline_survives(self):
  self.p['value']=True;self.h.press(self.fx,'MELT_LOCK',1);self.h.release_owner(1);self.assertEqual(self.writes,[True,True])
 def test_later_latch_edit_wins(self):
  self.h.press(self.fx,'MELT_LOCK',1);self.h.supersede(self.p);self.h.release(7,1);self.assertEqual(self.writes,[True])
 def test_disconnect_does_not_release_other_owner(self):
  self.h.press(self.fx,'MELT_LOCK',1);self.h.press(self.fx,'MELT_LOCK',2);self.h.release_owner(1);self.assertEqual(self.writes,[True,True]);self.h.release_owner(2);self.assertEqual(self.writes[-1],False)
 def test_replacement_is_never_written_on_release(self):
  self.h.press(self.fx,'MELT_LOCK',1);self.valid=False;self.h.release_owner(1);self.assertEqual(self.writes,[True])
 def test_event_cannot_be_held(self):
  self.p['valuetype']='ParamEvent'
  with self.assertRaises(ValueError):self.h.press(self.fx,'MELT_LOCK',1)
