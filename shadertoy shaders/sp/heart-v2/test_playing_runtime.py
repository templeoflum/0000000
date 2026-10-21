"""New playing commands against an isolated backend and fake native worker."""
import asyncio,json,socket,sys,tempfile,unittest
from pathlib import Path
import websockets
from test_launch import catalog
ROOT=Path(__file__).parent
class PlayingRuntimeTests(unittest.IsolatedAsyncioTestCase):
 async def test_playing_actions_use_native_identity_and_guard_releases(self):
  def port():
   with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
  http,wsport=port(),port()
  with tempfile.TemporaryDirectory(prefix='heart-playing-runtime-') as directory:
   root=Path(directory)
   for name in ['session_controls.py','authored.py','server.py','scan.py','motion.py','smart_motion.py','motion_clock.py','motion_frames.py','motion_memory.py','motion_persistence.py','catalog_updates.py','performance.py','play_actions.py','index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css']:
    text=(ROOT/name).read_text()
    if name=='server.py':text=text.replace("os.environ.get('HEART_V2_DISCOVERY')=='fixture'",'True').replace('8875',str(http)).replace('8876',str(wsport))
    (root/name).write_text(text)
   (root/'catalog.json').write_text(json.dumps(catalog()))
   (root/'scan.py').write_text("from pathlib import Path\nprint(Path(__file__).with_name('catalog.json').read_text())\n")
   (root/'bridge.py').write_text('''import json,sys
print(json.dumps({'connected':True}),flush=True)
for line in sys.stdin:
 with open('output.jsonl','a') as f:f.write(line)
 m=json.loads(line)
 if m['cmd']=='request':
  c=json.load(open('catalog.json'));path=m['path'];layer=next(l for l in c['layers'] if l['id']==10)
  if '/connect' in path:
   clipid=int(path.split('/')[-2]);layer['active']=next(x['col'] for x in layer['clips'] if x['id']==clipid)
  if path=='/composition/layers/by-id/10/clear':layer['active']=0;c['_changed']=False
  if '/connect' in path or path.endswith('/clear'):
   c['targets']=[t for t in c['targets'] if not(t.get('scope')=='clip' and t.get('layer_id')==10)]
   with open('catalog.json','w') as f:json.dump(c,f)
 if m.get('rpc'):print(json.dumps({'rpc':m['rpc'],'data':{'ok':True}}),flush=True)
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
     await receive(lambda m:m['type']=='catalog' and m['epoch']=='one')
     await command(cmd='watch',targets=[t['id'] for t in catalog()['targets']])
     await command(cmd='arm',on=True);await receive(lambda m:m['type']=='state' and m['armed'])
     await command(cmd='relationship',target='effect:other',pattern=10,spread=2)
     await command(cmd='parameter_motion',id=201,ratio='3:2',mult=-2,offset=.25,shape=.5)
     await command(cmd='motion_scale',targets=['effect:other'],mode='rate',value=2)
     state=await receive(lambda m:m['type']=='state' and m['values'].get('201',{}).get('rate_scale')==2)
     self.assertEqual(state['values']['201']['motion']['ratio'],'3:2')
     await command(cmd='group_level',epoch='one',members=[dict(id=10,target='layer:10',weight=.5)],value=.8)
     await receive(lambda m:m['type']=='state' and abs(m['values']['10']['value']-.4)<1e-6)
     await command(cmd='effect_press',key='linked',ids=[111,201]);await receive(lambda m:m['type']=='state' and m['values']['201']['envelope'])
     await command(cmd='manual',id=111,value=.27);await command(cmd='effect_release',key='linked')
     state=await receive(lambda m:m['type']=='state' and m['values']['201']['envelope']['direction']=='out')
     self.assertIsNone(state['values']['111']['envelope'])
     await command(cmd='layer_action',layer_id=10,action='next',eligible=[102]);await receive(lambda m:m['type']=='catalog' and m['layers'][0]['active']==2 and 'pending_clip' not in m['layers'][0])
     await command(cmd='layer_action',layer_id=10,action='eject');await receive(lambda m:m['type']=='catalog' and m['layers'][0]['active']==0 and 'pending_clip' not in m['layers'][0])
     await command(cmd='effect_press',key='final',ids=[201]);await command(cmd='arm',on=False);await receive(lambda m:m['type']=='state' and not m['armed'])
     messages=[json.loads(x) for x in (root/'output.jsonl').read_text().splitlines()]
     paths=[m.get('path') for m in messages if m['cmd']=='request']
     self.assertIn('/composition/clips/by-id/102/connect',paths);self.assertIn('/composition/layers/by-id/10/clear',paths)
     endpoint=next(i for i,m in enumerate(messages) if m.get('path')=='/parameter/by-id/201' and m.get('value')=={'value':0})
     self.assertTrue(any(m['cmd']=='arm' and not m['on'] for m in messages[endpoint+1:]))
     await command(cmd='arm',on=True);await receive(lambda m:m['type']=='state' and m['armed'])
     (root/'api-paused.json').write_text('{"reason":"isolated high-memory test"}')
     state=await receive(lambda m:m['type']=='state' and 'memory guard' in m.get('error',''))
     self.assertFalse(state['armed']);self.assertFalse(state['connected'])
     await command(cmd='arm',on=True)
     state=await receive(lambda m:m['type']=='state' and 'not connected' in m.get('error',''))
     self.assertFalse(state['armed'])
   finally:
    if proc.returncode is None:proc.terminate()
    await proc.communicate()
