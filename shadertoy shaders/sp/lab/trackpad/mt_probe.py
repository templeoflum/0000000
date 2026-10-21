#!/usr/bin/env python3
"""mt_probe.py — raw multitouch from the Mac trackpad via the private MultitouchSupport framework.
Streams every contact frame as JSON over ws://localhost:8770 and serves lab.html on http://localhost:8769.
Isolated R&D: no Resolume, no engine. Just what the hardware says."""
import ctypes, ctypes.util, json, time, threading, asyncio, os, sys, collections
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler

MT=ctypes.CDLL('/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport')
CF=ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

class mtPoint(ctypes.Structure): _fields_=[("x",ctypes.c_float),("y",ctypes.c_float)]
class mtReadout(ctypes.Structure): _fields_=[("pos",mtPoint),("vel",mtPoint)]
class Finger(ctypes.Structure):
    _fields_=[("frame",ctypes.c_int),("timestamp",ctypes.c_double),("identifier",ctypes.c_int),("state",ctypes.c_int),
              ("foo3",ctypes.c_int),("foo4",ctypes.c_int),("normalized",mtReadout),("size",ctypes.c_float),("zero1",ctypes.c_int),
              ("angle",ctypes.c_float),("majorAxis",ctypes.c_float),("minorAxis",ctypes.c_float),("mm",mtReadout),
              ("zero2",ctypes.c_int*2),("zdensity",ctypes.c_float)]
STATES={0:"none",1:"start",2:"hover",3:"make",4:"touch",5:"break",6:"linger",7:"leave"}
CB=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.POINTER(Finger),ctypes.c_int,ctypes.c_double,ctypes.c_int)

MT.MTDeviceCreateList.restype=ctypes.c_void_p
MT.MTRegisterContactFrameCallback.argtypes=[ctypes.c_void_p,CB]
MT.MTDeviceStart.argtypes=[ctypes.c_void_p,ctypes.c_int]
CF.CFArrayGetCount.argtypes=[ctypes.c_void_p]; CF.CFArrayGetCount.restype=ctypes.c_long
CF.CFArrayGetValueAtIndex.argtypes=[ctypes.c_void_p,ctypes.c_long]; CF.CFArrayGetValueAtIndex.restype=ctypes.c_void_p

LATEST={"t":0,"frame":0,"fingers":[],"hz":0}
_frames=collections.deque(maxlen=120); LOCK=threading.Lock()
def on_frame(dev,data,n,ts,frame):
    fs=[]
    for i in range(n):
        f=data[i]
        fs.append({"id":f.identifier,"state":STATES.get(f.state,f.state),"x":f.normalized.pos.x,"y":f.normalized.pos.y,
                   "vx":f.normalized.vel.x,"vy":f.normalized.vel.y,"size":f.size,"angle":f.angle,"major":f.majorAxis,"minor":f.minorAxis,
                   "mmx":f.mm.pos.x,"mmy":f.mm.pos.y,"zd":f.zdensity})
    now=time.time(); _frames.append(now)
    hz=len(_frames)/(now-_frames[0]) if len(_frames)>1 and now>_frames[0] else 0
    with LOCK: LATEST.update({"t":ts,"frame":frame,"fingers":fs,"hz":round(hz,1),"n":n})
    return 0
_cb=CB(on_frame)

def start_devices():
    lst=MT.MTDeviceCreateList(); n=CF.CFArrayGetCount(lst); print(f"[mt] devices: {n}",flush=True)
    for i in range(n):
        dev=CF.CFArrayGetValueAtIndex(lst,i); MT.MTRegisterContactFrameCallback(dev,_cb); MT.MTDeviceStart(dev,0); print(f"[mt] started device {i}",flush=True)
    return n

HERE=os.path.dirname(os.path.abspath(__file__))
class H(SimpleHTTPRequestHandler):
    def do_GET(s):
        f="lanes.html" if s.path.startswith("/lanes") else ("pads.html" if s.path.startswith("/pads") else "lab.html")
        s.send_response(200); s.send_header("Content-Type","text/html"); s.end_headers(); s.wfile.write(open(os.path.join(HERE,f)).read().encode())
    def log_message(s,*a): pass
def serve():
    threading.Thread(target=lambda: HTTPServer(("127.0.0.1",8769),H).serve_forever(),daemon=True).start()
    async def run():
        clients=set()
        async def handler(ws):
            clients.add(ws)
            try:
                async for _ in ws: pass
            finally: clients.discard(ws)
        async with websockets.serve(handler,"127.0.0.1",8770):
            last=-1
            while True:
                with LOCK: snap=dict(LATEST)
                if snap["frame"]!=last or True:
                    last=snap["frame"]; m=json.dumps(snap)
                    for c in list(clients):
                        try: await c.send(m)
                        except Exception: clients.discard(c)
                await asyncio.sleep(1/120)
    asyncio.new_event_loop().run_until_complete(run())

if __name__=="__main__":
    n=start_devices()
    if n==0: print("[mt] no multitouch devices found",flush=True); sys.exit(1)
    threading.Thread(target=serve,daemon=True).start()
    print("[mt] lab: http://localhost:8769",flush=True)
    # the framework delivers callbacks through the main thread's CFRunLoop — pump it here
    CF.CFRunLoopRunInMode.argtypes=[ctypes.c_void_p,ctypes.c_double,ctypes.c_bool]; CF.CFRunLoopRunInMode.restype=ctypes.c_int
    mode=ctypes.c_void_p.in_dll(CF,"kCFRunLoopDefaultMode"); t=time.time()
    while True:
        CF.CFRunLoopRunInMode(mode,0.05,True)
        if time.time()-t>3:
            t=time.time()
            with LOCK: print(f"[mt] hz={LATEST['hz']} fingers={LATEST.get('n',0)}",flush=True)
