/*{
  "DESCRIPTION": "SP Study COLOR (chain) - Hue Step deg/pass, Sat x/pass, Invert flavor, inside the loop. Self-looping on a Video Router.",
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
      "NAME": "hue",
      "LABEL": "Hue Step",
      "TYPE": "float",
      "DEFAULT": 3.0,
      "MIN": -30.0,
      "MAX": 30.0
    },
    {
      "NAME": "satv",
      "LABEL": "Sat",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.5,
      "MAX": 1.5
    },
    {
      "NAME": "inv",
      "LABEL": "Invert",
      "TYPE": "bool",
      "DEFAULT": false
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

vec3 spHueR(vec3 c, float a) {
    const vec3 k = vec3(0.57735);
    return c * cos(a) + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - cos(a));
}
void main() {
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {
        vec4 live = IMG_NORM_PIXEL(inputImage, uv);          // the layer above, via the Router
        vec2 puv = uv;                                       // where the loop reads its past

        vec3 prev = IMG_NORM_PIXEL(acc, puv).rgb;
        float pres = smoothstep(0.0, 0.04, spLum(prev));      // presence before color ops: Invert recolors what exists
        vec3 col = prev;
        if (abs(hue) > 0.01) col = clamp(spHueR(col, hue * 0.017453293), 0.0, 1.0);
        col = clamp(mix(vec3(spLum(col)), col, satv), 0.0, 1.0);
        if (inv) col = (vec3(1.0) - col) * pres;

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
