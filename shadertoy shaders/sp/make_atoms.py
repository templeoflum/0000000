#!/usr/bin/env python3
"""make_atoms.py — source-layer ATOMS (2026-09-02). Pure operators: no slot machinery, no drives,
plain emit, a flavor PICKER per atom, judged layer-soloed. Harness re-attached once locked.
  SP Atom Figure 3D — Figure A / Figure B / Morph over an SDF catalog (torus, sphere, box,
                      octahedron, tetrahedron, icosahedron, dodecahedron); one sun.
  SP Atom Figure 2D — disc / ring / polygon / star silhouette, fill or outline.
  SP Atom Grain     — film / static / dust / lines.
  SP Atom Texture   — scanlines / halftone / hatch / weave.
  SP Atom Glyph     — blocks / runes / matrix / dots — procedural glyph mass.
"""
import json, os, subprocess, sys

def emit(name, desc, inputs, body, passes=None):
    hdr = {"DESCRIPTION": desc, "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": inputs}
    if passes: hdr["PASSES"] = passes
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + body
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{name}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{name}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{name}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{name}.sp.json", "w"))
    return f"{D}/{name}.fs"

FIGS = ["torus", "sphere", "box", "octahedron", "tetrahedron", "icosahedron", "dodecahedron"]
IN_F3 = [
    {"NAME": "figA",   "LABEL": "Figure A", "TYPE": "long", "DEFAULT": 0, "VALUES": list(range(7)), "LABELS": FIGS},
    {"NAME": "figB",   "LABEL": "Figure B", "TYPE": "long", "DEFAULT": 5, "VALUES": list(range(7)), "LABELS": FIGS},
    {"NAME": "morph",  "LABEL": "Morph",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",  "LABEL": "Size",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "px",     "LABEL": "X",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "py",     "LABEL": "Y",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "tumble", "LABEL": "Tumble",   "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "axisv",  "LABEL": "Axis",     "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sun",    "LABEL": "Sun",      "TYPE": "float", "DEFAULT": 0.9, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "height", "LABEL": "Height",   "TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "distance","LABEL": "Distance","TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "shadow", "LABEL": "Shadow",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "material","LABEL": "Material","TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["smooth", "stone", "crystal", "glass"]},
    {"NAME": "micro",  "LABEL": "Micro",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "fine",   "LABEL": "Fine",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "colorm", "LABEL": "Color",    "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2], "LABELS": ["gray", "loop", "normal"]},
    {"NAME": "loopv",  "LABEL": "Loop",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 4.0},
    {"NAME": "hue",    "LABEL": "Hue",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rOff",   "LABEL": "Red",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gOff",   "LABEL": "Green",    "TYPE": "float", "DEFAULT": 0.33, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bOff",   "LABEL": "Blue",     "TYPE": "float", "DEFAULT": 0.67, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "shade",  "LABEL": "Shade",    "TYPE": "float", "DEFAULT": 0.8, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "edge",   "LABEL": "Edge",     "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "emboss", "LABEL": "Emboss",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]
BODY_F3 = """
#define PHI 1.6180339887
#define CAMZ 3.2
#define FOV 1.1
vec3 spRotAA(vec3 p, vec3 ax, float th) { float c = cos(th), s = sin(th); return p * c + cross(ax, p) * s + ax * dot(ax, p) * (1.0 - c); }
float spGdf(vec3 p, vec3 n) { return abs(dot(p, normalize(n))); }
float spH3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float spN3(vec3 p) {
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(spH3(i), spH3(i + vec3(1, 0, 0)), f.x), mix(spH3(i + vec3(0, 1, 0)), spH3(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(spH3(i + vec3(0, 0, 1)), spH3(i + vec3(1, 0, 1)), f.x), mix(spH3(i + vec3(0, 1, 1)), spH3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float spFig(int f, vec3 p, float r) {
    if (f == 0) { vec2 q = vec2(length(p.xz) - r * 0.72, p.y); return length(q) - r * 0.28; }
    if (f == 1) return length(p) - r;
    if (f == 2) { vec3 q = abs(p) - r * 0.554; return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r * 0.04; }
    if (f == 3) return (abs(p.x) + abs(p.y) + abs(p.z) - r) * 0.57735;
    if (f == 4) {
        float d = dot(p, normalize(vec3(1, 1, 1)));
        d = max(d, dot(p, normalize(vec3(-1, -1, 1)))); d = max(d, dot(p, normalize(vec3(-1, 1, -1)))); d = max(d, dot(p, normalize(vec3(1, -1, -1))));
        return d - r * 0.3333;
    }
    if (f == 5) {
        float d = spGdf(p, vec3(1, 1, 1));
        d = max(d, spGdf(p, vec3(-1, 1, 1))); d = max(d, spGdf(p, vec3(1, -1, 1))); d = max(d, spGdf(p, vec3(1, 1, -1)));
        d = max(d, spGdf(p, vec3(0, 1, PHI + 1.0))); d = max(d, spGdf(p, vec3(0, -1, PHI + 1.0)));
        d = max(d, spGdf(p, vec3(PHI + 1.0, 0, 1))); d = max(d, spGdf(p, vec3(-(PHI + 1.0), 0, 1)));
        d = max(d, spGdf(p, vec3(1, PHI + 1.0, 0))); d = max(d, spGdf(p, vec3(-1, PHI + 1.0, 0)));
        return d - r * 0.7947;
    }
    float d = spGdf(p, vec3(0, PHI, 1));
    d = max(d, spGdf(p, vec3(0, -PHI, 1))); d = max(d, spGdf(p, vec3(1, 0, PHI))); d = max(d, spGdf(p, vec3(-1, 0, PHI)));
    d = max(d, spGdf(p, vec3(PHI, 1, 0))); d = max(d, spGdf(p, vec3(-PHI, 1, 0)));
    return d - r * 0.7947;
}
float gR; vec3 gAxis; float gTh; vec3 gLp;
vec3 spObj(vec3 p) { return spRotAA(p, gAxis, gTh); }
float spMap(vec3 p) { vec3 q = spObj(p); return mix(spFig(figA, q, gR), spFig(figB, q, gR), morph); }
vec3 spNorm(vec3 p) { vec2 e = vec2(0.002, 0.0); return normalize(vec3(spMap(p + e.xyy) - spMap(p - e.xyy), spMap(p + e.yxy) - spMap(p - e.yxy), spMap(p + e.yyx) - spMap(p - e.yyx))); }
vec3 spRay(vec2 uv) { return normalize(vec3(uv * FOV, 1.0)); }
float spMarch(vec2 uv, out vec3 p, out float dmin) {
    vec3 ro = vec3(0.0, 0.0, -CAMZ), rd = spRay(uv); float t = 0.0, d = 0.0; dmin = 9.0;
    for (int i = 0; i < 80; i++) { p = ro + rd * t; d = spMap(p); dmin = min(dmin, d); if (d < 0.001 || t > 7.0) break; t += d * 0.8; }
    return (d < 0.001) ? 1.0 : 0.0;
}
float spRelief(vec3 po) {
    float sc = mix(10.0, 80.0, fine);
    if (material == 1) { float pores = 1.0 - smoothstep(0.40, 0.75, spN3(po * sc * 1.3 + 31.7)); return pores * 0.7 + spN3(po * sc * 4.0 + 7.3) * 0.3; }
    if (material == 3) return spN3(po * sc * 2.0) * 0.5;
    return spN3(po * sc) * 0.6 + spN3(po * sc * 4.1 + 7.3) * 0.4;
}
vec3 spSurface(vec3 p, vec3 n) {
    if (material == 2) {
        float k = mix(2.0, 7.0, fine);
        vec3 no = spObj(n);
        vec3 f = normalize(floor(no * k + 0.5) / k + 0.0001);
        return normalize(mix(n, spRotAA(f, gAxis, -gTh), micro));
    }
    if (micro < 0.001) return n;
    vec3 po = spObj(p); float e = 0.35 / mix(10.0, 80.0, fine);
    vec3 g = vec3(spRelief(po + vec3(e, 0, 0)) - spRelief(po - vec3(e, 0, 0)),
                  spRelief(po + vec3(0, e, 0)) - spRelief(po - vec3(0, e, 0)),
                  spRelief(po + vec3(0, 0, e)) - spRelief(po - vec3(0, 0, e)));
    return normalize(n + spRotAA(g, gAxis, -gTh) * micro * 1.4);
}
vec3 spSunDir() { float ph = sun * 6.2831853, th = (height - 0.5) * 3.14159; return normalize(vec3(cos(th) * sin(ph), sin(th), -cos(th) * cos(ph))); }
vec2 spShade(vec3 p, vec3 n, vec3 rd) {
    vec3 Lv = gLp - p; float Ld2 = dot(Lv, Lv); vec3 L = Lv * inversesqrt(Ld2);
    float D = length(gLp);
    float att = clamp((D - gR) * (D - gR) / Ld2, 0.0, 1.0);
    float lam = clamp(dot(n, L), 0.0, 1.0) * att;
    float facing = clamp(dot(n, -rd), 0.0, 1.0);
    float rimL = pow(1.0 - facing, 2.0);
    float fres = pow(1.0 - facing, 4.0);
    float specPow = mix(10.0, 40.0, distance);
    float spec = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow) * att;
    float vol, alpha = 1.0;
    if (material == 1) { float occ = (micro > 0.001) ? 1.0 - micro * 0.5 * spRelief(spObj(p)) : 1.0; vol = (0.10 + 0.85 * lam + 0.10 * rimL) * occ; }
    else if (material == 2) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.8) * att; vol = 0.10 + 0.45 * lam + 0.55 * fres + 1.2 * sp2; }
    else if (material == 3) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.4) * att; float frost = micro * 0.6;
        vol = 0.9 * fres + 1.3 * sp2 * (1.0 - frost * 0.7) + frost * (0.2 + 0.4 * lam); alpha = clamp(0.12 + 0.88 * fres + sp2 + frost, 0.0, 1.0); }
    else { vol = 0.14 + 0.72 * lam + 0.30 * rimL * (1.0 + 0.8 * micro) + spec * (0.35 + 0.8 * micro);
        if (micro > 0.001) { float gn = spN3(spObj(p) * 90.0); vol *= 1.0 + micro * 0.30 * (gn - 0.5) * (0.5 + rimL); } }
    return vec2(mix(0.92, vol, shade), alpha);
}
float spLum(vec2 uv) { vec3 p; float dm; if (spMarch(uv, p, dm) < 0.5) return 0.0; vec3 n = spSurface(p, spNorm(p)); return spShade(p, n, spRay(uv)).x; }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    gTh = TIME * tumble * 1.5;
    float ax = axisv * 3.14159;
    gAxis = normalize(vec3(sin(ax), cos(ax), 0.35 * sin(ax * 2.0)));
    vec3 sd = spSunDir();
    float near = 1.0 - distance;
    vec2 shOff = -normalize(sd.xy + vec2(0.0001, -0.0001)) * shadow * (0.10 + 0.10 * near);
    float shSoft = mix(0.01, 0.12, near) * shadow;
    float shLen = shadow * (0.20 + 0.12) + 0.002;
    float m = 0.04;
    float room = min(hf2.x, hf2.y) - m - shLen;
    float Rp = mix(0.03, max(room, 0.03), sizev);
    float k = Rp * FOV;
    gR = k * CAMZ / (1.0 + k);
    gLp = sd * gR * mix(1.35, 30.0, distance);
    vec2 c = (vec2(px, py) - 0.5) * 2.0 * max(hf2 - Rp - shLen - m, vec2(0.0));
    vec2 s = uv - c;
    vec3 p; float dm; float hit = spMarch(s, p, dm);
    vec3 col = vec3(0.0); float a = 0.0;
    if (hit > 0.5) {
        vec3 rd = spRay(s);
        vec3 n = spSurface(p, spNorm(p));
        float facing = clamp(dot(n, -rd), 0.0, 1.0);
        vec2 sh = spShade(p, n, rd);
        float body = sh.x;
        float inkOn = clamp(edge * 8.0, 0.0, 1.0);
        float rim = 1.0 - facing;
        float th2 = 1.0 - mix(0.5, 0.10, edge);
        float inkM = inkOn * 0.9 * smoothstep(th2 - 0.03, th2 + 0.03, rim);
        float shoulder = smoothstep(th2 - 0.30, th2, rim);
        float pinna = smoothstep(th2 - 0.09, th2 - 0.03, rim) * (1.0 - smoothstep(th2 - 0.03, th2, rim));
        body *= 1.0 + 0.20 * inkOn * shoulder;
        body += 0.30 * inkOn * pinna;
        body = mix(body, floor(body * 4.0 + 0.5) / 4.0, inkOn * shade * 0.6);
        if (emboss > 0.001) { vec2 dir = normalize(sd.xy + vec2(0.0001)) * (0.006 + 0.014 * Rp); body = clamp(body + (spLum(s - dir) - spLum(s + dir)) * emboss * 2.5, 0.0, 1.0); }
        body = min(body, 1.0);
        if (colorm == 0) col = vec3(body);
        else if (colorm == 1) col = (0.5 + 0.5 * cos(6.2831853 * (body * loopv + hue + vec3(rOff, gOff, bOff)))) * mix(1.0, body, 0.35);
        else col = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
        col *= (1.0 - inkM);
        a = max(sh.y, inkM);
    } else if (shadow > 0.001) {
        vec3 q; float dms; float sm = spMarch(s - shOff, q, dms);
        float pen = max(sm, 1.0 - smoothstep(0.0, shSoft + 0.002, dms));
        col = vec3(0.0); a = shadow * 0.65 * pen;
    }
    gl_FragColor = vec4(col, a);
}
"""
print("wrote", emit("SP Atom Solid", "SP Atom FIGURE 3D - Figure A / B / Morph; containment law; LIGHT sun/height/distance/shadow; MATERIAL smooth/stone/crystal/glass + micro/fine; COLOR gray/loop/normal; LINE shade/edge/emboss. No drives.", IN_F3, BODY_F3))

FIGS2 = ["disc", "ring", "capsule", "polygon", "star", "cross"]
IN_F2 = [
    {"NAME": "figA",    "LABEL": "Figure A", "TYPE": "long",  "DEFAULT": 0, "VALUES": list(range(6)), "LABELS": FIGS2},
    {"NAME": "figB",    "LABEL": "Figure B", "TYPE": "long",  "DEFAULT": 3, "VALUES": list(range(6)), "LABELS": FIGS2},
    {"NAME": "morph",   "LABEL": "Morph",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sides",   "LABEL": "Sides",    "TYPE": "float", "DEFAULT": 5.0, "MIN": 3.0, "MAX": 12.0},
    {"NAME": "sizev",   "LABEL": "Size",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "px",      "LABEL": "X",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "py",      "LABEL": "Y",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "turn",    "LABEL": "Turn",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "spin",    "LABEL": "Spin",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "outline", "LABEL": "Outline",  "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "soft",    "LABEL": "Soft",     "TYPE": "float", "DEFAULT": 0.05, "MIN": 0.0, "MAX": 1.0},
    # depth — Photoshop layer styles on the distance field, lit from one angle
    {"NAME": "sun",     "LABEL": "Sun",          "TYPE": "float", "DEFAULT": 0.35, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bevel",   "LABEL": "Bevel",        "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "emboss",  "LABEL": "Emboss",       "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "inner",   "LABEL": "Inner Shadow", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "iglow",   "LABEL": "Inner Glow",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "oglow",   "LABEL": "Outer Glow",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "satin",   "LABEL": "Satin",        "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gradient","LABEL": "Gradient",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "contour", "LABEL": "Contour",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "flow",    "LABEL": "Flow",         "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "shadow",  "LABEL": "Shadow",       "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    # color — a palette on the tone; the shadow is never colored
    {"NAME": "colorm",  "LABEL": "Base",         "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["gray", "normal"]},
    {"NAME": "wet",     "LABEL": "Wet",          "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "loopv",   "LABEL": "Loop",         "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 4.0},
    {"NAME": "hue",     "LABEL": "Hue",          "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rOff",    "LABEL": "Red",          "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gOff",    "LABEL": "Green",        "TYPE": "float", "DEFAULT": 0.33, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bOff",    "LABEL": "Blue",         "TYPE": "float", "DEFAULT": 0.67, "MIN": 0.0, "MAX": 1.0},
]
BODY_F2 = """
#define PI 3.14159265
// every 2D figure is normalized so its CIRCUMRADIUS is exactly r — one bounding circle for containment
float spFig2(int f, vec2 q, float r, float n) {
    float an = atan(q.y, q.x), len = length(q);
    if (f == 0) return len - r;                                                             // disc
    if (f == 1) return abs(len - r * 0.85) - r * 0.15;                                      // ring: outer = r
    if (f == 2) { vec2 p = q; p.x -= clamp(p.x, -r * 0.6, r * 0.6); return length(p) - r * 0.4; }   // capsule: half-length + radius = r
    if (f == 3) { float sec = 2.0 * PI / n; return cos(floor(0.5 + an / sec) * sec - an) * len - r * cos(sec * 0.5); }   // polygon: vertex = r
    if (f == 4) { float rr = r * (0.62 + 0.38 * cos(n * an)); return len - rr; }             // star: tip = r
    vec2 p = abs(q); float w = r * 0.28;                                                    // cross: arm = r
    float dx = max(p.x - r, p.y - w), dy = max(p.y - r, p.x - w);
    return min(dx, dy);
}
float spMap2(vec2 q, float r, float n) { return mix(spFig2(figA, q, r, n), spFig2(figB, q, r, n), morph); }   // distance fields interpolate
// Spin: the plane tumbles about its diagonal axis and is seen in perspective (the coin flip);
// returns the material-plane coordinate for a screen point, and a 'behind the eye' flag in z
vec3 spPlane(vec2 sq, float ph, float dU) {
    float c = cos(ph), s = sin(ph);
    vec3 uu = vec3(c, 0.0, -s);
    vec3 vv = vec3(s * s, c, c * s);
    vec3 nn = cross(uu, vv);
    vec3 D = vec3(sq, dU);
    float den = dot(nn, D);
    if (abs(den) < 1e-4) return vec3(1e6, 1e6, 0.0);
    float t = (dU * nn.z) / den;
    if (t <= 0.0) return vec3(1e6, 1e6, 0.0);
    vec3 Xp = vec3(0.0, 0.0, -dU) + t * D;
    return vec3(dot(uu, Xp), dot(vv, Xp), 1.0);
}
float gr2, gn2, gw2, gPh; vec2 gL2;
float spD(vec2 q) { return spMap2(q, gr2, gn2); }
float spMask(float d, float w) { return 1.0 - smoothstep(-w * 0.5, w * 0.5, d); }
// ── the HEIGHT of the styled surface at q: every layer style adds to it; tone and normal both read it ──
float spTone(vec2 q) {
    float r = gr2, w = gw2; vec2 L = gL2;
    float d = spD(q);
    vec2 e = vec2(0.002, 0.0);
    vec2 g = normalize(vec2(spD(q + e.xy) - spD(q - e.xy), spD(q + e.yx) - spD(q - e.yx)) + 1e-5);   // outward normal of the silhouette
    float NdL = dot(g, L);
    float tone = 0.85;
    float din = max(-d, 0.0);
    // Bevel: raised lip, lit on the sun side, dark on the far side
    float bw = r * (0.04 + bevel * 0.35);
    float lip = 1.0 - smoothstep(0.0, bw, din); lip = lip * lip * (3.0 - 2.0 * lip);
    tone += bevel * lip * NdL * 0.7;
    // Emboss: relief — the mask shifted toward and away from the light
    if (emboss > 0.001) {
        float off = r * (0.02 + emboss * 0.08);
        tone += (spMask(spD(q - L * off), w) - spMask(spD(q + L * off), w)) * emboss * 0.7;
    }
    // Inner Shadow: darkens inside the edge on the side away from the light
    float sw = r * (0.06 + inner * 0.4);
    float isd = 1.0 - smoothstep(0.0, sw, din);
    tone -= inner * isd * (0.25 + 0.75 * clamp(-NdL, 0.0, 1.0)) * 0.8;
    // Inner Glow: bright band inside the edge
    float igw = r * (0.03 + iglow * 0.3);
    tone += iglow * (1.0 - smoothstep(0.0, igw, din)) * 0.5;
    // Satin: the mask offset both ways across the light, multiplied
    if (satin > 0.001) {
        vec2 o = vec2(-L.y, L.x) * r * (0.08 + satin * 0.25);
        float sA = spMask(spD(q + o), w * 4.0 + r * 0.05), sB = spMask(spD(q - o), w * 4.0 + r * 0.05);
        tone -= (1.0 - sA * sB) * satin * 0.45;
    }
    // Gradient Overlay: ramp across the body along the light
    tone += gradient * dot(q / max(r, 0.001), L) * 0.35;
    // Contour: inset lines following the shape; strength and spacing ease in
    if (contour > 0.001) {
        float ease = smoothstep(0.0, 0.35, contour);
        float sp = r * mix(0.30, 0.05, contour);
        float k = abs(mod(din / sp + gPh, 1.0) - 0.5) * sp;   // Flow: integrated phase (in spacing units) — lines travel at constant spacing
        float lw = 0.0015 + w * 0.5 + sp * 0.12 * (1.0 - ease);
        float cl = 1.0 - smoothstep(0.0, lw, k);
        tone -= cl * 0.6 * ease * step(0.0001, din);
    }
    return clamp(tone, 0.0, 1.0);
}
// ── the UNLIT height of the styled surface: geometry only, no sun — this is what the normal reads ──
float spHeight(vec2 q) {
    float r = gr2, w = gw2; vec2 L = gL2;
    float d = spD(q);
    float din = max(-d, 0.0);
    float h = 0.0;
    // Bevel: a pillow lip rising over the bevel width (the look that worked)
    float bw = r * (0.06 + bevel * 0.35);
    float lip = 1.0 - smoothstep(0.0, bw, din); lip = lip * lip * (3.0 - 2.0 * lip);
    h -= lip * (0.35 + bevel * 0.65) * bw;                   // edge is lower than the plateau → normal tilts outward
    // Emboss: a raised plate of the same silhouette, slightly inset
    if (emboss > 0.001) { float off = r * (0.02 + emboss * 0.08); h += spMask(d + off, w) * emboss * off; }
    // Inner Shadow: the edge sinks instead of rising
    float sw = r * (0.06 + inner * 0.4);
    float isd = 1.0 - smoothstep(0.0, sw, din);
    h -= isd * inner * sw * 0.6;
    // Satin: folds across the light
    if (satin > 0.001) {
        vec2 o = vec2(-L.y, L.x) * r * (0.08 + satin * 0.25);
        float sA = spMask(spD(q + o), w * 4.0 + r * 0.05), sB = spMask(spD(q - o), w * 4.0 + r * 0.05);
        h -= (1.0 - sA * sB) * satin * r * 0.12;
    }
    // Gradient: a tilt of the whole plate along the light
    h += gradient * dot(q, L) * 0.35;
    // Contour: ridges at the inset lines
    if (contour > 0.001) {
        float ease = smoothstep(0.0, 0.35, contour);
        float sp = r * mix(0.30, 0.05, contour);
        float k = abs(mod(din / sp + gPh, 1.0) - 0.5) * sp;   // Flow: integrated phase (in spacing units) — lines travel at constant spacing
        float lw = 0.0015 + w * 0.5 + sp * 0.12 * (1.0 - ease);
        h += (1.0 - smoothstep(0.0, lw * 1.5, k)) * ease * lw * 1.2 * step(0.0001, din);
    }
    return h;
}
void main() {
    // pass 0: integrate the contour phase (speed = Flow², signed) in units of the current spacing; wraps at 1
    float spNow = mix(0.30, 0.05, contour);                 // spacing as a fraction of r (r cancels)
    if (PASSINDEX == 0) {
        float prev = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;
        float dt = clamp(TIMEDELTA, 0.0, 0.1);
        float v = prev + dt * flow * abs(flow) * 0.6 / spNow;
        gl_FragColor = vec4(fract(v), 0.0, 0.0, 1.0);
        return;
    }
    gPh = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;                // LIVE composition aspect
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    float n = floor(sides + 0.5);
    float w = 0.0012 + soft * 0.06;                         // Soft: edge width
    float m = 0.04;

    // containment: circumradius + outline + outer glow + shadow + softness + the perspective swell of Spin stay inside the frame
    float room = min(hf2.x, hf2.y) - m;
    float swell = 1.25;
    float ow = outline * 0.06;                              // Outline: stroke width, 0 = none
    float gw = oglow * 0.12;                                // Outer Glow reach
    vec2 L0 = vec2(cos(sun * 2.0 * PI), sin(sun * 2.0 * PI));
    float shLen = shadow * 0.14, shSoft = 0.004 + shadow * 0.03;   // Shadow: cast away from the sun
    float reach = max(max(ow, gw), shLen + shSoft) + w;
    float r = (mix(0.02, room, sizev) - reach) / swell;
    r = max(r, 0.01);
    float bound = r * swell + reach;
    vec2 c = (vec2(px, py) - 0.5) * 2.0 * max(hf2 - bound - m, vec2(0.0));
    vec2 q = uv - c;

    vec3 pm = spPlane(q, spin * 2.0 * PI, 1.8);            // Spin: perspective plane tumble
    float ok = pm.z;
    q = pm.xy;
    float a = turn * 2.0 * PI; q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q;
    gr2 = r; gn2 = n; gw2 = w; gL2 = L0;

    float d = spD(q);
    float fill = spMask(d, w) * ok;                                                   // the shape
    float line = (outline > 0.001) ? spMask(d - ow, w) * ok : 0.0;                    // Stroke: black, around it

    float tone = spTone(q);

    // ── COLOR: palette on the tone (shadow excluded) ──
    vec3 body = vec3(tone);
    if (colorm == 1) {                                  // normal map of the styled HEIGHT (unlit geometry): every style shapes it, the sun does not
        float hs = max(r * 0.012, 0.0015);
        vec2 dh = vec2(spHeight(q + vec2(hs, 0.0)) - spHeight(q - vec2(hs, 0.0)), spHeight(q + vec2(0.0, hs)) - spHeight(q - vec2(0.0, hs))) / (2.0 * hs);
        vec3 nm = normalize(vec3(-dh, 1.0));
        body = nm * 0.5 + 0.5;
    }
    // Loop stacked on the base, PER CHANNEL (a ColourLoop over the render): gray loops as before, normal keeps its directions
    if (wet > 0.001) {
        vec3 looped = 0.5 + 0.5 * cos(2.0 * PI * (body * loopv + hue + vec3(rOff, gOff, bOff)));
        body = mix(body, looped, wet);
    }

    // ── SHADOW: the silhouette cast away from the sun, black, alpha only ──
    float sh = 0.0;
    if (shadow > 0.001) {
        vec2 qs = q + L0 * shLen;
        float ds = spD(qs);
        sh = (1.0 - smoothstep(-shSoft, shSoft, ds)) * ok * shadow * 0.7;
    }

    // Outer Glow: white, outside the shape, its own alpha
    float glow = (oglow > 0.001) ? exp(-max(d, 0.0) / (gw * 0.4 + 0.0005)) * oglow * (1.0 - fill) : 0.0;

    float figA_ = max(max(fill, line), glow);
    vec3 col = body * fill + vec3(glow) * (1.0 - line);
    float alpha = figA_ + sh * (1.0 - figA_);
    col = col * figA_ / max(alpha, 0.0001);                  // shadow contributes black
    gl_FragColor = vec4(min(col, 1.0), alpha);
}
"""
print("wrote", emit("SP Atom Figure 2D", "SP Atom FIGURE 2D - Figure A / B / Morph over a 2D SDF catalog (disc, ring, capsule, polygon, star, cross); containment; Turn, Spin (perspective coin flip), Outline (black stroke), Soft; layer styles: Sun, Bevel, Emboss, Inner Shadow, Inner Glow, Outer Glow, Satin, Gradient, Contour + Flow, Shadow (black alpha); Color = Base gray/normal + Loop per channel (Wet/Loop/Hue/R/G/B). No drives.", IN_F2, BODY_F2, passes=[{"TARGET": "ph", "PERSISTENT": True, "FLOAT": True, "WIDTH": 1, "HEIGHT": 1}, {}]))

IN_GR = [
    {"NAME": "grain",   "LABEL": "Grain",   "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["film", "static", "dust", "lines"]},
    {"NAME": "amount",  "LABEL": "Amount",  "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",   "LABEL": "Size",    "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "flicker", "LABEL": "Flicker", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv",  "LABEL": "Level",   "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
]
BODY_GR = """
float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float spVal(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y); }
void main() {
    vec2 px = gl_FragCoord.xy;
    float frame = floor(TIME * (1.0 + flicker * 59.0));     // Flicker = how often the grain re-rolls
    float cell = 1.0 + sizev * 12.0;                         // Size = grain cell in pixels
    vec2 g = floor(px / cell) + frame * 7.31;
    float v;
    if (grain == 0) v = spVal(g * 0.7) * 0.6 + spN2(g) * 0.4;                          // film: clumpy
    else if (grain == 1) v = spN2(g);                                                    // static: white noise
    else if (grain == 2) v = (spN2(g) > 0.985 - amount * 0.1) ? 1.0 : 0.0;              // dust: sparse specks
    else { float col = floor(px.x / cell) + floor(frame * 0.3) * 3.0; v = (spN2(vec2(col, 1.0)) > 0.96) ? spVal(vec2(col, px.y * 0.02 + frame)) : 0.0; }  // lines: scratches
    v = clamp(v * amount + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
"""
print("wrote", emit("SP Atom Grain", "SP Atom GRAIN - film / static / dust / lines; Amount, Size (cell px), Flicker (re-roll rate), Level. Alpha = value. No drives.", IN_GR, BODY_GR))

IN_TX = [
    {"NAME": "tex",    "LABEL": "Texture", "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["scanlines", "halftone", "hatch", "weave"]},
    {"NAME": "count",  "LABEL": "Count",   "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "phasev", "LABEL": "Drift",   "TYPE": "float", "DEFAULT": 0.1, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "duty",   "LABEL": "Duty",    "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.05, "MAX": 0.95},
    {"NAME": "soft",   "LABEL": "Soft",    "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv", "LABEL": "Level",   "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
]
BODY_TX = """
float spBand(float x, float d, float s) { float g = abs(fract(x) - 0.5) * 2.0; return 1.0 - smoothstep(d - s, d + s, g); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy; float asp = RENDERSIZE.x / RENDERSIZE.y;
    float n = 8.0 + count * 232.0;                            // Count: lines across the frame
    float t = TIME * phasev * 2.0;
    float s = 0.01 + soft * 0.5, v;
    if (tex == 0) v = spBand(uv.y * n + t, duty, s);
    else if (tex == 1) { vec2 p = vec2(uv.x * asp, uv.y) * n * 0.5; p = mat2(0.7071, -0.7071, 0.7071, 0.7071) * p + t;
        v = 1.0 - smoothstep(duty * 0.5 - s * 0.3, duty * 0.5 + s * 0.3, length(fract(p) - 0.5)); }
    else if (tex == 2) { float a = (uv.x * asp + uv.y) * n * 0.5 + t, b = (uv.x * asp - uv.y) * n * 0.5 - t;
        v = max(spBand(a, duty * 0.6, s), spBand(b, duty * 0.6, s)); }
    else { vec2 p = vec2(uv.x * asp, uv.y) * n * 0.25; float over = mod(floor(p.x) + floor(p.y), 2.0);
        float bx = spBand(p.x + t * 0.1, duty, s), by = spBand(p.y - t * 0.1, duty, s);
        v = mix(bx * 0.55 + by * 0.45 * (1.0 - bx), by * 0.55 + bx * 0.45 * (1.0 - by), over); }
    v = clamp(v + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
"""
print("wrote", emit("SP Atom Texture", "SP Atom TEXTURE - scanlines / halftone / hatch / weave; Count, Drift, Duty, Soft, Level. Alpha = value. No drives.", IN_TX, BODY_TX))

IN_GL = [
    {"NAME": "glyph",   "LABEL": "Glyph",   "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["blocks", "runes", "matrix", "dots"]},
    {"NAME": "sizev",   "LABEL": "Size",    "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "density", "LABEL": "Density", "TYPE": "float", "DEFAULT": 0.6, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "weight",  "LABEL": "Weight",  "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "reveal",  "LABEL": "Reveal",  "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv",  "LABEL": "Level",   "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
]
BODY_GL = """
float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy; float asp = RENDERSIZE.x / RENDERSIZE.y;
    float cols = 60.0 - sizev * 52.0;                         // Size: 60 → 8 glyph columns
    vec2 grid = vec2(cols, floor(cols / asp / 1.4));         // glyph cells are 5x7-ish: taller than wide
    vec2 c = floor(uv * grid), f = fract(uv * grid);         // cell id, position inside the cell
    float tick = floor(TIME * (0.2 + reveal * 8.0));          // Reveal: how fast glyphs re-roll
    float id = spN2(c + tick * 0.37);                         // which glyph lives here now
    float on = (spN2(c * 1.7 + tick * 0.11) < density) ? 1.0 : 0.0;
    // 5x7 bitmap inside the cell with a 1-unit margin
    vec2 cell = f * vec2(7.0, 9.0) - vec2(1.0, 1.0);
    vec2 bit = floor(cell);
    float inside = (bit.x >= 0.0 && bit.x < 5.0 && bit.y >= 0.0 && bit.y < 7.0) ? 1.0 : 0.0;
    float bx = bit.x;
    if (glyph == 1) bx = min(bit.x, 4.0 - bit.x);             // runes: mirror-symmetric glyphs
    float b = spN2(vec2(bx, bit.y) + id * 97.0);
    float set = (b > 0.5) ? 1.0 : 0.0;
    if (glyph == 3) set = ((mod(bit.x, 2.0) == 0.0) && (mod(bit.y, 2.0) == 0.0) && b > 0.35) ? 1.0 : 0.0;   // dots: braille-like
    // Weight: pixel size inside its bit cell
    vec2 fb = fract(cell) - 0.5;
    float pix = 1.0 - smoothstep(0.25 + weight * 0.3, 0.3 + weight * 0.3, max(abs(fb.x), abs(fb.y)));
    float v = inside * set * pix * on;
    if (glyph == 2) {                                         // matrix: column rain, brightness trails down
        float speed = 0.5 + spN2(vec2(c.x, 3.0)) * 2.0;
        float head = fract(spN2(vec2(c.x, 9.0)) + TIME * (0.05 + reveal * 0.4) * speed);
        float dy = fract(head - c.y / grid.y);
        v *= smoothstep(0.6, 0.0, dy) * 1.2;
    }
    v = clamp(v + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
"""
print("wrote", emit("SP Atom Glyph", "SP Atom GLYPH - procedural glyph mass: blocks / runes / matrix / dots; Size, Density, Weight, Reveal, Level. Alpha = value. No drives.", IN_GL, BODY_GL))

if "--build" in sys.argv:
    for n in ["SP Atom Solid", "SP Atom Figure 2D", "SP Atom Grain", "SP Atom Texture", "SP Atom Glyph"]:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), n, "source"], check=True)
