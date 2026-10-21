"""Upgrade the heart only; leave Arena and the trackpad probe running."""
import asyncio,json,os,signal,subprocess,time
from pathlib import Path
import websockets
root=Path(__file__).resolve().parents[1]
async def main():
 async with websockets.connect('ws://127.0.0.1:8766') as ws: state=json.loads(await ws.recv())
 path=root/'audit/20260907-070411/restart-state.json';path.write_text(json.dumps(state,indent=2))
 rows=subprocess.check_output(['ps','-axo','pid,args'],text=True).splitlines()
 pids=[int(r.split()[0]) for r in rows if r.rstrip().endswith('Python heart.py --all')]
 if len(pids)!=1:raise RuntimeError(f'Expected exactly one original heart, found {pids}')
 os.kill(pids[0],signal.SIGTERM);time.sleep(1)
 env=dict(os.environ,SP_RESUME_STATUS=str(path))
 log=open(root/'engine/heart.log','a')
 child=subprocess.Popen([str(root/'engine/.venv/bin/python'),'heart.py','--all'],cwd=root/'engine',env=env,stdout=log,stderr=log,start_new_session=True)
 print('new heart pid',child.pid)
 for i in range(20):
  await asyncio.sleep(.5)
  if child.poll() is not None:raise RuntimeError('New heart exited; see heart.log')
  try:
   async with websockets.connect('ws://127.0.0.1:8766') as ws:
    fresh=json.loads(await ws.recv())
    if fresh.get('arena_connected'):
     print('connected clips',len(fresh['clips']),'delivery',fresh.get('delivery'));return
  except OSError:pass
 raise RuntimeError('New heart did not become ready')
asyncio.run(main())
