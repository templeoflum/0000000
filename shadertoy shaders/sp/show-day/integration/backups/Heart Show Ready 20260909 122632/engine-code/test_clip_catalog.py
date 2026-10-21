import copy,unittest
from unittest.mock import patch
import clip_catalog as catalog
import heart

def source(params):return {'id':12,'name':{'value':'Unregistered'},'connected':{'value':'Disconnected'},'video':{'description':'Unlisted source for discovery test','sourceparams':params}}
class CatalogTests(unittest.TestCase):
 def test_inactive_controls_are_read_without_mutation(self):
  c=source({'Warp':{'id':1,'valuetype':'ParamRange','min':-3,'max':8},'Fire':{'id':2,'valuetype':'ParamTrigger'},'Lock':{'id':3,'valuetype':'ParamBoolean'}});comp={'layers':[{'clips':[c,{'video':None}]}]};before=copy.deepcopy(comp)
  result=catalog.build(comp);self.assertEqual(result['clip_count'],1);self.assertEqual(result['parameter_count'],3);self.assertFalse(result['clips'][0]['active']);self.assertEqual(comp,before)
  self.assertEqual([p['mode'] for p in result['clips'][0]['parameters']],['continuous','momentary','toggle'])
 def test_unknown_source_is_discovered_without_allowlist(self):
  c=source({'Warp':{'id':1,'valuetype':'ParamRange','min':0,'max':1}})
  self.assertNotIn(c['video']['description'],heart.ATOMS);self.assertTrue(heart.is_sp(c));self.assertEqual(heart.atom_sections(c)[0][0],c['video']['description']);self.assertNotIn(c['video']['description'],heart.ATOMS)
 def test_schema_replacement_updates_catalog(self):
  c=source({'Warp':{'id':1,'valuetype':'ParamRange','min':0,'max':1}});a=catalog.build({'layers':[{'clips':[c]}]});c['video']['sourceparams']={'Tint':{'id':9,'valuetype':'ParamChoice','options':['Red','Blue']}};b=catalog.build({'layers':[{'clips':[c]}]})
  self.assertEqual(a['clips'][0]['parameters'][0]['name'],'Warp');self.assertEqual(b['clips'][0]['parameters'][0]['name'],'Tint')
 def test_unexposed_source_is_not_fabricated(self):
  self.assertFalse(heart.is_sp(source(None)));self.assertEqual(catalog.build({'layers':[{'clips':[source(None)]}]})['parameter_count'],0)
