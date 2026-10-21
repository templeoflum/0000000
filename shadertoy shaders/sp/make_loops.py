#!/usr/bin/env python3
"""make_loops.py — the three bed instruments, one per flavor. Wire EFFECT patches for the
native Feedback tap (clip = Feedback source + this effect). Each flavor owns only its moves:
SP Loop Shape : Zoom(0) · Rot(1) · Fold(2, mirror-fold) · Decay(3)   — the fold, top of bed
SP Loop Flow  : Push(0) · Direction(1, cyclic) · Wobble(2) · Shear(3) — the push, middle
SP Loop Color : Hue(0, cyclic, per-pass) · Invert(1) · Sat(2) · Bleed(3) — chroma, bottom seed"""
import sp_header as S

IMG = [{"NAME": "inputImage", "LABEL": "Input", "TYPE": "image"}]

# ── SP Loop Shape ────────────────────────────────────────────────────────────
S.CYC.clear()
SH = [("sZoom", "Zoom"), ("sRot", "Rot"), ("sFold", "Fold"), ("sDecay", "Decay")]
sin_ = IMG + list(S.ROOT)
sin_ += S.slot("sZoom", "Zoom", default=0.5, drive=True)
sin_ += S.slot("sRot", "Rot", default=0.5, drive=True)
sin_ += S.slot("sFold", "Fold", default=0.0)
sin_ += S.slot("sDecay", "Decay", default=1.0)

shape_body = f"""
void main() {{
    float H = TIME * heartRate;

    float Z = {S.call("sZoom", 0)};    // per-pass zoom — the fundamental (Scale family)
    float R = {S.call("sRot", 1)};     // per-pass rotation (Rotate family)
    float F = {S.call("sFold", 2)};    // 0 off → 1 full mirror-fold
    float D = {S.call("sDecay", 3)};   // trail persistence — the bed's last word

    vec2 uv = isf_FragNormCoord - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    float s = 1.0 / (1.0 + (Z - 0.5) * 0.35);
    float a = (R - 0.5) * 0.35;
    vec2 p = mat2(cos(a), -sin(a), sin(a), cos(a)) * (uv * s);
    p = mix(p, abs(p), F);                       // the fold: quadrant mirror, blendable
    p.x /= asp;
    vec4 c = IMG_NORM_PIXEL(inputImage, p + 0.5);
    gl_FragColor = vec4(c.rgb * (0.7 + 0.3 * D), c.a);
}}
"""
print("wrote", S.emit("SP Loop Shape — the fold: zoom/rotate/mirror per pass. SMART PARAM v4.", "SP probe", sin_, shape_body, "SP Loop Shape", S.groups(SH)))

# ── SP Loop Flow ─────────────────────────────────────────────────────────────
S.CYC.clear()
FL = [("wPush", "Push"), ("wDir", "Direction"), ("wWob", "Wobble"), ("wShear", "Shear")]
fin = IMG + list(S.ROOT)
fin += S.slot("wPush", "Push", default=0.3, drive=True)
fin += S.slot("wDir", "Direction", default=0.25, drive=False, cyclic=True)
fin += S.slot("wWob", "Wobble", default=0.5)
fin += S.slot("wShear", "Shear", default=0.5)

flow_body = f"""
void main() {{
    float H = TIME * heartRate;

    float P = {S.call("wPush", 0)};    // push amount — the fundamental
    float A = {S.call("wDir", 1)};     // cyclic angle — one slot = all the old direction columns
    float W = {S.call("wWob", 2)};     // perpendicular offset (drive = wobble)
    float E = {S.call("wShear", 3)};   // shear across the push

    vec2 uv = isf_FragNormCoord - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    float ang = A * 2.0 * SP_PI;
    vec2 dir = vec2(cos(ang), sin(ang));
    vec2 perp = vec2(-dir.y, dir.x);
    vec2 p = uv - dir * P * 0.12 - perp * (W - 0.5) * 0.06;
    p += perp * dot(uv, dir) * (E - 0.5) * 0.4;   // shear along the push axis
    p.x /= asp;
    gl_FragColor = IMG_NORM_PIXEL(inputImage, p + 0.5);
}}
"""
print("wrote", S.emit("SP Loop Flow — the push: direction/wobble/shear per pass. SMART PARAM v4.", "SP probe", fin, flow_body, "SP Loop Flow", S.groups(FL)))

# ── SP Loop Color ────────────────────────────────────────────────────────────
S.CYC.clear()
CO = [("cHue", "Hue"), ("cInv", "Invert"), ("cSat", "Sat"), ("cBleed", "Bleed")]
cin = IMG + list(S.ROOT)
cin += S.slot("cHue", "Hue", default=0.0, drive=True, cyclic=True)
cin += S.slot("cInv", "Invert", default=0.0)
cin += S.slot("cSat", "Sat", default=0.5)
cin += S.slot("cBleed", "Bleed", default=0.0)

color_body = f"""
void main() {{
    float H = TIME * heartRate;

    float HU = {S.call("cHue", 0)};    // palette phase — the fundamental (cyclic, per-pass)
    float IV = {S.call("cInv", 1)};    // continuous invert crossfade
    float SA = {S.call("cSat", 2)};    // tint strength: 0 grey -> 1 full chroma
    float BL = {S.call("cBleed", 3)};  // soft spread per pass

    vec2 uv = isf_FragNormCoord;
    vec4 c = IMG_NORM_PIXEL(inputImage, uv);
    if (BL > 0.001) {{
        float r = BL * 0.006;
        vec3 b = IMG_NORM_PIXEL(inputImage, uv + vec2(r, 0)).rgb + IMG_NORM_PIXEL(inputImage, uv - vec2(r, 0)).rgb
               + IMG_NORM_PIXEL(inputImage, uv + vec2(0, r)).rgb + IMG_NORM_PIXEL(inputImage, uv - vec2(0, r)).rgb;
        c.rgb = mix(c.rgb, b * 0.25, min(1.0, BL * 1.2));
    }}
    float lum = dot(c.rgb, vec3(0.299, 0.587, 0.114));
    // inject, don't adjust: luma through a cosine palette — grey in, color out. HU picks the
    // ramp phase; re-derived from luma every pass, so the loop tints without running away.
    // the color clock runs 4x: a bed hue is a FAST element — one slot phase = four palette laps
    vec3 chroma = 0.5 + 0.5 * cos(2.0 * SP_PI * (HU * 4.0 + lum * 0.45) + vec3(0.0, -2.094, -4.188));
    // THE BED IS NEVER WHITE: cap loop luminance in the vivid range — at full light the
    // palette would normalize and clamp straight back to white; at 0.75 it stays chroma.
    // Side effect: loop gain tops out at 0.75 — the feedback self-stabilizes.
    float l2 = min(lum, 1.0) * 0.75;
    vec3 tint = chroma * (l2 / max(dot(chroma, vec3(0.299, 0.587, 0.114)), 1e-3));
    vec3 col = mix(vec3(l2), min(tint, 1.0), SA);
    // per-pass leak toward true black: residue decays instead of hanging as wash
    col = max(col - 0.010, 0.0);
    col = mix(col, 1.0 - col, IV);
    // a bed is not a blanket: alpha keyed to source light — black is glass
    float a = c.a * smoothstep(0.02, 0.22, lum);
    gl_FragColor = vec4(col, a);
}}
"""
print("wrote", S.emit("SP Loop Color — chroma per pass: hue/invert/sat/bleed. SMART PARAM v4.", "SP probe", cin, color_body, "SP Loop Color", S.groups(CO)))
