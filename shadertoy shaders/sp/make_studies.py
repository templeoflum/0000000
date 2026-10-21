#!/usr/bin/env python3
"""make_studies.py — dedicated feedback studies, one lesson per shader, judged layer-soloed.
Each study effect sits on a Feedback clip and INJECTS ITS OWN PROBE (small orbiting dot), so
soloing the study layer closes the loop on itself: solo = isolation.
  Study 1  SP Study Level — the energy budget alone: Gain x Floor on an identity loop.
           Learn: equilibrium vs gain, wash onset, trail death, the Win95 point (gain 1, floor 0)."""
import json, os

def emit(name, desc, inputs, body, passes=None):
    hdr = {"DESCRIPTION": desc, "CREDIT": "SP study", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": inputs}
    if passes: hdr["PASSES"] = passes
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + body
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{name}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{name}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{name}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{name}.sp.json", "w"))
    return f"{D}/{name}.fs"

IN1 = [
    {"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"},
    {"NAME": "gainv",  "LABEL": "Gain",   "TYPE": "float", "DEFAULT": 0.97, "MIN": 0.80, "MAX": 1.00},
    {"NAME": "floorv", "LABEL": "Floor",  "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.10},
    {"NAME": "keyv",   "LABEL": "Key",    "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.5},
    {"NAME": "softv",  "LABEL": "Soft",   "TYPE": "float", "DEFAULT": 0.15, "MIN": 0.0,  "MAX": 1.0},
    {"NAME": "curvev", "LABEL": "Curve",  "TYPE": "float", "DEFAULT": 1.0,  "MIN": 0.4,  "MAX": 2.5},
    {"NAME": "ceilv",  "LABEL": "Ceiling","TYPE": "float", "DEFAULT": 1.0,  "MIN": 0.5,  "MAX": 1.0},
    {"NAME": "liftv",  "LABEL": "Lift",   "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.10},
]

BODY1 = """
void main() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 uv = isf_FragNormCoord;

    // the loop: previous comp frame, untouched map (identity) — ONLY the level law applies.
    // no injected content: the loop feeds on whatever the comp gives it
    vec4 c = IMG_NORM_PIXEL(inputImage, uv);
    // per-pass level chain: linear stage -> nonlinear stage -> ceiling
    vec3 col = max(c.rgb * gainv - floorv, 0.0);           // linear stage: gain and floor
    col = pow(col, vec3(curvev));                          // Curve: iterated nonlinearity — <1 hold-then-collapse, >1 crush-mids
    col = min(col + liftv, vec3(ceilv));                   // Lift AFTER the curve — study finding: pre-curve it
                                                           // cancels against Floor exactly (net L-F); post-curve they are independent
    // Key: luma below the key is transparent, above opaque. Soft = edge width. Key 0 = solid.
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    float w = 0.005 + softv * 0.25;
    float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv - w * 0.5, keyv + w * 0.5, lum);
    gl_FragColor = vec4(col, a);
}
"""

print("wrote", emit("SP Study Level", "SP Study 1 LEVEL - energy budget alone: full level chain (gain/lift/floor/curve/ceiling/key/soft) on identity loop. Feeds on comp content only.", IN1, BODY1))


# ── Study 2: MAP — the per-pass spatial transform ────────────────────────────
IN2 = [
    {"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"},
    # the study
    {"NAME": "zoomv", "LABEL": "Zoom",     "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.80, "MAX": 1.20},
    {"NAME": "rotx",  "LABEL": "Rot X",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -360.0, "MAX": 360.0},
    {"NAME": "roty",  "LABEL": "Rot Y",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -360.0, "MAX": 360.0},
    {"NAME": "rotz",  "LABEL": "Rot Z",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -360.0, "MAX": 360.0},
    {"NAME": "dx",    "LABEL": "Drift X",  "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.02, "MAX": 0.02},
    {"NAME": "dy",    "LABEL": "Drift Y",  "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.02, "MAX": 0.02},
    {"NAME": "cx",    "LABEL": "Center X", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0,  "MAX": 1.0},
    {"NAME": "cy",    "LABEL": "Center Y", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0,  "MAX": 1.0},
    # the learned base (Study 1)
    {"NAME": "gainv",  "LABEL": "Gain",  "TYPE": "float", "DEFAULT": 0.97, "MIN": 0.80, "MAX": 1.00},
    {"NAME": "floorv", "LABEL": "Floor", "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.10},
    {"NAME": "keyv",   "LABEL": "Key",   "TYPE": "float", "DEFAULT": 0.0,  "MIN": 0.0,  "MAX": 0.5},
]

BODY2 = """
void main() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 ctr = vec2(cx, cy);
    vec2 q = (isf_FragNormCoord - ctr) * vec2(asp, 1.0);

    // MAP — one transform per pass. Rot Z spins in-plane; Rot X/Y tilt the sampling plane in
    // perspective (ray-plane intersection, same math as the figure's coin flip) — edge-on = vanish
    float ax = rotx * 0.017453293;
    float ay = roty * 0.017453293;
    float az = rotz * 0.017453293;
    vec3 e1 = vec3(cos(ay), 0.0, -sin(ay));
    vec3 e2 = vec3(sin(ay) * sin(ax), cos(ax), cos(ay) * sin(ax));
    vec3 n = cross(e1, e2);
    vec3 E = vec3(0.0, 0.0, 1.6);
    vec3 rd = vec3(q, 0.0) - E;
    float den = dot(n, rd);
    float ok = (abs(den) > 1e-5) ? 1.0 : 0.0;
    float t = -dot(n, E) / (den + ((den >= 0.0) ? 1e-6 : -1e-6));
    ok *= (t > 0.0) ? 1.0 : 0.0;
    vec3 H = E + t * rd;
    vec2 pq = vec2(dot(H, e1), dot(H, e2));

    float ca = cos(-az), sa = sin(-az);
    pq = mat2(ca, -sa, sa, ca) * pq / zoomv;
    pq.x /= asp;
    vec2 p = pq + ctr - vec2(dx, dy);

    // outside the frame there is no signal
    float inside = ok * ((p.x >= 0.0 && p.x <= 1.0 && p.y >= 0.0 && p.y <= 1.0) ? 1.0 : 0.0);
    vec4 c = IMG_NORM_PIXEL(inputImage, clamp(p, 0.0, 1.0)) * inside;

    // learned level base (Study 1): gain/floor in the loop, key at the mix
    vec3 col = max(c.rgb * gainv - floorv, 0.0);
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    float aa = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);
    gl_FragColor = vec4(col, c.a * aa);
}
"""

print("wrote", emit("SP Study Map", "SP Study 2 MAP - per-pass spatial transform: zoom, 3-axis rotation (Z in-plane, X/Y perspective), drift, center, over the learned level base.", IN2, BODY2))


# ── Study 3: DELAY v10 — two chained atlases: 192 full-res frames = 3.2s @60 ──
# 8x12 fits (8x15 fails to allocate); discard is dead (Wire clears pre-pass) -> copy-holds.
# histA holds frames for global slots 0-95, histB for 96-191. 4 samplers total.
IN3 = [
    {"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"},
    {"NAME": "delayv", "LABEL": "Delay", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.05, "MAX": 3.2},
]

PASSES3 = [
    {"TARGET": "cnt",   "PERSISTENT": True, "FLOAT": True, "WIDTH": 1, "HEIGHT": 1},
    {"TARGET": "histA", "PERSISTENT": True, "WIDTH": "$WIDTH*8", "HEIGHT": "$HEIGHT*12"},
    {"TARGET": "histB", "PERSISTENT": True, "WIDTH": "$WIDTH*8", "HEIGHT": "$HEIGHT*12"},
    {},
]

BODY3 = """
vec2 spTileUV(float slot96, vec2 uv) {
    return (vec2(mod(slot96, 8.0), floor(slot96 / 8.0)) + uv) / vec2(8.0, 12.0);
}
void main() {
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {
        vec4 prev = IMG_PIXEL(cnt, vec2(0.5, 0.5));
        float dt = clamp(TIMEDELTA, 0.001, 0.1);
        float sdt = (prev.g <= 0.0) ? dt : mix(prev.g, dt, 0.05);
        gl_FragColor = vec4(mod(prev.r + 1.0, 192.0), sdt, 1.0, 1.0);
    } else if (PASSINDEX == 1) {
        float g = IMG_PIXEL(cnt, vec2(0.5, 0.5)).r;
        vec2 t = floor(uv * vec2(8.0, 12.0));
        float idx = t.y * 8.0 + t.x;
        float activeA = clamp(floor(delayv / max(IMG_PIXEL(cnt, vec2(0.5, 0.5)).g, 0.001) + 0.5), 1.0, 191.0) + 12.0;
        float distA = mod(g - idx + 192.0, 192.0);
        if (g < 95.5 && abs(idx - g) < 0.5) {
            gl_FragColor = IMG_NORM_PIXEL(inputImage, fract(uv * vec2(8.0, 12.0)));
        } else if (distA <= activeA) {
            gl_FragColor = IMG_NORM_PIXEL(histA, uv);   // hold only the window in use
        } else {
            gl_FragColor = vec4(0.0);                   // beyond the knob: no history kept
        }
    } else if (PASSINDEX == 2) {
        float g = IMG_PIXEL(cnt, vec2(0.5, 0.5)).r;
        vec2 t = floor(uv * vec2(8.0, 12.0));
        float idx = t.y * 8.0 + t.x;
        float activeB = clamp(floor(delayv / max(IMG_PIXEL(cnt, vec2(0.5, 0.5)).g, 0.001) + 0.5), 1.0, 191.0) + 12.0;
        float distB = mod(g - (idx + 96.0) + 192.0, 192.0);
        if (g >= 95.5 && abs(idx - (g - 96.0)) < 0.5) {
            gl_FragColor = IMG_NORM_PIXEL(inputImage, fract(uv * vec2(8.0, 12.0)));
        } else if (distB <= activeB) {
            gl_FragColor = IMG_NORM_PIXEL(histB, uv);   // hold only the window in use
        } else {
            gl_FragColor = vec4(0.0);                   // beyond the knob: no history kept
        }
    } else {
        vec4 c0 = IMG_PIXEL(cnt, vec2(0.5, 0.5));
        float N = clamp(floor(delayv / c0.g + 0.5), 1.0, 191.0);
        float slot = mod(c0.r - N + 192.0, 192.0);
        gl_FragColor = (slot < 95.5)
            ? IMG_NORM_PIXEL(histA, spTileUV(slot, uv))
            : IMG_NORM_PIXEL(histB, spTileUV(slot - 96.0, uv));
    }
}
"""

print("wrote", emit("SP Study Delay", "SP Study 3 DELAY v10 - 192-frame full-resolution line (3.2s @60fps), two chained atlases. Delay moves only the gap between start points; replay rate never changes.", IN3, BODY3, PASSES3))
