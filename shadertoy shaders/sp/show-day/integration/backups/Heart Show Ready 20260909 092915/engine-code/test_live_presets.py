import copy,json,tempfile,threading,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import heart
from live_presets import Store

class LivePresetTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.store=Store(self.tmp.name)
  sl=heart.Slot('Warp',False);sl.index=0;sl.owner='heart';sl.cfg=dict(manual=.3,ratio='1:1',mult=1.,offset=0.,shape=1,lo=.2,hi=.8,lock=False);sl.drive=True
  self.c=SimpleNamespace(layer=0,col=0,name='Source',slots=[sl],g=dict(pattern=0,seed=0,spread=1,depth=1.,fm=0.,speed=1.,relationship=None),auto=0,morph=1)
  sl.retarget(self.c.g,0);self.sl=sl
  self.h=SimpleNamespace(CLIPS={(0,0):self.c},LAYERS=[dict(i=1,name='figure')],FX={},capture_state=heart.capture_state,speed_value=heart.speed_value,RATIO_LIB=heart.RATIO_LIB,claim_slot=Mock(),current_controller=lambda c:c is self.c,LIVE_PRESET_LOCK=threading.RLock(),event=Mock(),persist_performance=Mock())
 def test_save_and_recall_json_without_composition_or_file_writes(self):
  self.store.save(self.h,'Flow');data=json.loads(self.store.path('Flow').read_text());self.assertEqual(data['kind'],'heart-performance')
  self.sl.cfg['hi']=.5;self.sl.retarget(self.c.g,1);self.store.load(self.h,'Flow',.5)
  self.assertEqual(self.sl.cfg['hi'],.8);self.assertEqual(self.c.morph,.5);self.h.persist_performance.assert_called_once()
  self.h.claim_slot.assert_not_called()
  self.assertEqual([p.name for p in Path(self.tmp.name).iterdir()],['Flow.json'])
 def test_missing_targets_skip_without_redirect(self):
  data=self.store.capture(self.h);self.c.name='Other';result=self.store.apply(self.h,data)
  self.assertEqual(result['targets'],0);self.assertTrue(result['skipped']);self.h.claim_slot.assert_not_called()
 def test_invalid_late_setting_is_rejected_before_any_claim(self):
  data=self.store.capture(self.h);data['amounts']['bad']=float('nan')
  with self.assertRaises(ValueError):self.store.apply(self.h,data)
  self.h.claim_slot.assert_not_called();self.assertEqual(self.sl.cfg['hi'],.8)
 def test_recall_morph_starts_at_current_signal_and_preserves_phase(self):
  data=self.store.capture(self.h);data['targets']['source/figure/Source']['slots']['Warp']['config']['hi']=.4
  self.sl.phi=.25;phase=self.sl.phi;old=self.sl.value(self.sl.target)
  self.store.apply(self.h,data,1)
  self.assertEqual(self.sl.phi,phase);self.assertAlmostEqual(self.sl.value(self.sl.blend(self.sl.t0)),old)
  self.assertAlmostEqual(self.sl.value(self.sl.blend(self.sl.t0+1)),.3)
 def test_replacement_during_preparation_does_not_commit(self):
  data=self.store.capture(self.h);data['targets']['source/figure/Source']['slots']['Warp']['config']['hi']=.4
  self.h.current_controller=lambda c:False
  with self.assertRaises(ValueError):self.store.apply(self.h,data)
  self.assertEqual(self.sl.cfg['hi'],.8)
 def test_undo_restores_prior_relationship(self):
  data=self.store.capture(self.h);data['targets']['source/figure/Source']['slots']['Warp']['config']['hi']=.4
  self.store.apply(self.h,data);self.store.undo_last(self.h);self.assertEqual(self.sl.cfg['hi'],.8)
 def test_existing_ids_are_not_saved(self):
  self.sl.ids={'':12345};data=self.store.capture(self.h)
  self.assertNotIn('12345',json.dumps(data));self.assertNotIn('composition',data)
