"""Configured accents stay on exact existing idle effects and preserve steady chains."""
import json
from pathlib import Path
import unittest
from scan import discover

ROOT=Path(__file__).parent

class RackConfiguration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rack=json.loads((ROOT/'effect-rack.json').read_text())
  cls.catalog=discover(json.loads((ROOT/'checks/session-native-before.json').read_text()))
  cls.targets={t['id']:t for t in cls.catalog['targets']}
  latest=json.loads((ROOT/'checks/session-composition-goo-catalog.json').read_text())
  cls.targets.update({t['id']:t for t in latest['targets'] if t.get('effect_name')=='Goo' and t['scope']=='composition'})

 def test_combined_stacks_only_use_existing_idle_effects(self):
  self.assertEqual(self.rack['epoch'],self.catalog['epoch'])
  for row in self.rack['rows']:
   for pad in row['pads']:
    if pad.get('id')!='stack':continue
    for binding in pad['bindings']:
     with self.subTest(row=row['id'],pad=pad['id'],target=binding['target']):
      target=self.targets[binding['target']]
      self.assertEqual(binding['identity'],[target.get(k)for k in ('scope','layer_id','group_id','clip_id','effect_name')])
      params={p['id']:p for p in target['params']}
      opacity=params[binding['opacity']];bypass=params[binding['bypass']]
      self.assertEqual(opacity['name'],'Opacity');self.assertEqual(bypass['name'],'Bypass')
      self.assertTrue(bypass['value']or opacity['value']==0,'A decay to zero must not erase a steady effect')
      self.assertNotIn(target['effect_name'],('Transform','Mask','EdgeDetection','Dilate'))

 def test_colour_controls_preserve_native_units_and_offset_timeline(self):
  for row in self.rack['rows']:
   self.assertEqual([c['id'] for c in row['controls']],['invert_a'] if row['id']=='feedback' else [])
   if row['id']!='feedback':self.assertTrue(row['color']);self.assertTrue(row['lut'])
   for control in row['controls']:
    self.assertNotEqual(control['id'],'Offset')
    for binding in control['bindings']:
     target=self.targets[binding['target']]
     self.assertEqual(binding['identity'],[target.get(k)for k in ('scope','layer_id','group_id','clip_id','effect_name')])
     native=next(p for p in target['params'] if p['id']==binding['parameter'])
     for key in ('name','type','min','max'):self.assertEqual(binding[key],native[key])
     self.assertEqual((control['min'],control['max']),(native['min'],native['max']))

 def test_existing_lut_and_latch_semantics_remain_explicit(self):
  for row in self.rack['rows']:
   pads={p['id']:p for p in row['pads']}
   if 'decon' not in pads:continue
   self.assertEqual(pads['decon']['mode'],'trigger');self.assertEqual(pads['pixel_melt']['mode'],'latch')
   for binding in pads['decon']['bindings']:self.assertEqual(binding['event_name'],'DECON')
   for binding in pads['pixel_melt']['bindings']:self.assertEqual(binding['latch_name'],'MELT_LOCK')
   self.assertNotIn('melt_hit',pads)
   for name in ('blok',):
    self.assertIs(pads[name]['clear'],False)
    self.assertIs(pads[name]['enable_control'],False)

 def test_feedback_toggles_have_exact_effect_opacity_and_bypass_bindings(self):
  row=next(r for r in self.rack['rows']if r['id']=='feedback')
  self.assertEqual(row['color'],[]);self.assertFalse(row.get('controls_visible',False))
  self.assertEqual(len(row['pads']),7)
  for pad in row['pads']:
   self.assertEqual(pad['mode'],'fade' if pad['id'].startswith('mirror_') else 'toggle')
   for binding in pad['bindings']:
    target=self.targets[binding['target']];params={p['id']:p for p in target['params']}
    self.assertEqual(binding['identity'],[target.get(k) for k in ('scope','layer_id','group_id','clip_id','effect_name')])
    self.assertEqual(params[binding['opacity']]['name'],'Opacity');self.assertEqual(params[binding['bypass']]['name'],'Bypass')
    self.assertEqual((params[binding['opacity']]['min'],params[binding['opacity']]['max']),(0,1))
    self.assertNotIn(target['effect_name'],('Transform','Mask'))

 def test_black_strobe_duplicate_resolves_by_id_and_actual_colour(self):
  stage=next(r for r in self.rack['rows']if r['id']=='stage')
  stack=next(p for p in stage['pads']if p['id']=='stack')
  strobes=[self.targets[b['target']]for b in stack['bindings']if self.targets[b['target']]['effect_name']=='Strobe']
  self.assertEqual(len(strobes),1)
  self.assertEqual(next(p['value']for p in strobes[0]['params']if p['name']=='Color'),'#000000ff')
  self.assertEqual(stack['label'],'Cut')

 def test_figure_cloner_and_three_mirrors_are_soft_toggles(self):
  pads={p['id']:p for row in self.rack['rows'] if row['id']=='figure' for p in row['pads']}
  for key,name in [('linear_cloner','LinearCloner'),('mirror_x','Mirror'),('mirror_y','Mirror'),('mirror_xy','Mirror')]:
   pad=pads[key];self.assertEqual(pad['mode'],'fade')
   for b in pad['bindings']:
    target=self.targets[b['target']];params={p['id']:p for p in target['params']}
    self.assertEqual(target['effect_name'],name);self.assertEqual(target['layer_id'],1788149968008)
    self.assertEqual(b['identity'],[target.get(k) for k in ('scope','layer_id','group_id','clip_id','effect_name')])
    self.assertEqual(params[b['opacity']]['name'],'Opacity');self.assertEqual(params[b['bypass']]['name'],'Bypass')

if __name__=='__main__':unittest.main()
