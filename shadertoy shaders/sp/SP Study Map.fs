/*{
  "DESCRIPTION": "SP Study 2 MAP - per-pass spatial transform: zoom, 3-axis rotation (Z in-plane, X/Y perspective), drift, center, over the learned level base.",
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
      "NAME": "rotx",
      "LABEL": "Rot X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -360.0,
      "MAX": 360.0
    },
    {
      "NAME": "roty",
      "LABEL": "Rot Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -360.0,
      "MAX": 360.0
    },
    {
      "NAME": "rotz",
      "LABEL": "Rot Z",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -360.0,
      "MAX": 360.0
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
  ]
}*/

void main() {
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    vec2 ctr = vec2(cx, cy);
    vec2 q = (isf_FragNormCoord - ctr) * vec2(asp, 1.0);

    // MAP — one transform per pass. Rot Z spins in-plane; Rot X/Y tilt the sampling plane in
    // perspective (ray-plane intersection, same math as the figure's coin flip) — edge-on = vanish
    float ax = rotx * 0.017453293;
    float ay = roty * 0.017453293;
    float az = rotz * 0.017453293;
    vec3 e1 = vec3(cos(ay), 0.0, -sin(ay));
    vec3 e2 = vec3(sin(ay) * sin(ax), cos(ax), cos(ay) * sin(ax));
    vec3 n = cross(e1, e2);
    vec3 E = vec3(0.0, 0.0, 1.6);
    vec3 rd = vec3(q, 0.0) - E;
    float den = dot(n, rd);
    float ok = (abs(den) > 1e-5) ? 1.0 : 0.0;
    float t = -dot(n, E) / (den + ((den >= 0.0) ? 1e-6 : -1e-6));
    ok *= (t > 0.0) ? 1.0 : 0.0;
    vec3 H = E + t * rd;
    vec2 pq = vec2(dot(H, e1), dot(H, e2));

    float ca = cos(-az), sa = sin(-az);
    pq = mat2(ca, -sa, sa, ca) * pq / zoomv;
    pq.x /= asp;
    vec2 p = pq + ctr - vec2(dx, dy);

    // outside the frame there is no signal
    float inside = ok * ((p.x >= 0.0 && p.x <= 1.0 && p.y >= 0.0 && p.y <= 1.0) ? 1.0 : 0.0);
    vec4 c = IMG_NORM_PIXEL(inputImage, clamp(p, 0.0, 1.0)) * inside;

    // learned level base (Study 1): gain/floor in the loop, key at the mix
    vec3 col = max(c.rgb * gainv - floorv, 0.0);
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    float aa = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);
    gl_FragColor = vec4(col, c.a * aa);
}
