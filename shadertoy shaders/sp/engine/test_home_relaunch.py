"""Offline regressions for exact Home and clip departure/relaunch."""
import concurrent.futures
import threading
import time
import copy
import json
import tempfile
from pathlib import Path
import unittest
from types import SimpleNamespace as N
from unittest.mock import patch
import heart
REAL_WCFG=heart.wcfg

class HomeRelaunchTests(unittest.TestCase):
    def setUp(self):
        for name in ('wglob','wcfg','claim_slot','event'):
            p=patch.object(heart,name);p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'RESUME',{});p.start();self.addCleanup(p.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.controls=Path(self.temp.name)/'controls.json'
        for name,value in [('CONTROL_FILE',str(self.controls)),('CONTROL_CONFIG',{}),('MOTION_FILE',str(Path(self.temp.name)/'motion.json')),('MOTION',{}),('ATOM_FILE',str(Path(self.temp.name)/'atoms.json'))]:
            p=patch.object(heart,name,value);p.start();self.addCleanup(p.stop)
    def clip(self):
        c=N(name='test',atom='TestAtom',layer=2,col=4,role='field',
            g={'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.},
            home=None,history=[],morph=3.,auto=0)
        sl=heart.Slot('Phase',True);sl.index=0;sl.identity='source/Phase'
        sl.owner='heart';sl.shape_opts=['loop','sway']
        sl.cfg={'manual':.4,'drive':True,'ratio':'1:2','mult':1,'offset':0.,
                'shape':0,'lo':.2,'hi':.8,'lock':False}
        sl.drive=True;sl.retarget(c.g,0);sl.rot=.31;c.slots=[sl]
        return c
    def home(self,c):
        with patch.object(heart,'load_homes',return_value={}), \
             patch.object(heart,'home_profile',return_value={'bindings':{},'static':{'Phase':.25}}), \
             patch.object(heart.time,'perf_counter',return_value=10.):
            heart.go_home(c)
    def settle(self,c):
        sl=c.slots[0]
        for n in range(1,401):e=sl.step(.001,10.+n*.01)
        return sl.value(e)
    def test_home_lands_exactly_after_rotating_drive_fades(self):
        c=self.clip();sl=c.slots[0];before=sl.value(sl.blend(10.))
        self.home(c)
        self.assertAlmostEqual(sl.value(sl.blend(10.)),before)
        self.assertAlmostEqual(self.settle(c),.25);self.assertFalse(sl.drive)
    def test_home_relaunch_preserves_rest_and_engine_configuration(self):
        c=self.clip();self.home(c);self.settle(c);heart.remember_clip_motion(c)
        relaunched=self.clip();heart.restore_clip_motion(relaunched);sl=relaunched.slots[0]
        self.assertFalse(sl.drive);self.assertAlmostEqual(sl.value(sl.target),.25)
        self.assertEqual(sl.cfg,c.slots[0].cfg);self.assertEqual(sl.phi,c.slots[0].phi)
        self.assertEqual(sl.rot,c.slots[0].rot)
    def test_rotation_can_start_again_after_home(self):
        c=self.clip();self.home(c);self.settle(c);sl=c.slots[0];rotation=sl.rot
        sl.drive=True;sl.retarget(c.g,15.);sl.step(.1,19.)
        self.assertGreater(sl.rot,rotation)
    def test_replacement_source_does_not_inherit_motion(self):
        c=self.clip();self.home(c);heart.remember_clip_motion(c)
        replacement=self.clip();replacement.atom='DifferentSource'
        heart.restore_clip_motion(replacement);self.assertTrue(replacement.slots[0].drive)
    def test_replacement_control_identity_does_not_inherit_motion(self):
        c=self.clip();self.home(c);heart.remember_clip_motion(c)
        replacement=self.clip();replacement.slots[0].identity='another/Phase'
        heart.restore_clip_motion(replacement);self.assertTrue(replacement.slots[0].drive)
    def test_changed_source_bounds_do_not_reinterpret_saved_motion(self):
        c=self.clip();self.home(c);heart.remember_clip_motion(c)
        replacement=self.clip();replacement.slots[0].pmax=180.
        heart.restore_clip_motion(replacement)
        self.assertTrue(replacement.slots[0].drive)
        self.assertEqual(replacement.slots[0].cfg['manual'],.4)

    def test_legacy_restart_snapshot_remains_readable(self):
        c=self.clip();heart.RESUME[(3,5)]={'slots':[{'name':'Phase','drive':False,'v':.27}]}
        heart.restore_clip_motion(c)
        self.assertAlmostEqual(c.slots[0].value(c.slots[0].target),.27)
        self.assertFalse(c.slots[0].drive)
    def test_home_commits_final_drives_once_with_absolute_pose(self):
        c=self.clip()
        second=heart.Slot('Other',False)
        second.index=1;second.identity='source/Other';second.owner='heart'
        second.shape_opts=['loop','sway'];second.cfg=copy.deepcopy(c.slots[0].cfg)
        second.drive=True;second.retarget(c.g,0);c.slots.append(second)
        for sl in c.slots:
            sl.persist_key='field/test/'+sl.identity;sl.acfg=copy.deepcopy(sl.cfg)
        with patch.object(heart.os,'replace',wraps=heart.os.replace) as replace:
            self.home(c)
        self.assertEqual(replace.call_count,1)
        stored=json.loads(self.controls.read_text())
        self.assertTrue(all(not cfg['drive'] for cfg in stored.values()))
        self.assertAlmostEqual(stored[c.slots[0].persist_key]['manual'],.25)

    def test_cold_atom_start_keeps_saved_arena_pose_and_final_drive(self):
        params={'Phase':{'id':42,'value':.63,'valuetype':'ParamRange','min':0.,'max':1.}}
        cj={'name':{'value':'test'},'_heart_layer_role':'field',
            'video':{'description':'TestAtom','sourceparams':params}}
        defaults={'TestAtom':{'Phase':dict(self.clip().slots[0].cfg,cyclic=True)}}
        with patch.object(heart,'ATOMS',defaults),patch.object(heart,'load_armsets',return_value={}):
            original=heart.Clip(2,4,cj);original.refresh(cj)
            original.slots[0].owner='heart';original.slots[0].drive=True
            self.home(original)
            saved=json.loads(self.controls.read_text())
            self.assertFalse(saved[original.slots[0].persist_key]['drive'])
            with patch.object(heart,'CONTROL_CONFIG',saved):
                cold=heart.Clip(2,4,cj);cold.refresh(cj)
            self.assertFalse(cold.slots[0].cfg['drive'])
            self.assertAlmostEqual(cold.slots[0].cfg['manual'],.63)

    def global_action(self,clips,action):
        with patch.object(heart,'motion_controllers',return_value=clips), \
             patch.object(heart,'current_controller',return_value=True), \
             patch.object(heart,'FX',{}),patch.object(heart,'STATE',{}), \
             patch.object(heart,'load_homes',return_value={}), \
             patch.object(heart,'home_profile',return_value={'bindings':{},'static':{'Phase':.25}}), \
             patch.object(heart.time,'perf_counter',return_value=10.):
            heart.play_all(action)

    def test_global_settle_exact_pose_and_single_persistence_pass(self):
        clips=[self.clip(),self.clip()]
        for index,c in enumerate(clips):
            c.name+=' '+str(index)
            sl=c.slots[0];sl.persist_key='field/'+c.name+'/'+sl.identity
            sl.acfg=copy.deepcopy(sl.cfg)
        with patch.object(heart.os,'replace',wraps=heart.os.replace) as replace:
            self.global_action(clips,'settle')
        self.assertEqual(replace.call_count,1)
        saved=json.loads(self.controls.read_text())
        for c in clips:
            self.assertAlmostEqual(self.settle(c),.25)
            self.assertFalse(saved[c.slots[0].persist_key]['drive'])
            self.assertAlmostEqual(saved[c.slots[0].persist_key]['manual'],.25)

    def test_global_open_parks_cyclic_slot_at_absolute_pose(self):
        c=self.clip();sl=c.slots[0]
        sl.persist_key='field/test/'+sl.identity;sl.acfg=copy.deepcopy(sl.cfg)
        with patch.object(heart,'opening_settings',return_value={'drive':False,'manual':.25}):
            self.global_action([c],'open')
        self.assertAlmostEqual(self.settle(c),.25)
        self.assertFalse(json.loads(self.controls.read_text())[sl.persist_key]['drive'])

    def test_global_settle_cold_start_remains_undriven(self):
        params={'Phase':{'id':42,'value':.25,'valuetype':'ParamRange','min':0.,'max':1.}}
        cj={'name':{'value':'test'},'_heart_layer_role':'field',
            'video':{'description':'TestAtom','sourceparams':params}}
        defaults={'TestAtom':{'Phase':dict(self.clip().slots[0].cfg,cyclic=True)}}
        with patch.object(heart,'ATOMS',defaults),patch.object(heart,'load_armsets',return_value={}):
            original=heart.Clip(2,4,cj);original.refresh(cj)
            original.slots[0].owner='heart';original.slots[0].drive=True
            original.slots[0].rot=.31
            self.global_action([original],'settle')
            self.assertAlmostEqual(self.settle(original),.25)
            with patch.object(heart,'CONTROL_CONFIG',json.loads(self.controls.read_text())):
                cold=heart.Clip(2,4,cj);cold.refresh(cj)
            self.assertFalse(cold.slots[0].cfg['drive'])
            self.assertAlmostEqual(cold.slots[0].cfg['manual'],.25)

    def test_concurrent_control_writers_preserve_all_updates(self):
        clips=[self.clip() for _ in range(4)]
        for index,c in enumerate(clips):
            c.name+=' '+str(index)
            sl=c.slots[0];sl.persist_key='field/'+c.name+'/'+sl.identity
            sl.acfg=copy.deepcopy(sl.cfg);sl.drive=False
        barrier=threading.Barrier(4)
        replace=heart.os.replace
        def slow_replace(src,dst):
            # Widen the original shared-temp-file collision window.
            time.sleep(.001)
            replace(src,dst)
        def writer(index):
            c=clips[index];sl=c.slots[0];barrier.wait(timeout=5)
            for n in range(20):
                if index==0:heart.persist_source_pose(c)
                elif index==1:REAL_WCFG(c,sl,'Lo',n/100.,{})
                elif index==2:
                    before=dict(sl.cfg,lo=-1)
                    heart.persist_play_settings('open',[(c,[(sl,before)])])
                else:heart.persist_performance([(c,dict(c.g),[(sl,dict(sl.cfg),{})])])
        with patch.object(heart.os,'replace',side_effect=slow_replace):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(writer,index) for index in range(4)]
                for future in futures:future.result(timeout=10)
        stored=json.loads(self.controls.read_text())
        self.assertEqual(set(stored),{c.slots[0].persist_key for c in clips})
        self.assertEqual(stored,heart.CONTROL_CONFIG)
        self.assertFalse(stored[clips[0].slots[0].persist_key]['drive'])
        self.assertEqual(stored[clips[1].slots[0].persist_key]['lo'],.19)
        self.assertFalse(stored[clips[2].slots[0].persist_key]['drive'])
        self.assertFalse(Path(str(self.controls)+'.tmp').exists())

    def test_concurrent_pose_and_config_on_same_control_keep_both(self):
        c=self.clip();sl=c.slots[0]
        sl.persist_key='field/test/'+sl.identity;sl.acfg=copy.deepcopy(sl.cfg);sl.drive=False
        barrier=threading.Barrier(2)
        def pose_writer():
            barrier.wait(timeout=5)
            for _ in range(30):heart.persist_source_pose(c)
        def range_writer():
            barrier.wait(timeout=5)
            for n in range(30):REAL_WCFG(c,sl,'Lo',n/100.,{})
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(pose_writer),pool.submit(range_writer)]
            for future in futures:future.result(timeout=10)
        saved=json.loads(self.controls.read_text())[sl.persist_key]
        self.assertFalse(saved['drive']);self.assertEqual(saved['lo'],.29)
        self.assertAlmostEqual(saved['manual'],.71)

    def test_native_owner_stays_undriven_on_restore(self):
        c=self.clip();heart.remember_clip_motion(c);replacement=self.clip()
        replacement.slots[0].owner='resolume';heart.restore_clip_motion(replacement)
        self.assertFalse(replacement.slots[0].drive)

if __name__=='__main__':unittest.main()
