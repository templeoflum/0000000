#!/usr/bin/env python3
"""Opt-in Heart-only performance exercise, with fresh capture and finally restoration.

Requires the state-only watch protocol (native_ids=[]).
No native WebSocket, native writes, composition reads, saves or app/browser launch.
Native HTTP is GET /parameter/by-id only. The default prints the offline plan.

Run from the candidate or installed Heart directory:
  python checks/verify_session_live.py --exercise --level .7
  python checks/verify_session_live.py --load --field room --level .7 --seconds 30

The native frame profiler can run after stdout emits {"phase":"loaded",...}.
--load always restores on timeout, interruption or failure. Native timelines and
relaunched clip oscillators resume their saved settings; exact phase continuity
cannot be exported by Heart's public protocol. Retained layer drives are untouched.
"""
import argparse
import asyncio
import copy
import json
import math
from pathlib import Path
import signal
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NUM = {'ParamRange', 'ParamFloat', 'ParamInt', 'ParamNumber'}
CORE = ('1d', '2d', '3d', '4d', 'shell', 'hybrid', 'ground', 'room', 'void')


def parameter_contracts(catalog):
    return {str(p['id']): (t['id'], t.get('kind'), t.get('scope'), t.get('layer_id'),
                           t.get('group_id'), t.get('clip_id'), t.get('effect_name'),
                           t.get('description'), p['name'], p['type'], p['min'], p['max'])
            for t in catalog['targets'] for p in t['params']}


def current_clip(layer):
    return next((c for c in layer['clips'] if c['col'] == layer.get('active')), None)


def make_plan(catalog, motion, mode, field='room'):
    layers = {l['id']: l for l in catalog['layers']}
    if mode == 'exercise':
        plan = []
        for name in CORE:
            controls = [c for c in motion['controls'] if c['clip'] == name]
            if not controls:
                raise ValueError(f'No prepared motion for {name}')
            ids = {(c['layer_id'], c['clip_id']) for c in controls}
            if len(ids) != 1:
                raise ValueError(f'Ambiguous prepared clip: {name}')
            lid, cid = ids.pop()
            layer = layers.get(lid)
            clip = next((c for c in (layer or {}).get('clips', []) if c['id'] == cid), None)
            if not clip or clip['name'] != name or clip['description'] != controls[0]['source']:
                raise ValueError(f'Prepared clip identity changed: {name}')
            plan.append(dict(layer_id=lid, clip_id=cid, name=name, layer=layer['name'], controls=controls))
        return plan, []
    plan = []; skipped = []
    for layer_name in ('figure', 'field', 'feedback', 'glyph', 'delay'):
        matches = [l for l in layers.values() if l['name'] == layer_name]
        if len(matches) != 1:
            skipped.append(dict(layer=layer_name, reason='Missing or ambiguous named layer')); continue
        layer = matches[0]
        if layer_name in ('figure', 'field'):
            wanted = '4d' if layer_name == 'figure' else field
            candidates = [c for c in layer['clips'] if c['name'] == wanted]
        elif layer_name == 'glyph':
            candidates = [c for c in layer['clips'] if 'script' in (c.get('description', '') + ' ' + c['name']).lower()]
        elif current_clip(layer):
            candidates = [current_clip(layer)]
        elif layer_name == 'feedback':
            candidates = [c for c in layer['clips'] if c.get('description') == 'Feedback'][:1]
        else:
            candidates = [c for c in layer['clips'] if c.get('description') == 'Video Router'][:1]
        if len(candidates) != 1:
            skipped.append(dict(layer=layer_name, reason='No unambiguous existing representative clip')); continue
        clip = candidates[0]
        plan.append(dict(layer_id=layer['id'], clip_id=clip['id'], name=clip['name'], layer=layer_name,
                         controls=[c for c in motion['controls'] if c['clip_id'] == clip['id']]))
    if not {'figure', 'field'}.issubset(p['layer'] for p in plan):
        raise ValueError('Representative Figure and Field clips are required')
    return plan, skipped


def target_batches(catalog, limit=20):
    batches = []; batch = []; count = 0
    for target in catalog['targets']:
        if len(target['params']) > 200:
            raise ValueError('Target exceeds bounded observation budget: ' + target['id'])
        if batch and count + len(target['params']) > limit:
            batches.append(batch); batch = []; count = 0
        batch.append(target); count += len(target['params'])
    return batches + ([batch] if batch else [])


class Heart:
    def __init__(self, ws):
        self.ws = ws; self.catalog = None; self.state = None; self.serial = 0
        self.animations = []; self.changed = asyncio.Event(); self.reader_error = None

    async def read(self):
        try:
            async for raw in self.ws:
                message = json.loads(raw)
                if message.get('type') == 'catalog' and 'targets' in message:
                    self.catalog = message
                if message.get('type') == 'state':
                    self.state = message; self.serial += 1
                if message.get('type') == 'animation':
                    self.animations.append(message)
                self.changed.set()
        except BaseException as exc:
            self.reader_error = repr(exc); self.changed.set()

    async def until(self, predicate, timeout=20, errors=True):
        async with asyncio.timeout(timeout):
            while not predicate():
                if self.reader_error:
                    raise RuntimeError(self.reader_error)
                if errors and self.state and self.state.get('error'):
                    raise RuntimeError(self.state['error'])
                self.changed.clear()
                await self.changed.wait()
        return self.state

    async def send(self, cmd, predicate=None, **data):
        if cmd == 'watch':
            # Export Heart program state without adding native subscriptions.
            # Any native values used as evidence or restoration inputs are read
            # by ID below (or through animation_get for numeric phase metadata).
            data.setdefault('native_ids', [])
        before = self.serial
        await self.ws.send(json.dumps(dict(cmd=cmd, **data)))
        await self.until(lambda: self.serial > before and (not predicate or predicate()), errors=False)
        if self.state.get('error'):
            raise RuntimeError(self.state['error'])

    async def animation(self, pid, **data):
        index = len(self.animations)
        await self.ws.send(json.dumps(dict(cmd='animation_set' if data else 'animation_get', id=int(pid), **data)))
        await self.until(lambda: any(m['id'] == int(pid) for m in self.animations[index:]), errors=False)
        message = next(m for m in self.animations[index:] if m['id'] == int(pid))
        if message.get('error'):
            raise RuntimeError(message['error'])
        return message['data']

    async def snapshot(self):
        catalog = copy.deepcopy(self.catalog); values = {}; groups = {}
        contracts = parameter_contracts(catalog)
        try:
            for batch in target_batches(catalog):
                ids = {str(p['id']) for t in batch for p in t['params']}
                await self.send('watch', targets=[t['id'] for t in batch],
                                predicate=lambda: ids.issubset(self.state.get('values', {})))
                if contracts != parameter_contracts(self.catalog):
                    raise RuntimeError('Catalog changed while capturing; no exercise started')
                values.update(copy.deepcopy(self.state['values'])); groups.update(copy.deepcopy(self.state['groups']))
            state = copy.deepcopy(self.state); state.update(values=values, groups=groups)
            return dict(catalog=catalog, state=state)
        finally:
            # This client shares the readback budget with the standalone surface
            # and rack priority controls. Never carry a capture batch into launch.
            await self.send('watch', targets=[])

    async def launch(self, row, epoch):
        if self.catalog['epoch'] != epoch:
            raise RuntimeError('Composition changed; refusing a stale launch')
        layer = next((l for l in self.catalog['layers'] if l['id'] == row['layer_id']), None)
        if not layer:
            raise RuntimeError('Layer changed')
        cid = row.get('clip_id')
        if cid is not None and not any(c['id'] == cid and c['name'] == row['name'] for c in layer['clips']):
            raise RuntimeError('Clip identity changed')
        def ready():
            layer_now = next((l for l in self.catalog['layers'] if l['id'] == row['layer_id']), None)
            clip = current_clip(layer_now) if layer_now else None
            return (bool(layer_now) and not layer_now.get('pending_clip') and
                    (clip['id'] if clip else None) == cid and
                    not self.state.get('authored', {}).get(str(cid), {}).get('busy'))
        if (current_clip(layer) or {}).get('id') != cid:
            await self.send('launch', layer_id=row['layer_id'], predicate=ready,
                            **({'clip_id': cid} if cid is not None else {'col': 0}))
        await self.until(ready)
        # A confirmed discovery can precede automatic starting-program application.
        await asyncio.sleep(.25)


async def native_values(ids):
    gate = asyncio.Semaphore(4)
    async def one(pid):
        async with gate:
            def read():
                with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{int(pid)}', timeout=4) as stream:
                    value = json.load(stream)
                if value.get('id') != int(pid):
                    raise ValueError('Native parameter ID changed')
                return value
            return str(pid), await asyncio.to_thread(read)
    return dict(await asyncio.gather(*(one(pid) for pid in ids)))


async def restore(heart, saved, affected, level_ids, report):
    epoch = saved['catalog']['epoch']
    if heart.catalog['epoch'] != epoch:
        raise RuntimeError('Composition changed; no stale restoration sent')
    await heart.send('hold', on=True, predicate=lambda: heart.state['hold'])
    old_layers = {l['id']: l for l in saved['catalog']['layers']}
    for lid in affected:
        clip = current_clip(old_layers[lid])
        await heart.launch(dict(layer_id=lid, clip_id=clip['id'] if clip else None,
                                name=clip['name'] if clip else None), epoch)
    old_contracts = parameter_contracts(saved['catalog']); current = parameter_contracts(heart.catalog)
    original_clip_targets = {t['id'] for t in saved['catalog']['targets']
                             if t.get('scope') == 'clip' and t.get('layer_id') in affected}
    restoring_ids = {pid for pid, contract in old_contracts.items()
                     if contract[0] in original_clip_targets or int(pid) in level_ids}
    if any(current.get(pid) != old_contracts[pid] for pid in restoring_ids):
        raise RuntimeError('Restoration target contract changed')
    for target in original_clip_targets:
        group = saved['state']['groups'].get(target)
        if group:
            await heart.send('relationship', target=target, seconds=0, **{k: group[k] for k in ('pattern', 'spread', 'seed', 'fm')})
            await heart.send('settings', target=target, amount=group['depth'], rate=group['speed'])
    for pid in restoring_ids:
        row = saved['state']['values'][pid]
        if old_contracts[pid][9] in ('ParamEvent', 'ParamTrigger'):
            continue
        await heart.send('manual', id=int(pid), value=row['value'])
        if row.get('motion'):
            await heart.send('range', id=int(pid), lo=row['lo'], hi=row['hi'])
            await heart.send('parameter_motion', id=int(pid), seconds=0,
                             **{k: row['motion'][k] for k in ('ratio', 'mult', 'offset', 'shape')})
            await heart.send('parameter_lock', epoch=epoch, id=int(pid), on=row.get('locked', False))
            if row['owned']:
                if row['drive']:
                    await heart.send('drive', id=int(pid), on=True)
            else:
                animation = saved['animations'][pid]
                fields = {k: p['value'] for k, p in (animation.get('parameters') or {}).items() if 'value' in p}
                values = dict(source=animation['phase_source'], fields=fields)
                values.update({k: animation['parameter'][k] for k in ('in', 'out') if k in animation['parameter']})
                if animation['phase_source'] == 'dashboard':
                    values['dial'] = animation['dial']
                await heart.animation(pid, **values)
    # Per-target scale is the only public scale restore action; heterogeneous scales
    # are rejected during capture before any clip is changed.
    for target in original_clip_targets:
        rows = [v for pid, v in saved['state']['values'].items() if old_contracts[pid][0] == target and v.get('motion')]
        if rows:
            for mode, key in (('rate', 'rate_scale'), ('intensity', 'intensity_scale')):
                await heart.send('motion_scale', targets=[target], mode=mode, value=rows[0].get(key, 1))
    if saved['state']['selected'] in {t['id'] for t in heart.catalog['targets']}:
        await heart.send('select', target=saved['state']['selected'])
    await heart.send('hold', on=saved['original_hold'], predicate=lambda: heart.state['hold'] == saved['original_hold'])
    after = await heart.snapshot()
    # Shared layer effects were never reconfigured. Assert their setting/state retention.
    retained = 0
    for pid, row in saved['state']['values'].items():
        if pid in restoring_ids or pid not in current or not row.get('motion'):
            continue
        now = after['state']['values'].get(pid)
        if not now:
            raise RuntimeError('Missing retained drive readback')
        for key in ('drive', 'locked', 'lo', 'hi', 'rate_scale', 'intensity_scale'):
            if now.get(key, 1) != row.get(key, 1):
                raise RuntimeError(f'Retained drive changed: {pid} {key}')
        for key in ('ratio', 'mult', 'offset', 'shape'):
            if now['motion'][key] != row['motion'][key]:
                raise RuntimeError(f'Retained motion changed: {pid} {key}')
        retained += int(row['drive'])
    if any((current_clip(l) or {}).get('id') != (current_clip(next(x for x in saved['catalog']['layers'] if x['id'] == l['id'])) or {}).get('id')
           for l in after['catalog']['layers'] if l['id'] in affected):
        raise RuntimeError('Playing clip restoration differs')
    for target, group in saved['state']['groups'].items():
        if target not in original_clip_targets and target in after['state']['groups'] and after['state']['groups'][target] != group:
            raise RuntimeError('Retained target group settings changed: ' + target)
    stable_levels = [pid for pid in level_ids if not saved['state']['values'][str(pid)]['drive']]
    level_readback = await native_values(stable_levels) if stable_levels else {}
    for pid, native in level_readback.items():
        if not math.isclose(native['value'], saved['state']['values'][pid]['value'], abs_tol=1e-5):
            raise RuntimeError('Native level restoration differs: ' + pid)
    report['restoration'] = dict(complete=True, retained_drives=retained, level_readback={pid:p['value'] for pid,p in level_readback.items()}, hold=after['state']['hold'],
                                 bpm_before=saved['state']['bpm'], bpm_after=after['state']['bpm'], tempo_written=False,
                                 clip_phase_continuity='Relaunched clips resume settings; exact previous phase is unavailable.')
    await heart.send('watch', targets=[])


async def run(args):
    import websockets
    task = asyncio.current_task()
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, task.cancel)
    motion = json.loads((ROOT / 'checks/session-starting-motion.json').read_text())
    report = dict(mode='exercise' if args.exercise else 'load', started=time.time(), checks=[], restoration={'complete':False},
                  scope='Native parameter delivery only; rendered FPS and visual acceptance are measured separately.')
    output = Path(args.output or ROOT / 'checks/session-native-verification.json')
    saved = None; affected = set(); level_ids = set(); capture_levels = set(); original_hold = None
    async with websockets.connect('ws://127.0.0.1:8876', max_size=16*1024*1024) as ws:
        heart = Heart(ws); reader = asyncio.create_task(heart.read())
        try:
            await heart.until(lambda: heart.catalog and heart.state and heart.state.get('connected'), errors=False)
            if not heart.state['armed']:
                raise RuntimeError('Heart must already be armed for an opt-in exercise')
            if heart.state.get('session', {}).get('busy'):
                raise RuntimeError('A recovery is running')
            loops = heart.state.get('session', {}).get('loops', {})
            if any(loop.get('running') for loop in loops.values()):
                raise RuntimeError('A trigger loop is running; defer verification until it is stopped')
            plan, skipped = make_plan(heart.catalog, motion, report['mode'], args.field)
            report.update(plan=plan, skipped=skipped)
            original_hold = heart.state['hold']
            await heart.send('hold', on=True, predicate=lambda: heart.state['hold'])
            saved = await heart.snapshot(); saved['original_hold'] = original_hold; saved['animations'] = {}
            if any(v.get('envelope') for v in saved['state']['values'].values()):
                raise RuntimeError('An effect envelope is active; defer verification until it releases')
            planned_layers = {p['layer_id'] for p in plan}; contracts = parameter_contracts(saved['catalog'])
            affected_targets = {t['id'] for t in saved['catalog']['targets'] if t.get('scope') == 'clip' and t.get('layer_id') in planned_layers}
            for target in affected_targets:
                group = saved['state']['groups'].get(target, {})
                if group.get('relationship'):
                    raise RuntimeError('Custom relationship recipe cannot be exported losslessly; exercise deferred')
                values = [v for pid, v in saved['state']['values'].items() if contracts[pid][0] == target and v.get('motion')]
                if any(len({v.get(key, 1) for v in values}) > 1 for key in ('rate_scale', 'intensity_scale')):
                    raise RuntimeError('Per-slot scale mixture cannot be restored with public target actions')
            for target in saved['catalog']['targets']:
                is_level = target['kind'] == 'layer' and int(target['id'].split(':')[1]) in planned_layers and args.level is not None
                for parameter in target['params']:
                    pid = str(parameter['id']); value = saved['state']['values'][pid]
                    if is_level and parameter['name'] == 'Level':
                        capture_levels.add(int(pid))
                    if (target['id'] in affected_targets or int(pid) in capture_levels) and value.get('motion') and not value['owned']:
                        saved['animations'][pid] = await heart.animation(pid)
                        saved['state']['values'][pid]['value'] = saved['animations'][pid]['parameter']['value']
            discrete = [int(pid) for pid, contract in contracts.items() if contract[0] in affected_targets and contract[9] not in NUM | {'ParamEvent', 'ParamTrigger'}]
            for pid, native in (await native_values(discrete)).items():
                saved['state']['values'][pid]['value'] = native['value']
            Path(str(output) + '.before.json').write_text(json.dumps(saved, indent=2) + '\n')
            await heart.send('hold', on=False, predicate=lambda: not heart.state['hold'])
            for row in plan:
                affected.add(row['layer_id'])
                await heart.launch(row, saved['catalog']['epoch'])
                if args.exercise:
                    await heart.send('authored', epoch=saved['catalog']['epoch'], clip_id=row['clip_id'], action='original')
                if args.level is not None:
                    tid = 'layer:' + str(row['layer_id'])
                    pid = next(p['id'] for t in heart.catalog['targets'] if t['id'] == tid for p in t['params'] if p['name'] == 'Level')
                    level_ids.add(pid)
                    await heart.send('manual', id=pid, value=args.level)
                controls = row['controls']
                ids = [c['parameter'] for c in controls]
                if ids:
                    await heart.send('watch', targets=sorted({c['target'] for c in controls}),
                                     predicate=lambda: set(map(str, ids)).issubset(heart.state.get('values', {})))
                    if not all(heart.state['values'][str(pid)]['drive'] for pid in ids):
                        raise RuntimeError('Prepared source drives did not start: ' + row['name'])
                    first = await native_values(ids)
                    await asyncio.sleep(args.sample_seconds)
                    second = await native_values(ids)
                    checks = []
                    for control in controls:
                        a = first[str(control['parameter'])]['value']; b = second[str(control['parameter'])]['value']
                        bounded = all(control['low'] - 1e-5 <= x <= control['high'] + 1e-5 for x in (a,b))
                        moved = abs(a-b) > 1e-7
                        checks.append(dict(control=control['control'], parameter=control['parameter'], first=a, second=b, bounded=bounded, changed=moved))
                    report['checks'].append(dict(clip=row['name'], controls=checks))
                    if not all(c['bounded'] and c['changed'] for c in checks):
                        raise RuntimeError('A prepared control did not move within its bounds: ' + row['name'])
                    if row['name'] == '1d':
                        source = next(t for t in heart.catalog['targets'] if t['id'] == controls[0]['target'])
                        opacity = next(p for p in source['params'] if p['name'] == 'Opacity')
                        report['line_opacity'] = (await native_values([opacity['id']]))[str(opacity['id'])]['value']
                print(json.dumps(dict(phase='clip_checked', clip=row['name'], layer=row['layer'])), flush=True)
            if args.load:
                print(json.dumps(dict(phase='loaded', seconds=args.seconds, clips=[p['name'] for p in plan], skipped=skipped)), flush=True)
                deadline = time.monotonic() + args.seconds
                while time.monotonic() < deadline:
                    await asyncio.sleep(min(.5, max(0, deadline - time.monotonic())))
                    if heart.catalog['epoch'] != saved['catalog']['epoch']:
                        raise RuntimeError('Composition changed during output profiling')
            report['passed'] = True
        except BaseException as exc:
            report['passed'] = False; report['error'] = repr(exc)
        finally:
            if saved:
                try:
                    await asyncio.shield(restore(heart, saved, affected, level_ids, report))
                except BaseException as exc:
                    report['restoration']['error'] = repr(exc)
                    report['passed'] = False
            elif original_hold is not None:
                try:
                    await heart.send('hold', on=original_hold, predicate=lambda: heart.state['hold'] == original_hold)
                    report['restoration'] = dict(complete=True, no_clips_changed=True, hold=original_hold)
                except BaseException as exc:
                    report['restoration']['error'] = repr(exc)
            output.write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(dict(phase='complete', passed=report.get('passed', False), restoration=report['restoration'], output=str(output))), flush=True)
            reader.cancel()
            await asyncio.gather(reader, return_exceptions=True)
    return 0 if report.get('passed') and report['restoration']['complete'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--exercise', action='store_true'); mode.add_argument('--load', action='store_true')
    parser.add_argument('--field', choices=('room','ground'), default='room')
    parser.add_argument('--level', type=float, help='Temporary level 0..1 on exercised layers; omitted preserves levels')
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--sample-seconds', type=float, default=2)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.level is not None and not 0 <= args.level <= 1:
        parser.error('--level must be 0..1')
    if not .5 <= args.sample_seconds <= 10 or not 1 <= args.seconds <= 120:
        parser.error('Sample must be .5..10 seconds; load must be 1..120 seconds')
    if not args.exercise and not args.load:
        catalog = json.loads((ROOT/'checks/session-runtime-before.json').read_text())['catalog']
        motion = json.loads((ROOT/'checks/session-starting-motion.json').read_text())
        print(json.dumps(dict(exercise=make_plan(catalog,motion,'exercise')[0], load=make_plan(catalog,motion,'load',args.field)),indent=2))
        return 0
    return asyncio.run(run(args))


if __name__ == '__main__':
    raise SystemExit(main())
