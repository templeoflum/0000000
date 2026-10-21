"""Shared playing actions. UI gestures use the same engine as hardware mappings."""
import copy

def hit_bindings(engine, data):
    """Validate every linked destination before changing any member."""
    if data.get('epoch') != engine.catalog['epoch']:
        raise ValueError('Composition changed; refresh the rack')
    bindings = data.get('bindings', [])
    if not isinstance(bindings, list) or not 1 <= len(bindings) <= 8:
        raise ValueError('Choose one to eight effect destinations')
    result = []; seen = set()
    for b in bindings:
        if not isinstance(b, dict): raise ValueError('Invalid rack destination')
        t = next((t for t in engine.catalog['targets'] if t['id'] == b.get('target')), None)
        if not t or t['kind'] != 'effect' or b.get('identity') != [t.get(k) for k in ('scope','layer_id','group_id','clip_id','effect_name')]:
            raise ValueError('Rack destination changed')
        params = {p['id']: p for p in t['params']}
        opacity = params.get(b.get('opacity')); bypass = params.get(b.get('bypass'))
        if not opacity or opacity['name'] != 'Opacity' or opacity['id'] not in engine.slots or (opacity['min'],opacity['max']) != (0,1):
            raise ValueError('Rack effect amount unavailable')
        if not bypass or bypass['name'] != 'Bypass' or bypass['type'] not in ('ParamBool','ParamBoolean'):
            raise ValueError('Rack effect bypass unavailable')
        event = params.get(b.get('event'))
        if 'event' in b and (not event or event['type'] not in ('ParamEvent','ParamTrigger') or event['name'] != b.get('event_name')):
            raise ValueError('Rack trigger changed')
        if opacity['id'] in seen: raise ValueError('Duplicate rack destination')
        seen.add(opacity['id']); result.append(b)
    return result


def effect_parameters(engine, ids):
    ids = list(dict.fromkeys(int(pid) for pid in ids))
    if not ids:
        raise ValueError('Choose an effect')
    for pid in ids:
        item = engine.params.get(pid)
        if not item or item[1]['name'] != 'Opacity' or pid not in engine.slots:
            raise ValueError('Effect opacity unavailable')
        if not any(t['id'] == item[0] and t['kind'] == 'effect' for t in engine.catalog['targets']):
            raise ValueError('Choose an effect opacity')
    return ids


class PlayActions:
    def __init__(self, engine):
        self.engine = engine
        self.held = {}
        self.serial = 0

    def begin(self, client, key, ids):
        ids = effect_parameters(self.engine, ids)
        if (client, key) in self.held:
            return
        self.serial += 1
        owner = f'play:{client}:{self.serial}'
        self.held[client, key] = (owner, {pid: copy.deepcopy(self.engine.contracts[pid]) for pid in ids})
        for pid in ids:
            self.engine.envelope(pid, 'in', owner=owner)

    def release(self, client=None, key=None, immediate=False):
        commands = []
        for token, (owner, members) in list(self.held.items()):
            if client is not None and token[0] != client:
                continue
            if key is not None and token[1] != key:
                continue
            self.held.pop(token)
            for pid, contract in members.items():
                if self.engine.control_owner.get(pid) != owner or self.engine.contracts.get(pid) != contract:
                    continue
                command = dict(cmd='envelope', id=pid, direction='out', _owner=owner)
                if immediate:
                    command = dict(cmd='manual', id=pid, value=self.engine.envelope_config(pid, {})['low'], _owner=owner, _duration=0)
                commands.append(command)
        return commands
