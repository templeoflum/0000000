import unittest,time
from unittest.mock import patch
import heart
class ReadbackTests(unittest.TestCase):
 def setUp(self):
  with patch.object(heart,'load_fx',return_value={}):self.fx=heart.Effect('test','C',0,0,'test',1,2,1.)
 def row(self,bypass,amount):return {'bypassed':{'value':bypass},'params':{'Opacity':{'value':amount}}}
 def test_external_enable_updates_idle_envelope(self):
  self.fx.observe(self.row(False,.7),time.perf_counter());self.assertEqual(self.fx.target,.7);self.assertFalse(self.fx.bypassed)
 def test_bypass_keeps_stored_amount_but_effective_zero(self):
  self.fx.observe(self.row(True,.7),time.perf_counter());self.assertEqual(self.fx.observed_amount,.7);self.assertEqual(self.fx.env,0);self.assertTrue(self.fx.bypassed)
 def test_old_snapshot_cannot_replace_new_gesture(self):
  started=time.perf_counter();self.fx.manual(1);self.fx.observe(self.row(True,0),started);self.assertEqual(self.fx.target,1)
 def test_readback_does_not_interrupt_fade(self):
  self.fx.manual(1);self.fx.env=.4;self.fx.observe(self.row(False,.3),time.perf_counter());self.assertEqual(self.fx.env,.4);self.assertEqual(self.fx.target,1)
 def test_snapshot_before_last_write_cannot_rewind_finished_fade(self):
  started=time.perf_counter();self.fx.output_at=time.perf_counter();self.fx.env=self.fx.target=1
  self.fx.observe(self.row(False,.8),started);self.assertEqual(self.fx.env,1)
 def test_push_protects_against_inflight_poll(self):
  started=time.perf_counter();self.fx.feedback('amount',.8);self.fx.feedback('bypass',False)
  self.fx.observe(self.row(True,0),started)
  self.assertFalse(self.fx.observed_bypassed);self.assertEqual(self.fx.observed_amount,.8)
 def test_push_updates_bypass_both_directions(self):
  self.fx.feedback('amount',.8)
  for bypass in (False,True,False):
   self.fx.feedback('bypass',bypass)
   self.assertEqual(self.fx.bypassed,bypass);self.assertEqual(self.fx.env,0 if bypass else .8)
 def test_echo_does_not_rewind_finished_fade(self):
  self.fx.output_at=time.perf_counter();self.fx.env=self.fx.target=1
  self.fx.feedback('amount',.95);self.fx.feedback('bypass',False)
  self.assertEqual(self.fx.env,1);self.assertEqual(self.fx.observed_amount,.95)
 def test_replaced_effect_does_not_receive_old_subscription(self):
  with patch.dict(heart.FX,{'test':object()}):
   heart.effect_feedback({'type':'parameter_update','id':2,'value':True},{2:(self.fx,'bypass')})
  self.assertFalse(hasattr(self.fx,'observed_bypassed'))
 def test_delayed_echo_cannot_change_requested_endpoint(self):
  self.fx.manual(1);self.fx.claim_needed=False;self.fx.env=1;self.fx.output_at=time.perf_counter()-1
  self.fx.feedback('bypass',False);self.fx.feedback('amount',.915)
  self.assertEqual(self.fx.target,1);self.assertTrue(self.fx.awaiting_output)
  self.fx.feedback('amount',1)
  self.assertFalse(self.fx.awaiting_output);self.assertEqual(self.fx.env,1)
 def test_delayed_poll_cannot_change_requested_endpoint(self):
  self.fx.manual(1);self.fx.env=1;self.fx.output_at=time.perf_counter()-1
  self.fx.observe(self.row(False,.915),time.perf_counter())
  self.assertEqual(self.fx.target,1)
 def test_bypass_at_zero_disabled_does_not_prevent_enable(self):
  from effect_test_support import ClaimedExecutor
  self.fx.cfg['bypass0']=False;self.fx.bypassed=True;self.fx.manual(1)
  with patch.object(heart,'MUTATIONS',ClaimedExecutor()),patch.object(heart,'put') as put:
   self.fx.step(.5,0);self.fx.step(.5,0)
   self.assertIn(((2,False),),[ (c.args,) for c in put.call_args_list])
