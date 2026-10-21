/*{
  "DESCRIPTION": "SP Atom 4D Field - window in w over a 4D distance-field catalog: any figure morphs to any figure, smoothly. The projected slab rendered as a STACK of N cross-sections through w (Layers/Spread/Sweep), front + back, Faces = opacity. Turn/Spin/Double/Sweep are POSITIONS (the heart drives), X/Y, Perspective, Sun/Height/Distance, Faces/Edges/Round/Vertices, Shade/Rim/Haze/Halo/Focus, Material (smooth/stone/crystal/glass) Micro/Fine, Color stack + Depth hue. Contained. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "figA",
      "LABEL": "Figure A",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5
      ],
      "LABELS": [
        "tesseract",
        "4-sphere",
        "duocylinder",
        "16-cell",
        "4D torus",
        "24-cell"
      ]
    },
    {
      "NAME": "figB",
      "LABEL": "Figure B",
      "TYPE": "long",
      "DEFAULT": 4,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5
      ],
      "LABELS": [
        "tesseract",
        "4-sphere",
        "duocylinder",
        "16-cell",
        "4D torus",
        "24-cell"
      ]
    },
    {
      "NAME": "morph",
      "LABEL": "Morph",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
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
      "MIN": 0.0,
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
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "spin",
      "LABEL": "Spin",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
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
      "NAME": "posx",
      "LABEL": "X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "posy",
      "LABEL": "Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "persp",
      "LABEL": "Perspective",
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
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "edgesv",
      "LABEL": "Edges",
      "TYPE": "float",
      "DEFAULT": 0.0,
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
      "NAME": "shade",
      "LABEL": "Shade",
      "TYPE": "float",
      "DEFAULT": 0.8,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rim",
      "LABEL": "Rim",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "haze",
      "LABEL": "Haze",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "halo",
      "LABEL": "Halo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "focus",
      "LABEL": "Focus",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "material",
      "LABEL": "Material",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "smooth",
        "stone",
        "crystal",
        "glass"
      ]
    },
    {
      "NAME": "micro",
      "LABEL": "Micro",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fine",
      "LABEL": "Fine",
      "TYPE": "float",
      "DEFAULT": 0.5,
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
      "NAME": "depthc",
      "LABEL": "Depth",
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
      "WIDTH": 242,
      "HEIGHT": 1
    },
    {}
  ]
}*/

#define PI 3.14159265
#define FOV 1.1
float gCamZ, gWD;                                            // Perspective: camera distance and 4D projection distance, together
void rot(inout float a, inout float b, float th) { float c = cos(th), s = sin(th); float na = c * a - s * b; b = s * a + c * b; a = na; }
#define EDGE0 2.0
#define VERT0 130.0
#define RIM0 146.0
#define NRIM 48
float gH, gW0, gW1, gRw, gPh; vec4 gA; float gB; vec3 gLp;
float h31(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float n3(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(h31(i), h31(i + vec3(1,0,0)), f.x), mix(h31(i + vec3(0,1,0)), h31(i + vec3(1,1,0)), f.x), f.y),
               mix(mix(h31(i + vec3(0,0,1)), h31(i + vec3(1,0,1)), f.x), mix(h31(i + vec3(0,1,1)), h31(i + vec3(1,1,1)), f.x), f.y), f.z); }
// the material's relief and surface normal (ported from the 3d solid): stone pores, crystal facets, glass frost
float relief(vec3 po) { float sc = mix(10.0, 80.0, fine) / max(gH * 4.0, 1e-3);
    if (material == 1) { float pores = 1.0 - smoothstep(0.40, 0.75, n3(po * sc * 1.3 + 31.7)); return pores * 0.7 + n3(po * sc * 4.0 + 7.3) * 0.3; }
    if (material == 3) return n3(po * sc * 2.0) * 0.5;
    return n3(po * sc) * 0.6 + n3(po * sc * 4.1 + 7.3) * 0.4; }
vec3 surface(vec3 p, vec3 n) {
    if (material == 2) { float k = mix(2.0, 7.0, fine); vec3 f = normalize(floor(n * k + 0.5) / k + 0.0001); return normalize(mix(n, f, micro)); }
    if (micro < 0.001) return n;
    float e = 0.35 / mix(10.0, 80.0, fine) * max(gH * 4.0, 1e-3);
    vec3 g = vec3(relief(p + vec3(e, 0, 0)) - relief(p - vec3(e, 0, 0)), relief(p + vec3(0, e, 0)) - relief(p - vec3(0, e, 0)), relief(p + vec3(0, 0, e)) - relief(p - vec3(0, 0, e)));
    return normalize(n + g * micro * 1.4); }
vec4 rot4(vec4 q) { rot(q.x, q.z, gA.x); rot(q.x, q.y, gA.y); rot(q.x, q.w, gA.z); rot(q.z, q.w, gA.w); rot(q.y, q.z, gB); return q; }
vec4 axisVec(int k) { return vec4(k == 0 ? 1.0 : 0.0, k == 1 ? 1.0 : 0.0, k == 2 ? 1.0 : 0.0, k == 3 ? 1.0 : 0.0); }
vec4 rd_(float x) { return IMG_PIXEL(ph, vec2(x + 0.5, 0.5)); }
vec4 vert(int i) { return vec4((i & 1) != 0 ? 1.0 : -1.0, (i & 2) != 0 ? 1.0 : -1.0, (i & 4) != 0 ? 1.0 : -1.0, (i & 8) != 0 ? 1.0 : -1.0) * gH; }
vec4 vertM(int i) { return rot4(vert(i)); }
vec3 projW(vec4 vw) { return vw.xyz * ((gWD * gH) / (gWD * gH - vw.w)); }
vec4 unrot4(vec4 q) { rot(q.y, q.z, -gB); rot(q.z, q.w, -gA.w); rot(q.x, q.w, -gA.z); rot(q.x, q.y, -gA.y); rot(q.x, q.z, -gA.x); return q; }
float pscale(float w) { return (gWD * gH) / (gWD * gH - w); }
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
        if (t > gW1 || t >= gWD * gH * 0.95) break;
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
float gAlpha = 1.0;                                          // glass: the material's own transparency, set by lit()
float lit(vec3 p, vec3 n0, vec3 rd) {
    vec3 n = surface(p, n0);
    vec3 Lv = gLp - p; float Ld2 = dot(Lv, Lv); vec3 L = Lv * inversesqrt(Ld2);
    float D = length(gLp); float att = clamp((D - gRw) * (D - gRw) / Ld2, 0.0, 1.0);
    float lam = clamp(dot(n, L), 0.0, 1.0) * att;
    float facing = clamp(dot(n, -rd), 0.0, 1.0);
    float rimL = pow(1.0 - facing, 2.0), fres = pow(1.0 - facing, 4.0);
    float specPow = mix(10.0, 40.0, distance);
    float spec = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow) * att;
    float vol; gAlpha = 1.0;
    if (material == 1) { float occ = (micro > 0.001) ? 1.0 - micro * 0.5 * relief(p) : 1.0; vol = (0.10 + 0.85 * lam + 0.10 * rimL) * occ; }
    else if (material == 2) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.8) * att; vol = 0.10 + 0.45 * lam + 0.55 * fres + 1.2 * sp2; }
    else if (material == 3) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.4) * att; float frost = micro * 0.6;
        vol = 0.9 * fres + 1.3 * sp2 * (1.0 - frost * 0.7) + frost * (0.2 + 0.4 * lam); gAlpha = clamp(0.12 + 0.88 * fres + sp2 + frost, 0.0, 1.0); }
    else { vol = 0.14 + 0.72 * lam + 0.30 * rimL * (1.0 + 0.8 * micro) + spec * (0.35 + 0.8 * micro);
        if (micro > 0.001) { float gn = n3(p * 90.0 / max(gH * 4.0, 1e-3)); vol *= 1.0 + micro * 0.30 * (gn - 0.5) * (0.5 + rimL); } }
    vol += rim * pow(1.0 - facing, 3.0) * 0.9;               // Rim: a light from behind, on the silhouette only
    return vol;
}
void setup() {
    gCamZ = mix(3.2, 1.55, persp); gWD = mix(2.2, 2.04, persp);   // Perspective: the 3D camera comes right in (contained by the bounding sphere); the 4D distance only nudges — a vertex must stay in front of the 4D eye (|w| <= 2H)
    float asp = RENDERSIZE.x / RENDERSIZE.y; vec2 hf2 = vec2(0.5 * asp, 0.5); float m = 0.04;
    // All primitives and rotated vertices fit a radius-2H hypersphere.
    // Its 4D perspective projection has this phase/window-independent bound.
    // Include extended square bars (3*.09 + sqrt(2)*.09 < .40) and vertices.
    float projectedBound = 2.0 * gWD / sqrt(gWD * gWD - 4.0) + 0.42;
    float fringe = 0.025; // reserve for source antialiasing, separate from framing margin
    float room = min(hf2.x, hf2.y) - m - fringe;
    float Rp = mix(0.03, max(room, 0.03), sizev);
    float k = Rp * FOV;
    gRw = k * gCamZ / sqrt(1.0 + k * k);
    gH = gRw / projectedBound;
    float Wc = wpos * 2.0 * gH;
    float T = max(thick * 2.0 * gH, gH * 2e-4);
    gW0 = max(Wc - T, -2.2 * gH); gW1 = min(Wc + T, gWD * gH * 0.9);
}
void main() {
    if (PASSINDEX == 0) {
        float x = floor(gl_FragCoord.x);
        // POSITIONS: Turn / Spin / Double are phases (1 = a full turn), Sweep the stack's phase. Nothing here has a clock: the heart drives.
        vec4 nA = vec4(turn, turn * 0.618, spin, spin * 0.618) * 2.0 * PI;
        float nB = dbl * 2.0 * PI, nS = sweep;
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
    float Rp = gRw / sqrt(gCamZ * gCamZ - gRw * gRw) / FOV;
    float Rc = Rp + 0.025;
    vec2 room2 = max(vec2(0.5 * asp, 0.5) - Rc - 0.04, vec2(0.0));
    uv -= vec2(posx, posy) * room2;
    // Conservative ray rejection outside the complete source + AA envelope.
    // This is tested against an uncullled render; downstream FX are unrestricted.
    if (length(uv) > Rc) { gl_FragColor = vec4(0.0); return; }
    vec3 sd = sunDir(); gLp = sd * gRw * mix(1.35, 30.0, distance);
    vec3 ro = vec3(0.0, 0.0, -gCamZ), rd = normalize(vec3(uv * FOV, 1.0));
    float pxw = (1.0 / RENDERSIZE.y) * gCamZ * FOV;
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
        float pxF = pxw * (1.0 + focus * 14.0 * abs(t - gCamZ) / max(gRw, 1e-3));   // Focus: soft away from the figure's centre depth
        float cov = 1.0 - smoothstep(0.0, pxF, max(dm2, 0.0));
        if (cov > 0.001) { tE = t; covE = cov; pE = p; nE = normalize(u * n2.x + v * n2.y); }
    }
    float lumE = (covE > 0.001) ? mix(0.92, lit(pE, nE, rd), shade) : 0.0;
    // Halo: where a nearer bar passes in front, cut a gap of width Halo around it in everything behind (the haloed-line cue)
    float haloW = gH * 0.09 * halo * 1.6;
    float tHalo = 1e9;                                       // the depth of the nearest bar whose halo band this pixel is in
    if (haloW > 1e-5 && rE > 1e-5) for (int e = 0; e < 64 + NRIM; e++) {
        float base = (e >= 64) ? RIM0 + float(2 * (e - 64)) : EDGE0 + float(2 * e);
        vec4 a4 = rd_(base); if (a4.w < 0.5) continue;
        vec3 hq = raySeg(ro, rd, a4.xyz, rd_(base + 1.0).xyz);
        if (hq.z < 0.0 || hq.z > 1.0) continue;
        if (hq.x > rE + pxw && hq.x < rE + haloW) tHalo = min(tHalo, hq.y);
    }
    if (covE > 0.001 && tE > tHalo + rE * 2.0) covE = 0.0;

    // march the shell inside the bounding sphere, stopping at the opaque bars
    float b = dot(ro, rd), c2 = dot(ro, ro) - gRw * gRw * 1.1, disc = b * b - c2;
    if (disc <= 0.0 && covE < 0.001) { gl_FragColor = vec4(0.0); return; }
    float t = max(-b - sqrt(max(disc, 0.0)), 0.0), tFar = min(-b + sqrt(max(disc, 0.0)), tE), d = 0.0, dmin = 9.0; vec3 p = ro;
    for (int i = 0; i < 56; i++) { p = ro + rd * t; d = field(p); dmin = min(dmin, d); if (d < 0.001 || t > tFar) break; t += d * 0.7; }
    float hit = (d < 0.001) ? 1.0 : 0.0;
    float cover = (disc > 0.0) ? max(hit, 1.0 - smoothstep(0.0, 0.0025 * (1.0 + focus * 14.0 * abs(t - gCamZ) / max(gRw, 1e-3)), dmin)) : 0.0;
    if (cover > 0.001 && t > tHalo + rE * 2.0) cover = 0.0;  // the face behind a near bar's halo
    if (cover < 0.001 && covE < 0.001) { gl_FragColor = vec4(0.0); return; }
    if (cover < 0.001) {                                     // only a bar or a vertex on this ray
        float fz = clamp((tE - (gCamZ - gRw)) / max(2.0 * gRw, 1e-3), 0.0, 1.0);   // 0 nearest … 1 farthest, inside the figure
        vec3 bodyE = vec3(mix(lumE, 0.5, haze * fz));      // Haze: contrast compresses with depth (aerial perspective)
        if (colorm == 1) bodyE = (nE * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
        if (wet > 0.001) bodyE = mix(bodyE, 0.5 + 0.5 * cos(2.0 * PI * (bodyE * loopv + hue + depthc * fz + vec3(rOff, gOff, bOff))), wet);   // Depth: hue walks with depth (chromostereopsis)
        gl_FragColor = vec4(bodyE * covE, covE); return;
    }
    vec3 nF = fnorm(p);
    float lumF = mix(0.92, lit(p, nF, rd), shade); float alphaF = gAlpha;
    float aF = clamp(faces, 0.0, 1.0) * mix(1.0, alphaF, shade);   // glass: the material thins the shell                        // Faces: shell opacity, all the way from clear to solid (as in the hybrid)
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
    float fz = clamp((t - (gCamZ - gRw)) / max(2.0 * gRw, 1e-3), 0.0, 1.0);
    vec3 body = vec3(mix(lum, 0.5, haze * fz));
    if (colorm == 1) body = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
    if (wet > 0.001) body = mix(body, 0.5 + 0.5 * cos(2.0 * PI * (body * loopv + hue + depthc * fz + vec3(rOff, gOff, bOff))), wet);
    gl_FragColor = vec4(body * A, A);
}
