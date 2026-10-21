"""Drive sweeps use native timeline bounds without rewriting those timelines."""
import time,unittest
from scan import discover,refresh_active
from server import Engine,native_drive_range

def composition():
 return dict(name={'id':10},layers=[dict(id=20,name='Instrument',clips=[dict(id=30,name='Movement',connected={'value':'Connected'},video={'effects':[dict(id=40,name='Transform',params={
  'X':dict(id=1,valuetype='ParamRange',min=-32768,max=32768,value=0,**{'in':-100,'out':100}),
  'Scale':dict(id=2,valuetype='ParamRange',min=0,max=1000,value=95,**{'in':90,'out':99})})]})])])

class NativeRangeTests(unittest.TestCase):
 def engine(self):
  e=Engine();e.reconcile(discover(composition()));e.armed=e.connected=True;return e
 def real_bounds(self,e,pid):
  p=e.params[pid][1];s=e.slots[pid];return tuple(p['min']+s.cfg[k]*(p['max']-p['min']) for k in ('lo','hi'))
 def test_discovery_preserves_timeline_in_out_and_initial_drive_limits(self):
  e=self.engine();self.assertEqual(self.real_bounds(e,1),(-100,100));self.assertEqual(self.real_bounds(e,2),(90,99))
  self.assertEqual(e.params[1][1]['in'],-100);self.assertFalse(e.slots[1].drive)
 def test_bulk_drive_open_shuffle_and_amount_keep_native_bounds_in_output(self):
  e=self.engine();e.drive_all(dict(epoch='10',target='effect:40',on=True));e.gesture('effect:40','open');e.gesture('effect:40','shuffle');e.settings('effect:40',dict(amount=.6,rate=2))
  now=time.perf_counter()+1
  for step in range(2000):
   for pid,v in e.tick(.02,now+step*.02):
    lo,hi={1:(-100,100),2:(90,99)}[pid];self.assertLessEqual(lo-1e-8,v);self.assertLessEqual(v,hi+1e-8)
  self.assertEqual(self.real_bounds(e,1),(-100,100));self.assertEqual(self.real_bounds(e,2),(90,99))
 def test_manual_authored_ranges_survive_open_and_native_rescan(self):
  e=self.engine();e.param_range(2,.092,.096);e.gesture('effect:40','open')
  c=composition();c['layers'][0]['clips'][0]['video']['effects'][0]['params']['Scale'].update({'in':91,'out':98})
  e.reconcile(discover(c));self.assertEqual(self.real_bounds(e,2),(92,96));self.assertTrue(e.slots[2].drive)
 def test_native_range_change_updates_unedited_defaults_without_resetting_drive(self):
  e=self.engine();e.drive(1,True);e.slots[1].phi=.7
  c=composition();clip=c['layers'][0]['clips'][0];clip['video']['effects'][0]['params']['X'].update({'in':-60,'out':60})
  fresh=refresh_active(e.catalog,{20:clip});self.assertTrue(fresh['_changed']);e.reconcile(fresh)
  self.assertEqual(self.real_bounds(e,1),(-60,60));self.assertEqual(e.slots[1].phi,.7);self.assertTrue(e.slots[1].drive)
 def test_reverse_equal_missing_and_invalid_bounds(self):
  p=dict(min=-10,max=10)
  self.assertEqual(native_drive_range(dict(p,**{'in':4,'out':-2})),(.4,.7))
  self.assertEqual(native_drive_range(dict(p,**{'in':2,'out':2})),(.6,.6))
  self.assertEqual(native_drive_range(p),(0,1))
  self.assertEqual(native_drive_range(dict(p,**{'in':float('nan'),'out':2})),(0,1))
 def test_replaced_parameter_does_not_inherit_old_authored_ranges(self):
  e=self.engine();e.param_range(2,.2,.8);e.drive(2,True)
  c=composition();c['layers'][0]['clips'][0]['video']['effects'][0]['params']['Scale']['id']=3;e.reconcile(discover(c))
  self.assertEqual(self.real_bounds(e,3),(90,99));self.assertFalse(e.slots[3].drive)
