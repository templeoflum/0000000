"""Real subprocess/socket pilot against fake Arena; no live composition writes."""
import asyncio,json,os,sys,time,threading,unittest
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import websockets
class BridgeTests(unittest.IsolatedAsyncioTestCase):
 async def test_values_claim_disarm_and_stale_epoch(self):
  claims=[];received=[];native_writes=[]
  class H(BaseHTTPRequestHandler):
   def do_DELETE(self):
    claims.append(self.path)
    if '/3/' in self.path:time.sleep(.15)
    self.send_response(200);self.end_headers();self.wfile.write(b'{}')
   def do_GET(self):
    value={'phase_source':'timeline','parameters':{}} if self.path.endswith('phase-source') else {'id':1,'min':0,'max':1,'value':.5}
    self.send_response(200);self.end_headers();self.wfile.write(json.dumps(value).encode())
   def do_PUT(self):
    native_writes.append(json.loads(self.rfile.read(int(self.headers.get('Content-Length',0)))))
    self.send_response(204);self.end_headers()
   def log_message(self,*args):pass
  http=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=http.serve_forever,daemon=True).start()
  async def handler(ws):
   await ws.send(b'{"name":'+b' '*1000000+b'}')
   try:
    async for raw in ws:received.append(json.loads(raw))
   except websockets.ConnectionClosed:pass
  async with websockets.serve(handler,'127.0.0.1',0,compression=None) as server:
   port=server.sockets[0].getsockname()[1];env=dict(os.environ,HEART_V2_ARENA=f'http://127.0.0.1:{http.server_port}/api/v1',HEART_V2_SOCKET=f'ws://127.0.0.1:{port}')
   proc=await asyncio.create_subprocess_exec(sys.executable,str(Path(__file__).with_name('bridge.py')),env=env,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
   async def send(m):proc.stdin.write((json.dumps(m)+'\n').encode());await proc.stdin.drain()
   try:
    await asyncio.wait_for(proc.stdout.readline(),3)
    await send(dict(cmd='bind',epoch='a',ids=[1,2],numeric=[1]));await send(dict(cmd='arm',on=True))
    for i in range(15):await send(dict(cmd='values',epoch='a',values=[[1,i/14]]));await asyncio.sleep(.02)
    await send(dict(cmd='values',epoch='a',values=[[2,True]]));await asyncio.sleep(.1)
    self.assertEqual(received[-1]['value'],True);self.assertEqual(len(claims),1);self.assertEqual(received[-2]['value'],1.)
    await send(dict(cmd='animation_set',id=1,rpc=5,source='timeline'))
    while True:
     reply=json.loads(await asyncio.wait_for(proc.stdout.readline(),3))
     if reply.get('rpc')==5:break
    self.assertIn('data',reply);self.assertEqual(native_writes,[{'phase_source':'timeline'}])
    count=len(received);await asyncio.sleep(.08);self.assertEqual(len(received),count)
    await send(dict(cmd='values',epoch='a',values=[[1,.3]]));await asyncio.sleep(.1)
    self.assertEqual(len(claims),2);self.assertEqual(received[-1]['value'],.3)
    await send(dict(cmd='bind',epoch='b',ids=[1],numeric=[1],keep=[1]));n=len(received);await send(dict(cmd='values',epoch='a',values=[[1,999]]));await asyncio.sleep(.06);self.assertEqual(len(received),n)
    await send(dict(cmd='values',epoch='b',values=[[1,.4]]));await asyncio.sleep(.08);self.assertEqual(received[-1]['value'],.4);self.assertEqual(len(claims),2)
    await send(dict(cmd='bind',epoch='c',ids=[1,3],numeric=[1,3],keep=[1]));await send(dict(cmd='values',epoch='c',values=[[3,.9]]))
    for _ in range(200):
     if any('/3/' in path for path in claims):break
     await asyncio.sleep(.005)
    self.assertTrue(any('/3/' in path for path in claims))
    await send(dict(cmd='bind',epoch='d',ids=[1,4],numeric=[1,4],keep=[1]));await send(dict(cmd='values',epoch='d',values=[[1,.5]]));await asyncio.sleep(.25)
    self.assertFalse(any(m['parameter'].endswith('/3') for m in received));self.assertEqual(received[-1]['value'],.5);self.assertEqual(sum('/1/' in p for p in claims),2)
    await send(dict(cmd='claim',id=1,rpc=6))
    while True:
     reply=json.loads(await asyncio.wait_for(proc.stdout.readline(),3))
     if reply.get('rpc')==6:break
    self.assertEqual(reply['data'],{'ok':True});self.assertEqual(sum('/1/' in p for p in claims),3)
    await send(dict(cmd='values',epoch='d',values=[[1,.7]]));await asyncio.sleep(.08)
    self.assertEqual(received[-1]['value'],.7);self.assertEqual(sum('/1/' in p for p in claims),3,'A hit claim is reused for its decay; no extra native animation reads/claims')
    n=len(received)
    await send(dict(cmd='arm',on=False));await send(dict(cmd='values',epoch='d',values=[[1,888]]));await asyncio.sleep(.06);self.assertEqual(len(received),n)
   finally:proc.terminate();await proc.wait()
  http.shutdown();http.server_close()
