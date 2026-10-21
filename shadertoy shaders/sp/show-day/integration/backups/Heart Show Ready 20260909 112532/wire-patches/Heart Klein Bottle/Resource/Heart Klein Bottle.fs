/*{
  "DESCRIPTION": "Heart Klein Bottle: guarded quaternion, ray and light math; shared Figure Transform owns placement. Original preserved.",
  "CREDIT": "lara / Shadertoy",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "quatW",
      "LABEL": "Quat W",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatX",
      "LABEL": "Quat X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatY",
      "LABEL": "Quat Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatZ",
      "LABEL": "Quat Z",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "refractIdx",
      "LABEL": "Refraction",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "wallThickness",
      "LABEL": "Wall Thickness",
      "TYPE": "float",
      "DEFAULT": 0.02,
      "MIN": 0.01,
      "MAX": 0.08
    },
    {
      "NAME": "exposure",
      "LABEL": "Exposure",
      "TYPE": "float",
      "DEFAULT": 2.0,
      "MIN": 0.5,
      "MAX": 4.0
    }
  ]
}*/
const float camDist=9.0;
const float fov=3.0;


#define S 256
#define P 0.001
#define R 2.
#define D 25.

#define PI 3.1415926

struct Ray { vec3 o; vec3 d; };
struct Hit { vec3 p; float t; float d; };

Ray _ray;

float _d;

mat3 quatToMat(vec4 q) {
    float q2=dot(q,q); q=q2>1e-10?q*inversesqrt(q2):vec4(0,0,0,1);
    float xx = q.x*q.x, yy = q.y*q.y, zz = q.z*q.z;
    float xy = q.x*q.y, xz = q.x*q.z, yz = q.y*q.z;
    float wx = q.w*q.x, wy = q.w*q.y, wz = q.w*q.z;
    return mat3(
        1.0 - 2.0*(yy+zz), 2.0*(xy+wz),     2.0*(xz-wy),
        2.0*(xy-wz),        1.0 - 2.0*(xx+zz), 2.0*(yz+wx),
        2.0*(xz+wy),        2.0*(yz-wx),     1.0 - 2.0*(xx+yy)
    );
}

mat2 rot(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}

float scene(vec3 p) {
    float t = wallThickness;
    float d = 1e10;

    p.y += .5;
    p.xy *= rot(PI/2.);

    vec3 q = p + vec3(1. - cos((1. - p.y)/3.*PI), 0, 0);
    float y = pow(sin((1. - p.y)/3.*PI/2.), 2.);

    float tube_hollow = max(max(abs(length(q.xz) - 0.5 + 0.25*y) - t, q.y - 1.0), -q.y - 2.0);
    float tube_solid = max(max(length(q.xz) - 0.5 + 0.25*y, q.y - 1.0), -q.y - 2.0);

    q = p - vec3(0, 1, 0);
    d = min(d, max(abs(length(vec2(length(q.xz) - 1.0, q.y)) - 0.5) - t, -q.y));

    q = p;
    d = min(d, max(max(max(abs(length(q.xz) - 1.5 + 1.25*y), q.y - 1.0), -q.y - 2.0) - t, -tube_solid));

    d = min(d, tube_hollow);

    q = p + vec3(1, 2, 0);
    d = min(d, max(abs(length(vec2(length(q.xy) - 1.0, q.z)) - 0.25) - t, q.y));

    return _d = d;
}

vec3 getNormal(vec3 p) {
    vec2 e = vec2(P, 0);
    return normalize(vec3(
        scene(p + e.xyy) - scene(p - e.xyy),
        scene(p + e.yxy) - scene(p - e.yxy),
        scene(p + e.yyx) - scene(p - e.yyx)
    ));
}

Hit march(Ray r) {
    float t = 0.0;
    float d;
    for (int i = 0; i < S; i++) {
        d = scene(r.o + r.d*t);
        t += d/R;
        if (d < P || t > D) break;
    }
    return Hit(r.o + r.d*t, t, d);
}

vec3 camPos;

vec3 getColor(Hit h) {
    if (h.d > P || h.t > D) return vec3(-1.0);

    vec4 col = vec4(0);
    vec3 light = camPos;
    Hit _h = h;
    float rIdx = mix(1.0, 2.0, refractIdx);

    for (int i = 0; i < 10; i++) {
        if (i == 2) { h = _h; _ray.d = normalize(h.p-camPos); }

        vec3 n = getNormal(h.p);
        float diff = max(dot(normalize(light - h.p), n), 0.0);
        float spec = pow(max(dot(reflect(normalize(h.p - light), n), normalize(camPos - h.p)), 0.0), 100.);
        vec4 c = vec4(vec3(.8, .9, 1)*diff + spec, .15);

        float facing=clamp(abs(dot(normalize(h.p-camPos),n)),0.0,1.0);
        float fresnel=.04+.96*pow(1.0-facing,5.0);
        c.rgb=c.rgb*(1.0-.7*fresnel)+vec3(.025,.035,.05);

        col.rgb = col.rgb*(1. - c.a) + c.rgb*c.a;
        col.w = clamp(col.w + c.a, 0., 1.);

        vec3 incident=normalize(_ray.d);
        n=faceforward(n,incident,n);
        vec3 nextDir=i>1?refract(incident,n,1.0/rIdx):reflect(incident,n);
        if(dot(nextDir,nextDir)<1e-10)nextDir=reflect(incident,n);
        _ray.d=normalize(nextDir);

        _ray.o = h.p + _ray.d*.1;
        h = march(_ray);
        if (h.d > P) break;
    }

    return pow(clamp(col.rgb*exposure,0.0,1.0),vec3(1.0/2.2));
}

void main() {
    vec2 uv = (2.0*gl_FragCoord.xy - RENDERSIZE.xy) / min(RENDERSIZE.x,RENDERSIZE.y);

    mat3 cam = quatToMat(vec4(quatX, quatY, quatZ, quatW));

    camPos = cam * vec3(0, 0, camDist);
    vec3 rd = cam * normalize(vec3(uv, -fov / camDist * 4.0));

    _ray = Ray(camPos, rd);

    Hit h = march(_ray);
    vec3 col = getColor(h);

    if (col.x < 0.0) {
        gl_FragColor = vec4(0.0);
        return;
    }

    gl_FragColor = vec4(col, 1.0);
}
