/*{
  "DESCRIPTION": "SP Study MIXER (chain) - the circuit element: Blend picker (max/add/screen/mix/difference/multiply) x Feed, live vs loop. Self-looping on a Video Router.",
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
      "NAME": "blend",
      "LABEL": "Blend",
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
        "max",
        "add",
        "screen",
        "mix",
        "difference",
        "multiply"
      ]
    },
    {
      "NAME": "feed",
      "LABEL": "Feed",
      "TYPE": "float",
      "DEFAULT": 1.0,
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
        vec3 col = prev;

        col = max(col * gainv - floorv, 0.0);                // the learned level base, in the loop

        col *= feed;                                           // Feed = how much loop re-enters
        vec3 l = live.rgb, outc;
        if      (blend == 0) outc = max(l, col);
        else if (blend == 1) outc = min(l + col, 1.0);
        else if (blend == 2) outc = 1.0 - (1.0 - l) * (1.0 - col);
        else if (blend == 3) outc = mix(l, col, 0.5);
        else if (blend == 4) outc = abs(l - col);
        else                 outc = l * col + l * (1.0 - feed);   // multiply gates on presence; Feed 0 = passthrough

        gl_FragColor = vec4(outc, 1.0);
    } else {
        vec3 c = IMG_NORM_PIXEL(acc, uv).rgb;
        float lum = spLum(c);
        float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);   // Key: at the mix
        gl_FragColor = vec4(c, a);
    }
}
