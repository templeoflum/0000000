"""Opt-in installed rack/recovery verification, with fresh scoped restoration.

Runs only when executed as a script. All writes use Heart; native HTTP is read-only.
The performer must keep the standalone Heart open. Root runs this sequentially
with other live exercises. Only vacant Base/Safe points are used and later cleared.
"""
import asyncio
import copy
import json
import math
import signal
import sys
import time
from pathlib import Path
import websockets

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from session_controls import native_program, same_program
from verify_session_live import Heart, current_clip, make_plan, native_values, parameter_contracts

NUM = {'ParamRange', 'ParamFloat', 'ParamInt', 'ParamNumber'}
LOOP_SETTINGS = ('pattern', 'kick', 'snare', 'strength', 'length')


def vacant_points(epoch, stored):
    # Even an older, currently unusable capture belongs to the performer.
    return [name for name in ('base', 'safe') if epoch+'|'+name not in stored]


def restore_steps(program):
    """Duration establishes the native limits for later timeline fields."""
    first = {key:program['fields'][key] for key in ('DurationType', 'DurationIsScalable', 'Duration') if key in program['fields']}
    later = {key:value for key,value in program['fields'].items() if key not in first}
    if later.get('PlayMode') == 'Bounce' and later.get('PlayDirection') in ('<', '>'):
        later.pop('PlayDirection')
    steps = [dict(**{key:value for key,value in program.items() if key != 'fields'}, fields=first)]
    if later: steps.append(dict(fields=later))
    return steps


def clip_pair(catalog):
    motion = json.loads((ROOT/'checks/session-starting-motion.json').read_text())
    plan, _ = make_plan(catalog, motion, 'exercise')
    plan.sort(key=lambda p:(p['name'] != '2d', p['name'] != '3d', p['name']))
    for first in plan:
        second = next((p for p in plan if p['layer_id'] == first['layer_id'] and p['clip_id'] != first['clip_id']), None)
        if second: return first, second
    raise RuntimeError('No verified same-layer clip pair for recovery exercise')


async def run(output=None):
    report = dict(started=time.time(), rows=[], recovery={}, restoration=dict(complete=False),
                  scope='Native parameter and program delivery; rendered FPS and artistic acceptance are separate.')
    output = Path(output or ROOT/'checks/session-rack-live.json')
    saved = None; original_loops = {}; original = {}; animations = {}; temporary = []
    anchor = None; epoch = None; rows = []; before_contracts = {}; controls_changed = False
    task = asyncio.current_task()
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, task.cancel)
    async with websockets.connect('ws://127.0.0.1:8876', max_size=16*1024*1024) as ws:
        heart = Heart(ws); reader = asyncio.create_task(heart.read())

        def check():
            if heart.catalog['epoch'] != epoch or not heart.state['armed'] or not heart.state['connected']:
                raise RuntimeError('Composition or connection changed; refusing stale exercise writes')

        async def wait_ready(timeout=20):
            def ready():
                if heart.state.get('session', {}).get('busy'): return False
                for row in rows:
                    if heart.state.get('session', {}).get('loops', {}).get(row['id'], {}).get('running'): return False
                    for pad in row['pads']:
                        if pad.get('mode') == 'pulse' and heart.state.get('effect_rack', {}).get(row['id'], {}).get('active', {}).get(pad['id']): return False
                return not any(v.get('pending') or (v.get('envelope') and v['envelope'].get('progress', 0) < 1) for v in heart.state.get('values', {}).values())
            await heart.until(ready, timeout=timeout)
            # A completed decay is followed by guarded native bypass/level restore.
            await asyncio.sleep(.25)

        async def values(ids):
            return {int(pid):p['value'] for pid,p in (await native_values(ids)).items()}

        async def settle(pid, expected, timeout=6):
            deadline = time.monotonic()+timeout; actual = None
            while time.monotonic() < deadline:
                check(); actual = (await values([pid]))[pid]
                if type(expected) is bool:
                    if actual is expected: return actual
                elif isinstance(expected, (int,float)) and math.isclose(actual,expected,abs_tol=1e-4): return actual
                elif actual == expected: return actual
                await asyncio.sleep(.05)
            raise AssertionError(dict(parameter=pid, expected=expected, actual=actual))

        async def program_matches(pid, expected, timeout=10):
            deadline = time.monotonic()+timeout
            while time.monotonic() < deadline:
                check(); actual = await heart.animation(pid)
                if same_program(native_program(actual,actual['parameter']),expected): return actual
                await asyncio.sleep(.05)
            raise AssertionError('Native animation was not restored: '+str(pid))

        async def capture(name):
            check(); await wait_ready()
            stored = json.loads((ROOT/'recovery.json').read_text()) if (ROOT/'recovery.json').exists() else {}
            if epoch+'|'+name in stored and name not in temporary:
                raise RuntimeError('Recovery point is no longer vacant: '+name)
            if name not in temporary: temporary.append(name)
            await heart.send('recovery', epoch=epoch, name=name, action='capture',
                             predicate=lambda:heart.state['session']['recovery'][name] and not heart.state['session']['busy'])
            stored = json.loads((ROOT/'recovery.json').read_text())
            point = stored.get(epoch+'|'+name, {})
            if point.get('version') != 2: raise RuntimeError('Expected native-program-aware recovery capture')
            return point

        async def return_point(name, predicate=None):
            check()
            await heart.send('recovery', epoch=epoch, name=name, action='return',
                             predicate=lambda:not heart.state['session']['busy'] and (predicate is None or predicate()))
            await heart.until(lambda:not heart.state['session']['busy'], timeout=30)

        async def restore_animation(pid, animation, original_state):
            program = native_program(animation,animation['parameter'])
            if program:
                # Empty animation edit releases any cached Heart claim without
                # restarting an unchanged native clock.
                current = await heart.animation(pid, fields={})
                if not same_program(native_program(current,current['parameter']),program):
                    for step in restore_steps(program): await heart.animation(pid,**step)
                await program_matches(pid,program)
            elif original_state.get('drive'):
                # A vacant anchor returns the exact Heart configuration and phase.
                if not anchor: raise RuntimeError('Driven rack controls require a vacant recovery anchor')
            else:
                await heart.send('manual', id=pid, value=original[pid])
                await settle(pid,original[pid])
                if not original_state.get('owned'):
                    await heart.animation(pid,source='static',**{key:animation['parameter'][key] for key in ('in','out') if key in animation['parameter']})

        try:
            await heart.until(lambda:heart.catalog and heart.state and heart.state.get('connected'),errors=False)
            if not heart.state['armed']: raise RuntimeError('Heart must already be armed')
            if heart.state.get('session', {}).get('busy'): raise RuntimeError('A recovery is already running')
            epoch = heart.catalog['epoch']; rows = copy.deepcopy(heart.catalog['effect_rack']['rows'])
            original_loops = copy.deepcopy(heart.state['session']['loops'])
            # Stop the fresh running choices before taking any baseline values.
            for row in rows: await heart.send('rack_sequence',epoch=epoch,row=row['id'],running=False)
            await wait_ready(); saved = await heart.snapshot(); before_contracts = parameter_contracts(saved['catalog'])
            ids = set()
            for row in rows:
                for bindings in [row['color']] + [pad['bindings'] for pad in row['pads']]:
                    for binding in bindings: ids.update(binding[key] for key in ('opacity','bypass','latch') if key in binding)
                ids.update(b['parameter'] for control in row.get('controls',[]) for b in control['bindings'])
            cross = next(p for t in saved['catalog']['targets'] if t['kind']=='crossfader' for p in t['params'] if p['name']=='phase')
            ids.add(cross['id'])
            if saved['state']['values'][str(cross['id'])].get('drive'): raise RuntimeError('Crossfader is currently driven; defer its manual exercise')
            original = await values(ids)
            for pid in ids:
                if before_contracts[str(pid)][9] in NUM: animations[pid] = await heart.animation(pid)
            stored = json.loads((ROOT/'recovery.json').read_text()) if (ROOT/'recovery.json').exists() else {}
            free = vacant_points(epoch,stored)
            report['before'] = dict(values=original, loops=original_loops, occupied_returns=sorted(set(('base','safe'))-set(free)), tempo=heart.state['bpm'], hold=heart.state['hold'])
            Path(str(output)+'.before.json').write_text(json.dumps(dict(snapshot=saved,values=original,animations=animations,loops=original_loops),indent=2)+'\n')
            if free:
                anchor = free[0]; point = await capture(anchor)
                report['recovery'][anchor] = dict(captured_before_edits=True, native_programs=sum('native_animation' in p for target in point['targets'].values() for p in target['params'].values()))
            elif any(saved['state']['values'][str(pid)].get('drive') for pid in ids):
                raise RuntimeError('No vacant anchor for preserving driven rack controls')
            controls_changed = True
            for row in rows:
                check(); rid = row['id']; result = dict(row=rid,colors=[],pulses=[],loops=[])
                for control in row.get('controls',[]):
                    value = control['min']+.43*(control['max']-control['min'])
                    await heart.send('rack_parameter',epoch=epoch,row=rid,control=control['id'],value=value)
                    got = [await settle(b['parameter'],value) for b in control['bindings']]
                    phases = [await heart.animation(b['parameter']) for b in control['bindings']]
                    if any(p['phase_source']!='static' for p in phases): raise AssertionError('Rack scalar did not take native ownership')
                    result['colors'].append(dict(control=control['id'],native=got,static=True))
                for pad in (p for p in row['pads'] if p['mode']=='pulse'):
                    baseline = await values([b[key] for b in pad['bindings'] for key in ('opacity','bypass')])
                    await heart.send('rack_fire',epoch=epoch,row=rid,pad=pad['id'],amount=.7,beats=min(4,max(.5,.4*heart.state['bpm']/60)),
                                     predicate=lambda rid=rid,pad=pad:heart.state['effect_rack'][rid]['active'][pad['id']])
                    peak = await values([b[key] for b in pad['bindings'] for key in ('opacity','bypass')])
                    if not all(peak[b['opacity']]>1e-5 and peak[b['bypass']] is False for b in pad['bindings']): raise AssertionError('Native pulse did not become visible')
                    await wait_ready()
                    for pid,value in baseline.items(): await settle(pid,value)
                    result['pulses'].append(dict(pad=pad['id'],sampled=peak,restored=True))
                for pattern in ('kick','alternate'):
                    baseline = await values([b[key] for pad in row['pads'] if pad['mode']=='pulse' for b in pad['bindings'] for key in ('opacity','bypass')])
                    await heart.send('rack_sequence',epoch=epoch,row=rid,kick='twitch',snare='stack',pattern=pattern,strength=.7,length=.5,running=True,
                                     predicate=lambda:heart.state['session']['loops'][rid]['running'])
                    beats = set(); deadline=time.monotonic()+max(2.8,4*60/heart.state['bpm'])
                    while time.monotonic()<deadline:
                        check(); beats.add(heart.state['session']['loops'][rid]['beat']); await asyncio.sleep(.1)
                    await heart.send('rack_sequence',epoch=epoch,row=rid,running=False,
                                     predicate=lambda:not heart.state['session']['loops'][rid]['running'])
                    await wait_ready()
                    for pid,value in baseline.items(): await settle(pid,value)
                    if len(beats)<2: raise AssertionError('Loop beat indicator did not advance')
                    result['loops'].append(dict(pattern=pattern,beats=sorted(beats),stopped=True))
                report['rows'].append(result); print('Native rack passed: '+rid,flush=True)
            await heart.send('manual',id=cross['id'],value=.25); await settle(cross['id'],.25)
            await heart.send('manual',id=cross['id'],value=original[cross['id']]); await settle(cross['id'],original[cross['id']]); report['crossfader']=True
            if anchor:
                await return_point(anchor)
                checked = []
                for pid,animation in animations.items():
                    program = native_program(animation,animation['parameter'])
                    if program and pid != cross['id']:
                        await program_matches(pid,program); checked.append(pid)
                report['recovery'][anchor].update(returned=True,native_clocks_verified=checked)
                # An untouched saved running native clock must also still move.
                if checked:
                    moving = [pid for pid in checked if animations[pid].get('parameters',{}).get('PlayDirection',{}).get('value')!='||']
                    if moving:
                        a=await values(moving); await asyncio.sleep(.3); b=await values(moving)
                        report['recovery'][anchor]['clock_motion']={pid:abs(a[pid]-b[pid])>1e-7 for pid in moving}
                        if not any(report['recovery'][anchor]['clock_motion'].values()): raise AssertionError('Restored native clocks did not move')
                if len(free)>1:
                    first,second = clip_pair(heart.catalog); await heart.launch(first,epoch)
                    target=first['controls'][0]; pid=target['parameter']
                    await heart.send('watch',targets=[target['target']],predicate=lambda:str(pid) in heart.state['values'])
                    initial=heart.state['values'][str(pid)];span=initial['hi']-initial['lo']
                    if span<=0: raise AssertionError('Prepared clip has no editable motion span')
                    lo=initial['lo']+.15*span;hi=initial['hi']-.15*span
                    await heart.send('hold',on=False);await heart.send('range',id=pid,lo=lo,hi=hi)
                    await heart.send('parameter_motion',id=pid,ratio='2:3',offset=.31,shape=.9,seconds=0)
                    await heart.send('drive',id=pid,on=True)
                    point_name=free[1];await capture(point_name);await heart.launch(second,epoch)
                    def returned():
                        layer=next(l for l in heart.catalog['layers'] if l['id']==first['layer_id'])
                        v=heart.state.get('values',{}).get(str(pid),{})
                        return (current_clip(layer) or {}).get('id')==first['clip_id'] and v.get('drive') and math.isclose(v.get('lo',-1),lo) and math.isclose(v.get('hi',-1),hi)
                    await return_point(point_name,returned);await asyncio.sleep(.3)
                    if not returned(): raise AssertionError('Authored startup overwrote recovered Drive settings')
                    v=heart.state['values'][str(pid)]
                    if v['motion']['ratio']!='2:3' or not math.isclose(v['motion']['offset'],.31): raise AssertionError('Edited clip motion was not recovered')
                    a=await values([pid]);await asyncio.sleep(.3);b=await values([pid])
                    p=next(p for t in heart.catalog['targets'] for p in t['params'] if p['id']==pid)
                    low=p['min']+lo*(p['max']-p['min']);high=p['min']+hi*(p['max']-p['min'])
                    if not all(low-1e-5<=x<=high+1e-5 for x in (a[pid],b[pid])) or abs(a[pid]-b[pid])<1e-7: raise AssertionError('Recovered clip Drive did not move within edited bounds')
                    report['recovery'][point_name]=dict(returned=True,cross_clip=[first['name'],second['name'],first['name']],parameter=pid,edited_range=[lo,hi],native_samples=[a[pid],b[pid]])
                else:report['recovery']['cross_clip_skipped']='A second vacant point is required to retain the untouched starting state while testing edited clip recovery.'
            else:report['recovery']['skipped']='Both performer return points are occupied.'
            report['passed']=True
        except BaseException as exc:
            report['passed']=False;report['error']=repr(exc)
        finally:
            async def cleanup():
                if not epoch: return
                check()
                for row in rows: await heart.send('rack_sequence',epoch=epoch,row=row['id'],running=False)
                await wait_ready(timeout=30)
                if saved and controls_changed:
                    if anchor:
                        scope=set(saved['catalog']['effect_rack'].get('recovery',{}).get('source_layers',[]))
                        expected={l['id']:(current_clip(l) or {}).get('id') for l in saved['catalog']['layers'] if l['id'] in scope}
                        await return_point(anchor,lambda:all((current_clip(l) or {}).get('id')==expected[l['id']] for l in heart.catalog['layers'] if l['id'] in expected))
                    current=parameter_contracts(heart.catalog)
                    if any(current.get(str(pid))!=before_contracts[str(pid)] for pid in original): raise RuntimeError('Cleanup parameter identity changed')
                    for pid in original:
                        row=saved['state']['values'][str(pid)]
                        if pid in animations: await restore_animation(pid,animations[pid],row)
                        else: await heart.send('manual',id=pid,value=original[pid]);await settle(pid,original[pid])
                    await heart.send('hold',on=saved['state']['hold'])
                    if saved['state']['selected'] in {t['id'] for t in heart.catalog['targets']}: await heart.send('select',target=saved['state']['selected'])
                    after=await heart.snapshot()
                    for pid in original:
                        before=saved['state']['values'][str(pid)];now=after['state']['values'][str(pid)]
                        if pid in animations and native_program(animations[pid],animations[pid]['parameter']):
                            if now.get('owned'): raise AssertionError('Native clock retained Heart ownership after cleanup')
                        elif before.get('motion'):
                            for key in ('drive','locked','lo','hi','rate_scale','intensity_scale'):
                                if now.get(key)!=before.get(key): raise AssertionError('Cleanup changed '+str(pid)+' '+key)
                for name in temporary:
                    await heart.send('recovery',epoch=epoch,name=name,action='clear',predicate=lambda n=name:not heart.state['session']['recovery'][n])
                temporary.clear()
                # Restore choices and Run only after their native destinations are back.
                for row in rows:
                    old=original_loops[row['id']]
                    await heart.send('rack_sequence',epoch=epoch,row=row['id'],**{k:old[k] for k in LOOP_SETTINGS},running=bool(old['running']),
                                     predicate=lambda rid=row['id'],run=bool(old['running']):heart.state['session']['loops'][rid]['running']==run)
                await heart.send('watch',targets=[])
                report['restoration']=dict(complete=True,original_running={key:value['running'] for key,value in original_loops.items()},hold=heart.state['hold'],tempo_before=report.get('before',{}).get('tempo'),tempo_after=heart.state['bpm'],tempo_written=False)
            try: await asyncio.shield(cleanup())
            except BaseException as exc:
                report['passed']=False;report['restoration']['error']=repr(exc);report['retained_temporary_points']=temporary
            output.write_text(json.dumps(report,indent=2)+'\n');reader.cancel();await asyncio.gather(reader,return_exceptions=True)
            print(json.dumps(dict(phase='complete',passed=report.get('passed',False),restoration=report['restoration'],output=str(output))),flush=True)
    return 0 if report.get('passed') and report['restoration']['complete'] else 1


if __name__=='__main__':
    raise SystemExit(asyncio.run(run()))
