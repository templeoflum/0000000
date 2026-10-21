/*{
  "DESCRIPTION": "SP Atom FIGURE 3D - Figure A / B / Morph; containment law; LIGHT sun/height/distance/shadow; MATERIAL smooth/stone/crystal/glass + micro/fine; COLOR gray/loop/normal; LINE shade/edge/emboss. No drives.",
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
        5,
        6
      ],
      "LABELS": [
        "torus",
        "sphere",
        "box",
        "octahedron",
        "tetrahedron",
        "icosahedron",
        "dodecahedron"
      ]
    },
    {
      "NAME": "figB",
      "LABEL": "Figure B",
      "TYPE": "long",
      "DEFAULT": 5,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6
      ],
      "LABELS": [
        "torus",
        "sphere",
        "box",
        "octahedron",
        "tetrahedron",
        "icosahedron",
        "dodecahedron"
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
      "NAME": "px",
      "LABEL": "X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "py",
      "LABEL": "Y",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "tumble",
      "LABEL": "Tumble",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "axisv",
      "LABEL": "Axis",
      "TYPE": "float",
      "DEFAULT": 0.3,
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
      "NAME": "shadow",
      "LABEL": "Shadow",
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
      "LABEL": "Color",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2
      ],
      "LABELS": [
        "gray",
        "loop",
        "normal"
      ]
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
      "NAME": "edge",
      "LABEL": "Edge",
      "TYPE": "float",
      "DEFAULT": 0.4,
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
    }
  ]
}*/

#define PHI 1.6180339887
#define CAMZ 3.2
#define FOV 1.1
vec3 spRotAA(vec3 p, vec3 ax, float th) { float c = cos(th), s = sin(th); return p * c + cross(ax, p) * s + ax * dot(ax, p) * (1.0 - c); }
float spGdf(vec3 p, vec3 n) { return abs(dot(p, normalize(n))); }
float spH3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float spN3(vec3 p) {
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(spH3(i), spH3(i + vec3(1, 0, 0)), f.x), mix(spH3(i + vec3(0, 1, 0)), spH3(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(spH3(i + vec3(0, 0, 1)), spH3(i + vec3(1, 0, 1)), f.x), mix(spH3(i + vec3(0, 1, 1)), spH3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
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
float gR; vec3 gAxis; float gTh; vec3 gLp;
vec3 spObj(vec3 p) { return spRotAA(p, gAxis, gTh); }
float spMap(vec3 p) { vec3 q = spObj(p); return mix(spFig(figA, q, gR), spFig(figB, q, gR), morph); }
vec3 spNorm(vec3 p) { vec2 e = vec2(0.002, 0.0); return normalize(vec3(spMap(p + e.xyy) - spMap(p - e.xyy), spMap(p + e.yxy) - spMap(p - e.yxy), spMap(p + e.yyx) - spMap(p - e.yyx))); }
vec3 spRay(vec2 uv) { return normalize(vec3(uv * FOV, 1.0)); }
float spMarch(vec2 uv, out vec3 p, out float dmin) {
    vec3 ro = vec3(0.0, 0.0, -CAMZ), rd = spRay(uv); float t = 0.0, d = 0.0; dmin = 9.0;
    for (int i = 0; i < 80; i++) { p = ro + rd * t; d = spMap(p); dmin = min(dmin, d); if (d < 0.001 || t > 7.0) break; t += d * 0.8; }
    return (d < 0.001) ? 1.0 : 0.0;
}
float spRelief(vec3 po) {
    float sc = mix(10.0, 80.0, fine);
    if (material == 1) { float pores = 1.0 - smoothstep(0.40, 0.75, spN3(po * sc * 1.3 + 31.7)); return pores * 0.7 + spN3(po * sc * 4.0 + 7.3) * 0.3; }
    if (material == 3) return spN3(po * sc * 2.0) * 0.5;
    return spN3(po * sc) * 0.6 + spN3(po * sc * 4.1 + 7.3) * 0.4;
}
vec3 spSurface(vec3 p, vec3 n) {
    if (material == 2) {
        float k = mix(2.0, 7.0, fine);
        vec3 no = spObj(n);
        vec3 f = normalize(floor(no * k + 0.5) / k + 0.0001);
        return normalize(mix(n, spRotAA(f, gAxis, -gTh), micro));
    }
    if (micro < 0.001) return n;
    vec3 po = spObj(p); float e = 0.35 / mix(10.0, 80.0, fine);
    vec3 g = vec3(spRelief(po + vec3(e, 0, 0)) - spRelief(po - vec3(e, 0, 0)),
                  spRelief(po + vec3(0, e, 0)) - spRelief(po - vec3(0, e, 0)),
                  spRelief(po + vec3(0, 0, e)) - spRelief(po - vec3(0, 0, e)));
    return normalize(n + spRotAA(g, gAxis, -gTh) * micro * 1.4);
}
vec3 spSunDir() { float ph = sun * 6.2831853, th = (height - 0.5) * 3.14159; return normalize(vec3(cos(th) * sin(ph), sin(th), -cos(th) * cos(ph))); }
vec2 spShade(vec3 p, vec3 n, vec3 rd) {
    vec3 Lv = gLp - p; float Ld2 = dot(Lv, Lv); vec3 L = Lv * inversesqrt(Ld2);
    float D = length(gLp);
    float att = clamp((D - gR) * (D - gR) / Ld2, 0.0, 1.0);
    float lam = clamp(dot(n, L), 0.0, 1.0) * att;
    float facing = clamp(dot(n, -rd), 0.0, 1.0);
    float rimL = pow(1.0 - facing, 2.0);
    float fres = pow(1.0 - facing, 4.0);
    float specPow = mix(10.0, 40.0, distance);
    float spec = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow) * att;
    float vol, alpha = 1.0;
    if (material == 1) { float occ = (micro > 0.001) ? 1.0 - micro * 0.5 * spRelief(spObj(p)) : 1.0; vol = (0.10 + 0.85 * lam + 0.10 * rimL) * occ; }
    else if (material == 2) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.8) * att; vol = 0.10 + 0.45 * lam + 0.55 * fres + 1.2 * sp2; }
    else if (material == 3) { float sp2 = pow(max(0.0, dot(reflect(-L, n), -rd)), specPow * 1.4) * att; float frost = micro * 0.6;
        vol = 0.9 * fres + 1.3 * sp2 * (1.0 - frost * 0.7) + frost * (0.2 + 0.4 * lam); alpha = clamp(0.12 + 0.88 * fres + sp2 + frost, 0.0, 1.0); }
    else { vol = 0.14 + 0.72 * lam + 0.30 * rimL * (1.0 + 0.8 * micro) + spec * (0.35 + 0.8 * micro);
        if (micro > 0.001) { float gn = spN3(spObj(p) * 90.0); vol *= 1.0 + micro * 0.30 * (gn - 0.5) * (0.5 + rimL); } }
    return vec2(mix(0.92, vol, shade), alpha);
}
float spLum(vec2 uv) { vec3 p; float dm; if (spMarch(uv, p, dm) < 0.5) return 0.0; vec3 n = spSurface(p, spNorm(p)); return spShade(p, n, spRay(uv)).x; }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    gTh = TIME * tumble * 1.5;
    float ax = axisv * 3.14159;
    gAxis = normalize(vec3(sin(ax), cos(ax), 0.35 * sin(ax * 2.0)));
    vec3 sd = spSunDir();
    float near = 1.0 - distance;
    vec2 shOff = -normalize(sd.xy + vec2(0.0001, -0.0001)) * shadow * (0.10 + 0.10 * near);
    float shSoft = mix(0.01, 0.12, near) * shadow;
    float shLen = shadow * (0.20 + 0.12) + 0.002;
    float m = 0.04;
    float room = min(hf2.x, hf2.y) - m - shLen;
    float Rp = mix(0.03, max(room, 0.03), sizev);
    float k = Rp * FOV;
    gR = k * CAMZ / (1.0 + k);
    gLp = sd * gR * mix(1.35, 30.0, distance);
    vec2 c = (vec2(px, py) - 0.5) * 2.0 * max(hf2 - Rp - shLen - m, vec2(0.0));
    vec2 s = uv - c;
    vec3 p; float dm; float hit = spMarch(s, p, dm);
    vec3 col = vec3(0.0); float a = 0.0;
    if (hit > 0.5) {
        vec3 rd = spRay(s);
        vec3 n = spSurface(p, spNorm(p));
        float facing = clamp(dot(n, -rd), 0.0, 1.0);
        vec2 sh = spShade(p, n, rd);
        float body = sh.x;
        float inkOn = clamp(edge * 8.0, 0.0, 1.0);
        float rim = 1.0 - facing;
        float th2 = 1.0 - mix(0.5, 0.10, edge);
        float inkM = inkOn * 0.9 * smoothstep(th2 - 0.03, th2 + 0.03, rim);
        float shoulder = smoothstep(th2 - 0.30, th2, rim);
        float pinna = smoothstep(th2 - 0.09, th2 - 0.03, rim) * (1.0 - smoothstep(th2 - 0.03, th2, rim));
        body *= 1.0 + 0.20 * inkOn * shoulder;
        body += 0.30 * inkOn * pinna;
        body = mix(body, floor(body * 4.0 + 0.5) / 4.0, inkOn * shade * 0.6);
        if (emboss > 0.001) { vec2 dir = normalize(sd.xy + vec2(0.0001)) * (0.006 + 0.014 * Rp); body = clamp(body + (spLum(s - dir) - spLum(s + dir)) * emboss * 2.5, 0.0, 1.0); }
        body = min(body, 1.0);
        if (colorm == 0) col = vec3(body);
        else if (colorm == 1) col = (0.5 + 0.5 * cos(6.2831853 * (body * loopv + hue + vec3(rOff, gOff, bOff)))) * mix(1.0, body, 0.35);
        else col = (n * vec3(1.0, 1.0, -1.0)) * 0.5 + 0.5;
        col *= (1.0 - inkM);
        a = max(sh.y, inkM);
    } else if (shadow > 0.001) {
        vec3 q; float dms; float sm = spMarch(s - shOff, q, dms);
        float pen = max(sm, 1.0 - smoothstep(0.0, shSoft + 0.002, dms));
        col = vec3(0.0); a = shadow * 0.65 * pen;
    }
    gl_FragColor = vec4(col, a);
}
