"""Rack scope, automatic release and the actual server command protocol."""
import asyncio, copy, json, socket, sys, tempfile, time, unittest
from pathlib import Path
import websockets
from server import Engine
from play_actions import hit_bindings

ROOT = Path(__file__).parent

def fixture():
    targets = []
    bindings = []
    for i in range(1, 5):
        t = dict(id=f'effect:{i}', kind='effect', scope='layer', layer_id=i,
                 effect_name='Corrupt', label=f'Layer {i} / Corrupt', params=[])
        for n, name, kind, value in [(0,'Opacity','ParamRange',0), (1,'Bypass','ParamBoolean',True), (2,'MELT','ParamEvent',False)]:
            t['params'].append(dict(id=i*10+n,name=name,type=kind,value=value,min=0,max=1,options=[]))
        targets.append(t)
        bindings.append(dict(target=t['id'],identity=['layer',i,None,None,'Corrupt'],opacity=i*10,bypass=i*10+1,event=i*10+2,event_name='MELT'))
    rows = []
    for key, members in [('stage',bindings[:1]),('figure',bindings[1:2]),('field',bindings[2:])]:
        rows.append(dict(id=key,label=key,pads=[dict(id='melt',label='Melt',bindings=members)],color=[{k:v for k,v in b.items() if k not in ('event','event_name')} for b in members]))
    return dict(type='catalog',epoch='rack-test',targets=targets,layers=[]), dict(epoch='rack-test',rows=rows)

class HitTests(unittest.TestCase):
    def engine(self):
        c, rack = fixture(); e = Engine(); e.rack_config=rack; e.reconcile(c); e.armed=e.connected=True
        return e
    def test_linked_validation_rejects_stale_or_partial_binding_before_writes(self):
        e=self.engine(); d=dict(epoch='rack-test',bindings=copy.deepcopy(e.rack_config['rows'][2]['pads'][0]['bindings']))
        self.assertEqual(len(hit_bindings(e,d)),2)
        for change in [lambda x:x.update(epoch='old'), lambda x:x['bindings'][1].update(opacity=10), lambda x:x['bindings'][1].update(event=12), lambda x:x['bindings'][1]['identity'].__setitem__(1,99), lambda x:x['bindings'].append(x['bindings'][0]), lambda x:x['bindings'].__setitem__(1,None)]:
            bad=copy.deepcopy(d);change(bad)
            with self.assertRaises(ValueError):hit_bindings(e,bad)
            self.assertFalse(e.owned)
    def test_pulse_retrigger_hold_and_manual_takeover(self):
        e=self.engine(); e.hold=True
        e.effect_pulse(10,.8,.2,key='stage:melt'); self.assertAlmostEqual(dict(e.tick(.1,time.perf_counter()))[10],.4)
        self.assertTrue(e.rack_state()['stage']['active']['melt'])
        e.effect_pulse(10,1,.2,key='stage:melt'); self.assertAlmostEqual(dict(e.tick(.1,time.perf_counter()))[10],.5)
        self.assertEqual(dict(e.tick(.1,time.perf_counter()))[10],0)
        self.assertFalse(e.rack_state()['stage']['active']['melt'])
        e.effect_pulse(10,.8,.2);e.manual(10,.3,duration=0);e.hold=False
        self.assertAlmostEqual(dict(e.tick(.4,time.perf_counter()))[10],.3)
        e.pending_hits[10]='pending';e.disarm();self.assertFalse(e.pending_hits);self.assertFalse(e.envelopes)
    def test_rack_offline_and_mixed_do_not_expand_readback(self):
        e=self.engine();e.observed[30]=(.2,0);e.observed[40]=(.8,0)
        self.assertTrue(e.rack_state()['field']['mixed']);self.assertFalse(e.watched)
        c=copy.deepcopy(e.catalog);c['targets'][3]['effect_name']='Replacement';e.reconcile(c)
        self.assertFalse(e.rack_state()['field']['ready']);self.assertTrue(e.rack_state()['stage']['ready'])

class HitRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_gate_trigger_decay_color_clear_and_disarm(self):
        def port():
            with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
        http, wsport=port(),port();c,rack=fixture()
        with tempfile.TemporaryDirectory(prefix='heart-hit-runtime-') as directory:
            root=Path(directory)
            for name in ['session_controls.py','authored.py','server.py','motion.py','smart_motion.py','motion_clock.py','motion_frames.py','motion_memory.py','motion_persistence.py','catalog_updates.py','performance.py','play_actions.py','index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css']:
                text=(ROOT/name).read_text()
                if name=='server.py':text=text.replace("os.environ.get('HEART_V2_DISCOVERY')=='fixture'",'True').replace('8875',str(http)).replace('8876',str(wsport))
                (root/name).write_text(text)
            (root/'catalog.json').write_text(json.dumps(c));(root/'effect-rack.json').write_text(json.dumps(rack))
            (root/'scan.py').write_text("from pathlib import Path\nprint(Path(__file__).with_name('catalog.json').read_text())\n")
            (root/'bridge.py').write_text('''import json,sys,time
from pathlib import Path
print(json.dumps({'connected':True}),flush=True)
for line in sys.stdin:
 with open('output.jsonl','a') as f:f.write(line)
 m=json.loads(line)
 if m['cmd']=='claim' and Path('delay').exists():time.sleep(.2)
 if m.get('rpc'):
  fail=Path('fail').exists() and m.get('path')=='/parameter/by-id/40'
  print(json.dumps(dict(rpc=m['rpc'],**({'error':'native rejected gate'} if fail else {'data':{'ok':True}}))),flush=True)
''')
            proc=await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            try:
                await asyncio.wait_for(proc.stdout.readline(),5)
                async with websockets.connect(f'ws://127.0.0.1:{wsport}') as ws:
                    async def receive(predicate):
                        async def loop():
                            while True:
                                m=json.loads(await ws.recv())
                                if predicate(m):return m
                        return await asyncio.wait_for(loop(),5)
                    async def command(**d):await ws.send(json.dumps(d))
                    def messages():return [json.loads(x) for x in (root/'output.jsonl').read_text().splitlines()]
                    await receive(lambda m:m['type']=='catalog' and m['epoch']=='rack-test')
                    await command(cmd='watch',targets=[t['id'] for t in c['targets']]);await command(cmd='arm',on=True)
                    await receive(lambda m:m['type']=='state' and m['armed'])
                    await command(cmd='hold',on=True)
                    hit=dict(cmd='effect_hit',epoch='rack-test',bindings=rack['rows'][2]['pads'][0]['bindings'],beats=1,amount=.8,key='field:melt')
                    await command(**hit)
                    await receive(lambda m:m['type']=='state' and m['effect_rack']['field']['active']['melt'])
                    state=await receive(lambda m:m['type']=='state' and not m['effect_rack']['field']['active']['melt'])
                    self.assertEqual(state['values']['30']['value'],0);self.assertEqual(state['values']['40']['value'],0)
                    out=messages();gates=[i for i,m in enumerate(out) if m.get('value')=={'value':.8}];triggers=[i for i,m in enumerate(out) if m.get('path','').endswith('/trigger')]
                    self.assertEqual(len(triggers),2);self.assertLess(max(gates),min(triggers));self.assertFalse(any(m['cmd']=='animation_set' for m in out))
                    await command(cmd='effect_color',epoch='rack-test',bindings=rack['rows'][2]['color'],amount=.37)
                    await receive(lambda m:m['type']=='state' and m['values']['30']['value']==.37 and m['values']['40']['value']==.37)
                    self.assertTrue(any(m['cmd']=='values' and [30,.37] in m['values'] and [40,.37] in m['values'] for m in messages()))
                    await command(cmd='effect_color',epoch='rack-test',bindings=rack['rows'][2]['color'],amount=0)
                    await receive(lambda m:m['type']=='state' and m['values']['30']['value']==0)
                    (root/'fail').touch();n=len(messages());await command(**hit)
                    await receive(lambda m:m['type']=='state' and 'native rejected' in m.get('error',''))
                    out=messages()[n:];self.assertFalse(any(m.get('path','').endswith('/trigger') for m in out));self.assertTrue(any(m.get('path')=='/parameter/by-id/30' and m.get('value')=={'value':0} for m in out));(root/'fail').unlink()
                    (root/'delay').touch();n=len(messages());await command(**hit)
                    for _ in range(100):
                        if any(m['cmd']=='claim' for m in messages()[n:]):break
                        await asyncio.sleep(.005)
                    async with websockets.connect(f'ws://127.0.0.1:{wsport}') as second:await second.send(json.dumps(dict(cmd='arm',on=False)));await receive(lambda m:m['type']=='state' and not m['armed'])
                    out=messages()[n:];self.assertFalse(any(m.get('path','').endswith('/trigger') for m in out))
                    for pid in [30,40]:self.assertTrue(any(m.get('path')==f'/parameter/by-id/{pid}' and m.get('value')=={'value':0} for m in out))
            finally:
                if proc.returncode is None:proc.terminate()
                await proc.communicate()

class NativeRackControls(unittest.TestCase):
 def engine(self):
  c,rack=fixture();e=Engine()
  for i,t in enumerate(c['targets'],1):t['params'].append(dict(id=i*10+3,name='MELT_LOCK',type='ParamBoolean',value=False,min=0,max=1,options=[]))
  for row in rack['rows']:
   row['pads'][0]['mode']='trigger'
   row['pads'].append(dict(id='pixel',mode='latch',bindings=[dict(b,latch=b['opacity']+3,latch_name='MELT_LOCK') for b in row['pads'][0]['bindings']]))
  e.rack_config=rack;e.reconcile(c);return e
 def test_lut_enable_and_event_are_independent(self):
  e=self.engine();d=dict(epoch='rack-test',row='field',pad='melt')
  with self.assertRaises(ValueError):e.rack_plan(dict(d,action='trigger'))
  values,events=e.rack_plan(dict(d,action='enable',on=True));self.assertEqual(events,[]);self.assertEqual(values,[(30,1.),(31,False),(40,1.),(41,False)])
  for pid,v in values:e.params[pid][1]['value']=v
  values,events=e.rack_plan(dict(d,action='trigger'));self.assertEqual(values,[]);self.assertEqual(events,[32,42])
 def test_melt_latch_off_leaves_effect_enabled(self):
  e=self.engine();values,events=e.rack_plan(dict(epoch='rack-test',row='field',pad='pixel',action='latch',on=False));self.assertEqual(events,[]);self.assertEqual(values,[(30,1.),(31,False),(33,False),(40,1.),(41,False),(43,False)])
  e.observed[33]=(True,0);e.observed[43]=(True,0);self.assertTrue(e.rack_state()['field']['latched']['pixel'])
 def test_lut_power_keeps_each_dialed_amount_and_remembers_zero(self):
  e=self.engine();d=dict(epoch='rack-test',row='field',pad='melt')
  for pid,value in [(30,.37),(40,.61)]:e.params[pid][1]['value']=value
  for on in (True,False,True):
   values,events=e.rack_plan(dict(d,action='enable',on=on))
   self.assertEqual(values,[(31,not on),(41,not on)]);self.assertEqual(events,[])
  for pid in (30,40):e.params[pid][1]['value']=0
  values,_=e.rack_plan(dict(d,action='enable',on=True))
  self.assertEqual(values,[(30,.37),(31,False),(40,.61),(41,False)])
 def test_replaced_latch_rejects_entire_linked_row(self):
  e=self.engine();e.params[43][1]['name']='Other'
  with self.assertRaises(ValueError):e.rack_plan(dict(epoch='rack-test',row='field',pad='pixel',action='latch',on=True))
