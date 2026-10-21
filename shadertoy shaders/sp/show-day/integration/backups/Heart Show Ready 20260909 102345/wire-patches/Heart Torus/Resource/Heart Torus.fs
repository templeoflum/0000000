/*{
  "CREDIT": "Geometric Exercise by balkhan, converted for Wire pipeline",
  "DESCRIPTION": "Heart control-ready copy; original preserved. Raymarched geometric torus assembly. Background transparent.",
  "CATEGORIES": [
    "generator",
    "raymarch"
  ],
  "ISFVSN": "2",
  "INPUTS": [
    {
      "NAME": "animationSpeed",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "torusSize",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color1R",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color1G",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color1B",
      "TYPE": "float",
      "DEFAULT": 0.9,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2R",
      "TYPE": "float",
      "DEFAULT": 0.95,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2G",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2B",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/
const float vignette=1.0;
const float camZ=1.857142857;
const float camY=0.5;
const float camX=0.5;


vec2  march(vec3 pos, vec3 dir);
vec3  camera(vec2 uv);
void  rotate(inout vec2 v, float angle);
float mylength(vec2 p);

float t;
vec3  ret_col;
vec3  h;
float mind, ming, mint, minl;

#define I_MAX 100.
#define E     0.0001
#define FAR   140.
#define PI    3.14159
#define TAU   PI*2.

vec2 modA(vec2 p, float count) {
    float an = TAU / count;
    float a  = atan(p.y, p.x) + an * .5;
    a = mod(a, an) - an * .5;
    return vec2(cos(a), sin(a)) * length(p);
}

float scene(vec3 p) {
    mind = 1e5; ming = 1e5; mint = 1e5; minl = 1e5;

    rotate(p.xz, 1.57 - .15 * t);
    rotate(p.yz, 1.57 - .125 * t);
    vec3 op = p;
    float var = (atan(p.x, p.z) + PI) / (TAU);
    var = var * 40.;
    p.xz = modA(p.xz, 40.);
    p.xz -= vec2(8., .0);

    rotate(p.xy, t * .25 * (mod(var - .5, 2.) <= 1. ? 1. : -1.));
    vec2 q = vec2(length(p.xy) - mix(1.0, 10.0, torusSize), p.z);
    mind = mylength(q) - .05;

    float vir = (atan(p.x, p.y) + PI) / (TAU);
    var = vir * 30.;
    p.xy = modA(p.xy, 30.) - vec2(.0, .0);
    p.xz -= vec2(4., .0);
    q = vec2(length(p.zx) - 0.25, p.y - .0);
    ming = mylength(q) - .05;
    mind = min(mind, ming);

    float as = (mind == ming ? 1. : 0.);
    ret_col = step(as, .0) * vec4(color1R,color1G,color1B,1.0).rgb + step(1., as) * vec4(color2R,color2G,color2B,1.0).rgb;

    rotate(p.xz, t * 1.5 * (mod(var, 2.) <= 1. ? 1. : -1.) * (mod(vir, 2.) <= 1. ? 1. : -1.));
    p.xz = modA(p.xz, 20.) - vec2(.0, -.0);
    p.xy -= vec2(.25, .0);
    q = vec2(length(p.xy) - .1, p.z);
    mint = mylength(q) - .02;
    mind = min(mind, mint);
    as = (mind == mint ? 1. : 0.);
    if (as == 1.) ret_col = vec4(color1R,color1G,color1B,1.0).rgb;

    // dodecahedron
    rotate(op.zx, t * .5);
    op.xz = modA(op.xz, 25.);
    op -= vec3(6., .0, 0.);
    op /= 1.732;
    vec3 b = vec3(.075);
    minl = max(max(abs(op.x) + .5 * abs(op.y) - b.x, abs(op.y) + .5 * abs(op.z) - b.y), abs(op.z) + .5 * abs(op.x) - b.z);
    b *= .95;
    minl = max(minl, -max(max(abs(op.x) + .5 * abs(op.y) - b.x, abs(op.y) - .5 * abs(op.z) - b.y), abs(op.z) + .5 * abs(op.x) - b.z));
    minl = max(minl, -max(max(abs(op.x) - .5 * abs(op.y) - b.x, abs(op.y) + .5 * abs(op.z) - b.y), abs(op.z) + .5 * abs(op.x) - b.z));
    minl = max(minl, -max(max(abs(op.x) + .5 * abs(op.y) - b.x, abs(op.y) + .5 * abs(op.z) - b.y), abs(op.z) - .5 * abs(op.x) - b.z));

    mind = min(mind, minl);
    as = mind == minl ? 1. : 0.;
    if (as == 1.) ret_col = vec4(color2R,color2G,color2B,1.0).rgb;

    h += .036125 * vec4(color2R,color2G,color2B,1.0).rgb / (pow(minl, 25.) + .5);

    return mind;
}

vec2 march(vec3 pos, vec3 dir) {
    vec2  dist       = vec2(0.0, 0.0);
    vec3  p          = vec3(0.0, 0.0, 0.0);
    vec2  s          = vec2(0.0, 0.0);
    float dinamyceps = E;
    for (float i = -1.; i < I_MAX; ++i) {
        p          = pos + dir * dist.y;
        dist.x     = scene(p);
        dist.y    += dist.x * 1.;
        dinamyceps = -dist.x + (dist.y) / (1500.);
        if (log(dist.y * dist.y / dist.x / 1e5) > 0. || dist.x < dinamyceps || dist.y > FAR) break;
        s.x++;
    }
    s.y = dist.y;
    return s;
}

float mylength(vec2 p) {
    p = p * p * p * p;
    p = p * p;
    return pow(p.x + p.y, 1. / 8.);
}

void rotate(inout vec2 v, float angle) {
    v = vec2(cos(angle) * v.x + sin(angle) * v.y, -sin(angle) * v.x + cos(angle) * v.y);
}

vec3 camera(vec2 uv) {
    float fov   = 1.;
    vec3  forw  = vec3(0.0, 0.0, -1.0);
    vec3  right = vec3(1.0, 0.0,  0.0);
    vec3  up    = vec3(0.0, 1.0,  0.0);
    return normalize(uv.x * right + uv.y * up + fov * forw);
}

void main() {
    float _animSpeed = mix(0.01, 1.0, animationSpeed);
    t = abs(TIME * _animSpeed);

    vec2 R  = RENDERSIZE.xy;
    vec2 uv = vec2(gl_FragCoord.xy - R / 2.) / min(R.x,R.y);

    vec3 dir = camera(uv);

    vec3 pos = vec3(
        mix(-2.0,  2.0,  camX),
        mix(-2.0,  2.0,  camY),
        mix( 5.0, 40.0,  camZ)
    );

    h = vec3(0.0);
    vec2 inter = march(pos, dir);

    // Miss — transparent
    if (inter.y > FAR) {
        gl_FragColor = vec4(0.0);
        return;
    }

    vec3 col = ret_col * (1. - inter.x * .025);
    col += h;

    float vig = clamp(1.5 - length(uv), .5, 1.) * clamp(1.1 - length(uv), .0, 1.);
    col *= mix(1.0, vig, vignette);

    gl_FragColor = vec4(col, 1.0);
}