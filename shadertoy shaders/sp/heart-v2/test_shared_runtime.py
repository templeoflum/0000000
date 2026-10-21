"""Real Heart + discovery + bridge processes against an isolated fake Arena."""
import asyncio
import copy
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import websockets
from test_phase_detection import fixture

ROOT=Path(__file__).parent


class SharedRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_external_clip_handoff_and_frames_preserve_native_programs(self):
        native=fixture();layer=native['layers'][0];second=copy.deepcopy(layer['clips'][0]);second['id']=41
        for p in second['video']['sourceparams'].values():p['id']+=100
        layer['clips'].append(second);active=40;calls=[];writes=[]
        def allparams(obj):
            if isinstance(obj,dict):
                if obj.get('valuetype'):yield obj
                for v in obj.values():yield from allparams(v)
            elif isinstance(obj,list):
                for v in obj:yield from allparams(v)
        parameters={p['id']:p for p in allparams(native)}
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path=self.path.removeprefix('/api/v1');calls.append(path)
                if path=='/composition':
                    data=copy.deepcopy(native)
                    for c in data['layers'][0]['clips']:c['connected']['value']='Connected' if c['id']==active else 'Disconnected'
                elif path.endswith('/clips/active'):data=next(c for c in layer['clips'] if c['id']==active)
                elif path.startswith('/parameter/by-id/'):
                    pid=int(path.split('/')[3]);data=parameters[pid]
                    if path.endswith('/phase-source'):data=dict(phase_source='timeline' if pid in (2,5,105) else 'static',parameters={'PlayDirection':{'value':'||'}})
                elif '/effects/by-id/' in path:data=next(f for f in layer['video']['effects'] if f['id']==int(path.rsplit('/',1)[1]))
                elif '/clips/' in path:
                    data=copy.deepcopy(layer['clips'][int(path.rsplit('/',1)[1])-1]);data['connected']['value']='Connected' if data['id']==active else 'Disconnected'
                else:self.send_error(404);return
                raw=json.dumps(data).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
            def do_PUT(self):writes.append(self.path);self.send_response(204);self.end_headers()
            def do_DELETE(self):writes.append(self.path);self.send_response(204);self.end_headers()
            def log_message(self,*args):pass
        api=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=api.serve_forever,daemon=True).start()
        osc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);osc.bind(('127.0.0.1',0));osc.setblocking(False)
        def port():
            with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
        wsport=port();env=dict(os.environ,HEART_V2_HTTP_PORT=str(port()),HEART_V2_WS_PORT=str(wsport),HEART_V2_ARENA=f'http://127.0.0.1:{api.server_port}/api/v1',HEART_V2_TRANSPORT='http',HEART_V2_OSC_PORT=str(osc.getsockname()[1]))
        env.pop('HEART_V2_SOCKET',None);env.pop('HEART_V2_DISCOVERY',None)
        packets=[]
        async def drain():
            while True:packets.append((time.perf_counter(),await asyncio.get_running_loop().sock_recv(osc,65536)))
        reader=asyncio.create_task(drain())
        try:
            with tempfile.TemporaryDirectory(prefix='heart-shared-runtime-') as directory:
                root=Path(directory)
                for p in ROOT.glob('*.py'):shutil.copy(p,root/p.name)
                for name in ('index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css'):shutil.copy(ROOT/name,root/name)
                proc=await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,env=env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
                try:
                    self.assertTrue(await asyncio.wait_for(proc.stdout.readline(),5))
                    async with websockets.connect(f'ws://127.0.0.1:{wsport}',max_size=8*1024*1024) as ws:
                        catalogue={}
                        async def until(predicate):
                            nonlocal catalogue
                            async with asyncio.timeout(8):
                                while True:
                                    m=json.loads(await ws.recv())
                                    if m['type']=='catalog':catalogue=m
                                    if m['type']=='catalog_patch':
                                        from catalog_updates import apply_patch
                                        catalogue=apply_patch(catalogue,m['patch']);m=dict(catalogue,type='catalog')
                                    if predicate(m):return m
                        await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
                        await until(lambda m:m['type']=='state' and m['connected'])
                        await ws.send(json.dumps(dict(cmd='arm',on=True)))
                        await until(lambda m:m['type']=='state' and m['metrics']['sent']>10)
                        self.assertTrue(any(b'/clips/1/' in p for _,p in packets))
                        switched=time.perf_counter();active=41
                        await until(lambda m:m['type']=='catalog' and any(t.get('clip_id')==41 and any(p.get('native_phase') for p in t['params']) for t in m['targets']))
                        await until(lambda m:m['type']=='state' and m['metrics']['sent']>50)
                        async with asyncio.timeout(2):
                            while not any(b'/clips/2/' in p for _,p in packets):await asyncio.sleep(.01)
                        first=min(t for t,p in packets if b'/clips/2/' in p)
                        self.assertLess(first-switched,.8)
                        self.assertEqual(calls.count('/composition'),1,'No periodic full composition reads')
                        self.assertEqual(writes,[],'Phase control must not rewrite values, ranges or programs')
                        # The same range edit retains ownership and normalized Amount.
                        await ws.send(json.dumps(dict(cmd='parameter_motion',id=105,amount=.25,range_offset=.7,seconds=0)))
                        parameters[105]['in']=.27;parameters[105]['out']=.28
                        await until(lambda m:m['type']=='catalog' and any(p['id']==105 and p.get('in')==.27 for t in m['targets'] for p in t['params']))
                        await ws.send(json.dumps(dict(cmd='watch',targets=['source:41'],native_ids=[])))
                        s=await until(lambda m:m['type']=='state' and '105' in m['values'])
                        self.assertTrue(s['values']['105']['drive']);self.assertEqual(s['values']['105']['motion']['amount'],.25)
                        # Remember the complete relationship, including Shuffle's slot,
                        # through two native clip changes and a real process restart.
                        for d in [dict(cmd='relationship',target='source:41',pattern=4,spread=2,seed=3,fm=.2,seconds=0),
                                  dict(cmd='settings',target='source:41',rate=.025,amount=.6,seconds=0),
                                  dict(cmd='drive_bank',epoch=catalogue['epoch'],target='source:41',action='shuffle'),
                                  dict(cmd='parameter_motion',id=105,ratio='2:3',offset=.42,mult=.025,seconds=0),
                                  dict(cmd='motion_multiplier',epoch=catalogue['epoch'],scope='global',value=.5,seconds=0),
                                  dict(cmd='drive',id=105,on=False),
                                  dict(cmd='parameter_lock',epoch=catalogue['epoch'],id=105,on=True)]:
                            await ws.send(json.dumps(d))
                        s=await until(lambda m:m['type']=='state' and m['values'].get('105',{}).get('locked'))
                        expected={k:v for k,v in s['values']['105']['motion'].items() if k!='cycles_per_beat'}
                        group=s['groups']['source:41']
                        self.assertIn('family_slot',expected)
                        active=40
                        await until(lambda m:m['type']=='catalog' and any(t.get('clip_id')==40 for t in m['targets']))
                        active=41
                        await until(lambda m:m['type']=='catalog' and any(t.get('clip_id')==41 and any(p.get('native_phase') for p in t['params']) for t in m['targets']))
                        s=await until(lambda m:m['type']=='state' and m['values'].get('105',{}).get('native_phase'))
                        self.assertFalse(s['values']['105']['drive'])
                        self.assertEqual({k:v for k,v in s['values']['105']['motion'].items() if k!='cycles_per_beat'},expected)
                    proc.terminate();await proc.communicate()
                    self.assertTrue((root/'motion-settings.json').exists())
                    proc=await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,env=env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
                    self.assertTrue(await asyncio.wait_for(proc.stdout.readline(),5))
                    async with websockets.connect(f'ws://127.0.0.1:{wsport}',max_size=8*1024*1024) as ws:
                        catalogue={}
                        await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
                        await ws.send(json.dumps(dict(cmd='watch',targets=['source:41','effect:32'],native_ids=[])))
                        s=await until(lambda m:m['type']=='state' and m['connected'] and m['values'].get('105',{}).get('native_phase'))
                        self.assertFalse(s['armed']);self.assertFalse(s['values']['105']['owned'])
                        self.assertEqual({k:v for k,v in s['values']['105']['motion'].items() if k!='cycles_per_beat'},expected)
                        self.assertEqual(s['groups']['source:41'],group)
                        self.assertEqual(s['motion_multipliers']['global'],.5)
                        await ws.send(json.dumps(dict(cmd='arm',on=True)))
                        s=await until(lambda m:m['type']=='state' and m['metrics']['sent']>10)
                        self.assertTrue(s['values']['2']['drive']);self.assertFalse(s['values']['105']['drive'])
                        self.assertEqual(writes,[],'Recall must not restore native values, ranges or timeline programs')
                        self.assertEqual(calls.count('/composition'),2,'Only one cold read per process')
                finally:
                    if proc.returncode is None:proc.terminate()
                    await proc.wait()
        finally:
            reader.cancel();await asyncio.gather(reader,return_exceptions=True);osc.close();await asyncio.to_thread(api.shutdown);api.server_close()


if __name__=='__main__':unittest.main()
