import copy,json,random,unittest,xml.etree.ElementTree as ET
from authored import Authored,variation,xml_program
from server import Engine
from scan import discover,refresh_active
from pathlib import Path

class AuthoredPrograms(unittest.TestCase):
 def program(self,id=1,duration=12):
  return dict(id=id,name='X',type='ParamRange',min=-100,max=100,value=0,source='timeline',**{'in':-5,'out':7},fields=dict(Duration=duration,Speed=.9,PlayMode='Bounce',PlayDirection='>',DurationIsScalable=False),phase=.2)
 def test_saved_duration_and_abgr(self):
  n=dict(id=1,valuetype='ParamRange',min=0,max=100,options=[])
  x=ET.fromstring('<ParamRange name="X" value="5"><DurationSource userDuration="12" scale=".25"/><PhaseSourceTimeline phase=".3"><Params><Param name="DurationIsScalable" T="BOOL" value="1"/></Params></PhaseSourceTimeline></ParamRange>')
  self.assertEqual(xml_program(x,n)['fields']['Duration'],3)
  x.find('.//Param').set('value','0');self.assertEqual(xml_program(x,n)['fields']['Duration'],12)
  self.assertEqual(xml_program(ET.fromstring('<ParamColor name="Tint" value="4281541137"/>'),dict(n,valuetype='ParamColor'))['value'],'#112233ff')
 def test_shuffle_preserves_ranges_shapes_and_timing_set(self):
  ps=[self.program(1,12),self.program(2,18),self.program(3,7),dict(self.program(4),source='static')];before=copy.deepcopy(ps)
  out=variation(ps,'shuffle',rng=random.Random(2));self.assertEqual(len(out),3)
  self.assertEqual(sorted(p['fields']['Duration'] for p in out),[7,12,18]);self.assertEqual(ps,before)
  for p,q in zip(out,ps):
   for k in ('in','out','min','max','value'):self.assertEqual(p[k],q[k])
   self.assertEqual(p['fields']['PlayMode'],q['fields']['PlayMode'])
 def test_rate_is_based_on_current_variation_without_compounding(self):
  p=self.program();self.assertEqual(variation([p],'rate',2)[0]['fields']['Duration'],6);self.assertEqual(variation([p],'rate',.5)[0]['fields']['Duration'],24)
  for rate in (0,True,16,float('nan')):
   with self.assertRaises(ValueError):variation([p],'rate',rate)
 def test_lock_and_identity_gate(self):
  p=self.program();t=dict(id='source:2',kind='source',scope='clip',layer_id=3,clip_id=2,params=[{**p,'options':[]}]);c=dict(type='catalog',epoch='1',targets=[t],layers=[])
  ref=dict(id=t['id'],identity=['source','clip',3,2,None],params=[p]);data=dict(epoch='1',clips={'2':dict(targets=[ref],reference='test')});e=Engine();e.authored=Authored(data);e.reconcile(c);e.slots[1].cfg['lock']=True
  self.assertEqual(e.authored.plans(e,2,'shuffle'),[]);self.assertEqual(len(e.authored.plans(e,2,'original')),1)
  e.drive(1,True);self.assertTrue(e.slots[1].drive)
  broken=copy.deepcopy(c);broken['targets'][0]['layer_id']=4
  with self.assertRaises(ValueError):e.authored.targets(broken,2)
 def test_shuffle_keeps_paused_and_manual_parameters_out(self):
  class Slot:
   cfg={'lock':False}
  ps=[self.program(i,i*10) for i in (1,2,3)];ref=dict(id='source:2',identity=['source','clip',3,2,None],params=ps);a=Authored(dict(epoch='1',clips={'2':dict(targets=[ref],reference='test')}))
  e=Engine();e.authored=a;e.reconcile(dict(type='catalog',epoch='1',layers=[],targets=[dict(id='source:2',kind='source',scope='clip',layer_id=3,clip_id=2,params=[dict(p,options=[]) for p in ps])]))
  a.paused.add(1);e.owned.add(2);self.assertEqual([p['id'] for p in a.plans(e,2,'shuffle')],[3]);self.assertEqual([p['id'] for p in a.plans(e,2,'rate')],[1,3])
  e.slots[1].cfg['lock']=True;self.assertEqual([p['id'] for p in a.plans(e,2,'resume',ids=[1])],[1])
 def test_shuffle_uses_existing_variation_timings(self):
  ps=[self.program(i,i*10) for i in (1,2)];ref=dict(id='source:2',identity=['source','clip',3,2,None],params=ps);a=Authored(dict(epoch='1',clips={'2':dict(targets=[ref],reference='test')}));e=Engine();e.authored=a
  e.reconcile(dict(type='catalog',epoch='1',layers=[],targets=[dict(id='source:2',kind='source',scope='clip',layer_id=3,clip_id=2,params=[dict(p,options=[]) for p in ps])]))
  a.runtime['2']={'1':self.program(1,25),'2':self.program(2,35)}
  self.assertEqual(sorted(p['fields']['Duration'] for p in a.plans(e,2,'shuffle')),[25,35])
 def test_annotation_does_not_force_catalog_changes(self):
  p=dict(id=11,valuetype='ParamRange',min=0,max=1,value=.2);clip=dict(id=2,name={'value':'X'},video={'sourceparams':{'X':p}},connected={'value':'Connected'})
  c=discover(dict(name={'id':1},layers=[dict(id=3,name={'value':'Layer'},clips=[clip])]))
  c['targets'][-1]['authored']={'clip_id':2};c['targets'][-1]['params'][0]['authored']={'source':'static'}
  self.assertFalse(refresh_active(c,{3:clip})['_changed'])
 def test_reference_profiles_validate_against_original_native_ids(self):
  from build_authored import build
  native=json.loads(Path('/Users/donovan/work/0000000/shadertoy shaders/sp/heart-v2/checks/deep-clean-before-native.json').read_text()) if Path('/Users/donovan/work/0000000/shadertoy shaders/sp/heart-v2/checks/deep-clean-before-native.json').exists() else None
  if native is None:self.skipTest('Native capture not available')
  authored=Authored(json.loads(Path('authored-clips.json').read_text()))
  for l in native['layers']:
   for c in l.get('clips',[]):
    if str(c['id']) not in authored.profiles:continue
    old=l.get('active_clip');l['active_clip']=c
    try:self.assertTrue(authored.targets(discover(native),c['id']))
    finally:
     if old:l['active_clip']=old
     else:l.pop('active_clip',None)

class HeartRangeDefaults(unittest.TestCase):
 def engine(self):
  p=AuthoredPrograms().program();static=dict(p,id=4,name='Static',source='static',value=3)
  refs=dict(id='source:2',identity=['source','clip',3,2,None],params=[p,static]);e=Engine();e.authored=Authored(dict(epoch='1',auto_layers=[3],clips={'2':dict(targets=[refs],reference='original')}));e.armed=e.connected=True
  c=dict(type='catalog',epoch='1',layers=[],targets=[dict(id='source:2',label='source',kind='source',scope='clip',layer_id=3,clip_id=2,params=[dict(x,options=[]) for x in (p,static)])]);e.reconcile(c);return e,c
 def test_original_bounds_are_heart_bounds_and_static_stays_fixed(self):
  import time
  e,c=self.engine();self.assertEqual(e.clip_starts,{2});self.assertFalse(e.slots[1].drive);e.reset_clip(2)
  self.assertTrue(e.slots[1].drive);self.assertFalse(e.slots[4].drive);self.assertAlmostEqual(e.slots[1].cfg['lo'],.475);self.assertAlmostEqual(e.slots[1].cfg['hi'],.535)
  for i in range(1200):
   values=dict(e.tick(1/120,time.perf_counter()));self.assertTrue(-5<=values.get(1,0)<=7);self.assertEqual(e.current_value(4),3)
  e.drive_all(dict(epoch='1',target='source:2',on=True));self.assertFalse(e.slots[4].drive)
 def test_shuffle_retains_original_bounds_and_locks(self):
  e,c=self.engine();e.reset_clip(2);e.slots[4].cfg['lock']=True;before=copy.deepcopy(e.slots[4].cfg);bounds=(e.slots[1].cfg['lo'],e.slots[1].cfg['hi']);e.shuffle_drives(['source:2']);self.assertEqual(bounds,(e.slots[1].cfg['lo'],e.slots[1].cfg['hi']));self.assertEqual(before,e.slots[4].cfg)
 def test_revisit_restores_start_without_resetting_retained_layer(self):
  e,c=self.engine();e.reset_clip(2);e.clip_starts.clear();e.reconcile(c);self.assertFalse(e.clip_starts)
  e.reconcile(dict(type='catalog',epoch='1',targets=[],layers=[]));e.reconcile(c);self.assertEqual(e.clip_starts,{2})
