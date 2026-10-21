"""Visible Heart state is independent of per-client native polling scope."""
import asyncio
import copy
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path
import websockets
from server import Engine

ROOT = Path(__file__).parent


def fixture():
    def target(tid,kind,ids,names=None):
        return dict(id=tid,kind=kind,scope='layer',layer_id=1,params=[dict(id=pid,name=(names or {}).get(pid,str(pid)),type='ParamRange',min=0,max=1,value=.2,options=[]) for pid in ids])
    return dict(type='catalog',epoch='readback-test',layers=[],targets=[target('source:1','source',[1,2]),target('effect:2','effect',[10,11,12]),target('effect:3','effect',[20,21]),target('layer:1','layer',[30,31,32],{30:'Level',31:'Hidden',32:'Other'}),target('crossfader:1','crossfader',[40,41],{40:'phase',41:'curve'})])


class ReadbackScopeTests(unittest.TestCase):
    def engine(self):
        e=Engine();e.reconcile(fixture());return e

    def test_optional_subset_empty_and_legacy_keep_selected_and_priority(self):
        e=self.engine();fixed={1,2,30,31,40};watches={'surface':{'effect:2'}}
        self.assertEqual(set(e.observation_ids(watches,{})),fixed|{10,11,12})
        self.assertEqual(set(e.observation_ids(watches,{'surface':set()})),fixed)
        self.assertEqual(set(e.observation_ids(watches,{'surface':{10,21,999}})),fixed|{10})
        e.selected='effect:2'
        self.assertEqual(set(e.observation_ids(watches,{'surface':set()})),{10,11,12,30,31,40})

    def test_union_checks_each_clients_target_scope_and_retains_full_state(self):
        e=self.engine();watches={'a':{'effect:2'},'b':{'effect:3'}};native={'a':{10,20},'b':{21,11}}
        self.assertEqual(set(e.observation_ids(watches,native)),{1,2,10,21,30,31,40})
        e.watched=set().union(*watches.values())
        self.assertTrue({1,2,10,11,12,20,21}.issubset(e.state()['values']))
        watches.pop('b');native.pop('b')
        self.assertEqual(set(e.observation_ids(watches,native)),{1,2,10,30,31,40})

    def test_large_export_with_empty_native_subset_does_not_expand_polling(self):
        e=self.engine();catalog=copy.deepcopy(e.catalog);catalog['targets'][1]['params']=[dict(id=i,name=str(i),type='ParamRange',min=0,max=1,value=0,options=[]) for i in range(1000,1400)];e.reconcile(catalog);e.watched={'effect:2'}
        self.assertGreater(len(e.state()['values']),256)
        self.assertEqual(set(e.observation_ids({'capture':{'effect:2'}},{'capture':set()})),{1,2,30,31,40})


class ReadbackScopeRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_watch_protocol_legacy_empty_subset_and_disconnect_cleanup(self):
        def port():
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));return sock.getsockname()[1]
        http,wsport=port(),port()
        with tempfile.TemporaryDirectory(prefix='heart-readback-scope-') as directory:
            root=Path(directory)
            for name in ['server.py','session_controls.py','authored.py','motion.py','smart_motion.py','motion_clock.py','motion_frames.py','motion_memory.py','motion_persistence.py','catalog_updates.py','performance.py','play_actions.py']:
                text=(ROOT/name).read_text()
                if name=='server.py':text=text.replace("os.environ.get('HEART_V2_DISCOVERY')=='fixture'",'True').replace('8875',str(http)).replace('8876',str(wsport))
                (root/name).write_text(text)
            (root/'index.html').write_text('<head></head>')
            (root/'catalog.json').write_text(json.dumps(fixture()))
            (root/'scan.py').write_text("from pathlib import Path\nprint(Path(__file__).with_name('catalog.json').read_text())\n")
            (root/'bridge.py').write_text("import sys,json\nprint(json.dumps({'connected':True}),flush=True)\nfor line in sys.stdin:\n with open('output.jsonl','a') as f:f.write(line)\n")
            proc=await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            try:
                self.assertTrue(await asyncio.wait_for(proc.stdout.readline(),5))
                async with websockets.connect(f'ws://127.0.0.1:{wsport}') as first:
                    async def message(predicate):
                        async def loop():
                            while True:
                                value=json.loads(await first.recv())
                                if predicate(value):return value
                        return await asyncio.wait_for(loop(),4)
                    async def observed(expected):
                        async def loop():
                            while True:
                                path=root/'output.jsonl'
                                records=[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
                                observations=[m for m in records if m['cmd']=='observe']
                                if observations and set(observations[-1]['ids'])==expected:return
                                await asyncio.sleep(.005)
                        await asyncio.wait_for(loop(),4)
                    async def watch(ws,**data):await ws.send(json.dumps(dict(cmd='watch',**data)))
                    await message(lambda m:m['type']=='catalog' and m['epoch']=='readback-test')
                    fixed={1,2,30,31,40}
                    await watch(first,targets=['effect:2'],native_ids=[10,20,999]);await observed(fixed|{10})
                    async with websockets.connect(f'ws://127.0.0.1:{wsport}') as second:
                        await watch(second,targets=['effect:3']);await observed(fixed|{10,20,21})
                    await observed(fixed|{10})
                    await watch(first,targets=['effect:2']);await observed(fixed|{10,11,12})
                    await watch(first,targets=['effect:2'],native_ids=[]);await observed(fixed)
                    state=await message(lambda m:m['type']=='state' and '12' in m['values'])
                    self.assertFalse(state['armed']);self.assertTrue({'10','11','12'}.issubset(state['values']))
                    await watch(first,targets=['effect:3'],native_ids=[True])
                    await message(lambda m:m['type']=='state' and 'native parameter IDs' in m.get('error',''))
                    await observed(fixed)
            finally:
                if proc.returncode is None:proc.terminate()
                await proc.communicate()


if __name__=='__main__':unittest.main()
