"""Real shared-slot behavior with isolated persistence and no running Arena."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import heart
from transport import Transport, tempo_value


class EffectMotionTests(unittest.TestCase):
    def setUp(self):
        from effect_test_support import ClaimedExecutor
        claim_patch=patch.object(heart,'MUTATIONS',ClaimedExecutor());claim_patch.start();self.addCleanup(claim_patch.stop)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        for name,value in {'FX':{},'CLIPS':{},'CONTROL_CONFIG':{},'MOTION':{},
            'CONTROL_FILE':self.tmp.name+'/controls.json','MOTION_FILE':self.tmp.name+'/motion.json',
            'HOME_FILE':self.tmp.name+'/home.json'}.items():
            p=patch.object(heart,name,value);p.start();self.addCleanup(p.stop)
        for name in ('put','put_http','claim_slot','event'):
            p=patch.object(heart,name);p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'load_fx',return_value={});p.start();self.addCleanup(p.stop)
        self.fx=heart.Effect('layer/A~1/effect/Cloner~1','L',1,1,'Cloner',1,2,1.)
        self.fx.params={'Rotation':{'id':3,'valuetype':'ParamRange','min':-180,'max':180,'value':0},
            'Count':{'id':4,'valuetype':'ParamRange','min':1,'max':50,'value':5,'view':{'display_units':'integer'}},
            'Enabled':{'id':5,'valuetype':'ParamBoolean','value':True}}
        heart.FX[self.fx.key]=self.fx
        self.c=self.fx.motion=heart.EffectMotion(self.fx);self.c.refresh(self.fx)

    def test_reset_without_saved_home_uses_connected_pose_and_stops_drive(self):
        sl=self.c.slots[0];initial=sl.cfg['manual'];sl.cfg['manual']=.9;sl.drive=True
        heart.axis_good_go(self.c,sl.name)
        self.assertEqual(sl.cfg['manual'],initial)
        self.assertFalse(sl.drive)

    def test_discovery_observes_without_taking_ownership_or_writing(self):
        self.assertEqual(len(self.c.slots),2)
        self.assertTrue(all(not sl.drive and sl.owner=='unverified' for sl in self.c.slots))
        for n in range(10):heart.step_motion(self.c,.1,n,True)
        heart.put.assert_not_called();heart.claim_slot.assert_not_called()
        self.assertEqual(heart.patch_effect_states(),{})

    def test_range_edit_after_manual_takeover_cannot_revive_old_drive(self):
        sl=self.c.slots[0];sl.owner='heart';sl.drive=True;sl.retarget(self.c.g,0)
        heart.manual_parameter(self.fx.params['Rotation'],45.)
        heart.wcfg(self.c,sl,'Lo',.1,{})
        self.assertFalse(sl.drive)
        self.assertEqual(sl.blend(sl.t0+.2)['drive'],0.)
        self.assertEqual(sl.value(sl.blend(sl.t0+.2)),.625)

    def test_manual_cyclic_value_accounts_for_accumulated_rotation(self):
        sl=self.c.slots[0];sl.owner='heart';sl.cyclic=True;sl.rot=.3;sl.drive=True;sl.retarget(self.c.g,0)
        heart.manual_parameter(self.fx.params['Rotation'],45.)
        self.assertAlmostEqual(sl.value(sl.blend(sl.t0)),.625)

    def test_open_drives_numeric_counts_and_continuous_native_ranges(self):
        heart.open_motion(self.c)
        rotation,count=self.c.slots
        self.assertTrue(rotation.drive);self.assertTrue(count.drive)
        self.assertEqual((rotation.cfg['lo'],rotation.cfg['hi']),(0.,1.))
        self.assertEqual((count.cfg['lo'],count.cfg['hi']),(0.,1.))
        self.assertEqual(heart.slot_out(rotation,.25),-90)
        self.assertEqual(heart.slot_out(count,.5),26)
        self.assertEqual(count.cfg['manual'],4/49)
        self.assertEqual(self.fx.target,1.)

    def test_home_settles_and_cancels_pulse_auto_and_pending_then_undo_restores(self):
        self.fx.env=self.fx.target=.7;heart.open_motion(self.c)
        self.c.auto=4;before=heart.capture_state(self.c);self.fx.manual(.7);self.fx.pulse();self.fx.pending=9
        heart.go_home(self.c)
        self.assertTrue(all(not sl.drive for sl in self.c.slots));self.assertEqual(self.c.auto,0)
        self.assertEqual(self.fx.target,0);self.assertIsNone(self.fx.pulse_state);self.assertIsNone(self.fx.pending)
        for _ in range(200):self.fx.step(.01,0.)
        self.assertEqual(self.fx.env,0.)
        heart.undo(self.c)
        self.assertEqual(self.fx.target,.7);self.assertEqual(self.c.auto,4)
        self.assertEqual(heart.capture_state(self.c)['slots'],before['slots'])

    def test_set_home_saves_visible_pose_and_legacy_motion_home_returns_still(self):
        sl=self.c.slots[0];sl.owner='heart';sl.drive=True;sl.phi=.25;sl.dur=0;sl.retarget(self.c.g,0)
        visible=sl.value(sl.target);heart.set_home(self.c)
        self.assertEqual(self.c.home['slots']['Rotation']['pose'],visible)
        self.assertTrue(self.c.home['slots']['Rotation']['drive'])
        self.c.slots[0].cfg['manual']=.9;heart.go_home(self.c)
        self.assertEqual(self.c.slots[0].cfg['manual'],visible)
        self.assertFalse(self.c.slots[0].drive)

    def test_open_keeps_timing_and_undo_restores_ranges_and_envelope(self):
        sl=self.c.slots[0];sl.cfg.update(lo=.2,hi=.6,lock=True,ratio='1:4');self.c.g['speed']=.25
        self.fx.env=self.fx.target=.35;before=heart.capture_state(self.c)
        heart.open_motion(self.c)
        self.assertEqual(self.c.g['speed'],.25);self.assertEqual(sl.cfg['ratio'],'1:4');self.assertFalse(sl.cfg['lock'])
        heart.undo(self.c)
        self.assertEqual(self.fx.target,.35);self.assertEqual(heart.capture_state(self.c),before)

    def test_motion_writes_real_values_at_existing_delivery_cadence(self):
        sl=self.c.slots[0];sl.owner='heart';sl.drive=True;self.c.morph=0
        with patch.dict(heart.STATE,arena_connected=True):
            for n in range(240):heart.step_motion(self.c,1/240,n/240,False)
        values=[call.args[1] for call in heart.put.call_args_list if call.args[0]==3]
        self.assertGreater(len(set(values)),20);self.assertLessEqual(len(values),60)
        self.assertTrue(all(-180<=v<=180 for v in values))

    def test_rebind_changes_instance_and_does_not_redirect_ongoing_drive(self):
        old=self.fx.instance;self.c.slots[0].drive=True
        self.fx.params['Rotation']['id']=300;self.c.refresh(self.fx)
        with self.assertRaises(ValueError):heart.validate_surface_target({'cmd':'manual','effect':self.fx.key,'instance':old})
        self.assertFalse(self.c.slots[0].drive)
        self.assertEqual(self.c.slots[0].ids[''],300)

    def test_refresh_preserves_unchanged_slots_and_relationship_members(self):
        heart.open_motion(self.c);old=self.c.slots[0];relationship=copy.deepcopy(self.c.g['relationship'])
        self.fx.params['New']={'id':9,'valuetype':'ParamFloat','min':0,'max':1,'value':.4}
        self.c.refresh(self.fx)
        self.assertIs(self.c.slots[0],old);self.assertTrue(old.drive)
        self.assertFalse(self.c.slots[-1].drive);self.assertEqual(self.c.g['relationship'],relationship)

    def test_home_and_undo_are_scoped_and_roundtrip_effect_relationships(self):
        before=heart.capture_state(self.c);heart.go_home(self.c);heart.set_home(self.c)
        import json
        with open(heart.HOME_FILE) as f:homes=json.load(f)
        self.assertIn('effect:'+self.fx.key,homes);self.assertNotIn('Cloner',homes)
        heart.undo(self.c)
        self.assertEqual(heart.capture_state(self.c)['slots'],before['slots'])
        self.c.slots[0].owner="heart"
        states=heart.patch_effect_states();self.assertEqual(states[self.fx.key]['version'],2)

    def test_downbeat_realigns_phases_without_changing_relationships(self):
        sl=self.c.slots[0];sl.phi=3.4;sl.phi_fm=9.2;sl.rot=.7;g=copy.deepcopy(self.c.g)
        self.fx.pending=7.;self.fx.hold_until=8.
        heart.align_motion(20.)
        self.assertEqual((sl.phi,sl.phi_fm,sl.rot),(0.,0.,0.));self.assertEqual(self.c.g,g)
        self.assertEqual(self.fx.pending,2.);self.assertEqual(self.fx.hold_until,3.)


class PulseTests(unittest.TestCase):
    def setUp(self):
        from effect_test_support import ClaimedExecutor
        claim_patch=patch.object(heart,'MUTATIONS',ClaimedExecutor());claim_patch.start();self.addCleanup(claim_patch.stop)
        with patch.object(heart,'load_fx',return_value={}):self.e=heart.Effect('pulse','L',1,1,'test',1,2,1.)
        self.p=patch.object(heart,'put');self.p.start();self.addCleanup(self.p.stop)

    def finish(self):
        for _ in range(150):self.e.step(.01,0.)

    def test_opposite_pulse_returns_nonzero_baseline_while_clock_held(self):
        for baseline,endpoint in ((.37,1.),(.83,0.)):
            self.e.env=self.e.target=baseline;self.e.pulse()
            self.assertEqual(self.e.target,endpoint);self.finish()
            self.assertAlmostEqual(self.e.env,baseline);self.assertIsNone(self.e.pulse_state)

    def test_retrigger_keeps_original_baseline(self):
        self.e.env=self.e.target=.8;self.e.pulse();self.e.step(.02,0)
        self.e.pulse();self.assertEqual(self.e.pulse_state['baseline'],.8)
        self.finish();self.assertAlmostEqual(self.e.env,.8)

    def test_new_manual_intent_cancels_return(self):
        self.e.env=self.e.target=.2;self.e.pulse();self.e.manual(.6);self.finish()
        self.assertIsNone(self.e.pulse_state);self.assertAlmostEqual(self.e.env,.6)

    def test_latch_interrupts_pulse_using_baseline_not_pulse_endpoint(self):
        self.e.env=self.e.target=.8;self.e.pulse();self.e.press(0);self.finish()
        self.assertEqual(self.e.env,0.);self.assertIsNone(self.e.pulse_state)


class TransportTests(unittest.TestCase):
    def test_taps_estimate_tempo_and_ignore_doubletap(self):
        t=Transport();self.assertIsNone(t.tap(0));self.assertEqual(t.tap(.5),120.)
        self.assertIsNone(t.tap(.54));self.assertEqual(t.tap(1.01),60/.505)
        self.assertIsNone(t.tap(5.));self.assertEqual(len(t.taps),1)

    def test_phrase_and_downbeat_are_independent_of_motion_hold(self):
        t=Transport()
        for _ in range(20):t.advance(.25,120)
        self.assertEqual(t.snapshot(8,0)['beat'],3)
        self.assertEqual(t.snapshot(8,0)['bar'],3)
        t.downbeat();self.assertEqual(t.advance(0,120),10)
        self.assertEqual(t.snapshot(8,0)['beat'],1);self.assertEqual(t.snapshot(8,0)['phase'],0)
        self.assertIsNone(t.advance(0,120))

    def test_sleep_gap_does_not_replay_elapsed_hours(self):
        t=Transport();t.advance(3600,120);self.assertEqual(t.beats,.5)
        for value in (float('nan'),float('inf'),0,501):
            with self.assertRaises(ValueError):tempo_value(value)


if __name__=='__main__':unittest.main()
