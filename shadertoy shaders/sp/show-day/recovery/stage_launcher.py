"""Stage the launcher-only proposal; never modifies the shared launcher."""
from pathlib import Path
import difflib
HERE=Path(__file__).resolve().parent
source=HERE.parents[1]/'launch.py'
old=source.read_text()
new=old.replace('import fcntl, os, socket, subprocess, sys, time, urllib.request','import fcntl, json, os, socket, subprocess, sys, time, urllib.request\nfrom websockets.sync.client import connect')
anchor='\ndef arena_ready():'
helper='''
def heart_ready():
    """Recognize both local Heart endpoints without sending control commands.

    This is an accidental port-collision check, not authentication or Arena
    readiness. A held/disconnected Heart is still the expected service.
    """
    try:
        expected=(ROOT/'engine/status.html').read_bytes()
        url='http://127.0.0.1:8765/status.html'
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url,timeout=1) as response:
            if response.status!=200 or response.geturl()!=url:return False
            if response.read(len(expected)+1)!=expected:return False
        with connect('ws://127.0.0.1:8766/',open_timeout=1,
                     close_timeout=.2,max_size=4*1024*1024,proxy=None) as ws:
            state=json.loads(ws.recv(timeout=1))
        return (isinstance(state,dict)
                and isinstance(state.get('arena_connected'),bool)
                and isinstance(state.get('hold'),bool)
                and all(isinstance(state.get(k),list) for k in ('clips','layers','fx'))
                and isinstance(state.get('patch_operation'),dict)
                and isinstance(state.get('delivery'),dict))
    except Exception:
        return False
'''
assert old.count(anchor)==1
new=new.replace(anchor,'\n'+helper+anchor)
anchor="        if not listening(8770):"
assert old.count(anchor)==1
new=new.replace(anchor,"        if not wait_for(heart_ready,3):\n            raise RuntimeError('Heart control ports are occupied but the expected Heart services did not respond. The session was left intact; check sp/engine/heart.log and the port owners before retrying.')\n"+anchor)
(HERE/'launch.proposed.py').write_text(new)
(HERE/'launcher-identity.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/sp/launch.py',tofile='b/sp/launch.py')))
