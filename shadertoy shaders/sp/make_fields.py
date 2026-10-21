#!/usr/bin/env python3
"""make_fields.py — field ATOMS (2026-09-02, "start small, get it locked, then expand").
Pure operators: NO slot machinery, NO drives, plain emit, judged layer-soloed. Harness later.
Field convention kept from SP Field: grayscale, alpha = value (dark = open — feedback lives in the gaps).
  SP Field Outdoor — layered horizon: parallax silhouettes over a sky. Ground picker = flavor.
"""
import json, os, subprocess, sys

def emit(name, desc, inputs, body):
    hdr = {"DESCRIPTION": desc, "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": inputs}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + body
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{name}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{name}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{name}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{name}.sp.json", "w"))
    return f"{D}/{name}.fs"

IN_OUT = [
    {"NAME": "ground",  "LABEL": "Ground",   "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["ridges", "dunes", "sea", "sky"]},
    {"NAME": "horizon", "LABEL": "Horizon",  "TYPE": "float", "DEFAULT": 0.45, "MIN": 0.1, "MAX": 0.9},
    {"NAME": "scalev",  "LABEL": "Scale",    "TYPE": "float", "DEFAULT": 0.4,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "driftv",  "LABEL": "Drift",    "TYPE": "float", "DEFAULT": 0.2,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "hazev",   "LABEL": "Haze",     "TYPE": "float", "DEFAULT": 0.5,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "contrast","LABEL": "Contrast", "TYPE": "float", "DEFAULT": 0.5,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv",  "LABEL": "Level",    "TYPE": "float", "DEFAULT": 0.0,  "MIN": -0.5, "MAX": 0.5},
]

BODY_OUT = """
float spN1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float spVal(vec2 p) {
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y);
}
float spFbm(vec2 p) {                                     // 4 octaves, plain
    return 0.5 * spVal(p) + 0.25 * spVal(p * 2.03 + 7.7) + 0.125 * spVal(p * 4.01 + 13.1) + 0.0625 * spVal(p * 8.07 + 29.3);
}
float spRidge(vec2 p) {                                   // ridged: 1 - |2n-1|, stacked
    float r = 0.0, a = 0.5;
    for (int k = 0; k < 4; k++) { r += a * (1.0 - abs(2.0 * spVal(p) - 1.0)); p = p * 2.03 + 11.3; a *= 0.5; }
    return r;
}
// height of silhouette layer k at horizontal x (0..1 frame units), scrolled by t
float spHeight(int g, float x, float t, float k) {
    float f = 1.5 + scalev * 6.0;                          // spatial frequency, the fundamental
    float sx = x * f * (0.6 + 0.35 * k) + t * (0.3 + 0.5 * k) + k * 17.0;   // nearer layers move faster (parallax)
    if (g == 0) return spRidge(vec2(sx, k * 3.1)) * 0.5;                          // ridges: sharp peaks
    if (g == 1) return 0.5 + 0.5 * sin(sx * 2.0 + spVal(vec2(sx * 0.5, k)) * 3.0) * 0.5 + 0.15 * spVal(vec2(sx * 3.0, k));  // dunes: long soft waves
    if (g == 2) return 0.5 + 0.06 * sin(sx * 9.0 + t * 3.0 + k) + 0.05 * spVal(vec2(sx * 6.0, t * 0.7 + k));   // sea: flat, rippling
    return 0.0;                                                                   // sky: no ground silhouettes
}
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float t = TIME * driftv * 0.25;
    float con = 0.2 + contrast * 2.8;

    // SKY — gradient up from the horizon, with cloud fbm that only the sky flavor lets through fully
    float sy = clamp((uv.y - horizon) / max(1.0 - horizon, 0.001), 0.0, 1.0);
    float cloud = spFbm(vec2(uv.x * (2.0 + scalev * 6.0) + t * 0.6, uv.y * 3.0 + t * 0.1));
    float cloudAmt = (ground == 3) ? 1.0 : 0.25;
    float sky = mix(0.55, 0.25, sy) + (cloud - 0.5) * cloudAmt * 0.5;
    sky *= smoothstep(0.0, 0.05, uv.y - horizon + 0.02);  // nothing below the horizon

    // GROUND — 4 silhouette layers far→near; near = darker, far = hazed toward the sky value
    float v = sky;
    for (int k = 0; k < 4; k++) {
        float fk = float(k);
        float depthAmt = (fk + 1.0) / 4.0;                 // 0.25 far … 1.0 near
        float h = spHeight(ground, uv.x, t, fk);
        float amp = (ground == 2) ? 0.05 : 0.12 + 0.1 * fk; // sea stays flat
        float yLine = horizon - fk * 0.09 * (ground == 2 ? 0.6 : 1.0) + h * amp;
        float edge = smoothstep(yLine + 0.004, yLine - 0.004, uv.y);   // 1 below the line
        float shade = mix(0.18, 0.05, depthAmt);           // near = darkest
        float hazed = mix(shade, sky, hazev * (1.0 - depthAmt));   // far layers fade into sky
        v = mix(v, hazed, edge);
    }
    if (ground == 3) v = sky;                               // sky flavor: the field IS the sky

    v = clamp((v - 0.35) * con + 0.35 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);                        // alpha ground: dark = open
}
"""
print("wrote", emit("SP Field Outdoor",
    "SP Field OUTDOOR atom - layered horizon: parallax silhouettes (ridges/dunes/sea) or sky over a gradient. Grayscale, alpha = value. No drives.", IN_OUT, BODY_OUT))

if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), "SP Field Outdoor", "source"], check=True)

# ── INDOOR: one-point-perspective room. Room picker = flavor. ───────────────
IN_IN = [
    {"NAME": "room",    "LABEL": "Room",     "TYPE": "long",  "DEFAULT": 1, "VALUES": [0, 1, 2, 3], "LABELS": ["grid", "corridor", "tiles", "blinds"]},
    {"NAME": "horizon", "LABEL": "Horizon",  "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.2, "MAX": 0.8},
    {"NAME": "vx",      "LABEL": "Vanish X", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.2, "MAX": 0.8},
    {"NAME": "scalev",  "LABEL": "Scale",    "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "driftv",  "LABEL": "Drift",    "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "hazev",   "LABEL": "Haze",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "contrast","LABEL": "Contrast", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv",  "LABEL": "Level",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
]
BODY_IN = """
float spLine(float x, float w) { float g = abs(fract(x) - 0.5); return 1.0 - smoothstep(w, w + 0.02, 0.5 - g); }   // 1 on the line
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    float t = TIME * driftv * 0.6;
    float f = 1.0 + scalev * 5.0;
    float con = 0.2 + contrast * 2.8;
    float v = 0.0;

    if (room == 3) {                                        // BLINDS: light through slats, no perspective
        float y = uv.y * (4.0 + scalev * 20.0) + t;
        float slat = smoothstep(0.45, 0.55, abs(fract(y) - 0.5) * 2.0);
        float sweep = 0.5 + 0.5 * sin(uv.x * 3.0 - t * 0.5);
        v = mix(0.08, 0.6, slat) * (0.6 + 0.4 * sweep);
    } else {
        vec2 d = (uv - vec2(vx, horizon)) * vec2(asp, 1.0); // direction from the vanishing point
        bool floorCeil = abs(d.y) >= abs(d.x);
        float z = 1.0 / max(floorCeil ? abs(d.y) : abs(d.x), 0.002);    // depth along the face
        float u = (floorCeil ? d.x : d.y) * z;              // lateral coordinate on the face
        float depthFade = clamp(z * 0.12, 0.0, 1.0);
        float base = 0.08;
        float lines = 0.0;
        if (room == 0) {                                    // GRID: floor and ceiling ruled, walls dark
            if (floorCeil) lines = max(spLine(u * f * 0.8, 0.04), spLine(z * f * 0.25 + t, 0.04));
        } else if (room == 1) {                             // CORRIDOR: every face ruled, the box reads
            lines = max(spLine(u * f * 0.8, 0.03), spLine(z * f * 0.25 + t, 0.03));
            base = floorCeil ? 0.10 : 0.06;
        } else {                                            // TILES: checker floor, faint ceiling
            if (floorCeil && d.y < 0.0) {
                float c = mod(floor(u * f * 0.8) + floor(z * f * 0.25 + t), 2.0);
                lines = mix(0.15, 0.85, c);
            } else if (floorCeil) lines = 0.12;
        }
        v = base + lines * 0.6;
        v = mix(v, 0.3, hazev * depthFade);                 // far = hazed to mid
    }
    v = clamp((v - 0.35) * con + 0.35 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
"""
print("wrote", emit("SP Field Indoor",
    "SP Field INDOOR atom - one-point-perspective room: grid / corridor / tiles / blinds. Grayscale, alpha = value. No drives.", IN_IN, BODY_IN))

# ── ABSTRACT: pure math fields. Field picker = flavor. ───────────────────────
IN_AB = [
    {"NAME": "field",   "LABEL": "Field",    "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["interference", "flow", "cells", "bands"]},
    {"NAME": "scalev",  "LABEL": "Scale",    "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "driftv",  "LABEL": "Drift",    "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "warpv",   "LABEL": "Warp",     "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "contrast","LABEL": "Contrast", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "levelv",  "LABEL": "Level",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
]
BODY_AB = """
float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec2  spN22(vec2 p) { return vec2(spN2(p), spN2(p + 19.19)); }
float spVal(vec2 p) {
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y);
}
float spFbm(vec2 p) { return 0.5 * spVal(p) + 0.25 * spVal(p * 2.03 + 7.7) + 0.125 * spVal(p * 4.01 + 13.1) + 0.0625 * spVal(p * 8.07 + 29.3); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    uv.x *= RENDERSIZE.x / RENDERSIZE.y;
    float t = TIME * driftv;
    float f = 1.0 + scalev * 9.0;
    float con = 0.2 + contrast * 2.8;
    float v = 0.5;
    if (field == 0) {                                       // INTERFERENCE: five sources, summed waves
        float s = 0.0;
        for (int i = 0; i < 5; i++) {
            float fi = float(i);
            vec2 src = (spN22(vec2(fi * 3.7, 1.3)) - 0.5) * 1.6 + 0.15 * vec2(cos(t * 0.3 + fi), sin(t * 0.23 + fi * 1.7)) * warpv * 3.0;
            s += sin(length(uv - src) * f * 8.0 - t * 3.0);
        }
        v = 0.5 + 0.5 * (s / 5.0);
    } else if (field == 1) {                                // FLOW: domain-warped fbm
        vec2 p = uv * f;
        vec2 q = vec2(spFbm(p + t * 0.3), spFbm(p + vec2(5.2, 1.3) + t * 0.2));
        vec2 r = vec2(spFbm(p + warpv * 4.0 * q + vec2(1.7, 9.2)), spFbm(p + warpv * 4.0 * q + vec2(8.3, 2.8)));
        v = spFbm(p + warpv * 4.0 * r);
    } else if (field == 2) {                                // CELLS: voronoi distance
        vec2 p = uv * f * 1.5; vec2 ip = floor(p), fp = fract(p);
        float m = 8.0;
        for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = spN22(ip + g); o = 0.5 + 0.5 * sin(t + 6.2831 * o) * (0.3 + warpv * 0.7);
            m = min(m, length(g + o - fp));
        }
        v = m;
    } else {                                                // BANDS: rotating sine bands
        float a = warpv * 3.14159 + t * 0.1;
        v = 0.5 + 0.5 * sin((uv.x * cos(a) + uv.y * sin(a)) * f * 6.0 + t * 2.0);
    }
    v = clamp((v - 0.5) * con + 0.5 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
"""
print("wrote", emit("SP Field Abstract",
    "SP Field ABSTRACT atom - pure math fields: interference / flow / cells / bands. Grayscale, alpha = value. No drives.", IN_AB, BODY_AB))

if "--build" in sys.argv:
    for n in ["SP Field Indoor", "SP Field Abstract"]:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), n, "source"], check=True)
