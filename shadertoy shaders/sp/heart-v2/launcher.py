"""Idempotent desktop launcher for the separate v2 pilot."""
import subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='http://localhost:8875/'
def running():
 try:
  with urllib.request.urlopen(URL,timeout=1) as r:return b'<title>Heart v2</title>' in r.read(2048)
 except OSError:return False
if not running():
 with open(ROOT/'server.log','a') as log:
  p=subprocess.Popen([str(ROOT.parent/'engine/.venv/bin/python'),str(ROOT/'server.py')],cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
 for _ in range(40):
  if running():break
  if p.poll() is not None:raise SystemExit('Heart v2 could not start. See server.log.')
  time.sleep(.15)
if running():subprocess.run(['open',str(ROOT/'Heart Surface.app')],check=True)
else:subprocess.run(['open',str(ROOT/'server.log')])
