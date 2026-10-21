"""Rack sequencing and two scoped recovery points. No native IO in the clock."""
import copy
import json
import math
import time

NUM = {'ParamRange', 'ParamFloat', 'ParamInt', 'ParamNumber'}
EVENTS = {'ParamEvent', 'ParamTrigger'}
IDENTITY = ('kind', 'scope', 'layer_id', 'group_id', 'clip_id', 'effect_name', 'description')


def contract(value):
    """Persistence changes tuples into lists, including nested choice lists."""
    return json.loads(json.dumps(value))


def native_program(phase, parameter):
    source = phase.get('phase_source')
    if source == 'static': return None
    if source not in {'timeline','bpm_sync','composition_fft','external_fft','entity_fft','crossfader','clip_position','transition','dashboard'}:
        raise ValueError('Native animation source cannot be captured')
    fields = {name:copy.deepcopy(p['value']) for name,p in (phase.get('parameters') or {}).items() if name not in ('BPM','Finished') and p.get('valuetype') not in EVENTS and 'value' in p}
    program = dict(source=source, fields=fields)
    if source == 'dashboard': program['dial'] = phase['dial']
    program.update({name:parameter[name] for name in ('in','out') if name in parameter})
    return program


def same_program(a, b):
    if not a or not b: return a == b
    a = copy.deepcopy(a); b = copy.deepcopy(b)
    # Bounce direction changes naturally. Returning an untouched running clock
    # must not restart it merely because it reached the opposite side.
    if a.get('fields',{}).get('PlayMode') == b.get('fields',{}).get('PlayMode') == 'Bounce':
        for program in (a,b):
            if program['fields'].get('PlayDirection') in ('<','>'): program['fields']['PlayDirection'] = 'running'
    return a == b


class SessionControls:
    def __init__(self, engine):
        self.e = engine
        self.beat = 0.
        self.loops = {}
        self.returns = {}
        self.preferences = {}
        self.busy = False
        self.operation = None
        self.serial = 0
        self.inflight = 0

    def row(self, key):
        row = next((r for r in self.e.catalog.get('effect_rack', {}).get('rows', []) if r['id'] == key), None)
        if not row:
            raise ValueError('Rack section unavailable')
        return row

    def loop(self, key):
        row = self.row(key)
        choices = [p['id'] for p in row['pads'] if p.get('mode') in ('pulse', 'trigger', 'toggle')]
        if key not in self.loops:
            loop = dict(running=False, pattern='kick', kick='twitch' if 'twitch' in choices else next(iter(choices), ''), snare='stack' if 'stack' in choices else 'melt_hit' if 'melt_hit' in choices else next(iter(choices), ''), strength=.65, length=.25, generation=0, last=-1, skipped=0)
            saved = self.preferences.get(self.e.catalog['epoch'], {}).get(key, {})
            for name in ('kick', 'snare'):
                if saved.get(name) in choices: loop[name] = saved[name]
            if saved.get('pattern') in ('kick', 'alternate'): loop['pattern'] = saved['pattern']
            for name, low, high in [('strength', 0., 1.), ('length', .125, 2.)]:
                value = saved.get(name)
                if type(value) in (int, float) and math.isfinite(value) and low <= value <= high: loop[name] = value
            self.loops[key] = loop
        return self.loops[key]

    def configure(self, data):
        if data.get('epoch') != self.e.catalog['epoch']:
            raise ValueError('Composition changed')
        if self.busy:
            raise ValueError('Recovery in progress')
        key = data['row']; row = self.row(key); old = self.loop(key); new = dict(old)
        choices = {p['id'] for p in row['pads'] if p.get('mode') in ('pulse', 'trigger', 'toggle')}
        for name in ('kick', 'snare'):
            if name in data:
                if data[name] not in choices: raise ValueError('Choose a one-shot effect')
                new[name] = data[name]
        if 'pattern' in data:
            if data['pattern'] not in ('kick', 'alternate'): raise ValueError('Choose Kick or Kick / Snare')
            new['pattern'] = data['pattern']
        for name, low, high in [('strength', 0., 1.), ('length', .125, 2.)]:
            if name in data:
                value = data[name]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high: raise ValueError('Invalid hit setting')
                new[name] = value
        if 'running' in data:
            if type(data['running']) is not bool: raise ValueError('Choose Run or Stop')
            new['running'] = data['running']
        if new['running']:
            if not self.e.armed or not self.e.connected: raise ValueError('Arm v2 first')
            if not self.e.rack_state().get(key, {}).get('ready'): raise ValueError('Rack section offline')
            for pad in {new['kick'], new['snare']} if new['pattern'] == 'alternate' else {new['kick']}:
                p = next((p for p in row['pads'] if p['id'] == pad), None)
                if not p: raise ValueError('Choose a one-shot effect')
                if p.get('mode') == 'trigger': self.e.rack_plan(dict(epoch=self.e.catalog['epoch'], row=key, pad=pad, action='trigger'))
        if any(new[k] != old[k] for k in ('running', 'pattern', 'kick', 'snare')):
            new['generation'] += 1
            new['last'] = math.floor(self.beat)
        self.loops[key] = new
        self.preferences.setdefault(self.e.catalog['epoch'], {})[key] = {name:new[name] for name in ('kick','snare','pattern','strength','length')}
        return new

    def stop(self, key=None):
        for row, loop in self.loops.items():
            if key is None or key == row:
                loop['running'] = False; loop['generation'] += 1

    def valid(self, command):
        if self.busy and command.get('_recovery') != self.operation['token']:
            return False
        token = command.get('_loop')
        if token is None: return True
        if not isinstance(token, (list, tuple)) or len(token) != 2: return False
        row, generation = token
        loop = self.loops.get(row, {})
        return bool(self.e.armed and self.e.connected and command.get('epoch') == self.e.catalog['epoch'] and loop.get('running') and loop.get('generation') == generation)

    def due(self, dt, beat=None):
        if not self.e.armed or not self.e.connected or self.busy:
            return []
        if not isinstance(dt, (int, float)) or not math.isfinite(dt): return []
        self.beat = self.beat+max(0., dt)*self.e.bpm/60 if beat is None else beat
        beat = math.floor(self.beat); commands = []
        for key, loop in self.loops.items():
            if not loop['running'] or beat <= loop['last']: continue
            missed = beat - loop['last'] - 1; loop['last'] = beat; loop['skipped'] += missed
            # After a stall, advance the indicator without replaying missed hits.
            if self.beat - beat > .15: loop['skipped'] += 1; continue
            pad = loop['snare'] if loop['pattern'] == 'alternate' and beat % 2 else loop['kick']
            commands.append(dict(cmd='rack_fire', epoch=self.e.catalog['epoch'], row=key, pad=pad, amount=loop['strength'], beats=loop['length'], _loop=(key, loop['generation'])))
        return commands

    def downbeat(self):
        self.beat = 0.
        for loop in self.loops.values(): loop['last'] = -1; loop['generation'] += 1

    def control(self, row_id, control_id):
        control = next((c for c in self.row(row_id).get('controls', []) if c['id'] == control_id), None)
        if not control or not control.get('bindings'): raise ValueError('Rack control unavailable')
        kind = control.get('type', control['bindings'][0].get('type'))
        if kind not in NUM | {'ParamBoolean', 'ParamChoice'}: raise ValueError('Rack control destination changed')
        seen = set()
        for b in control['bindings']:
            target = next((t for t in self.e.catalog['targets'] if t['id'] == b['target']), None)
            param = self.e.params.get(b['parameter'])
            if not target or [target.get(k) for k in ('scope','layer_id','group_id','clip_id','effect_name')] != b['identity'] or not param or param[0] != b['target'] or b['parameter'] in seen or any(param[1].get(k) != b.get(k) for k in ('name','type','min','max')) or param[1]['type'] != kind or (control['min'], control['max']) != (param[1]['min'], param[1]['max']):
                raise ValueError('Rack control destination changed')
            if kind == 'ParamChoice' and (b.get('options') != param[1].get('options') or control.get('options') != param[1].get('options')):
                raise ValueError('Rack control choices changed')
            seen.add(b['parameter'])
        return control

    def recovery_targets(self):
        config = self.e.rack_config.get('recovery', {})
        fixed = set(config.get('targets', [])); layers = set(config.get('source_layers', []))
        targets = []
        for target in self.e.catalog['targets']:
            if target.get('effect_name') == 'Mask' or target['kind'] not in ('source', 'effect'): continue
            member = target.get('layer_id') in layers
            if target.get('effect_name') == 'Transform':
                # Only motion already controlled by Heart belongs to shared Movement.
                if member and target.get('scope') == 'layer' and any(p['id'] in self.e.owned for p in target['params']): targets.append(target)
            elif target['id'] in fixed or (member and target.get('scope') == 'clip'):
                targets.append(target)
        return targets

    def recovery_parameters(self):
        """Recall Heart controls and declared rack values; leave native clocks running."""
        safe = set()
        for row in self.e.catalog.get('effect_rack', {}).get('rows', []):
            if not self.e.rack_state().get(row['id'], {}).get('ready'):
                raise ValueError('Recovery rack destination unavailable')
            for bindings in [row['color']] + [pad['bindings'] for pad in row['pads']]:
                for binding in bindings:
                    safe.update(binding[key] for key in ('opacity', 'bypass', 'latch') if key in binding)
            for control in row.get('controls', []):
                safe.update(b['parameter'] for b in self.control(row['id'], control['id'])['bindings'])
        result = {}
        for target in self.recovery_targets():
            ids = []
            for p in target['params']:
                pid = p['id']
                if p['type'] in EVENTS: continue
                transform = target.get('effect_name') == 'Transform'
                authored_switch = p['type'] not in NUM and p.get('authored') and p['authored'].get('source') != 'native'
                if pid in self.e.owned or (not transform and (pid in safe or pid in self.e.control_owner or authored_switch)):
                    ids.append(pid)
            if ids: result[target['id']] = ids
        return result

    def assert_capture_ready(self):
        hits = any(env.get('progress', 0) < 1 for env in self.e.envelopes.values())
        if self.inflight or self.e.launches or self.e.pending_hits or self.e.rack_returns or self.e.clip_starts or self.e.authored.busy or hits or any(l['running'] for l in self.loops.values()) or any(sw.get('pending') for sw in self.e.switches.values()):
            raise ValueError('Stop loops and let current changes finish before capturing')

    def begin(self, name, action):
        if name not in ('base', 'safe'): raise ValueError('Choose Base or Safe')
        if action not in ('capture', 'return'): raise ValueError('Choose Set or Return')
        if self.busy: raise ValueError('Recovery in progress')
        if not self.e.armed or not self.e.connected: raise ValueError('Arm v2 first')
        if action == 'capture': self.assert_capture_ready()
        else: self.prepare_return(name); self.stop()
        self.serial += 1
        self.operation = dict(token=self.serial, epoch=self.e.catalog['epoch'], revision=self.e.epoch, action=action)
        self.busy = True
        return self.serial

    def check(self, token, stable=False):
        op = self.operation
        if not op or token != op['token'] or not self.e.armed or not self.e.connected or op['epoch'] != self.e.catalog['epoch'] or (stable and op['revision'] != self.e.epoch):
            raise ValueError('Recovery cancelled; composition or connection changed')

    def end(self, token):
        if self.operation and self.operation['token'] == token:
            self.operation = None; self.busy = False

    def cancel(self):
        self.stop(); self.operation = None; self.busy = False

    def capture(self, name, fresh=None, token=None, native_programs=None):
        if name not in ('base', 'safe'): raise ValueError('Choose Base or Safe')
        if token is not None: self.check(token, stable=True)
        elif self.busy: raise ValueError('Recovery in progress')
        self.assert_capture_ready()
        params_by_target = self.recovery_parameters()
        if not params_by_target: raise ValueError('No Heart recovery controls available')
        fresh = fresh or {}; native_programs = native_programs or {}; snapshots = {}
        for target in self.recovery_targets():
            params = {}
            for pid in params_by_target.get(target['id'], []):
                p = self.e.params[pid][1]; sl = self.e.slots.get(pid)
                value = fresh.get(pid, self.e.current_value(pid))
                if sl and pid in self.e.owned and not sl.drive and not p.get('native_phase'):
                    value = p['min'] + sl.cfg['manual'] * (p['max'] - p['min'])
                item = dict(contract=contract(self.e.contracts[pid]), value=value)
                if native_programs.get(pid) and not self.e.catalog.get('native_phase_mode'): item['native_animation'] = copy.deepcopy(native_programs[pid])
                if sl:
                    cfg = copy.deepcopy(sl.cfg)
                    if pid not in self.e.owned: cfg['manual'] = self.e.native_position(p,value) if p.get('native_phase') else (value - p['min']) / (p['max'] - p['min'])
                    item.update(cfg=cfg, drive=sl.drive and pid in self.e.owned, phi=sl.phi, phi_fm=sl.phi_fm, rate_scale=self.e.rate_scale.get(pid, 1.), intensity_scale=self.e.intensity_scale.get(pid, 1.))
                params[str(pid)] = item
            if params:
                snapshots[target['id']] = dict(identity=[target.get(k) for k in IDENTITY], params=params, group=copy.deepcopy(self.e.groups.get(target['id'])))
        layers = []
        for lid in self.e.rack_config.get('recovery', {}).get('source_layers', []):
            layer = next((l for l in self.e.catalog['layers'] if l['id'] == lid), None)
            if not layer: raise ValueError('Recovery layer missing')
            clip = next((c for c in layer['clips'] if c['col'] == layer['active']), None)
            layers.append(dict(id=lid, clip=copy.deepcopy(clip)))
        # Only restore ancestor controls when every target they affect belongs
        # to this return. A Figure return cannot silently change the whole stage.
        scopes = {key for target in snapshots for key in self.e.motion_scale_keys.get(target, [])
                  if all(t in snapshots for t, keys in self.e.motion_scale_keys.items() if key in keys)}
        multipliers = {key:self.e.motion_multipliers.get(key, {}).get('value', 1.) for key in scopes}
        snapshot = dict(version=3, epoch=self.e.catalog['epoch'], targets=snapshots, layers=layers, hold=self.e.hold, motion_multipliers=multipliers)
        self.returns[self.e.catalog['epoch']+'|'+name] = snapshot
        return snapshot

    def validate(self, snapshot, require_active=False):
        if snapshot.get('version') not in (2,3) or snapshot.get('epoch') != self.e.catalog['epoch']:
            raise ValueError('Recovery composition changed; set a new return')
        layers = {}; actual = {t['id']: t for t in self.e.catalog['targets']}
        for item in snapshot['layers']:
            layer = next((l for l in self.e.catalog['layers'] if l['id'] == item['id']), None)
            if not layer: raise ValueError('Recovery layer missing')
            layers[item['id']] = item
            clip = item['clip']
            if clip:
                current = next((c for c in layer['clips'] if c['id'] == clip['id']), None)
                if not current or any(current.get(k) != clip.get(k) for k in ('name', 'description')): raise ValueError('Recovery source changed')
            active = next((c for c in layer['clips'] if c['col'] == layer['active']), None)
            if require_active and (active or {}).get('id') != (clip or {}).get('id'):
                raise ValueError('Recovery clip did not launch')
        for target_id, saved in snapshot['targets'].items():
            identity = saved.get('identity')
            if not isinstance(identity, list) or len(identity) != len(IDENTITY): raise ValueError('Recovery target identity missing')
            scope = dict(zip(IDENTITY, identity)); target = actual.get(target_id)
            if target:
                if [target.get(k) for k in IDENTITY] != identity: raise ValueError('Recovery target changed')
            else:
                layer = layers.get(scope['layer_id']); clip = (layer or {}).get('clip')
                if require_active or scope['scope'] != 'clip' or not clip or clip['id'] != scope['clip_id']:
                    raise ValueError('Recovery target unavailable')
                live_layer = next(l for l in self.e.catalog['layers'] if l['id'] == layer['id'])
                if any(c['id'] == clip['id'] and c['col'] == live_layer['active'] for c in live_layer['clips']):
                    raise ValueError('Recovery source controls unavailable')
            for key, item in saved['params'].items():
                if self.e.catalog.get('native_phase_mode') and item.get('native_animation'): raise ValueError('Set Base/Safe again for native range control')
                pid = int(key)
                if pid in self.e.contracts:
                    if contract(self.e.contracts[pid]) != item['contract']: raise ValueError('Recovery parameter changed')
                elif target or require_active: raise ValueError('Recovery parameter unavailable')
        return snapshot

    def clear(self, name):
        if name not in ('base', 'safe'): raise ValueError('Choose Base or Safe')
        if self.busy: raise ValueError('Recovery in progress')
        self.returns.pop(self.e.catalog['epoch']+'|'+name, None)

    def prepare_return(self, name):
        if name not in ('base', 'safe'): raise ValueError('Choose Base or Safe')
        snapshot = self.returns.get(self.e.catalog['epoch']+'|'+name)
        if not snapshot: raise ValueError('Set '+name.title()+' first')
        return self.validate(snapshot)

    def apply_return(self, snapshot, token=None):
        if token is not None: self.check(token)
        self.validate(snapshot, require_active=True)
        self.stop(); values = []; now = time.perf_counter()
        for target, saved in snapshot['targets'].items():
            if saved['group'] is not None: self.e.groups[target] = copy.deepcopy(saved['group'])
            for key, item in saved['params'].items():
                pid = int(key)
                if item.get('native_animation'):
                    self.e.claim(pid); self.e.envelopes.pop(pid,None); self.e.owned.discard(pid); self.e.lastout.pop(pid,None); self.e.observed.pop(pid,None)
                    if pid in self.e.slots: self.e.slots[pid].drive = False
                    continue
                self.e.manual(pid, item['value'], duration=0)
                self.e.observed.pop(pid, None)
                sl = self.e.slots.get(pid)
                if sl:
                    sl.cfg = copy.deepcopy(item['cfg']); sl.drive = item['drive']
                    if not sl.native_phase: sl.phi = item['phi']; sl.phi_fm = item.get('phi_fm', 0.)
                    else:
                        sl.cfg.setdefault('amount',1.);sl.cfg.setdefault('range_offset',sl.cfg['manual'])
                    self.e.rate_scale[pid] = item.get('rate_scale', 1.); self.e.intensity_scale[pid] = item.get('intensity_scale', 1.)
                    sl.prev = sl.target = None; sl.dur = 0; sl.retarget(self.e.groups[target], now); self.e.owned.add(pid)
                    self.e.lastout[pid] = item['value']
                if self.e.params[pid][1].get('native_phase') and sl:
                    sl.cfg.update(lo=0.,hi=1.,range_authored=False);sl.prev=sl.target=None;sl.retarget(self.e.groups[target],now)
                    values.append((pid, {'phase':sl.value(sl.target)}))
                else: values.append((pid, item['value']))
        for key,value in snapshot.get('motion_multipliers',{}).items():
            if any(key in keys for keys in self.e.motion_scale_keys.values()) and all(t in snapshot['targets'] for t,keys in self.e.motion_scale_keys.items() if key in keys):
                self.e.motion_multipliers[key]=dict(value=value,**{'from':self.e.multiplier_value(key,now)},started=now,seconds=60/self.e.bpm)
        self.e.set_hold(snapshot['hold'])
        return values

    def state(self):
        loops = {r['id']:dict(self.loop(r['id']), beat=math.floor(self.beat)%4+1) for r in self.e.catalog.get('effect_rack', {}).get('rows', [])}
        return dict(loops=loops, recovery={name:self.returns.get(self.e.catalog['epoch']+'|'+name,{}).get('version') in (2,3) for name in ('base','safe')}, busy=self.busy)
