#!/usr/bin/env python3
"""render_isf.py — offscreen GPU render of a single-pass ISF fragment shader at a real resolution, to PNG.
QA harness: look at actual pixels before reloading anything into Arena.
  qa/.venv/bin/python render_isf.py "SP Atom Glyph.fs" -o out.png [-w 1080 -H 1920] [--set style=1 --set glyph=3.5 ...]
  --crop cx,cy,w,h   save a native-pixel crop (centre in 0..1, size in px) instead of the whole frame
  --scale N          downscale the saved image by N (whole frame overview)
Inputs not given take the ISF DEFAULT. TIME is 0 unless --time. Persistent-pass shaders are not supported (single pass)."""
import argparse, json, os, sys
import numpy as np, moderngl
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("fs"); ap.add_argument("-o", "--out", required=True)
ap.add_argument("-w", type=int, default=1080); ap.add_argument("-H", type=int, default=1920)
ap.add_argument("--set", action="append", default=[]); ap.add_argument("--time", type=float, default=0.0)
ap.add_argument("--crop", default=None); ap.add_argument("--scale", type=int, default=1)
ap.add_argument("--input", default=None, help="PNG fed as inputImage (effect shaders)")
ap.add_argument("--rgba", action="store_true", help="save the raw RGBA instead of compositing over black")
a = ap.parse_args()
src = open(a.fs).read()
hdr = json.loads(src[src.index("/*") + 2:src.index("*/")]); body = src[src.index("*/") + 2:]
sets = {}
for kv in a.set:
    k, v = kv.split("="); sets[k] = v
decl = []; vals = {}
for inp in hdr["INPUTS"]:
    n, t = inp["NAME"], inp["TYPE"]
    if t in ("image", "audio", "audioFFT"): continue          # samplers come from --input
    v = sets.get(n, inp.get("DEFAULT", 0))
    if t == "float": decl.append(f"uniform float {n};"); vals[n] = float(v)
    elif t in ("long", "bool"):
        if isinstance(v, str) and not v.lstrip("-").isdigit() and "LABELS" in inp: v = inp["LABELS"].index(v)
        decl.append(f"uniform int {n};"); vals[n] = int(float(v))
    elif t == "color": decl.append(f"uniform vec4 {n};"); vals[n] = tuple(float(x) for x in (v if isinstance(v, (list, tuple)) else v.split(",")))
    elif t == "point2D": decl.append(f"uniform vec2 {n};"); vals[n] = tuple(float(x) for x in (v if isinstance(v, (list, tuple)) else v.split(",")))
    else: decl.append(f"uniform float {n};"); vals[n] = float(v)
ISF_MACROS = """
uniform sampler2D inputImage; uniform vec2 _inputImage_size;
#define IMG_SIZE(img) _inputImage_size
#define IMG_PIXEL(img, px) texture(img, (px) / _inputImage_size)
#define IMG_NORM_PIXEL(img, uv) texture(img, uv)
#define IMG_THIS_PIXEL(img) texture(img, gl_FragCoord.xy / RENDERSIZE)
#define IMG_THIS_NORM_PIXEL(img) texture(img, gl_FragCoord.xy / RENDERSIZE)
vec2 isf_FragNormCoord;
"""
frag = "#version 410\nout vec4 fragColor;\n#define gl_FragColor fragColor\nuniform vec2 RENDERSIZE; uniform float TIME;\n" + ISF_MACROS + "\n".join(decl) + "\n" + body.replace("void main()", "void isf_main(); void main(){ isf_FragNormCoord = gl_FragCoord.xy / RENDERSIZE; isf_main(); }\nvoid isf_main()", 1)
vert = "#version 410\nin vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }"
ctx = moderngl.create_standalone_context()
try:
    prog = ctx.program(vertex_shader=vert, fragment_shader=frag)
except Exception as e:
    print("COMPILE ERROR\n", e); sys.exit(2)
for k, v in vals.items():
    if k in prog: prog[k].value = v
prog["RENDERSIZE"].value = (float(a.w), float(a.H))
if a.input:
    im_in = Image.open(a.input).convert("RGBA")
    tex = ctx.texture(im_in.size, 4, im_in.transpose(Image.FLIP_TOP_BOTTOM).tobytes()); tex.use(0)
    if "inputImage" in prog: prog["inputImage"].value = 0
    if "_inputImage_size" in prog: prog["_inputImage_size"].value = (float(im_in.width), float(im_in.height))
if "TIME" in prog: prog["TIME"].value = a.time
vbo = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4").tobytes())
vao = ctx.simple_vertex_array(prog, vbo, "p")
fbo = ctx.simple_framebuffer((a.w, a.H), components=4); fbo.use(); ctx.clear(0, 0, 0, 0)
vao.render(moderngl.TRIANGLE_STRIP)
img = np.frombuffer(fbo.read(components=4), dtype="u1").reshape(a.H, a.w, 4)[::-1]
# composite over black so alpha reads as coverage (the layer sits over black feedback)
rgb = (img[..., :3].astype(np.float32) * (img[..., 3:4].astype(np.float32) / 255.0)).astype("u1")
im = Image.fromarray(img.copy(), "RGBA") if a.rgba else Image.fromarray(rgb, "RGB")
if a.crop:
    cx, cy, cw, ch = [float(x) for x in a.crop.split(",")]
    x0 = int(cx * a.w - cw / 2); y0 = int((1 - cy) * a.H - ch / 2)
    im = im.crop((x0, y0, x0 + int(cw), y0 + int(ch)))
if a.scale > 1: im = im.resize((im.width // a.scale, im.height // a.scale), Image.LANCZOS)
im.save(a.out); print("wrote", a.out, im.size, "alpha coverage %.4f" % (img[..., 3].astype(np.float32).mean() / 255))
