"""Continuous output without native WebSocket composition broadcasts."""
import asyncio,json,os,sys,time,threading,unittest,socket,struct
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler

class HTTPOutputTests(unittest.IsolatedAsyncioTestCase):
 async def test_phase_output_preserves_program_and_rejects_inflight_stale_destination(self):
  writes=[];blocked=threading.Event();release=threading.Event();block=False
  clip=dict(id=30,connected={'value':'Connected'},video=dict(description='Field',sourceparams={'W':dict(id=1,min=-1,max=1,**{'in':.2,'out':.3})}))
  class Handler(BaseHTTPRequestHandler):
   def do_GET(self):
    if '/clips/' in self.path:
     if block:blocked.set();release.wait(2)
     data=clip
    else:data=dict(id=1,value=.25)
    self.send_response(200);self.end_headers();self.wfile.write(json.dumps(data).encode())
   def do_DELETE(self):writes.append('DELETE');self.send_response(204);self.end_headers()
   def do_PUT(self):writes.append('PUT');self.send_response(204);self.end_headers()
   def log_message(self,*args):pass
  http=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
  osc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);osc.bind(('127.0.0.1',0));osc.setblocking(False)
  env=dict(os.environ,HEART_V2_ARENA=f'http://127.0.0.1:{http.server_port}/api/v1',HEART_V2_TRANSPORT='http',HEART_V2_OSC_PORT=str(osc.getsockname()[1]))
  env.pop('HEART_V2_SOCKET',None)
  proc=await asyncio.create_subprocess_exec(sys.executable,str(Path(__file__).with_name('bridge.py')),env=env,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
  reports=[]
  async def read():
   while line:=await proc.stdout.readline():reports.append(json.loads(line))
  reader=asyncio.create_task(read())
  async def send(**m):proc.stdin.write((json.dumps(m)+'\n').encode());await proc.stdin.drain()
  async def until(predicate):
   async with asyncio.timeout(3):
    while not predicate():await asyncio.sleep(.005)
  async def receive():return await asyncio.wait_for(asyncio.get_running_loop().sock_recv(osc,65536),1)
  route=dict(layer=1,clip=1,clip_id=30,description='Field',source='field',name='W',min=-1,max=1)
  try:
   await send(cmd='bind',epoch='a',ids=[1],numeric=[1],phases={1:route});await until(lambda:any(m.get('connected') for m in reports));await send(cmd='arm',on=True)
   await send(cmd='values',epoch='a',values=[[1,{'phase':.4}]]);packet=await receive();self.assertIn(b'/phase',packet);self.assertAlmostEqual(struct.unpack('>f',packet[-4:])[0],.4)
   block=True;await send(cmd='values',epoch='a',values=[[1,{'phase':.5}]]);await until(blocked.is_set)
   await send(cmd='values',epoch='a',values=[[1,{'phase':.9}]]);await asyncio.sleep(.02);release.set();packet=await receive();self.assertAlmostEqual(struct.unpack('>f',packet[-4:])[0],.9)
   release.clear();blocked.clear();await send(cmd='values',epoch='a',values=[[1,{'phase':.7}]]);await until(blocked.is_set)
   await send(cmd='arm',on=False);await asyncio.sleep(.02);release.set();await asyncio.sleep(.08)
   with self.assertRaises(BlockingIOError):osc.recv(65536)
   block=False;clip['id']=31;await send(cmd='arm',on=True);await send(cmd='values',epoch='a',values=[[1,{'phase':.5}]]);await until(lambda:any(m.get('phase_stopped') for m in reports))
   with self.assertRaises(BlockingIOError):osc.recv(65536)
   # Queued frames can arrive after a failed identity check. They must not
   # keep an unsendable phase pending and starve commands/disarm forever.
   for _ in range(5):await send(cmd='values',epoch='a',values=[[1,{'phase':.6}]])
   await send(cmd='animation_get',id=1,rpc=91);await until(lambda:any(m.get('rpc')==91 for m in reports))
   self.assertEqual(writes,[])
   # A fresh binding must be able to deliver again after the old one stops.
   route=dict(route,clip_id=31);await send(cmd='bind',epoch='a',ids=[1],numeric=[1],phases={1:route},keep=[])
   await send(cmd='values',epoch='a',values=[[1,{'phase':.8}]]);packet=await receive();self.assertAlmostEqual(struct.unpack('>f',packet[-4:])[0],.8)
  finally:
   release.set();proc.terminate();await proc.wait();reader.cancel();await asyncio.gather(reader,return_exceptions=True);osc.close();await asyncio.to_thread(http.shutdown);http.server_close()

 async def test_claim_latest_values_readback_and_stale_disarm(self):
  writes=[];claims=[];values={1:.1,2:False,3:.3}
  blocked=threading.Event();release=threading.Event()
  class Handler(BaseHTTPRequestHandler):
   def do_GET(self):
    pid=int(self.path.rsplit('/',1)[1]);body=json.dumps({'id':pid,'value':values[pid]}).encode()
    self.send_response(200);self.end_headers();self.wfile.write(body)
   def do_DELETE(self):
    pid=int(self.path.split('/')[-2]);claims.append(pid)
    if pid==3:blocked.set();release.wait(2)
    self.send_response(204);self.end_headers()
   def do_PUT(self):
    pid=int(self.path.rsplit('/',1)[1]);value=json.loads(self.rfile.read(int(self.headers['Content-Length'])))['value']
    values[pid]=value;writes.append((pid,value,time.perf_counter()))
    self.send_response(204);self.end_headers()
   def log_message(self,*args):pass
  http=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=http.serve_forever,daemon=True).start()
  env=dict(os.environ,HEART_V2_ARENA=f'http://127.0.0.1:{http.server_port}/api/v1',HEART_V2_TRANSPORT='http')
  env.pop('HEART_V2_SOCKET',None)
  proc=await asyncio.create_subprocess_exec(sys.executable,str(Path(__file__).with_name('bridge.py')),env=env,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
  reports=[]
  async def read():
   while line:=await proc.stdout.readline():reports.append(json.loads(line))
  reader=asyncio.create_task(read())
  async def send(**m):proc.stdin.write((json.dumps(m)+'\n').encode());await proc.stdin.drain()
  async def until(predicate):
   async with asyncio.timeout(3):
    while not predicate():await asyncio.sleep(.005)
  try:
   await send(cmd='bind',epoch='a',ids=[1,2,3],numeric=[1,3])
   await until(lambda:any(m.get('connected') for m in reports))
   await send(cmd='observe',epoch='a',ids=[2,1])
   await until(lambda:any(m.get('native_values') for m in reports))
   self.assertEqual(writes,[])
   await send(cmd='arm',on=True)
   for i in range(20):
    await send(cmd='values',epoch='a',values=[[1,i/19]])
    await asyncio.sleep(.01)
   await send(cmd='values',epoch='a',values=[[2,True]])
   await until(lambda:values[1]==1 and values[2] is True)
   self.assertEqual(claims,[1]);self.assertGreater(len(writes),10)
   await until(lambda:any([2,True] in m.get('native_values',[]) for m in reports))
   # A slow claim must consume the most recent value, not a queued sweep.
   await send(cmd='values',epoch='a',values=[[3,.4]])
   await until(blocked.is_set)
   for i in range(10):await send(cmd='values',epoch='a',values=[[3,i/10]])
   await asyncio.sleep(.03);release.set()
   await until(lambda:values[3]==.9)
   self.assertEqual([v for pid,v,t in writes if pid==3],[.9])
   # Changed identity and disarm cancel work waiting on a native claim.
   blocked.clear();release.clear()
   await send(cmd='bind',epoch='b',ids=[1,2,3],numeric=[1,3],keep=[1,2])
   await send(cmd='values',epoch='b',values=[[3,.6]])
   await until(blocked.is_set)
   await send(cmd='bind',epoch='c',ids=[1,2],numeric=[1],keep=[1,2])
   await send(cmd='arm',on=False)
   await send(cmd='values',epoch='b',values=[[1,999]])
   await asyncio.sleep(.03);count=len(writes);release.set();await asyncio.sleep(.1)
   self.assertEqual(len(writes),count)
   await send(cmd='arm',on=True)
   await send(cmd='values',epoch='a',values=[[1,888]])
   await asyncio.sleep(.05);self.assertEqual(len(writes),count)
   await send(cmd='values',epoch='c',values=[[2,False]])
   await until(lambda:values[2] is False)
   self.assertFalse(any(m.get('error') for m in reports),reports)
  finally:
   release.set();proc.terminate();await proc.wait();reader.cancel()
   await asyncio.gather(reader,return_exceptions=True)
   await asyncio.to_thread(http.shutdown);http.server_close()
