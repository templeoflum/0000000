import unittest,math
from modulation import Bank
class BankTests(unittest.TestCase):
 def setUp(self):self.b=Bank();self.b.configure('shared',1,0)
 def test_fanout_same_signal_evaluated_once(self):
  for i in range(20):self.b.bind(str(i),'shared',i,0,0,0)
  self.b.advance(.25,1)
  self.assertEqual({self.b.value(str(i),i,1) for i in range(20)},{.5-.5*math.cos(math.pi/2)})
  self.assertEqual(self.b.generators['shared']['phase'],.25)
 def test_unbound_clock_survives_reassignment(self):
  self.b.bind('source','shared',1,0,0,0);self.b.advance(.25,1);self.b.remove('source');self.b.advance(.25,2)
  self.b.bind('source','shared',2,.3,2,0)
  self.assertEqual(self.b.generators['shared']['phase'],.5);self.assertEqual(self.b.value('source',2,2),1)
 def test_old_instance_never_receives_reassigned_route(self):
  self.b.bind('r','shared',1,0,0);self.b.bind('r','shared',2,0,0)
  self.assertIsNone(self.b.value('r',1,1));self.assertIsNotNone(self.b.value('r',2,1))
 def test_rate_change_keeps_phase(self):
  self.b.advance(.25,1);self.b.configure('shared',-1,1,1)
  self.assertEqual(self.b.generators['shared']['phase'],.25)
  self.b.advance(0,1);self.assertEqual(self.b.generators['shared']['rate'],1)
  self.b.advance(0,2);self.assertEqual(self.b.generators['shared']['rate'],-1)
 def test_join_starts_at_current_value(self):
  self.b.advance(.5,1);self.b.bind('r','shared',1,.2,1,1)
  self.assertAlmostEqual(self.b.value('r',1,1),.2);self.assertAlmostEqual(self.b.value('r',1,2),1)
 def test_count_change_does_not_change_phase_or_rate(self):
  self.b.advance(.3,1);g=dict(self.b.generators['shared'])
  self.b.bind('a','shared',1,0,1);self.b.bind('b','shared',2,0,1);self.b.remove('a')
  self.assertEqual(g,self.b.generators['shared'])
 def test_missing_route_visible(self):
  self.b.bind('r','shared',1,0,0)
  self.assertEqual(self.b.snapshot(set())['routes']['r']['status'],'unassigned')
 def test_invalid_before_mutation(self):
  with self.assertRaises(ValueError):self.b.configure('shared',float('nan'),1)
  with self.assertRaises(ValueError):self.b.bind('r','missing',1,0,0)
  self.assertEqual(len(self.b.generators),1);self.assertFalse(self.b.routes)
 def test_transform_belongs_to_route(self):
  self.b.advance(.5,1);self.b.bind('r','shared',1,0,1,0,.2,.7)
  self.assertAlmostEqual(self.b.value('r',1,1),.7);self.assertEqual(self.b.generators['shared']['value'],1)
