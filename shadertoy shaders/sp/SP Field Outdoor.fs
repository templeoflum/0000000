/*{
  "DESCRIPTION": "SP Field OUTDOOR atom - layered horizon: parallax silhouettes (ridges/dunes/sea) or sky over a gradient. Grayscale, alpha = value. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "ground",
      "LABEL": "Ground",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "ridges",
        "dunes",
        "sea",
        "sky"
      ]
    },
    {
      "NAME": "horizon",
      "LABEL": "Horizon",
      "TYPE": "float",
      "DEFAULT": 0.45,
      "MIN": 0.1,
      "MAX": 0.9
    },
    {
      "NAME": "scalev",
      "LABEL": "Scale",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "driftv",
      "LABEL": "Drift",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hazev",
      "LABEL": "Haze",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrast",
      "LABEL": "Contrast",
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

float spN1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float spN2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float spVal(vec2 p) {
    vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(spN2(i), spN2(i + vec2(1, 0)), f.x), mix(spN2(i + vec2(0, 1)), spN2(i + vec2(1, 1)), f.x), f.y);
}
float spFbm(vec2 p) {                                     // 4 octaves, plain
    return 0.5 * spVal(p) + 0.25 * spVal(p * 2.03 + 7.7) + 0.125 * spVal(p * 4.01 + 13.1) + 0.0625 * spVal(p * 8.07 + 29.3);
}
float spRidge(vec2 p) {                                   // ridged: 1 - |2n-1|, stacked
    float r = 0.0, a = 0.5;
    for (int k = 0; k < 4; k++) { r += a * (1.0 - abs(2.0 * spVal(p) - 1.0)); p = p * 2.03 + 11.3; a *= 0.5; }
    return r;
}
// height of silhouette layer k at horizontal x (0..1 frame units), scrolled by t
float spHeight(int g, float x, float t, float k) {
    float f = 1.5 + scalev * 6.0;                          // spatial frequency, the fundamental
    float sx = x * f * (0.6 + 0.35 * k) + t * (0.3 + 0.5 * k) + k * 17.0;   // nearer layers move faster (parallax)
    if (g == 0) return spRidge(vec2(sx, k * 3.1)) * 0.5;                          // ridges: sharp peaks
    if (g == 1) return 0.5 + 0.5 * sin(sx * 2.0 + spVal(vec2(sx * 0.5, k)) * 3.0) * 0.5 + 0.15 * spVal(vec2(sx * 3.0, k));  // dunes: long soft waves
    if (g == 2) return 0.5 + 0.06 * sin(sx * 9.0 + t * 3.0 + k) + 0.05 * spVal(vec2(sx * 6.0, t * 0.7 + k));   // sea: flat, rippling
    return 0.0;                                                                   // sky: no ground silhouettes
}
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float t = TIME * driftv * 0.25;
    float con = 0.2 + contrast * 2.8;

    // SKY — gradient up from the horizon, with cloud fbm that only the sky flavor lets through fully
    float sy = clamp((uv.y - horizon) / max(1.0 - horizon, 0.001), 0.0, 1.0);
    float cloud = spFbm(vec2(uv.x * (2.0 + scalev * 6.0) + t * 0.6, uv.y * 3.0 + t * 0.1));
    float cloudAmt = (ground == 3) ? 1.0 : 0.25;
    float sky = mix(0.55, 0.25, sy) + (cloud - 0.5) * cloudAmt * 0.5;
    sky *= smoothstep(0.0, 0.05, uv.y - horizon + 0.02);  // nothing below the horizon

    // GROUND — 4 silhouette layers far→near; near = darker, far = hazed toward the sky value
    float v = sky;
    for (int k = 0; k < 4; k++) {
        float fk = float(k);
        float depthAmt = (fk + 1.0) / 4.0;                 // 0.25 far … 1.0 near
        float h = spHeight(ground, uv.x, t, fk);
        float amp = (ground == 2) ? 0.05 : 0.12 + 0.1 * fk; // sea stays flat
        float yLine = horizon - fk * 0.09 * (ground == 2 ? 0.6 : 1.0) + h * amp;
        float edge = smoothstep(yLine + 0.004, yLine - 0.004, uv.y);   // 1 below the line
        float shade = mix(0.18, 0.05, depthAmt);           // near = darkest
        float hazed = mix(shade, sky, hazev * (1.0 - depthAmt));   // far layers fade into sky
        v = mix(v, hazed, edge);
    }
    if (ground == 3) v = sky;                               // sky flavor: the field IS the sky

    v = clamp((v - 0.35) * con + 0.35 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);                        // alpha ground: dark = open
}
