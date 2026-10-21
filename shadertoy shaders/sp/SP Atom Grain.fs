/*{
  "DESCRIPTION": "SP Atom GRAIN - film / static / dust / lines; Amount, Size (cell px), Flicker (re-roll rate), Level. Alpha = value. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "grain",
      "LABEL": "Grain",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "film",
        "static",
        "dust",
        "lines"
      ]
    },
    {
      "NAME": "amount",
      "LABEL": "Amount",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sizev",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "flicker",
      "LABEL": "Flicker",
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
float spVal(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y); }
void main() {
    vec2 px = gl_FragCoord.xy;
    float frame = floor(TIME * (1.0 + flicker * 59.0));     // Flicker = how often the grain re-rolls
    float cell = 1.0 + sizev * 12.0;                         // Size = grain cell in pixels
    vec2 g = floor(px / cell) + frame * 7.31;
    float v;
    if (grain == 0) v = spVal(g * 0.7) * 0.6 + spN2(g) * 0.4;                          // film: clumpy
    else if (grain == 1) v = spN2(g);                                                    // static: white noise
    else if (grain == 2) v = (spN2(g) > 0.985 - amount * 0.1) ? 1.0 : 0.0;              // dust: sparse specks
    else { float col = floor(px.x / cell) + floor(frame * 0.3) * 3.0; v = (spN2(vec2(col, 1.0)) > 0.96) ? spVal(vec2(col, px.y * 0.02 + frame)) : 0.0; }  // lines: scratches
    v = clamp(v * amount + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
