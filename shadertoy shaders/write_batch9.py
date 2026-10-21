import os

# --- Deep Quantum Time State (sci-fi) ---
# Single pass, musicstream declared but never sampled. Clean conversion.
content1 = r"""/*{
    "DESCRIPTION": "Quantum cryptography sci-fi visualization with entanglement and collapse.",
    "CREDIT": "rmmcal / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

mat2 rotate_v(float a){
    return mat2(cos(a), sin(a), -sin(a), cos(a));
}

float qtime;
struct QuantumState{
    vec3 momentum;
    vec3 position;
};

QuantumState normalizeQ(QuantumState q){
    q.position = normalize(q.position);
    q.momentum = normalize(q.momentum);
    return q;
}

vec3 getQuantumSpin(QuantumState q){
    vec3 ps = q.position;
    float t = qtime;
    ps.zy = rotate_v(q.momentum.x*t) * ps.zy;
    ps.zx = rotate_v(q.momentum.y*t) * ps.zx;
    ps.xy = rotate_v(q.momentum.z*t) * ps.xy;
    return normalize(ps);
}

void getQuantumEntangle(inout QuantumState q1, inout QuantumState q2){
    QuantumState q;
    q.momentum.x = ( dot(q1.momentum.zy, q2.momentum.zy) );
    q.momentum.y = ( dot(q1.momentum.zx, q2.momentum.zx) );
    q.momentum.z = ( dot(q1.momentum.xy, q2.momentum.xy) );
    q1.momentum = -q.momentum;
    q2.momentum =  q.momentum;
}

void getQuantumCollapse(inout QuantumState q1, vec3 angle){
    QuantumState q;
    q.momentum.x = ( dot(q1.momentum.zy, angle.zy) );
    q.momentum.y = ( dot(q1.momentum.zx, angle.zx) );
    q.momentum.z = ( dot(q1.momentum.xy, angle.xy) );
    q1.momentum = q.momentum;
}

QuantumState getQuantum(vec3 p){
    QuantumState q;
    q.position = vec3(0.,1.,0.);
    q.momentum = vec3(mod(cos(p.x+p.y+p.z), 1.),
                       mod(cos(p.x+p.y), 1.),
                       mod(cos(p.x), 1.));
    return normalizeQ(q);
}

float sdLine( in vec2 p, in vec2 a, in vec2 b )
{
    vec2 pa = p-a;
    vec2 ba = b-a;
    float sd = dot(pa,ba) / dot(ba,ba);
    float h = clamp(sd, 0.0, 1.0);
    return length( pa - ba*h );
}

void drawState(inout vec4 c, vec2 p, QuantumState q){
    p *= 5.;
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p*vec2(1.,2.)))));
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p*vec2(2.,1.)))));
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine(p, vec2(0.,0.), vec2(0.,1.)))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine(p, vec2(0.,0.), vec2(1.,0.)))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine(p, vec2(0.,0.), vec2(-.45)))));
    vec3 spin = getQuantumSpin(q);
    c = mix(c,vec4(0.,0.,1.,1.), smoothstep(-0.01,.0, .01-sdLine(p, vec2(0.,0.), spin.xy)));
    c = mix(c,vec4(0.,1.,1.,1.), smoothstep(-0.01,.0, -abs(.02-sdLine(p, vec2(0.,0.), spin.xy))));
}

void drawStateColorUp(inout vec4 c, vec2 p, vec4 cor, QuantumState q){
    p *= 5.;
    float d = -1.;
    d = max(d, min(p.y, 1.-length(p)));
    d = max(d, 1.-length(p*vec2(1.,2.)));
    c = mix(c,cor, smoothstep(-0.05,.0, d));
}

void drawStateColorAll(inout vec4 c, vec2 p, vec4 cor, QuantumState q){
    p *= 5.;
    c = mix(c,cor, smoothstep(-0.05,.0, -abs(1.-length(p*vec2(1.,2.)))));
    c = mix(c,cor, smoothstep(-0.05,.0, -abs(1.-length(p*vec2(2.,1.)))));
    c = mix(c,cor, smoothstep(-0.05,.0, (1.-length(p))));
}

void main()
{
    float time = TIME * speed;
    vec2 uv = gl_FragCoord.xy/RENDERSIZE.xy;
    vec2 a = vec2(RENDERSIZE.x/RENDERSIZE.y, 1.);
    vec2 p = (uv-.5)*a;

    vec4 c = vec4(1.);

    qtime = fract((time*15.)/30.)*30.;

    QuantumState q1 = getQuantum(vec3(1.,2.,3.));
    QuantumState q2 = getQuantum(vec3(5.,2.,1.));

    if (time > 10.)
    {
        c = mix(c,vec4(1.,.95,.9,1.), smoothstep(-0.01,.0, (.3-sdLine(p, vec2(-.5,-1.), vec2(-.5,1.)))));
        c = mix(c,vec4(1.,.95,.9,1.), smoothstep(-0.01,.0, (.3-sdLine(p, vec2( .5,-1.), vec2( .5,1.)))));
    }

    if (time > 5.)
    {
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine(p, vec2(-1.,0.), vec2(1.,0.)))));
        vec4 cor1 = vec4(0.8,1.,1.,0.);
        drawStateColorAll(c, p-vec2(-0.5,0.),cor1, q1);
        drawStateColorAll(c, p-vec2( 0.5,0.),cor1, q2);
        getQuantumEntangle(q1, q2);
    }

    if (time > 10.)
    {
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine(p, vec2(-.5,-1.), vec2(-.5,1.)))));
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine(p, vec2( .5,-1.), vec2( .5,1.)))));
        getQuantumCollapse(q1, vec3(0.,1.,0.));
        getQuantumCollapse(q2, vec3(0.,1.,0.));
        vec4 cor1 = vec4(0.5,1.,.9,0.);
        drawStateColorUp(c, p-vec2(-0.5,0.),cor1, q1);
        drawStateColorUp(c, p-vec2( 0.5,0.),cor1, q2);
    }

    drawState(c, p-vec2(-0.5,0.), q1);
    drawState(c, p-vec2(+0.5,0.), q2);
    gl_FragColor = vec4(c.rgb, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Deep Quantum Time State'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Deep Quantum Time State.fs'), 'w') as f:
    f.write(content1)
print('Written Deep Quantum Time State.fs')


# --- Klein Bottle (3D) ---
# Single pass, cubemap replaced with procedural environment color
content2 = r"""/*{
    "DESCRIPTION": "Raymarched Klein Bottle with reflections and refractions.",
    "CREDIT": "lara / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define S 256
#define P 0.001
#define R 2.
#define D 15.
#define M 0.

#define PI 3.1415926

struct Ray { vec3 o; vec3 d; };
struct Camera { vec3 p; vec3 t; };
struct Hit { vec3 p; float t; float d; };

Ray _ray;
Camera _cam;

float _d, _dsky;
bool _ignoreBottle;

mat2 rot(float a)
{
    float c=cos(a),s=sin(a);
    return mat2(c,-s,s,c);
}

// Procedural cubemap replacement
vec3 cubeColor(vec3 n) {
    vec3 sky = mix(vec3(0.05, 0.08, 0.15), vec3(0.3, 0.5, 0.8), n.y * 0.5 + 0.5);
    sky += pow(max(dot(n, normalize(vec3(1,1,-1))), 0.0), 32.0) * vec3(1.0, 0.95, 0.8) * 0.5;
    sky += pow(max(dot(n, normalize(vec3(-1,0.5,0.5))), 0.0), 16.0) * vec3(0.3, 0.4, 0.6) * 0.3;
    float grid = max(
        smoothstep(0.02, 0.0, abs(fract(n.x * 2.0) - 0.5)),
        smoothstep(0.02, 0.0, abs(fract(n.z * 2.0) - 0.5))
    );
    sky += grid * 0.05;
    return sky;
}

float scene(vec3 p)
{
    _dsky = abs(length(p)-D+8.)-P;

    if (_ignoreBottle) { return _d = _dsky; }

    float t = 0.02;
    float d = 1e10;

    p.y += .5;
    p.xy *= rot(PI/2.);

    vec3  q = p + vec3(1.-cos((1.-p.y)/3.*PI),0,0);
    float y = pow(sin((1.-p.y)/3.*PI/2.),2.);

    float tube_hollow = max(max(abs(length(q.xz)-0.5+0.25*y)-t,q.y-1.0),-q.y-2.0);
    float tube_solid  = max(max(length(q.xz)-0.5+0.25*y,q.y-1.0),-q.y-2.0);

    q = p - vec3(0,1,0);
    d = min(d,max(abs(length(vec2(length(q.xz)-1.0,q.y))-0.5)-t,-q.y));

    q = p;
    d = min(d,max(max(max(abs(length(q.xz)-1.5+1.25*y),q.y-1.0),-q.y-2.0)-t,-tube_solid));

    d = min(d,tube_hollow);

    q = p + vec3(1,2,0);
    d = min(d,max(abs(length(vec2(length(q.xy)-1.0,q.z))-0.25)-t,q.y));

    d = min(d,_dsky);

    return _d = d;
}

vec3 getNormal(vec3 p)
{
    vec2 e = vec2(P,0);
    return normalize(vec3(
        scene(p+e.xyy)-scene(p-e.xyy),
        scene(p+e.yxy)-scene(p-e.yxy),
        scene(p+e.yyx)-scene(p-e.yyx)
    ));
}

Hit march(Ray r)
{
    float t = 0.0;
    float d;
    for(int i = 0; i < S; i++)
    {
        d = scene(r.o+r.d*t);
        t += d/R;
        if (d < P || t > D) { break; }
    }
    return Hit(r.o+r.d*t, t, d);
}

Ray lookAt(Camera cam, vec2 uv)
{
    vec3 d = normalize(cam.t-cam.p);
    vec3 r = normalize(cross(d, vec3(0,1,0)));
    vec3 u = cross(r, d);
    return Ray(cam.p, normalize(r*uv.x + u*uv.y + d));
}

vec3 getColor(Hit h)
{
    if (_d > P) { return vec3(0); }
    if (_d == _dsky) { return cubeColor(getNormal(h.p)); }

    vec4 col = vec4(0);
    vec3 light = _cam.p;

    Hit _h = h;

    for(int i = 0; i < 10; i++)
    {
        if (i == 2) { h = _h; }

        vec3 n = getNormal(h.p);

        float diff = max(dot(normalize(light-h.p),n),0.0);
        float spec = pow(max(dot(reflect(normalize(h.p-light),n),normalize(_cam.p-h.p)),0.0),100.);

        vec4 c = vec4(vec3(.8,.9,1)*diff+spec,.15);

        if (i < 2 && _d == _dsky) { c = vec4(cubeColor(n), 1.0); }

        float r = 1.12;
        float f = r + (1. - r)*(1. - dot(normalize(h.p-_cam.p),n))*5.;
        c.rgb = mix(c.rgb,vec3(0),f);

        col.rgb = col.rgb*(1.-c.a) + c.rgb*c.a;
        col.w = clamp(col.w+c.a,0.,1.);

        if (i > 1)
        { _ray.d = normalize(refract(h.p-_cam.p,n,1.5)); }
        else
        { _ray.d = normalize(reflect(h.p-_cam.p,n)); }

        _ray.o = h.p + _ray.d*.1;
        h = march(_ray);
        if (h.d > P) { break; }
    }

    _ray.d = normalize(_h.p-_cam.p);
    _ray.o = _h.p;

    _ignoreBottle = true;
    h = march(_ray);
    _ignoreBottle = false;

    return mix(cubeColor(getNormal(h.p)),col.rgb,col.a);
}

void main()
{
    float time = TIME * speed;
    vec2 uv = (2.0*gl_FragCoord.xy-RENDERSIZE.xy)/RENDERSIZE.yy;

    // Auto-orbit camera
    vec2 uvm = vec2(-time*.2, 0);

    _ignoreBottle = false;
    _cam = Camera(vec3(0,0,4), vec3(0,0,0));
    _cam.p.yz *= rot(-uvm.y*PI);
    _cam.p.xz *= rot(uvm.x*PI);

    _ray = lookAt(_cam,uv);

    vec3 col = getColor(march(_ray));

    gl_FragColor = vec4(col, 1.0);
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\Klein Bottle (3D)'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'Klein Bottle (3D).fs'), 'w') as f:
    f.write(content2)
print('Written Klein Bottle (3D).fs')


# --- Quantum Socket ---
# Single pass, no texture inputs. Remove UNITY_MODE, fix fwidth, ZERO, AA
content3 = r"""/*{
    "DESCRIPTION": "USB socket wheel raymarching scene.",
    "CREDIT": "XMunkki / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

vec2 mul2x2(mat2 m, vec2 p) { return m * p; }
vec3 mul3x3(mat3 m, vec3 p) { return m * p; }
float _atan(float x, float y) { return atan(x, y); }

#define PI (3.1415926535897932384626433832795)
#define PI2 (2.0 * PI)

float sdPlane( vec3 p ) { return p.y; }

float sdSphere( vec3 p, float s ) { return length(p)-s; }

float sdBox( vec3 p, vec3 b )
{
    vec3 d = abs(p) - b;
    return min(max(d.x,max(d.y,d.z)),0.0) + length(max(d,0.0));
}

float sdRoundBox( in vec3 p, in vec3 b, in float r )
{
    vec3 q = abs(p) - b;
    return min(max(q.x,max(q.y,q.z)),0.0) + length(max(q,0.0)) - r;
}

float sdTorus( vec3 p, vec2 t )
{
    return length( vec2(length(p.xz)-t.x,p.y) )-t.y;
}

float sdCapsule( vec3 p, vec3 a, vec3 b, float r )
{
    vec3 pa = p-a, ba = b-a;
    float h = clamp( dot(pa,ba)/dot(ba,ba), 0.0, 1.0 );
    return length( pa - ba*h ) - r;
}

float dot2_v(in vec3 v) { return dot(v,v); }
float dot2_v2(in vec2 v) { return dot(v,v); }

float sdCappedCone( in vec3 p, in float h, in float r1, in float r2 )
{
    vec2 q = vec2( length(p.xz), p.y );
    vec2 k1 = vec2(r2,h);
    vec2 k2 = vec2(r2-r1,2.0*h);
    vec2 ca = vec2(q.x-min(q.x,(q.y < 0.0)?r1:r2), abs(q.y)-h);
    vec2 cb = q - k1 + k2*clamp( dot(k1-q,k2)/dot2_v2(k2), 0.0, 1.0 );
    float s = (cb.x < 0.0 && ca.y < 0.0) ? -1.0 : 1.0;
    return s*sqrt( min(dot2_v2(ca),dot2_v2(cb)) );
}

float sdCylinder( vec3 p, vec2 h )
{
    vec2 d = abs(vec2(length(p.xz),p.y)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float sdCylinder_xy( vec3 p, vec2 h )
{
    vec2 d = abs(vec2(length(p.xy),p.z)) - h;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float opS( float d1, float d2 ) { return max(-d2,d1); }

vec2 opS_v2(vec2 d1, vec2 d2) { return vec2(max(-d2.x,d1.x), d1.y); }

float opU(float d1, float d2) { return min(d1, d2); }

vec2 opU_v2( vec2 d1, vec2 d2 ) { return (d1.x<d2.x) ? d1 : d2; }

float s2dCircle(in vec2 p, float r) { return length(p) - r; }

float s2dBox(in vec2 p, in vec2 b)
{
    vec2 d = abs(p) - b;
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float s2dCapsule(vec2 p, vec2 a, vec2 b, float r)
{
    vec2 pa = p - a, ba = b - a;
    float h = clamp( dot(pa,ba)/dot(ba,ba), 0.0, 1.0 );
    return length( pa - ba*h ) - r;
}

float s2dTri(in vec2 p)
{
    vec2 slope1 = normalize(vec2(0.6, 1));
    vec2 slope2 = vec2(slope1.x, -slope1.y);
    float slope_ofs = 0.065;
    float d = dot(p, vec2(-1, 0));
    d = max(d, dot(p - vec2(0, slope_ofs), slope1));
    d = max(d, dot(p - vec2(0, -slope_ofs), slope2));
    return d;
}

float s2dUsbLogo(in vec2 p)
{
    float d = 1e10;
    p.y -= 0.5;
    d = opU(d, s2dCircle(p-vec2(0.11,0.0), 0.1));
    d = opU(d, s2dBox(p-vec2(0.5,0.0), vec2(0.39, 0.02)));
    d = opU(d, s2dTri(p-vec2(0.88,0.0)));
    d = opU(d, s2dCircle(p-vec2(0.56,0.15), 0.052));
    d = opU(d, s2dCapsule(p,vec2(0.56,0.15), vec2(0.4,0.15), 0.02));
    d = opU(d, s2dCapsule(p,vec2(0.25,0.0), vec2(0.4,0.15), 0.02));
    d = opU(d, s2dBox(p-vec2(0.74,-0.15), vec2(0.052, 0.052)));
    d = opU(d, s2dCapsule(p,vec2(0.74,-0.15), vec2(0.58,-0.15), 0.02));
    d = opU(d, s2dCapsule(p,vec2(0.38,0.0), vec2(0.58,-0.15), 0.02));
    return d;
}

vec3 rot_xy(vec3 p, float ang)
{
    float c = cos(ang);
    float s = sin(ang);
    return vec3(p.x * c + p.y * s, p.x * s - p.y * c, p.z);
}

#define usb_plug_ratio (12.0 / 4.5)

vec2 sdUsbHole(in vec3 pos)
{
    vec2 res = vec2( 1e10, 0.0 );
    float shell_mat = 46.0 - length(pos.xy) * 10.0;
    float d = sdCylinder_xy(pos-vec3(0, 0, 0.5), vec2(1.0, 0.5));
    d = opS(d, sdCylinder_xy(pos-vec3(0, 0, -0.1), vec2(0.9, 0.2)));
    d -= 0.03;
    d = opU(d, sdCapsule(pos-vec3(0,0,0.7), vec3(-0.9,0,0), vec3(0.9,0,0), 0.3));
    d = opS(d, sdRoundBox(pos, vec3(0.1 * usb_plug_ratio, 0.1, 0.5), 0.05));
    res = opU_v2(res, vec2(d, shell_mat));
    res = opU_v2(res, vec2(sdBox(pos-vec3(0, 0.05, 0.43), vec3(0.1 * usb_plug_ratio, 0.05, 0.3)), 333.0));
    return res;
}

vec2 sdUsbPlug(in vec3 pos)
{
    vec2 res = vec2( 1e10, 0.0 );
    pos.z = -pos.z;
    res = opU_v2(res, vec2(sdBox(pos, vec3(0.1 * usb_plug_ratio, 0.1, 0.6)), 123.0));
    res = opU_v2(res, vec2(sdBox(pos-vec3( 0.1,0,-0.35), vec3(0.06, 0.105, 0.1)), 85.0));
    res = opU_v2(res, vec2(sdBox(pos-vec3(-0.1,0,-0.35), vec3(0.06, 0.105, 0.1)), 85.0));
    float body_mat = 55.0 - abs(fract(pos.z/0.4)) * 3.0;
    res = opU_v2(res, vec2(sdRoundBox(pos-vec3(0,0,0.5), vec3(0.1 * usb_plug_ratio, 0.1, 0.5), 0.1), body_mat));
    res = opU_v2(res, vec2(sdCylinder_xy(pos-vec3(0,0,1.0), vec2(0.3, 0.3)) - 0.03, 56.0));
    res = opU_v2(res, vec2(sdCylinder_xy(pos-vec3(0,0,1.2), vec2(0.2, 0.3)) - 0.03, 6.0));
    res = opU_v2(res, vec2(sdCylinder_xy(pos-vec3(0,0,5.2), vec2(0.11, 5.0)), 10.0));
    return res;
}

vec2 sdWheel(in vec3 pos)
{
    vec2 res = vec2( 1e10, 0.0 );
    float segment_ang = PI2 / 6.0;
    float rot_ang = TIME * speed;
    rot_ang *= segment_ang;
    rot_ang -= segment_ang / 2.0;
    float wheel_mat = 15.0 + length(pos.xy) * 10.0;
    float center_mat = 5486.0 + length(pos.xy) * 5.0;
    vec3 wpos = rot_xy(pos, rot_ang);
    float logo_scale = 4.0;
    float logo = s2dUsbLogo((wpos.xy / logo_scale + vec2(0.5, 0.5))) * logo_scale;
    if (logo <= 0.0) center_mat = 1000.0;
    float d = sdCylinder_xy(wpos-vec3(0,0,1), vec2(5.2, 0.5));
    d = opU(d, sdCylinder_xy(wpos-vec3(0,0,0.8), vec2(5.7, 0.1)));
    res = opU_v2(res, vec2(d, wheel_mat));
    res = opU_v2(res, vec2(sdRoundBox(wpos-vec3(0,0,0.6), vec3(1.8, 1.8, 0.1), 0.1), center_mat));
    res = opU_v2(res, vec2(sdRoundBox(rot_xy(wpos, PI/4.0)-vec3(0,0,0.6), vec3(1.8, 1.8, 0.1), 0.1), center_mat));
    float seg_ang = _atan(pos.y, pos.x) - rot_ang;
    seg_ang += segment_ang / 2.0;
    seg_ang -= mod(seg_ang, segment_ang);
    seg_ang += rot_ang;
    vec3 hole_pos = vec3(cos(seg_ang), sin(seg_ang), 0.0) * 4.0;
    res = opS_v2(res, vec2(sdCylinder_xy(pos - hole_pos, vec2(1.1, 5.0)), 1.0));
    res = opU_v2(res, sdUsbHole(pos - hole_pos));
    return res;
}

vec2 sdWheelExplosion(in vec3 pos)
{
    vec2 res = vec2( 1e10, 0.0 );
    float expl = 0.0;
    res = opU_v2(res, sdWheel(pos));
    res.x += expl * 3.0;
    return res;
}

vec2 map_m(in vec3 pos)
{
    vec2 res = vec2( 1e10, 0.0 );
    float time = TIME * speed;
    float usb_plug_offset = pow(abs(cos(time*3.0)), 5.0);
    float usb_plug_orientation = smoothstep(0.0, 1.0, abs(cos(time*1.1235)));
    usb_plug_offset *= 1.5;
    float usb_plug_ang = usb_plug_orientation * PI;
    res = opU_v2(res, sdWheelExplosion(pos));
    res = opU_v2(res, sdUsbPlug(rot_xy(pos-vec3(0,-4.0,-0.15-usb_plug_offset),usb_plug_ang)));
    return res;
}

vec2 castRay( in vec3 ro, in vec3 rd )
{
    vec2 res = vec2(-1.0,-1.0);
    float tmin = 1.0;
    float tmax = 20.0;
    float t = tmin;
    for( int i=0; i<130 && t<tmax; i++ )
    {
        vec2 h = map_m( ro+rd*t );
        if( abs(h.x)<(0.0001*t) )
        {
            res = vec2(t,h.y);
            break;
        }
        t += h.x;
    }
    return res;
}

float calcSoftshadow( in vec3 ro, in vec3 rd, in float mint, in float tmax_v )
{
    float res = 1.0;
    float t = mint;
    for( int i=0; i<16; i++ )
    {
        float h = map_m( ro + rd*t ).x;
        res = min( res, 8.0*h/t );
        t += clamp( h, 0.02, 0.10 );
        if( res<0.005 || t>tmax_v ) break;
    }
    return clamp( res, 0.0, 1.0 );
}

vec3 calcNormal( in vec3 pos )
{
    vec2 e = vec2(1.0,-1.0)*0.5773*0.0005;
    return normalize( e.xyy*map_m( pos + e.xyy ).x +
                      e.yyx*map_m( pos + e.yyx ).x +
                      e.yxy*map_m( pos + e.yxy ).x +
                      e.xxx*map_m( pos + e.xxx ).x );
}

float calcAO( in vec3 pos, in vec3 nor )
{
    float occ = 0.0;
    float sca = 1.0;
    for( int i=0; i<5; i++ )
    {
        float hr = 0.01 + 0.12*float(i)/4.0;
        vec3 aopos = nor * hr + pos;
        float dd = map_m( aopos ).x;
        occ += -(dd-hr)*sca;
        sca *= 0.95;
    }
    return clamp( 1.0 - 3.0*occ, 0.0, 1.0 ) * (0.5+0.5*nor.y);
}

// fwidth replacement for ISF
float checkersGradBox( in vec2 p )
{
    vec2 w = vec2(0.02) + 0.001;
    vec2 i = 2.0*(abs(fract((p-0.5*w)*0.5)-0.5)-abs(fract((p+0.5*w)*0.5)-0.5))/w;
    return 0.5 - 0.5*i.x*i.y;
}

vec3 render_v( in vec3 ro, in vec3 rd )
{
    vec3 col = vec3(0.7, 0.9, 1.0) + rd.y*0.8;
    col *= 0.1;
    vec2 res = castRay(ro,rd);
    float t = res.x;
    float m = res.y;
    if( m>-0.5 )
    {
        vec3 pos = ro + t*rd;
        vec3 nor = (m<1.5) ? vec3(0.0,1.0,0.0) : calcNormal( pos );
        vec3 ref = reflect( rd, nor );
        col = 0.45 + 0.35*sin( vec3(0.05,0.08,0.10)*(m-1.0) );
        if( m<1.5 )
        {
            float f = checkersGradBox( 5.0*pos.xz );
            col = 0.3 + f*vec3(0.1, 0.1, 0.1);
        }
        float occ = calcAO( pos, nor );
        vec3  lig = normalize( vec3(-0.4, 0.7, -0.6) );
        vec3  hal = normalize( lig-rd );
        float amb = clamp( 0.5+0.5*nor.y, 0.0, 1.0 );
        float dif = clamp( dot( nor, lig ), 0.0, 1.0 );
        float bac = clamp( dot( nor, normalize(vec3(-lig.x,0.0,-lig.z))), 0.0, 1.0 )*clamp( 1.0-pos.y,0.0,1.0);
        float dom = smoothstep( -0.2, 0.2, ref.y );
        float fre = pow( clamp(1.0+dot(nor,rd),0.0,1.0), 2.0 );
        dif *= calcSoftshadow( pos, lig, 0.02, 2.5 );
        dom *= calcSoftshadow( pos, ref, 0.02, 2.5 );
        float spe = pow( clamp( dot( nor, hal ), 0.0, 1.0 ),16.0)*
                    dif *
                    (0.04 + 0.96*pow( clamp(1.0+dot(hal,rd),0.0,1.0), 5.0 ));
        vec3 lin = vec3(0.0);
        lin += 1.30*dif*vec3(1.00,0.80,0.55);
        lin += 0.30*amb*vec3(0.40,0.60,1.00)*occ;
        lin += 0.40*dom*vec3(0.40,0.60,1.00)*occ;
        lin += 0.50*bac*vec3(0.25,0.25,0.25)*occ;
        lin += 0.25*fre*vec3(1.00,1.00,1.00)*occ;
        col = col*lin;
        col += 9.00*spe*vec3(1.00,0.90,0.70);
        col = mix( col, vec3(0.2,0.2,0.3), 1.0-exp( -0.0001*t*t*t ) );
        if (m == 1000.0) col = vec3(0,0,0);
    }
    return vec3( clamp(col,0.0,1.0) );
}

mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
    vec3 cw = normalize(ta-ro);
    vec3 cp = vec3(sin(cr), cos(cr),0.0);
    vec3 cu = normalize( cross(cw,cp) );
    vec3 cv = ( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

void main()
{
    float time = TIME * speed;

    // Auto-orbit camera
    float mo_x = 0.5 + 0.3*sin(time*0.3);
    float mo_y = 0.4 + 0.1*sin(time*0.2);

    vec3 ro = vec3( 2.6*cos(0.5*time + 6.0*mo_x), -3.5 + 2.0*mo_y, -6.5 + 1.6*sin(0.5*time + 6.0*mo_x) );
    vec3 ta = vec3( 0, -2.5, 0 );
    mat3 ca = setCamera( ro, ta, 0.0 );

    vec2 p = (-RENDERSIZE.xy + 2.0*gl_FragCoord.xy)/RENDERSIZE.y;
    vec3 rd = mul3x3(ca, normalize( vec3(p.xy,2.0) ));
    vec3 col = render_v( ro, rd );
    col = pow( col, vec3(0.4545) );

    gl_FragColor = vec4( col, 1.0 );
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quantum Socket'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, 'Quantum Socket.fs'), 'w') as f:
    f.write(content3)
print('Written Quantum Socket.fs')


# --- Steiner Surfaces ---
# Image pass with keyboard+buffer. GLSL 1.20 fallback already present:
# #if __VERSION__ < 300 => texelFetch returns vec4(0)
# All keypresses default to false, which gives good defaults.
# Replace iMouse with auto-orbit, iTime with TIME*speed
content4 = r"""/*{
    "DESCRIPTION": "Steiner Surfaces - representations of the projective plane.",
    "CREDIT": "mla / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define texelFetch_v(x,y,z) (vec4(0))

const float PI =  3.141592654;
const float TWOPI =  2.0*PI;

const float scale_v = 1.0;
const float camera = 2.0;
const float ambient = 0.4;
const float diffuse_v = 0.2;
const float specular_v = 1.0;
const float specpow = 25.0;

bool alert = false;

vec2 rotate_v(vec2 p, float t) {
  return p * cos(-t) + vec2(p.y, -p.x) * sin(-t);
}

float Boys(vec3 p) {
  float time = TIME * speed;
  float t = 0.5-0.5*cos(time/PI);
  float x = p.x, y = p.y, z = p.z;
  float x2 = x*x, y2 = y*y, z2 = z*z, t2 = t*t;
  float x3 = x2*x, y3 = y2*y, z3 = z2*z, t3 = t2*t;
  float x4 = x2*x2, y4 = y2*y2, z4 = z2*z2, t4 = t2*t2;
  float x5 = x2*x3, y5 = y2*y3, z5 = z2*z3, t5 = t2*t3;
  float x6 = x3*x3, y6 = y3*y3, z6 = z3*z3, t6 = t3*t3;
  float s = sqrt(2.0);
  return
    - 24.0*z6 + 48.0*z5 - 32.0*z4 + 64.0/9.0*z3 - 16.0*y2*z2 - 16.0*z2*x2
    - 81.0*y6*t2 - 81.0*x6*t2 - (144.0*t2 + 36.0)*y2*z2*x2
    + (72.0*s*t2 - 72.0*s)*y2*z2*x + (24.0*s - 24.0*s*t2)*z2*x3 - (18.0 + 72.0*t2)*y4*z2
    + (24.0 - 24.0*t2)*y2*z3 + (24.0 - 24.0*t2)*z3*x2 - (18.0 + 72.0*t2)*z2*x4
    + (54.0*s*t3 - 54.0*s*t)*z*y5 - (36.0*s*t + 12.0*s*t3)*z3*y3
    + (108.0*s*t - 108.0*s*t3)*x2*z*y3 + (108.0*s*t + 36.0*s*t3)*x2*z3*y
    + (162.0*s*t - 162.0*s*t3)*x4*z*y + 72.0*s*y2*z3*x + 48.0*s*y3*z2*t
    - 144.0*s*y*z2*x2*t - 324.0*s*y4*z*x*t2 - 216.0*s*y2*z*x3*t2 + 36.0*y4*z*t2
    - 243.0*y2*x4*t2 + 36.0*z4*x2*t2 - 243.0*y4*x2*t2 + 36.0*z*x4*t2 - 24.0*s*z3*x3
    + 36.0*y2*z4*t2 + 108.0*s*z*x5*t2 + 72.0*y2*z*x2*t2;
}

float Steiner(vec4 pos) {
  float time = TIME * speed;
  float x = pos.x, y = pos.y, z = pos.z, w = pos.w;
  float t = 0.2*time;
  float p = cos(t)/sqrt(3.0), q = sin(t);
  float x2 = x*x, y2 = y*y, z2 =z*z, w2 = w*w, pq = p*q, p2 = p*p;
  float x4 = x2*x2, y4 = y2*y2, z4 = z2*z2;
  return
    (1.0-2.0*pq-2.0*p2)*x4 + 4.0*pq*x2*w2 - 4.0*p2*y2*w2 + 4.0*(p2-pq)*x2*y2
    + 4.0*p2*y4 - 2.0*(p+q)*x2*z*w + x2*z2 + y2*z2;
}

vec4 quat = vec4(0,0,0,1);
vec4 qmul(vec4 p, vec4 q) {
    return vec4(p.w*q.xyz+q.w*p.xyz+cross(p.xyz,q.xyz),
                p.w*q.w-dot(p.xyz,q.xyz));
}

bool doquat = false;

vec4 map4(vec3 p) {
    vec4 p4 = vec4(p,1);
    if(doquat) p4 = qmul(p4,quat);
    return p4;
}

float eval(vec3 p) {
  return Steiner(map4(p));
}

vec3 grad(vec3 p, float eps) {
  vec2 e = vec2(0,eps);
  return vec3(eval(p+e.yxx)-eval(p-e.yxx),
              eval(p+e.xyx)-eval(p-e.xyx),
              eval(p+e.xxy)-eval(p-e.xxy))/(2.0*eps);
}

vec3 transform_v(in vec3 p) {
  float time = TIME * speed;
  // Auto-orbit (replaces mouse + keyboard)
  float theta = 0.3 * sin(time * 0.2);
  float phi = time * 0.3;
  p.yz = rotate_v(p.yz, -theta);
  p.zx = rotate_v(p.zx, phi);
  // Additional rotation (keypress CHAR_R was toggle - default: rotation ON)
  p.xz = rotate_v(p.xz, 0.123*time);
  return p;
}

float gridline(vec3 p) {
  vec4 p4 = map4(p);
  vec4 t = fract(p4*8.0);
  t = min(t,1.0-t);
  float d = t.z;
  return step(0.2,d);
}

float flip_v = 1.0;
float map_f(vec3 pos, vec3 dir) {
  float k = length(grad(pos,0.001));
  return max(length(pos)-10.0, flip_v*eval(pos)/k);
}

float TMAX = 10.0;
float fudge = 1.0;
float hmax_v = 1.0;
float march(vec3 ro, vec3 rd, float t) {
  for(int i = 0; i < 200; i++) {
    float precis = 0.001;
    float h = map_f(ro+rd*t,rd);
    if (h < precis) return t;
    h = min(h,hmax_v);
    t += fudge*h;
    if (t > TMAX) break;
  }
  return 1e8;
}

void main() {
  float time = TIME * speed;
  vec3 light = normalize(vec3(0.0,1.0,-1.0));
  vec3 lightcolor = vec3(1);
  vec2 uv = (2.0*gl_FragCoord.xy - RENDERSIZE.xy)/RENDERSIZE.y;
  vec3 p0 = vec3(0,0,-camera);
  p0 *= 1.0; // default zoom (keycount returns 0)
  vec3 r = vec3(scale_v*uv,2);

  light = transform_v(light);
  p0 = transform_v(p0);
  r = transform_v(r);
  r = normalize(r);

  // doquat = false by default (keypress Q returns false)
  float specmix = 0.0;
  vec3 color_v = vec3(0);
  float t = 0.1;
  bool dogrid = true; // !keypress(G) = true
  for (int i = 0; i < 3; i++) {
    t = march(p0,r,t);
    flip_v = -flip_v;
    fudge = 0.5;
    hmax_v = 0.25;
    if (t > TMAX) break;
    vec3 p = p0+t*r;
    if (dogrid && gridline(p) != 0.0) {
      t += 0.01;
      continue;
    }
    float eps = 0.01;
    vec3 normal = grad(p,eps);
    normal = normalize(normal);
    vec3 basecolor = 0.5+0.5*abs(normal);
    if (dot(r,normal) > 0.0) normal = -normal;
    color_v += basecolor*ambient;
    color_v += basecolor*diffuse_v*(max(0.0,dot(light,normal)));
    float spec = pow(max(0.0,dot(reflect(light,normal),vec3(r))),specpow);
    vec3 specularcolor = mix(basecolor,lightcolor,specmix);
    color_v += specular_v*spec*specularcolor;
    break;
  }

  color_v = sqrt(color_v);
  if (alert) color_v.x = 1.0;
  gl_FragColor = vec4(color_v,1);
}
"""

path4 = r'C:\Users\User\Documents\Resolume Wire\Patches\Steiner Surfaces'
os.makedirs(path4, exist_ok=True)
with open(os.path.join(path4, 'Steiner Surfaces.fs'), 'w') as f:
    f.write(content4)
print('Written Steiner Surfaces.fs')

print('Batch 9 complete: 4 shaders written')
