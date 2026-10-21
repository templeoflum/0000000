"""Nine starting motions use exact native contracts and retain their saved pose."""
import copy
import hashlib
import json
import math
from pathlib import Path
import unittest

from authored import Authored, heart_seed
from scan import discover
from server import Engine

ROOT = Path(__file__).parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class StartingMotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'authored-clips.json').read_text())
        cls.report = json.loads((ROOT / 'checks/session-starting-motion.json').read_text())
        cls.native = json.loads((ROOT / 'checks/session-native-before.json').read_text())
        cls.added = {c['parameter']: c for c in cls.report['controls']}
        # Preserve the original preparation evidence and its unchanged-parameter
        # hashes. The later camera pass supersedes only these existing programs.
        strengthened = ROOT / 'checks/session-field-motion-strengthened.json'
        if strengthened.exists():
            current = json.loads(strengthened.read_text())
            if current['composition_epoch'] != cls.data['epoch']:
                raise AssertionError('Strengthened motion belongs to another composition')
            for control in current['controls']:
                previous = cls.added[control['parameter']]
                for key in ('clip', 'clip_id', 'layer_id', 'target', 'control', 'value'):
                    if control[key] != previous[key]:
                        raise AssertionError('Strengthened motion changed an original identity or pose')
                cls.added[control['parameter']] = {**previous, **control}

    def test_existing_timelines_and_other_parameters_preserved(self):
        untouched = [(cid, t['id'], p) for cid, c in self.data['clips'].items()
                     for t in c['targets'] for p in t['params'] if p['id'] not in self.added]
        old_timelines = [(cid, tid, p) for cid, tid, p in untouched if p.get('source') == 'timeline']
        proof = self.report['preservation']
        self.assertEqual(len(old_timelines), proof['existing_timelines'])
        self.assertEqual(digest(old_timelines), proof['existing_timeline_sha256'])
        self.assertEqual(digest(untouched), proof['unmodified_parameter_sha256'])

    def test_nine_clips_bind_and_start_at_saved_value(self):
        seen = set()
        for layer in self.native['layers']:
            for clip in layer['clips']:
                controls = [c for c in self.added.values() if c['clip_id'] == clip['id']]
                if not controls:
                    continue
                with self.subTest(clip=controls[0]['clip']):
                    native = copy.deepcopy(self.native)
                    live_layer = next(l for l in native['layers'] if l['id'] == layer['id'])
                    live_layer['active_clip'] = copy.deepcopy(clip)
                    engine = Engine()
                    engine.authored = Authored(copy.deepcopy(self.data))
                    engine.reconcile(discover(native))
                    self.assertTrue(engine.authored.targets(engine.catalog, clip['id']))
                    start = dict(engine.reset_clip(clip['id']))
                    for item in controls:
                        pid = item['parameter']
                        slot = engine.slots[pid]
                        param = engine.params[pid][1]
                        seed = heart_seed(param, engine.bpm)
                        self.assertTrue(slot.drive)
                        self.assertEqual(param['authored']['fields']['Duration'], item['nominal_seconds'])
                        self.assertAlmostEqual(param['authored']['phase'], item['phase'], places=10)
                        self.assertAlmostEqual(start[pid], item['value'], places=10)
                        self.assertAlmostEqual(seed['manual'], (item['value'] - param['min']) / (param['max'] - param['min']))
                        samples = []
                        # Cover a complete waveform independently of musical rate, including both limits.
                        for i in range(1201):
                            slot.phi = i / 1200
                            value = param['min'] + slot.value(slot.target) * (param['max'] - param['min'])
                            self.assertGreaterEqual(value, item['low'] - 1e-10)
                            self.assertLessEqual(value, item['high'] + 1e-10)
                            samples.append(value)
                        self.assertGreater(max(samples) - min(samples), .99 * (item['high'] - item['low']))
                        self.assertLess(max(abs(b - a) for a, b in zip(samples, samples[1:])), .004 * (item['high'] - item['low']))
                    seen.add(controls[0]['clip'])
        self.assertEqual(seen, {'1d', '2d', '3d', '4d', 'shell', 'hybrid', 'ground', 'room', 'void'})

    def test_motion_does_not_touch_mixing_geometry_counts_or_integrated_rates(self):
        forbidden = {'Opacity', 'Bypass', 'Layers', 'Count', 'Density', 'Quality', 'Resolution', 'Rate', 'Flow'}
        for control in self.added.values():
            self.assertNotIn(control['control'], forbidden)
            if control['clip'] in ('4d', 'hybrid'):
                self.assertNotIn(control['control'], ('Turn', 'Spin'))
            self.assertLessEqual(control['low'], control['value'])
            self.assertGreaterEqual(control['high'], control['value'])
        line = next(c for c in self.data['clips'].values() if c['name'] == '1d')
        params = next(t['params'] for t in line['targets'] if t['identity'][-1] == 'SPAtomLine')
        opacity = next(p for p in params if p['name'] == 'Opacity')
        self.assertEqual(opacity['value'], 0)
        self.assertEqual(opacity['source'], 'static')


if __name__ == '__main__':
    unittest.main()
