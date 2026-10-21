#!/usr/bin/env python3
"""make_figure3d_atom.py — SP Atom Figure 3D, the hyper-real pass (2026-09-02).
EFFECT on a Video Router (needs what is BEHIND it: refraction / reflection / caustics).
Sections: Figure · Body · Light · Material · Color · Line · Alpha (clip-wide).
Materials are substances with material-science microstructure:
  smooth  chrome — env reflection, anisotropic brushed micro-abrasions
  stone   limestone — multi-scale tonal fbm, pits (cell noise), calcite specks, fossil streaks, AO in the pits
  crystal facets, three-wavelength dispersion, internal planar fractures + inclusions
  glass   refraction w/ thickness + dispersion, Schlick fresnel, thick rim, studio window reflections, dust/scratches
  water   animated ripple normals, glint sparkles (thresholded high-power spec), caustics on the transmitted image,
          Beer-Lambert teal absorption
No drives, no slot machinery. Judged live on the layer."""
import json, os, subprocess, sys

NAME = "SP Atom 3D"
FIGS = ["torus", "sphere", "box", "octahedron", "tetrahedron", "icosahedron", "dodecahedron"]
INPUTS = [
    {"NAME": "inputImage", "LABEL": "Behind", "TYPE": "image"},
    {"NAME": "figA",   "LABEL": "Figure A", "TYPE": "long", "DEFAULT": 0, "VALUES": list(range(7)), "LABELS": FIGS},
    {"NAME": "figB",   "LABEL": "Figure B", "TYPE": "long", "DEFAULT": 5, "VALUES": list(range(7)), "LABELS": FIGS},
    {"NAME": "morph",  "LABEL": "Morph",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",  "LABEL": "Size",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "px",     "LABEL": "X",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "py",     "LABEL": "Y",        "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "tumble", "LABEL": "Tumble",   "TYPE": "float", "DEFAULT": 0.2, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "axisv",  "LABEL": "Axis",     "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sun",    "LABEL": "Sun",      "TYPE": "float", "DEFAULT": 0.9, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "height", "LABEL": "Height",   "TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "distance","LABEL": "Distance","TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "shadow", "LABEL": "Shadow",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "material","LABEL": "Material","TYPE": "long",  "DEFAULT": 3, "VALUES": [0, 1, 2, 3, 4], "LABELS": ["smooth", "stone", "crystal", "glass", "water"]},
    {"NAME": "micro",  "LABEL": "Micro",    "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "fine",   "LABEL": "Fine",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "colorm", "LABEL": "Color",    "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["natural", "gray", "loop", "normal"]},
    {"NAME": "loopv",  "LABEL": "Loop",     "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 4.0},
    {"NAME": "hue",    "LABEL": "Hue",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "rOff",   "LABEL": "Red",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gOff",   "LABEL": "Green",    "TYPE": "float", "DEFAULT": 0.33, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bOff",   "LABEL": "Blue",     "TYPE": "float", "DEFAULT": 0.67, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "shade",  "LABEL": "Shade",    "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "edge",   "LABEL": "Edge",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "emboss", "LABEL": "Emboss",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "alphav", "LABEL": "Alpha",    "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
]

BODY = r"""
#define PHI 1.6180339887
#define CAMZ 3.2
#define FOV 1.1
#define PI 3.14159265

// ───────────────────────── noise kit ─────────────────────────
float spH3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
vec3  spH33(vec3 p) { return vec3(spH3(p), spH3(p + 19.19), spH3(p + 47.3)); }
float spN3(vec3 p) {
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(spH3(i), spH3(i + vec3(1, 0, 0)), f.x), mix(spH3(i + vec3(0, 1, 0)), spH3(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(spH3(i + vec3(0, 0, 1)), spH3(i + vec3(1, 0, 1)), f.x), mix(spH3(i + vec3(0, 1, 1)), spH3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float spFbm3(vec3 p) { return 0.5 * spN3(p) + 0.25 * spN3(p * 2.07 + 3.1) + 0.125 * spN3(p * 4.13 + 7.7) + 0.0625 * spN3(p * 8.29 + 11.3); }
float spRidge3(vec3 p) { float r = 0.0, a = 0.5; for (int k = 0; k < 3; k++) { r += a * (1.0 - abs(2.0 * spN3(p) - 1.0)); p = p * 2.1 + 5.3; a *= 0.5; } return r; }
// cell noise: F1 distance and the cell id — pits, inclusions, fracture planes
vec2 spCell(vec3 p) {
    vec3 ip = floor(p), fp = fract(p); float m = 8.0, id = 0.0;
    for (int k = -1; k <= 1; k++) for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
        vec3 g = vec3(float(i), float(j), float(k)); vec3 o = spH33(ip + g);
        float d = length(g + o - fp); if (d < m) { m = d; id = spH3(ip + g + 3.3); }
    }
    return vec2(m, id);
}

// ───────────────────────── figures (circumradius = r) ─────────────────────────
vec3 spRotAA(vec3 p, vec3 ax, float th) { float c = cos(th), s = sin(th); return p * c + cross(ax, p) * s + ax * dot(ax, p) * (1.0 - c); }
float spGdf(vec3 p, vec3 n) { return abs(dot(p, normalize(n))); }
float spFig(int f, vec3 p, float r) {
    if (f == 0) { vec2 q = vec2(length(p.xz) - r * 0.72, p.y); return length(q) - r * 0.28; }
    if (f == 1) return length(p) - r;
    if (f == 2) { vec3 q = abs(p) - r * 0.554; return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r * 0.04; }
    if (f == 3) return (abs(p.x) + abs(p.y) + abs(p.z) - r) * 0.57735;
    if (f == 4) {
        float d = dot(p, normalize(vec3(1, 1, 1)));
        d = max(d, dot(p, normalize(vec3(-1, -1, 1)))); d = max(d, dot(p, normalize(vec3(-1, 1, -1)))); d = max(d, dot(p, normalize(vec3(1, -1, -1))));
        return d - r * 0.3333;
    }
    if (f == 5) {
        float d = spGdf(p, vec3(1, 1, 1));
        d = max(d, spGdf(p, vec3(-1, 1, 1))); d = max(d, spGdf(p, vec3(1, -1, 1))); d = max(d, spGdf(p, vec3(1, 1, -1)));
        d = max(d, spGdf(p, vec3(0, 1, PHI + 1.0))); d = max(d, spGdf(p, vec3(0, -1, PHI + 1.0)));
        d = max(d, spGdf(p, vec3(PHI + 1.0, 0, 1))); d = max(d, spGdf(p, vec3(-(PHI + 1.0), 0, 1)));
        d = max(d, spGdf(p, vec3(1, PHI + 1.0, 0))); d = max(d, spGdf(p, vec3(-1, PHI + 1.0, 0)));
        return d - r * 0.7947;
    }
    float d = spGdf(p, vec3(0, PHI, 1));
    d = max(d, spGdf(p, vec3(0, -PHI, 1))); d = max(d, spGdf(p, vec3(1, 0, PHI))); d = max(d, spGdf(p, vec3(-1, 0, PHI)));
    d = max(d, spGdf(p, vec3(PHI, 1, 0))); d = max(d, spGdf(p, vec3(-PHI, 1, 0)));
    return d - r * 0.7947;
}
float gR; vec3 gAxis; float gTh; vec3 gLp; float gRp;
vec3 spObj(vec3 p) { return spRotAA(p, gAxis, gTh); }
vec3 spWorldDir(vec3 v) { return spRotAA(v, gAxis, -gTh); }
float spMap(vec3 p) { vec3 q = spObj(p); return mix(spFig(figA, q, gR), spFig(figB, q, gR), morph); }
vec3 spNorm(vec3 p) { vec2 e = vec2(0.0015, 0.0); return normalize(vec3(spMap(p + e.xyy) - spMap(p - e.xyy), spMap(p + e.yxy) - spMap(p - e.yxy), spMap(p + e.yyx) - spMap(p - e.yyx))); }
vec3 spRay(vec2 uv) { return normalize(vec3(uv * FOV, 1.0)); }
float spMarch(vec2 uv, out vec3 p, out float dmin) {
    vec3 ro = vec3(0.0, 0.0, -CAMZ), rd = spRay(uv); float t = 0.0, d = 0.0; dmin = 9.0;
    for (int i = 0; i < 90; i++) { p = ro + rd * t; d = spMap(p); dmin = min(dmin, d); if (d < 0.0008 || t > 7.0) break; t += d * 0.85; }
    return (d < 0.0008) ? 1.0 : 0.0;
}
float spThickness(vec3 p, vec3 rd) {                        // march INSIDE from the entry point to the exit
    float t = 0.01;
    for (int i = 0; i < 28; i++) { float d = -spMap(p + rd * t); if (d < 0.001) break; t += max(d * 0.9, 0.004); if (t > 3.0 * gR) break; }
    return t;
}
float spAO(vec3 p, vec3 n) {                                // SDF ambient occlusion, 5 taps
    float occ = 0.0, sca = 1.0;
    for (int i = 1; i <= 5; i++) { float h = 0.012 + 0.06 * float(i) * gR; float d = spMap(p + n * h); occ += (h - d) * sca; sca *= 0.75; }
    return clamp(1.0 - 2.5 * occ / gR, 0.0, 1.0);
}
float spSoftShadow(vec3 p, vec3 L, float maxT) {           // toward the sun, k = 10
    float res = 1.0, t = 0.02 * gR;
    for (int i = 0; i < 20; i++) { float h = spMap(p + L * t); if (h < 0.0005) return 0.0; res = min(res, 10.0 * h / t); t += clamp(h, 0.01, 0.1); if (t > maxT) break; }
    return clamp(res, 0.0, 1.0);
}

// ───────────────────────── light ─────────────────────────
vec3 spSunDir() { float ph = sun * 2.0 * PI, th = (height - 0.5) * PI; return normalize(vec3(cos(th) * sin(ph), sin(th), -cos(th) * cos(ph))); }
// environment: what is BEHIND (the routed layer) mapped by direction + a studio window so glass has something to reflect
vec3 spEnv(vec3 dir, float rough) {
    vec2 e = 0.5 + vec2(dir.x, dir.y) * 0.42;
    vec3 bg = IMG_NORM_PIXEL(inputImage, clamp(e, 0.0, 1.0)).rgb;
    float sky = 0.35 + 0.35 * dir.y;                          // soft top-lit studio
    vec2 w = abs(vec2(dir.x - 0.35, dir.y - 0.45)) / vec2(0.28, 0.42);   // one rectangular softbox, sun side
    float win = (1.0 - smoothstep(0.7, 1.0 + rough * 2.0, max(w.x, w.y)));
    vec2 w2 = abs(vec2(dir.x + 0.55, dir.y - 0.1)) / vec2(0.12, 0.5);
    float win2 = (1.0 - smoothstep(0.7, 1.0 + rough * 2.0, max(w2.x, w2.y))) * 0.5;
    return bg * 0.85 + vec3(sky) * 0.25 + vec3(win + win2) * 3.5;    // softboxes are HDR: they must survive a 4% fresnel
}
float spSchlick(float f0, float c) { float m = 1.0 - c; float m2 = m * m; return f0 + (1.0 - f0) * m2 * m2 * m; }
float spSpec(vec3 n, vec3 L, vec3 V, float rough) {          // Blinn-Phong normalized by roughness
    vec3 H = normalize(L + V); float e = mix(400.0, 8.0, rough);
    return pow(max(0.0, dot(n, H)), e) * (e + 8.0) / 25.0;
}

// ───────────────────────── material microstructure (object space) ─────────────────────────
float spScale() { return mix(6.0, 60.0, fine); }
// height fields; each material has its own physics of surface
float spRelief(vec3 po) {
    float sc = spScale();
    if (material == 1) {                                     // limestone: grain + pits + fossil streaks
        float grain = spFbm3(po * sc * 2.0);
        float pit = 1.0 - smoothstep(0.08, 0.30, spCell(po * sc * 0.9).x);          // round pits
        float streak = spRidge3(po * sc * 0.35 + spFbm3(po * sc * 0.2) * 1.5) ;      // warped, fossil-like
        return grain * 0.35 - pit * 0.9 + smoothstep(0.75, 0.95, streak) * 0.25;
    }
    if (material == 4) {                                     // water: two travelling wave trains + capillary noise
        float t = TIME * 0.7;
        vec3 q = po * sc * 0.5;
        float w = sin(q.x * 2.1 + q.z * 0.7 + t * 1.6) * 0.5 + sin(q.z * 2.9 - q.x * 0.4 - t * 1.1) * 0.35 + sin((q.x + q.y) * 4.7 + t * 2.3) * 0.15;
        return w * 0.6 + (spN3(po * sc * 3.0 + t) - 0.5) * 0.5;
    }
    if (material == 3) {                                     // glass: dust + a few micro scratches
        float dust = smoothstep(0.93, 1.0, spN3(po * sc * 6.0));
        float scratch = smoothstep(0.985, 1.0, spN3(vec3(po.x * sc * 40.0, po.y * sc * 0.8, po.z * sc * 0.8)));
        return -(dust * 0.6 + scratch * 0.4);
    }
    // smooth chrome: brushed micro-abrasions — anisotropic, along the object x axis
    return spN3(vec3(po.x * sc * 0.6, po.y * sc * 30.0, po.z * sc * 30.0)) * 0.7 + spN3(po * sc * 8.0) * 0.3;
}
vec3 spSurface(vec3 p, vec3 n) {
    if (material == 2) {                                     // crystal: facet planes, Fine = count, Micro = how hard they snap
        float k = mix(2.0, 7.0, fine);
        vec3 no = spObj(n);
        vec3 f = normalize(floor(no * k + 0.5) / k + 0.0001);
        return normalize(mix(n, spWorldDir(f), micro));
    }
    if (micro < 0.001) return n;
    vec3 po = spObj(p); float e = 0.30 / spScale();
    vec3 g = vec3(spRelief(po + vec3(e, 0, 0)) - spRelief(po - vec3(e, 0, 0)),
                  spRelief(po + vec3(0, e, 0)) - spRelief(po - vec3(0, e, 0)),
                  spRelief(po + vec3(0, 0, e)) - spRelief(po - vec3(0, 0, e)));
    float amt = (material == 1) ? 1.6 : (material == 4) ? 0.9 : (material == 3) ? 0.5 : 0.35;
    return normalize(n + spWorldDir(g) * micro * amt);
}
// albedo / absorption per material
vec3 spAlbedo(vec3 po) {
    if (material == 1) {                                     // limestone: warm grays, calcite specks, iron stains
        float sc = spScale();
        float tone = spFbm3(po * sc * 0.6);
        vec3 base = mix(vec3(0.52, 0.50, 0.46), vec3(0.68, 0.66, 0.62), tone);
        float speck = smoothstep(0.82, 0.9, spN3(po * sc * 9.0));                   // calcite: bright specks
        float stain = smoothstep(0.6, 0.9, spFbm3(po * sc * 0.25 + 9.0)) * 0.5;      // faint iron
        return mix(base, vec3(0.85, 0.83, 0.80), speck) * mix(vec3(1.0), vec3(0.85, 0.72, 0.55), stain);
    }
    if (material == 0) return vec3(0.9);                     // chrome
    return vec3(1.0);
}

// ───────────────────────── shading ─────────────────────────
struct Shaded { vec3 col; float alpha; float lum; };
Shaded spShade(vec3 p, vec3 n0, vec3 rd, vec2 suv) {
    Shaded S;
    vec3 n = spSurface(p, n0);
    vec3 V = -rd;
    vec3 Lv = gLp - p; float Ld2 = dot(Lv, Lv); vec3 L = Lv * inversesqrt(Ld2);
    float D = length(gLp);
    float att = clamp((D - gR) * (D - gR) / Ld2, 0.0, 1.0);
    float sh = spSoftShadow(p, L, D);
    float ao = spAO(p, n0);
    float NdL = clamp(dot(n, L), 0.0, 1.0), NdV = clamp(dot(n, V), 0.0, 1.0);
    float diff = NdL * att * sh;
    vec3 po = spObj(p);
    float lightSize = mix(0.35, 0.05, distance);              // near lamp = broad, far sun = tight
    vec3 col; float alpha = 1.0;

    if (material == 1) {                                     // STONE — matte, pits occlude, specks glint
        vec3 alb = spAlbedo(po);
        float relief = spRelief(po);
        float pitOcc = clamp(1.0 + relief * 0.8 * micro, 0.3, 1.0);
        float rough = 0.85;
        float spec = spSpec(n, L, V, rough) * att * sh * 0.08;
        float speck = smoothstep(0.82, 0.9, spN3(po * spScale() * 9.0));
        spec += spSpec(n, L, V, 0.25) * att * sh * speck * 0.6;    // calcite glints
        col = alb * (0.18 * ao + 0.95 * diff) * pitOcc + spec;
    } else if (material == 0) {                              // CHROME — env reflection, brushed anisotropy
        float rough = 0.05 + micro * 0.35;
        vec3 R = reflect(rd, n);
        vec3 env = spEnv(R, rough);
        float F = spSchlick(0.6, NdV);
        // anisotropic highlight: stretch along the brushed direction (object x)
        vec3 T = spWorldDir(vec3(1.0, 0.0, 0.0)); vec3 H = normalize(L + V);
        float th = dot(H, T), nh = dot(H, n);
        float aniso = exp(-(th * th) / (0.02 + 0.5 * micro)) * pow(max(nh, 0.0), 30.0);
        float spec = (spSpec(n, L, V, rough) * 0.6 + aniso * micro * 1.5) * att * sh;
        col = env * mix(0.7, 1.0, F) * ao * 0.9 + vec3(spec) + diff * 0.08;
    } else if (material == 4) {                              // WATER — refracted floor with caustics, glints, teal absorption
        float ior = 1.333;
        vec3 T3 = refract(rd, n, 1.0 / ior);
        float thick = spThickness(p, T3);
        vec2 off = T3.xy * thick * 0.22;
        // caustics: curvature of the wave field focuses the transmitted light
        vec3 po2 = spObj(p); float e = 0.30 / spScale();
        float lap = spRelief(po2 + vec3(e, 0, 0)) + spRelief(po2 - vec3(e, 0, 0)) + spRelief(po2 + vec3(0, 0, e)) + spRelief(po2 - vec3(0, 0, e)) - 4.0 * spRelief(po2);
        float caus = 1.0 + clamp(-lap * 4.0 * micro, -0.6, 1.8) * att * sh;
        vec3 floorC = IMG_NORM_PIXEL(inputImage, clamp(suv + off, 0.0, 1.0)).rgb * caus;
        vec3 absorb = exp(-vec3(0.55, 0.12, 0.08) * thick * 2.5);   // Beer-Lambert: red dies first → teal
        vec3 trans = floorC * absorb + vec3(0.02, 0.10, 0.11) * (1.0 - absorb) * (0.4 + 0.6 * diff);
        float F = spSchlick(0.02, NdV);
        vec3 R = reflect(rd, n); vec3 env = spEnv(R, 0.05);
        // glints: high-power specular through a sparkle mask that rides the ripples
        float glintMask = smoothstep(0.55, 0.95, spN3(po2 * spScale() * 7.0 + TIME * 1.5));
        float glint = pow(max(0.0, dot(n, normalize(L + V))), 900.0) * glintMask * 6.0 * att;
        col = mix(trans, env, F) + vec3(spSpec(n, L, V, 0.06) * 0.35 + glint) * sh;
        alpha = 1.0;
    } else {                                                 // GLASS / CRYSTAL — dispersion, fresnel, thickness
        bool cr = (material == 2);
        float ior = cr ? 1.62 : 1.5;
        float disp = cr ? 0.03 + 0.05 * fine : 0.008 + 0.02 * micro;   // wavelength spread of the IOR
        float thick = spThickness(p, refract(rd, n, 1.0 / ior));
        vec3 trans;
        float scale = 0.26;
        vec3 Tr = refract(rd, n, 1.0 / (ior - disp)), Tg = refract(rd, n, 1.0 / ior), Tb = refract(rd, n, 1.0 / (ior + disp));
        trans.r = IMG_NORM_PIXEL(inputImage, clamp(suv + Tr.xy * thick * scale, 0.0, 1.0)).r;
        trans.g = IMG_NORM_PIXEL(inputImage, clamp(suv + Tg.xy * thick * scale, 0.0, 1.0)).g;
        trans.b = IMG_NORM_PIXEL(inputImage, clamp(suv + Tb.xy * thick * scale, 0.0, 1.0)).b;
        // what the sun does inside: the refracted sun tints the transmitted image (looking through toward the light)
        float sunThrough = pow(max(0.0, dot(Tg, L)), 12.0) * att;
        trans += vec3(sunThrough) * 0.6;
        float F = spSchlick(cr ? 0.06 : 0.04, NdV);
        vec3 R = reflect(rd, n); vec3 env = spEnv(R, 0.02);
        float spec = spSpec(n, L, V, 0.04) * att * sh;
        if (cr) {                                            // internal structure: planar fractures + inclusions, 4 samples along the ray inside
            vec3 fr = vec3(0.0); float inc = 0.0;
            for (int k = 1; k <= 4; k++) {
                vec3 q = spObj(p + Tg * thick * float(k) / 5.0);
                vec2 c = spCell(q * mix(2.0, 5.0, micro));
                float plane = 1.0 - smoothstep(0.0, 0.05, abs(c.x - 0.38));     // cell walls = fracture planes
                float rainbow = fract(c.y * 3.0 + dot(q, L) * 2.0);             // thin-film rainbow on the crack
                fr += (0.5 + 0.5 * cos(2.0 * PI * (rainbow + vec3(0.0, 0.33, 0.67)))) * plane * 0.35;
                inc += smoothstep(0.88, 0.96, spN3(q * 40.0)) * 0.5;            // tiny bubbles/inclusions
            }
            trans += fr * (0.4 + 0.6 * att) + vec3(inc) * 0.25;
            trans = mix(trans, vec3(0.9, 0.95, 1.0) * dot(trans, vec3(0.33)), 0.15);
        } else {
            float dust = smoothstep(0.93, 1.0, spN3(po * spScale() * 6.0)) * micro;
            trans = mix(trans, vec3(0.8), dust * 0.5);
            float absorbG = exp(-thick * 0.35);              // faint green edge of real glass
            trans *= mix(vec3(1.0), vec3(0.88, 1.0, 0.94), 1.0 - absorbG);
        }
        // thick rim: at grazing angles glass goes dark then bright (total internal reflection band)
        float rimBand = smoothstep(0.02, 0.18, NdV) * (1.0 - smoothstep(0.18, 0.45, NdV));
        col = mix(trans, env, F) + vec3(spec) * 1.2 + env * rimBand * 0.35 - vec3(0.10) * (1.0 - smoothstep(0.0, 0.08, NdV));
        alpha = 1.0;
    }
    col = max(col, 0.0);
    S.col = col; S.alpha = alpha; S.lum = dot(col, vec3(0.299, 0.587, 0.114));
    return S;
}
float spLumCheap(vec2 uv) {                                  // emboss taps: geometry-only shading
    vec3 p; float dm; if (spMarch(uv, p, dm) < 0.5) return 0.0;
    vec3 n = spNorm(p); vec3 L = normalize(gLp - p);
    return 0.15 + 0.85 * clamp(dot(n, L), 0.0, 1.0);
}

void main() {
    vec2 suv = isf_FragNormCoord;                            // screen uv for the routed layer
    vec2 uv = suv - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    gTh = tumble * 6.28318530718; // Heart owns phase; never multiply a driven rate by elapsed TIME.
    float ax = axisv * PI;
    gAxis = normalize(vec3(sin(ax), cos(ax), 0.35 * sin(ax * 2.0)));

    vec3 sd = spSunDir();
    float near = 1.0 - distance;
    vec2 shOff = -normalize(sd.xy + vec2(0.0001, -0.0001)) * shadow * (0.10 + 0.10 * near);
    float shSoft = mix(0.01, 0.12, near) * shadow;
    float shLen = shadow * 0.32 + 0.002;                      // worst case — Size never depends on Distance

    // ── CONTAINMENT LAW ──
    float m = 0.04;
    float room = min(hf2.x, hf2.y) - m - shLen;
    float Rp = mix(0.03, max(room, 0.03), sizev); gRp = Rp;
    float k = Rp * FOV;
    gR = k * CAMZ / (1.0 + k);
    gLp = sd * gR * mix(1.35, 30.0, distance);
    vec2 c = (vec2(px, py) - 0.5) * 2.0 * max(hf2 - Rp - shLen - m, vec2(0.0));
    vec2 s = uv - c;

    vec3 p; float dm; float hit = spMarch(s, p, dm);
    vec3 col = vec3(0.0); float a = 0.0;
    if (hit > 0.5) {
        vec3 rd = spRay(s);
        vec3 n0 = spNorm(p);
        Shaded S = spShade(p, n0, rd, suv);
        vec3 n = spSurface(p, n0);
        float facing = clamp(dot(n, -rd), 0.0, 1.0);
        float body = S.lum;
        // Shade: how much the light is allowed to shape the body (0 = flat silhouette)
        vec3 flat3 = vec3(0.92);
        col = mix(flat3, S.col, shade);

        // ── LINE ──
        float inkOn = clamp(edge * 8.0, 0.0, 1.0);
        float rim = 1.0 - facing;
        float th2 = 1.0 - mix(0.5, 0.10, edge);
        float inkM = inkOn * 0.9 * smoothstep(th2 - 0.03, th2 + 0.03, rim);
        float shoulder = smoothstep(th2 - 0.30, th2, rim);
        float pinna = smoothstep(th2 - 0.09, th2 - 0.03, rim) * (1.0 - smoothstep(th2 - 0.03, th2, rim));
        col *= 1.0 + 0.20 * inkOn * shoulder;
        col += 0.30 * inkOn * pinna;
        if (inkOn > 0.0) { float l = dot(col, vec3(0.299, 0.587, 0.114)); float lb = floor(l * 4.0 + 0.5) / 4.0; col *= mix(1.0, lb / max(l, 0.001), inkOn * shade * 0.6); }
        if (emboss > 0.001) {
            vec2 dir = normalize(sd.xy + vec2(0.0001)) * (0.006 + 0.014 * Rp);
            col = clamp(col + (spLumCheap(s - dir) - spLumCheap(s + dir)) * emboss * 2.5, 0.0, 4.0);
        }

        // ── COLOR ──
        float lum = dot(col, vec3(0.299, 0.587, 0.114));
        if (colorm == 1) col = vec3(lum);
        else if (colorm == 2) col = (0.5 + 0.5 * cos(2.0 * PI * (min(lum, 1.0) * loopv + hue + vec3(rOff, gOff, bOff)))) * mix(1.0, min(lum, 1.0), 0.35);
        else if (colorm == 3) col = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
        col *= (1.0 - inkM);
        a = max(alphav, inkM);                               // clip-wide Alpha; ink stays opaque
    } else if (shadow > 0.001) {                             // SHADOW — black, alpha only, never colored
        vec3 q; float dms; float sm = spMarch(s - shOff, q, dms);
        float pen = max(sm, 1.0 - smoothstep(0.0, shSoft + 0.002, dms));
        col = vec3(0.0); a = shadow * 0.65 * pen;
    }
    gl_FragColor = vec4(min(col, vec3(1.0)), a);
}
"""

def emit():
    hdr = {"DESCRIPTION": "SP Atom FIGURE 3D (effect on a Video Router: refracts/reflects what is behind). Figure A/B/Morph; containment law; Light sun/height/distance/shadow; Material smooth/stone/crystal/glass/water with material-science microstructure; Color natural/gray/loop/normal; Line shade/edge/emboss; clip-wide Alpha. No drives.",
           "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs")

emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), NAME, "effect"], check=True)
