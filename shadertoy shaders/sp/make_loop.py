#!/usr/bin/env python3
"""make_loop.py — SP Loop: the bed's probe. A texture input (route it like the native
Feedback source) transformed per pass by SP slots — the motion-preset columns of the old
machine (rotate/scale/move) as ONE performable SP clip.
Slots: Zoom(0) · Rot(1) · X(2) · Y(3) · Decay(4). All sway (lo..hi), none cyclic."""
import sp_header as S

S.CYC.clear()
SLOTS = [("lZoom", "Zoom"), ("lRot", "Rot"), ("lX", "X"), ("lY", "Y"), ("lDecay", "Decay")]
inputs = [{"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"}]
inputs += list(S.ROOT)
inputs += S.slot("lZoom", "Zoom", default=0.5, drive=True)
inputs += S.slot("lRot", "Rot", default=0.5, drive=True)
inputs += S.slot("lX", "X", default=0.5)
inputs += S.slot("lY", "Y", default=0.5)
inputs += S.slot("lDecay", "Decay", default=1.0)

body = f"""
void main() {{
    float H = TIME * heartRate;

    float Z = {S.call("lZoom", 0)};    // per-pass zoom — the fundamental (Scale In/Out family)
    float R = {S.call("lRot", 1)};     // per-pass rotation (Rotate Z family)
    float X = {S.call("lX", 2)};       // per-pass push (Move family)
    float Y = {S.call("lY", 3)};
    float D = {S.call("lDecay", 4)};   // trail persistence

    vec2 uv = isf_FragNormCoord - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    float s = 1.0 / (1.0 + (Z - 0.5) * 0.35);
    float a = (R - 0.5) * 0.35;
    mat2 M = mat2(cos(a), -sin(a), sin(a), cos(a));
    vec2 p = M * (uv * s) - vec2(X - 0.5, Y - 0.5) * 0.12;
    p.x /= asp;
    p += 0.5;

    vec4 c = IMG_NORM_PIXEL(inputImage, p);
    gl_FragColor = vec4(c.rgb * (0.7 + 0.3 * D), c.a);
}}
"""

print("wrote", S.emit("SP Loop — feedback motion probe: routed input transformed per pass. SMART PARAM v4.", "SP probe", inputs, body, "SP Loop", S.groups(SLOTS)))
