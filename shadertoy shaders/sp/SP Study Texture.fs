/*{
  "DESCRIPTION": "SP Study TEXTURE (chain) - Diffuse and Etch both live in the loop; Grain sets the kernel scale. Self-looping on a Video Router.",
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
      "NAME": "dif",
      "LABEL": "Diffuse",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "etch",
      "LABEL": "Etch",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 2.0
    },
    {
      "NAME": "grain",
      "LABEL": "Grain",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
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
        float r = (0.0008 + grain * 0.012);                   // Grain = kernel radius (pattern scale)
        vec2 px = vec2(r / (RENDERSIZE.x / RENDERSIZE.y), r);
        vec3 b = (IMG_NORM_PIXEL(acc, puv + vec2( px.x, 0.0)).rgb + IMG_NORM_PIXEL(acc, puv + vec2(-px.x, 0.0)).rgb
                + IMG_NORM_PIXEL(acc, puv + vec2(0.0,  px.y)).rgb + IMG_NORM_PIXEL(acc, puv + vec2(0.0, -px.y)).rgb) * 0.25;
        vec3 col = clamp(mix(prev, b, dif) + (prev - b) * etch, 0.0, 1.0);   // spread toward b, fight against b

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
