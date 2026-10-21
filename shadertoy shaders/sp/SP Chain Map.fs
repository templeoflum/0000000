/*{
  "DESCRIPTION": "SP Chain MAP - per-pass zoom/rotate/drift/center on a routed loop, over the level base. Self-looping on a Video Router.",
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
      "NAME": "zoomv",
      "LABEL": "Zoom",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.8,
      "MAX": 1.2
    },
    {
      "NAME": "rotz",
      "LABEL": "Rotate",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -30.0,
      "MAX": 30.0
    },
    {
      "NAME": "dx",
      "LABEL": "Drift X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.02,
      "MAX": 0.02
    },
    {
      "NAME": "dy",
      "LABEL": "Drift Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.02,
      "MAX": 0.02
    },
    {
      "NAME": "cx",
      "LABEL": "Center X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cy",
      "LABEL": "Center Y",
      "TYPE": "float",
      "DEFAULT": 0.5,
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

        float asp = RENDERSIZE.x / RENDERSIZE.y;
        vec2 ctr = vec2(cx, cy);
        vec2 q = (uv - ctr) * vec2(asp, 1.0);
        float a = -rotz * 0.017453293;
        q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q / zoomv;   // inverse per-pass map
        puv = q / vec2(asp, 1.0) + ctr - vec2(dx, dy);
        float inside = (puv.x >= 0.0 && puv.x <= 1.0 && puv.y >= 0.0 && puv.y <= 1.0) ? 1.0 : 0.0;
        vec3 col = IMG_NORM_PIXEL(acc, clamp(puv, 0.0, 1.0)).rgb * inside;   // outside the frame: no signal

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
