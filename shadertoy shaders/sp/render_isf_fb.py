#!/usr/bin/env python3
"""render_isf_fb.py — offscreen GPU render of a MULTI-PASS ISF shader with PERSISTENT buffers over N frames.
For feedback / delay atoms: the input can move frame to frame (--move dx,dy px/frame) so trails and echoes show.
  qa/.venv/bin/python render_isf_fb.py "SP Chain Map.fs" --input frame.png --frames 90 -o out.png [--strip 6]
  --set name=value (ISF inputs), -w/-H (frame size), --move dx,dy, --strip K saves a filmstrip of K evenly spaced frames.
PASSES: each TARGET gets its own FBO (size from WIDTH/HEIGHT expressions with $WIDTH/$HEIGHT, default frame size);
PERSISTENT targets keep their contents between frames; the last pass renders to the output. PASSINDEX, RENDERSIZE,
TIME, FRAMEINDEX are provided; IMG_* macros resolve the sampler and its size per image."""
import argparse, json, re, sys, time, statistics
import numpy as np, moderngl
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("fs"); ap.add_argument("-o", "--out", required=True)
ap.add_argument("-w", type=int, default=1920); ap.add_argument("-H", type=int, default=1080)
ap.add_argument("--set", action="append", default=[]); ap.add_argument("--input", default=None)
ap.add_argument("--frames", type=int, default=60); ap.add_argument("--move", default="0,0")
ap.add_argument("--strip", type=int, default=0); ap.add_argument("--scale", type=int, default=1); ap.add_argument("--fps", type=float, default=60.0)
ap.add_argument("--benchmark", help="write synchronized render timings to JSON (excludes image readback)")
ap.add_argument("--warmup", type=int, default=12)
ap.add_argument("--rgba", action="store_true", help="Save raw source coverage for containment checks")
a = ap.parse_args()
src = open(a.fs).read()
hdr = json.loads(src[src.index("/*") + 2:src.index("*/")]); body = src[src.index("*/") + 2:]
sets = {}
for kv in a.set:
    k, v = kv.split("="); sets[k] = v
decl = []; vals = {}; images = []
for inp in hdr["INPUTS"]:
    n, t = inp["NAME"], inp["TYPE"]
    if t == "image": images.append(n); continue
    if t in ("audio", "audioFFT"): continue
    v = sets.get(n, inp.get("DEFAULT", 0))
    if t == "float": decl.append(f"uniform float {n};"); vals[n] = float(v)
    elif t in ("long", "bool"):
        if isinstance(v, str) and not v.lstrip("-").isdigit() and "LABELS" in inp: v = inp["LABELS"].index(v)
        if isinstance(v, bool): v = int(v)
        decl.append(f"uniform int {n};" if t == "long" else f"uniform bool {n};"); vals[n] = int(float(v)) if t == "long" else bool(int(float(v)) if not isinstance(v, bool) else v)
    elif t == "color": decl.append(f"uniform vec4 {n};"); vals[n] = tuple(float(x) for x in (v if isinstance(v, (list, tuple)) else v.split(",")))
    elif t == "point2D": decl.append(f"uniform vec2 {n};"); vals[n] = tuple(float(x) for x in (v if isinstance(v, (list, tuple)) else v.split(",")))
passes = hdr.get("PASSES") or [{}]
targets = [p.get("TARGET") for p in passes if p.get("TARGET")]
def dim(expr, base):
    if expr is None: return base
    if isinstance(expr, (int, float)): return int(expr)
    e = str(expr).replace("$WIDTH", str(a.w)).replace("$HEIGHT", str(a.H))
    return int(eval(e, {"__builtins__": {}}, {}))
samplers = images + targets
sdecl = "".join(f"uniform sampler2D {s}; uniform vec2 _{s}_size;\n" for s in samplers)
macros = """
#define IMG_SIZE(img) _##img##_size
#define IMG_PIXEL(img, px) texture(img, (px) / _##img##_size)
#define IMG_NORM_PIXEL(img, uv) texture(img, uv)
#define IMG_THIS_PIXEL(img) texture(img, gl_FragCoord.xy / RENDERSIZE)
#define IMG_THIS_NORM_PIXEL(img) texture(img, gl_FragCoord.xy / RENDERSIZE)
"""
frag = ("#version 410\nout vec4 fragColor;\n#define gl_FragColor fragColor\nuniform vec2 RENDERSIZE; uniform float TIME; uniform int PASSINDEX; uniform int FRAMEINDEX; uniform float TIMEDELTA;\nvec2 isf_FragNormCoord;\n"
        + sdecl + macros + "\n".join(decl) + "\n" + body.replace("void main()", "void isf_main(); void main(){ isf_FragNormCoord = gl_FragCoord.xy / RENDERSIZE; isf_main(); }\nvoid isf_main()", 1))
vert = "#version 410\nin vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }"
ctx = moderngl.create_standalone_context()
try: prog = ctx.program(vertex_shader=vert, fragment_shader=frag)
except Exception as e: print("COMPILE ERROR\n", e); sys.exit(2)
for k, v in vals.items():
    if k in prog: prog[k].value = v
vbo = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4").tobytes()); vao = ctx.simple_vertex_array(prog, vbo, "p")
# buffers: one per target (persistent or not), double-buffered so a pass can read its own previous contents
bufs = {}
for p in passes:
    t = p.get("TARGET")
    if not t: continue
    W, Hh = dim(p.get("WIDTH"), a.w), dim(p.get("HEIGHT"), a.H)
    comp = "f4" if p.get("FLOAT") else "f1"
    mk = lambda: ctx.texture((W, Hh), 4, dtype=comp)
    bufs[t] = {"read": mk(), "write": mk(), "size": (W, Hh), "persistent": bool(p.get("PERSISTENT"))}
    for tx in (bufs[t]["read"], bufs[t]["write"]): tx.repeat_x = tx.repeat_y = False; tx.filter = (moderngl.LINEAR, moderngl.LINEAR)
    z = np.zeros((Hh, W, 4), dtype="f4" if comp == "f4" else "u1"); bufs[t]["read"].write(z.tobytes()); bufs[t]["write"].write(z.tobytes())
out_tex = ctx.texture((a.w, a.H), 4); out_fbo = ctx.framebuffer(color_attachments=[out_tex])
fbos = {t: {"read": ctx.framebuffer(color_attachments=[b["read"]]), "write": ctx.framebuffer(color_attachments=[b["write"]])} for t, b in bufs.items()}
base_in = Image.open(a.input).convert("RGBA") if a.input else Image.new("RGBA", (a.w, a.H), (0, 0, 0, 0))
in_tex = ctx.texture(base_in.size, 4); dx, dy = [float(x) for x in a.move.split(",")]
strip = []; keep = set(np.linspace(0, a.frames - 1, a.strip).astype(int)) if a.strip else set()
timings = []
for f in range(a.frames):
    # the moving input: the frame shifted by (dx, dy) * f pixels, wrapping
    im = base_in
    if dx or dy:
        arr = np.array(base_in); arr = np.roll(arr, (int(round(dy * f)), int(round(dx * f))), axis=(0, 1)); im = Image.fromarray(arr, "RGBA")
    in_tex.write(im.transpose(Image.FLIP_TOP_BOTTOM).tobytes())
    if "TIME" in prog: prog["TIME"].value = f / a.fps
    if "FRAMEINDEX" in prog: prog["FRAMEINDEX"].value = f
    if "TIMEDELTA" in prog: prog["TIMEDELTA"].value = 1.0 / a.fps
    if a.benchmark: ctx.finish(); render_start = time.perf_counter()
    for pi, p in enumerate(passes):
        t = p.get("TARGET"); unit = 0
        for s in samplers:
            if s in images: tex = in_tex; size = in_tex.size
            else: tex = bufs[s]["read"]; size = bufs[s]["size"]
            tex.use(unit)
            if s in prog: prog[s].value = unit
            if f"_{s}_size" in prog: prog[f"_{s}_size"].value = (float(size[0]), float(size[1]))
            unit += 1
        if t: fbo = fbos[t]["write"]; size = bufs[t]["size"]
        else: fbo = out_fbo; size = (a.w, a.H)
        fbo.use(); ctx.viewport = (0, 0, size[0], size[1])
        prog["RENDERSIZE"].value = (float(size[0]), float(size[1]))
        if "PASSINDEX" in prog: prog["PASSINDEX"].value = pi
        ctx.clear(0, 0, 0, 0); vao.render(moderngl.TRIANGLE_STRIP)
        if t:  # the pass's result becomes readable for later passes and the next frame
            bufs[t]["read"], bufs[t]["write"] = bufs[t]["write"], bufs[t]["read"]
            fbos[t]["read"], fbos[t]["write"] = fbos[t]["write"], fbos[t]["read"]
    if a.benchmark:
        ctx.finish()
        if f >= a.warmup: timings.append((time.perf_counter() - render_start) * 1000)
    if f in keep or f == a.frames - 1:
        img = np.frombuffer(out_fbo.read(components=4), dtype="u1").reshape(a.H, a.w, 4)[::-1]
        rgb = (img[..., :3].astype(np.float32) * (img[..., 3:4].astype(np.float32) / 255.0)).astype("u1")
        if f in keep: strip.append(Image.fromarray(rgb, "RGB"))
        if f == a.frames - 1: final = Image.fromarray(img.copy(), "RGBA") if a.rgba else Image.fromarray(rgb, "RGB")
if a.scale > 1: final = final.resize((a.w // a.scale, a.H // a.scale), Image.LANCZOS)
final.save(a.out); print("wrote", a.out, final.size, "frames", a.frames)
if strip:
    k = len(strip); sw = a.w // 4; sh = a.H // 4
    sheet = Image.new("RGB", (sw * min(k, 3), sh * ((k + 2) // 3)))
    for i, im in enumerate(strip): sheet.paste(im.resize((sw, sh), Image.LANCZOS), ((i % 3) * sw, (i // 3) * sh))
    sp = a.out.rsplit(".", 1)[0] + "_strip.png"; sheet.save(sp); print("wrote", sp)

if a.benchmark:
    if not timings: raise ValueError("frames must exceed warmup")
    ordered = sorted(timings)
    report = {"shader": a.fs, "renderer": ctx.info["GL_RENDERER"], "resolution": [a.w,a.H],
              "method": "CPU submission plus GPU completion, all passes; excludes readback; not Arena frame time",
              "samples": len(timings), "warmup": a.warmup, "settings": sets,
              "median_ms": statistics.median(timings), "p95_ms": ordered[min(len(ordered)-1, int(len(ordered)*0.95))],
              "max_ms": max(timings), "samples_ms": timings}
    open(a.benchmark,"w").write(json.dumps(report,indent=2))
    print("render ms median",round(report["median_ms"],3),"p95",round(report["p95_ms"],3))
