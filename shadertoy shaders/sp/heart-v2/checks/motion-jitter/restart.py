"""Restart Heart with saved preferences; leave the standalone surface open."""
import asyncio,json,os,signal,subprocess,sys,time
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
async def state(ws,predicate):
 async with asyncio.timeout(30):
  while True:
   m=json.loads(await ws.recv())
   if m['type']=='state' and predicate(m):return m
async def main():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
  before=await state(ws,lambda s:s['connected']);(OUT/'restart-before.json').write_text(json.dumps(before))
  await ws.send(json.dumps(dict(cmd='arm',on=False)));await state(ws,lambda s:not s['armed'])
 rows=[r.split(None,2) for r in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines()]
 servers=[int(pid) for pid,ppid,cmd in rows if cmd.endswith(str(ROOT/'server.py'))];assert len(servers)==1,servers
 children=[int(pid) for pid,ppid,cmd in rows if int(ppid)==servers[0] and any(cmd.endswith(str(ROOT/name)) for name in ('bridge.py','discovery.py','scan.py'))]
 assert any(cmd==str(ROOT/'Heart Surface.app/Contents/MacOS/HeartSurface') for pid,ppid,cmd in rows)
 os.kill(servers[0],signal.SIGTERM)
 for _ in range(40):
  running=subprocess.run(['ps','-p',str(servers[0]),'-o','stat='],capture_output=True,text=True).stdout.strip()
  if not running or running.startswith('Z'):break
  await asyncio.sleep(.1)
 else:raise RuntimeError('Old Heart did not finish saving; leaving it alone')
 for pid in children:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 env=dict(os.environ)
 if '--trace' in sys.argv:env['HEART_V2_TRACE_DIR']=str(OUT)
 else:env.pop('HEART_V2_TRACE_DIR',None)
 with (OUT/'server.log').open('a') as log:
  process=subprocess.Popen([str(ROOT.parent/'engine/.venv/bin/python'),str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=log,stderr=log,start_new_session=True)
 (OUT/'installed-pid.txt').write_text(str(process.pid));await asyncio.sleep(1)
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
  await state(ws,lambda s:s['connected'])
  await ws.send(json.dumps(dict(cmd='select',target=before['selected'])))
  if before['armed']:
   for n in range(6):
    await ws.send(json.dumps(dict(cmd='arm',on=True)))
    try:
     async with asyncio.timeout(3):await state(ws,lambda s:s['armed'])
     break
    except TimeoutError:
     if n==5:raise
   if before['hold']:await ws.send(json.dumps(dict(cmd='hold',on=True)))
  after=await state(ws,lambda s:s['armed']==before['armed']);print(json.dumps(dict(armed=after['armed'],error=after['error'],bpm=after['bpm'],pid=process.pid)))
asyncio.run(main())
