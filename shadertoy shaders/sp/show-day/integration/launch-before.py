"""Start missing Heart services, then show the native monitor. Never restart a performance."""
from pathlib import Path
import fcntl, os, socket, subprocess, sys, time, urllib.request
ROOT=Path(__file__).resolve().parent
PYTHON=ROOT/'engine/.venv/bin/python'

def listening(port):
    try:
        with socket.create_connection(('127.0.0.1',port),timeout=.3):return True
    except OSError:return False

def arena_ready():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8080/api/v1/composition',timeout=3) as r:return r.status==200
    except Exception:return False

def start(script,folder,log):
    with open(log,'a') as out:
        return subprocess.Popen([str(PYTHON),*script],cwd=folder,stdout=out,stderr=out,start_new_session=True)

def wait_for(check,seconds,child=None):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if check():return True
        if child and child.poll() is not None:return False
        time.sleep(.25)
    return False

def main():
    # Serializes double-clicks without killing or duplicating existing services.
    with open(ROOT/'engine/.launch.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if not (listening(8765) and listening(8766)):
            if listening(8765) or listening(8766):
                raise RuntimeError('Heart is still starting or a control port is occupied. Wait a moment and try again; the running session was left intact.')
            if not arena_ready():
                subprocess.run(['/usr/bin/open','-gj','-b','com.resolume.arena'],check=True)
                if not wait_for(arena_ready,25):
                    raise RuntimeError('Resolume is not ready. Open your composition and enable its Web Server on port 8080, then open Heart again.')
            child=start(['heart.py','--all'],ROOT/'engine',ROOT/'engine/heart.log')
            if not wait_for(lambda:listening(8765) and listening(8766),12,child):
                raise RuntimeError('The Heart engine could not start. See sp/engine/heart.log.')
        if not listening(8770):
            child=start(['mt_probe.py'],ROOT/'lab/trackpad',ROOT/'lab/trackpad/probe.log')
            if not wait_for(lambda:listening(8770),5,child):
                print('Trackpad input unavailable; mouse controls remain available.',file=sys.stderr)
        app=ROOT/'monitor/Heart.app'
        if not (app/'Contents/MacOS/Heart').exists():
            subprocess.run(['/bin/zsh',str(ROOT/'monitor/build.sh')],check=True)
        subprocess.run(['/usr/bin/open',str(app)],check=True)
        print('Heart ready. Existing motion and Resolume session preserved.')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(str(exc),file=sys.stderr);sys.exit(1)
