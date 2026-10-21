#!/usr/bin/env python3
"""make_sky.py — SP Atom Sky, MVP: the atmosphere in the open region above the horizon. Grounded in the
atmospheric-optics records: a horizon GLOW that fades upward (twilight arch), a BELT band (the Belt of Venus
over the Earth-shadow), and crepuscular RAYS converging on the sun's point on the horizon. Bright = present,
black = open — the sky stays open for feedback except where the atmosphere is. Horizon follows Tilt."""
import json, os, subprocess, sys

NAME = "SP Atom Sky"
INPUTS = [
    {"NAME": "horizon", "LABEL": "Horizon", "TYPE": "float", "DEFAULT": 0.5,  "MIN": 0.05, "MAX": 0.95},
    {"NAME": "tilt",    "LABEL": "Tilt",    "TYPE": "float", "DEFAULT": -1.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "sun",     "LABEL": "Sun",     "TYPE": "float", "DEFAULT": 0.5,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "glow",    "LABEL": "Glow",    "TYPE": "float", "DEFAULT": 0.4,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "belt",    "LABEL": "Belt",    "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rays",    "LABEL": "Rays",    "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
#define PI 3.14159265
float h1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float n1(float x) { float i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f); return mix(h1(i), h1(i + 1.0), f); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 sc = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float a = (tilt + 1.0) * PI; sc = mat2(cos(a), -sin(a), sin(a), cos(a)) * sc;   // the world rolls, the sky with it
    sc.y -= (horizon - 0.5);
    float up = sc.y;                                         // > 0 in the sky
    if (up <= 0.0) { gl_FragColor = vec4(0.0); return; }     // below the horizon: nothing (the ground's)
    // GLOW: the twilight arch — brightest at the horizon, fading upward over Glow's height
    float gh = 0.05 + glow * 0.6;
    float g = exp(-up / gh) * glow * 1.6;
    // BELT: the Earth-shadow (dark) hugging the horizon with the bright belt above it (10–20° in the real sky)
    float shadowH = 0.05 + belt * 0.05, beltH = shadowH + 0.08 + belt * 0.1;
    float earthShadow = 1.0 - smoothstep(shadowH - 0.02, shadowH + 0.02, up);
    float beltBand = smoothstep(shadowH, shadowH + 0.03, up) * (1.0 - smoothstep(beltH - 0.03, beltH + 0.03, up));
    float b = belt * (beltBand * 0.9 - earthShadow * 0.6);
    // RAYS: crepuscular — shafts radiating from the sun's point on the horizon, alternating light and shadow
    vec2 sunP = vec2((sun - 0.5) * asp * 1.4, 0.0);
    vec2 rel = sc - vec2(sunP.x, 0.0);
    float ang = atan(rel.y, rel.x);
    float shaft = n1(ang * 9.0) * n1(ang * 23.0 + 5.0);
    float r = rays * smoothstep(0.15, 0.6, shaft) * exp(-length(rel) * 1.2) * 1.2;
    float v = clamp(g + b + r, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);                         // bright = atmosphere present, black = open
}
"""
def emit():
    hdr = {"DESCRIPTION": "SP Atom Sky - MVP: the atmosphere above the horizon — Glow (twilight arch), Belt (Belt of Venus over the Earth-shadow), Rays (crepuscular, from the Sun's point). Horizon follows Tilt. Bright = present, black = open. No drives.",
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
