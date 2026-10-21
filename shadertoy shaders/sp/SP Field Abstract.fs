/*{
  "DESCRIPTION": "SP Field ABSTRACT atom - pure math fields: interference / flow / cells / bands. Grayscale, alpha = value. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "field",
      "LABEL": "Field",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "interference",
        "flow",
        "cells",
        "bands"
      ]
    },
    {
      "NAME": "scalev",
      "LABEL": "Scale",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "driftv",
      "LABEL": "Drift",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "warpv",
      "LABEL": "Warp",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrast",
      "LABEL": "Contrast",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "levelv",
      "LABEL": "Level",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.5,
      "MAX": 0.5
    }
  ]
}*/

float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec2  spN22(vec2 p) { return vec2(spN2(p), spN2(p + 19.19)); }
float spVal(vec2 p) {
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y);
}
float spFbm(vec2 p) { return 0.5 * spVal(p) + 0.25 * spVal(p * 2.03 + 7.7) + 0.125 * spVal(p * 4.01 + 13.1) + 0.0625 * spVal(p * 8.07 + 29.3); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    uv.x *= RENDERSIZE.x / RENDERSIZE.y;
    float t = TIME * driftv;
    float f = 1.0 + scalev * 9.0;
    float con = 0.2 + contrast * 2.8;
    float v = 0.5;
    if (field == 0) {                                       // INTERFERENCE: five sources, summed waves
        float s = 0.0;
        for (int i = 0; i < 5; i++) {
            float fi = float(i);
            vec2 src = (spN22(vec2(fi * 3.7, 1.3)) - 0.5) * 1.6 + 0.15 * vec2(cos(t * 0.3 + fi), sin(t * 0.23 + fi * 1.7)) * warpv * 3.0;
            s += sin(length(uv - src) * f * 8.0 - t * 3.0);
        }
        v = 0.5 + 0.5 * (s / 5.0);
    } else if (field == 1) {                                // FLOW: domain-warped fbm
        vec2 p = uv * f;
        vec2 q = vec2(spFbm(p + t * 0.3), spFbm(p + vec2(5.2, 1.3) + t * 0.2));
        vec2 r = vec2(spFbm(p + warpv * 4.0 * q + vec2(1.7, 9.2)), spFbm(p + warpv * 4.0 * q + vec2(8.3, 2.8)));
        v = spFbm(p + warpv * 4.0 * r);
    } else if (field == 2) {                                // CELLS: voronoi distance
        vec2 p = uv * f * 1.5; vec2 ip = floor(p), fp = fract(p);
        float m = 8.0;
        for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = spN22(ip + g); o = 0.5 + 0.5 * sin(t + 6.2831 * o) * (0.3 + warpv * 0.7);
            m = min(m, length(g + o - fp));
        }
        v = m;
    } else {                                                // BANDS: rotating sine bands
        float a = warpv * 3.14159 + t * 0.1;
        v = 0.5 + 0.5 * sin((uv.x * cos(a) + uv.y * sin(a)) * f * 6.0 + t * 2.0);
    }
    v = clamp((v - 0.5) * con + 0.5 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
