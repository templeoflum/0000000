/*{
  "DESCRIPTION": "SP Atom FIGURE 2D - Figure A / B / Morph over a 2D SDF catalog (disc, ring, capsule, polygon, star, cross); containment; Turn, Spin (perspective coin flip), Outline (black stroke), Soft; layer styles: Sun, Bevel, Emboss, Inner Shadow, Inner Glow, Outer Glow, Satin, Gradient, Contour + Flow, Shadow (black alpha); Color = Base gray/normal + Loop per channel (Wet/Loop/Hue/R/G/B). No drives.",
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
        "disc",
        "ring",
        "capsule",
        "polygon",
        "star",
        "cross"
      ]
    },
    {
      "NAME": "figB",
      "LABEL": "Figure B",
      "TYPE": "long",
      "DEFAULT": 3,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5
      ],
      "LABELS": [
        "disc",
        "ring",
        "capsule",
        "polygon",
        "star",
        "cross"
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
      "NAME": "sides",
      "LABEL": "Sides",
      "TYPE": "float",
      "DEFAULT": 5.0,
      "MIN": 3.0,
      "MAX": 12.0
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
      "NAME": "turn",
      "LABEL": "Turn",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "spin",
      "LABEL": "Spin",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "outline",
      "LABEL": "Outline",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "soft",
      "LABEL": "Soft",
      "TYPE": "float",
      "DEFAULT": 0.05,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sun",
      "LABEL": "Sun",
      "TYPE": "float",
      "DEFAULT": 0.35,
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
      "NAME": "oglow",
      "LABEL": "Outer Glow",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "satin",
      "LABEL": "Satin",
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
      "NAME": "flow",
      "LABEL": "Flow",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
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
      "WIDTH": 1,
      "HEIGHT": 1
    },
    {}
  ]
}*/

#define PI 3.14159265
// every 2D figure is normalized so its CIRCUMRADIUS is exactly r — one bounding circle for containment
float spFig2(int f, vec2 q, float r, float n) {
    float an = atan(q.y, q.x), len = length(q);
    if (f == 0) return len - r;                                                             // disc
    if (f == 1) return abs(len - r * 0.85) - r * 0.15;                                      // ring: outer = r
    if (f == 2) { vec2 p = q; p.x -= clamp(p.x, -r * 0.6, r * 0.6); return length(p) - r * 0.4; }   // capsule: half-length + radius = r
    if (f == 3) { float sec = 2.0 * PI / n; return cos(floor(0.5 + an / sec) * sec - an) * len - r * cos(sec * 0.5); }   // polygon: vertex = r
    if (f == 4) { float rr = r * (0.62 + 0.38 * cos(n * an)); return len - rr; }             // star: tip = r
    vec2 p = abs(q); float w = r * 0.28;                                                    // cross: arm = r
    float dx = max(p.x - r, p.y - w), dy = max(p.y - r, p.x - w);
    return min(dx, dy);
}
float spMap2(vec2 q, float r, float n) { return mix(spFig2(figA, q, r, n), spFig2(figB, q, r, n), morph); }   // distance fields interpolate
// Spin: the plane tumbles about its diagonal axis and is seen in perspective (the coin flip);
// returns the material-plane coordinate for a screen point, and a 'behind the eye' flag in z
vec3 spPlane(vec2 sq, float ph, float dU) {
    float c = cos(ph), s = sin(ph);
    vec3 uu = vec3(c, 0.0, -s);
    vec3 vv = vec3(s * s, c, c * s);
    vec3 nn = cross(uu, vv);
    vec3 D = vec3(sq, dU);
    float den = dot(nn, D);
    if (abs(den) < 1e-4) return vec3(1e6, 1e6, 0.0);
    float t = (dU * nn.z) / den;
    if (t <= 0.0) return vec3(1e6, 1e6, 0.0);
    vec3 Xp = vec3(0.0, 0.0, -dU) + t * D;
    return vec3(dot(uu, Xp), dot(vv, Xp), 1.0);
}
float gr2, gn2, gw2, gPh; vec2 gL2;
float spD(vec2 q) { return spMap2(q, gr2, gn2); }
float spMask(float d, float w) { return 1.0 - smoothstep(-w * 0.5, w * 0.5, d); }
// ── the HEIGHT of the styled surface at q: every layer style adds to it; tone and normal both read it ──
float spTone(vec2 q) {
    float r = gr2, w = gw2; vec2 L = gL2;
    float d = spD(q);
    vec2 e = vec2(0.002, 0.0);
    vec2 g = normalize(vec2(spD(q + e.xy) - spD(q - e.xy), spD(q + e.yx) - spD(q - e.yx)) + 1e-5);   // outward normal of the silhouette
    float NdL = dot(g, L);
    float tone = 0.85;
    float din = max(-d, 0.0);
    // Bevel: raised lip, lit on the sun side, dark on the far side
    float bw = r * (0.04 + bevel * 0.35);
    float lip = 1.0 - smoothstep(0.0, bw, din); lip = lip * lip * (3.0 - 2.0 * lip);
    tone += bevel * lip * NdL * 0.7;
    // Emboss: relief — the mask shifted toward and away from the light
    if (emboss > 0.001) {
        float off = r * (0.02 + emboss * 0.08);
        tone += (spMask(spD(q - L * off), w) - spMask(spD(q + L * off), w)) * emboss * 0.7;
    }
    // Inner Shadow: darkens inside the edge on the side away from the light
    float sw = r * (0.06 + inner * 0.4);
    float isd = 1.0 - smoothstep(0.0, sw, din);
    tone -= inner * isd * (0.25 + 0.75 * clamp(-NdL, 0.0, 1.0)) * 0.8;
    // Inner Glow: bright band inside the edge
    float igw = r * (0.03 + iglow * 0.3);
    tone += iglow * (1.0 - smoothstep(0.0, igw, din)) * 0.5;
    // Satin: the mask offset both ways across the light, multiplied
    if (satin > 0.001) {
        vec2 o = vec2(-L.y, L.x) * r * (0.08 + satin * 0.25);
        float sA = spMask(spD(q + o), w * 4.0 + r * 0.05), sB = spMask(spD(q - o), w * 4.0 + r * 0.05);
        tone -= (1.0 - sA * sB) * satin * 0.45;
    }
    // Gradient Overlay: ramp across the body along the light
    tone += gradient * dot(q / max(r, 0.001), L) * 0.35;
    // Contour: inset lines following the shape; strength and spacing ease in
    if (contour > 0.001) {
        float ease = smoothstep(0.0, 0.35, contour);
        float sp = r * mix(0.30, 0.05, contour);
        float k = abs(mod(din / sp + gPh, 1.0) - 0.5) * sp;   // Flow: integrated phase (in spacing units) — lines travel at constant spacing
        float lw = 0.0015 + w * 0.5 + sp * 0.12 * (1.0 - ease);
        float cl = 1.0 - smoothstep(0.0, lw, k);
        tone -= cl * 0.6 * ease * step(0.0001, din);
    }
    return clamp(tone, 0.0, 1.0);
}
// ── the UNLIT height of the styled surface: geometry only, no sun — this is what the normal reads ──
float spHeight(vec2 q) {
    float r = gr2, w = gw2; vec2 L = gL2;
    float d = spD(q);
    float din = max(-d, 0.0);
    float h = 0.0;
    // Bevel: a pillow lip rising over the bevel width (the look that worked)
    float bw = r * (0.06 + bevel * 0.35);
    float lip = 1.0 - smoothstep(0.0, bw, din); lip = lip * lip * (3.0 - 2.0 * lip);
    h -= lip * (0.35 + bevel * 0.65) * bw;                   // edge is lower than the plateau → normal tilts outward
    // Emboss: a raised plate of the same silhouette, slightly inset
    if (emboss > 0.001) { float off = r * (0.02 + emboss * 0.08); h += spMask(d + off, w) * emboss * off; }
    // Inner Shadow: the edge sinks instead of rising
    float sw = r * (0.06 + inner * 0.4);
    float isd = 1.0 - smoothstep(0.0, sw, din);
    h -= isd * inner * sw * 0.6;
    // Satin: folds across the light
    if (satin > 0.001) {
        vec2 o = vec2(-L.y, L.x) * r * (0.08 + satin * 0.25);
        float sA = spMask(spD(q + o), w * 4.0 + r * 0.05), sB = spMask(spD(q - o), w * 4.0 + r * 0.05);
        h -= (1.0 - sA * sB) * satin * r * 0.12;
    }
    // Gradient: a tilt of the whole plate along the light
    h += gradient * dot(q, L) * 0.35;
    // Contour: ridges at the inset lines
    if (contour > 0.001) {
        float ease = smoothstep(0.0, 0.35, contour);
        float sp = r * mix(0.30, 0.05, contour);
        float k = abs(mod(din / sp + gPh, 1.0) - 0.5) * sp;   // Flow: integrated phase (in spacing units) — lines travel at constant spacing
        float lw = 0.0015 + w * 0.5 + sp * 0.12 * (1.0 - ease);
        h += (1.0 - smoothstep(0.0, lw * 1.5, k)) * ease * lw * 1.2 * step(0.0001, din);
    }
    return h;
}
void main() {
    // pass 0: integrate the contour phase (speed = Flow², signed) in units of the current spacing; wraps at 1
    float spNow = mix(0.30, 0.05, contour);                 // spacing as a fraction of r (r cancels)
    if (PASSINDEX == 0) {
        float prev = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;
        float dt = clamp(TIMEDELTA, 0.0, 0.1);
        float v = prev + dt * flow * abs(flow) * 0.6 / spNow;
        gl_FragColor = vec4(fract(v), 0.0, 0.0, 1.0);
        return;
    }
    gPh = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;                // LIVE composition aspect
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    float n = floor(sides + 0.5);
    float w = 0.0012 + soft * 0.06;                         // Soft: edge width
    float m = 0.04;

    // containment: circumradius + outline + outer glow + shadow + softness + the perspective swell of Spin stay inside the frame
    float room = min(hf2.x, hf2.y) - m;
    float swell = 1.25;
    float ow = outline * 0.06;                              // Outline: stroke width, 0 = none
    float gw = oglow * 0.12;                                // Outer Glow reach
    vec2 L0 = vec2(cos(sun * 2.0 * PI), sin(sun * 2.0 * PI));
    float shLen = shadow * 0.14, shSoft = 0.004 + shadow * 0.03;   // Shadow: cast away from the sun
    float reach = max(max(ow, gw), shLen + shSoft) + w;
    float r = (mix(0.02, room, sizev) - reach) / swell;
    r = max(r, 0.01);
    float bound = r * swell + reach;
    vec2 c = (vec2(px, py) - 0.5) * 2.0 * max(hf2 - bound - m, vec2(0.0));
    vec2 q = uv - c;

    vec3 pm = spPlane(q, spin * 2.0 * PI, 1.8);            // Spin: perspective plane tumble
    float ok = pm.z;
    q = pm.xy;
    float a = turn * 2.0 * PI; q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q;
    gr2 = r; gn2 = n; gw2 = w; gL2 = L0;

    float d = spD(q);
    float fill = spMask(d, w) * ok;                                                   // the shape
    float line = (outline > 0.001) ? spMask(d - ow, w) * ok : 0.0;                    // Stroke: black, around it

    float tone = spTone(q);

    // ── COLOR: palette on the tone (shadow excluded) ──
    vec3 body = vec3(tone);
    if (colorm == 1) {                                  // normal map of the styled HEIGHT (unlit geometry): every style shapes it, the sun does not
        float hs = max(r * 0.012, 0.0015);
        vec2 dh = vec2(spHeight(q + vec2(hs, 0.0)) - spHeight(q - vec2(hs, 0.0)), spHeight(q + vec2(0.0, hs)) - spHeight(q - vec2(0.0, hs))) / (2.0 * hs);
        vec3 nm = normalize(vec3(-dh, 1.0));
        body = nm * 0.5 + 0.5;
    }
    // Loop stacked on the base, PER CHANNEL (a ColourLoop over the render): gray loops as before, normal keeps its directions
    if (wet > 0.001) {
        vec3 looped = 0.5 + 0.5 * cos(2.0 * PI * (body * loopv + hue + vec3(rOff, gOff, bOff)));
        body = mix(body, looped, wet);
    }

    // ── SHADOW: the silhouette cast away from the sun, black, alpha only ──
    float sh = 0.0;
    if (shadow > 0.001) {
        vec2 qs = q + L0 * shLen;
        float ds = spD(qs);
        sh = (1.0 - smoothstep(-shSoft, shSoft, ds)) * ok * shadow * 0.7;
    }

    // Outer Glow: white, outside the shape, its own alpha
    float glow = (oglow > 0.001) ? exp(-max(d, 0.0) / (gw * 0.4 + 0.0005)) * oglow * (1.0 - fill) : 0.0;

    float figA_ = max(max(fill, line), glow);
    vec3 col = body * fill + vec3(glow) * (1.0 - line);
    float alpha = figA_ + sh * (1.0 - figA_);
    col = col * figA_ / max(alpha, 0.0001);                  // shadow contributes black
    gl_FragColor = vec4(min(col, 1.0), alpha);
}
