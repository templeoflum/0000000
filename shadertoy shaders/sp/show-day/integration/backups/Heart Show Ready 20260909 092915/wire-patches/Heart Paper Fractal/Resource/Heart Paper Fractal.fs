/*{
  "CREDIT": "Code by Flopine, converted for Wire pipeline",
  "DESCRIPTION": "Heart control-ready Field copy; original shader body preserved. Plane folding fractal with raymarched SDF, glow, and genuine alpha transparency.",
  "CATEGORIES": [
    "generator"
  ],
  "INPUTS": [
    {
      "NAME": "rotAsymX",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rotAsymY",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "spinRate",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "foldRate",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "spinOffset",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "foldOffset",
      "TYPE": "float",
      "DEFAULT": 0.03,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sizeOffset",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "foldDistA",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "foldDistB",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "camX",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "camY",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "camZ",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "glowAmount",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

// Code by Flopine — plane folding fractal
// Converted: semantic parameter names, 0-1 normalized, genuine alpha, procedural noise

float hash21(vec2 x) {
    return fract(sin(dot(x, vec2(54.4, 62.1))) * 457.5);
}

mat2 rot(float a, float asymX, float asymY) {
    return mat2(cos(a), sin(a * asymX), -sin(a * asymY), cos(a));
}

void mo(inout vec2 p, vec2 d) {
    p = abs(p) - d;
    if (p.y > p.x) p = p.yx;
}

float plane(vec3 p, vec3 n) {
    return dot(p, normalize(n));
}

float _foldDistA;
float _foldDistB;

float cut_ps(vec3 p, float s) {
    p *= s;
    mo(p.xy, vec2(1.0));
    mo(p.yz, vec2(0.6 * _foldDistA + _foldDistB));
    mo(p.xz, vec2(0.1 * _foldDistA + _foldDistB));
    return plane(p, vec3(1., 1., 4.)) / s;
}

float _asymX;
float _asymY;
float _spinRate;
float _spinOffset;

float prim1(vec3 p, float s) {
    p.xz *= rot(TIME * _spinRate + _spinOffset, _asymX, _asymY);
    return cut_ps(p, s);
}

float _foldRate;
float _foldOffset;
float _sizeOffset;

float fractal(vec3 p) {
    float size = 1.0;
    float d = prim1(p, size - _sizeOffset);
    for (int i = 1; i < 5; i++) {
        float ratio = float(i) / 5.0;
        p.yz *= rot(TIME * ratio * _foldRate + _foldOffset, _asymX, _asymY);
        size -= 0.2;
        d = min(d, prim1(p, size + _sizeOffset));
    }
    return d;
}

float g1 = 0.0;

float SDF(vec3 p) {
    // Procedural noise replacing iChannel0 texture
    float noise = hash21(mod(p.xy * 0.1 + TIME, 1.0)) * 0.3;
    float sphe = length(p) - (0.8 + noise);
    g1 += 0.1 / (0.1 + sphe * sphe);
    return max(-length(p + vec3(0., 0., 4.5)) + 0.8, min(sphe, fractal(p)));
}

void main() {
    // Remap 0-1 inputs to working ranges
    _asymX      = mix(0.0,  2.0,  rotAsymX);
    _asymY      = mix(0.0,  2.0,  rotAsymY);
    _spinRate   = mix(0.0,  2.0,  spinRate);
    _foldRate   = mix(0.0,  2.0,  foldRate);
    _spinOffset = mix(0.0,  10.0, spinOffset);
    _foldOffset = mix(0.0,  10.0, foldOffset);
    _sizeOffset = mix(-0.5, 0.5,  sizeOffset);
    _foldDistA  = mix(0.0,  1.0,  foldDistA);
    _foldDistB  = mix(0.0,  1.0,  foldDistB);
    float _glowAmount = mix(0.0, 0.5, glowAmount);

    float _camX = mix(0.0,  20.0, camX);
    float _camY = mix(0.0,  10.0, camY);
    float _camZ = mix(0.0,  5.0,  camZ);

    vec2 uv = (2.0 * gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
    float dither = hash21(uv);

    vec3 ro = vec3(0.001 + 10.0 - _camX, 0.001 + 5.0 - _camY, -4.5 - _camZ);
    vec3 rd = normalize(vec3(uv, 0.8));
    vec3 p  = ro;

    float shad = 0.0;
    bool hit = false;

    for (float i = 0.0; i < 64.0; i++) {
        float d = SDF(p);
        if (d < 0.001) {
            hit = true;
            shad = i / 64.0;
            break;
        }
        d *= 0.8 + dither * 0.1;
        p += d * rd;
    }

    if (hit) {
        vec3 col = vec3(1.0 - shad);
        col += g1 * vec3(0.15, 0.0, 0.1) * _glowAmount;
        // Glow bleeds into background with partial alpha on non-hit pixels
        gl_FragColor = vec4(col, 1.0);
    } else {
        // Miss — transparent, but preserve glow halo
        float glowAlpha = clamp(g1 * _glowAmount, 0.0, 1.0);
        vec3 glowCol = g1 * vec3(0.15, 0.0, 0.1) * _glowAmount;
        gl_FragColor = vec4(glowCol, glowAlpha);
    }
}