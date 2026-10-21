#!/usr/bin/env python3
"""make_probe.py — SP Probe: one dot/ring on black, the bed's probe clip.
Blank-generic on purpose: X/Y (position), Size, Hue (cyclic), Bright as SP slots;
plain Ring (0=disc, 1=thin ring) and Sat (0=gray — grayscale-first probing) faders."""
import sp_header as S

SLOTS = [("pX", "X"), ("pY", "Y"), ("pSize", "Size"), ("pHue", "Hue"), ("pBright", "Bright")]
inputs = list(S.ROOT)
inputs += S.slot("pX", "X", default=0.5, drive=True)
inputs += S.slot("pY", "Y", default=0.5, drive=True)
inputs += S.slot("pSize", "Size", default=0.35, drive=True)
inputs += S.slot("pHue", "Hue", default=0.0, drive=True, cyclic=True)
inputs += S.slot("pBright", "Bright", default=1.0)
inputs += [
    {"NAME": "ring", "LABEL": "Ring", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sat", "LABEL": "Sat", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]

body = f"""
void main() {{
    float H = TIME * heartRate;                 // pilot convention: heart in-shader; Wire-side later

    // ── smart params → signals in [0,1] ──
    float X  = {S.call("pX", 0)};      // position sway
    float Y  = {S.call("pY", 1)};
    float SZ = {S.call("pSize", 2)};   // dot radius
    float HU = {S.call("pHue", 3)};    // hue rotation (cyclic)
    float B  = {S.call("pBright", 4)}; // brightness

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    vec2 c = vec2((X - 0.5) * asp * 0.8, (Y - 0.5) * 0.8);
    float d = length(uv - c);
    float rad = 0.03 + SZ * 0.30;
    float e = 0.004 + rad * 0.06;                                  // soft edge
    float disc = smoothstep(rad, rad - e, d);
    float inner = rad * (0.9 * ring);
    float shape = disc * (1.0 - smoothstep(inner, inner - e, d));  // ring=0 → disc, ring→1 → thin ring

    vec3 col = 0.5 + 0.5 * cos(2.0 * SP_PI * (HU + vec3(0.0, -0.33, -0.67)));
    col = mix(vec3(1.0), col, sat);                                // sat 0 = white/gray probe
    gl_FragColor = vec4(col * shape * B, 1.0);
}}
"""

path = S.emit("SP Probe — one dot/ring on black. SMART PARAM v4.", "SP probe", inputs, body, "SP Probe", S.groups(SLOTS))
print("wrote", path)
