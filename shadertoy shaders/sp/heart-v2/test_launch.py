"""Clip handoff preserves surviving instruments and fences stale discovery."""
import copy,time,unittest
from server import Engine

def catalog(active=1):
 def target(name,scope,layer,pid,clip=None):
  t=dict(id=name,kind='effect' if 'effect' in name else 'source' if scope=='clip' else 'layer',scope=scope,layer=layer,layer_id=layer*10,params=[dict(id=pid,name='Opacity' if 'effect' in name else 'Level',type='ParamRange',min=0,max=1,value=.2)])
  if clip is not None:t.update(clip=clip,clip_id=100+clip)
  return t
 return dict(type='catalog',epoch='one',layers=[dict(id=10,i=1,active=active,clips=[dict(id=101,col=1),dict(id=102,col=2)]),dict(id=20,i=2,active=1,clips=[dict(id=201,col=1)])],targets=[target('layer:10','layer',1,10),target('effect:layer','layer',1,11),target('source:'+str(active),'clip',1,100+active,active),target('effect:clip'+str(active),'clip',1,110+active,active),target('effect:other','clip',2,201,1)])

class LaunchTests(unittest.TestCase):
 def engine(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True
  for pid in e.slots:e.manual(pid,.6)
  e.envelope(111,'in');e.envelope(201,'in');e.gesture('layer:10','shuffle');e.slots[11].drive=True;e.slots[11].phi=.73
  e.tick(.05,time.perf_counter()+.1);return e
 def test_handoff_keeps_layer_controls_other_envelope_and_output(self):
  e=self.engine();slot=e.slots[11];phase=slot.phi;env=e.envelopes[201];value=e.lastout[201]
  e.begin_launch(1,2)
  self.assertEqual(e.owned,{10,11,201});self.assertIs(e.slots[11],slot);self.assertEqual(slot.phi,phase)
  self.assertIs(e.envelopes[201],env);self.assertEqual(e.lastout[201],value)
  self.assertEqual(set(e.binding()['keep']),{10,11,201});self.assertFalse(e.binding()['reset'])
  self.assertNotIn(101,e.params);self.assertNotIn(111,e.params)
  self.assertEqual(e.catalog['layers'][0]['pending_clip'],2)
 def test_old_scan_cannot_restore_replaced_clip_while_pending(self):
  e=self.engine();e.begin_launch(1,2);e.reconcile(catalog(1))
  self.assertNotIn(101,e.params);self.assertNotIn(111,e.params);self.assertIn(201,e.envelopes)
  with self.assertRaises(ValueError):e.manual(101,.5)
  e.reconcile(catalog(2));self.assertIn(102,e.params);self.assertNotIn(102,e.owned);self.assertFalse(e.slots[102].drive);self.assertFalse(e.launches)
 def test_newest_launch_wins_and_failed_confirmation_recovers_idle(self):
  e=self.engine();e.begin_launch(1,2);e.begin_launch(1,1);e.reconcile(catalog(2));self.assertNotIn(102,e.params)
  e.launches[10]['started']-=11;e.reconcile(catalog(2))
  self.assertIn(102,e.params);self.assertNotIn(102,e.owned);self.assertIn('not confirmed',e.error);self.assertIn(201,e.owned)
 def test_reused_id_or_new_composition_cannot_inherit_output(self):
  e=self.engine();c=catalog();c['targets'][-1]['clip_id']=999
  e.reconcile(c);self.assertNotIn(201,e.owned);self.assertNotIn(201,e.lastout);self.assertNotIn(201,e.retained)
  c['epoch']='two';e.reconcile(c);self.assertFalse(e.owned);self.assertTrue(e.binding()['reset'])
 def test_invalid_launch_does_not_touch_running_state(self):
  e=self.engine();owned=e.owned.copy();slots=e.slots.copy()
  with self.assertRaises(ValueError):e.begin_launch(1,99)
  self.assertEqual(e.owned,owned);self.assertEqual(e.slots,slots)
