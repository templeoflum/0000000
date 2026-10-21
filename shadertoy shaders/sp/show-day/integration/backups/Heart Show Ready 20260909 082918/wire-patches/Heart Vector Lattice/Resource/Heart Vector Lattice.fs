/*{
  "CREDIT": "by rez, converted for Wire pipeline",
  "DESCRIPTION": "Heart control-ready Field copy; original shader body preserved. Raymarched bar/tube lattice.",
  "CATEGORIES": [
    "generator",
    "raymarching"
  ],
  "ISFVSN": "2",
  "INPUTS": [
    {
      "NAME": "camSpeed",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rotX",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "rotZ",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "colorR",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "colorG",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "colorB",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

const float PI = 3.14159265358979323846;

vec2 rotate(vec2 k, float t) {
    return vec2(cos(t) * k.x - sin(t) * k.y, sin(t) * k.x + cos(t) * k.y);
}

float rand(in vec2 p, in float t, in float v) {
    return fract(sin(dot(p + mod(t, 1.0), vec2(12.9898, 78.2333))) * v);
}

float scene(vec3 p) {
    float bar_p = 1.0;
    float bar_w = bar_p * (0.125 + 0.03125 * float(1.0 + 2.0 * sin(PI * p.z * 2.0 - PI * 0.5)));
    float bar_x = length(max(abs(mod(p.yz, bar_p) - bar_p * 0.5) - bar_w, 0.0));
    float bar_y = length(max(abs(mod(p.xz, bar_p) - bar_p * 0.5) - bar_w, 0.0));
    float bar_z = length(max(abs(mod(p.xy, bar_p) - bar_p * 0.5) - bar_w, 0.0));
    float tube_p = 0.125;
    float tube_w = tube_p * 0.375;
    float tube_x = length(mod(p.yz, tube_p) - tube_p * 0.5) - tube_w;
    float tube_y = length(mod(p.xz, tube_p) - tube_p * 0.5) - tube_w;
    float tube_z = length(mod(p.xy, tube_p) - tube_p * 0.5) - tube_w;
    return -min(min(max(max(-bar_x, -bar_y), -bar_z), tube_y), tube_z);
}

void main() {
    float _camSpeed = mix(0.0,  2.0,  camSpeed);
    float _rotX     = mix(0.0,  2.0,  rotX);
    float _rotZ     = mix(0.0,  2.0,  rotZ);
    vec3  _colorMul = vec3(mix(0.5, 1.5, colorR),
                           mix(0.5, 1.5, colorG),
                           mix(0.5, 1.5, colorB));

    float speed   = TIME * _camSpeed;
    float ground_z = 4.0 * sin(PI * TIME * 0.0625);

    vec2 position = gl_FragCoord.xy / RENDERSIZE.xy;
    vec2 p = -1.0 + 2.0 * position;

    vec3 dir = normalize(vec3(p * vec2(1.0 / RENDERSIZE.y * RENDERSIZE.x, 1.0), 1.0));
    dir.yz = rotate(dir.yz, PI * 0.5 * sin(TIME * 0.25 * _rotX));
    dir.xy = rotate(dir.xy, PI * 1.0 * cos(TIME * 0.25 * _rotZ));

    vec3 ray = vec3(0.0, 0.0, ground_z);
    float t = 0.0;

    for (int i = 0; i < 64; i++) {
        float k = scene(ray + dir * t);
        if (abs(k) < 0.001) break;
        t += k * 0.5;
    }

    vec3 hit = ray + dir * t;
    vec2 h = vec2(0.005, -0.005);
    vec3 n = normalize(vec3(scene(hit + h.xyy), scene(hit + h.yxx), scene(hit + h.yyx)));

    float c = (n.x * 2.0 + n.y + n.z) * 0.25 - t * 0.025;
    vec3 color = vec3(
        c * t * 0.625 - p.x * 0.125,
        c * t * 0.25  + t * 0.03125,
        c * 0.375     + t * 0.0625 + p.y * 0.125
    );
    color = smoothstep(0.4, 0.7, c) + color * color;
    color *= 0.6 + 0.4 * rand(p, TIME, 43758.5453);
    color = vec3(
        color.x * 0.9 - 0.1 * cos(p.x * RENDERSIZE.x),
        color.y * 0.95 + 0.05 * sin(p.y * RENDERSIZE.x / 2.0),
        color.z * 0.9 + 0.1 * cos(PI / 2.0 + p.x * RENDERSIZE.x)
    );

    color *= _colorMul;

    gl_FragColor = vec4(color, 1.0);
}