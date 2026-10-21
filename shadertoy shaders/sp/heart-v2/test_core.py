import unittest,time,copy
from server import Engine
from scan import discover

def catalog(n=2):
 return {'type':'catalog','epoch':'one','layers':[],'targets':[{'id':'source:1','kind':'source','label':'Unmodified shader','params':[dict(id=i,name=str(i),type='ParamFloat',min=-10,max=10,value=0,options=[]) for i in range(n)]}]}
class CoreTests(unittest.TestCase):
 def engine(self,n=2):
  e=Engine();e.reconcile(catalog(n));e.connected=e.armed=True;return e
 def test_manual_native_range_and_disarm(self):
  e=self.engine();e.manual(0,5);v=dict(e.tick(.02,time.perf_counter()+1));self.assertAlmostEqual(v[0],5);e.disarm();self.assertEqual(e.tick(.02,time.perf_counter()),[])
 def test_generic_open_range_and_settle(self):
  e=self.engine();e.gesture('source:1','open');self.assertTrue(all(s.drive for s in e.slots.values()));e.settings('source:1',dict(lo=.2,hi=.8,amount=.5,rate=2));self.assertTrue(all(s.cfg['lo']==.2 for s in e.slots.values()));e.gesture('source:1','settle');self.assertFalse(any(s.drive for s in e.slots.values()))
 def test_replacement_does_not_keep_ownership(self):
  e=self.engine();e.manual(0,5);c=catalog();c['epoch']='two';self.assertTrue(e.reconcile(c));self.assertFalse(e.owned)
 def test_unchanged_catalog_keeps_phase(self):
  e=self.engine();e.slots[0].phi=.62;e.manual(0,3);self.assertFalse(e.reconcile(catalog()));self.assertEqual(e.slots[0].phi,.62);self.assertIn(0,e.owned)
 def test_unknown_nan_and_inverted_range_rejected(self):
  e=self.engine()
  for fn in [lambda:e.manual(99,0),lambda:e.manual(0,float('nan')),lambda:e.settings('source:1',dict(lo=.8,hi=.2))]:
   with self.assertRaises((ValueError,KeyError)):fn()
 def test_hold_and_disconnect_emit_nothing(self):
  e=self.engine();e.gesture('source:1','open');e.hold=True;self.assertEqual(e.tick(.016,time.perf_counter()),[]);e.hold=False;e.connected=False;self.assertEqual(e.tick(.016,time.perf_counter()),[])
 def test_shuffle_does_not_alter_bounds(self):
  e=self.engine();e.settings('source:1',dict(lo=.1,hi=.4));e.gesture('source:1','shuffle','irrational');self.assertEqual(e.slots[0].cfg['hi'],.4);self.assertFalse(e.slots[0].drive)
 def test_discovery_all_layers_and_native_controls(self):
  p={'id':7,'valuetype':'ParamFloat','min':0,'max':1,'value':.5};c={'name':{'id':99},'layers':[{'id':1,'name':{'value':'Any layer'},'video':{},'clips':[{'id':2,'name':{'value':'Any clip'},'connected':{'value':'Connected'},'video':{'sourceparams':{'X':p}}}]}]}
  d=discover(c);self.assertEqual(d['targets'][0]['params'][0]['id'],7);self.assertEqual(d['layers'][0]['active'],1)
if __name__=='__main__':unittest.main()

class ScopeTests(unittest.TestCase):
 def test_open_does_not_activate_effect_opacity(self):
  e=Engine();c=catalog();c['targets'][0]['kind']='effect';c['targets'][0]['params'][0]['name']='Opacity';e.reconcile(c);e.gesture('source:1','open');self.assertFalse(e.slots[0].drive);self.assertTrue(e.slots[1].drive)

class NavigationTests(unittest.TestCase):
 def test_scope_ownership_and_native_clip_controls(self):
  p=lambda i:dict(id=i,valuetype='ParamRange',min=0,max=1,value=.5)
  c={'name':{'id':99},'video':{'opacity':p(1)},'layers':[{'id':2,'name':{'value':'Figure'},'video':{'opacity':p(3)},'clips':[{'id':4,'name':{'value':'Shape'},'connected':{'value':'Connected'},'video':{'opacity':p(5),'sourceparams':{'Spin':p(6)},'effects':[{'id':7,'name':'Cloner','params':{'Amount':p(8)}}]}}]}]}
  d=discover(c);ts={t['id']:t for t in d['targets']}
  self.assertEqual(ts['composition:99']['scope'],'composition')
  self.assertEqual(ts['layer:2']['layer'],1)
  self.assertEqual(ts['clip:4']['params'][0]['id'],5)
  self.assertEqual(ts['effect:7']['scope'],'clip')
  self.assertEqual(ts['effect:7']['clip'],1)
 def test_discrete_only_selection_survives_scan(self):
  c=catalog();c['targets'].append(dict(id='bool',kind='layer',params=[dict(id=99,name='Hidden',type='ParamBoolean',min=0,max=1,value=False,options=[])]))
  e=Engine();e.reconcile(c);e.selected='bool';e.reconcile(c);self.assertEqual(e.selected,'bool')

class HomeTests(unittest.TestCase):
 def test_home_restores_values_ranges_and_drives(self):
  e=Engine();e.reconcile(catalog());e.manual(0,4);e.param_range(1,.2,.7);e.slots[1].drive=True;e.groups['source:1']['speed']=2;e.set_home('source:1')
  e.manual(0,-8);e.param_range(1,0,1);e.slots[1].drive=False;e.groups['source:1']['speed']=8;e.return_home('source:1')
  self.assertEqual(e.slots[0].cfg['manual'],.7) # Home captures a manual edit even before the next output tick
  self.assertEqual(e.slots[1].cfg['lo'],.2);self.assertTrue(e.slots[1].drive);self.assertEqual(e.groups['source:1']['speed'],2)
 def test_range_is_individual_and_home_rejects_changed_contract(self):
  e=Engine();e.reconcile(catalog());e.param_range(0,.1,.8);self.assertEqual(e.slots[1].cfg['lo'],0);e.set_home('source:1');c=catalog();c['targets'][0]['params'][0]['max']=20;e.reconcile(c)
  with self.assertRaises(ValueError):e.return_home('source:1')

class StageTests(unittest.TestCase):
 def test_stage_uses_group_membership_not_layer_names(self):
  p=lambda i:dict(id=i,valuetype='ParamRange',value=.5,min=0,max=1)
  c={'name':{'id':1},'layergroups':[{'id':8,'name':{'value':'__stage__ Test'},'layers':[{'id':3}],'video':{'opacity':p(80)}}],'layers':[{'id':2,'name':{'value':'Portal ordinary'},'video':{'opacity':p(20)},'clips':[]},{'id':3,'name':{'value':'Anything'},'video':{'opacity':p(30)},'clips':[]}]}
  d=discover(c);self.assertIsNone(d['layers'][0]['stage']);self.assertEqual(d['layers'][1]['stage'],8);self.assertEqual(next(t for t in d['targets'] if t['id']=='group:8')['scope'],'stage')
 def test_watched_second_target_does_not_replace_selected(self):
  e=Engine();c=catalog();c['targets'].append(dict(id='layer:2',kind='layer',params=[dict(id=22,name='Level',type='ParamRange',min=0,max=1,value=.8)]));e.reconcile(c);e.selected='source:1';e.watched={'layer:2'};s=e.state();self.assertIn(22,s['values']);self.assertEqual(s['selected'],'source:1')

class SwitchTests(unittest.TestCase):
 def setup_switch(self):
  e=Engine();c=catalog();c['targets'][0]['params'].append(dict(id=90,name='Bypass',type='ParamBoolean',min=0,max=1,value=True,options=[]));e.reconcile(c);return e,c
 def test_switch_feedback_is_immediate_and_old_scan_cannot_revert_it(self):
  e,c=self.setup_switch();e.manual(90,False);self.assertFalse(e.state()['values'][90]['value']);self.assertTrue(e.state()['values'][90]['pending']);e.reconcile(c);self.assertFalse(e.state()['values'][90]['value'])
 def test_old_confirmation_cannot_overwrite_second_click(self):
  e,c=self.setup_switch();e.manual(90,False);old=e.switches[90]['serial'];e.manual(90,True);e.confirm_switch(90,old,False);self.assertTrue(e.state()['values'][90]['value']);e.confirm_switch(90,e.switches[90]['serial'],True);self.assertFalse(e.state()['values'][90]['pending'])
