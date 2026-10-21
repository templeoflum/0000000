/*{
  "DESCRIPTION": "SP Study FOLD (chain) - Mirror picker off/x/xy/radial-6 with blendable Fold amount and center, inside the loop. Self-looping on a Video Router.",
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
      "NAME": "mir",
      "LABEL": "Mirror",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "off",
        "x",
        "xy",
        "radial"
      ]
    },
    {
      "NAME": "foldv",
      "LABEL": "Fold",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
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
        vec2 f = q;
        if (mir == 1) f.x = abs(q.x);
        else if (mir == 2) f = abs(q);
        else if (mir == 3) {
            float an = atan(q.y, q.x); float rr = length(q);
            an = abs(mod(an, 1.0471976) - 0.5235988);          // 6-fold sector
            f = vec2(cos(an), sin(an)) * rr;
        }
        q = mix(q, f, foldv);                                  // the fold is blendable
        puv = q / vec2(asp, 1.0) + ctr;
        float inside = (puv.x >= 0.0 && puv.x <= 1.0 && puv.y >= 0.0 && puv.y <= 1.0) ? 1.0 : 0.0;
        vec3 col = IMG_NORM_PIXEL(acc, clamp(puv, 0.0, 1.0)).rgb * inside;

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
