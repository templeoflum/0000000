#!/usr/bin/env python3
"""make_1d.py — SP Atom 1D, the MVP: ONE interval on ONE axis, extruded across the frame.
Three knobs. Size (its one extent), Position (where on the axis), Angle (which axis).
Nothing else until we know what a 1D object even is on stage."""
import json, os, subprocess, sys

NAME = "SP Atom 1D"
INPUTS = [
    {"NAME": "lengthv","LABEL": "Length",  "TYPE": "float", "DEFAULT": 0.6, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "pos",   "LABEL": "Position 1", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "pos2",  "LABEL": "Position 2", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "angle", "LABEL": "Angle",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
#define PI 3.14159265
float smin(float a, float b, float k) { return -k * log(exp(-a / k) + exp(-b / k)); }   // soft minimum: no kinks, always ≤ the true min (safe)
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;                // LIVE composition aspect
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    float m = 0.04;
    vec2 lim = hf2 - m;
    float a = angle * 2.0 * PI;
    vec2 dir = vec2(cos(a), sin(a)), nrm = vec2(-dir.y, dir.x);   // the line's direction; across it there is nothing
    vec2 ad = abs(dir) + 1e-4, an = abs(nrm) + 1e-4;
    float k = 0.02;
    float px1 = 1.0 / RENDERSIZE.y;                          // the line is one pixel thin, anti-aliased
    float thick = px1 * 0.75;

    // Length: the one extent, contained at this angle (the pixel of thickness counted)
    float lmax = smin((lim.x - ad.x * thick) / an.x, (lim.y - ad.y * thick) / an.y, k);
    float len_ = mix(0.005, max(lmax, 0.005), lengthv);
    // Position 1: along the line; Position 2: across it — both inside what remains, rules bent on purpose
    vec2 box = an * len_ + ad * thick;
    vec2 room = max(lim - box, vec2(0.0));
    vec2 p = vec2(pos - 0.5, pos2 - 0.5) * 2.0;             // wanted offsets in (along, across), as fractions
    vec2 off = nrm * p.x + dir * p.y;                        // screen direction of the combined move (before scaling)
    float pl = max(length(p), 1e-5);
    vec2 ao = abs(off) / pl + 1e-5;                          // unit direction of the move
    float T = smin(room.x / ao.x, room.y / ao.y, k);         // how far the box may travel in that direction
    vec2 c = off * clamp(T, 0.0, 1e3) * min(1.0, 1.0 / pl); // fader throw scales the travel; the diagonal is clamped to the same limit
    vec2 q = uv - c;
    float along = dot(q, nrm), across = dot(q, dir);
    float v = (1.0 - smoothstep(len_ - px1, len_ + px1, abs(along))) * (1.0 - smoothstep(thick - px1, thick + px1, abs(across)));
    gl_FragColor = vec4(vec3(v), v);
}
"""
def emit():
    hdr = {"DESCRIPTION": "SP Atom 1D - MVP: one line, one pixel thin. Length, Position 1 (along), Position 2 (across), Angle. Never touches the frame at any angle. No drives.",
           "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), NAME, "source"], check=True)
