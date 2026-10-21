import copy, json, time, unittest, struct
from pathlib import Path
from server import Engine
from bridge import phase_bundle
from scan import discover

def catalog():
 p=dict(id=1,valuetype='ParamRange',min=-1,max=1,value=.25,**{'in':.2,'out':.3})
 c=discover(dict(name={'id':10},layers=[dict(id=20,name='Figure',clips=[dict(id=30,name='shell',connected={'value':'Connected'},video=dict(description='Field',sourceparams={'W':p,'Size':dict(p,id=2)}))])]))
 t=next(t for t in c['targets'] if t['kind']=='source');t['native_phase_clip']=True
 t['params'][0]['native_phase']=dict(layer=1,clip=1,clip_id=30,source='field',description='Field',name='W',min=-1,max=1)
 return c

class NativePhaseTests(unittest.TestCase):
 def engine(self):
  e=Engine();e.reconcile(catalog());e.armed=e.connected=True;return e
 def test_only_prepared_timelines_start_and_static_values_survive(self):
  e=self.engine();e.start_phases(30)
  self.assertTrue(e.slots[1].drive);self.assertFalse(e.slots[2].drive);self.assertEqual(e.params[2][1]['value'],.25)
  e.drive_all(dict(epoch='10',target='source:30',on=False));self.assertFalse(e.slots[1].drive)
  e.drive_all(dict(epoch='10',target='source:30',on=True));self.assertTrue(e.slots[1].drive);self.assertFalse(e.slots[2].drive)
  with self.assertRaises(ValueError):e.drive(2,True)
 def test_ranges_stay_native_and_phase_survives_narrow_and_reversed_edits(self):
  e=self.engine();e.start_phases(30);e.slots[1].phi=.3
  c=catalog();p=next(t for t in c['targets'] if t['kind']=='source')['params'][0];p.update({'in':.29,'out':.21})
  e.reconcile(c);self.assertEqual(e.slots[1].phi,.3);self.assertEqual((e.slots[1].cfg['lo'],e.slots[1].cfg['hi']),(0,1))
  for i in range(100):
   for pid,v in e.tick(.02,time.perf_counter()+1+i*.02):self.assertGreaterEqual(v['phase'],0);self.assertLessEqual(v['phase'],1)
  with self.assertRaises(ValueError):e.param_range(1,0,1)
 def test_pause_hold_rearm_and_replacement(self):
  e=self.engine();e.start_phases(30);e.tick(.1,time.perf_counter()+1);e.set_hold(True);phi=e.slots[1].phi
  self.assertEqual(e.tick(.1,time.perf_counter()+2),[]);self.assertEqual(e.slots[1].phi,phi)
  e.set_hold(False);e.drive(1,False);e.tick(.02,time.perf_counter()+3);self.assertAlmostEqual(e.slots[1].cfg['manual'],e.slots[1].sent_phase)
  c=catalog();t=next(t for t in c['targets'] if t['kind']=='source');t['params'][0].pop('native_phase');e.reconcile(c)
  self.assertFalse(e.slots[1].drive);self.assertNotIn(1,e.owned);self.assertNotIn(1,e.binding()['phases'])
 def test_fractional_multiplier_reaches_integrated_rate(self):
  e=self.engine()
  for mult in (.025,-.025,0,.001):
   e.parameter_motion(1,dict(mult=mult,seconds=0));self.assertAlmostEqual(e.slots[1].target['x'],mult)
 def test_bundle_validates_identity_and_clamps_phase_without_value_writes(self):
  e=self.engine();r=e.params[1][1]['native_phase'];clip=dict(id=30,connected={'value':'Connected'},video=dict(description='Field',sourceparams={'W':dict(id=1,min=-1,max=1,**{'in':.2,'out':.3})}))
  data=phase_bundle(clip,[(1,{'phase':.4},r)])
  self.assertIn(b'/composition/layers/1/clips/1/video/source/field/w/phase',data);self.assertAlmostEqual(struct.unpack('>f',data[-4:])[0],.4)
  for change in ('clip','parameter','source','inactive'):
   c=copy.deepcopy(clip)
   if change=='clip':c['id']=31
   elif change=='parameter':c['video']['sourceparams']['W']['id']=2
   elif change=='source':c['video']['description']='Other'
   else:c['connected']['value']='Disconnected'
   with self.assertRaises(ValueError):phase_bundle(c,[(1,{'phase':.4},r)])

if __name__=='__main__':unittest.main()
