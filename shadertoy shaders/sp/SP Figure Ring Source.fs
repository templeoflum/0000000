/*{
  "CREDIT": "RainbowRingCubicTwist by mojovideotech, converted for Wire pipeline",
  "DESCRIPTION": "Heart Figure ring source: bounded by the shorter frame dimension; use the shared Figure Transform for placement and size.",
  "CATEGORIES": [
    "generator",
    "rainbow",
    "circular",
    "rotation"
  ],
  "ISFVSN": "2",
  "INPUTS": [
    {
      "NAME": "thickness",
      "TYPE": "float",
      "DEFAULT": 0.75,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "twists",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rate",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gamma",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

vec3 ringColor(vec2 baseP, float twistCount, float T, vec2 R, float thickness, float gamma) {
    vec2 P = baseP;
    P *= vec2(2.6 - thickness, twistCount);
    vec4 S = 0.08 * cos(1.5 * vec4(0.0, 1.0, 2.0, 3.0) + T + P.y + sin(P.y) * cos(T));
    // Outside the analytical ring support, cancellation must be exactly zero.
    // Low gamma otherwise amplifies floating-point residue into a full-frame haze.
    if (abs(P.x) > 0.08001) return vec3(0.0);
    vec4 E = S.yzwx;
    vec4 F = max(P.x - S, E - P.x);
    vec3 raw = (dot(clamp(F * R.y, 0.0, 1.0), 72.0 * (S - E)) * (S - 0.1)).rgb;
    return pow(max(raw, 0.0), vec3(gamma));
}

void main() {
    float _thickness = mix(0.5,  2.0,  thickness);
    float _rate      = mix(-2.0, 2.0,  rate);
    float _gamma     = mix(0.25, 1.0,  gamma);

    float _twistsRaw   = mix(1.0, 5.0, twists);
    float _twistsFloor = floor(_twistsRaw);
    float _twistsCeil  = ceil(_twistsRaw);
    float _twistsFrac  = fract(_twistsRaw);

    float T = TIME * _rate;
    vec2 R = RENDERSIZE;

    // Maximum ring support is (0.333 + 0.08 / 0.6) / 1.18 < 0.396 of the short side.
    // Frame-derived projection leaves room without masking/cropping the figure.
    vec2 P = (gl_FragCoord.xy - 0.5 * R) * (1.18 * R.y / min(R.x, R.y));
    vec2 baseP = vec2(length(P) / R.y - 0.333, atan(P.y, P.x));

    vec3 rgb1 = ringColor(baseP, _twistsFloor, T, R, _thickness, _gamma);
    vec3 rgb2 = ringColor(baseP, _twistsCeil,  T, R, _thickness, _gamma);

    // Difference blend — scaled by frac so it's zero at integers (clean) and max at 0.5
    float blendFac = smoothstep(0.0, 1.0, _twistsFrac);
    vec3 rgb = mix(rgb1, rgb2, blendFac);

    float luma  = dot(rgb, vec3(0.299, 0.587, 0.114));
    float alpha = clamp(luma * 8.0, 0.0, 1.0);

    gl_FragColor = vec4(rgb, alpha);
}