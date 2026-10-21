import os

# --- flex links - v2 ---
content1 = r"""/*{
    "DESCRIPTION": "Flex links cube with rotating bands.",
    "CREDIT": "FabriceNeyret2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot(ang) mat2(cos(ang+vec4(0,11,33,0)))
#define rot3(P,A,ang) (mix(A*dot(P,A), P, cos(ang)) + sin(ang)*cross(P,A))
#define B(rx,ry,rz) max(a.x-rx, max(a.y-ry, a.z-rz))

void main()
{
    float time = TIME * speed;
    float t = 9.;
    vec3 R = vec3(RENDERSIZE, 1.0);
    vec2 U = gl_FragCoord.xy;
    vec3 D = normalize(vec3(U+U, -12.*R.y) - R);
    vec3 p = vec3(0,0,60);
    vec3 q, a;
    vec3 M = vec3(1,.5,0) * cos(.3*time + vec3(0,11,0));

    vec4 O = vec4(1);
    for (int i = 0; i < 400; i++) {
        if (O.x <= 0. || t <= .01) break;
        q = p;
        q.yz *= rot(-M.y);
        q.xz *= rot(-M.x-1.57);
        q = rot3(q, vec3(sin(time),0,cos(time)), 3.14*smoothstep(6.,1.7,length(q)));
        a = abs(q);
        t = B(1., 1., 1.);
        t = min(t, B(1e5, .3, .1));
        t = min(t, B(.3, .1, 1e5));
        t = min(t, B(.1, 1e5, .3));
        p += .2*t*D;
        O -= .005;
    }
    O *= O*O*2.;
    gl_FragColor = O;
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\flex links - v2'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'flex links - v2.fs'), 'w') as f:
    f.write(content1)
print('Written flex links - v2.fs')


# --- flex links - v3 ---
content2 = r"""/*{
    "DESCRIPTION": "Flex links cube with normal-based coloring.",
    "CREDIT": "FabriceNeyret2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot(ang) mat2(cos(ang+vec4(0,11,33,0)))
#define rot3(P,A,ang) (mix(A*dot(P,A), P, cos(ang)) + sin(ang)*cross(P,A))
#define B(rx,ry,rz) max(a.x-rx, max(a.y-ry, a.z-rz))

float df(vec3 q, inout vec3 a, inout float t) {
    a = abs(q);
    t = B(1., 1., 1.);
    t = min(t, B(1e5, .3, .1));
    t = min(t, B(.3, .1, 1e5));
    return min(t, B(.1, 1e5, .3));
}

void main()
{
    float time = TIME * speed;
    float t = 9.;
    vec3 R = vec3(RENDERSIZE, 1.0);
    vec2 U = gl_FragCoord.xy;
    vec3 D = normalize(vec3(U+U, -12.*R.y) - R);
    vec3 p = vec3(0,0,60);
    vec3 q, a;
    vec3 M = vec3(1,.5,0) * cos(.3*time + vec3(0,11,0));

    p.yz *= rot(-M.y);
    p.xz *= rot(-M.x-1.57);
    D.yz *= rot(-M.y);
    D.xz *= rot(-M.x-1.57);

    vec4 O = vec4(1);
    for (int i = 0; i < 400; i++) {
        if (O.x <= 0. || t <= .01) break;
        q = rot3(p, vec3(sin(time),0,cos(time)), 3.14*smoothstep(6.,1.7,length(p)));
        t = df(q, a, t);
        p += .2*t*D;
        O -= .005;
    }

    O *= O*O*2.;
    vec3 e = vec3(-1,1,0)*1e-3;
    float t2;
    vec3 a2;
    O.rgb *= .5 - .5*normalize(
        e.xxy*df(q+e.xxy, a2, t2) +
        e.xyx*df(q+e.xyx, a2, t2) +
        e.yxx*df(q+e.yxx, a2, t2) +
        e.yyy*df(q+e.yyy, a2, t2)
    );
    gl_FragColor = O;
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\flex links - v3'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'flex links - v3.fs'), 'w') as f:
    f.write(content2)
print('Written flex links - v3.fs')


# --- flex links radial - slice ---
content3 = r"""/*{
    "DESCRIPTION": "Flex links radial sphere with sliced bands.",
    "CREDIT": "FabriceNeyret2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot3(P,A,ang) (mix(A*dot(P,A), P, cos(ang)) + sin(ang)*cross(P,A))

float df(vec3 q) {
    float d1 = length(q) - 1.7;
    float cut = abs(fract(atan(q.z, q.x)/3.14)*3.14 - .1);
    float d2 = 1e3;
    if (cut < .1) {
        d2 = length(q) * length(fract(vec2(atan(q.z,q.x)+.05, atan(q.y,length(q.xz))) / .314) - .5) - .2;
    }
    return min(d1, d2);
}

void main()
{
    float time = TIME * speed;
    float t = 9.;
    vec3 R = vec3(RENDERSIZE, 1.0);
    vec2 U = gl_FragCoord.xy;
    vec3 D = normalize(vec3(U+U, -12.*R.y) - R);
    vec3 p = vec3(0,0,60);
    vec3 q;

    vec4 O = vec4(1);
    for (int i = 0; i < 1000; i++) {
        if (O.x <= 0. || t <= .01 || p.z <= -4.) break;
        q = rot3(p, vec3(sin(time),0,cos(time)), 3.14*smoothstep(.05, .6, 1./length(p)));
        t = df(q);
        p += .03*t*D;
        O -= .001;
    }

    vec3 e = vec3(-1,1,0)*1e-3;
    O.rgb = .5 - .5*normalize(
        e.xxy*df(q+e.xxy) +
        e.xyx*df(q+e.xyx) +
        e.yxx*df(q+e.yxx) +
        e.yyy*df(q+e.yyy)
    );
    gl_FragColor = O;
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\flex links radial - slice'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, 'flex links radial - slice.fs'), 'w') as f:
    f.write(content3)
print('Written flex links radial - slice.fs')


# --- flex links radial - slice2 ---
content4 = r"""/*{
    "DESCRIPTION": "Flex links radial sphere orthogonal slice.",
    "CREDIT": "FabriceNeyret2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot3(P,A,ang) (mix(A*dot(P,A), P, cos(ang)) + sin(ang)*cross(P,A))

float df(vec3 q) {
    float d1 = length(q) - 1.7;
    float cut = abs(atan(q.y, length(q.xz)));
    float d2 = 1e3;
    if (cut < .1) {
        d2 = length(q) * length(fract(vec2(atan(q.z,q.x), atan(q.y,length(q.xz))-.42) / .628 * 2.) - .5) - .2;
    }
    return min(d1, d2);
}

void main()
{
    float time = TIME * speed;
    float t = 9.;
    vec3 R = vec3(RENDERSIZE, 1.0);
    vec2 U = gl_FragCoord.xy;
    vec3 D = normalize(vec3(U+U, -12.*R.y) - R).xzy;
    vec3 p = vec3(0,60,0);
    vec3 q;

    vec4 O = vec4(1);
    for (int i = 0; i < 1000; i++) {
        if (O.x <= 0. || t <= .01 || p.y <= -4.) break;
        q = rot3(p, vec3(sin(time),0,cos(time)), 3.14*smoothstep(.05, .6, 1./length(p)));
        t = df(q);
        p += .03*t*D;
        O -= .001;
    }

    vec3 e = vec3(-1,1,0)*1e-3;
    O.rgb = .5 - .5*normalize(
        e.xxy*df(q+e.xxy) +
        e.xyx*df(q+e.xyx) +
        e.yxx*df(q+e.yxx) +
        e.yyy*df(q+e.yyy)
    );
    gl_FragColor = O;
}
"""

path4 = r'C:\Users\User\Documents\Resolume Wire\Patches\flex links radial - slice2'
os.makedirs(path4, exist_ok=True)
with open(os.path.join(path4, 'flex links radial - slice2.fs'), 'w') as f:
    f.write(content4)
print('Written flex links radial - slice2.fs')


# --- flex links radial - v4 ---
# Uses fwidth - replaced with 0.02
content5 = r"""/*{
    "DESCRIPTION": "Flex links radial sphere with checkered bands.",
    "CREDIT": "FabriceNeyret2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot(ang) mat2(cos(ang+vec4(0,11,33,0)))
#define rot3(P,A,ang) (mix(A*dot(P,A), P, cos(ang)) + sin(ang)*cross(P,A))

float df(vec3 q, out vec2 uv_out) {
    float d1 = length(q) - 1.7;
    float d2 = length(q) * length(fract(vec2(atan(q.z,q.x), atan(q.y,length(q.xz))) / .628) - .5) - .2;
    uv_out = fract(vec2(atan(q.z,q.x), atan(q.y,length(q.xz))) / .628) - .5;
    return min(d1, d2);
}

float df_simple(vec3 q) {
    float d1 = length(q) - 1.7;
    float d2 = length(q) * length(fract(vec2(atan(q.z,q.x), atan(q.y,length(q.xz))) / .628) - .5) - .2;
    return min(d1, d2);
}

void main()
{
    float time = TIME * speed;
    float t = 9.;
    vec3 R = vec3(RENDERSIZE, 1.0);
    vec2 U = gl_FragCoord.xy;
    vec3 D = normalize(vec3(U+U, -12.*R.y) - R);
    vec3 p = vec3(0,0,60);
    vec3 q, a;
    vec3 M = vec3(1,.5,0) * cos(.3*time + vec3(0,11,0));

    p.yz *= rot(-M.y);
    p.xz *= rot(-M.x-1.57);
    D.yz *= rot(-M.y);
    D.xz *= rot(-M.x-1.57);

    vec4 O = vec4(1);
    vec2 uv_band;
    for (int i = 0; i < 400; i++) {
        if (O.x <= 0. || t <= .01) break;
        q = rot3(p, vec3(sin(time),0,cos(time)), 3.14*smoothstep(.05, .6, 1./length(p)));
        t = df(q, uv_band);
        p += .2*t*D;
        O -= .005;
    }

    if (length(q) < 1.8) {
        a.xy = cos(6.28*uv_band);
        t = a.x*a.y;
        O.rgb *= .5 + .5*smoothstep(1.,0., t/0.02);
    } else {
        vec3 e = vec3(-1,1,0)*1e-3;
        O.rgb *= .5 - .5*normalize(
            e.xxy*df_simple(q+e.xxy) +
            e.xyx*df_simple(q+e.xyx) +
            e.yxx*df_simple(q+e.yxx) +
            e.yyy*df_simple(q+e.yyy)
        );
    }
    gl_FragColor = O;
}
"""

path5 = r'C:\Users\User\Documents\Resolume Wire\Patches\flex links radial - v4'
os.makedirs(path5, exist_ok=True)
with open(os.path.join(path5, 'flex links radial - v4.fs'), 'w') as f:
    f.write(content5)
print('Written flex links radial - v4.fs')

print('Batch 10 complete: 5 flex links shaders written')
