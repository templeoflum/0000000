#!/usr/bin/env python3
"""make_4d_field.py — SP Atom 4D Field: the window in w, FIELD version. The shape comes from a 4D distance field,
so any figure morphs into any other, smoothly. Figure A / B / Morph over tesseract · 4-sphere · duocylinder ·
16-cell · 4D torus · 24-cell. The projected slab [W−T, W+T] is rendered as its outer SHELL: each 3D point
inverse-projects to a line through the eye in w; a short march along that line inside the window finds the
solid. Shell front + back, translucent by Faces; the slab's end caps are the cut surfaces. No cell walls."""
import json, os, subprocess, sys

NAME = "SP Atom 4D Field"
FIGS = ["tesseract", "4-sphere", "duocylinder", "16-cell", "4D torus", "24-cell"]
INPUTS = [
    {"NAME": "figA",   "LABEL": "Figure A",  "TYPE": "long",  "DEFAULT": 0, "VALUES": list(range(6)), "LABELS": FIGS},
    {"NAME": "figB",   "LABEL": "Figure B",  "TYPE": "long",  "DEFAULT": 4, "VALUES": list(range(6)), "LABELS": FIGS},
    {"NAME": "morph",  "LABEL": "Morph",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",  "LABEL": "Size",      "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "wpos",   "LABEL": "W",         "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "thick",  "LABEL": "Thickness", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    # the stack: N cross-sections through w inside the window, each projected — the layers are deliberate now
    {"NAME": "layers", "LABEL": "Layers",    "TYPE": "float", "DEFAULT": 8.0, "MIN": 2.0, "MAX": 32.0},
    {"NAME": "spread", "LABEL": "Spread",    "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sweep",  "LABEL": "Sweep",     "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "drift",  "LABEL": "Drift",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "turn",   "LABEL": "Turn",      "TYPE": "float", "DEFAULT": 0.15, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "spin",   "LABEL": "Spin",      "TYPE": "float", "DEFAULT": 0.2, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "dbl",    "LABEL": "Double",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sun",    "LABEL": "Sun",       "TYPE": "float", "DEFAULT": 0.9, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "height", "LABEL": "Height",    "TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "distance","LABEL": "Distance", "TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "faces",  "LABEL": "Faces",     "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "edgesv", "LABEL": "Edges",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "roundv", "LABEL": "Round",     "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "verts",  "LABEL": "Vertices",  "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "shade",  "LABEL": "Shade",     "TYPE": "float", "DEFAULT": 0.8, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "colorm", "LABEL": "Base",      "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["gray", "normal"]},
    {"NAME": "wet",    "LABEL": "Wet",       "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "loopv",  "LABEL": "Loop",      "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 4.0},
    {"NAME": "hue",    "LABEL": "Hue",       "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rOff",   "LABEL": "Red",       "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gOff",   "LABEL": "Green",     "TYPE": "float", "DEFAULT": 0.33, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bOff",   "LABEL": "Blue",      "TYPE": "float", "DEFAULT": 0.67, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
#define PI 3.14159265
#define CAMZ 3.2
#define FOV 1.1
#define WD 2.2
void rot(inout float a, inout float b, float th) { float c = cos(th), s = sin(th); float na = c * a - s * b; b = s * a + c * b; a = na; }
#define EDGE0 2.0
#define VERT0 130.0
#define RIM0 146.0
#define NRIM 48
float gH, gW0, gW1, gRw, gPh; vec4 gA; float gB; vec3 gLp;
vec4 rot4(vec4 q) { rot(q.x, q.z, gA.x); rot(q.x, q.y, gA.y); rot(q.x, q.w, gA.z); rot(q.z, q.w, gA.w); rot(q.y, q.z, gB); return q; }
vec4 axisVec(int k) { return vec4(k == 0 ? 1.0 : 0.0, k == 1 ? 1.0 : 0.0, k == 2 ? 1.0 : 0.0, k == 3 ? 1.0 : 0.0); }
vec4 rd_(float x) { return IMG_PIXEL(ph, vec2(x + 0.5, 0.5)); }
vec4 vert(int i) { return vec4((i & 1) != 0 ? 1.0 : -1.0, (i & 2) != 0 ? 1.0 : -1.0, (i & 4) != 0 ? 1.0 : -1.0, (i & 8) != 0 ? 1.0 : -1.0) * gH; }
vec4 vertM(int i) { return rot4(vert(i)); }
vec3 projW(vec4 vw) { return vw.xyz * ((WD * gH) / (WD * gH - vw.w)); }
vec4 unrot4(vec4 q) { rot(q.y, q.z, -gB); rot(q.z, q.w, -gA.w); rot(q.x, q.w, -gA.z); rot(q.x, q.y, -gA.y); rot(q.x, q.z, -gA.x); return q; }
float pscale(float w) { return (WD * gH) / (WD * gH - w); }
float fig4(int f, vec4 p, float r) {
    if (f == 0) { vec4 q = abs(p) - r * 0.5; return length(max(q, 0.0)) + min(max(max(q.x, q.y), max(q.z, q.w)), 0.0); }
    if (f == 1) return length(p) - r;
    if (f == 2) return max(length(p.xy) - r * 0.7071, length(p.zw) - r * 0.7071);
    if (f == 3) return (abs(p.x) + abs(p.y) + abs(p.z) + abs(p.w) - r) * 0.5;
    if (f == 4) { vec2 q = vec2(length(p.xyz) - r * 0.7, p.w); return length(q) - r * 0.3; }
    vec4 q = abs(p); float c = 0.0;
    c = max(c, (q.x + q.y) * 0.7071); c = max(c, (q.x + q.z) * 0.7071); c = max(c, (q.x + q.w) * 0.7071);
    c = max(c, (q.y + q.z) * 0.7071); c = max(c, (q.y + q.w) * 0.7071); c = max(c, (q.z + q.w) * 0.7071);
    return c - r * 0.7071;
}
float sd4(vec4 q) { float r = 2.0 * gH; return mix(fig4(figA, q, r), fig4(figB, q, r), morph); }
// the STACK: N cross-sections at chosen w positions inside the window, each projected; the field is the union.
// Spread bunches the positions toward the near (0) or far (1) edge; Sweep (integrated phase) slides them through w.
float field(vec3 p) {
    float dmin = 1e9, span = gW1 - gW0, acc = 0.0, dprev = 0.0;
    float N = floor(layers + 0.5);
    for (int i = 0; i < 32; i++) {
        if (float(i) >= N) break;
        float u = fract((float(i) + 0.5) / N + gPh);          // even stack, sliding with the sweep phase
        float e = mix(0.35, 2.85, spread);                   // Spread: warp the stack toward one edge
        u = pow(u, e);
        // Drift: each sample is pushed on by the distance the previous one measured — the stack disagrees
        // from pixel to pixel, which is where the moiré and the rounding come from (1 = the original march)
        acc += drift * 0.8 * max(dprev, 0.0);
        float t = gW0 + u * span + acc;
        if (t > gW1 || t >= WD * gH * 0.95) break;
        float sc = pscale(t);
        float d = sd4(unrot4(vec4(p / sc, t))) * sc;
        dmin = min(dmin, d); dprev = d;
    }
    return dmin;
}
vec3 fnorm(vec3 p) { vec2 e = vec2(0.003, 0.0); return normalize(vec3(field(p + e.xyy) - field(p - e.xyy), field(p + e.yxy) - field(p - e.yxy), field(p + e.yyx) - field(p - e.yyx))); }
vec3 raySeg(vec3 ro, vec3 rd, vec3 a, vec3 b) {          // (distance, t along the ray, s along the segment; s outside (0,1) = beyond an end)
    vec3 u = rd, v = b - a, w = ro - a;
    float A = dot(u, u), B = dot(u, v), C = dot(v, v), D = dot(u, w), E = dot(v, w);
    float den = A * C - B * B; float sc, tc;
    if (den < 1e-7) { sc = 0.0; tc = -D / A; } else { sc = (A * E - B * D) / den; tc = (B * clamp(sc, 0.0, 1.0) - D) / A; }
    tc = max(tc, 0.0);
    float scc = clamp(sc, 0.0, 1.0);
    return vec3(length(ro + rd * tc - (a + v * scc)), tc, sc);
}
// exact ray / infinite-cylinder entry (axis point a, unit dir d, radius r); returns t or -1
float rayCyl(vec3 ro, vec3 rd, vec3 a, vec3 d, float r) {
    vec3 oc = ro - a;
    vec3 rdp = rd - d * dot(rd, d), ocp = oc - d * dot(oc, d);
    float A = dot(rdp, rdp), B = 2.0 * dot(rdp, ocp), C = dot(ocp, ocp) - r * r;
    if (A < 1e-9) return -1.0;
    float disc = B * B - 4.0 * A * C; if (disc < 0.0) return -1.0;
    return (-B - sqrt(disc)) / (2.0 * A);
}
// the tube PROFILE: a rounded square, Round 0 = square, 1 = circle
float prof2(vec2 q, float r, float c) { vec2 d = abs(q) - (r - c); return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0) - c; }
// ray / extruded profile: the problem is 2D in the bar's cross-section plane (u, v); a short 2D march
float rayTube(vec3 ro, vec3 rd, vec3 a, vec3 u, vec3 v, float r, float c, out vec2 n2, out float dmin) {
    vec3 oc = ro - a;
    vec2 o2 = vec2(dot(oc, u), dot(oc, v)), d2 = vec2(dot(rd, u), dot(rd, v));
    float sp = length(d2); if (sp < 1e-6) { dmin = 9.0; n2 = vec2(0.0); return -1.0; }
    float t = 0.0, d = 0.0; dmin = 9.0;
    // start near the closest approach minus the profile's reach
    float tc = -dot(o2, d2) / (sp * sp); t = max(tc - r * 1.5 / sp, 0.0);
    for (int i = 0; i < 12; i++) { vec2 q = o2 + d2 * t; d = prof2(q, r, c); dmin = min(dmin, d); if (d < 0.0004 || t > tc + r * 1.5 / sp) break; t += d / sp * 0.95; }
    vec2 q = o2 + d2 * t; vec2 e = vec2(0.001, 0.0);
    n2 = normalize(vec2(prof2(q + e.xy, r, c) - prof2(q - e.xy, r, c), prof2(q + e.yx, r, c) - prof2(q - e.yx, r, c)));
    return (d < 0.0004) ? t : -1.0;
}
// the MITER at corner v for the bar heading along dir: keep only the side of every bisector plane that belongs to this bar
bool keptAtCorner(vec3 p, int v, vec3 dir) {
    vec4 pv4 = rd_(VERT0 + float(v)); if (pv4.w < 0.5) return true;   // not a corner: the bar was cut by the window, no miter
    vec3 pv = pv4.xyz;
    for (int k = 0; k < 4; k++) {
        vec4 pn4 = rd_(VERT0 + float(v ^ (1 << k))); if (pn4.w < 0.5) continue;   // a neighbour outside the window owns nothing
        vec3 pn = pn4.xyz;
        vec3 dj = normalize(pn - pv);
        if (dot(dj, dir) > 0.999) continue;                  // that is this bar itself
        if (dot(p - pv, dir - dj) < 0.0) return false;       // closer to the neighbour's axis: the neighbour owns it
    }
    return true;
}
vec3 sunDir() { float ph = sun * 2.0 * PI, th = (height - 0.5) * PI; return normalize(vec3(cos(th) * sin(ph), sin(th), -cos(th) * cos(ph))); }
float lit(vec3 p, vec3 n, vec3 rd) {
    vec3 Lv = gLp - p; float Ld2 = dot(Lv, Lv); vec3 L = Lv * inversesqrt(Ld2);
    float D = length(gLp); float att = clamp((D - gRw) * (D - gRw) / Ld2, 0.0, 1.0);
    float lam = clamp(dot(n, L), 0.0, 1.0) * att;
    float facing = clamp(dot(n, -rd), 0.0, 1.0);
    float specPow = mix(10.0, 40.0, distance);
    float spec = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow) * att;
    return 0.14 + 0.72 * lam + 0.30 * pow(1.0 - facing, 2.0) + spec * 0.35;
}
void setup() {
    float asp = RENDERSIZE.x / RENDERSIZE.y; vec2 hf2 = vec2(0.5 * asp, 0.5); float m = 0.04;
    float room = min(hf2.x, hf2.y) - m;
    float Rp = mix(0.03, max(room, 0.03), sizev);
    float protrude = 0.23 / (2.0 * WD / (WD - 1.0)) * 1.15;   // a fixed reserve for the biggest sphere
    Rp /= (1.0 + protrude);
    float k = Rp * FOV;
    gRw = k * CAMZ / (1.0 + k);
    gH = gRw / (2.0 * WD / (WD - 1.0));
    float Wc = wpos * 2.0 * gH;
    float T = max(thick * 2.0 * gH, gH * 2e-4);
    gW0 = max(Wc - T, -2.2 * gH); gW1 = min(Wc + T, WD * gH * 0.9);
}
void main() {
    if (PASSINDEX == 0) {
        float x = floor(gl_FragCoord.x);
        float dt = clamp(TIMEDELTA, 0.0, 0.1);
        float rt = turn * abs(turn) * 1.2, rs = spin * abs(spin) * 1.2;
        vec4 pA = rd_(0.0); vec4 p1 = rd_(1.0);
        vec4 nA = vec4(mod(pA.x + dt * rt, 2.0 * PI), mod(pA.y + dt * rt * 0.618, 2.0 * PI), mod(pA.z + dt * rs, 2.0 * PI), mod(pA.w + dt * rs * 0.618, 2.0 * PI));
        float nB = mod(p1.x + dt * rs * dbl, 2.0 * PI), nS = fract(p1.y + dt * sweep * abs(sweep) * 0.5);
        if (x < 1.0) { gl_FragColor = nA; return; }
        if (x < 2.0) { gl_FragColor = vec4(nB, nS, 0.0, 1.0); return; }
        gA = nA; gB = nB; gPh = nS; setup();
        if (x < VERT0) {                                     // a tesseract edge endpoint, clipped to the window, projected
            float e = floor((x - EDGE0) * 0.5); float which = mod(x - EDGE0, 2.0);
            int ei = int(e); int i = ei / 4; int kk = ei - i * 4;
            if ((i & (1 << kk)) != 0) { gl_FragColor = vec4(0.0); return; }
            vec4 aw = vertM(i), bw = vertM(i + (1 << kk));
            float wa = aw.w, wb = bw.w, t0 = 0.0, t1 = 1.0, dw = wb - wa;
            if (abs(dw) < 1e-6) { if (wa < gW0 || wa > gW1) { gl_FragColor = vec4(0.0); return; } }
            else { float ta = (gW0 - wa) / dw, tb = (gW1 - wa) / dw; t0 = max(0.0, min(ta, tb)); t1 = min(1.0, max(ta, tb)); if (t1 <= t0) { gl_FragColor = vec4(0.0); return; } }
            gl_FragColor = vec4(projW(mix(aw, bw, (which < 0.5) ? t0 : t1)), 1.0); return;
        }
        if (x < RIM0) {
        int i = int(x - VERT0); vec4 v = vertM(i);           // a vertex
        gl_FragColor = vec4(projW(v), (v.w >= gW0 && v.w <= gW1) ? 1.0 : 0.0); return;
        }
        // a rim segment: face fi (24 squares), plane pi (0 = W-T, 1 = W+T), endpoint 'which'
        float r_ = x - RIM0; int si = int(floor(r_ * 0.5)); float which = mod(r_, 2.0);
        int fi = si / 2, pi_ = si - fi * 2;
        int pr = fi / 4, ob = fi - pr * 4;
        int k1 = (pr < 3) ? 0 : ((pr < 5) ? 1 : 2);
        int k2 = (pr == 0) ? 1 : ((pr == 1) ? 2 : ((pr == 2) ? 3 : ((pr == 3) ? 2 : 3)));
        int i0 = 0, oi = 0;
        for (int k = 0; k < 4; k++) { if (k == k1 || k == k2) continue; if (((ob >> oi) & 1) != 0) i0 |= (1 << k); oi++; }
        float P = (pi_ == 0) ? gW0 : gW1;
        int ea[4] = int[4](i0, i0 | (1 << k2), i0, i0 | (1 << k1));
        int eb[4] = int[4](i0 | (1 << k1), i0 | (1 << k1) | (1 << k2), i0 | (1 << k2), i0 | (1 << k1) | (1 << k2));
        vec3 c0 = vec3(0.0), c1 = vec3(0.0); int nc = 0;
        for (int q = 0; q < 4; q++) {
            vec4 aw = vertM(ea[q]), bw = vertM(eb[q]);
            float wa = aw.w, wb = bw.w;
            if ((wa - P) * (wb - P) < 0.0) { vec3 c = projW(mix(aw, bw, (P - wa) / (wb - wa))); if (nc == 0) c0 = c; else c1 = c; nc++; }
        }
        if (nc != 2) { gl_FragColor = vec4(0.0); return; }
        gl_FragColor = vec4((which < 0.5) ? c0 : c1, 1.0); return;
    }
    gA = rd_(0.0); vec4 p1 = rd_(1.0); gB = p1.x; gPh = p1.y; setup();
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;
    float Rp = (gRw / (CAMZ - gRw)) / FOV;
    float protrude = 0.23 / (2.0 * WD / (WD - 1.0)) * 1.15;
    if (length(uv) > Rp * (1.0 + protrude) * 1.06 + 3.0 / RENDERSIZE.y) { gl_FragColor = vec4(0.0); return; }
    vec3 sd = sunDir(); gLp = sd * gRw * mix(1.35, 30.0, distance);
    vec3 ro = vec3(0.0, 0.0, -CAMZ), rd = normalize(vec3(uv * FOV, 1.0));
    float pxw = (1.0 / RENDERSIZE.y) * CAMZ * FOV;
    float erode = 0.0;

    // edges: nearest, opaque, radius eroding
    float tE = 1e9, covE = 0.0; vec3 nE = vec3(0.0, 0.0, -1.0), pE = vec3(0.0);
    float rE = gH * 0.09 * edgesv;                           // Edges: wireframe thickness — its own thing, never erodes
    float rV = gH * 0.14 * verts;                            // Vertices: their own spheres, their own size; at 0 there is no vertex at all
    // schedule: corners first (a sphere owns its corner), then the open edge cylinders between them
    if (rV > 1e-5) for (int i = 0; i < 16; i++) {
        vec4 c4 = rd_(VERT0 + float(i)); if (c4.w < 0.5) continue;
        vec3 oc = ro - c4.xyz; float b = dot(oc, rd);
        float dl = length(oc - rd * b);                      // closest approach of the ray to the sphere's center
        float cov = 1.0 - smoothstep(rV, rV + pxw, dl);
        if (cov > 0.001) { float h = b * b - dot(oc, oc) + rV * rV; float t = -b - sqrt(max(h, 0.0));
            if (t < tE) { tE = t; covE = cov; pE = ro + rd * t; nE = normalize(pE - c4.xyz); } }
    }
    if (rE > 1e-5) for (int e = 0; e < 64 + NRIM; e++) {
        bool rim = e >= 64;
        float base = rim ? RIM0 + float(2 * (e - 64)) : EDGE0 + float(2 * e);
        vec4 a4 = rd_(base); if (a4.w < 0.5) continue;
        vec3 a = a4.xyz, b = rd_(base + 1.0).xyz;
        int va = rim ? 0 : e / 4, vb = rim ? 0 : va + (1 << (e - va * 4));   // the two corners this bar joins (none for a rim)
        vec3 d = normalize(b - a); float L = length(b - a); if (L < 1e-5) continue;
        // cull: the ray must pass near the extended bar
        vec3 hq = raySeg(ro, rd, a - d * rE * 3.0, b + d * rE * 3.0);
        if (hq.x > rE * 1.5 + pxw) continue;
        // the profile's frame: sides aligned with the walls, from a neighbouring edge at corner a
        vec3 pv = rd_(VERT0 + float(va)).xyz, ref = (abs(d.y) < 0.9) ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0);
        if (!rim) for (int k = 0; k < 4; k++) { vec3 pn = rd_(VERT0 + float(va ^ (1 << k))).xyz; vec3 dj = normalize(pn - pv); if (abs(dot(dj, d)) < 0.99) { ref = dj; break; } }
        vec3 u = normalize(cross(d, ref)); vec3 v = cross(u, d);
        vec2 n2; float dm2;
        float t = rayTube(ro, rd, a, u, v, rE, rE * roundv, n2, dm2);
        if (t <= 0.0 || t >= tE) continue;
        vec3 p = ro + rd * t;
        float s_ = dot(p - a, d);
        bool cornerA = !rim && rd_(VERT0 + float(va)).w > 0.5, cornerB = !rim && rd_(VERT0 + float(vb)).w > 0.5;   // true corners, or window cuts
        float extA = cornerA ? rE * 3.0 : rE, extB = cornerB ? rE * 3.0 : rE;   // a cut end runs one radius past the cut, to meet the rim bars there
        if (s_ < -extA || s_ > L + extB) continue;
        if (cornerA && s_ < rE * 3.0 && !keptAtCorner(p, va, d)) continue;          // mitered at corner a
        if (cornerB && s_ > L - rE * 3.0 && !keptAtCorner(p, vb, -d)) continue;     // mitered at corner b
        float cov = 1.0 - smoothstep(0.0, pxw, max(dm2, 0.0));
        if (cov > 0.001) { tE = t; covE = cov; pE = p; nE = normalize(u * n2.x + v * n2.y); }
    }
    float lumE = (covE > 0.001) ? mix(0.92, lit(pE, nE, rd), shade) : 0.0;

    // march the shell inside the bounding sphere, stopping at the opaque bars
    float b = dot(ro, rd), c2 = dot(ro, ro) - gRw * gRw * 1.1, disc = b * b - c2;
    if (disc <= 0.0 && covE < 0.001) { gl_FragColor = vec4(0.0); return; }
    float t = max(-b - sqrt(max(disc, 0.0)), 0.0), tFar = min(-b + sqrt(max(disc, 0.0)), tE), d = 0.0, dmin = 9.0; vec3 p = ro;
    for (int i = 0; i < 56; i++) { p = ro + rd * t; d = field(p); dmin = min(dmin, d); if (d < 0.001 || t > tFar) break; t += d * 0.7; }
    float hit = (d < 0.001) ? 1.0 : 0.0;
    float cover = (disc > 0.0) ? max(hit, 1.0 - smoothstep(0.0, 0.0025, dmin)) : 0.0;
    if (cover < 0.001 && covE < 0.001) { gl_FragColor = vec4(0.0); return; }
    if (cover < 0.001) {                                     // only a bar or a vertex on this ray
        vec3 bodyE = vec3(lumE);
        if (colorm == 1) bodyE = (nE * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
        if (wet > 0.001) bodyE = mix(bodyE, 0.5 + 0.5 * cos(2.0 * PI * (bodyE * loopv + hue + vec3(rOff, gOff, bOff))), wet);
        gl_FragColor = vec4(bodyE * covE, covE); return;
    }
    vec3 nF = fnorm(p);
    float lumF = mix(0.92, lit(p, nF, rd), shade);
    float aF = clamp(faces, 0.0, 1.0);                        // Faces: shell opacity, all the way from clear to solid (as in the hybrid)
    float lum = lumF, A = aF; vec3 n = nF;
    if (hit > 0.5 && aF < 0.999) {                             // translucent: find the back surface and blend it behind
        float tb = t + 0.01; vec3 pb = p;
        for (int i = 0; i < 24; i++) { pb = ro + rd * tb; float db = field(pb); if (db > 0.0 || tb > tFar) break; tb += max(-db * 0.8, 0.01); }
        vec3 nB = -fnorm(pb);
        float lumB = mix(0.92, lit(pb, nB, rd), shade);
        lum = aF * lumF + (1.0 - aF) * aF * lumB; A = aF + (1.0 - aF) * aF;
        n = normalize(nF * aF + nB * (1.0 - aF));
        lum /= max(A, 1e-4);
    }
    A *= cover;
    if (covE > 0.001) {                                      // the bar behind the shell (the march stopped at it)
        float A2 = A + (1.0 - A) * covE;
        lum = (lum * A + lumE * (1.0 - A) * covE) / max(A2, 1e-4);
        n = normalize(n * A + nE * (1.0 - A) * covE + vec3(0.0, 0.0, -1e-4)); A = A2;
    }
    vec3 body = vec3(lum);
    if (colorm == 1) body = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
    if (wet > 0.001) body = mix(body, 0.5 + 0.5 * cos(2.0 * PI * (body * loopv + hue + vec3(rOff, gOff, bOff))), wet);
    gl_FragColor = vec4(body * A, A);
}
"""
def emit():
    hdr = {"DESCRIPTION": "SP Atom 4D Field - window in w over a 4D distance-field catalog: any figure morphs to any figure, smoothly. The projected slab rendered as a STACK of N cross-sections through w (Layers/Spread/Sweep), front + back, Faces = opacity. Turn/Spin/Double, Sun/Height/Distance, Shade/Edge, Color stack. Contained. No drives.",
           "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS,
           "PASSES": [{"TARGET": "ph", "PERSISTENT": True, "FLOAT": True, "WIDTH": 242, "HEIGHT": 1}, {}]}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), NAME, "source"], check=True)
