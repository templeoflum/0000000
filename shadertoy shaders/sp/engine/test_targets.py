import unittest
import targets
class TargetTests(unittest.TestCase):
 def test_distinct_instances_and_reorder(self):
  a={'name':'Blur','params':{}};b={'name':'Sharpen','params':{}}
  def keys(items):return [x[0] for x in targets.effects({'video':{'effects':items}})]
  self.assertEqual(set(keys([a,b])),set(keys([b,a])))
  self.assertEqual(len(set(keys([a,a]))),2)
 def test_scope_and_active_clip(self):
  e={'name':'Blur','params':{}}
  comp={'video':{'effects':[e]},'layers':[{'name':{'value':'a'},'video':{'effects':[e]},'clips':[{'name':{'value':'a'},'connected':{'value':'Connected'},'video':{'effects':[e]}}]}],'layergroups':[{'name':{'value':'g'},'video':{'effects':[e]}}]}
  found=list(targets.effects(comp));self.assertEqual(len(found),4);self.assertEqual(len({x[0] for x in found}),4)
 def test_conversions(self):
  self.assertEqual(targets.convert({'valuetype':'ParamInt','min':0,'max':10},4.8),5)
  with self.assertRaises(ValueError):targets.convert({'valuetype':'ParamRange'},float('nan'))
  with self.assertRaises(ValueError):targets.convert({'valuetype':'ParamBool'},1)
  with self.assertRaises(ValueError):targets.convert({'valuetype':'ParamChoice','options':['a']},'b')
  self.assertEqual(targets.convert({'valuetype':'ParamColor'},'#112233'),'#112233ff')
if __name__=='__main__':unittest.main()

class OperationTests(unittest.TestCase):
 def test_cancel_discards_stale_writes(self):
  from patches import Operations,Cancelled
  o=Operations();o.number=1;out=[]
  o.write(1,out.append,'first');o.cancel()
  with self.assertRaises(Cancelled):o.write(1,out.append,'stale')
  self.assertEqual(out,['first']);o.pool.shutdown()
 def test_latest_queued_recall_wins(self):
  from patches import Operations
  import threading
  o=Operations();started=threading.Event();release=threading.Event();out=[]
  def slow(t):started.set();release.wait(2);o.write(t,out.append,'old')
  f=o.submit(slow);self.assertTrue(started.wait(1))
  a=o.submit(lambda t:o.write(t,out.append,'middle'))
  b=o.submit(lambda t:o.write(t,out.append,'new'));release.set()
  for x in [f,a,b]:x.result(3)
  self.assertEqual(out,['new']);o.pool.shutdown()

class IntegrationTests(unittest.TestCase):
 def test_duplicate_atom_controls_keep_separate_targets(self):
  import heart,copy
  from unittest.mock import patch
  def p(pid,v):return {'id':pid,'valuetype':'ParamRange','min':0.,'max':1.,'value':v}
  c={'name':{'value':'fixture'},'video':{'description':'TestA','sourceparams':{'Gain':p(1,.2)},'effects':[{'name':'TestB','params':{'Gain':p(2,.8)}}]}}
  with patch.object(heart,'ATOMS',{'TestA':{},'TestB':{}}),patch.object(heart,'save_atoms'),patch.object(heart,'load_armsets',return_value={}):
   clip=heart.Clip(0,0,c);clip.refresh(c)
   self.assertEqual(len(clip.slots),2)
   self.assertEqual({s.ids[''] for s in clip.slots},{1,2})
   self.assertEqual({s.cfg['manual'] for s in clip.slots},{.2,.8})
   self.assertEqual(len({s.identity for s in clip.slots}),2)
   state=heart.capture_state(clip)
   self.assertEqual(len(state['slots']),2)
 def test_momentary_multiple_owners_restore_prior_amount(self):
  import heart
  from unittest.mock import patch
  with patch.object(heart,'load_fx',return_value={}):e=heart.Effect('test','L',1,1,'test',1,2,1)
  e.env=e.target=.35;e.last_written=.35;e.cfg['mode']='momentary'
  e.press(0,'mouse');e.press(0,'key');e.release('mouse');self.assertEqual(e.target,1)
  e.release('key');self.assertEqual(e.target,.35)
 def test_manual_effect_takeover_cancels_old_release(self):
  import heart
  from unittest.mock import patch
  with patch.object(heart,'load_fx',return_value={}):e=heart.Effect('test','L',1,1,'test',1,2,1)
  e.cfg['mode']='momentary';e.press(0,'a');e.manual(.6);e.release('a')
  self.assertEqual(e.target,.6)
 def test_snapshot_preflight_rejects_missing_clip(self):
  from patches import validate_snapshot
  import tempfile,pathlib
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'x.avc';p.write_text('<Composition><Layer layerIndex="0"><Params><Param name="Name" value="feedback"/></Params></Layer><Deck/></Composition>')
   with self.assertRaises(ValueError):validate_snapshot(p,{'feedback':{'clip':'missing'}})

class LegacyTests(unittest.TestCase):
 def test_duplicate_legacy_slots_keep_companion_controls_together(self):
  import heart
  def effect(name,pid):return {'name':name,'params':{'Hue':{'id':pid,'value':.5},'Hue Drive':{'id':pid+1,'value':True},'Hue Shape':{'id':pid+2,'options':['rotate','sway'],'index':1}}}
  clip={'video':{'effects':[effect('A',10),effect('B',20)]}}
  params=heart.allparams(clip)
  names=[n[:-6] for n in params if n.endswith(' Drive')]
  self.assertEqual(len(names),2)
  for n in names:self.assertEqual(params[n+' Drive']['id'],params[n]['id']+1)
 def test_release_survives_effect_id_replacement(self):
  import heart
  from unittest.mock import patch
  def comp(pid):return {'name':{'id':900},'video':{'effects':[{'id':777,'name':'Blur','params':{'Opacity':{'id':pid,'value':.8,'max':1}}}]}}
  with patch.object(heart,'FX',{}),patch.object(heart,'FX_RELEASES',{}),patch.object(heart,'load_fx',return_value={}):
   heart.discover_fx(comp(1));e=next(iter(heart.FX.values()));e.cfg['mode']='momentary';e.target=.25;e.press(0,'a')
   heart.release_effects();heart.discover_fx(comp(2));e=next(iter(heart.FX.values()))
   self.assertEqual(e.target,.25)
