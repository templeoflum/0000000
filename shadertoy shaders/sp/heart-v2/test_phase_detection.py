"""Native animation mode, not a per-clip binding, determines drive eligibility."""
import copy,time,unittest
from scan import discover,native_phases,refresh_active
from server import Engine
from bridge import phase_bundle

def fixture():
 def p(pid,value=.3):return dict(id=pid,valuetype='ParamRange',min=0,max=1,**{'in':.2,'out':.6},value=value)
 fx=lambda eid,params,removable=True:dict(id=eid,name='Transform',is_user_removable=removable,params=params)
 return dict(name={'id':10},layers=[dict(id=20,name='Arbitrary layer',video={'effects':[fx(31,{'Scale':p(1)},False),fx(32,{'Scale':p(2),'Position X':p(3),'Opacity':p(4)})]},clips=[dict(id=40,name='Arbitrary source',connected={'value':'Connected'},video=dict(description='Some Source',sourceparams={'W':p(5),'Size':p(6)}))])])

class DetectionTests(unittest.TestCase):
 def prepare(self,c,previous=None,modes=None,now=10,budget=96):
  modes=modes or {1:('static',False),2:('timeline',True),3:('timeline',False),4:('static',False),5:('timeline',True),6:('external_fft',False)}
  parameters={p['id']:p for t in c['targets'] for p in t['params']};calls=[]
  def read(path):
   calls.append(path);pid=int(path.split('/')[3]);p=parameters[pid]
   if path.endswith('/phase-source'):
    source,paused=modes.get(pid,('static',False));return dict(phase_source=source,parameters={'PlayDirection':{'value':'||' if paused else '>'}})
   return dict(id=pid,min=p['min'],max=p['max'],value=p['value'],**{'in':p['in'],'out':p['out']})
  return native_phases(c,previous,read,budget,now),calls
 def test_layer_effect_and_source_detection_without_any_config(self):
  c,calls=self.prepare(discover(fixture()));p={p['id']:p for t in c['targets'] for p in t['params']}
  self.assertEqual({pid for pid,x in p.items() if x.get('native_phase')},{2,5})
  self.assertEqual(p[2]['native_phase']['address'],'/composition/layers/1/video/effects/transform2/effect/scale/phase')
  self.assertEqual(p[1]['phase_route']['address'],'/composition/layers/1/video/effects/transform/scale/phase')
  self.assertEqual(p[4]['phase_route']['address'],'/composition/layers/1/video/effects/transform2/opacity/phase')
  self.assertEqual(p[5]['native_phase']['address'],'/composition/layers/1/clips/1/video/source/somesource/w/phase')
  e=Engine();e.reconcile(c);e.armed=e.connected=True;e.start_prepared()
  self.assertEqual({pid for pid,s in e.slots.items() if s.drive},{2,5})
  e.drive_all(dict(epoch='10',target='effect:32',on=True));self.assertFalse(e.slots[3].drive)
  for pid in (1,3,4,6):
   with self.assertRaises(ValueError):e.drive(pid,True)
  e.manual(4,.75,duration=0);self.assertEqual(e.slots[4].cfg['manual'],.75);self.assertFalse(e.slots[4].drive)
 def test_mode_changes_opt_in_and_release_without_overwriting_bounds(self):
  c,_=self.prepare(discover(fixture()));e=Engine();e.reconcile(c);e.armed=e.connected=True;e.start_prepared();e.drive(2,False)
  same,_=self.prepare(discover(fixture()),c,now=13);e.reconcile(same);e.start_prepared();self.assertFalse(e.slots[2].drive,'User Drive off survives reinspection')
  changed,_=self.prepare(discover(fixture()),same,modes={2:('static',False),3:('timeline',True)},now=16);e.reconcile(changed);e.start_prepared()
  self.assertFalse(e.slots[2].drive);self.assertNotIn(2,e.owned);self.assertTrue(e.slots[3].drive)
  self.assertEqual((e.params[3][1]['in'],e.params[3][1]['out']),(.2,.6))
  with self.assertRaises(ValueError):e.param_range(4,0,1)
 def test_budget_priority_and_failure_do_not_invent_a_drive(self):
  c=discover(fixture());previous=copy.deepcopy(c);previous['_phase_priority']=[5]
  result,calls=self.prepare(c,previous,budget=2)
  self.assertLessEqual(len(calls),4);self.assertIn('/parameter/by-id/5/phase-source',calls)
  self.assertFalse(next(p for t in result['targets'] for p in t['params'] if p['id']==2).get('native_phase'))
  def fail(path):raise OSError('offline')
  result=native_phases(copy.deepcopy(result),result,fail,96,20)
  self.assertFalse(any(p.get('native_phase') for t in result['targets'] for p in t['params']))
 def test_native_range_edits_and_effect_identity_validation(self):
  c,_=self.prepare(discover(fixture()));r=next(p for t in c['targets'] for p in t['params'] if p['id']==2)['native_phase'];effect=fixture()['layers'][0]['video']['effects'][1]
  self.assertIn(b'/transform2/effect/scale/phase',phase_bundle(effect,[(2,{'phase':.5},r)]))
  effect['params']['Scale']['id']=100
  with self.assertRaises(ValueError):phase_bundle(effect,[(2,{'phase':.5},r)])
 def test_source_osc_names_preserve_native_plus_and_parentheses(self):
  for name,slug in [('4D Voronoi + Hopf Fibration','4dvoronoi+hopffibration'),('16 Dimensional Julia (Sedenion)','16dimensionaljulia(sedenion)')]:
   raw=fixture();raw['layers'][0]['clips'][0]['video']['description']=name
   c,_=self.prepare(discover(raw));p=next(p for t in c['targets'] for p in t['params'] if p['id']==5)
   self.assertEqual(p['native_phase']['address'],f'/composition/layers/1/clips/1/video/source/{slug}/w/phase')
   self.assertIn(f'/source/{slug}/w/phase'.encode(),phase_bundle(raw['layers'][0]['clips'][0],[(5,{'phase':.5},p['native_phase'])]))
 def test_active_source_addresses_keep_actual_layer_index(self):
  raw=fixture();raw['layers'].insert(0,dict(id=99,name='Other',clips=[]));c=discover(raw)
  clip=raw['layers'][1]['clips'][0];clip['video']['sourceparams']['W']['in']=.25
  c=refresh_active(c,{20:clip});p=next(p for t in c['targets'] for p in t['params'] if p['id']==5)
  self.assertEqual(p['phase_route']['read'],'/composition/layers/2/clips/1')
  self.assertIn('/layers/2/',p['phase_route']['address'])
 def test_home_and_base_restore_phase_without_restoring_native_ranges(self):
  c,_=self.prepare(discover(fixture()));e=Engine();e.reconcile(c);e.armed=e.connected=True;e.start_prepared()
  e.rack_config={'recovery':{'source_layers':[20],'targets':[]}}
  e.manual(2,.5,duration=0);e.set_home('effect:32');saved=e.session.capture('base')
  self.assertAlmostEqual(saved['targets']['effect:32']['params']['2']['cfg']['manual'],.75)
  self.assertNotIn('native_animation',saved['targets']['effect:32']['params']['2'])
  changed=copy.deepcopy(c);p=next(p for t in changed['targets'] for p in t['params'] if p['id']==2);p.update({'in':.1,'out':.3})
  e.reconcile(changed);e.manual(2,.12,duration=0);e.return_home('effect:32')
  self.assertAlmostEqual(e.slots[2].cfg['manual'],.75)
  output=dict(e.session.apply_return(saved));self.assertAlmostEqual(output[2]['phase'],.75)
  self.assertEqual((e.params[2][1]['in'],e.params[2][1]['out']),(.1,.3))
  self.assertEqual((e.slots[2].cfg['lo'],e.slots[2].cfg['hi']),(0,1))
 def test_generic_transition_discards_legacy_drives(self):
  c=discover(fixture());e=Engine();e.reconcile(c);e.armed=e.connected=True;e.drive(4,True)
  prepared,_=self.prepare(c);e.reconcile(prepared);e.start_prepared()
  self.assertFalse(e.slots[4].drive);self.assertNotIn(4,e.owned);self.assertTrue(e.slots[2].drive)

if __name__=='__main__':unittest.main()
