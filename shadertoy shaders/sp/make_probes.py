#!/usr/bin/env python3
"""make_probes.py — the two MVP probes, pilot standard, minimal on purpose.
SP Field : full-frame grayscale ground.  Slots: Scale(0) · Drift(1, cyclic) · Contrast(2) · Level(3)
SP Figure: one grayscale silhouette.     Slots: Size(0) · X(1) · Y(2) · Edge(3)"""
import sp_header as S

# ── SP Field ──────────────────────────────────────────────────────────────────
S.CYC.clear()
FIELD_SLOTS = [("fScale", "Scale"), ("fDrift", "Drift"), ("fContrast", "Contrast"), ("fLevel", "Level")]
fin = list(S.ROOT)
fin += S.slot("fScale", "Scale", default=0.35, drive=True)
fin += S.slot("fDrift", "Drift", default=0.0, drive=True, cyclic=True)
fin += S.slot("fContrast", "Contrast", default=0.5)
fin += S.slot("fLevel", "Level", default=0.5)

field_body = f"""
float spN2(vec2 p) {{ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }}
float spVal(vec2 p) {{
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y);
}}
void main() {{
    float H = TIME * heartRate;                 // pilot convention: heart in-shader; Wire-side later

    float SC = {S.call("fScale", 0)};      // spatial frequency — the fundamental
    float DR = {S.call("fDrift", 1)};      // cyclic drift phase
    float CO = {S.call("fContrast", 2)};
    float LV = {S.call("fLevel", 3)};

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    uv.x *= RENDERSIZE.x / RENDERSIZE.y;

    float a = DR * 2.0 * SP_PI;
    vec2 p = uv * (1.5 + SC * 14.0) + 0.8 * vec2(cos(a), sin(a));
    float n = 0.6 * spVal(p) + 0.3 * spVal(p * 2.03 + 7.7) + 0.1 * spVal(p * 4.01 + 13.1);

    float v = clamp((n - 0.5) * (0.2 + CO * 2.8) + LV, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);   // alpha ground: dark = open — the feedback lives in the gaps
}}
"""
p1 = S.emit("SP Field — grayscale ground probe. SMART PARAM v4.", "SP probe", fin, field_body, "SP Field", S.groups(FIELD_SLOTS))
print("wrote", p1)

# ── SP Figure — the 2D base contract: Size·X·Y·Turn·Edge·Outline ─────────────
S.CYC.clear()
FIG_SLOTS = [("gSize", "Size"), ("gX", "X"), ("gY", "Y"), ("gTurn", "Turn"), ("gLine", "Outline"), ("gMat", "Material"), ("gFlt", "Float"), ("gSpn", "Spin")]
gin = list(S.ROOT)
gin += S.slot("gSize", "Size", default=0.4, drive=True)
gin += S.slot("gX", "X", default=0.5, drive=True)
gin += S.slot("gY", "Y", default=0.5, drive=True)
gin += S.slot("gTurn", "Turn", default=0.0, drive=True, cyclic=True)
gin += S.slot("gLine", "Outline", default=0.0)
gin += S.slot("gMat", "Material", default=0.8)
gin += S.slot("gFlt", "Float", default=0.25)
gin += S.slot("gSpn", "Spin", default=0.0, drive=True, cyclic=True)

fig_body = f"""
float sdCapsule2(vec2 p, float L, float r) {{
    p.x -= clamp(p.x, -L, L);
    return length(p) - r;
}}
float spFlat(vec2 p, mat2 R, float L, float r) {{
    return sdCapsule2(R * p, L, r);
}}
vec3 spPlaneMap(vec2 sq, vec3 uu, vec3 vv, vec3 nn, float dU) {{   // eye-ray ∩ rotated plane → material coords
    vec3 D = vec3(sq, dU);
    float den = dot(nn, D);
    if (abs(den) < 1e-4) return vec3(1e6, 1e6, 0.0);
    float t = (dU * nn.z) / den;
    if (t <= 0.0) return vec3(1e6, 1e6, 0.0);
    vec3 Xp = vec3(0.0, 0.0, -dU) + t * D;
    return vec3(dot(uu, Xp), dot(vv, Xp), 1.0);
}}
void main() {{
    float H = TIME * heartRate;                 // pilot convention: heart in-shader; Wire-side later

    float SZ = {S.call("gSize", 0)};       // presence — the fundamental
    float X  = {S.call("gX", 1)};
    float Y  = {S.call("gY", 2)};
    float TN = {S.call("gTurn", 3)};       // cyclic in-plane rotation (2D's one plane)
    float OL = {S.call("gLine", 4)};       // 0 solid — 1 open ring
    float MT = {S.call("gMat", 5)};        // MATERIAL: fog → soft pillow → hard inked solid
    float FLT = {S.call("gFlt", 6)};       // FLOAT: grounded → seated → airborne
    float SPN = {S.call("gSpn", 7)};       // SPIN: cyclic plane tumble on the diagonal axis
    // ── the folds: three macros drive the old internals on taste curves ──
    float ED = pow(MT, 0.7);                                    // edge hardens with material
    float EM = smoothstep(0.05, 0.6, MT);                       // relief arrives early
    float ST = smoothstep(0.55, 1.0, MT) * 0.8;                 // ink only on hard material
    float SH = smoothstep(0.05, 0.35, FLT) * (1.0 - smoothstep(0.5, 0.95, FLT));   // contact: rises, then lifts away
    float DR = smoothstep(0.35, 1.0, FLT);                      // throw grows with altitude

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    // ── containment law: the figure may NEVER touch the frame edge (cloners repeat edges) ──
    float rad = 0.02 + SZ * 0.34;                               // bounding radius incl. rotation
    float m = 0.03;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    vec2 c = (vec2(X, Y) - 0.5) * 2.0 * max(hf2 - rad * 1.6 - m, vec2(0.0));   // travel shrinks as size grows (slab+shadows margin)

    float a = TN * 2.0 * SP_PI;
    mat2 R = mat2(cos(a), sin(a), -sin(a), cos(a));

    // ── in-shader perspective plane rotation (Transform's trick, but containment-safe) ──
    float axr = SPN * 2.0 * SP_PI;                              // one Spin phase, both planes:
    float ayr = SPN * 2.0 * SP_PI;                              // a tumble about the diagonal axis
    float ca_ = cos(axr), sa_ = sin(axr), cb_ = cos(ayr), sb_ = sin(ayr);
    vec3 uu = vec3(cb_, 0.0, -sb_);
    vec3 vv = vec3(sa_ * sb_, ca_, sa_ * cb_);
    vec3 nn = vec3(ca_ * sb_, -sa_, ca_ * cb_);
    float dU = 4.0;
    float kNow = dU / (dU - min(length(nn.xy), 0.95));          // adaptive shrink: near edge can never escape
    vec2 s2 = (uv - c) / rad;
    float edgeGuard = 1.0 - smoothstep(0.985, 1.0, length(s2)); // containment safety feather
    vec3 mm = spPlaneMap(s2 * kNow, uu, vv, nn, dU);
    vec2 p = mm.xy * rad;                                       // the flat drawing, seen in perspective
    float r = rad * 0.45;                                       // capsule: length 2·rad, width 0.9·rad
    float L = rad - r;
    vec2 q = R * p;
    vec2 qq = vec2(q.x - clamp(q.x, -L, L), q.y);
    float ql = length(qq);
    float sd0 = ql - r;                                         // the silhouette
    vec2 gsd = (ql > 1e-6) ? (qq / ql) * R : vec2(0.0, 1.0);    // SDF gradient, back in screen space

    float sd = sd0;
    float e = mix(r * 0.9, 0.003, ED);
    float w = mix(r * 1.30, max(0.008, rad * 0.08), OL);        // hollow: real closed dwell at low OL, then opens along the spine
    float vTop = smoothstep(0.0, -e, sd) - smoothstep(0.0, -e, sd + w);
    float v = vTop;

    // ── Stroke: ink riding the VISIBLE silhouette (the mid-fade contour), not the static
    //    capsule — it follows Edge dynamically. Ink softness breathes with Edge too. ──
    float sw = ST * r * 0.09;
    float top = min(-0.5 * e + 0.5 * sw, 0.0);
    float bot = top - sw;
    float ia = max(0.0035, e * 0.15);
    float stroke = smoothstep(top + ia, top - ia, sd0) * (1.0 - smoothstep(bot + ia, bot - ia, sd0));
    // inner rim: ink the hollow's visible contour too (depth: a hole through a solid, not missing
    // paint) — but ONLY while the aperture is actually open, so the full capsule returns clean
    float lvl2 = -(w + 0.5 * e);                                // mid-fade of the inner edge
    float top2 = lvl2 + 0.5 * sw;
    float bot2 = lvl2 - 0.5 * sw;
    float inner = smoothstep(top2 + ia, top2 - ia, sd) * (1.0 - smoothstep(bot2 + ia, bot2 - ia, sd));
    float gateAp = smoothstep(0.0, r * 0.08, r - w);            // aperture-open gate
    inner *= gateAp;                                            // fades in as the hollow opens
    stroke = max(stroke, inner);

    // ── the ink IS the boundary: with any real stroke, no body material renders beyond it
    //    (kills the translucent "jacket" the outer half of a soft fade would otherwise wear) ──
    float bodyCut = mix(1.0, smoothstep(top + ia, top - ia, sd0), clamp(ST * 8.0, 0.0, 1.0));
    vTop *= bodyCut; v *= bodyCut;

    // ── Emboss: dome relief over a wide band from the SDF gradient (probes have SDFs;
    //    adapted shaders without one fall back to luminance-gradient). Light = the comp's
    //    one implied sun, same as the 3D figure. ──
    float t = clamp(-sd / r, 0.0, 1.0);                         // full dome: 0 at rim → 1 only at the spine
    float tilt = cos(t * 1.5708) * EM * 2.2;                    // no plateau — the solid reads as one pillow
    vec3 n = normalize(vec3(gsd * tilt, 1.0));
    vec3 Ld = normalize(vec3(-0.4, 0.55, 1.15));  // same sun azimuth, brought frontal: crown lit, edges fall away
    float lam = max(0.0, dot(n, Ld));
    float spec = pow(max(0.0, dot(reflect(-Ld, n), vec3(0.0, 0.0, 1.0))), 20.0);
    float shade = mix(1.0, 0.30 + 0.80 * lam, EM);
    vec3 col = vec3(vTop * shade + vTop * spec * EM);

    // ── corpus pass (field.visual-perception) ──
    float strokeOn = clamp(ST * 8.0, 0.0, 1.0);
    // Cornsweet shoulders: the body brightens toward its ink — reads as lighter material for free
    float cw = r * 0.35;
    float shO = smoothstep(top - cw, top, sd0);
    float shI = smoothstep(top2 + cw, top2, sd) * gateAp;
    col *= 1.0 + 0.20 * strokeOn * max(shO, shI);
    // Pinna bright line: a hairline light contour inside the dark ink — luminance spreads across the body
    float hw = max(0.004, sw * 0.5);
    float hl  = smoothstep(bot + ia, bot - ia, sd0) * (1.0 - smoothstep(bot - hw + ia, bot - hw - ia, sd0));
    float hl2 = (smoothstep(top2 - ia, top2 + ia, sd) * (1.0 - smoothstep(top2 + hw - ia, top2 + hw + ia, sd))) * gateAp;
    col += vec3(0.30) * strokeOn * max(hl, hl2) * v;
    // Crater pit: the aperture's inner wall shaded INVERTED to the dome — same sun, hole reads sunken
    float pw = r * 0.18;
    float pband = (smoothstep(bot2 + ia, bot2 - ia, sd) - smoothstep(bot2 - pw + ia, bot2 - pw - ia, sd)) * gateAp;
    pband = max(pband, 0.0) * clamp((sd - (bot2 - pw)) / pw, 0.0, 1.0);
    vec2 gN = normalize(gsd + vec2(1e-5));
    float pitLit = max(0.0, dot(-gN, normalize(Ld.xy)));
    col += vec3(0.10 + 0.40 * pitLit) * pband;

    float ink = stroke * 0.85;                                  // drawn line, not a void
    col *= (1.0 - ink);
    float aFig = max(max(v, ink), pband * 0.85);

    // ── Shadow: soft dark cast toward lower-right (the sun sits upper-left), under the figure ──
    float aSh = 0.0;
    if (SH > 0.001) {{
        vec3 mS = spPlaneMap((s2 - vec2(0.11, -0.13) * SH) * kNow, uu, vv, nn, dU);
        float sdSh = spFlat(mS.xy * rad, R, L, r);
        aSh = SH * 0.55 * smoothstep(rad * 0.10, -rad * 0.10, sdSh) * (1.0 - aFig);
    }}
    if (DR > 0.001) {{
        vec3 mD = spPlaneMap((s2 - vec2(0.30, -0.34) * DR) * kNow, uu, vv, nn, dU);
        float sdD = spFlat(mD.xy * rad, R, L, r);
        float aD = DR * 0.40 * smoothstep(rad * 0.24, -rad * 0.24, sdD) * (1.0 - aFig);
        aSh = max(aSh, aD);
    }}
    gl_FragColor = vec4(min(col, vec3(1.0)) * edgeGuard, min(1.0, aFig + aSh) * edgeGuard);   // real alpha: contained, always
}}
"""
p2 = S.emit("SP Figure — one grayscale silhouette probe. SMART PARAM v4.", "SP probe", gin, fig_body, "SP Figure", S.groups(FIG_SLOTS))
print("wrote", p2)
