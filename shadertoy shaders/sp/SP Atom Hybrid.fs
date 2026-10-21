/*{
  "DESCRIPTION": "SP Atom 4D - the tesseract through a window in w; CONNECT blends the frame's distance field (walls + edges) with the stack's field: one level set morphs from walls to layers (Layers/Spread/Sweep/Drift) (Thickness 0 = cross-section, 1 = projection with edges + translucent clipped Faces); Turn/Spin/Double; Sun/Height/Distance light the faces, edges and cuts; Shade; Edges (wireframe thickness) / Vertices (corner spheres) / Faces; layer styles on every face (Bevel/Emboss/Inner Shadow/Inner Glow/Gradient/Contour); Color Base gray/normal + Loop per channel. Contained. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "sizev",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "wpos",
      "LABEL": "W",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "thick",
      "LABEL": "Thickness",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "connect",
      "LABEL": "Connect",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "layers",
      "LABEL": "Layers",
      "TYPE": "float",
      "DEFAULT": 8.0,
      "MIN": 2.0,
      "MAX": 32.0
    },
    {
      "NAME": "spread",
      "LABEL": "Spread",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sweep",
      "LABEL": "Sweep",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "drift",
      "LABEL": "Drift",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "turn",
      "LABEL": "Turn",
      "TYPE": "float",
      "DEFAULT": 0.15,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "spin",
      "LABEL": "Spin",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "dbl",
      "LABEL": "Double",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sun",
      "LABEL": "Sun",
      "TYPE": "float",
      "DEFAULT": 0.9,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "height",
      "LABEL": "Height",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "distance",
      "LABEL": "Distance",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "faces",
      "LABEL": "Faces",
      "TYPE": "float",
      "DEFAULT": 0.35,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "shade",
      "LABEL": "Shade",
      "TYPE": "float",
      "DEFAULT": 0.8,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "edgesv",
      "LABEL": "Edges",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "roundv",
      "LABEL": "Round",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "verts",
      "LABEL": "Vertices",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bevel",
      "LABEL": "Bevel",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "emboss",
      "LABEL": "Emboss",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "inner",
      "LABEL": "Inner Shadow",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "iglow",
      "LABEL": "Inner Glow",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gradient",
      "LABEL": "Gradient",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contour",
      "LABEL": "Contour",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "colorm",
      "LABEL": "Base",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "gray",
        "normal"
      ]
    },
    {
      "NAME": "wet",
      "LABEL": "Wet",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "loopv",
      "LABEL": "Loop",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 4.0
    },
    {
      "NAME": "hue",
      "LABEL": "Hue",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rOff",
      "LABEL": "Red",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gOff",
      "LABEL": "Green",
      "TYPE": "float",
      "DEFAULT": 0.33,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bOff",
      "LABEL": "Blue",
      "TYPE": "float",
      "DEFAULT": 0.67,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ],
  "PASSES": [
    {
      "TARGET": "ph",
      "PERSISTENT": true,
      "FLOAT": true,
      "WIDTH": 434,
      "HEIGHT": 1
    },
    {}
  ]
}*/

#define PI 3.14159265
#define CAMZ 3.2
#define FOV 1.1
#define WD 2.2
// geometry buffer layout (pass 0, one row): [0] phases xz,xy,xw,zw  [1] phase yz
//   [2 .. 129]  edges: slot e = i*4+k (64 slots, 32 used): pixel 2+2e = a.xyz (w: 1 valid / 0 absent), 2+2e+1 = b.xyz
//   [130 .. 273] faces: face f (24): 6 pixels each = clipped+projected verts (w = vertex count n, 0 = absent)
#define EDGE0 2.0
#define FACE0 130.0
#define VERT0 418.0
void rot(inout float a, inout float b, float th) { float c = cos(th), s = sin(th); float na = c * a - s * b; b = s * a + c * b; a = na; }
float gH, gW0, gW1, gRw, gPh; vec4 gA; float gB; vec3 gLp;
vec4 rot4(vec4 q) { rot(q.x, q.z, gA.x); rot(q.x, q.y, gA.y); rot(q.x, q.w, gA.z); rot(q.z, q.w, gA.w); rot(q.y, q.z, gB); return q; }
vec4 unrot4(vec4 q) { rot(q.y, q.z, -gB); rot(q.z, q.w, -gA.w); rot(q.x, q.w, -gA.z); rot(q.x, q.y, -gA.y); rot(q.x, q.z, -gA.x); return q; }
float pscale(float w) { return (WD * gH) / (WD * gH - w); }
vec3 projW(vec4 vw) { return vw.xyz * pscale(vw.w); }
vec4 axisVec(int k) { return vec4(k == 0 ? 1.0 : 0.0, k == 1 ? 1.0 : 0.0, k == 2 ? 1.0 : 0.0, k == 3 ? 1.0 : 0.0); }
vec4 vert(int i) { return vec4((i & 1) != 0 ? 1.0 : -1.0, (i & 2) != 0 ? 1.0 : -1.0, (i & 4) != 0 ? 1.0 : -1.0, (i & 8) != 0 ? 1.0 : -1.0) * gH; }
// the slice planes of the stack (Layers / Spread / Sweep), and the nearest one to a given w
float slicePlane(int i) {
    float N = floor(layers + 0.5), span = gW1 - gW0;
    float u = fract((float(i) + 0.5) / N + gPh);
    return gW0 + pow(u, mix(0.35, 2.85, spread)) * span;
}
float nearestSlice(float w) {
    float N = floor(layers + 0.5), best = gW0, bd = 1e9;
    for (int i = 0; i < 32; i++) { if (float(i) >= N) break; float t = slicePlane(i); float d = abs(w - t); if (d < bd) { bd = d; best = t; } }
    return best;
}
// THE MORPH: a rotated vertex, its w pulled toward the nearest slice plane by Connect. Only w moves; every face stays a face.
vec4 vertM(int i) { return rot4(vert(i)); }                 // geometry is never moved; the morph happens in the field
vec4 rd_(float x) { return IMG_PIXEL(ph, vec2(x + 0.5, 0.5)); }

// ── the tesseract: circumradius 2h ──
float sd4(vec4 q) { vec4 d = abs(q) - gH; return length(max(d, 0.0)) + min(max(max(d.x, d.y), max(d.z, d.w)), 0.0); }
float sdSection(vec3 p, float wc) { float s = pscale(wc); return sd4(unrot4(vec4(p / s, wc))) * s; }

int clipPoly(inout vec4 P[8], int n, float wlim, float sgn) {
    vec4 Q[8]; int m = 0;
    for (int i = 0; i < 8; i++) {
        if (i >= n) break;
        vec4 a = P[i]; vec4 b = P[(i + 1 < n) ? i + 1 : 0];
        float da = sgn * (a.w - wlim), db = sgn * (b.w - wlim);
        if (da >= 0.0) { Q[m] = a; m++; }
        if ((da >= 0.0) != (db >= 0.0) && abs(da - db) > 1e-9) { float t = da / (da - db); Q[m] = mix(a, b, t); m++; }
    }
    for (int i = 0; i < 8; i++) P[i] = Q[i];
    return m;
}
// the shared per-frame setup (both passes): sizes, window, light
void setup() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    float m = 0.04;
    float room = min(hf2.x, hf2.y) - m;
    float Rp = mix(0.03, max(room, 0.03), sizev);
    float protrude = 0.23 / (2.0 * WD / (WD - 1.0)) * 1.15;   // a FIXED reserve for the biggest sphere: sliders never resize the figure
    Rp /= (1.0 + protrude);
    float k = Rp * FOV;
    gRw = k * CAMZ / (1.0 + k);
    gH = gRw / (2.0 * WD / (WD - 1.0));
    float Wc = wpos * 2.0 * gH;
    float T = max(thick * 2.0 * gH, gH * 2e-4);
    gW0 = Wc - T; gW1 = Wc + T;
}
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
    vec3 pv = rd_(VERT0 + float(v)).xyz;
    for (int k = 0; k < 4; k++) {
        vec3 pn = rd_(VERT0 + float(v ^ (1 << k))).xyz;
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
vec3 marchSection(vec3 ro, vec3 rd, float wc, out vec3 n) {
    float b = dot(ro, rd), c2 = dot(ro, ro) - gRw * gRw * 1.1, disc = b * b - c2;
    n = vec3(0.0, 0.0, -1.0);
    if (disc <= 0.0) return vec3(0.0, 1e9, 0.0);
    float t = max(-b - sqrt(disc), 0.0), tFar = -b + sqrt(disc), d = 0.0, dmin = 9.0; vec3 p = ro;
    for (int i = 0; i < 40; i++) { p = ro + rd * t; d = sdSection(p, wc); dmin = min(dmin, d); if (d < 0.001 || t > tFar) break; t += d * 0.9; }
    float hit = (d < 0.001) ? 1.0 : 0.0;
    float cov = max(hit, 1.0 - smoothstep(0.0, 0.0025, dmin));
    float lum = 0.0;
    if (cov > 0.001) {
        vec2 e = vec2(0.002, 0.0);
        n = normalize(vec3(sdSection(p + e.xyy, wc) - sdSection(p - e.xyy, wc), sdSection(p + e.yxy, wc) - sdSection(p - e.yxy, wc), sdSection(p + e.yyx, wc) - sdSection(p - e.yyx, wc)));
        lum = mix(0.92, lit(p, n, rd), shade);
    }
    return vec3(cov, t, lum);
}
// ── PASS 0: phases, then the whole frame's geometry, once ──
void pass0() {
    float x = floor(gl_FragCoord.x);
    float dt = clamp(TIMEDELTA, 0.0, 0.1);
    float rt = turn * abs(turn) * 1.2, rs = spin * abs(spin) * 1.2;
    vec4 pA = rd_(0.0); float pB = rd_(1.0).x;
    vec4 nA = vec4(mod(pA.x + dt * rt, 2.0 * PI), mod(pA.y + dt * rt * 0.618, 2.0 * PI), mod(pA.z + dt * rs, 2.0 * PI), mod(pA.w + dt * rs * 0.618, 2.0 * PI));
    float nB = mod(pB + dt * rs * dbl, 2.0 * PI);
    float nS = fract(rd_(1.0).y + dt * sweep * abs(sweep) * 0.5);
    if (x < 1.0) { gl_FragColor = nA; return; }
    if (x < 2.0) { gl_FragColor = vec4(nB, nS, 0.0, 1.0); return; }
    gA = nA; gB = nB; gPh = nS; setup();
    if (x < FACE0) {                                         // an edge endpoint
        float e = floor((x - EDGE0) * 0.5); float which = mod(x - EDGE0, 2.0);
        int ei = int(e); int i = ei / 4; int k = ei - i * 4;
        if ((i & (1 << k)) != 0) { gl_FragColor = vec4(0.0); return; }   // not an edge slot
        vec4 aw = vertM(i), bw = vertM(i + (1 << k));
        float wa = aw.w, wb = bw.w, t0 = 0.0, t1 = 1.0, dw = wb - wa;
        if (abs(dw) < 1e-6) { if (wa < gW0 || wa > gW1) { gl_FragColor = vec4(0.0); return; } }
        else { float ta = (gW0 - wa) / dw, tb = (gW1 - wa) / dw; t0 = max(0.0, min(ta, tb)); t1 = min(1.0, max(ta, tb)); if (t1 <= t0) { gl_FragColor = vec4(0.0); return; } }
        vec3 v = projW(mix(aw, bw, (which < 0.5) ? t0 : t1));
        gl_FragColor = vec4(v, 1.0); return;
    }
    if (x >= VERT0) {                                        // a vertex: projected, w = 1 if inside the window
        int i = int(x - VERT0); vec4 v = vertM(i);
        gl_FragColor = vec4(projW(v), (v.w >= gW0 && v.w <= gW1) ? 1.0 : 0.0); return;
    }
    // a tesseract face vertex: 48 triangles, two per square (a folded square is no longer flat; its triangles are)
    float f = floor((x - FACE0) / 6.0); float q = mod(x - FACE0, 6.0);
    int fi = int(f); int tri = fi - (fi / 2) * 2; fi = fi / 2;
    int pi_ = fi / 4; int sk = (fi - pi_ * 4) / 2; int sl = fi - pi_ * 4 - sk * 2;
    int i, j, k, l;
    if (pi_ == 0) { i = 0; j = 1; k = 2; l = 3; } else if (pi_ == 1) { i = 0; j = 2; k = 1; l = 3; } else if (pi_ == 2) { i = 0; j = 3; k = 1; l = 2; }
    else if (pi_ == 3) { i = 1; j = 2; k = 0; l = 3; } else if (pi_ == 4) { i = 1; j = 3; k = 0; l = 2; } else { i = 2; j = 3; k = 0; l = 1; }
    vec4 ei_ = axisVec(i) * gH, ej = axisVec(j) * gH;
    vec4 base = (axisVec(k) * (sk == 0 ? -1.0 : 1.0) + axisVec(l) * (sl == 0 ? -1.0 : 1.0)) * gH;
    // the square's four corners as vertex indices, morphed
    int c0 = 0, c1 = 0, c2 = 0, c3 = 0;
    for (int b = 0; b < 4; b++) {
        int bit = 1 << b;
        bool onK = (b == k), onL = (b == l), onI = (b == i), onJ = (b == j);
        if (onK && sk == 1) { c0 += bit; c1 += bit; c2 += bit; c3 += bit; }
        if (onL && sl == 1) { c0 += bit; c1 += bit; c2 += bit; c3 += bit; }
        if (onI) { c1 += bit; c2 += bit; }
        if (onJ) { c2 += bit; c3 += bit; }
    }
    vec4 P[8];
    vec4 Q0 = vertM(c0), Q1 = vertM(c1), Q2 = vertM(c2), Q3 = vertM(c3);
    if (tri == 0) { P[0] = Q0; P[1] = Q1; P[2] = Q2; } else { P[0] = Q0; P[1] = Q2; P[2] = Q3; }
    int n = 3;
    n = clipPoly(P, n, gW0, 1.0); if (n >= 3) n = clipPoly(P, n, gW1, -1.0);
    if (n < 3 || int(q) >= n) { gl_FragColor = vec4(0.0, 0.0, 0.0, (n < 3) ? 0.0 : float(n)); return; }
    // EROSION (Connect's second half): every wall shrinks toward its own center — geometry, not opacity
    float erode = min(smoothstep(0.5, 1.0, connect), 0.985);   // never fully degenerate: a zero-area wall would NaN the ray
    vec3 cen = vec3(0.0); for (int m_ = 0; m_ < 8; m_++) { if (m_ < n) cen += projW(P[m_]); } cen /= float(n);
    vec3 v = vec3(0.0);
    for (int m_ = 0; m_ < 8; m_++) { if (m_ == int(q)) v = mix(projW(P[m_]), cen, erode); }
    gl_FragColor = vec4(v, float(n));
}
// ── the layered walls: the stack of cross-sections through w. Fill lofts each gap toward the continuous hull ──
float stackField(vec3 p, float fill) {
    float dmin = 1e9, span = gW1 - gW0, acc = 0.0, dprev = 0.0;
    float N = floor(layers + 0.5);
    for (int i = 0; i < 32; i++) {
        if (float(i) >= N) break;
        float u0 = fract((float(i) + 0.5) / N + gPh), u1 = fract((float(i) + 1.5) / N + gPh);
        float e = mix(0.35, 2.85, spread);
        u0 = pow(u0, e); u1 = pow(u1, e);
        acc += drift * 0.8 * max(dprev, 0.0);
        float t0 = gW0 + u0 * span + acc;
        if (t0 > gW1 || t0 >= WD * gH * 0.95) break;
        float t1 = (u1 > u0) ? gW0 + u1 * span + acc : gW1;    // the next slice (or the window's end) — the gap to loft
        float d = 1e9;
        for (int k = 0; k < 3; k++) {                        // Fill: sample the loft between this slice and the next
            float t = mix(t0, min(t1, gW1), fill * float(k) / 2.0);
            if (k > 0 && fill < 0.001) break;
            float sc = pscale(t);
            d = min(d, sd4(unrot4(vec4(p / sc, t))) * sc);
        }
        dmin = min(dmin, d); dprev = d;
    }
    return dmin;
}
// the stack (from the shell): a thin shell around the layered solid, Fill lofts the gaps toward the hull
float gFill;
float shellField(vec3 p) { return abs(stackField(p, gFill)) - gH * 0.012; }
vec3 shellNorm(vec3 p) { vec2 e = vec2(0.003, 0.0); return normalize(vec3(shellField(p + e.xyy) - shellField(p - e.xyy), shellField(p + e.yxy) - shellField(p - e.yxy), shellField(p + e.yyx) - shellField(p - e.yyx))); }
// a small depth-sorted list of translucent hits
#define NH 8
float hT[NH]; float hL[NH]; float hA[NH]; vec3 hN[NH]; int hCount;
void addHit(float t, float l, float a, vec3 n) {
    if (a < 0.001) return;
    int pos = hCount < NH ? hCount : NH - 1;
    if (hCount >= NH && t >= hT[NH - 1]) return;
    for (int i = NH - 1; i > 0; i--) { if (i <= pos && hT[i - 1] > t) { hT[i] = hT[i - 1]; hL[i] = hL[i - 1]; hA[i] = hA[i - 1]; hN[i] = hN[i - 1]; pos = i - 1; } }
    hT[pos] = t; hL[pos] = l; hA[pos] = a; hN[pos] = n;
    if (hCount < NH) hCount++;
}
void main() {
    if (PASSINDEX == 0) { pass0(); return; }
    gA = rd_(0.0); vec4 p1 = rd_(1.0); gB = p1.x; gPh = p1.y; setup();
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;
    float Rp = (gRw / (CAMZ - gRw)) / FOV;                   // the figure's projected radius
    float protrude = 0.23 / (2.0 * WD / (WD - 1.0)) * 1.15;
    if (length(uv) > Rp * (1.0 + protrude) * 1.06 + 3.0 / RENDERSIZE.y) { gl_FragColor = vec4(0.0); return; }
    vec3 sd = sunDir(); gLp = sd * gRw * mix(1.35, 30.0, distance);
    vec3 ro = vec3(0.0, 0.0, -CAMZ), rd = normalize(vec3(uv * FOV, 1.0));
    float pxw = (1.0 / RENDERSIZE.y) * CAMZ * FOV;

    // ── FRAME (analytic) + SHELL (marched), merged by depth ──
    gFill = 1.0 - smoothstep(0.0, 0.6, connect);            // the shell: filled hull → terraces
    float erode = smoothstep(0.5, 1.0, connect);             // the frame: walls shrink (pass 0), edges thin, cuts fade
    hCount = 0; for (int i = 0; i < NH; i++) hT[i] = 1e9;

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
    if (rE > 1e-5) for (int e = 0; e < 64; e++) {
        float base = EDGE0 + float(2 * e);
        vec4 a4 = rd_(base); if (a4.w < 0.5) continue;
        vec3 a = a4.xyz, b = rd_(base + 1.0).xyz;
        int va = e / 4, vb = va + (1 << (e - va * 4));         // the two corners this bar joins
        vec3 d = normalize(b - a); float L = length(b - a);
        // cull: the ray must pass near the extended bar
        vec3 hq = raySeg(ro, rd, a - d * rE * 3.0, b + d * rE * 3.0);
        if (hq.x > rE * 1.5 + pxw) continue;
        // the profile's frame: sides aligned with the walls, from a neighbouring edge at corner a
        vec3 pv = rd_(VERT0 + float(va)).xyz, ref = vec3(0.0, 1.0, 0.0);
        for (int k = 0; k < 4; k++) { vec3 pn = rd_(VERT0 + float(va ^ (1 << k))).xyz; vec3 dj = normalize(pn - pv); if (abs(dot(dj, d)) < 0.99) { ref = dj; break; } }
        vec3 u = normalize(cross(d, ref)); vec3 v = cross(u, d);
        vec2 n2; float dm2;
        float t = rayTube(ro, rd, a, u, v, rE, rE * roundv, n2, dm2);
        if (t <= 0.0 || t >= tE) continue;
        vec3 p = ro + rd * t;
        float s_ = dot(p - a, d);
        if (s_ < -rE * 3.0 || s_ > L + rE * 3.0) continue;
        if (s_ < rE * 3.0 && !keptAtCorner(p, va, d)) continue;          // mitered at corner a
        if (s_ > L - rE * 3.0 && !keptAtCorner(p, vb, -d)) continue;     // mitered at corner b
        float cov = 1.0 - smoothstep(0.0, pxw, max(dm2, 0.0));
        if (cov > 0.001) { tE = t; covE = cov; pE = p; nE = normalize(u * n2.x + v * n2.y); }
    }
    float lumE = (covE > 0.001) ? mix(0.92, lit(pE, nE, rd), shade) : 0.0;

    // walls (already eroded in pass 0)
    if (faces > 0.001) for (int f = 0; f < 48; f++) {
        float fb = FACE0 + float(f * 6);
        vec4 v0 = rd_(fb); int n = int(v0.w + 0.5); if (n < 3) continue;
        vec3 V[6]; V[0] = v0.xyz;
        for (int q = 1; q < 6; q++) V[q] = (q < n) ? rd_(fb + float(q)).xyz : V[0];
        vec3 cr = cross(V[1] - V[0], V[2] - V[0]); if (dot(cr, cr) < 1e-12) continue;   // degenerate (eroded away)
        vec3 nrm = normalize(cr);
        float den = dot(rd, nrm); if (abs(den) < 1e-6) continue;
        float t = dot(V[0] - ro, nrm) / den; if (!(t > 0.0 && t < tE)) continue;
        vec3 p = ro + rd * t; float mn = 1e9, mx = -1e9;
        for (int q = 0; q < 6; q++) { if (q >= n) break; vec3 a = V[q], b = V[(q + 1 < n) ? q + 1 : 0]; float sg = dot(cross(b - a, p - a), nrm); mn = min(mn, sg); mx = max(mx, sg); }
        if (!(mn >= 0.0 || mx <= 0.0)) continue;
        vec3 nf = (dot(nrm, rd) < 0.0) ? nrm : -nrm;
        addHit(t, mix(0.92, lit(p, nf, rd), shade), faces, nf);
    }
    // cuts (the window's end caps), fading with the erosion
    float open_ = smoothstep(0.0, 0.12, thick);
    float cutA = mix(1.0, faces, open_) * (1.0 - erode);
    float wMax = min(2.0 * gH, WD * gH * 0.9);
    float T = (gW1 - gW0) * 0.5;
    vec3 n0, n1;
    if (cutA > 0.001 && abs(gW0) <= wMax) { vec3 s0 = marchSection(ro, rd, gW0, n0); if (s0.x > 0.001 && s0.y < tE) addHit(s0.y, s0.z, cutA * s0.x, n0); }
    if (cutA > 0.001 && abs(gW1) <= wMax && T > gH * 1e-3) { vec3 s1 = marchSection(ro, rd, gW1, n1); if (s1.x > 0.001 && s1.y < tE) addHit(s1.y, s1.z, cutA * s1.x, n1); }

    // the shell: marched through up to 4 surfaces; at Connect 0 it lies on the outer walls, so it eases in there
    float shellA = faces * smoothstep(0.0, 0.1, connect);
    if (shellA > 0.001) {
        float b = dot(ro, rd), c2 = dot(ro, ro) - gRw * gRw * 1.1, disc = b * b - c2;
        if (disc > 0.0) {
            float t = max(-b - sqrt(disc), 0.0), tFar = min(-b + sqrt(disc), tE); int hits = 0;
            for (int i = 0; i < 40; i++) {
                if (t > tFar || hits >= 4) break;
                vec3 p = ro + rd * t; float d = shellField(p);
                if (d < 0.001) { vec3 n = shellNorm(p); if (dot(n, rd) > 0.0) n = -n;
                    addHit(t, mix(0.92, lit(p, n, rd), shade), shellA, n); t += gH * 0.05; hits++; continue; }
                t += d * 0.8;
            }
        }
    }
    // composite front to back, the opaque edge last
    float Tr = 1.0, Aacc = 0.0, Cacc = 0.0; vec3 nacc = vec3(0.0);
    for (int i = 0; i < NH; i++) { if (i >= hCount) break; float a = hA[i]; Aacc += Tr * a; Cacc += Tr * a * hL[i]; nacc += Tr * a * hN[i]; Tr *= (1.0 - a); }
    if (covE > 0.001) { Aacc += Tr * covE; Cacc += Tr * covE * lumE; nacc += Tr * covE * nE; }
    if (Aacc < 0.001) { gl_FragColor = vec4(0.0); return; }
    float lum = Cacc / Aacc; vec3 n = normalize(nacc + vec3(0.0, 0.0, -1e-4));
    vec3 body = vec3(lum);
    if (colorm == 1) body = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
    if (wet > 0.001) body = mix(body, 0.5 + 0.5 * cos(2.0 * PI * (body * loopv + hue + vec3(rOff, gOff, bOff))), wet);
    gl_FragColor = vec4(body * Aacc, Aacc);
}