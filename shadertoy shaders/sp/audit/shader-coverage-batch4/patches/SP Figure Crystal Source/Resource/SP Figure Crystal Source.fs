/*{
  "DESCRIPTION": "Heart bounded Figure source. Shared Figure Transform owns size and placement. Crystal drops with refraction and procedural environment.",
  "CREDIT": "spolsh / Shadertoy",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "speed",
      "LABEL": "Speed",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 3.0
    },
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
      "NAME": "ior",
      "LABEL": "Refraction",
      "TYPE": "float",
      "DEFAULT": 0.19,
      "MIN": 0.05,
      "MAX": 0.5
    }
  ]
}*/

#define HASHSCALE4 vec4(.1031, .1030, .0973, .1099)

float TT = 0.0;

mat3 quatToMat(vec4 q) {
    float q2 = dot(q,q);
    q = q2 > 1e-10 ? q * inversesqrt(q2) : vec4(0.0,0.0,0.0,1.0);
    float xx = q.x*q.x, yy = q.y*q.y, zz = q.z*q.z;
    float xy = q.x*q.y, xz = q.x*q.z, yz = q.y*q.z;
    float wx = q.w*q.x, wy = q.w*q.y, wz = q.w*q.z;
    return mat3(
        1.0 - 2.0*(yy+zz), 2.0*(xy+wz),     2.0*(xz-wy),
        2.0*(xy-wz),        1.0 - 2.0*(xx+zz), 2.0*(yz+wx),
        2.0*(xz+wy),        2.0*(yz-wx),     1.0 - 2.0*(xx+yy)
    );
}

vec4 hash41(float p)
{
    vec4 p4 = fract(vec4(p) * HASHSCALE4);
    p4 += dot(p4, p4.wzxy+19.19);
    return fract((p4.xxyz+p4.yzzw)*p4.zywx);
}

float smin_v( float a, float b, float k )
{
    float h = clamp( 0.5+0.5*(b-a)/k, 0.0, 1.0 );
    return mix( b, a, h ) - k*h*(1.0-h);
}

float map_v(vec3 p)
{
    float s = length(p - vec3(0.0, .01*sin(8.0*TT), 0.0)) - 0.5;
    s += 0.005*sin(45.0*p.x+10.0*TT);

    for (int i=0; i<12; ++i) {
        vec4 rnd = hash41(100.0+float(i));
        vec3 rndPos = 2.0*(normalize(rnd.xyz) - vec3(0.5));
        rndPos.y *= 0.2;
        float timeOffset = rnd.w;
        float phase = fract(timeOffset - 0.25*TT);
        // Keep satellite centers in a radius-1.15 neighborhood.
        vec3 direction = normalize(rndPos + vec3(0.00001));
        vec3 offset = direction * mix(0.1, 1.15, phase);
        float rnd2 = fract(rnd.x + rnd.y);
        float s0 = length(p + offset) - 0.25*mix(0.8 + 0.2*rnd2, 0.2 + 0.8*rnd2, phase);
        // Fade each droplet before its wrap, instead of teleporting a visible satellite.
        float envelope = smoothstep(0.0,0.12,phase) * (1.0-smoothstep(0.82,1.0,phase));
        s0 += (1.0-envelope)*0.3;
        s = smin_v(s, s0, 0.16);
    }

    s += 0.002*sin(20.0*p.x + 10.0*TT);

    return s;
}

vec3 env_v(vec3 dir)
{
    float y = dir.y * 0.5 + 0.5;
    vec3 sky = mix(vec3(0.02, 0.05, 0.15), vec3(0.1, 0.2, 0.4), y);
    float ex = mix(6.0, 12.0, 0.5*(sin(0.5*TT) + 1.0));
    float t0 = 0.05*pow(1.0 - dot(vec3(0.0, -1.0, 0.0), dir), ex);
    float t1 = mix(0.2, 2.5, 1.0 - abs(sin(2.0*3.14*dir.y)));
    float n = fract(sin(dot(dir.xz, vec2(12.9898, 78.233))) * 43758.5453);
    vec3 cubemap = vec3(0.3 + 0.7*n, 0.4 + 0.6*n, 0.5 + 0.5*n);
    vec3 c = cubemap * t0 * t1;
    return c * vec3(0.35, 1.2, 2.5);
}

vec3 calcNormal(vec3 p)
{
    vec2 e = vec2(1.0,-1.0)*0.5773*0.0005;
    return normalize(
        e.xyy*map_v(p + e.xyy) +
        e.yxy*map_v(p + e.yxy) +
        e.yyx*map_v(p + e.yyx) +
        e.xxx*map_v(p + e.xxx) );
}

vec3 tonemapping(vec3 color)
{
    color = max(vec3(0.), color-vec3(0.004));
    color = (color * (6.2*color+.5))/(color*(6.2*color+1.7)+0.06);
    return color;
}

void main()
{
    TT = TIME * speed;

    vec2 uv = (2.0*gl_FragCoord.xy - RENDERSIZE.xy) / min(RENDERSIZE.x, RENDERSIZE.y);

    mat3 cam = quatToMat(vec4(quatX, quatY, quatZ, quatW));

    vec3 ro = cam * vec3(0.0, 0.0, 4.8);
    vec3 rd = cam * normalize(vec3(uv, -1.8));
    vec3 p;

    float t = 0.0, d = 0.0, a = 0.0;
    for(int i=0; i<50; ++i) {
        t += (d = map_v(p = ro + rd*t));
        if (d < 0.01) break;
    }

    if (t >= 25.0 || d >= 0.01) {
        gl_FragColor = vec4(0.0);
        return;
    }

    vec3 n = calcNormal(p);
    vec3 rl = reflect(rd, n);
    vec3 rr = refract(rd, n, ior);

    for(int i=0; i<25; ++i) {
        d = map_v(p = ro + rd*t);
        a += step(d, 0.008) * 0.005;
        t += 0.02;
    }

    a = exp(-a*25.0);
    vec3 c = env_v(mix(rr, rl, a));
    c *= mix(vec3(1.4, 1.0, 0.9), vec3(1.0), clamp(0.2*length(p), 0.0, 1.0));

    c = tonemapping(c);
    c = pow(c, vec3(0.4545));

    gl_FragColor = vec4(c, 1.0);
}
