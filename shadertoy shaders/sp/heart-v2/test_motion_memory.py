import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from motion_memory import MotionMemory, key, slot_settings
from scan import discover
from server import Engine
import test_phase_detection as detection


def catalog():
    return detection.DetectionTests().prepare(discover(detection.fixture()), now=time.perf_counter())[0]


def started(c=None):
    e = Engine(); e.reconcile(c or catalog()); e.armed = e.connected = True; e.start_prepared()
    return e


def without_source(c):
    c = copy.deepcopy(c)
    c['targets'] = [t for t in c['targets'] if t.get('clip_id') != 40]
    c['layers'][0]['active'] = 0
    return c


class MotionMemoryTests(unittest.TestCase):
    def test_clip_revisit_restores_shuffled_family_and_every_motion_control(self):
        c = catalog(); e = started(c); tid = 'source:40'
        e.relationship(tid, dict(pattern=4, spread=2, seed=3, fm=.25, seconds=0))
        e.settings(tid, dict(amount=.4, rate=.025, seconds=0))
        e.shuffle_drives([tid])
        e.parameter_motion(5, dict(ratio='2:3', mult=-.025, amount=.2, range_offset=.7, shape=.3, seconds=0))
        e.parameter_lock(dict(epoch='10', id=5, on=True))
        before = copy.deepcopy(e.slots[5].cfg); group = copy.deepcopy(e.groups[tid])
        e.drive(5, False)
        e.reconcile(without_source(c)); e.tick(.1, time.perf_counter()+1)
        self.assertNotIn(5, e.slots)
        e.reconcile(c); e.start_prepared()
        self.assertEqual(slot_settings(e.slots[5].cfg), slot_settings(before))
        self.assertEqual(e.groups[tid], group)
        self.assertFalse(e.slots[5].drive)
        self.assertNotIn(5, e.owned)

    def test_app_restart_keeps_settings_but_not_old_native_pose_or_phase(self):
        c = catalog(); e = started(c)
        e.parameter_motion(5, dict(ratio='1:3', offset=.71, mult=.025, amount=.3, range_offset=.4))
        e.settings('source:40', dict(rate=2, amount=.7))
        e.slots[5].phi = 812.4; e.slots[5].cfg['manual'] = .93
        e.motion_multiplier(dict(epoch='10', scope='global', value=.5))
        e.drive(2, False); e.disarm(); e.motion_memory.capture(e)
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'motion-settings.json'; MotionMemory.write(path, e.motion_memory.data)
            fresh = Engine(); fresh.motion_memory.load(path)
            tuned = copy.deepcopy(c); p = next(p for t in tuned['targets'] for p in t['params'] if p['id'] == 5)
            p.update(value=.75, **{'in': .7, 'out': .9})
            original = copy.deepcopy(tuned); fresh.reconcile(tuned)
            self.assertFalse(fresh.armed); self.assertEqual(fresh.owned, set()); self.assertFalse(fresh.slots[5].drive)
            self.assertEqual(fresh.slots[5].cfg['ratio'], '1:3'); self.assertEqual(fresh.slots[5].phi, 0)
            self.assertAlmostEqual(fresh.slots[5].cfg['manual'], .25)
            self.assertEqual(fresh.motion_multipliers['global']['value'], .5)
            self.assertEqual(fresh.groups['source:40']['speed'], 2)
            fresh.armed = fresh.connected = True; fresh.start_prepared()
            self.assertTrue(fresh.slots[5].drive); self.assertFalse(fresh.slots[2].drive)
            self.assertEqual(tuned, original, 'Recall must not edit native values or programs')
            raw = path.read_text()
            for field in ('manual', 'native_phase', 'phi', 'started', 'lo', 'hi'):
                self.assertNotIn('"'+field+'":', raw)

    def test_mode_detection_loss_preserves_preferences_without_driving_native_mode(self):
        c = catalog(); e = started(c)
        e.parameter_motion(5, dict(ratio='1:4', mult=.3, offset=.2)); e.drive(5, False)
        unprepared = copy.deepcopy(c)
        for t in unprepared['targets']:
            for p in t['params']: p.pop('native_phase', None)
        e.reconcile(unprepared); e.start_prepared()
        self.assertFalse(e.slots[5].drive); self.assertNotIn(5, e.owned)
        self.assertEqual(e.slots[5].cfg['ratio'], '1:4')
        e.reconcile(c); e.start_prepared()
        self.assertFalse(e.slots[5].drive); self.assertTrue(e.slots[2].drive)
        self.assertEqual(e.slots[5].cfg['mult'], .3)

    def test_rearm_keeps_explicit_off_and_restarts_previously_enabled(self):
        e = started(); e.drive(5, False); e.disarm()
        e.armed = e.connected = True
        e.phase_starts.update((2, 5)); e.start_prepared()
        self.assertFalse(e.slots[5].drive); self.assertTrue(e.slots[2].drive)

    def test_replaced_parameter_or_shader_cannot_inherit_settings(self):
        c = catalog(); e = started(c)
        e.parameter_motion(5, dict(mult=.025)); e.relationship('source:40', dict(pattern=4))
        renamed = copy.deepcopy(c)
        t = next(t for t in renamed['targets'] if t['id'] == 'source:40'); t['params'][0]['name'] = 'Different parameter'
        e.reconcile(renamed); self.assertEqual(e.slots[5].cfg['mult'], 1)
        replaced = copy.deepcopy(c); t = next(t for t in replaced['targets'] if t['id'] == 'source:40'); t['description'] = 'Different source'
        e.reconcile(replaced); self.assertEqual(e.groups['source:40']['pattern'], 0); self.assertEqual(e.slots[5].cfg['mult'], 1)

    def test_compositions_keep_separate_settings_with_same_parameter_ids(self):
        c = catalog(); e = started(c); e.parameter_motion(5, dict(mult=.025))
        other = copy.deepcopy(c); other['epoch'] = 'different'
        e.reconcile(other); self.assertEqual(e.slots[5].cfg['mult'], 1)
        e.parameter_motion(5, dict(mult=4)); e.reconcile(c)
        self.assertEqual(e.slots[5].cfg['mult'], .025)
        e.reconcile(other); self.assertEqual(e.slots[5].cfg['mult'], 4)

    def test_route_reordering_recalls_settings_but_uses_new_binding(self):
        c = catalog(); e = started(c); e.parameter_motion(5, dict(mult=.025))
        c = copy.deepcopy(c); p = next(p for t in c['targets'] for p in t['params'] if p['id'] == 5)
        p['native_phase']['address'] = p['native_phase']['address'].replace('/layers/1/', '/layers/2/')
        e.reconcile(c); e.start_prepared()
        self.assertEqual(e.slots[5].cfg['mult'], .025); self.assertNotIn(5, e.retained)
        self.assertIn('/layers/2/', e.binding()['phases'][5]['address'])

    def test_scope_multipliers_survive_empty_layer_and_restart(self):
        c = catalog(); e = started(c)
        e.motion_multiplier(dict(epoch='10', scope='layer', layer_id=20, value=.025))
        empty = copy.deepcopy(c); empty['targets'] = []
        e.reconcile(empty); self.assertEqual(e.motion_multipliers['layer:20']['value'], .025)
        fresh = Engine(); fresh.motion_memory.data = copy.deepcopy(e.motion_memory.data); fresh.reconcile(c)
        self.assertEqual(fresh.motion_multipliers['layer:20']['value'], .025)

    def test_stage_family_position_restored_only_in_valid_scope(self):
        c = catalog(); e = started(c)
        e.parameter_motion(5, dict(scope_family=dict(scope='layer:20', pattern=13, slot=7)))
        e.reconcile(without_source(c)); e.reconcile(c)
        self.assertEqual(e.slots[5].cfg['scope_family'], dict(scope='layer:20', pattern=13, slot=7))
        target = next(t for t in c['targets'] if t['id'] == 'source:40')
        e.motion_memory.data['compositions']['10']['targets'][key(target)]['params']['5']['cfg']['scope_family']['scope'] = 'stage:999:gone'
        fresh = Engine(); fresh.motion_memory.data = copy.deepcopy(e.motion_memory.data); fresh.reconcile(c)
        self.assertNotIn('scope_family', fresh.slots[5].cfg)

    def test_memory_excludes_motion_frames_and_repeated_inspections_do_not_dirty(self):
        e = started(); e.motion_memory.capture(e); revision = e.motion_memory.revision
        for n in range(5):
            e.tick(.01, time.perf_counter()+n*.01); e.reconcile(copy.deepcopy(e.catalog)); e.motion_memory.capture(e)
        self.assertEqual(e.motion_memory.revision, revision)

    def test_malformed_saved_settings_are_ignored_per_field(self):
        e = started(); e.motion_memory.capture(e); data = copy.deepcopy(e.motion_memory.data)
        row = next(row for row in data['compositions']['10']['targets'].values() if row['identity'][0] == 'source:40')
        row['group'].update(pattern=900, speed=float('nan'))
        row['params']['5']['cfg'].update(ratio=[], mult=float('inf'), amount=9, offset=.3, scope_family={'pattern': []})
        fresh = Engine(); fresh.motion_memory.data = data; fresh.reconcile(catalog())
        self.assertEqual(fresh.groups['source:40']['pattern'], 0); self.assertEqual(fresh.slots[5].cfg['mult'], 1)
        self.assertEqual(fresh.slots[5].cfg['offset'], .3)

    def test_failed_atomic_replace_keeps_previous_file(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'motion-settings.json'; path.write_text('previous')
            with patch.object(Path, 'replace', side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError): MotionMemory.write(path, {'version': 1})
            self.assertEqual(path.read_text(), 'previous')


if __name__ == '__main__': unittest.main()
