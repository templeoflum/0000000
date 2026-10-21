#!/usr/bin/env python3
"""make_chain_studies.py — feedback studies for the SERIAL CHAIN (2026-09-02):
Delay line (top) -> Sculpt (middle) -> Feedback (bottom); each layer's Video Router reads the
layer directly above. A Router has no loop, so the loop lives INSIDE the study effect:
    acc(t) = combine( input , op( acc(t-1) ) * Gain - Floor )     one persistent buffer
Dry is never attenuated (combine = max, his delay model); Key hides at the mix (alpha).
One lesson per shader, judged with his eye, one at a time:
  Study Texture  Diffuse + Etch BOTH live at once — their competition grows pattern
  Study Color    Hue step °/pass · Sat ×/pass · Invert (flavor)
  Study Fold     Mirror picker off/x/xy/radial-6 + Fold amount (blendable)
  Study Mixer    the circuit element itself: Blend picker (max/add/screen/mix/diff/mult) × Feed
"""
import json, os, subprocess, sys

def emit(name, desc, inputs, body):
    hdr = {"DESCRIPTION": desc, "CREDIT": "SP study", "ISFVSN": "2", "CATEGORIES": ["Generator"],
           "INPUTS": [{"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"}] + inputs,
           "PASSES": [{"TARGET": "acc", "PERSISTENT": True}, {}]}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + body
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{name}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{name}.fs", "w").write(out)
    here = os.path.dirname(os.path.abspath(__file__))
    open(os.path.join(here, f"{name}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{name}.sp.json", "w"))
    return f"{D}/{name}.fs"

BASE = [
    {"NAME": "gainv",  "LABEL": "Gain",  "TYPE": "float", "DEFAULT": 0.97, "MIN": 0.80, "MAX": 1.00},
    {"NAME": "floorv", "LABEL": "Floor", "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.10},
    {"NAME": "keyv",   "LABEL": "Key",   "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.5},
]

# shared frame: PASS 0 writes acc, PASS 1 shows it. OP fills `col` from `prev` (and may remap uv).
FRAME = """
float spLum(vec3 c) {{ return dot(c, vec3(0.299, 0.587, 0.114)); }}
{helpers}
void main() {{
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {{
        vec4 live = IMG_NORM_PIXEL(inputImage, uv);          // the layer above, via the Router
        vec2 puv = uv;                                       // where the loop reads its past
{op}
        col = max(col * gainv - floorv, 0.0);                // the learned level base, in the loop
{combine}
        gl_FragColor = vec4(outc, 1.0);
    }} else {{
        vec3 c = IMG_NORM_PIXEL(acc, uv).rgb;
        float lum = spLum(c);
        float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);   // Key: at the mix
        gl_FragColor = vec4(c, a);
    }}
}}
"""
COMBINE_MAX = "        vec3 outc = max(live.rgb, col);                       // dry never attenuated"

def study(name, desc, inputs, op, helpers="", combine=COMBINE_MAX):
    return emit(name, desc, inputs + BASE, FRAME.format(helpers=helpers, op=op, combine=combine))

# ── TEXTURE: Diffuse and Etch both live; one kernel serves both ──────────────
IN_T = [
    {"NAME": "dif",  "LABEL": "Diffuse", "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "etch", "LABEL": "Etch",    "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 2.0},
    {"NAME": "grain","LABEL": "Grain",   "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
]
OP_T = """
        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        float r = (0.0008 + grain * 0.012);                   // Grain = kernel radius (pattern scale)
        vec2 px = vec2(r / (RENDERSIZE.x / RENDERSIZE.y), r);
        vec3 b = (IMG_NORM_PIXEL(acc, puv + vec2( px.x, 0.0)).rgb + IMG_NORM_PIXEL(acc, puv + vec2(-px.x, 0.0)).rgb
                + IMG_NORM_PIXEL(acc, puv + vec2(0.0,  px.y)).rgb + IMG_NORM_PIXEL(acc, puv + vec2(0.0, -px.y)).rgb) * 0.25;
        vec3 col = clamp(mix(prev, b, dif) + (prev - b) * etch, 0.0, 1.0);   // spread toward b, fight against b
"""
print("wrote", study("SP Study Texture",
    "SP Study TEXTURE (chain) - Diffuse and Etch both live in the loop; Grain sets the kernel scale. Self-looping on a Video Router.", IN_T, OP_T))

# ── COLOR: per-pass hue step, sat, invert flavor ──────────────────────────────
IN_C = [
    {"NAME": "hue",  "LABEL": "Hue Step", "TYPE": "float", "DEFAULT": 3.0, "MIN": -30.0, "MAX": 30.0},
    {"NAME": "satv", "LABEL": "Sat",      "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.5,   "MAX": 1.5},
    {"NAME": "inv",  "LABEL": "Invert",   "TYPE": "bool",  "DEFAULT": False},
]
HELP_C = """
vec3 spHueR(vec3 c, float a) {
    const vec3 k = vec3(0.57735);
    return c * cos(a) + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - cos(a));
}"""
OP_C = """
        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        float pres = smoothstep(0.0, 0.04, spLum(prev));      // presence before color ops: Invert recolors what exists
        vec3 col = prev;
        if (abs(hue) > 0.01) col = clamp(spHueR(col, hue * 0.017453293), 0.0, 1.0);
        col = clamp(mix(vec3(spLum(col)), col, satv), 0.0, 1.0);
        if (inv) col = (vec3(1.0) - col) * pres;
"""
print("wrote", study("SP Study Color",
    "SP Study COLOR (chain) - Hue Step deg/pass, Sat x/pass, Invert flavor, inside the loop. Self-looping on a Video Router.", IN_C, OP_C, HELP_C))

# ── FOLD: mirror picker + blendable amount ────────────────────────────────────
IN_F = [
    {"NAME": "mir",   "LABEL": "Mirror", "TYPE": "long",  "DEFAULT": 1, "VALUES": [0, 1, 2, 3], "LABELS": ["off", "x", "xy", "radial"]},
    {"NAME": "foldv", "LABEL": "Fold",   "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "cx",    "LABEL": "Center X", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "cy",    "LABEL": "Center Y", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
]
OP_F = """
        float asp = RENDERSIZE.x / RENDERSIZE.y;
        vec2 ctr = vec2(cx, cy);
        vec2 q = (uv - ctr) * vec2(asp, 1.0);
        vec2 f = q;
        if (mir == 1) f.x = abs(q.x);
        else if (mir == 2) f = abs(q);
        else if (mir == 3) {
            float an = atan(q.y, q.x); float rr = length(q);
            an = abs(mod(an, 1.0471976) - 0.5235988);          // 6-fold sector
            f = vec2(cos(an), sin(an)) * rr;
        }
        q = mix(q, f, foldv);                                  // the fold is blendable
        puv = q / vec2(asp, 1.0) + ctr;
        float inside = (puv.x >= 0.0 && puv.x <= 1.0 && puv.y >= 0.0 && puv.y <= 1.0) ? 1.0 : 0.0;
        vec3 col = IMG_NORM_PIXEL(acc, clamp(puv, 0.0, 1.0)).rgb * inside;
"""
print("wrote", study("SP Study Fold",
    "SP Study FOLD (chain) - Mirror picker off/x/xy/radial-6 with blendable Fold amount and center, inside the loop. Self-looping on a Video Router.", IN_F, OP_F))

# ── MIXER: the circuit element — how live and loop combine ────────────────────
IN_M = [
    {"NAME": "blend", "LABEL": "Blend", "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1, 2, 3, 4, 5],
     "LABELS": ["max", "add", "screen", "mix", "difference", "multiply"]},
    {"NAME": "feed",  "LABEL": "Feed",  "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
]
OP_M = """
        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        vec3 col = prev;
"""
COMBINE_M = """
        col *= feed;                                           // Feed = how much loop re-enters
        vec3 l = live.rgb, outc;
        if      (blend == 0) outc = max(l, col);
        else if (blend == 1) outc = min(l + col, 1.0);
        else if (blend == 2) outc = 1.0 - (1.0 - l) * (1.0 - col);
        else if (blend == 3) outc = mix(l, col, 0.5);
        else if (blend == 4) outc = abs(l - col);
        else                 outc = l * col + l * (1.0 - feed);   // multiply gates on presence; Feed 0 = passthrough
"""
print("wrote", study("SP Study Mixer",
    "SP Study MIXER (chain) - the circuit element: Blend picker (max/add/screen/mix/difference/multiply) x Feed, live vs loop. Self-looping on a Video Router.", IN_M, OP_M, combine=COMBINE_M))

if "--build" in sys.argv:
    for n in ["SP Study Texture", "SP Study Color", "SP Study Fold", "SP Study Mixer"]:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), n, "effect"], check=True)

# ── FEEDBACK-LAYER versions of LEVEL and MAP (2026-09-02): the comp-loop originals become
#    plain per-pass operators on the SCULPT layer (router, no loop); these carry the loop. ──
IN_L = [
    {"NAME": "curvev", "LABEL": "Curve",   "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.4, "MAX": 2.5},
    {"NAME": "ceilv",  "LABEL": "Ceiling", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.5, "MAX": 1.0},
    {"NAME": "liftv",  "LABEL": "Lift",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 0.10},
]
OP_L = """
        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        vec3 col = pow(prev, vec3(curvev));                   // Curve: iterated nonlinearity
        col = min(col + liftv, vec3(ceilv));                  // Lift post-curve (independent of Floor), Ceiling
"""
print("wrote", study("SP Chain Level",
    "SP Chain LEVEL - the energy budget on a routed loop: Gain/Floor (base) + Curve/Lift/Ceiling, Key at the mix. Self-looping on a Video Router.", IN_L, OP_L))

IN_MP = [
    {"NAME": "zoomv", "LABEL": "Zoom",     "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.80, "MAX": 1.20},
    {"NAME": "rotz",  "LABEL": "Rotate",   "TYPE": "float", "DEFAULT": 0.0, "MIN": -30.0, "MAX": 30.0},
    {"NAME": "dx",    "LABEL": "Drift X",  "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.02, "MAX": 0.02},
    {"NAME": "dy",    "LABEL": "Drift Y",  "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.02, "MAX": 0.02},
    {"NAME": "cx",    "LABEL": "Center X", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0,  "MAX": 1.0},
    {"NAME": "cy",    "LABEL": "Center Y", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0,  "MAX": 1.0},
]
OP_MP = """
        float asp = RENDERSIZE.x / RENDERSIZE.y;
        vec2 ctr = vec2(cx, cy);
        vec2 q = (uv - ctr) * vec2(asp, 1.0);
        float a = -rotz * 0.017453293;
        q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q / zoomv;   // inverse per-pass map
        puv = q / vec2(asp, 1.0) + ctr - vec2(dx, dy);
        float inside = (puv.x >= 0.0 && puv.x <= 1.0 && puv.y >= 0.0 && puv.y <= 1.0) ? 1.0 : 0.0;
        vec3 col = IMG_NORM_PIXEL(acc, clamp(puv, 0.0, 1.0)).rgb * inside;   // outside the frame: no signal
"""
print("wrote", study("SP Chain Map",
    "SP Chain MAP - per-pass zoom/rotate/drift/center on a routed loop, over the level base. Self-looping on a Video Router.", IN_MP, OP_MP))
