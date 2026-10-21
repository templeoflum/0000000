"""Offline effect ownership regressions. No server, transport, or disk writes.

Existing single-owner quantized release test is elsewhere.
"""
import asyncio
import unittest
from unittest.mock import patch
import heart


class EffectOwnershipTests(unittest.TestCase):
    def setUp(self):
        from effect_test_support import ClaimedExecutor
        claim_patch=patch.object(heart,'MUTATIONS',ClaimedExecutor());claim_patch.start();self.addCleanup(claim_patch.stop)
        for p in (patch.object(heart, 'FX', {}), patch.object(heart, 'FX_RELEASES', {}),
                  patch.object(heart, 'load_fx', return_value={}), patch.object(heart, 'put')):
            p.start(); self.addCleanup(p.stop)

    def effect(self, value=.35):
        fx = heart.Effect('test', 'L', 1, 0, 'Blur', 101, 102, 1.)
        fx.cfg.update(mode='momentary', attack=.01, release=.01)
        fx.env = fx.target = value
        fx.last_written = value
        fx.composition_epoch=900; fx.native_identity=777
        heart.FX[fx.key] = fx
        return fx

    def rediscover(self, pid, value, epoch=900, native_id=777):
        row = ('test', 'L', 1, 0, {'id': native_id, 'name': 'Blur', 'params': {
            'Opacity': {'id': pid, 'value': value, 'max': 1., 'valuetype': 'ParamRange'}},
            'bypassed': {'id': 102, 'value': False}})
        with patch.object(heart.targets, 'effects', return_value=[row]):
            heart.discover_fx({'name': {'id': epoch}, 'layers': []})
        return heart.FX['test']

    def test_nonzero_baseline_restored_after_last_release(self):
        for release_order in [('A', 'B'), ('B', 'A')]:
            with self.subTest(release_order=release_order):
                fx = self.effect(.35)
                fx.press(0, 'A'); fx.press(0, 'B'); fx.step(.1, 0)
                self.assertEqual(fx.env, 1.)
                fx.release(release_order[0]); self.assertEqual(fx.target, 1.)
                fx.release(release_order[1]); fx.step(.1, 0)
                self.assertEqual(fx.env, .35)
                self.assertFalse(fx.held); self.assertFalse(fx.owners)

    def test_repeated_press_same_owner_keeps_original_baseline(self):
        fx = self.effect(.35)
        fx.press(0, 'A'); fx.press(.2, 'A'); fx.release('A')
        self.assertEqual(fx.target, .35)

    def test_unrelated_client_release_does_not_drop_held_effect(self):
        fx = self.effect()
        fx.press(0, 'A'); fx.release('B')
        self.assertEqual(fx.target, 1.)
        self.assertEqual(fx.owners, {'A'})

    def test_manual_amount_wins_over_late_releases(self):
        fx = self.effect()
        fx.press(0, 'A'); fx.press(0, 'B'); fx.manual(.7)
        fx.release('A'); fx.release('B')
        self.assertEqual(fx.target, .7)
        self.assertIsNone(fx.return_target)

    def test_mode_change_then_latch_wins_over_old_release(self):
        fx = self.effect(.35)
        fx.press(0, 'A')
        # Same sequence as fx_cfg: release ownership, then apply new config.
        fx.release(); fx.cfg['mode'] = 'latch'; fx.press(0, 'B')
        fx.release('A'); fx.release('B')
        self.assertEqual(fx.target, 1.)

    def test_reconnect_restores_baseline_across_replaced_ids(self):
        fx = self.effect(.35)
        fx.press(0, 'A'); fx.step(.1, 0)
        heart.release_effects()
        new = self.rediscover(201, 1.)
        self.assertEqual(new.target, .35)
        self.assertFalse(new.owners)

    def test_id_replacement_without_disconnect_restores_held_baseline(self):
        fx = self.effect(.35)
        fx.press(0, 'A'); fx.step(.1, 0)
        new = self.rediscover(201, 1.)
        # Even an unrelated late release cannot reinstate the pressed amount.
        new.release('A')
        self.assertEqual(new.target, .35)

    def test_new_manual_intent_cancels_queued_reconnect_return(self):
        fx = self.effect(.35)
        fx.press(0, 'A'); fx.step(.1, 0)
        heart.release_effects()
        fx.manual(.7)
        new = self.rediscover(201, 1.)
        self.assertEqual(new.target, .7)


    def test_recall_new_generation_does_not_receive_old_return(self):
        fx=self.effect(.35);fx.press(0,'A');heart.release_effects()
        new=self.rediscover(201,.8,epoch=901)
        self.assertEqual(new.target,.8)

    def test_unrelated_same_key_effect_does_not_receive_old_return(self):
        fx=self.effect(.35);fx.press(0,'A');heart.release_effects()
        new=self.rediscover(201,.8,native_id=778)
        self.assertEqual(new.target,.8)

    def test_release_all_releases_presets_and_exact_effect_instance(self):
        fx=self.effect(.35);fx.press(0,'A')
        old=object();current=object();holds={(1,1,1):old,(2,1,2):current}
        owned={'test':fx}
        # A new effect under the same key belongs to another client's hold.
        replacement=self.effect(.7);replacement.press(0,'B')
        with patch.object(heart,'CLIPS',{'current':current}),patch.object(heart,'preset_mom') as release:
            asyncio.run(heart.release_surface_controls(holds,owned,'A'))
            release.assert_called_once_with(current,2,False)
        self.assertEqual(fx.target,.35)
        self.assertEqual(replacement.target,1.)
        self.assertEqual(holds,{});self.assertEqual(owned,{})

if __name__ == '__main__': unittest.main()
