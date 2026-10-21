"""Sequenced rack accents and scoped Base/Safe returns, including live protocol races."""
import asyncio
import copy
import json
import socket
import sys
import tempfile
import time
import unittest
from pathlib import Path
import websockets
from server import Engine
from session_controls import native_program,same_program
from test_effect_hits import fixture as hit_fixture

ROOT = Path(__file__).parent


def fixture():
    catalog, rack = hit_fixture()
    for i, target in enumerate(catalog['targets'], 1):
        target['params'] += [
            dict(id=i*10+3, name='MELT_LOCK', type='ParamBoolean', min=0, max=1, value=False, options=[]),
            dict(id=i*10+4, name='Factor', type='ParamRange', min=0, max=1, value=.3, options=[]),
            dict(id=i*10+5, name='Offset', type='ParamRange', min=0, max=1, value=.2, options=[]),
            dict(id=i*10+6, name='Tint', type='ParamChoice', min=0, max=1, value='Red', options=['Red', 'Blue'])]
    for row in rack['rows']:
        members = row['pads'][0]['bindings']
        row['pads'][0]['mode'] = 'trigger'
        row['pads'] += [dict(id='pixel', mode='latch', bindings=[dict(b, latch=b['opacity']+3, latch_name='MELT_LOCK') for b in members]),
                        dict(id='twitch', mode='pulse', bindings=[{k:v for k,v in b.items() if k not in ('event','event_name')} for b in members]),
                        dict(id='melt_hit', mode='trigger', clear=False, bindings=copy.deepcopy(members))]
        row['controls'] = [dict(id='factor', min=0, max=1, bindings=[dict(target=b['target'], identity=b['identity'], parameter=b['opacity']+4, name='Factor', type='ParamRange', min=0, max=1) for b in members])]
    rack['recovery'] = dict(source_layers=[1], targets=[t['id'] for t in catalog['targets']])
    catalog['layers'] = [dict(id=1, i=1, active=1, clips=[dict(id=101, col=1, name='Shape', description='Original shape'), dict(id=102, col=2, name='Other', description='Other shape')])]
    def target(tid, kind, pid, scope='layer', name='Amount', effect_name=None, clip_id=None):
        return dict(id=tid, kind=kind, scope=scope, layer_id=1, layer=1, effect_name=effect_name, clip_id=clip_id, params=[dict(id=pid, name=name, type='ParamRange', min=0, max=1, value=.2, options=[])])
    catalog['targets'] += [target('source:101','source',1010,'clip',clip_id=101), target('effect:movement','effect',1000,effect_name='Transform'), target('effect:mask','effect',1002,effect_name='Mask'), target('layer:1','layer',1003,name='Level')]
    catalog['targets'][-3]['params'].append(dict(id=1001, name='Canvas scale', type='ParamRange', min=0, max=1, value=.9, options=[]))
    return catalog, rack


def engine():
    catalog, rack = fixture(); e = Engine(); e.rack_config = rack; e.reconcile(catalog); e.armed = e.connected = True
    return e


def add_discrete_controls(rack):
    for row in rack['rows']:
        for cid, name, kind, offset, options in [('lock','MELT_LOCK','ParamBoolean',3,None),('tint','Tint','ParamChoice',6,['Red','Blue'])]:
            bindings = [dict(target=b['target'],identity=b['identity'],parameter=b['opacity']+offset,name=name,type=kind,min=0,max=1,**({'options':options[:]} if options else {})) for b in row['pads'][0]['bindings']]
            row['controls'].append(dict(id=cid,type=kind,min=0,max=1,bindings=bindings,**({'options':options[:]} if options else {})))


class TypedRackControlTests(unittest.TestCase):
    def test_linked_boolean_and_choice_state_retains_types_and_mixed_values(self):
        e=engine();add_discrete_controls(e.rack_config)
        self.assertEqual(e.session.control('field','tint')['options'],['Red','Blue'])
        e.observed.update({33:(True,0),43:(False,0),36:('Blue',0),46:('Red',0)})
        state=e.rack_state()['field'];self.assertTrue(state['ready'])
        self.assertEqual(state['controls']['lock'],dict(value=True,mixed=True))
        self.assertEqual(state['controls']['tint'],dict(value='Blue',mixed=True))
        e.observed.update({43:(True,0),46:('Blue',0)})
        state=e.rack_state()['field'];self.assertFalse(state['controls']['lock']['mixed']);self.assertFalse(state['controls']['tint']['mixed'])

    def test_choice_binding_and_control_contract_changes_disable_whole_row(self):
        mutations=[lambda e,c:c['bindings'][1].update(options=['Blue','Red']),lambda e,c:c.update(options=['Red']),lambda e,c:e.params[46][1].update(options=['Red']),lambda e,c:c['bindings'][1].update(type='ParamBoolean'),lambda e,c:c['bindings'][1].update(min=-1),lambda e,c:c['bindings'][1].update(parameter=36),lambda e,c:c.update(type='ParamBoolean')]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                e=engine();add_discrete_controls(e.rack_config);control=e.session.control('field','tint');mutate(e,control)
                with self.assertRaises(ValueError):e.session.control('field','tint')
                self.assertFalse(e.rack_state()['field']['ready']);self.assertFalse(e.owned)


class SequenceTests(unittest.TestCase):
    def start(self, e, **settings):
        return e.session.configure(dict(epoch=e.catalog['epoch'], row='stage', running=True, kick='twitch', snare='twitch', **settings))

    def test_four_on_floor_alternate_and_tempo(self):
        e = engine(); self.start(e)
        self.assertEqual(e.session.due(.49), [])
        self.assertEqual(e.session.due(.01)[0]['pad'], 'twitch')
        e.params[10][1]['value'] = 1; e.params[11][1]['value'] = False
        e.session.configure(dict(epoch=e.catalog['epoch'], row='stage', pattern='alternate', snare='melt_hit'))
        self.assertEqual(e.session.due(.5)[0]['pad'], 'twitch')
        self.assertEqual(e.session.due(.5)[0]['pad'], 'melt_hit')
        e.bpm = 60
        self.assertEqual(e.session.due(.5), [])
        self.assertEqual(e.session.due(.5)[0]['pad'], 'twitch')

    def test_stall_skips_missed_beats_and_never_catches_up(self):
        e = engine(); self.start(e)
        self.assertEqual(e.session.due(3.2), [])
        self.assertEqual(e.session.loop('stage')['skipped'], 6)
        self.assertEqual(e.session.due(.3)[0]['pad'], 'twitch')
        self.assertEqual(e.session.due(.001), [])

    def test_stop_reassignment_downbeat_disarm_and_epoch_fence_queued_hit(self):
        e = engine(); self.start(e); hit = e.session.due(.5)[0]; self.assertTrue(e.session.valid(hit))
        e.session.stop('stage'); self.assertFalse(e.session.valid(hit))
        self.start(e); hit = e.session.due(.5)[0]; e.session.downbeat(); self.assertFalse(e.session.valid(hit))
        hit = e.session.due(.001)[0]; self.assertEqual(hit['pad'], 'twitch')
        e.disarm(); self.assertFalse(e.session.valid(hit)); self.assertFalse(e.session.loop('stage')['running']); self.assertEqual(e.session.due(.5), [])
        e.armed = True; self.start(e); hit = e.session.due(.5)[0]
        c = copy.deepcopy(e.catalog); c['epoch'] = 'other'; e.reconcile(c); self.assertFalse(e.session.valid(hit)); self.assertFalse(e.session.loops)

    def test_hold_keeps_accents_and_release_running(self):
        e = engine(); self.start(e); e.hold = True
        self.assertEqual(len(e.session.due(.5)), 1)
        e.effect_pulse(10, .8, .2); e.tick(.2, time.perf_counter()); self.assertEqual(e.current_value(10), 0)

    def test_invalid_settings_and_disabled_native_events_do_not_start(self):
        e = engine()
        for setting in [dict(epoch='stale'),dict(pattern='random'),dict(kick='pixel'),dict(strength=float('nan')),dict(length=True),dict(length=3),dict(running=1),dict(kick='melt_hit')]:
            d = dict(epoch=e.catalog['epoch'], row='stage', running=True, kick='twitch'); d.update(setting)
            with self.assertRaises(ValueError): e.session.configure(d)
        self.assertFalse(e.session.loop('stage')['running'])

    def test_sequence_preferences_restore_idle_and_are_composition_scoped(self):
        e = engine(); self.start(e, pattern='alternate', strength=.8, length=.5)
        settings = json.loads(json.dumps(e.session.preferences)); self.assertNotIn('running', settings['rack-test']['stage'])
        e.session.preferences = settings; e.session.loops.clear()
        loop = e.session.loop('stage'); self.assertFalse(loop['running']); self.assertEqual(loop['pattern'],'alternate'); self.assertEqual(loop['strength'],.8)
        e.session.preferences['rack-test']['stage'].update(running=True,length=float('nan'),kick='removed')
        e.session.loops.clear(); loop = e.session.loop('stage'); self.assertFalse(loop['running']); self.assertEqual(loop['length'],.25); self.assertEqual(loop['kick'],'twitch')

    def test_rack_retrigger_retains_original_baseline_and_manual_takeover_cancels_return(self):
        e = engine(); b = e.rack_config['rows'][0]['pads'][2]['bindings'][0]
        e.params[11][1]['value'] = False; e.manual(10,.35,duration=0)
        record = e.rack_pulse_baseline(b); self.assertEqual(record['value'],.35); self.assertFalse(record['bypass'])
        e.claim(10,'hit:1'); record.update(owner='hit:1'); e.rack_returns[10] = record
        e.effect_pulse(10,.9,.4,owner='hit:1',end=.35); e.tick(.2,time.perf_counter())
        self.assertGreater(e.current_value(10),.35); self.assertEqual(e.rack_pulse_baseline(b)['value'],.35)
        e.manual(10,.22,duration=0); self.assertNotIn(10,e.rack_returns)
        e.tick(.5,time.perf_counter()); self.assertAlmostEqual(e.current_value(10),.22)

    def test_clear_ignores_aliases_and_preserves_pixel_latch_release(self):
        e = engine(); values, events = e.rack_plan(dict(epoch=e.catalog['epoch'], row='stage', action='clear'))
        self.assertEqual(events, [])
        # One LUT off and one Pixel Melt on, with no alias write overriding it.
        self.assertEqual([value for pid, value in values if pid == 11], [True, False])
        self.assertIn((13, False), values)

    def test_linked_scalar_contract_checks_actual_parameter_owner(self):
        e = engine(); control = e.rack_config['rows'][2]['controls'][0]
        e.catalog['effect_rack']['rows'][2]['controls'][0]['bindings'][1]['parameter'] = 34
        with self.assertRaises(ValueError): e.session.control('field', 'factor')
        self.assertFalse(e.owned)


class ToggleRackTests(unittest.TestCase):
    def setup_rack(self):
        e=engine();binding=copy.deepcopy(e.rack_config['rows'][0]['pads'][2]['bindings'][0])
        e.rack_config['rows'].append(dict(id='feedback',color=[],pads=[dict(id='mirror',mode='toggle',bindings=[binding])],controls=[]))
        return e

    def apply(self,e,**changes):
        values,events=e.rack_plan(dict(epoch=e.catalog['epoch'],row='feedback',pad='mirror',**changes))
        self.assertEqual(events,[])
        for pid,value in values:
            e.manual(pid,value,duration=0)
            if pid in e.slots:e.lastout[pid]=value
            if pid in e.switches:e.confirm_switch(pid,e.switches[pid]['serial'],value)
        return values

    def test_toggle_preserves_alpha_and_zero_reenables_last_nonzero(self):
        e=self.setup_rack();self.assertTrue(e.rack_state()['feedback']['ready'])
        self.apply(e,action='opacity',amount=.37);self.apply(e,action='enable',on=True)
        self.assertEqual(self.apply(e,action='enable',on=False),[(11,True)])
        self.assertEqual(e.current_value(10),.37)
        self.apply(e,action='opacity',amount=0);self.apply(e,action='enable',on=True)
        self.assertEqual(e.current_value(10),.37);self.assertFalse(e.current_value(11))
        live=e.rack_state()['feedback'];self.assertEqual(live['levels']['mirror']['value'],.37);self.assertTrue(live['enabled']['mirror'])
        self.apply(e,action='clear');self.assertEqual(e.current_value(10),.37);self.assertTrue(e.current_value(11))

    def test_alpha_does_not_enable_bypass_and_toggle_is_not_a_loop_voice(self):
        e=self.setup_rack();self.apply(e,action='enable',on=False);self.apply(e,action='opacity',amount=.42)
        self.assertTrue(e.current_value(11))
        with self.assertRaises(ValueError):e.session.configure(dict(epoch=e.catalog['epoch'],row='feedback',kick='mirror',snare='mirror',running=True,pattern='alternate'))
        with self.assertRaises(ValueError):self.apply(e,action='opacity',amount=float('nan'))
        self.assertEqual(e.current_value(10),.42)

    def test_toggle_during_pulse_restores_baseline_before_turning_off(self):
        e=self.setup_rack();self.apply(e,action='opacity',amount=.37);self.apply(e,action='enable',on=True)
        binding=e.rack_config['rows'][-1]['pads'][0]['bindings'][0];record=e.rack_pulse_baseline(binding)
        e.claim(10,'hit:test');record.update(owner='hit:test');e.rack_returns[10]=record
        e.effect_pulse(10,.1,.4,owner='hit:test',end=.37)
        self.apply(e,action='enable',on=False);e.tick(.5,time.perf_counter())
        self.assertEqual(e.current_value(10),.37);self.assertTrue(e.current_value(11));self.assertNotIn(10,e.rack_returns)


class RecoveryTests(unittest.TestCase):
    def test_native_program_capture_restore_keeps_native_ownership(self):
        e=engine();e.manual(14,.8,duration=0)
        phase=dict(phase_source='timeline',parameters={'Duration':dict(value=4.6,valuetype='ParamRange'),'PlayMode':dict(value='Bounce',valuetype='ParamChoice'),'PlayDirection':dict(value='>',valuetype='ParamChoice'),'Finished':dict(value=0,valuetype='ParamNumber'),'BPM':dict(value=120,valuetype='ParamRange')})
        program=native_program(phase,dict(value=.42,**{'in':.1,'out':.9}))
        self.assertNotIn('Finished',program['fields']);self.assertNotIn('BPM',program['fields'])
        saved=e.session.capture('base',{14:.42},native_programs={14:program})
        self.assertEqual(saved['targets']['effect:1']['params']['14']['native_animation'],program)
        values=e.session.apply_return(saved);self.assertNotIn(14,e.owned);self.assertFalse(e.slots[14].drive);self.assertNotIn(14,dict(values))
        opposite=copy.deepcopy(program);opposite['fields']['PlayDirection']='<'
        self.assertTrue(same_program(program,opposite));opposite['fields']['PlayDirection']='||';self.assertFalse(same_program(program,opposite))

    def test_manual_takeover_discards_stale_observation(self):
        e=engine();e.observed[14]=(.01,time.perf_counter());e.manual(14,.4,duration=0)
        self.assertNotIn(14,e.observed)

    def test_capture_excludes_native_timelines_mixing_masks_and_untouched_geometry(self):
        e = engine()
        for pid in (1010,1000,1002,1003): e.manual(pid,.6,duration=0)
        e.observed[14] = (.01, time.perf_counter())
        saved = e.session.capture('base', {14:.42})
        ids = {int(pid) for t in saved['targets'].values() for pid in t['params']}
        self.assertTrue({10,11,13,14,1010,1000}.issubset(ids))
        self.assertTrue(ids.isdisjoint({12,15,16,1001,1002,1003}))
        self.assertEqual(saved['targets']['effect:1']['params']['14']['value'], .42)

    def test_owned_choices_and_nested_contracts_survive_json_roundtrip(self):
        e = engine(); e.manual(16,'Blue'); e.confirm_switch(16,e.switches[16]['serial'],'Blue')
        saved = e.session.capture('base'); e.session.returns = json.loads(json.dumps(e.session.returns))
        e.manual(16,'Red'); e.session.apply_return(e.session.prepare_return('base'))
        self.assertEqual(e.current_value(16),'Blue')
        e.params[16][1]['options'] = ['Yellow']; e.contracts[16] = tuple(list(e.contracts[16])[:-1] + [['Yellow']])
        with self.assertRaises(ValueError): e.session.prepare_return('base')

    def test_ranges_phases_families_and_manual_value_restore_without_old_observation(self):
        e = engine(); e.manual(1000,.7,duration=0); e.param_range(1000,.2,.8); sl = e.slots[1000]
        sl.drive = True; sl.phi = .62; sl.phi_fm = .37; sl.cfg.update(ratio='3:5', lock=True)
        e.groups['effect:movement'].update(speed=2, depth=.6); e.rate_scale[1000] = .5; e.intensity_scale[1000] = .7
        e.hold = True; saved = e.session.capture('safe')
        e.manual(1000,.1,duration=0); e.groups['effect:movement']['speed'] = 8; e.slots[1000].phi = 9; e.observed[1000] = (.99,0); e.hold = False
        e.session.apply_return(saved)
        self.assertEqual(sl.cfg['lo'],.2); self.assertEqual(sl.cfg['hi'],.8); self.assertTrue(sl.drive); self.assertTrue(sl.cfg['lock']); self.assertEqual(sl.phi,.62); self.assertEqual(sl.phi_fm,.37)
        self.assertEqual(e.groups['effect:movement']['speed'],2); self.assertEqual(e.rate_scale[1000],.5); self.assertEqual(e.intensity_scale[1000],.7); self.assertTrue(e.hold); self.assertNotIn(1000,e.observed)

    def test_capture_after_envelope_completed_and_immediate_manual_edit(self):
        e = engine(); e.effect_pulse(10,.8,.2)
        with self.assertRaises(ValueError): e.session.capture('base')
        e.tick(.2,time.perf_counter()); e.manual(14,.77,duration=0)
        self.assertEqual(e.session.capture('base')['targets']['effect:1']['params']['14']['value'],.77)
        e.pending_hits[20] = 'preparing'
        with self.assertRaises(ValueError): e.session.capture('safe')

    def test_capture_rejects_running_loop_pending_switch_launch_and_action(self):
        for state in ('loop','switch','launch','inflight'):
            e = engine()
            if state == 'loop': e.session.loop('stage')['running'] = True
            if state == 'switch': e.manual(11,False)
            if state == 'launch': e.launches[1] = {}
            if state == 'inflight': e.session.inflight = 1
            with self.assertRaises(ValueError): e.session.begin('base','capture')
            self.assertFalse(e.session.busy)

    def test_missing_fixed_target_and_changed_identity_reject_before_any_write(self):
        for mutation in ('missing','identity','parameter'):
            e = engine(); saved = e.session.capture('base'); original = copy.deepcopy(e.slots[14].cfg)
            c = copy.deepcopy(e.catalog)
            if mutation == 'missing': c['targets'] = [t for t in c['targets'] if t['id'] != 'effect:4']
            elif mutation == 'identity': c['targets'][3]['group_id'] = 999
            else: c['targets'][3]['params'][0]['max'] = 2
            e.reconcile(c)
            with self.assertRaises(ValueError): e.session.prepare_return('base')
            with self.assertRaises(ValueError): e.session.apply_return(saved)
            self.assertEqual(e.slots[14].cfg,original); self.assertFalse(e.owned)

    def test_clip_switch_permits_expected_missing_controls_but_requires_correct_final_clip(self):
        e = engine(); e.manual(1010,.5); saved = e.session.capture('base')
        c = copy.deepcopy(e.catalog); c['layers'][0]['active'] = 2; c['targets'] = [t for t in c['targets'] if t['id'] != 'source:101']; e.reconcile(c)
        self.assertIs(e.session.prepare_return('base'),saved)
        with self.assertRaises(ValueError): e.session.apply_return(saved)
        c['layers'][0]['clips'][0]['description'] = 'Replacement shader'; e.reconcile(c)
        with self.assertRaises(ValueError): e.session.prepare_return('base')

    def test_missing_source_controls_when_saved_clip_is_already_active_rejects(self):
        e = engine(); e.manual(1010,.5); e.session.capture('base'); c = copy.deepcopy(e.catalog); c['targets'] = [t for t in c['targets'] if t['id'] != 'source:101']; e.reconcile(c)
        with self.assertRaises(ValueError): e.session.prepare_return('base')

    def test_operation_tokens_guard_connection_composition_and_old_finally(self):
        e = engine(); token = e.session.begin('base','capture')
        with self.assertRaises(ValueError): e.session.begin('safe','capture')
        self.assertFalse(e.session.valid(dict(cmd='manual')))
        e.session.cancel(); new = e.session.begin('safe','capture'); e.session.end(token); self.assertTrue(e.session.busy)
        with self.assertRaises(ValueError): e.session.capture('base',token=token)
        e.disarm()
        with self.assertRaises(ValueError): e.session.check(new)
        self.assertFalse(e.session.busy)

    def test_old_capture_without_native_program_support_requires_reset(self):
        e=engine();saved=e.session.capture('base');saved['version']=1
        with self.assertRaises(ValueError):e.session.prepare_return('base')
        self.assertFalse(e.session.state()['recovery']['base'])

    def test_clear_only_named_return_and_refuses_busy_or_unknown_name(self):
        e = engine(); e.session.capture('base'); e.session.capture('safe')
        with self.assertRaises(ValueError): e.session.clear('everything')
        token = e.session.begin('safe','return')
        with self.assertRaises(ValueError): e.session.clear('safe')
        e.session.end(token); e.session.clear('base')
        self.assertNotIn('rack-test|base',e.session.returns); self.assertIn('rack-test|safe',e.session.returns)

    def test_return_stops_loop_and_rejects_commands_without_internal_token(self):
        e = engine(); e.session.capture('safe'); e.session.loop('stage')['running'] = True
        token = e.session.begin('safe','return'); self.assertFalse(e.session.loop('stage')['running'])
        self.assertFalse(e.session.valid(dict(cmd='rack_fire')))
        self.assertTrue(e.session.valid(dict(cmd='launch',_recovery=token)))
        self.assertEqual(e.session.due(.5), [])


class SessionRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_protocol_capture_fresh_return_reject_stale_hits_and_disarm_during_capture(self):
        def port():
            with socket.socket() as sock: sock.bind(('127.0.0.1',0)); return sock.getsockname()[1]
        http, wsport = port(), port(); catalog, rack = fixture()
        add_discrete_controls(rack)
        binding=copy.deepcopy(rack['rows'][0]['pads'][2]['bindings'][0]);rack['rows'].append(dict(id='feedback',color=[],pads=[dict(id='mirror',mode='fade',bindings=[binding])],controls=[]))
        contrast=copy.deepcopy(rack['rows'][0]['pads'][2]);contrast.update(id='twitch_contrast',contrast_hit=True)
        rack['rows'][0]['pads'].append(contrast)
        native = {p['id']:p['value'] for t in catalog['targets'] for p in t['params']}; native[14] = .42
        delay = False
        async def native_read(reader, writer):
            request = await reader.readuntil(b'\r\n\r\n'); parts=request.split(b' ')[1].decode().split('/'); is_phase=parts[-1]=='phase-source'; pid=int(parts[-2] if is_phase else parts[-1])
            if delay: await asyncio.sleep(.25)
            if is_phase:
                programs=json.loads((root/'native-programs.json').read_text())
                data=programs.get(str(pid),dict(phase_source='static',parameters={}))
            else:data=dict(id=pid,valuetype='ParamRange',min=0,max=1,value=native[pid],**{'in':0,'out':1})
            body = json.dumps(data).encode()
            writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body)).encode()+b'\r\nConnection: close\r\n\r\n'+body)
            try: await writer.drain()
            finally: writer.close(); await writer.wait_closed()
        api = await asyncio.start_server(native_read,'127.0.0.1',0); apiport = api.sockets[0].getsockname()[1]
        with tempfile.TemporaryDirectory(prefix='heart-session-runtime-') as directory:
            root = Path(directory)
            for name in ['session_controls.py','authored.py','server.py','motion.py','smart_motion.py','motion_clock.py','motion_frames.py','motion_memory.py','motion_persistence.py','catalog_updates.py','performance.py','play_actions.py','index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css']:
                text = (ROOT/name).read_text()
                if name == 'server.py': text = text.replace("os.environ.get('HEART_V2_DISCOVERY')=='fixture'",'True').replace('8875',str(http)).replace('8876',str(wsport)).replace('127.0.0.1:8080',f'127.0.0.1:{apiport}')
                (root/name).write_text(text)
            (root/'native-programs.json').write_text(json.dumps({'14':dict(phase_source='timeline',parameters={'Duration':dict(value=4.6,valuetype='ParamRange'),'PlayMode':dict(value='Bounce',valuetype='ParamChoice'),'PlayDirection':dict(value='>',valuetype='ParamChoice'),'Finished':dict(value=0,valuetype='ParamNumber')})}))
            (root/'catalog.json').write_text(json.dumps(catalog)); (root/'effect-rack.json').write_text(json.dumps(rack))
            catalogs = {}; profiles = {}
            for cid, value in [(101,.2),(102,.4)]:
                variant = copy.deepcopy(catalog); variant['layers'][0]['active'] = cid-100
                source = next(t for t in variant['targets'] if t['id']=='source:101'); source['id'] = 'source:'+str(cid); source['clip_id'] = cid; source['params'][0].update(id=cid*10,value=value)
                catalogs[str(cid)] = variant
                profiles[str(cid)] = dict(reference='fixture',targets=[dict(id=source['id'],identity=[source.get(k) for k in ('kind','scope','layer_id','clip_id','effect_name')],params=[dict(source['params'][0],source='static')])])
            (root/'all-catalogs.json').write_text(json.dumps(catalogs)); (root/'authored-clips.json').write_text(json.dumps(dict(epoch='rack-test',auto_layers=[1],clips=profiles)))
            (root/'scan.py').write_text("from pathlib import Path\nprint(Path(__file__).with_name('catalog.json').read_text())\n")
            (root/'bridge.py').write_text('''import json,sys
from pathlib import Path
print(json.dumps({'connected':True}),flush=True)
for line in sys.stdin:
 with open('output.jsonl','a') as f:f.write(line)
 m=json.loads(line)
 if m.get('path','').endswith('/connect'):
  cid=m['path'].split('/')[-2];Path('catalog.json').write_text(json.dumps(json.loads(Path('all-catalogs.json').read_text())[cid]))
 if m['cmd']=='observe':print(json.dumps(dict(native_epoch=m['epoch'],native_values=[[14,.01]])),flush=True)
 if m.get('rpc'):
  result={'ok':True}
  if m['cmd'] in ('animation_get','animation_set'):
   key=str(m['id']);programs=json.loads(Path('native-programs.json').read_text());result=programs.get(key,{'phase_source':'static','parameters':{}})
   if 'source' in m:result={'phase_source':m['source'],'parameters':{}}
   for name,value in m.get('fields',{}).items():result['parameters'][name]={'value':value,'valuetype':'ParamChoice' if isinstance(value,str) else 'ParamRange'}
   programs[key]=result;Path('native-programs.json').write_text(json.dumps(programs));result=dict(result,parameter={'id':m['id'],'value':.42,'min':0,'max':1,'in':0,'out':1})
  print(json.dumps(dict(rpc=m['rpc'],data=result)),flush=True)
''')
            proc = await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            try:
                self.assertTrue(await asyncio.wait_for(proc.stdout.readline(),5))
                async with websockets.connect(f'ws://127.0.0.1:{wsport}') as ws:
                    async def receive(predicate):
                        async def loop():
                            while True:
                                message = json.loads(await ws.recv())
                                if predicate(message): return message
                        return await asyncio.wait_for(loop(),5)
                    async def command(**data): await ws.send(json.dumps(data))
                    def messages(): return [json.loads(line) for line in (root/'output.jsonl').read_text().splitlines()]
                    await receive(lambda m:m['type']=='catalog' and m['epoch']=='rack-test')
                    await command(cmd='watch',targets=['effect:1']); await command(cmd='arm',on=True)
                    await receive(lambda m:m['type']=='state' and m['armed'])
                    for control,value,error in [('lock',1,'Expected on/off'),('tint','Missing','Unknown choice'),('lock','true','Expected on/off'),('tint',False,'Unknown choice')]:
                        count=len(messages());await command(cmd='rack_parameter',epoch='rack-test',row='stage',control=control,value=value)
                        await receive(lambda m:m['type']=='state' and error in m.get('error',''))
                        self.assertFalse(any(m['cmd'] in ('claim','animation_set','values','request') for m in messages()[count:]))
                    for control,pid,value in [('lock',13,True),('tint',16,'Blue')]:
                        native[pid]=value;count=len(messages())
                        await command(cmd='rack_parameter',epoch='rack-test',row='stage',control=control,value=value)
                        state=await receive(lambda m:m['type']=='state' and m['values'][str(pid)]['value']==value and not m['values'][str(pid)]['pending'])
                        self.assertEqual(state['effect_rack']['stage']['controls'][control]['value'],value)
                        writes=messages()[count:]
                        self.assertTrue(any([pid,value] in m.get('values',[]) for m in writes))
                        self.assertFalse(any(m.get('id')==pid and m['cmd']=='animation_set' for m in writes))
                    count = len(messages()); await command(cmd='rack_fire',epoch='stale',row='stage',pad='twitch')
                    await receive(lambda m:m['type']=='state' and 'Composition changed' in m.get('error',''))
                    self.assertFalse(any(m['cmd'] in ('claim','request') for m in messages()[count:]))
                    # Soft toggles set zero before enabling, fade, and bypass only
                    # after the fade-out endpoint. Their original strength survives.
                    await command(cmd='rack_control',epoch='rack-test',row='feedback',pad='mirror',action='opacity',amount=.37)
                    await receive(lambda m:m['type']=='state' and m['effect_rack']['feedback']['levels']['mirror']['value']==.37)
                    await command(cmd='rack_timing',epoch='rack-test',row='feedback',pad='mirror',length=1)
                    await receive(lambda m:m['type']=='state' and m['session']['loops']['feedback']['timings']['mirror']==1)
                    count=len(messages());native[11]=False
                    await command(cmd='rack_control',epoch='rack-test',row='feedback',pad='mirror',action='enable',on=True)
                    await receive(lambda m:m['type']=='state' and m['effect_rack']['feedback']['active']['mirror'] and 0<m['values']['10']['value']<.37)
                    await receive(lambda m:m['type']=='state' and not m['effect_rack']['feedback']['active']['mirror'] and abs(m['values']['10']['value']-.37)<1e-6)
                    writes=messages()[count:];start=next(i for i,m in enumerate(writes) if m.get('path')=='/parameter/by-id/10' and m.get('value',{}).get('value')==0)
                    enabled=next(i for i,m in enumerate(writes) if m.get('path')=='/parameter/by-id/11' and m.get('value',{}).get('value') is False);self.assertLess(start,enabled)
                    count=len(messages());native[11]=True
                    await command(cmd='rack_control',epoch='rack-test',row='feedback',pad='mirror',action='enable',on=False)
                    during=await receive(lambda m:m['type']=='state' and m['effect_rack']['feedback']['active']['mirror'] and 0<m['values']['10']['value']<.37)
                    self.assertFalse(during['values']['11']['value']);self.assertFalse(during['effect_rack']['feedback']['enabled']['mirror'])
                    await receive(lambda m:m['type']=='state' and not m['effect_rack']['feedback']['active']['mirror'] and abs(m['values']['10']['value']-.37)<1e-6 and m['values']['11']['value'])
                    writes=messages()[count:];zero=next(i for i,m in enumerate(writes) if m.get('path')=='/parameter/by-id/10' and m.get('value',{}).get('value')==0)
                    bypass=next(i for i,m in enumerate(writes) if m.get('path')=='/parameter/by-id/11' and m.get('value',{}).get('value') is True);self.assertLess(zero,bypass)
                    count=len(messages());await command(cmd='rack_fire',epoch='rack-test',row='feedback',pad='mirror')
                    await receive(lambda m:m['type']=='state' and 'toggle, not a one-shot' in m.get('error',''))
                    self.assertFalse(any(m.get('cmd') in ('claim','request') for m in messages()[count:]))
                    await asyncio.sleep(.05)
                    await command(cmd='recovery',epoch='rack-test',action='capture',name='base')
                    await receive(lambda m:m['type']=='state' and m['session']['recovery']['base'] and not m['session']['busy'])
                    saved = json.loads((root/'recovery.json').read_text())['rack-test|base']
                    self.assertEqual(saved['targets']['effect:1']['params']['14']['value'],.42)
                    await command(cmd='rack_parameter',epoch='rack-test',row='stage',control='factor',value=.8)
                    await receive(lambda m:m['type']=='state' and m['values']['14']['value']==.8)
                    self.assertEqual(json.loads((root/'native-programs.json').read_text())['14']['phase_source'],'static')
                    await receive(lambda m:m['type']=='state' and m['values']['14']['owned'])
                    await command(cmd='recovery',epoch='rack-test',action='return',name='base')
                    state = await receive(lambda m:m['type']=='state' and not m['session']['busy'] and m['values']['14']['value']==.42)
                    self.assertTrue(state['armed']);self.assertFalse(state['values']['14']['owned'])
                    restored_program=json.loads((root/'native-programs.json').read_text())['14']
                    self.assertEqual(restored_program['phase_source'],'timeline');self.assertEqual(restored_program['parameters']['Duration']['value'],4.6)
                    # Cross-clip return must run after authored startup, preserving
                    # edited motion rather than leaving the freshly loaded baseline.
                    await command(cmd='watch',targets=['effect:1','source:101'])
                    await command(cmd='range',id=1010,lo=.6,hi=.9)
                    await command(cmd='drive',id=1010,on=True)
                    await receive(lambda m:m['type']=='state' and m['values'].get('1010',{}).get('drive'))
                    await command(cmd='recovery',epoch='rack-test',action='capture',name='base')
                    await receive(lambda m:m['type']=='state' and not m['session']['busy'] and m['values'].get('1010',{}).get('lo')==.6)
                    await command(cmd='launch',layer_id=1,clip_id=102)
                    await receive(lambda m:m['type']=='catalog' and m['layers'][0]['active']==2)
                    await command(cmd='recovery',epoch='rack-test',action='return',name='base')
                    await receive(lambda m:m['type']=='catalog' and m['layers'][0]['active']==1)
                    restored = await receive(lambda m:m['type']=='state' and not m['session']['busy'] and m['values'].get('1010',{}).get('drive'))
                    self.assertEqual(restored['values']['1010']['lo'],.6); self.assertEqual(restored['values']['1010']['hi'],.9)
                    await asyncio.sleep(.15)
                    restored = await receive(lambda m:m['type']=='state' and not m['session']['busy'])
                    self.assertTrue(restored['values']['1010']['drive']); self.assertEqual(restored['values']['1010']['lo'],.6)
                    # Rack retrigger decays back to its original steady level.
                    native[11] = False
                    await command(cmd='manual',id=11,value=False); await command(cmd='manual',id=10,value=.35)
                    await receive(lambda m:m['type']=='state' and m['values']['10']['value']==.35 and not m['values']['11']['pending'])
                    await command(cmd='rack_fire',epoch='rack-test',row='stage',pad='twitch',amount=.8,beats=1)
                    await receive(lambda m:m['type']=='state' and m['effect_rack']['stage']['active']['twitch'])
                    await command(cmd='rack_fire',epoch='rack-test',row='stage',pad='twitch',amount=.9,beats=.5)
                    await receive(lambda m:m['type']=='state' and not m['effect_rack']['stage']['active']['twitch'] and m['values']['10']['value']==.35 and not m['values']['11']['value'])
                    native[11] = True
                    await command(cmd='manual',id=11,value=True); await command(cmd='manual',id=10,value=.9)
                    await receive(lambda m:m['type']=='state' and m['values']['10']['value']==.9 and m['values']['11']['value'] and not m['values']['11']['pending'])
                    await command(cmd='rack_fire',epoch='rack-test',row='stage',pad='twitch',amount=.6,beats=.5)
                    await receive(lambda m:m['type']=='state' and m['effect_rack']['stage']['active']['twitch'])
                    await receive(lambda m:m['type']=='state' and not m['effect_rack']['stage']['active']['twitch'] and m['values']['10']['value']==.9 and m['values']['11']['value'])
                    # Opt-in contrast retains one-shot pulse mode: an enabled
                    # full baseline dips, while zero rises, then both return.
                    self.assertEqual(contrast['mode'],'pulse')
                    for baseline, peak in [(1,.35),(0,.65)]:
                        with self.subTest(contrast_baseline=baseline):
                            native[11]=False
                            await command(cmd='manual',id=11,value=False);await command(cmd='manual',id=10,value=baseline)
                            await receive(lambda m:m['type']=='state' and m['values']['10']['value']==baseline and not m['values']['11']['value'] and not m['values']['11']['pending'])
                            count=len(messages())
                            await command(cmd='rack_fire',epoch='rack-test',row='stage',pad='twitch_contrast',amount=.65,beats=.5)
                            await receive(lambda m:m['type']=='state' and m['effect_rack']['stage']['active']['twitch_contrast'])
                            await receive(lambda m:m['type']=='state' and not m['effect_rack']['stage']['active']['twitch_contrast'] and m['values']['10']['value']==baseline and not m['values']['11']['value'])
                            self.assertTrue(any(m.get('path')=='/parameter/by-id/10' and abs(m.get('value',{}).get('value',99)-peak)<1e-6 for m in messages()[count:]))
                    await command(cmd='rack_sequence',epoch='rack-test',row='stage',kick='twitch',snare='twitch',pattern='alternate',strength=.7,length=.5,running=False)
                    await receive(lambda m:m['type']=='state' and m['session']['loops']['stage']['pattern']=='alternate')
                    settings = json.loads((root/'session-settings.json').read_text())['rack-test']['stage']
                    self.assertEqual(settings['strength'],.7); self.assertNotIn('running',settings)
                    # A second client can disarm while a slow capture awaits IO.
                    delay = True
                    await command(cmd='recovery',epoch='rack-test',action='capture',name='safe')
                    await receive(lambda m:m['type']=='state' and m['session']['busy'])
                    async with websockets.connect(f'ws://127.0.0.1:{wsport}') as second:
                        await second.send(json.dumps(dict(cmd='manual',id=14,value=.9)))
                        await receive(lambda m:m['type']=='state' and 'Recovery in progress' in m.get('error',''))
                        await second.send(json.dumps(dict(cmd='arm',on=False)))
                        await receive(lambda m:m['type']=='state' and not m['armed'])
                    await receive(lambda m:m['type']=='state' and 'cancelled' in m.get('error',''))
                    self.assertNotIn('rack-test|safe',json.loads((root/'recovery.json').read_text()))
                    await command(cmd='arm',on=True); await receive(lambda m:m['type']=='state' and m['armed'])
                    await command(cmd='recovery',epoch='stale',action='clear',name='base')
                    await receive(lambda m:m['type']=='state' and 'Composition changed' in m.get('error',''))
                    self.assertIn('rack-test|base',json.loads((root/'recovery.json').read_text()))
                    await command(cmd='recovery',epoch='rack-test',action='clear',name='base')
                    await receive(lambda m:m['type']=='state' and not m['session']['recovery']['base'])
                    self.assertNotIn('rack-test|base',json.loads((root/'recovery.json').read_text()))
            finally:
                if proc.returncode is None: proc.terminate()
                await proc.communicate(); api.close(); await api.wait_closed()


if __name__ == '__main__': unittest.main()
