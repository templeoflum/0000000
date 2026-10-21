/*{
  "DESCRIPTION": "SP Study 1 LEVEL - energy budget alone: full level chain (gain/lift/floor/curve/ceiling/key/soft) on identity loop. Feeds on comp content only.",
  "CREDIT": "SP study",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "inputImage",
      "LABEL": "Input",
      "TYPE": "image"
    },
    {
      "NAME": "gainv",
      "LABEL": "Gain",
      "TYPE": "float",
      "DEFAULT": 0.97,
      "MIN": 0.8,
      "MAX": 1.0
    },
    {
      "NAME": "floorv",
      "LABEL": "Floor",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.1
    },
    {
      "NAME": "keyv",
      "LABEL": "Key",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.5
    },
    {
      "NAME": "softv",
      "LABEL": "Soft",
      "TYPE": "float",
      "DEFAULT": 0.15,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "curvev",
      "LABEL": "Curve",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.4,
      "MAX": 2.5
    },
    {
      "NAME": "ceilv",
      "LABEL": "Ceiling",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.5,
      "MAX": 1.0
    },
    {
      "NAME": "liftv",
      "LABEL": "Lift",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.1
    }
  ]
}*/

void main() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 uv = isf_FragNormCoord;

    // the loop: previous comp frame, untouched map (identity) — ONLY the level law applies.
    // no injected content: the loop feeds on whatever the comp gives it
    vec4 c = IMG_NORM_PIXEL(inputImage, uv);
    // per-pass level chain: linear stage -> nonlinear stage -> ceiling
    vec3 col = max(c.rgb * gainv - floorv, 0.0);           // linear stage: gain and floor
    col = pow(col, vec3(curvev));                          // Curve: iterated nonlinearity — <1 hold-then-collapse, >1 crush-mids
    col = min(col + liftv, vec3(ceilv));                   // Lift AFTER the curve — study finding: pre-curve it
                                                           // cancels against Floor exactly (net L-F); post-curve they are independent
    // Key: luma below the key is transparent, above opaque. Soft = edge width. Key 0 = solid.
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    float w = 0.005 + softv * 0.25;
    float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv - w * 0.5, keyv + w * 0.5, lum);
    gl_FragColor = vec4(col, a);
}
