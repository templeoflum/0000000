"""Native metadata contract checks, using an isolated fake transport."""
import json,unittest
from unittest.mock import patch
from bridge import animation
class AnimationTests(unittest.TestCase):
 def setUp(self):
  self.calls=[];self.source='timeline';self.direction='Forward';self.bounds={'in':0,'out':1}
 def request(self,path,method='POST',value=None):
  self.calls.append((path,method,value))
  if method=='PUT':
   if path.endswith('phase-source'):self.source=value['phase_source']
   elif path.endswith('/42'):self.direction=value['value']
   else:self.bounds.update(value)
   return b''
  if path.endswith('phase-source'):
   return json.dumps({'phase_source':self.source,'parameters':{'playdirection':{'id':42,'valuetype':'ParamChoice','value':self.direction,'options':['Forward','Backward','Pause']}}}).encode()
  return json.dumps({'id':1,'valuetype':'ParamRange','min':0,'max':1,**self.bounds,'value':.4}).encode()
 def test_direction_readback_and_native_range(self):
  with patch('bridge.request',self.request):data=animation({'cmd':'animation_set','id':1,'fields':{'playdirection':'Backward'},'in':.2,'out':.8})
  self.assertEqual(data['parameters']['playdirection']['value'],'Backward')
  self.assertIn(('/parameter/by-id/1','PUT',{'in':.2,'out':.8}),self.calls)
 def test_rejects_unknown_paths_choices_and_ranges(self):
  for payload in ({'fields':{'/evil':0}},{'fields':{'playdirection':'oops'}},{'in':float('nan')},{'out':2},{'source':'bad'},{'source':'dashboard','dial':0}):
   self.calls.clear()
   with patch('bridge.request',self.request),self.assertRaises(ValueError):animation(dict(cmd='animation_set',id=1,**payload))
   self.assertFalse(any(c[1]=='PUT' for c in self.calls))
 def test_get_is_read_only(self):
  with patch('bridge.request',self.request):data=animation({'cmd':'animation_get','id':1})
  self.assertEqual(data['parameter']['value'],.4);self.assertTrue(all(c[1]=='GET' for c in self.calls))

 def test_waits_for_deferred_native_source(self):
  self.source='static';reads=0
  def delayed(path,method='POST',value=None):
   nonlocal reads
   if method=='PUT' and path.endswith('phase-source'):return b''
   if method=='GET' and path.endswith('phase-source'):
    reads+=1
    if reads>=3:self.source='timeline'
   return self.request(path,method,value)
  with patch('bridge.request',delayed),patch('bridge.time.sleep'):
   result=animation({'cmd':'animation_set','id':1,'source':'timeline'})
  self.assertEqual(result['phase_source'],'timeline');self.assertGreaterEqual(reads,3)
