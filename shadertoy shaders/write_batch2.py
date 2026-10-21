import os

# 1. Quaternion Kinematics
content1 = """/*{
    "DESCRIPTION": "Quaternion bone chain kinematics demo.",
    "CREDIT": "spalmer / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define quat vec4

const vec4 qidentity = vec4(0,0,0,1);

vec4 qfromto(vec3 vsrc, vec3 vdst) {
    vec3 vhalf = vsrc + vdst;
    vhalf *= length(vdst) / length(vhalf);
    return vec4(cross(vsrc, vhalf), dot(vsrc, vhalf));
}

vec4 qaxisangle(vec3 axis, float rad) {
    rad *= .5;
    return vec4(sin(rad) * axis, cos(rad));
}

vec4 qrev(vec4 q) {
    q.w = -q.w;
    return q;
}

vec4 qmul(vec4 a, vec4 b) {
    vec3 va = a.xyz, vb = b.xyz;
    return vec4(b) * a.w - vec4(cross(vb, va) - va * b.w, dot(va, vb));
}

vec4 qrenormalize(vec4 q) {
    float l2 = dot(q, q);
    return l2 == 1. ? q : .5 * (3. - l2) * q;
}

vec3 qrot(vec4 q, vec3 r) {
    vec3 axis = q.xyz;
    float w = q.w;
    return 2.*((cross(axis,r) + r * w) * w + axis * dot(axis,r)) - r;
}

vec3 QrbitCamera(vec2 a, vec3 d) {
    a.y = clamp(a.y, -.5, .5);
    const float pi = acos(-1.);
    a *= pi;
    vec4 q = qidentity;
    q = qmul(q, qaxisangle(vec3(0,1,0), 2.*a.x));
    q = qmul(q, qaxisangle(vec3(-1,0,0), a.y));
    q = qrenormalize(q);
    return qrot(q, d);
}

float dbox(vec3 p, vec3 e) {
    p = abs(p); p -= e;
    return all(lessThan(p, vec3(0)))
     ? max(max(p.x, p.y), p.z)
     : length(max(p, vec3(0)));
}

vec2 scene(vec3 e, float t) {
    e.xz = abs(e.xz);
    e.zx -= 6.;
    float dp = e.y + .1*(cos(9.*e.x) + cos(9.*e.z));
    vec2 r = vec2(dp, 1);
    vec3 p0 = vec3(0), p1;
    float a = .2 * sin(t * 1.7);
    vec4 q = qidentity, R = vec4(normalize(vec3(.5,1,-.2)) * sin(a), cos(a));
    for (int i = 8; i-- > 0; ) {
        p1 = p0;
        p0 += qrot(q, vec3(0,1,0));
        float d = dbox(qrot(qrev(q), e - .5*(p0 + p1)), vec3(.1,.4,.1)) - .1;
        if (d < r.x) r = vec2(d, float(i)+2.);
        q = qmul(q, R);
        q = qrenormalize(q);
    }
    return r;
}

void main() {
    float t = TIME * speed;
    vec4 o = vec4(0);
    vec3 e = RENDERSIZE.xyy;
    vec3 d = normalize(vec3((gl_FragCoord.xy - .5 * e.xy) / e.y, 1));

    vec2 cam = vec2(.1*sin(.2*t), 0.0);
    d = QrbitCamera(cam, d);
    d = normalize(d);
    e -= e; e.y += 4.;
    float r = 24., tt = 0.;
    vec2 h;
    for (int i = 40; i-- > 0; ) {
        h = scene(e, t);
        h.x *= .8;
        tt += h.x; e += h.x * d;
        if (abs(h.x) < .001 * tt || tt > r || e.y > 9.) break;
    }
    o = exp(-.06 * min(r, tt)) * vec4(1);
    float g = (scene(e + vec3(.1), t).x - scene(e, t).x) / length(vec3(.1));
    o.rgb *= clamp(g * .25 + .5, 0., 1.);
    o.rgb *= cos(vec3(0,2,4)-1.+11.7*h.y) * .5 + .5;
    if (e.y >= 9. || tt > r) o *= 0.;
    o = sqrt(o);
    gl_FragColor = vec4(o.rgb, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quaternion Kinematics'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Quaternion Kinematics.fs'), 'w') as f:
    f.write(content1)
print('Written Quaternion Kinematics.fs')

# 2. quaternion slerp
content2 = """/*{
    "DESCRIPTION": "Quaternion SLERP interpolation with raymarched scene.",
    "CREDIT": "DeltaT / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define MAX_DIST 16.
#define PI 3.14159
#define TAU 6.28319

vec3 rotApply(vec3 v, vec4 R) {
    vec3 i = cross(R.xyz, v);
    return v + 2.*(R.w * i + cross(R.xyz, i));
}

vec4 rotReverse(vec4 R) {
    return vec4(-R.xyz, R.w);
}

vec4 rotStack(vec4 Q, vec4 R) {
    vec3 bQ = Q.xyz;
    vec3 bR = R.xyz;
    return vec4(Q.w*bR+R.w*bQ + cross(bQ, bR), Q.w*R.w - dot(bQ, bR));
}

vec4 rotSlerp(vec4 Q, vec4 R, float t) {
    vec4 d = rotStack(R, rotReverse(Q));
    float halfangle = mod(atan(length(d.xyz), d.w)+PI*0.5, PI)-PI*0.5;
    vec3 plane = d.xyz == vec3(0) ? vec3(1, 0, 0) : normalize(d.xyz);
    return rotStack(vec4(plane*sin(halfangle*t), cos(halfangle*t)), Q);
}

vec4 hash14(float p) {
    vec4 p4 = fract(vec4(p) * vec4(.1031, .1030, .0973, .1099));
    p4 += dot(p4, p4.wzxy+33.33);
    return 2.*fract((p4.xxyz+p4.yzzw)*p4.zywx)-1.;
}

float distBox(vec3 p, float r) {
    vec3 p1 = abs(p);
    float d = length(max(p1-r, 0.));
    float dsigned = min(max(max(p1.x-r, p1.y-r), p1.z-r), 0.);
    return d + dsigned;
}

float distCylinder(vec3 p, vec3 a, vec3 b, float r) {
    vec3 ba = b - a;
    vec3 pa = p - a;
    float baba = dot(ba,ba);
    float paba = dot(pa,ba);
    float x = length(pa*baba-ba*paba) - r*baba;
    float y = abs(paba-baba*0.5)-baba*0.5;
    float x2 = x*x;
    float y2 = y*y*baba;
    float dd = (max(x,y)<0.0)?-min(x2,y2):(((x>0.0)?x2:0.0)+((y>0.0)?y2:0.0));
    return sign(dd)*sqrt(abs(dd))/baba;
}

float distSphere(vec3 p, float r) {
    return length(p) - r;
}

float t_anim;

vec4 distScene(vec3 p) {
    float time = t_anim * 0.75;
    vec4 R1 = normalize(hash14(floor(time)));
    vec4 R2 = normalize(hash14(floor(time)+1.));
    vec4 R = rotSlerp(R1, R2, smoothstep(0., 1., fract(time)));

    float t = smoothstep(0., 1., fract(time))*3.;
    vec3 pm = rotApply(vec3(mod(p.x+t+1.5, 3.)-1.5, p.yz), normalize(hash14(floor(time)+floor((p.x+t)/3.+0.5))));
    p = rotApply(p, R);

    float phi = atan(p.y, p.x);
    float theta = acos(clamp(dot(normalize(p), vec3(0, 0, 1)), -1.0, 1.0));
    vec2 a = vec2(mod(theta, TAU/6.), mod(phi, TAU/6.));
    vec4 sphere = vec4((max(a.x, a.y) < TAU/12. || min(a.x, a.y) > TAU/12.) ? vec3(1) : vec3(0.5), distSphere(p, 0.4));

    vec3 O = vec3(0);
    vec4 X = vec4(vec3(1, 0, 0), min(distCylinder(p, O, vec3(1, 0, 0), .03), distCylinder(pm, O, vec3(1, 0, 0), .03)));
    vec4 Y = vec4(vec3(0, 1, 0), min(distCylinder(p, O, vec3(0, 1, 0), .03), distCylinder(pm, O, vec3(0, 1, 0), .03)));
    vec4 Z = vec4(vec3(0, 0, 1), min(distCylinder(p, O, vec3(0, 0, 1), .03), distCylinder(pm, O, vec3(0, 0, 1), .03)));
    float d = min(min(min(X.w, Y.w), Z.w), sphere.w);
    return d == X.w ? X : (d == Y.w ? Y : (d == Z.w ? Z : sphere));
}

vec4 rayMarch(vec3 pos, vec3 rd) {
    vec4 d = vec4(0);
    for (int i = 0; i < 100; i++) {
        vec3 p = pos + rd*d.w;
        vec4 ds = distScene(p);
        d.xyz = ds.xyz;
        if (ds.w <= 0.001) break;
        d.w += ds.w;
        if (d.w > MAX_DIST) break;
    }
    return d;
}

vec3 getNormal(vec3 p) {
    vec2 e = vec2(.001, 0);
    float d = distScene(p).w;
    vec3 n = d-vec3(distScene(p-e.xyy).w, distScene(p-e.yxy).w, distScene(p-e.yyx).w);
    return normalize(n);
}

vec3 render(vec3 campos, vec4 rot, vec2 coord) {
    vec3 raydir = rotApply(normalize(vec3(coord.x, 1.5, coord.y)), rot);
    vec4 d = rayMarch(campos, raydir);
    float gradient = (raydir.z*5.+1.)*0.5;
    vec3 skyColour = mix(vec3(0., 0.6, 0.8), vec3(0, 0.7, 0.9), gradient);
    if (d.w >= MAX_DIST) return skyColour;
    vec3 p = campos + raydir * d.w;
    vec3 n = getNormal(p);
    vec3 light = vec3(3, 0, 3);
    float diff = dot(n, normalize(light-p));
    float specular = max(0., dot(normalize(-raydir), -normalize(reflect(light-p, n))));
    return mix(d.xyz*mix(vec3(0.3), vec3(1), diff*0.5+0.5), vec3(1), pow(specular, 10.));
}

void main() {
    t_anim = TIME * speed;
    vec2 uv = (gl_FragCoord.xy * 2. - RENDERSIZE.xy) / RENDERSIZE.y;

    float camAngle = t_anim * 0.3;
    vec4 dir = rotStack(vec4(0, 0, sin(-camAngle), cos(-camAngle)), vec4(sin(0.3), 0, 0, cos(0.3)));
    vec3 campos = rotApply(vec3(0, -3, 0), dir);

    vec3 col = render(campos, dir, uv);
    gl_FragColor = vec4(col, 1);
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\quaternion slerp'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'quaternion slerp.fs'), 'w') as f:
    f.write(content2)
print('Written quaternion slerp.fs')

# 3. Quaternion Twister
content3 = """/*{
    "DESCRIPTION": "Twisting space with quaternions and Dirac belt trick.",
    "CREDIT": "mla / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

float PI = 3.1415927;
float lradius = 0.025, pradius = 0.2;
float eyedist = 2.0;
vec3 light = vec3(0,1,2);
int maxsteps = 200;
float precis = 1e-4;
float lfactor = 0.2;

vec3 qrot(vec3 p, vec4 q) {
    return p + 2.0*cross(q.xyz, cross(q.xyz, p) + q.w*p);
}

float segment(vec3 p, vec3 q, vec3 r) {
    p -= q; r -= q;
    float h = clamp(dot(p,r)/dot(r,r), 0.0, 1.0);
    return length(p - h*r);
}

vec3 A_v, B_v, C_v, a_v, b_v, c_v;

void init_ico(int Q, int R) {
    float q = PI/float(Q);
    float r = PI/float(R);
    A_v = vec3(1,0,0);
    B_v = vec3(0,1,0);
    float x = -cos(r);
    float y = -cos(q);
    float z = sqrt(1.0-x*x-y*y);
    C_v = vec3(x,y,z);
    a_v = normalize(cross(B_v,C_v));
    b_v = normalize(cross(C_v,A_v));
    c_v = normalize(cross(A_v,B_v));
}

vec3 fold(vec3 pos) {
    for (int i = 0; i < 8; i++) {
        pos.xy = abs(pos.xy);
        float k = dot(pos, C_v);
        if (k > 0.0) break;
        pos -= 2.0*k*C_v;
    }
    return pos;
}

float t_time;

float de(vec3 p, out int type) {
    float t = 0.2 * t_time;
    vec4 qt = vec4(sin(PI*t), 0, 0, cos(PI*t));
    float s = max(0.0, 1.0-(length(p)-pradius)/(1.0-pradius));
    s = 0.5-0.5*cos(PI*s);
    qt = mix(vec4(0,0,0,1), qt, s);
    qt.y = sqrt(max(0.0,(1.0-dot(qt,qt))));
    if (mod(t,4.0) > 2.0) qt.y = -qt.y;
    p = qrot(p, qt);
    vec3 p0 = p;
    p = fold(p);

    float d = 1e8, d0;
    type = 0;
    d0 = segment(p, vec3(0), a_v) - lradius;
    if (d0 < d) { type = 1; d = d0; }
    d0 = segment(p, vec3(0), b_v) - lradius;
    if (d0 < d) { type = 2; d = d0; }
    d0 = segment(p, vec3(0), c_v) - lradius;
    if (d0 < d) { type = 3; d = d0; }
    d0 = length(p) - pradius;
    if (d0 < d) { type = 4; d = d0; }
    d *= lfactor;
    d = max(d, length(p0)-1.1);
    return d;
}

float de_simple(vec3 p) {
    int type;
    return de(p, type);
}

float maxdist_v = 10.0;

float march(vec3 q, vec3 r) {
    float t = 0.0;
    float R = 1.0 + lradius;
    float B = dot(q,r), C = dot(q,q)-R*R;
    float D = B*B - C;
    if (D < 0.0) return -1.0;
    D = sqrt(D);
    float t0 = -B-D;
    maxdist_v = -B+D;
    if (t0 > 0.0) t = t0;

    for (int i = 0; i < 200; i++) {
        vec3 p = q+t*r;
        float d = de_simple(p);
        if (abs(d) < precis) return t;
        t += d;
        if (t > maxdist_v) break;
    }
    return -1.0;
}

vec3 getnormal(vec3 p) {
    float eps = 0.001;
    vec2 e = vec2(eps,0);
    return normalize(vec3(de_simple(p + e.xyy) - de_simple(p - e.xyy),
                          de_simple(p + e.yxy) - de_simple(p - e.yxy),
                          de_simple(p + e.yyx) - de_simple(p - e.yyx)));
}

vec2 rotate2(vec2 p, float t) {
    return cos(t)*p + sin(t)*vec2(-p.y, p.x);
}

vec3 transformframe(vec3 p) {
    float camAngle = t_time * 0.15;
    p.zx = rotate2(p.zx, -camAngle);
    p.zx = rotate2(p.zx, 0.25*PI);
    p.xy = rotate2(p.xy, 0.25*PI);
    return p;
}

vec3 getbasecolor(int type) {
    if (type == 1) return vec3(1,1,0);
    if (type == 2) return vec3(0,1,0);
    if (type == 3) return vec3(0,0,1);
    if (type == 4) return vec3(1,0,0);
    return vec3(0.75,1,0.75);
}

vec3 getbackground(vec3 r) {
    return mix(vec3(1), pow(r, vec3(2)), 0.5);
}

vec3 raycolor(vec3 q, vec3 r) {
    float t = march(q, r);
    if (t < 0.0) return getbackground(r);
    vec3 p = q+t*r;
    vec3 normal = getnormal(p);
    int type;
    de(p, type);
    vec3 lightdir = normalize(light-p);
    vec3 color = mix(vec3(1), getbasecolor(type), 0.6);
    float ambient = 0.3;
    float diffuse = 0.7*clamp(dot(normal, lightdir), 0.0, 1.0);
    color *= ambient + diffuse;
    return color;
}

void main() {
    t_time = TIME * speed;
    init_ico(3, 5);
    maxdist_v = eyedist + 1.0;
    vec3 eye = vec3(0, 0, eyedist);
    eye = transformframe(eye);
    light = transformframe(light);

    vec2 z = (2.0*gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
    vec3 ray = vec3(z, -2);
    ray = transformframe(ray);
    ray = normalize(ray);
    vec3 col = raycolor(eye, ray);
    col = pow(col, vec3(0.4545));
    gl_FragColor = vec4(col, 1);
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quaternion Twister'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, 'Quaternion Twister.fs'), 'w') as f:
    f.write(content3)
print('Written Quaternion Twister.fs')
