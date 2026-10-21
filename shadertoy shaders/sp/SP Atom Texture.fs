/*{
  "DESCRIPTION": "SP Atom TEXTURE - scanlines / halftone / hatch / weave; Count, Drift, Duty, Soft, Level. Alpha = value. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "tex",
      "LABEL": "Texture",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "scanlines",
        "halftone",
        "hatch",
        "weave"
      ]
    },
    {
      "NAME": "count",
      "LABEL": "Count",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "phasev",
      "LABEL": "Drift",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "duty",
      "LABEL": "Duty",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.05,
      "MAX": 0.95
    },
    {
      "NAME": "soft",
      "LABEL": "Soft",
      "TYPE": "float",
      "DEFAULT": 0.2,
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

float spBand(float x, float d, float s) { float g = abs(fract(x) - 0.5) * 2.0; return 1.0 - smoothstep(d - s, d + s, g); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy; float asp = RENDERSIZE.x / RENDERSIZE.y;
    float n = 8.0 + count * 232.0;                            // Count: lines across the frame
    float t = TIME * phasev * 2.0;
    float s = 0.01 + soft * 0.5, v;
    if (tex == 0) v = spBand(uv.y * n + t, duty, s);
    else if (tex == 1) { vec2 p = vec2(uv.x * asp, uv.y) * n * 0.5; p = mat2(0.7071, -0.7071, 0.7071, 0.7071) * p + t;
        v = 1.0 - smoothstep(duty * 0.5 - s * 0.3, duty * 0.5 + s * 0.3, length(fract(p) - 0.5)); }
    else if (tex == 2) { float a = (uv.x * asp + uv.y) * n * 0.5 + t, b = (uv.x * asp - uv.y) * n * 0.5 - t;
        v = max(spBand(a, duty * 0.6, s), spBand(b, duty * 0.6, s)); }
    else { vec2 p = vec2(uv.x * asp, uv.y) * n * 0.25; float over = mod(floor(p.x) + floor(p.y), 2.0);
        float bx = spBand(p.x + t * 0.1, duty, s), by = spBand(p.y - t * 0.1, duty, s);
        v = mix(bx * 0.55 + by * 0.45 * (1.0 - bx), by * 0.55 + bx * 0.45 * (1.0 - by), over); }
    v = clamp(v + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
