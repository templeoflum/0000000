"""Last-used motion settings, independent of native programs and runtime clocks."""
import copy
import hashlib
import json
import math
from pathlib import Path

from smart_motion import FAMILIES, RATIO_LIB


def identity(target):
    return [target.get(k) for k in ('id', 'kind', 'scope', 'layer_id', 'group_id', 'clip_id', 'effect_name', 'description')]


def contract(parameter):
    # Routes, animation mode and native In/Out may change during ordinary tuning.
    return [parameter.get(k) for k in ('id', 'name', 'type', 'min', 'max', 'options')]


def key(target):
    return hashlib.sha256(json.dumps(identity(target), separators=(',', ':')).encode()).hexdigest()


def number(value, low, high, integer=False):
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high and (not integer or value == int(value))


def group_settings(raw):
    if not isinstance(raw, dict): return {}
    bounds = {'pattern': (0, len(FAMILIES)-1, True), 'spread': (0, 16, True), 'seed': (0, 127, True), 'depth': (0, 1, False), 'fm': (0, 4, False), 'speed': (.001, 64, False)}
    return {k: raw[k] for k, (lo, hi, whole) in bounds.items() if number(raw.get(k), lo, hi, whole)}


def slot_settings(raw):
    if not isinstance(raw, dict): return {}
    out = {}
    if isinstance(raw.get('ratio'), str) and raw['ratio'] in RATIO_LIB: out['ratio'] = raw['ratio']
    if number(raw.get('mult'), -16, 16) and (raw['mult'] == 0 or abs(raw['mult']) >= .001): out['mult'] = raw['mult']
    for name in ('offset', 'shape', 'amount', 'range_offset'):
        if number(raw.get(name), 0, 1): out[name] = raw[name]
    if type(raw.get('lock')) is bool: out['lock'] = raw['lock']
    if number(raw.get('family_slot'), 0, 10000, True): out['family_slot'] = int(raw['family_slot'])
    family = raw.get('scope_family')
    if isinstance(family, dict) and isinstance(family.get('scope'), str) and number(family.get('pattern'), 0, len(FAMILIES)-1, True) and number(family.get('slot'), 0, 10000, True):
        out['scope_family'] = {k: family[k] for k in ('scope', 'pattern', 'slot')}
    return out


class MotionMemory:
    def __init__(self):
        self.data = {'version': 1, 'compositions': {}}
        self.revision = self.saved_revision = 0

    def load(self, path):
        path = Path(path)
        if not path.exists(): return
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('compositions'), dict):
            raise ValueError('Unsupported motion settings file')
        json.dumps(data, allow_nan=False)
        # Validate lazily against the current native identities before use.
        self.data = data

    def composition(self, epoch):
        row = self.data['compositions'].get(str(epoch), {})
        return row if isinstance(row, dict) else {}

    def target(self, epoch, target):
        rows = self.composition(epoch).get('targets', {})
        row = rows.get(key(target), {}) if isinstance(rows, dict) else {}
        return row if isinstance(row, dict) and row.get('identity') == identity(target) else {}

    def parameter(self, epoch, target, parameter):
        rows = self.target(epoch, target).get('params', {})
        row = rows.get(str(parameter['id']), {}) if isinstance(rows, dict) else {}
        return row if isinstance(row, dict) and row.get('contract') == contract(parameter) else {}

    def capture(self, engine, targets=None):
        if not engine.catalog.get('native_phase_mode'): return
        epoch = str(engine.catalog['epoch'])
        previous = self.composition(epoch)
        stored = previous.get('targets', {})
        if not isinstance(stored, dict): stored = {}
        rows = dict(stored)
        for target in engine.catalog['targets']:
            if targets is not None and target['id'] not in targets: continue
            params = self.target(epoch, target).get('params', {})
            params = dict(params) if isinstance(params, dict) else {}
            for p in target['params']:
                sl = engine.slots.get(p['id'])
                if not sl: continue
                row = dict(contract=contract(p), cfg=slot_settings(sl.cfg))
                intent = getattr(sl, 'drive_intent', None)
                if type(intent) is bool: row['drive'] = intent
                params[str(p['id'])] = row
            if params:
                rows[key(target)] = dict(identity=identity(target), group=group_settings(engine.groups[target['id']]), params=params)
        scopes = previous.get('scopes', {})
        scopes = dict(scopes) if isinstance(scopes, dict) else {}
        scopes.update({k: r['value'] for k, r in engine.motion_multipliers.items()})
        current = dict(targets=rows, scopes=scopes)
        if current != previous:
            self.data['compositions'][epoch] = current
            self.revision += 1

    def restore_slot(self, epoch, target, parameter, slot):
        row = self.parameter(epoch, target, parameter)
        slot.cfg.update(slot_settings(row.get('cfg')))
        slot.drive_intent = row.get('drive') if type(row.get('drive')) is bool else None

    def restore_scopes(self, engine):
        raw = self.composition(engine.catalog['epoch']).get('scopes', {})
        if not isinstance(raw, dict): return
        for k in engine.valid_motion_scopes():
            v = raw.get(k)
            if k not in engine.motion_multipliers and number(v, .001, 64):
                engine.motion_multipliers[k] = dict(value=v, **{'from': v}, started=0., seconds=0.)

    def snapshot(self):
        return self.revision, copy.deepcopy(self.data)

    @staticmethod
    def write(path, data):
        path = Path(path)
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False))
        tmp.replace(path)
