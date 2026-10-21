"""Native subscriptions are read-only, scoped and fenced when parameters change."""
import asyncio,json,os,sys,unittest
from pathlib import Path
import websockets

class ObservationTests(unittest.IsolatedAsyncioTestCase):
 async def test_disarmed_readback_scope_and_rebinding(self):
  requests=[];native=[]
  async def handler(ws):
   native.append(ws)
   await ws.send(b'{"catalog":'+b' '*1000000+b'}')
   async for raw in ws:
    m=json.loads(raw);requests.append(m);pid=int(m['parameter'].split('/')[-1])
    if m['action']=='subscribe':await ws.send(json.dumps(dict(id=pid,type='parameter_subscribed',value=.3)))
  async with websockets.serve(handler,'127.0.0.1',0) as server:
   port=server.sockets[0].getsockname()[1]
   proc=await asyncio.create_subprocess_exec(sys.executable,str(Path(__file__).with_name('bridge.py')),env=dict(os.environ,HEART_V2_SOCKET=f'ws://127.0.0.1:{port}'),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
   async def send(**m):proc.stdin.write((json.dumps(m)+'\n').encode());await proc.stdin.drain()
   async def receive(predicate):
    async def loop():
     while True:
      m=json.loads(await proc.stdout.readline())
      if predicate(m):return m
    return await asyncio.wait_for(loop(),4)
   try:
    await receive(lambda m:m.get('connected'))
    await send(cmd='bind',epoch='a',ids=[1,2],numeric=[1,2]);await send(cmd='observe',epoch='a',ids=[1,99])
    first=await receive(lambda m:m.get('native_values'));self.assertEqual(first['native_values'],[[1,.3]])
    await native[0].send(json.dumps(dict(id=1,type='parameter_update',value=.8)))
    self.assertEqual((await receive(lambda m:m.get('native_values')))['native_values'],[[1,.8]])
    await send(cmd='bind',epoch='b',ids=[1,2],numeric=[1,2],keep=[])
    await send(cmd='observe',epoch='b',ids=[2]);next_values=await receive(lambda m:m.get('native_epoch')=='b')
    self.assertEqual(next_values['native_values'],[[2,.3]])
    self.assertTrue(any(m['action']=='unsubscribe' and m['parameter'].endswith('/1') for m in requests))
    self.assertTrue(all(m['action'] in ('subscribe','unsubscribe') for m in requests))
    self.assertFalse(any(m['parameter'].endswith('/99') for m in requests))
   finally:
    proc.terminate();await proc.wait()
