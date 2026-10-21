"""Global performance actions reuse Smart Params without resetting their phases."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import heart
import test_performance_motion
class GlobalPlayTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_performance_motion.EffectMotionTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.c=self.fixture.c;self.fx=self.fixture.fx
        for sl in self.c.slots:sl.owner='heart';sl.drive=True;sl.phi=.37;sl.retarget(self.c.g,0)
        for name,value in [('CLIPS',{}),('STATE',{'hold':True}),('load_homes',lambda:{}),('home_profile',lambda c:{'bindings':{}})]:
            p=patch.object(heart,name,value);p.start();self.addCleanup(p.stop)
    def test_settle_stops_motion_and_effects_without_resetting_phase(self):
        self.fx.target=1
        heart.play_all('settle')
        self.assertEqual(self.fx.target,0)
        self.assertFalse(heart.STATE['hold'])
        self.assertTrue(all(not s.drive and s.phi==.37 for s in self.c.slots))
    def test_shuffle_preserves_ranges_drives_and_locks(self):
        first,locked=self.c.slots;locked.cfg['lock']=True
        first.cfg.update(lo=.2,hi=.8);before=dict(locked.cfg)
        heart.play_all('shuffle','harmonic')
        self.assertEqual((first.cfg['lo'],first.cfg['hi'],first.drive,first.phi),(.2,.8,True,.37))
        self.assertEqual(locked.cfg,before)
    def test_open_preserves_phase_and_starts_active_effect_motion(self):
        self.fx.env=self.fx.target=.5;self.fx.bypassed=False
        for s in self.c.slots:s.drive=False
        heart.play_all('open')
        self.assertTrue(all(s.drive and s.phi==.37 for s in self.c.slots));self.assertEqual(self.fx.target,.5)
    def test_open_preserves_active_effect_envelope(self):
        self.fx.target=.42;self.fx.env=.3
        heart.play_all('open')
        self.assertEqual(self.fx.target,.42);self.assertEqual(self.fx.env,.3)
    def test_open_leaves_parked_effect_settings_alone(self):
        self.fx.env=self.fx.target=0;self.fx.observed_bypassed=True
        for sl in self.c.slots:sl.drive=False
        before=[dict(sl.cfg) for sl in self.c.slots]
        heart.play_all('open')
        self.assertEqual([sl.cfg for sl in self.c.slots],before)
        self.assertTrue(all(not sl.drive for sl in self.c.slots))
    def test_speed_invalid_input_has_no_effect(self):
        before=dict(self.c.g)
        with self.assertRaises(ValueError):heart.play_all('speed',float('nan'))
        self.assertEqual(self.c.g,before)
    def test_replaced_controller_is_not_touched(self):
        with patch.object(heart,'current_controller',return_value=False):heart.play_all('settle')
        self.assertTrue(all(s.drive for s in self.c.slots))

    def source(self,atom):
        params={};pid=100
        def add(name,value,kind='ParamRange',**extra):
            nonlocal pid
            pid+=1;params[name]=dict(id=pid,value=value,valuetype=kind,**extra)
        for name in ('A','Locked'):
            add(name,.4,min=0.,max=1.)
            if not atom:
                for key,value,kind in [('Drive',False,'ParamBoolean'),('Ratio','1/pi','ParamChoice'),('Mult',2.,'ParamRange'),('Offset',.13,'ParamRange'),('Lo',.2,'ParamRange'),('Hi',.8,'ParamRange'),('Lock',name=='Locked','ParamBoolean')]:add(name+' '+key,value,kind)
                add(name+' Shape','sway','ParamChoice',index=1,options=['loop','sway'])
        if not atom:add('Pattern','per-slot','ParamChoice',index=0,options=heart.FAMILIES)
        if atom:
            defaults={name:dict(ratio='1/pi',mult=2.,offset=.13,shape=1,lo=.2,hi=.8,lock=name=='Locked') for name in ('A','Locked')}
            p=patch.object(heart,'ATOMS',{'Play Test':defaults});p.start();self.addCleanup(p.stop)
        cj={'name':{'value':'Play Test'},'_heart_layer_role':'figure','video':{'description':'Play Test','sourceparams':params}}
        with patch.object(heart,'load_armsets',return_value={}):c=heart.Clip(4,0,cj)
        c.refresh(cj);c.taken=True
        for sl in c.slots:sl.drive=True;sl.owner='heart';sl.phi=.37
        heart.CLIPS[(4,0)]=c
        heart.MOTION['figure/'+heart.motion_key(c)]={'timing_mode':'irrational','pattern':17,'depth':.25}
        c.refresh(cj)
        return c,cj

    def test_atom_global_gestures_survive_repeated_real_refresh(self):
        c,cj=self.source(True);locked=copy.deepcopy(c.slots[1].cfg)
        heart.play_all('shuffle','harmonic');expected=copy.deepcopy(c.slots[0].cfg)
        for _ in range(3):c.refresh(cj)
        self.assertEqual(c.g['timing_mode'],'harmonic');self.assertEqual(c.g['pattern'],0)
        self.assertNotIn(c.slots[0].cfg['ratio'],heart.IRRATIONAL_RATIOS)
        self.assertEqual(c.slots[0].cfg,expected);self.assertEqual(c.slots[1].cfg,locked)
        heart.play_all('speed',2.);heart.play_all('open')
        for _ in range(3):c.refresh(cj)
        self.assertEqual((c.g['speed'],c.g['depth']),(2.,1.))
        self.assertTrue(all(sl.drive and sl.phi==.37 for sl in c.slots))
        self.assertTrue(all((sl.cfg['lo'],sl.cfg['hi'])==(0.,1.) for sl in c.slots))
        disk=json.loads(Path(heart.MOTION_FILE).read_text());self.assertEqual(disk['figure/'+heart.motion_key(c)]['timing_mode'],'harmonic')
        self.assertEqual(json.loads(Path(heart.CONTROL_FILE).read_text())[c.slots[0].persist_key]['ratio'],expected['ratio'])

    def test_legacy_refresh_reads_committed_native_settings_without_native_drive(self):
        c,cj=self.source(False);params=cj['video']['sourceparams'];writes=[]
        def write(pid,value):
            writes.append(pid);p=next(p for p in params.values() if p['id']==pid);p['value']=value
            if 'options' in p:p['index']=p['options'].index(value)
        with patch.object(heart,'put_http',side_effect=write):
            heart.play_all('shuffle','unison');heart.play_all('speed',.5);heart.play_all('open')
        expected=[copy.deepcopy(sl.cfg) for sl in c.slots]
        for _ in range(3):c.refresh(cj)
        self.assertEqual((c.g['timing_mode'],c.g['pattern'],c.g['speed'],c.g['depth']),('unison',0,.5,1.))
        self.assertEqual([sl.cfg for sl in c.slots],expected)
        self.assertEqual(c.slots[0].cfg['ratio'],'1:1')
        self.assertNotIn(params['A Drive']['id'],writes);self.assertFalse(params['A Drive']['value'])
        self.assertTrue(all(sl.drive and sl.phi==.37 for sl in c.slots))

    def test_effect_settings_survive_refresh_and_reconstruction_with_batched_writes(self):
        c=self.c;self.fx.env=self.fx.target=.5;c.g['depth']=.2
        for sl in c.slots:sl.cfg.update(ratio='1/pi',mult=2.,offset=.13,lo=.2,hi=.8)
        with patch.object(heart.os,'replace',wraps=heart.os.replace) as replace:
            heart.play_all('shuffle','unison');self.assertEqual(replace.call_count,2)
        heart.play_all('speed',2.);heart.play_all('open')
        expected=[{k:sl.cfg[k] for k in ('ratio','mult','offset','lo','hi')} for sl in c.slots]
        c.refresh(self.fx);rebuilt=heart.EffectMotion(self.fx);rebuilt.refresh(self.fx)
        self.assertEqual((rebuilt.g['timing_mode'],rebuilt.g['speed'],rebuilt.g['depth']),('unison',2.,1.))
        self.assertEqual([{k:sl.cfg[k] for k in ('ratio','mult','offset','lo','hi')} for sl in rebuilt.slots],expected)
        self.assertTrue(all(not sl.drive for sl in rebuilt.slots),'reconstruction must not claim native ownership')

if __name__=='__main__':unittest.main()
