import copy,time,unittest
from unittest.mock import patch
from server import Engine
from test_launch import catalog

class DriveBankTests(unittest.TestCase):
 def setup_engine(self):
  c=catalog();source=next(t for t in c['targets'] if t['id']=='source:1')
  source['params'] += [dict(id=pid,name=str(pid),type='ParamRange',value=.4,min=0,max=1) for pid in (103,104)]
  e=Engine();e.reconcile(c);e.armed=e.connected=True
  for pid in (11,101,103,201):e.drive(pid,True);e.param_range(pid,.2,.7)
  e.relationship('source:1',dict(pattern=3,fm=.4,seconds=0));e.settings('source:1',dict(rate=2,amount=.35))
  for sl in e.slots.values():sl.phi=.73;sl.phi_fm=.27
  return e
 def test_layer_shuffle_only_driven_preserves_family_range_phase_and_other_layers(self):
  e=self.setup_engine();before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};groups=copy.deepcopy(e.groups);owned=e.owned.copy();owners=e.control_owner.copy();now=time.perf_counter()+1
  values={pid:sl.value(sl.blend(now)) for pid,sl in e.slots.items()}
  with patch('server.time.perf_counter',return_value=now),patch('server.random.shuffle',side_effect=lambda xs:xs.reverse()):
   e.drive_bank_action(dict(epoch='one',layer_id=10,action='shuffle'))
  self.assertEqual(e.groups,groups);self.assertEqual(e.owned,owned);self.assertEqual(e.control_owner,owners)
  for pid,sl in e.slots.items():
   self.assertEqual(sl.phi,.73);self.assertAlmostEqual(sl.value(sl.blend(now)),values[pid])
   if pid in (11,101,103):
    self.assertNotEqual(sl.cfg['offset'],before[pid]['offset'])
    for key in ('lo','hi','manual','mult','shape'):self.assertEqual(sl.cfg[key],before[pid][key])
   else:self.assertEqual(sl.cfg,before[pid])
  self.assertEqual(e.slots[101].cfg['family_slot'],e.slots[103].index)
  self.assertEqual(e.slots[103].cfg['family_slot'],e.slots[101].index)
 def test_unison_stays_unison_and_legacy_shuffle_uses_same_scope(self):
  e=self.setup_engine();e.relationship('source:1',dict(pattern=1,seconds=0));idle=copy.deepcopy(e.slots[104].cfg)
  e.gesture('source:1','shuffle')
  self.assertEqual(e.groups['source:1']['pattern'],1);self.assertEqual(e.slots[101].cfg['offset'],e.slots[103].cfg['offset']);self.assertEqual(e.slots[104].cfg,idle)
  self.assertEqual(e.slots[101].target['x'],e.slots[103].target['x'])
 def test_summary_includes_unwatched_drives_without_broad_value_subscriptions(self):
  e=self.setup_engine();e.selected='source:1';e.watched=set();s=e.state()
  self.assertNotIn(201,s['values']);self.assertEqual(s['drive_bank']['effect:other']['count'],1)
  self.assertEqual(s['drive_bank']['source:1'],dict(count=2,pattern=3,rate=2,eligible=3,active=2));self.assertIn('drive_bank',s['capabilities'])
 def test_family_rate_and_idle_pin_preserve_authored_controls(self):
  e=self.setup_engine();before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};driven={pid for pid,sl in e.slots.items() if sl.drive}
  e.drive_bank_action(dict(epoch='one',target='source:1',action='family',pattern=4))
  e.drive_bank_action(dict(epoch='one',target='source:1',action='rate',rate=.5))
  self.assertEqual(e.groups['source:1']['pattern'],4);self.assertEqual(e.groups['source:1']['speed'],.5);self.assertEqual(e.groups['source:1']['depth'],.35)
  self.assertEqual({pid:sl.cfg for pid,sl in e.slots.items()},before);self.assertEqual({pid for pid,sl in e.slots.items() if sl.drive},driven)
  e.drive(101,False);e.drive(103,False);before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()}
  e.drive_bank_action(dict(epoch='one',target='source:1',action='shuffle'));self.assertEqual({pid:sl.cfg for pid,sl in e.slots.items()},before)
 def test_missing_stale_and_stage_targets_are_rejected(self):
  e=self.setup_engine();before=copy.deepcopy(e.groups)
  for data in [dict(epoch='old',target='source:1',action='shuffle'),dict(epoch='one',target='missing',action='family',pattern=3),dict(epoch='one',layer_id=99,action='shuffle'),dict(epoch='one',target='source:1',action='family',pattern=1.5)]:
   with self.assertRaises(ValueError):e.drive_bank_action(data)
  self.assertEqual(e.groups,before)
  next(t for t in e.catalog['targets'] if t['id']=='source:1')['stage']=123
  self.assertNotIn('source:1',e.state()['drive_bank'])
  with self.assertRaises(ValueError):e.drive_bank_action(dict(epoch='one',target='source:1',action='shuffle'))

 def test_drive_all_skips_locked_on_and_off_preserving_ranges(self):
  e=self.setup_engine();e.parameter_lock(dict(epoch='one',id=101,on=True));e.parameter_lock(dict(epoch='one',id=104,on=True));e.drive(103,False)
  before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};phase=e.slots[101].phi
  e.drive_all(dict(epoch='one',target='source:1'))
  self.assertTrue(e.slots[101].drive);self.assertTrue(e.slots[103].drive);self.assertFalse(e.slots[104].drive);self.assertTrue(e.slots[201].drive)
  e.drive_bank_action(dict(epoch='one',target='source:1',action='drive'))
  self.assertTrue(e.slots[101].drive);self.assertFalse(e.slots[103].drive);self.assertFalse(e.slots[104].drive)
  self.assertEqual(e.slots[101].cfg,before[101]);self.assertEqual(e.slots[104].cfg,before[104]);self.assertEqual(e.slots[101].phi,phase)
  self.assertEqual((e.slots[103].cfg['lo'],e.slots[103].cfg['hi']),(.2,.7));self.assertTrue(e.state()['values'][101]['locked'])
 def test_locked_drives_skip_shuffle_and_all_locked_is_noop(self):
  e=self.setup_engine()
  for pid in (101,103,104):e.parameter_lock(dict(epoch='one',id=pid,on=True))
  before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};owners=e.control_owner.copy()
  e.drive_all(dict(epoch='one',target='source:1'));e.drive_bank_action(dict(epoch='one',target='source:1',action='shuffle'))
  self.assertEqual(before,{pid:sl.cfg for pid,sl in e.slots.items()});self.assertEqual(owners,e.control_owner)
  self.assertEqual(e.state()['drive_bank']['source:1']['eligible'],0)
 def test_bulk_actions_reject_stale_targets_and_new_clip_starts_idle(self):
  e=self.setup_engine()
  for command in (dict(epoch='old',target='source:1'),dict(epoch='one',target='missing')):
   with self.assertRaises(ValueError):e.drive_all(command)
  with self.assertRaises(ValueError):e.parameter_lock(dict(epoch='old',id=101,on=True))
  e.reconcile(catalog(2));self.assertFalse(e.slots[102].drive);self.assertTrue(e.slots[201].drive)
  with self.assertRaises(ValueError):e.drive_all(dict(epoch='one',target='source:1'))
