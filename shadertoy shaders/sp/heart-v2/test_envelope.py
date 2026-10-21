import unittest,copy
from server import Engine
class EnvelopeTests(unittest.TestCase):
 def engine(self):
  e=Engine();e.reconcile(dict(type='catalog',epoch='one',layers=[],targets=[dict(id='effect:1',kind='effect',params=[dict(id=1,name='Opacity',type='ParamRange',min=0,max=1,value=0)])]));e.armed=e.connected=True;e.envelope_config(1,dict(curve='linear',in_time=2,out_time=4));return e
 def step(self,e,dt):return dict(e.tick(dt,100))
 def test_reverse_and_same_direction_retrigger_and_hold(self):
  e=self.engine();e.envelope(1,'in');self.assertAlmostEqual(self.step(e,.5)[1],.25)
  e.envelope(1,'out');self.assertEqual(e.envelopes[1]['start'],.25);self.assertAlmostEqual(self.step(e,.5)[1],.125)
  e.envelope(1,'out');self.assertEqual(e.envelopes[1]['start'],1);self.assertAlmostEqual(self.step(e,1)[1],.75)
  self.assertEqual(self.step(e,3)[1],0);self.assertEqual(self.step(e,2),{});self.assertEqual(e.envelopes[1]['progress'],1)
  e.envelope(1,'out');self.assertEqual(e.envelopes[1]['start'],1)
 def test_hold_freezes_and_disarm_cancels(self):
  e=self.engine();e.envelope(1,'in');self.step(e,.5);e.hold=True;self.step(e,5);self.assertEqual(e.envelopes[1]['elapsed'],.5);e.hold=False;self.assertAlmostEqual(self.step(e,.5)[1],.5);e.disarm();self.assertFalse(e.envelopes);self.assertFalse(self.step(e,1))
 def test_curves_endpoints_and_settings_apply_next_trigger(self):
  for curve in ['linear','smooth','ease-in','ease-out']:
   e=self.engine();e.envelope_config(1,dict(low=.2,high=.8,curve=curve));e.envelope(1,'in');e.envelope(1,'in');v=self.step(e,1)[1];self.assertGreater(v,.2);self.assertLess(v,.8);e.envelope_config(1,dict(high=.5));self.assertAlmostEqual(self.step(e,2)[1],.8)
 def test_manual_and_replacement_cancel(self):
  e=self.engine();e.envelope(1,'in');self.step(e,.5);e.manual(1,.7);self.assertFalse(e.envelopes)
  e.envelope(1,'in');c=copy.deepcopy(e.catalog);c['epoch']='two';e.reconcile(c);self.assertFalse(e.envelopes);self.assertFalse(e.envelope_settings);self.assertFalse(e.owned)
 def test_invalid_commands_leave_envelope_unchanged(self):
  e=self.engine();e.envelope(1,'in');before=copy.deepcopy(e.envelopes)
  for d in [dict(low=.8,high=.2),dict(curve='bad'),dict(in_time=float('nan'))]:
   with self.assertRaises(ValueError):e.envelope_config(1,d)
  with self.assertRaises(ValueError):e.envelope(1,'wrong')
  self.assertEqual(e.envelopes,before)
  e.params[1][1]['name']='Other'
  with self.assertRaises(ValueError):e.envelope(1,'in')
