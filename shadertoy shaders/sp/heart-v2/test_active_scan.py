"""Lightweight discovery preserves layer motion while following playing clips."""
import copy,unittest
from scan import discover,refresh_active

class ActiveScanTests(unittest.TestCase):
 def setUp(self):
  def clip(id,pid):return dict(id=id,name={'value':str(id)},connected={'value':'Connected'},video={'sourceparams':{'X':dict(id=pid,valuetype='ParamRange',min=-1,max=1,value=.1)}})
  self.first=clip(20,201);self.second=clip(30,301)
  self.composition=dict(name={'id':100},layers=[dict(id=10,name='Figure',clips=[self.first,self.second],active_clip=self.first,video={'effects':[dict(id=99,name='Transform',params={'X':dict(id=999,valuetype='ParamRange',min=-10,max=10,value=0)})]})])
  self.catalog=discover(self.composition)
 def test_unchanged_values_do_not_rebind_or_broadcast(self):
  clip=copy.deepcopy(self.first);clip['video']['sourceparams']['X']['value']=.7
  result=refresh_active(self.catalog,{10:clip})
  self.assertFalse(result.pop('_changed'));self.assertEqual(result,self.catalog)
 def test_clip_switch_preserves_layer_effect_and_native_identity(self):
  result=refresh_active(self.catalog,{10:self.second})
  self.assertTrue(result['_changed']);self.assertEqual(result['layers'][0]['active'],2)
  targets={t['id']:t for t in result['targets']}
  self.assertNotIn('source:20',targets);self.assertIn('source:30',targets)
  self.assertEqual(targets['source:30']['layer_id'],10);self.assertEqual(targets['source:30']['clip'],2)
  self.assertEqual(targets['effect:99'],next(t for t in self.catalog['targets'] if t['id']=='effect:99'))
 def test_clear_unknown_and_changed_source_contract(self):
  cleared=refresh_active(self.catalog,{10:None})
  self.assertEqual(cleared['layers'][0]['active'],0)
  self.assertFalse(any(t.get('scope')=='clip' for t in cleared['targets']))
  unknown=copy.deepcopy(self.first);unknown['id']=1234
  self.assertEqual(refresh_active(self.catalog,{10:unknown}),{'needs_full':True})
  changed=copy.deepcopy(self.first);changed['video']['sourceparams']['X']['id']=202
  self.assertTrue(refresh_active(self.catalog,{10:changed})['_changed'])
