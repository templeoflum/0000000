#!/usr/bin/env python3
"""preview.py — Arena output → Syphon → MJPEG for the surface's 'out' tab.
Runs on its own venv (python3.12: syphon-python has no 3.14 wheel). Serves:
  http://localhost:8767/mjpeg   multipart stream (the surface's <img>)
  http://localhost:8767/jpg     single frame
Waits politely if no Syphon server exists (Arena → Output → Syphon off)."""
import time, threading, io
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import numpy as np
from PIL import Image
import syphon
from syphon.utils.numpy import copy_mtl_texture_to_image

FPS = 24          # capture + stream rate (Arena renders faster; we sample)
QUALITY = 78
MAXW = 960        # downscale for the surface — it's a preview, not the output
FLIP = False      # set True if the image shows upside down

viewers = 0
last_request = 0.0

latest = {"jpg": None, "t": 0.0}

def grab():
    client = None
    last_frame = time.time()
    next_t = time.perf_counter()
    while True:
        if viewers == 0 and time.time()-last_request>2:
            time.sleep(0.25); next_t=time.perf_counter(); continue
        try:
            if client is not None and time.time() - last_frame > 5:
                print("[preview] no frames for 5s — reconnecting to Syphon", flush=True)
                try: client.stop()
                except Exception: pass
                client = None
            if client is None:
                last_frame = time.time()
                servers = syphon.SyphonServerDirectory().servers
                if not servers:
                    print("[preview] no Syphon server — enable Arena → Output → Syphon", flush=True)
                    time.sleep(2); continue
                desc = next((s for s in servers if "Arena" in s.app_name), servers[0])
                client = syphon.SyphonMetalClient(desc)
                print(f"[preview] connected: {desc.app_name} / {desc.name}", flush=True)
            if client.has_new_frame:
                a = copy_mtl_texture_to_image(client.new_frame_image)   # (H,W,4) RGBA uint8
                if FLIP: a = np.flipud(a)
                k = max(1, (a.shape[1] + MAXW - 1) // MAXW)             # filtered downscale (C box filter):
                img = Image.fromarray(np.ascontiguousarray(a[..., :3])) # fine detail survives, cheap
                if k > 1: img = img.reduce(k)
                buf = io.BytesIO(); img.save(buf, "JPEG", quality=QUALITY)
                latest["jpg"] = buf.getvalue(); latest["t"] = last_frame = time.time()
            next_t += 1.0 / FPS                                 # absolute pacing: work doesn't stack on sleep
            d = next_t - time.perf_counter()
            if d > 0: time.sleep(d)
            else: next_t = time.perf_counter()
        except Exception as e:
            print("[preview] grab error:", e, flush=True)
            client = None; time.sleep(2)

class H(BaseHTTPRequestHandler):
    def do_GET(s):
        global viewers,last_request
        last_request=time.time()
        if s.path.startswith("/jpg"):
            j = latest["jpg"]
            if not j: s.send_response(503); s.end_headers(); return
            s.send_response(200); s.send_header("Content-Type", "image/jpeg")
            s.send_header("Content-Length", str(len(j))); s.end_headers(); s.wfile.write(j)
        elif s.path.startswith("/mjpeg"):
            s.send_response(200)
            s.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame"); s.end_headers()
            lt = 0.0; viewers += 1
            try:
                while True:
                    if latest["t"] > lt and latest["jpg"]:
                        lt = latest["t"]; j = latest["jpg"]
                        s.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                                      + str(len(j)).encode() + b"\r\n\r\n" + j + b"\r\n")
                        s.wfile.flush()
                    time.sleep(1.0 / 60.0)
            except (BrokenPipeError, ConnectionResetError): pass
            finally: viewers -= 1
        else:
            s.send_response(404); s.end_headers()
    def log_message(s, *a): pass

class TS(ThreadingMixIn, HTTPServer): daemon_threads = True

if __name__ == "__main__":
    # Syphon/PyObjC discovery wants the main thread — HTTP goes to the side thread instead
    srv = TS(("127.0.0.1", 8767), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("[preview] serving http://localhost:8767/mjpeg", flush=True)
    grab()
