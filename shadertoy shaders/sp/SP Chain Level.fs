/*{
  "DESCRIPTION": "SP Chain LEVEL - the energy budget on a routed loop: Gain/Floor (base) + Curve/Lift/Ceiling, Key at the mix. Self-looping on a Video Router.",
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
    }
  ],
  "PASSES": [
    {
      "TARGET": "acc",
      "PERSISTENT": true
    },
    {}
  ]
}*/

float spLum(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main() {
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {
        vec4 live = IMG_NORM_PIXEL(inputImage, uv);          // the layer above, via the Router
        vec2 puv = uv;                                       // where the loop reads its past

        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        vec3 col = pow(prev, vec3(curvev));                   // Curve: iterated nonlinearity
        col = min(col + liftv, vec3(ceilv));                  // Lift post-curve (independent of Floor), Ceiling

        col = max(col * gainv - floorv, 0.0);                // the learned level base, in the loop
        vec3 outc = max(live.rgb, col);                       // dry never attenuated
        gl_FragColor = vec4(outc, 1.0);
    } else {
        vec3 c = IMG_NORM_PIXEL(acc, uv).rgb;
        float lum = spLum(c);
        float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);   // Key: at the mix
        gl_FragColor = vec4(c, a);
    }
}
