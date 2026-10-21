import copy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from dependencies import build_contract, validate_contract, ContractError

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'sp/design/heart-performance-plan/baseline'
SNAP = ROOT / 'sp/engine/patches/Feedback shaping.avc'


class DependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = json.loads((BASE / 'routing-current.json').read_text())
        cls.sources = json.loads((BASE / 'installed-sources.json').read_text())
        cls.effects = json.loads((BASE / 'installed-effects.json').read_text())
        cls.layers = json.loads(SNAP.with_suffix('.json').read_text())['layers']
        cls.contract = build_contract(SNAP, cls.live, cls.layers)

    def validate(self, **kwargs):
        args = dict(snapshot_path=SNAP, sources=self.sources, effects=self.effects)
        args.update(kwargs)
        return validate_contract(self.contract, **args)

    def test_offline_installation(self):
        self.assertEqual(self.validate(), [])

    def test_live_hidden_router_fails_closed(self):
        errors = self.validate(live_comp=self.live)
        self.assertTrue(errors)
        self.assertTrue(all('router input unavailable' in e or 'native plugin identifiers unavailable' in e for e in errors), errors)

    def test_fresh_native_snapshot(self):
        p = BASE / 'native-routing-readback.avc'
        self.assertTrue(p.exists())
        self.assertEqual(self.validate(live_comp=self.live, observed_snapshot_path=p), [])

    def test_missing_wire(self):
        fx = copy.deepcopy(self.effects)
        fx['video'] = [x for x in fx['video'] if x['idstring'] != '823bbd09-9ef5-4685-8e96-1f042f760a06']
        self.assertTrue(any('Missing effect plugin' in e for e in self.validate(effects=fx)))

    def test_display_name_is_not_plugin_identity(self):
        fx = copy.deepcopy(self.effects)
        for e in fx['video']:
            if e['idstring'] == '823bbd09-9ef5-4685-8e96-1f042f760a06':
                e['idstring'] = 'wrong-plugin-with-same-name'
        self.assertTrue(self.validate(effects=fx))

    def test_uuid_case_normalization(self):
        fx = copy.deepcopy(self.effects)
        for e in fx['video']:
            if e['idstring'] == '823bbd09-9ef5-4685-8e96-1f042f760a06':
                e['idstring'] = e['idstring'].upper()
        self.assertEqual(self.validate(effects=fx), [])

    def test_group_member_removed(self):
        live = copy.deepcopy(self.live)
        live['layergroups'][0]['layers'].pop()
        self.assertTrue(any('membership' in e for e in self.validate(live_comp=live, observed_snapshot_path=SNAP)))

    def test_live_dimensions(self):
        live = copy.deepcopy(self.live)
        live['layers'][0]['clips'][5]['video']['width']['value'] = 960
        self.assertTrue(any('dimensions' in e for e in self.validate(live_comp=live, observed_snapshot_path=SNAP)))

    def test_fresh_runtime_ids(self):
        live = copy.deepcopy(self.live)
        def replace(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k == 'id': x[k] = 123
                    else: replace(v)
            elif isinstance(x, list):
                for v in x: replace(v)
        replace(live)
        self.assertEqual(self.validate(live_comp=live, observed_snapshot_path=SNAP), [])

    def test_fresh_native_runtime_ids(self):
        r = ET.parse(SNAP)
        for e in r.iter():
            if 'uniqueId' in e.attrib: e.set('uniqueId', '456')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'observed.avc'; r.write(p)
            self.assertEqual(self.validate(live_comp=self.live, observed_snapshot_path=p), [])

    def test_wrong_plugin_same_label(self):
        r = ET.parse(SNAP)
        clip = next(c for c in r.iter('Clip') if c.get('layerIndex') == '0' and c.get('columnIndex') == '5')
        clip.findall('VideoTrack/RenderPass/RenderPass')[1].set('uniqueTypeId', 'different-plugin')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'observed.avc'; r.write(p)
            self.assertTrue(any('routing mismatch' in e for e in self.validate(live_comp=self.live, observed_snapshot_path=p)))

    def test_inactive_deck_duplicate_ignored(self):
        r = ET.parse(SNAP)
        decks = r.getroot().findall('Deck')
        clip = next(c for c in decks[0].findall('Clip') if c.get('layerIndex') == '0' and c.get('columnIndex') == '5')
        decks[1].append(copy.deepcopy(clip))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'observed.avc'; r.write(p)
            self.assertEqual(self.validate(live_comp=self.live, observed_snapshot_path=p), [])

    def test_layer_order_changes_route_meaning(self):
        r = ET.parse(SNAP)
        layers = r.getroot().findall('Layer')
        layers[0].set('layerIndex', '1'); layers[1].set('layerIndex', '0')
        # Move clips with their named layer, leaving serialized Input unchanged.
        for c in r.iter('Clip'):
            if c.get('layerIndex') in ('0', '1'):
                c.set('layerIndex', str(1 - int(c.get('layerIndex'))))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'observed.avc'; r.write(p)
            self.assertTrue(any('routing mismatch' in e for e in self.validate(live_comp=self.live, observed_snapshot_path=p)))

    def test_live_layer_order(self):
        live = copy.deepcopy(self.live)
        live['layers'][0], live['layers'][1] = live['layers'][1], live['layers'][0]
        self.assertTrue(any('layer order' in e for e in self.validate(live_comp=live, observed_snapshot_path=SNAP)))

    def test_wrong_route_same_layout(self):
        r = ET.parse(SNAP)
        clip = next(c for c in r.iter('Clip') if c.get('layerIndex') == '0' and c.get('columnIndex') == '5')
        clip.find('VideoTrack/PrimarySource/VideoSource/Params/ParamChoice').set('value', '3:4')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'observed.avc'; r.write(p)
            self.assertTrue(any('routing mismatch' in e for e in self.validate(live_comp=self.live, observed_snapshot_path=p)))

    def test_semantic_route_change(self):
        live = copy.deepcopy(self.live)
        v = live['layers'][0]['clips'][5]['video']
        v['sourceparams'] = {'Input': {'value': 'sculpt', 'options': ['sculpt', 'figure'], 'index': 0}}
        c = build_contract(SNAP, live, self.layers)
        v['sourceparams']['Input']['value'] = 'figure'
        errors = validate_contract(c, SNAP, live, self.sources, self.effects, SNAP)
        self.assertTrue(any('router input mismatch' in e for e in errors))

    def test_effect_order_changed(self):
        live = copy.deepcopy(self.live)
        fx = live['layers'][0]['clips'][5]['video']['effects']; fx[2], fx[3] = fx[3], fx[2]
        self.assertTrue(any('order' in e for e in self.validate(live_comp=live, observed_snapshot_path=SNAP)))

    def test_ambiguous_clip(self):
        live = copy.deepcopy(self.live)
        live['layers'][0]['clips'].append(copy.deepcopy(live['layers'][0]['clips'][5]))
        with self.assertRaises(ContractError): build_contract(SNAP, live, self.layers)

    def test_inactive_library_not_required(self):
        ids = {i['source_id'] for i in self.contract['instruments']}
        self.assertNotIn('33451984-d702-4253-af9e-56f21fd40696', ids)  # inactive Ground

    def test_inventory_unavailable(self):
        self.assertTrue(any('inventory unavailable' in e for e in self.validate(sources=None)))

    def test_xml_only_build(self):
        c = build_contract(SNAP, layers=self.layers)
        self.assertEqual(validate_contract(c, SNAP, sources=self.sources, effects=self.effects), [])


if __name__ == '__main__': unittest.main()

class NativeFeedbackDependencyTests(unittest.TestCase):
    def test_feedback_requires_installed_native_source(self):
        layers=json.loads(SNAP.with_suffix('.json').read_text())['layers']
        root=ET.parse(SNAP)
        for source in root.findall('.//PrimarySource/VideoSource'):
            source.clear();source.attrib.update(type='VideoSourceFeedback',width='1920',height='1080')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'feedback.avc';root.write(path)
            contract=build_contract(path,layers=layers)
            self.assertTrue(contract['instruments'])
            self.assertTrue(all(i['source_id']=='FEEDBACK_SRC' for i in contract['instruments']))
            sources=json.loads((BASE/'installed-sources.json').read_text())
            effects=json.loads((BASE/'installed-effects.json').read_text())
            self.assertEqual(validate_contract(contract,path,sources=sources,effects=effects),[])
            sources['video']=[s for s in sources['video'] if s['idstring']!='FEEDBACK_SRC']
            self.assertTrue(any('Missing source plugin: FEEDBACK_SRC' in e for e in validate_contract(contract,path,sources=sources,effects=effects)))
