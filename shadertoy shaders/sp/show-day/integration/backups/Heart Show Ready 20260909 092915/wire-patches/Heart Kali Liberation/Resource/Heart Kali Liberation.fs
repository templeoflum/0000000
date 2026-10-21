/*{
  "CATEGORIES": [
    "Psychedelic",
    "Fractal"
  ],
  "DESCRIPTION": "Heart control-ready Field copy; original preserved. Enhanced shader with tunable parameters for psychedelic effects.",
  "INPUTS": [
    {
      "NAME": "speed",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": -2.0,
      "MAX": 2.0
    },
    {
      "NAME": "zoom",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.1,
      "MAX": 5.0
    },
    {
      "NAME": "morphing",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 2.0
    },
    {
      "NAME": "colorPulse",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 5.0
    },
    {
      "NAME": "brightness",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 3.0
    },
    {
      "NAME": "contrast",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 3.0
    },
    {
      "NAME": "cameraX",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -5.0,
      "MAX": 5.0
    },
    {
      "NAME": "cameraY",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -5.0,
      "MAX": 5.0
    },
    {
      "NAME": "cameraZ",
      "TYPE": "float",
      "DEFAULT": -10.0,
      "MIN": -60.0,
      "MAX": -1.0
    },
    {
      "NAME": "colorPalette",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 3.0
    }
  ]
}*/

#define resolution RENDERSIZE

vec3 objcol;

float hash12(vec2 p) {
    vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, s, -s, c);
}

float de(vec3 pos, float t) {
    float a = sin(t * 6.28318 / 17.0) * 4.0;
    float f = sin(t * 5.0 + sin(t * 20.0) * 0.2);

    pos.xz *= rot(t + 0.5);
    pos.yz *= rot(t);
    vec3 p = pos;
    float s = 1.0;

    for (int i = 0; i < 4; i++) {
        p = abs(p) * 1.3 - 0.5 - f * 0.1 - a;
        p.xy *= rot(radians(45.0));
        p.xz *= rot(radians(45.0));
        s *= 1.3;
    }

    float fra = length(p) / s - 0.5;
    pos.xy *= rot(t);
    p = abs(pos) - 2.0 - a;
    float d = length(p) - 0.7;
    d = min(d, max(length(p.xz) - 0.1, p.y));
    d = min(d, max(length(p.yz) - 0.1, p.x));
    d = min(d, max(length(p.xy) - 0.1, p.z));
    p = abs(pos);
    p.x -= 4.0 + a + f * 0.5;
    d = min(d, length(p) - 0.7);
    p = abs(pos);
    p.y -= 4.0 + a + f * 0.5;
    d = min(d, length(p) - 0.7);
    d = min(d, max(length(p.xz) - 0.1, p.y));
    d = min(d, fra);
    objcol = abs(p);
    if (d == fra) objcol = vec3(2.0, 0.0, 0.0);
    return d;
}

vec3 normal(vec3 p, float t) {
    vec2 d = vec2(0.0, 0.01);
    return normalize(vec3(
        de(p + d.yxx, t),
        de(p + d.xyx, t),
        de(p + d.xxy, t)) - de(p, t));
}

vec4 march(vec3 from, vec3 dir, float t) {
    float d = 0.0, td = 0.0;
    // maxdist scales with camera distance so object never gets clipped
    float maxdist = length(from) * 4.0;
    vec3 p = from, col = vec3(0.0);
    float hits = 0.0;

    for (int i = 0; i < 100; i++) {
        float d2 = de(p, t) * (1.0 - hash12(gl_FragCoord.xy + t) * 0.2);
        if (d2 < 0.0) {
            vec3 n = normal(p, t);
            dir = reflect(dir, n);
            d2 = 0.1;
        }
        d = max(0.01, abs(d2));
        if (d < 0.05) hits += 1.0;
        p += d * dir;
        td += d;
        if (td > maxdist) break;
        col += (0.03 / maxdist) * objcol * length(from);
    }
    return vec4(pow(col, vec3(2.0)), hits);
}

vec3 getColor(float t) {
    t = fract(t);
    if (colorPalette < 1.0) {
        return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.0, 0.33, 0.67)));
    } else if (colorPalette < 2.0) {
        return vec3(
            min(1.0, t * 1.5),
            min(1.0, max(0.0, t - 0.3)),
            0.0
        );
    } else if (colorPalette < 3.0) {
        return fract(vec3(t * 0.61, t * 0.83, t * 0.47));
    } else {
        return abs(fract(vec3(t * 3.0, t * 5.0, t * 7.0)) * 2.0 - 1.0);
    }
}

vec3 adjustBrightnessContrast(vec3 color, float b, float c) {
    color *= b;
    color = (color - 0.5) * c + 0.5;
    return clamp(color, 0.0, 1.0);
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution.xy - 0.5;
    uv.x *= resolution.x / resolution.y;

    float t = TIME * speed;

    vec3 from = vec3(cameraX, cameraY, cameraZ + zoom);
    vec3 dir = normalize(vec3(uv, 1.0));

    dir.x += sin(t * morphing) * 0.1;
    dir.y += cos(t * morphing) * 0.1;

    vec4 result = march(from, dir, t);

    if (result.a < 0.005) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }

    vec3 col = result.rgb;
    col *= getColor(t * colorPulse);
    col = adjustBrightnessContrast(col, brightness, contrast);

    gl_FragColor = vec4(col, 1.0);
}