import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import instruments
from motion import animated_home

class InstrumentTests(unittest.TestCase):
 def test_home_is_role_scoped_and_unknown_source_is_untouched(self):
  self.assertIsNotNone(instruments.home('figure','SP Atom Solid'))
  self.assertIsNone(instruments.home('field','SP Atom Solid'))
  self.assertIsNone(instruments.home('figure','unknown'))
 def test_new_controls_stay_still_and_bindings_survive_reordering(self):
  profile=instruments.home('figure','z33d+')
  slots={n:{'drive':True,'pose':.5,'config':{}} for n in ['New control','e','rot angle','axis drift','my','mx']}
  state={'global':{},'slots':slots};result=animated_home(state,profile)
  self.assertFalse(result['slots']['New control']['drive'])
  self.assertFalse(result['slots']['axis drift']['drive'])
  self.assertEqual(result['slots']['axis drift']['pose'],0)
  self.assertTrue(result['slots']['rot angle']['drive'])
  other=animated_home({'global':{},'slots':dict(reversed(list(slots.items())))},profile)
  self.assertEqual(result['global']['relationship'],other['global']['relationship'])
 def test_bank_follows_source_identity_descriptions_not_positions(self):
  clips=[{'col':50,'name':'renamed','source':'z33d+'},{'col':2,'name':'3d','source':'unrelated'},{'col':9,'name':'test','source':'SP Atom Solid'}]
  bank=instruments.bank('figure',clips)
  self.assertEqual([c['col'] for c in bank],[50,9]);self.assertEqual(bank[0]['name'],'Seed · z33d+')
  self.assertEqual(instruments.bank('field',clips),[])
 def test_rejects_duplicate_sources_and_effect_scope_containment(self):
  for mutate in [lambda d:d['instruments'].append(copy.deepcopy(d['instruments'][0])),lambda d:d['instruments'][0]['framing'].update(scope='layer')]:
   data={'version':1,'instruments':copy.deepcopy(instruments.CATALOG)};mutate(data)
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'defs.json';p.write_text(json.dumps(data))
    with self.assertRaises(ValueError):instruments.load(p)
 def test_instrument_home_is_still_and_user_home_supplies_pose(self):
  import heart
  from types import SimpleNamespace
  profile=instruments.home('figure','SP Atom Solid')
  state={'global':{},'slots':{n:{'drive':False,'pose':.5,'config':{}} for n in profile['bindings']}}
  clip=SimpleNamespace(role='figure',atom='SP Atom Solid',name='renamed',home=None,slots=[],history=[],morph=1)
  with patch.object(heart,'capture_state',return_value=state),patch.object(heart,'load_homes',return_value={}),patch.object(heart,'apply_state') as apply:
   clip.slots=[SimpleNamespace(name=n,identity=n,owner='heart',target=None) for n in profile['bindings']]
   heart.go_home(clip)
   target=apply.call_args.args[1];self.assertFalse(target['slots']['Tumble']['drive'])
   self.assertEqual(target['slots']['Tumble']['pose'],.2)
   clip.home={'sweet_home':True,'version':2,'slots':{'Tumble':{'pose':.7,'drive':True,'config':{}}}}
   heart.go_home(clip)
   self.assertEqual(apply.call_args.args[1]['slots']['Tumble']['pose'],.7)
   self.assertFalse(apply.call_args.args[1]['slots']['Tumble']['drive'])
 def test_open_keeps_figure_framing_but_opens_other_axes_and_keeps_choices_still(self):
  import heart
  from types import SimpleNamespace
  profile=instruments.home('figure','SP Atom Solid')
  slots=[SimpleNamespace(name=n,identity=n,owner='heart',target=None,cfg={'lo':.1,'hi':.9}) for n in ['Size','X','Y','Tumble','Hue','New control','Figure A']]
  slots[-1].choices=['torus','cube']
  state={'global':{},'slots':{s.name:{'drive':False,'pose':profile['bindings'].get(s.name,{}).get('center',.5),'config':{}} for s in slots}}
  clip=SimpleNamespace(role='figure',atom='SP Atom Solid',name='renamed',slots=slots,history=[],morph=1)
  with patch.object(heart,'capture_state',return_value=state),patch.object(heart,'apply_state') as apply:
   heart.open_motion(clip);target=apply.call_args.args[1]
   for name in ['Size','X','Y']:
    self.assertFalse(target['slots'][name]['drive']);self.assertEqual(target['slots'][name]['pose'],state['slots'][name]['pose'])
   for name in ['Tumble','Hue','New control']:
    self.assertTrue(target['slots'][name]['drive']);cfg=target['slots'][name]['config'];self.assertLessEqual(cfg['hi']-cfg['lo'],.300001)
    if name in profile['bindings']:
     low,high=profile['bindings'][name]['range'];self.assertGreaterEqual(cfg['lo'],low);self.assertLessEqual(cfg['hi'],high)
   self.assertFalse(target['slots']['Figure A']['drive'])

if __name__=='__main__':unittest.main()
