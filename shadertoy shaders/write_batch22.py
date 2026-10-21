import os

# --- Crystal Drops ---
# Buffer A has all raymarching (crystal drops with smin)
# Image does post-processing (chromatic aberration, vignette) - merged simplified
# Buffer B does DOF - skipped
# Replaced cubemap texture(iChannel0, dir) with procedural environment
# Replaced iMouse camera orbit with auto-orbit
# Renamed: R -> RS, T -> TT, F -> FC
content1 = r"""/*{
    "DESCRIPTION": "Crystal drops with refraction and procedural environment.",
    "CREDIT": "spolsh / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define HASHSCALE4 vec4(.1031, .1030, .0973, .1099)

float TT = 0.0;

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
        vec3 offset = mix( 0.1*rndPos, 15.0*rndPos, phase);
        float rnd2 = fract(rnd.x + rnd.y);
        float s0 = length(p + offset) - 0.25*mix(0.8 + 0.2*rnd2, 0.2 + 0.8*rnd2, phase);
        s = smin_v(s, s0, 0.4);
    }

    s += 0.002*sin(20.0*p.x + 10.0*TT);

    return s;
}

// Procedural environment replacing cubemap
vec3 env_v(vec3 dir)
{
    // Procedural crystal-like environment
    float y = dir.y * 0.5 + 0.5;
    vec3 sky = mix(vec3(0.02, 0.05, 0.15), vec3(0.1, 0.2, 0.4), y);

    // Bright highlights
    float ex = mix(6.0, 12.0, 0.5*(sin(0.5*TT) + 1.0));
    float t0 = 0.05*pow(1.0 - dot(vec3(0.0, -1.0, 0.0), dir), ex);

    // Angular bands
    float t1 = mix(0.2, 2.5, 1.0 - abs(sin(2.0*3.14*dir.y)));

    // Procedural noise-like pattern
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

mat3 setCamera(in vec3 ro, in vec3 ta, float cr)
{
    vec3 cw = normalize(ta-ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw,cp));
    vec3 cv = normalize(cross(cu,cw));
    return mat3(cu, cv, cw);
}

vec3 tonemapping(vec3 color)
{
    color = max(vec3(0.), color-vec3(0.004));
    color = (color * (6.2*color+.5))/(color*(6.2*color+1.7)+0.06);
    return color;
}

void main()
{
    float time = TIME * speed;
    TT = time;

    vec2 u = gl_FragCoord.xy / RENDERSIZE.xy;
    vec2 v = 2.0*(u - 0.5);
    v.x *= RENDERSIZE.x / RENDERSIZE.y;

    // Auto-orbiting camera
    float camAngle = 0.2 * TT;
    vec3 ro = vec3(
        8.0*cos(camAngle),
        2.0*sin(TT*0.15),
        8.0*sin(camAngle)
    );
    float taAnim = 2.0*(smoothstep(-0.1, 0.1, sin(0.1*TT)) - 0.5);
    vec3 ta = vec3(taAnim, -0.05, 0.0);

    mat3 ca = setCamera(ro, ta, 0.0);
    vec3 rd = ca * normalize(vec3(v, mix(4.5, 5.0, taAnim)));
    vec3 p;
    vec3 c = env_v(rd);

    float t = 0.0, d = 0.0, a = 0.0;
    for(int i=0; i<50; ++i) {
        t += (d = map_v(p = ro + rd*t));
        if (d < 0.01) break;
    }

    float depth = length(p-ro);

    if (t < 25.0) {
        vec3 n = calcNormal(p);
        vec3 rl = reflect(rd, n);
        vec3 rr = refract(rd, n, .19);

        for(int i=0; i<25; ++i) {
            d = map_v(p = ro + rd*t);
            a += step(d, 0.008) * 0.005;
            t += 0.02;
        }

        a = exp(-a*25.0);
        c = env_v(mix(rr, rl, a));
        c *= mix(vec3(1.4, 1.0, 0.9), vec3(1.0), clamp(0.2*length(p), 0.0, 1.0));
        c *= mix(vec3(1.5), vec3(.3), clamp(pow(0.1*depth, 2.0), 0.0, 1.0));
    }

    c = tonemapping(c);

    // Simplified vignette from Image pass
    vec2 vv = 2.0*(u - 0.5);
    vv.y *= 2.39 * RENDERSIZE.y / RENDERSIZE.x;
    vv = clamp((vv*0.5)+0.5, 0., 1.);
    c *= 0.25 + 0.75*pow(16.0*vv.x*vv.y*(1.0-vv.x)*(1.0-vv.y), 0.25);

    // Gamma
    c = pow(c, vec3(0.4545));

    gl_FragColor = vec4(c, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Crystal Drops'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Crystal Drops.fs'), 'w') as f:
    f.write(content1)
print('Written Crystal Drops.fs')
print('Batch 22 complete: 1 shader written')
