import unittest, tempfile, copy, json
from pathlib import Path
from unittest.mock import patch
import heart
from delivery import LatestValues

class DeliveryTests(unittest.TestCase):
 def test_latest_and_fair(self):
  q=LatestValues();q.put((1,0));q.put((2,2))
  for i in range(10000): q.put((1,i))
  self.assertEqual(q.qsize(),2);self.assertEqual(q.take(),[(1,9999),(2,2)])
 def test_output_rate_and_final_value(self):
  q=LatestValues()
  with patch('delivery.time.perf_counter',return_value=10):
   q.put((1,.2));self.assertEqual(q.take(),[(1,.2)])
   q.put((1,.3));q.put((1,.4));self.assertEqual(q.take(),[])
   q.put((2,False));self.assertEqual(q.take(),[(2,False)])
  with patch('delivery.time.perf_counter',return_value=10.02):
   self.assertEqual(q.take(),[(1,.4)])
 def test_bounded_disconnect(self):
  q=LatestValues(2)
  for i in range(20):q.put((i,i))
  self.assertEqual(q.qsize(),2);q.clear();self.assertEqual(q.take(),[])

class StateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.patches=[patch.object(heart,'ATOM_FILE',str(Path(self.tmp.name)/'atoms.json')),patch.object(heart,'MOTION_FILE',str(Path(self.tmp.name)/'motion.json')),patch.object(heart,'MOTION',{}),patch.object(heart,'put_http'),patch.object(heart,'event')]
  for p in self.patches:p.start();self.addCleanup(p.stop)
  self.c=type('ClipStub',(),{})();c=self.c;c.name='test';c.atom='test';c.gids={};c.g={'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.};c.history=[]
  heart.ATOMS['test']={'_global':dict(c.g)}
  sl=heart.Slot('X',False);sl.index=0;sl.ids={'':42};sl.shape_opts=['loop','sway'];sl.acfg={'lo':0.2,'hi':0.8};heart.ATOMS['test']['X']=sl.acfg
  sl.cfg={'manual':0.5,'drive':False,'ratio':'1:2','mult':1,'offset':0.,'shape':1,'lo':0.2,'hi':0.8,'lock':False};sl.drive=False;sl.retarget(c.g,0);c.slots=[sl]
 def test_automatic_home_does_not_override_motion_profile(self):
  home_path=str(Path(self.tmp.name)/'home.json')
  with patch.object(heart,'HOME_FILE',home_path):
   heart.set_home(self.c,False)
   self.assertFalse(json.loads(Path(home_path).read_text())['test']['sweet_home'])
   heart.set_home(self.c)
   self.assertTrue(json.loads(Path(home_path).read_text())['test']['sweet_home'])
 def test_reconnect_preserves_motion_and_clears_pending_values(self):
  before=heart.capture_state(self.c)
  with patch.object(heart,'OUT',LatestValues()),patch.dict(heart.STATE,{'arena_connected':True}):
   heart.OUT.put((42,.9));heart.request_reconnect()
   self.assertFalse(heart.STATE['arena_connected']);self.assertEqual(heart.OUT.qsize(),0)
   self.assertTrue(heart.RECONNECT.is_set());self.assertTrue(heart.RESCAN.is_set())
   self.assertEqual(heart.capture_state(self.c),before)
  heart.RECONNECT.clear();heart.RESCAN.clear()
 def test_atom_roundtrip(self):
  c=self.c;h=heart.capture_state(c);c.g['depth']=.1;c.slots[0].cfg['lo']=.7;c.slots[0].drive=True
  heart.apply_state(c,h)
  self.assertEqual(c.g['depth'],1.);self.assertEqual(c.slots[0].cfg['lo'],.2);self.assertFalse(c.slots[0].drive)
  heart.put_http.assert_not_called()
 def test_overlapping_returns(self):
  c=self.c;base=heart.capture_state(c);a=copy.deepcopy(base);a['slots']['X']['pose']=.7;b=copy.deepcopy(base);b['slots']['X']['pose']=.9
  with patch.object(heart,'load_presets',return_value={'test':{'1':a,'2':b}}):
   heart.preset_mom(c,1,True);heart.preset_mom(c,2,True);heart.preset_mom(c,1,False)
   self.assertEqual(c.slots[0].cfg['manual'],.9)
   heart.preset_mom(c,2,False);self.assertEqual(c.slots[0].cfg['manual'],.5)
 def test_range_and_undo(self):
  c=self.c;heart.fire(c,seed=4,arm={'global':set(),'slots':{'X':{'range'}}})
  cfg=c.slots[0].acfg;self.assertTrue(.2<=cfg['lo']<cfg['hi']<=.8)
  heart.undo(c);self.assertEqual(c.slots[0].cfg['lo'],.2)
 def test_release_cancels_quantized_press(self):
  with patch.object(heart,'load_fx',return_value={}):e=heart.Effect('x','L',1,1,'test',1,2,1.)
  e.cfg.update(mode='momentary',quant=1);e.press(0);e.release();e.step(.1,1)
  self.assertIsNone(e.pending);self.assertEqual(e.env,0)
 def test_speed_preserves_phase_and_relative_rates(self):
  c=self.c;sl=c.slots[0];sl.phi=7.3
  old=sl.eff_cfg(c.g)['x'];heart.motion_save(c,'speed',.25)
  self.assertEqual(sl.phi,7.3);self.assertEqual(sl.eff_cfg(c.g)['x'],old*.25)
  self.assertEqual(sl.cfg['mult'],1);self.assertEqual(sl.cfg['ratio'],'1:2')
  with self.assertRaises(ValueError):heart.motion_save(c,'speed',float('nan'))
 def test_home_relationship_survives_parameter_count(self):
  from motion import animated_home,recipe_rate
  base=heart.capture_state(self.c)
  profile={'bindings':{'X':{'center':.5,'range':[.4,.6]},'Removed':{'center':.2,'range':[.1,.3]}}}
  a=animated_home(base,profile);base['slots']['New']=copy.deepcopy(base['slots']['X'])
  b=animated_home(base,profile)
  self.assertTrue(b['slots']['X']['drive']);self.assertFalse(b['slots']['New']['drive'])
  self.assertEqual(recipe_rate(a['global']['relationship'],'X',0),recipe_rate(b['global']['relationship'],'X',99))
  self.assertEqual(b['slots']['X']['config']['lo'],.4)
 def test_home_static_mode_is_not_animated(self):
  from motion import animated_home
  base=heart.capture_state(self.c);base['slots']['Color']=copy.deepcopy(base['slots']['X']);base['slots']['Color']['drive']=True
  result=animated_home(base,{'bindings':{'X':{'center':.5,'range':[.4,.6]}},'static':{'Color':.5,'Absent':1}})
  self.assertEqual(result['slots']['Color']['pose'],.5)
  self.assertFalse(result['slots']['Color']['drive'])
  self.assertTrue(result['slots']['X']['drive'])
  self.assertTrue(base['slots']['Color']['drive'])
 def test_replaced_effect_adopts_new_color_and_amount(self):
  def comp(pid,color):
   return {'video':{'effects':[]},'layers':[{'video':{'effects':[{'name':'Colorize','params':{'Opacity':{'id':pid,'value':.35,'max':1},'Color':{'id':pid+1,'valuetype':'ParamColor','value':color}}}]}}]}
  with patch.object(heart,'FX',{}),patch.object(heart,'load_fx',return_value={}):
   heart.discover_fx(comp(100,'#50ddffff'));old=heart.FX['L1/1'];old.target=1
   heart.discover_fx(comp(200,'#ffdd50ff'));new=heart.FX['L1/1']
   self.assertIsNot(old,new);self.assertEqual(new.target,.35)
   self.assertEqual(new.colors['Color']['id'],201)
 def test_legacy_preset_clears_new_relationship(self):
  c=self.c;h=heart.capture_state(c);h['global'].pop('relationship');h['global'].pop('speed')
  heart.motion_save(c,'relationship',{'kind':'pendulum','base':17,'members':{'X':4}})
  heart.apply_state(c,h)
  self.assertIsNone(c.g['relationship']);self.assertEqual(c.g['speed'],1)

if __name__=='__main__':unittest.main()
