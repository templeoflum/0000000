"""Both Open entry points share support-control protection without phase resets."""
import unittest
from unittest.mock import patch
import heart
import test_performance_motion


class EffectOpenTests(unittest.TestCase):
    def setUp(self):
        fixture=test_performance_motion.EffectMotionTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        self.fx=fixture.fx
        p=patch.dict(heart.STATE, hold=False);p.start();self.addCleanup(p.stop)

    def controller(self, native, names):
        heart.FX.clear();self.fx.key='layer/figure~1/effect/'+native+'~1'
        self.fx.params={name:{'id':100+i,'valuetype':'ParamRange','min':0.,'max':1.,'value':.63} for i,name in enumerate(names)}
        heart.FX[self.fx.key]=self.fx
        c=self.fx.motion=heart.EffectMotion(self.fx);c.refresh(self.fx)
        self.fx.env=self.fx.target=.5;self.fx.observed_bypassed=False;self.fx.observed_amount=.5
        for sl in c.slots:
            sl.owner='heart';sl.phi=.37;sl.phi_fm=.21
            sl.cfg.update(ratio='1:4',offset=.25,mult=2.,lo=.3,hi=.8)
            sl.retarget(c.g,0)
        return c

    def run_open(self, c, global_open):
        heart.play_all('open') if global_open else heart.open_motion(c)
        for sl in c.slots:
            self.assertEqual((sl.phi,sl.phi_fm),(.37,.21))
            self.assertEqual((sl.cfg['ratio'],sl.cfg['offset'],sl.cfg['mult']),('1:4',.25,2.))
        return {sl.name:sl for sl in c.slots}

    def test_cloners_both_open_paths(self):
        for native in ('LinearCloner','RadialCloner'):
            for global_open in (False,True):
                with self.subTest(native=native,global_open=global_open):
                    c=self.controller(native,['Start Scale','End Scale','Clones','Tails','Delay Amount','Master Rotation'])
                    slots=self.run_open(c,global_open)
                    for name in ('Start Scale','End Scale'):
                        self.assertTrue(slots[name].drive)
                        self.assertEqual((slots[name].cfg['lo'],slots[name].cfg['hi']),(.2,1.))
                    for name in ('Clones','Tails','Delay Amount'):
                        self.assertFalse(slots[name].drive);self.assertAlmostEqual(slots[name].cfg['manual'],.63)
                    self.assertTrue(slots['Master Rotation'].drive)

    def test_iterate_both_open_paths(self):
        for global_open in (False,True):
            with self.subTest(global_open=global_open):
                c=self.controller('Iterate',['StartOpacity','OpacityChange','DOpacityChange','BlendMode','Scale','TranslateX','GRotateZ','TransformStrength','Iterations'])
                slots=self.run_open(c,global_open)
                for name in ('StartOpacity','OpacityChange','DOpacityChange'):
                    self.assertFalse(slots[name].drive);self.assertEqual(slots[name].cfg['manual'],1.)
                for name in ('BlendMode','Scale','TranslateX'):
                    self.assertFalse(slots[name].drive);self.assertAlmostEqual(slots[name].cfg['manual'],.63)
                for name in ('TransformStrength','Iterations'):
                    self.assertTrue(slots[name].drive)
                    self.assertEqual((slots[name].cfg['lo'],slots[name].cfg['hi']),(.1,.35))
                self.assertTrue(slots['GRotateZ'].drive)
                self.assertEqual((slots['GRotateZ'].cfg['lo'],slots['GRotateZ'].cfg['hi']),(0.,1.))

    def test_unrelated_effect_still_opens_full_range(self):
        for global_open in (False,True):
            c=self.controller('Other',['Scale','Clones','StartOpacity'])
            for sl in self.run_open(c,global_open).values():
                self.assertTrue(sl.drive);self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(0.,1.))

    def test_transform_preserves_every_axis_in_both_open_paths(self):
        names=['Position X','Position Y','Scale','Scale W','Scale H','Rotation X',
               'Rotation Y','Rotation Z','Anchor X','Anchor Y','Anchor Z']
        for global_open in (False,True):
            with self.subTest(global_open=global_open):
                c=self.controller('Transform',names)
                for sl in self.run_open(c,global_open).values():
                    self.assertFalse(sl.drive)
                    self.assertAlmostEqual(sl.cfg['manual'],.63)
                    self.assertEqual((sl.cfg['lo'],sl.cfg['hi']),(.3,.8))


if __name__=='__main__':unittest.main()
