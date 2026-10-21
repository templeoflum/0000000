"""Actual server protocol, with isolated ports and fake discovery/output workers."""
import asyncio,hashlib,json,socket,sys,tempfile,unittest
from pathlib import Path
import websockets
ROOT=Path(__file__).parent
class RuntimeTests(unittest.IsolatedAsyncioTestCase):
 async def test_reload_lease_and_envelope_protocol(self):
  def port():
   with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
  http_port,ws_port=port(),port()
  with tempfile.TemporaryDirectory(prefix='heart-runtime-') as directory:
   root=Path(directory)
   for name in ['session_controls.py','authored.py','server.py','smart_motion.py','motion_clock.py','motion_frames.py','motion_memory.py','motion_persistence.py','catalog_updates.py','motion.py','performance.py','play_actions.py','index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css']:
    text=(ROOT/name).read_text()
    if name=='server.py':text=text.replace("os.environ.get('HEART_V2_DISCOVERY')=='fixture'",'True').replace('8875',str(http_port)).replace('8876',str(ws_port))
    (root/name).write_text(text)
   catalog=dict(type='catalog',epoch='test',layers=[dict(id=10,i=1,name='Test layer',active=1,clips=[dict(id=101,col=1,name='One'),dict(id=102,col=2,name='Two')])],targets=[dict(id='effect:1',kind='effect',params=[dict(id=1,name='Opacity',type='ParamRange',value=0,min=0,max=1)]),dict(id='effect:2',kind='effect',scope='clip',layer=1,layer_id=10,clip=1,clip_id=101,params=[dict(id=2,name='Opacity',type='ParamRange',value=0,min=0,max=1)])])
   (root/'catalog.json').write_text(json.dumps(catalog))
   (root/'scan.py').write_text("import time\nfrom pathlib import Path\ns=Path(__file__).with_name('catalog.json').read_text()\ntime.sleep(.25)\nprint(s)")
   (root/'bridge.py').write_text("import sys,json\nprint(json.dumps({'connected':True}),flush=True)\nfor line in sys.stdin:\n with open('output.jsonl','a') as f:f.write(line)\n m=json.loads(line)\n if m['cmd']=='request' and m['path']=='/composition/clips/by-id/102/connect':\n  c=json.load(open('catalog.json'));c['layers'][0]['active']=2;t=c['targets'][1];t.update(id='effect:3',clip=2,clip_id=102);t['params'][0]['id']=3\n  with open('catalog.json','w') as f:json.dump(c,f)\n  print(json.dumps({'rpc':m['rpc'],'data':{'ok':True}}),flush=True)\n elif m.get('rpc'):\n  print(json.dumps({'rpc':m['rpc'],'data':{'ok':True}}),flush=True)\n")
   proc=await asyncio.create_subprocess_exec(sys.executable,str(root/'server.py'),cwd=root,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   try:
    ready=await asyncio.wait_for(proc.stdout.readline(),5)
    if not ready:raise RuntimeError((await proc.stderr.read()).decode())
    async with websockets.connect(f'ws://127.0.0.1:{ws_port}') as ws:
     async def receive(predicate):
      async def loop():
       while True:
        m=json.loads(await ws.recv())
        if predicate(m):return m
      return await asyncio.wait_for(loop(),5)
     async def command(**m):await ws.send(json.dumps(m))
     version=await receive(lambda m:m['type']=='surface_version')
     reader,writer=await asyncio.open_connection('127.0.0.1',http_port);writer.write(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n');await writer.drain();response=await reader.read();writer.close();await writer.wait_closed()
     digest=hashlib.sha256(b''.join((root/n).read_bytes() for n in ('index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css'))).hexdigest();self.assertEqual(version['version'],digest);self.assertIn(digest.encode(),response)
     await receive(lambda m:m['type']=='state' and m['connected'] and '1' in m['values'])
     await command(cmd='watch',targets=['effect:2'])
     await receive(lambda m:m['type']=='state' and '2' in m['values'])
     async with websockets.connect(f'ws://127.0.0.1:{ws_port}') as observer:
      await observer.send(json.dumps(dict(cmd='watch',targets=[])))
      while True:
       observed=json.loads(await asyncio.wait_for(observer.recv(),5))
       if observed['type']=='state':break
      self.assertIn('2',observed['values'])
     layout=dict(id='controls',name='Controller check',controls=[dict(id='fader',label='Level',kind='continuous',members=[dict(id=1)])],inputs=[dict(device='midi-test',control='cc:0:7',slot='fader')])
     await command(cmd='layout_save',layout=layout);saved=await receive(lambda m:m['type']=='layout');self.assertIn('contract',saved['layout']['controls'][0]['members'][0])
     await command(cmd='layout_grab',id='controls');await receive(lambda m:m['type']=='state' and m['performance']['active']=='controls')
     await command(cmd='surface_reload',request=1);self.assertTrue((await receive(lambda m:m['type']=='surface_reload'))['allowed'])
     await command(cmd='arm',on=True);s=await receive(lambda m:m['type']=='state' and bool(m['error']));self.assertFalse(s['armed']);self.assertIn('update in progress',s['error'])
     await asyncio.sleep(2.1);await command(cmd='arm',on=True);await receive(lambda m:m['type']=='state' and m['armed'])
     await command(cmd='input',device='midi-test',control='cc:0:7',phase='move',value=.37);await receive(lambda m:m['type']=='state' and m['values']['1']['value']==.37)
     await command(cmd='input_release')
     await command(cmd='surface_reload',request=2);self.assertFalse((await receive(lambda m:m['type']=='surface_reload'))['allowed'])
     await command(cmd='envelope_config',id=1,settings=dict(in_time=.2,out_time=.2,curve='linear'))
     await command(cmd='envelope',id=1,direction='in');s=await receive(lambda m:m['type']=='state' and m['values']['1']['value']==1);self.assertEqual(s['values']['1']['envelope']['progress'],1)
     await command(cmd='envelope',id=1,direction='out');await receive(lambda m:m['type']=='state' and m['values']['1']['value']==0)
     await command(cmd='drive',id=1,on=True);await command(cmd='manual',id=2,value=.6)
     await command(cmd='range',id=1,lo=.2,hi=.7)
     await command(cmd='drive_bank',epoch='test',target='effect:1',action='family',pattern=3)
     await command(cmd='drive_bank',epoch='test',target='effect:1',action='rate',rate=2)
     await command(cmd='drive_bank',epoch='test',target='effect:1',action='shuffle')
     s=await receive(lambda m:m['type']=='state' and m['drive_bank']['effect:1']['rate']==2)
     self.assertEqual(s['drive_bank']['effect:1'],dict(count=1,pattern=3,rate=2,eligible=1,active=1))
     self.assertEqual((s['values']['1']['lo'],s['values']['1']['hi']),(.2,.7))
     self.assertFalse(s['values']['2']['drive']);self.assertEqual(s['values']['2']['value'],.6)
     await command(cmd='parameter_lock',epoch='test',id=1,on=True)
     await command(cmd='drive_all',epoch='test',target='effect:1',on=False)
     s=await receive(lambda m:m['type']=='state' and m['values']['1']['locked'])
     self.assertTrue(s['values']['1']['drive'])
     await command(cmd='parameter_lock',epoch='test',id=1,on=False)
     await command(cmd='refresh');await asyncio.sleep(.05);await command(cmd='launch',layer=1,col=2)
     await receive(lambda m:m['type']=='catalog' and any(t['id']=='effect:3' for t in m['targets']))
     s=await receive(lambda m:m['type']=='state' and m['values']['1']['drive']);self.assertTrue(s['armed']);self.assertEqual(s['metrics']['owned'],1)
     self.assertNotIn('2',s['values']);v=s['values']['1']['value'];await receive(lambda m:m['type']=='state' and m['values']['1']['value']!=v)
     momentary=dict(id='momentary',name='Momentary',controls=[dict(id='pad',kind='button',press=dict(cmd='envelope',id=1,direction='in'),release=dict(cmd='envelope',id=1,direction='out'))],inputs=[])
     await command(cmd='layout_save',layout=momentary);await receive(lambda m:m['type']=='layout')
     await command(cmd='layout_grab',id='momentary');await command(cmd='control',slot='pad',phase='begin',value=1)
     await receive(lambda m:m['type']=='state' and m['values']['1']['value']==1)
     await command(cmd='arm',on=False);await receive(lambda m:m['type']=='state' and not m['armed'])
     output=[json.loads(line) for line in (root/'output.jsonl').read_text().splitlines()];values=[v for m in output if m['cmd'] in ('values','frame') for _,v in m['values']];self.assertIn(1,values);self.assertIn(0,values);self.assertTrue(all(0<=v<=1 for v in values))
     endpoint=next(i for i,m in enumerate(output) if m['cmd']=='request' and m.get('path')=='/parameter/by-id/1' and m.get('value')=={'value':0})
     self.assertTrue(any(m['cmd']=='arm' and not m['on'] for m in output[endpoint+1:]),'release endpoint is acknowledged before disarm')
     launch=next(i for i,m in enumerate(output) if m['cmd']=='request' and m.get('path')=='/composition/clips/by-id/102/connect')
     self.assertTrue(all(pid!=2 for m in output[launch:] if m['cmd'] in ('values','frame') for pid,_ in m['values']))
     self.assertTrue(any(m['cmd']=='bind' and 1 in m.get('keep',[]) and 2 not in m['ids'] for m in output))
   finally:
    if proc.returncode is None:proc.terminate()
    await proc.communicate()
