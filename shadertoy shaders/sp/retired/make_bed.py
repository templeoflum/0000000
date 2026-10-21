#!/usr/bin/env python3
"""make_bed.py — SP Feedback: ONE channel strip for the feedback chain, instanced at each
of the three insertion points. No slot machinery, no drives — every control is a per-pass
amount, and because the chain iterates, constant settings ARE motion.
  MAP     Zoom ×/pass (<1 recede, 1 stamp, >1 approach) · Center X/Y · Rotate °/pass · Drift X/Y
  FOLD    Mirror: off / x / xy / radial-6   (is or isn't)
  TEXTURE Diffuse (blur) + Etch (sharpen) — BOTH live at once; their competition grows pattern
  COLOR   Hue Step °/pass · Sat ×/pass · Invert on/off (a flavor value, not a sweep)
  LEVEL   Gain ×/pass · Floor −/pass  (gain 1 + floor 0 = Win95 stamp; floor >0 = trails die
          to true black)  — alpha = signal presence at the tap: no signal, no pixel."""
import sp_header as S

INPUTS = [
    {"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"},
    # MAP
    {"NAME": "zoomv", "LABEL": "Zoom", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.9, "MAX": 1.1},
    {"NAME": "cx", "LABEL": "Center X", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "cy", "LABEL": "Center Y", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rotv", "LABEL": "Rotate", "TYPE": "float", "DEFAULT": 0.0, "MIN": -10.0, "MAX": 10.0},
    {"NAME": "dx", "LABEL": "Drift X", "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.01, "MAX": 0.01},
    {"NAME": "dy", "LABEL": "Drift Y", "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.01, "MAX": 0.01},
    # FOLD
    {"NAME": "mir", "LABEL": "Mirror", "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["off", "x", "xy", "radial"]},
    # TEXTURE
    {"NAME": "dif", "LABEL": "Diffuse", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "etch", "LABEL": "Etch", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 2.0},
    # COLOR
    {"NAME": "hue", "LABEL": "Hue Step", "TYPE": "float", "DEFAULT": 0.0, "MIN": -30.0, "MAX": 30.0},
    {"NAME": "satv", "LABEL": "Sat", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.5, "MAX": 1.5},
    {"NAME": "inv", "LABEL": "Invert", "TYPE": "bool", "DEFAULT": False},
    # LEVEL
    {"NAME": "gainv", "LABEL": "Gain", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.85, "MAX": 1.05},
    {"NAME": "floorv", "LABEL": "Floor", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 0.05},
]

body = """
vec3 spHueR(vec3 c, float a) {
    const vec3 k = vec3(0.57735);
    return c * cos(a) + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - cos(a));
}
void main() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 ctr = vec2(cx, cy);
    vec2 q = isf_FragNormCoord - ctr;
    q.x *= asp;

    // FOLD — on the output frame, before the map
    if (mir == 1) q.x = abs(q.x);
    else if (mir == 2) q = abs(q);
    else if (mir == 3) {
        float an = atan(q.y, q.x); float rr = length(q);
        an = abs(mod(an, 1.0471976) - 0.5235988);          // 6-fold sector
        q = vec2(cos(an), sin(an)) * rr;
    }

    // MAP — inverse per-pass transform: this frame shows the tap zoomed/rotated/drifted once
    float a = -rotv * 0.017453293;
    q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q / zoomv;
    q.x /= asp;
    vec2 p = q + ctr - vec2(dx, dy);

    float inside = (p.x >= 0.0 && p.x <= 1.0 && p.y >= 0.0 && p.y <= 1.0) ? 1.0 : 0.0;
    vec2 pc = clamp(p, 0.0, 1.0);
    vec4 c = IMG_NORM_PIXEL(inputImage, pc) * inside;

    // TEXTURE — one blur kernel serves both: Diffuse spreads toward it, Etch fights against it
    float r = 0.0015 + dif * 0.010;
    vec3 b = (IMG_NORM_PIXEL(inputImage, clamp(p + vec2( r, 0.0), 0.0, 1.0)).rgb
            + IMG_NORM_PIXEL(inputImage, clamp(p + vec2(-r, 0.0), 0.0, 1.0)).rgb
            + IMG_NORM_PIXEL(inputImage, clamp(p + vec2(0.0,  r), 0.0, 1.0)).rgb
            + IMG_NORM_PIXEL(inputImage, clamp(p + vec2(0.0, -r), 0.0, 1.0)).rgb) * 0.25 * inside;
    vec3 col = mix(c.rgb, b, dif) + (c.rgb - b) * etch;
    col = clamp(col, 0.0, 1.0);

    // presence: does signal exist here at the tap — decided before color ops, so Invert
    // recolors what exists instead of painting where nothing is
    float pres = smoothstep(0.0, 0.04, dot(col, vec3(0.299, 0.587, 0.114)));

    // COLOR
    if (abs(hue) > 0.01) col = clamp(spHueR(col, hue * 0.017453293), 0.0, 1.0);
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    col = clamp(mix(vec3(lum), col, satv), 0.0, 1.0);
    if (inv) col = vec3(1.0) - col;

    // LEVEL
    col = max(col * gainv - floorv, 0.0);
    float post = dot(col, vec3(0.299, 0.587, 0.114));

    gl_FragColor = vec4(col, c.a * pres * smoothstep(0.0, 0.02, post));
}
"""

# plain emit — NO sp.glsl slot block: the strip has no drive machinery, so no slot uniforms
import json, os
hdr = {"DESCRIPTION": "SP Feedback — one channel strip per insertion point: MAP/FOLD/TEXTURE/COLOR/LEVEL, all per-pass. v1.",
       "CREDIT": "SP probe", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS}
out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + body
D = os.path.expanduser("~/Documents/Resolume Wire/Patches/SP Feedback/Resource"); os.makedirs(D, exist_ok=True)
open(f"{D}/SP Feedback.fs", "w").write(out)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SP Feedback.fs"), "w").write(out)
json.dump({}, open(f"{D}/SP Feedback.sp.json", "w"))
print("wrote", f"{D}/SP Feedback.fs")
