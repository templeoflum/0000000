import unittest
from live_scan import compact
class ScanTests(unittest.TestCase):
 def test_keeps_active_controls_and_catalogues_inactive(self):
  p={'id':3,'valuetype':'ParamRange','value':.3,'min':0,'max':1}
  def clip(state):return {'id':1,'name':{'value':'shader'},'connected':{'value':state},'video':{'description':'shader','sourceparams':{'Amount':p},'effects':[{'name':'x'}]}}
  result=compact({'layers':[{'clips':[clip('Connected'),clip('Disconnected')]}]})
  a,b=result['layers'][0]['clips'];self.assertIn('sourceparams',a['video']);self.assertNotIn('sourceparams',b['video'])
  self.assertEqual(result['_heart_catalog']['parameter_count'],2)
