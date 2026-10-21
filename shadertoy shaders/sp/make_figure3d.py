#!/usr/bin/env python3
"""make_figure3d.py — SP Figure 3D: the torus, carrying the 2D study's laws into volume.
Quaternion-style tumbling: Tumble = rotation phase (cyclic) about an axis that itself
precesses (Axis, cyclic) — the Tumble:Axis RATIO is the tumbling character.
Slots: Size(0) · X(1) · Y(2) · Tumble(3,cyc) · Axis(4,cyc) · Edge(5, silhouette softness/halo)
· Outline(6, arc opening with closed dwell; top range thins tube to WIRE — the vanish beat)
· Emboss(7, flat silhouette ↔ full volume — flat tumble is rotationally bistable)
· Stroke(8, toon ink on the true silhouette; hole rims inked free) · Shadow(9) · Drop(10).
Laws: containment · ink is the boundary (halo suppressed under stroke) · Cornsweet shoulder +
Pinna line at the toon threshold · one sun · judge layer-soloed only."""
import sp_header as S

S.CYC.clear()
SLOTS = [("hSize", "Size"), ("hX", "X"), ("hY", "Y"), ("hTum", "Tumble"), ("hAxis", "Axis"),
         ("hEdge", "Edge"), ("hLine", "Outline"), ("hEmb", "Emboss"), ("hStk", "Stroke"),
         ("hShd", "Shadow"), ("hDrop", "Drop"), ("hMic", "Micro")]
inputs = list(S.ROOT)
inputs += S.slot("hSize", "Size", default=0.4, drive=True)
inputs += S.slot("hX", "X", default=0.5, drive=True)
inputs += S.slot("hY", "Y", default=0.5, drive=True)
inputs += S.slot("hTum", "Tumble", default=0.0, drive=True, cyclic=True)
inputs += S.slot("hAxis", "Axis", default=0.0, drive=True, cyclic=True)
inputs += S.slot("hEdge", "Edge", default=0.8)
inputs += S.slot("hLine", "Outline", default=0.0)
inputs += S.slot("hEmb", "Emboss", default=0.9)
inputs += S.slot("hStk", "Stroke", default=0.0)
inputs += S.slot("hShd", "Shadow", default=0.0)
inputs += S.slot("hDrop", "Drop", default=0.0)
inputs += S.slot("hMic", "Micro", default=0.0)

body = f"""
vec3 spRotAA(vec3 p, vec3 ax, float th) {{                 // Rodrigues, inverse rotation
    float c = cos(th), s = sin(th);
    return p * c + cross(ax, p) * s + ax * dot(ax, p) * (1.0 - c);
}}
float spH3(vec3 p) {{ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }}
float spN3(vec3 p) {{
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(spH3(i), spH3(i + vec3(1, 0, 0)), f.x), mix(spH3(i + vec3(0, 1, 0)), spH3(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(spH3(i + vec3(0, 0, 1)), spH3(i + vec3(1, 0, 1)), f.x), mix(spH3(i + vec3(0, 1, 1)), spH3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}}
float spTorusS(vec3 p, float ra, float rb) {{ vec2 q = vec2(length(p.xy) - ra, p.z); return length(q) - rb; }}
float spTorusW(vec3 p, float ra, float rb, float wr) {{    // the wire lattice ON the torus surface
    vec2 q = vec2(length(p.xy) - ra, p.z);
    float dsh = abs(length(q) - rb);                       // distance to the shell
    float at = atan(p.y, p.x);
    float ap = atan(q.y, q.x);
    float st = 6.2831853 / 10.0;                           // 10 spokes around the ring
    float sp = 6.2831853 / 6.0;                            // 6 rings around the tube
    float gt = abs(fract(at / st + 0.5) - 0.5) * st * ra;
    float gp = abs(fract(ap / sp + 0.5) - 0.5) * sp * rb;
    float dg = min(gt, gp);
    return sqrt(dsh * dsh + dg * dg) - wr;
}}
float spMapT(vec3 p, vec3 ax, float th, float ra, float rb, float W, float wr) {{
    vec3 q = spRotAA(p, ax, th);
    q = q.xzy;
    float ds = spTorusS(q, ra, rb);
    if (W <= 0.001) return ds;
    return mix(ds, spTorusW(q, ra, rb, wr), W);            // the surface DEGRADES into its wires
}}
float spSilT(vec3 ro, vec3 ax, float th, float ra, float rb, float W, float wr) {{
    float t = 0.0, mind = 9.0;                             // soft silhouette mask for shadows
    for (int i = 0; i < 20; i++) {{
        float d = spMapT(ro + vec3(0.0, 0.0, t), ax, th, ra, rb, W, wr);
        mind = min(mind, d);
        if (d < 0.004 || t > 3.6) break;
        t += d * 0.85;
    }}
    return 1.0 - smoothstep(0.0, 0.12, mind);
}}
void main() {{
    float H = TIME * heartRate;

    float SZ = {S.call("hSize", 0)};   // presence — the fundamental
    float X  = {S.call("hX", 1)};
    float Y  = {S.call("hY", 2)};
    float TM = {S.call("hTum", 3)};    // rotation phase about the precessing axis
    float AX = {S.call("hAxis", 4)};   // axis precession phase — Tumble:Axis ratio = the character
    float ED = {S.call("hEdge", 5)};
    float OL = {S.call("hLine", 6)};
    float EM = {S.call("hEmb", 7)};
    float ST = {S.call("hStk", 8)};
    float SH = {S.call("hShd", 9)};
    float DR = {S.call("hDrop", 10)};
    float MC = {S.call("hMic", 11)};   // 0 clean chrome — 1 fuzzy noisy SEM chrome

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    // ── containment law ──
    float rad = 0.03 + SZ * 0.33;
    float m = 0.03;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    vec2 c = (vec2(X, Y) - 0.5) * 2.0 * max(hf2 - rad * 1.6 - m, vec2(0.0));
    vec2 s = (uv - c) / rad;

    // ── quaternion-style tumble: axis precesses on a cone, body rotates about it ──
    float psi = AX * 2.0 * SP_PI;
    vec3 ax = normalize(vec3(cos(psi) * 0.62, sin(psi) * 0.62, 0.78));
    float th = TM * 2.0 * SP_PI;

    // ── Outline: closed dwell → surface degrades to WIREFRAME → wires thin (the vanish beat) ──
    float ra = 0.60, rb = 0.24;
    float W = smoothstep(0.10, 0.60, OL);
    float wr = mix(0.055, 0.012, smoothstep(0.60, 1.0, OL));

    float strokeOn = clamp(ST * 8.0, 0.0, 1.0);
    float e3 = mix(0.30, 0.008, ED);

    vec3 col = vec3(0.0);
    float aOut = 0.0;
    if (dot(s, s) < 1.1) {{
        vec3 ro = vec3(s, -2.0);
        float t = 0.0, mind = 9.0; bool hit = false; vec3 p = ro;
        for (int i = 0; i < 56; i++) {{
            p = ro + vec3(0.0, 0.0, t);
            float d = spMapT(p, ax, th, ra, rb, W, wr);
            mind = min(mind, d);
            if (d < 0.0025) {{ hit = true; break; }}
            t += d * 0.85;
            if (t > 4.0) break;
        }}
        if (hit) {{
            vec2 h = vec2(mix(0.005, 0.0018, W), 0.0);     // finer normals on thin wires
            vec3 n = normalize(vec3(
                spMapT(p + h.xyy, ax, th, ra, rb, W, wr) - spMapT(p - h.xyy, ax, th, ra, rb, W, wr),
                spMapT(p + h.yxy, ax, th, ra, rb, W, wr) - spMapT(p - h.yxy, ax, th, ra, rb, W, wr),
                spMapT(p + h.yyx, ax, th, ra, rb, W, wr) - spMapT(p - h.yyx, ax, th, ra, rb, W, wr)));
            // ── Micro: fuzzy noisy chrome — noise lives in OBJECT space, rides the tumble ──
            if (MC > 0.001) {{
                vec3 po = spRotAA(p, ax, th) * 26.0;
                vec2 e2 = vec2(0.05, 0.0);
                vec3 g3 = vec3(spN3(po + e2.xyy) - spN3(po - e2.xyy),
                               spN3(po + e2.yxy) - spN3(po - e2.yxy),
                               spN3(po + e2.yyx) - spN3(po - e2.yyx));
                n = normalize(n + g3 * MC * 0.55);
            }}
            vec3 Ld = normalize(vec3(-0.5, 0.7, -0.6));    // the one sun
            float lam = max(0.0, dot(n, Ld));
            float rimL = pow(1.0 - max(0.0, dot(n, vec3(0.0, 0.0, -1.0))), 2.0);
            float spec = pow(max(0.0, dot(reflect(-Ld, n), vec3(0.0, 0.0, -1.0))), 24.0);
            float vol = 0.14 + 0.72 * lam + 0.30 * rimL * (1.0 + 0.8 * MC) + spec * (0.35 + 0.95 * W + 0.8 * MC);
            if (MC > 0.001) {{                              // SEM detector grain, strongest on slopes
                float gn = spN3(spRotAA(p, ax, th) * 90.0);
                vol *= 1.0 + MC * 0.30 * (gn - 0.5) * (0.5 + rimL);
            }}
            float body = mix(0.92, vol, EM);               // Emboss 0 = flat silhouette: bistable tumble

            float rim = 1.0 - abs(n.z);                    // toon silhouette measure
            float th2 = 1.0 - mix(0.5, 0.10, ST);
            float inkM = strokeOn * 0.85 * smoothstep(th2 - 0.03, th2 + 0.03, rim);
            float shoulder = smoothstep(th2 - 0.30, th2, rim);          // Cornsweet: brighten toward the ink
            float pinna = smoothstep(th2 - 0.09, th2 - 0.03, rim) * (1.0 - smoothstep(th2 - 0.03, th2, rim));
            body *= 1.0 + 0.20 * strokeOn * shoulder;
            body += 0.30 * strokeOn * pinna;
            col = vec3(body) * (1.0 - inkM);
            aOut = 1.0;
        }} else {{
            float halo = (1.0 - smoothstep(0.0, e3, mind)) * 0.85;      // Edge: near-miss glow
            halo *= (1.0 - strokeOn);                                   // the ink is the boundary
            col = vec3(halo);
            aOut = halo;
            if (SH > 0.001) {{
                float sm = spSilT(vec3(s - vec2(0.26, -0.30) * SH, -2.0), ax, th, ra, rb, W, wr);
                aOut = max(aOut, SH * 0.55 * sm * (1.0 - halo));
            }}
            if (DR > 0.001) {{
                float dm = spSilT(vec3(s - vec2(0.72, -0.80) * DR, -2.0), ax, th, ra, rb, W, wr);
                aOut = max(aOut, DR * 0.40 * dm * (1.0 - halo));
            }}
        }}
    }}
    gl_FragColor = vec4(min(col, vec3(1.0)), aOut);        // object only, transparent world
}}
"""

print("wrote", S.emit("SP Figure 3D — the torus carrying the 2D laws: quaternion tumble, arc, wire, toon ink. SMART PARAM v4.", "SP probe", inputs, body, "SP Figure 3D", S.groups(SLOTS)))
