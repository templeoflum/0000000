"""Transport overload and reconnect limits against isolated native sockets."""
import asyncio,json,os,sys,tempfile,unittest
from pathlib import Path
import websockets
ROOT=Path(__file__).parent

class TransportLimits(unittest.IsolatedAsyncioTestCase):
 async def test_subscription_cap_prioritizes_requested_order(self):
  requests=[]
  async def handler(ws):
   try:
    async for raw in ws:requests.append(json.loads(raw))
   except websockets.ConnectionClosed:pass
  async with websockets.serve(handler,'127.0.0.1',0) as server:
   port=server.sockets[0].getsockname()[1]
   proc=await asyncio.create_subprocess_exec(sys.executable,str(ROOT/'bridge.py'),env=dict(os.environ,HEART_V2_SOCKET=f'ws://127.0.0.1:{port}'),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
   async def send(**m):proc.stdin.write((json.dumps(m)+'\n').encode());await proc.stdin.drain()
   try:
    await asyncio.wait_for(proc.stdout.readline(),3)
    ids=list(range(300,0,-1))
    await send(cmd='bind',epoch='test',ids=ids,numeric=[])
    await send(cmd='observe',epoch='test',ids=ids)
    reply=json.loads(await asyncio.wait_for(proc.stdout.readline(),3))
    self.assertIn('limited to 256',reply['error'])
    await asyncio.sleep(.3)
    subscribed={int(m['parameter'].split('/')[-1]) for m in requests if m['action']=='subscribe'}
    self.assertEqual(subscribed,set(ids[:256]))
    await send(cmd='observe',epoch='test',ids=[1])
    await asyncio.sleep(.3)
    for m in requests:
     self.assertIn(m['action'],('subscribe','unsubscribe'))
    removed={int(m['parameter'].split('/')[-1]) for m in requests if m['action']=='unsubscribe'}
    self.assertEqual(removed,subscribed)
    self.assertEqual(requests[-1]['parameter'],'/parameter/by-id/1')
   finally:proc.terminate();await proc.wait()

 async def test_failed_connections_stop_until_deliberate_retry(self):
  connections=[]
  async def handler(ws):connections.append(ws);await ws.close()
  async with websockets.serve(handler,'127.0.0.1',0) as server, asyncio.timeout(5):
   port=server.sockets[0].getsockname()[1]
   with tempfile.TemporaryDirectory(prefix='heart-reconnect-limit-') as directory:
    (Path(directory)/'phase_frames.py').write_text((ROOT/'phase_frames.py').read_text())
    script=Path(directory)/'bridge.py';script.write_text((ROOT/'bridge.py').read_text().replace('RECONNECT_DELAYS=(5,15)','RECONNECT_DELAYS=(.01,.01)'))
    proc=await asyncio.create_subprocess_exec(sys.executable,str(script),env=dict(os.environ,HEART_V2_SOCKET=f'ws://127.0.0.1:{port}'),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
    async def paused():
     while True:
      m=json.loads(await proc.stdout.readline())
      if 'paused after 3 failures' in m.get('error',''):return
    try:
     await paused();self.assertEqual(len(connections),3)
     await asyncio.sleep(.15);self.assertEqual(len(connections),3)
     proc.stdin.write(b'{"cmd":"reconnect"}\n');await proc.stdin.drain()
     await paused();self.assertEqual(len(connections),6)
     await asyncio.sleep(.15);self.assertEqual(len(connections),6)
    finally:proc.terminate();await proc.wait()
