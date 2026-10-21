import os

# --- 4D Voronoi + Hopf Fibration ---
content1 = r"""/*{
    "DESCRIPTION": "Hopf Fibration macro-structure with 4D Voronoi micro-structure.",
    "CREDIT": "mimitech / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define TAU 6.28318530718
#define RADIUS 4.15
#define BRIGHTNESS 1.5

struct Voro4 {
    float d1;
    float d2;
    float hue;
};

mat2 rot(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

vec4 hash44(vec4 p) {
    float n = dot(p, vec4(1.0, 57.0, 113.0, 157.0));
    return fract(sin(vec4(n, n + 1.0, n + 2.0, n + 3.0)) * 43758.5453123);
}

float hash41(vec4 p) {
    float n = dot(p, vec4(1.0, 57.0, 113.0, 157.0));
    return fract(sin(n) * 43758.5453123);
}

vec3 mysticPalette(float t) {
    vec3 c = 0.58 + 0.42 * cos(TAU * (vec3(0.05, 0.33, 0.67) + t + vec3(0.00, 0.03, 0.08)));
    c = pow(c, vec3(1.18));
    vec3 gold   = vec3(1.20, 0.88, 0.46);
    vec3 cyan   = vec3(0.42, 1.00, 1.22);
    vec3 violet = vec3(0.70, 0.50, 1.18);
    vec3 accent = mix(gold, cyan, 0.5 + 0.5 * sin(TAU * (1.7 * t + 0.17)));
    accent = mix(accent, violet, 0.35);
    return 1.15 * mix(c, accent, 0.32) * vec3(0.93, 0.84, 1.10);
}

vec4 hopfWarp(vec3 p, float time) {
    vec4 q = vec4(p * 0.32, length(p) * 0.15 + sin(time * 0.1) * 0.15);
    q.xy = rot(time * 0.05 + 0.3) * q.xy;
    q.xw = rot(time * 0.09 + 0.7) * q.xw;
    q.yz = rot(time * 0.07 + 1.1) * q.yz;
    q.zw = rot(time * 0.11 + 1.8) * q.zw;
    vec4 q4 = normalize(q + vec4(0.0001));
    float u = 2.0 * (q4.x * q4.z + q4.y * q4.w);
    float v = 2.0 * (q4.y * q4.z - q4.x * q4.w);
    float phase = atan(q4.y, q4.x);
    float flow = time * 0.8;
    float scaleS2 = 3.5;
    float scaleS1 = 2.5;
    return vec4(u * scaleS2, v * scaleS2, cos(phase + flow) * scaleS1, sin(phase + flow) * scaleS1);
}

Voro4 voronoi4(vec4 p) {
    vec4 g = floor(p);
    vec4 f = fract(p);
    float md1 = 1e9;
    float md2 = 1e9;
    vec4 bestCell = vec4(0.0);
    for (int xi = -1; xi <= 1; ++xi)
    for (int yi = -1; yi <= 1; ++yi)
    for (int zi = -1; zi <= 1; ++zi)
    for (int wi = -1; wi <= 1; ++wi) {
        vec4 o = vec4(float(xi), float(yi), float(zi), float(wi));
        vec4 cell = g + o;
        vec4 h = hash44(cell);
        vec4 fp = o + (0.22 + 0.56 * h);
        vec4 r = fp - f;
        float d = dot(r, r);
        if (d < md1) {
            md2 = md1; md1 = d; bestCell = cell;
        } else if (d < md2) {
            md2 = d;
        }
    }
    Voro4 v;
    v.d1 = md1; v.d2 = md2;
    v.hue = hash41(bestCell + 19.19);
    return v;
}

vec2 raySphere(vec3 ro, vec3 rd, float r) {
    float b = dot(ro, rd);
    float c = dot(ro, ro) - r * r;
    float h = b * b - c;
    if (h < 0.0) return vec2(-1.0);
    h = sqrt(h);
    return vec2(-b - h, -b + h);
}

vec3 layerColor(vec3 p, float time, float depthMix) {
    vec4 warpedCoord = hopfWarp(p, time + depthMix * 0.2);
    Voro4 v = voronoi4(warpedCoord);
    float edge = exp(-22.0 * max(v.d2 - v.d1, 0.0));
    float interior = 0.55 + 0.45 * cos(8.0 * v.d1 - 5.0 * v.hue + 0.35 * time);
    vec3 cellCol = mysticPalette(v.hue);
    vec3 glowCol = mix(vec3(1.25, 0.82, 0.40), vec3(0.36, 0.96, 1.30), 0.5 + 0.5 * sin(TAU * (v.hue + 0.08 * time)));
    vec3 col = cellCol * (0.4 + 0.5 * interior);
    col += glowCol * (1.2 * edge);
    float centerCore  = exp(-180.0 * v.d1);
    float centerFlash = exp(-60.0  * v.d1);
    vec3 hotCol = mix(vec3(2.10, 1.95, 1.70), vec3(1.45, 1.75, 2.15), 0.5 + 0.5 * sin(TAU * (v.hue + 0.07 * time)));
    vec3 centerCol = mix(vec3(1.50, 1.18, 0.62), vec3(0.72, 1.15, 1.55), 0.5 + 0.5 * sin(TAU * (v.hue + 0.13 * time)));
    col += centerCol * (2.0 * centerFlash);
    col += hotCol * (4.5 * centerCore);
    return max(col, 0.0);
}

void main() {
    float time = TIME * speed;
    vec2 uv = (gl_FragCoord.xy - 0.5 * RENDERSIZE.xy) / RENDERSIZE.y;
    float yaw = 0.08 * time;
    float pitch = 0.25 * sin(time * 0.1);
    float camR = 6.8;
    vec3 ro = vec3(camR * sin(yaw) * cos(pitch), camR * sin(pitch), camR * cos(yaw) * cos(pitch));
    vec3 ta = vec3(0.0);
    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize(cross(vec3(0.0, 1.0, 0.0), ww));
    vec3 vv = cross(ww, uu);
    vec3 rd = normalize(uv.x * uu + uv.y * vv + 2.0 * ww);
    vec3 bg = vec3(0.008, 0.010, 0.020);
    vec3 sp = floor(rd * 200.0);
    bg += smoothstep(0.996, 1.0, fract(sin(dot(sp, vec3(17.0, 59.0, 113.0))) * 43758.5453)) * vec3(0.8, 0.9, 1.1);
    vec3 col = bg;
    vec2 hit = raySphere(ro, rd, RADIUS);
    if (hit.y > 0.0) {
        float tF = max(hit.x, 0.0);
        float tB = hit.y;
        vec3 pF = ro + rd * tF;
        vec3 n = normalize(pF);
        vec3 ir = refract(rd, n, 1.0 / 1.12);
        if (dot(ir, ir) < 0.001) ir = reflect(rd, n);
        float thickness = tB - tF;
        vec3 s0 = pF + ir * (0.12 * thickness);
        vec3 s1 = pF + ir * (0.38 * thickness);
        vec3 s2 = pF + ir * (0.72 * thickness);
        vec3 c0 = layerColor(s0, time, 0.0);
        vec3 c1 = layerColor(s1, time, 1.5);
        vec3 c2 = layerColor(s2, time, 2.8);
        col = 0.65 * c0 + 0.28 * c1 + 0.15 * c2;
        col *= 0.95 * exp(-0.025 * thickness * thickness);
        float fres = pow(1.0 - max(dot(-rd, n), 0.0), 4.5);
        col += fres * vec3(0.18, 0.28, 0.62);
        float aura = exp(-6.0 * abs(length(cross(ro, rd)) - RADIUS));
        col += 0.04 * aura * vec3(0.65, 0.78, 1.10);
        col = mix(col, bg, 0.08);
    }
    col *= 1.0 - 0.28 * dot(uv, uv);
    col *= BRIGHTNESS;
    col = 1.0 - exp(-1.35 * col);
    col = pow(col, vec3(0.84));
    gl_FragColor = vec4(col, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\4D Voronoi + Hopf Fibration'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, '4D Voronoi + Hopf Fibration.fs'), 'w') as f:
    f.write(content1)
print('Written 4D Voronoi + Hopf Fibration.fs')

# --- Sands ---
content2 = r"""/*{
    "DESCRIPTION": "Raymarched sand dune landscape with soft shadows and AO.",
    "CREDIT": "eddietree / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const float MAX_TRACE_DISTANCE = 10.0;
const float INTERSECTION_PRECISION = 0.01;
const int NUM_OF_TRACE_STEPS = 70;

float tri(in float x){return abs(fract(x)-.5);}
vec3 tri3(in vec3 p){return vec3( tri(p.z+tri(p.y*1.)), tri(p.z+tri(p.x*1.)), tri(p.y+tri(p.x*1.)));}

vec3 hsv(float h, float s, float v)
{
  return mix( vec3( 1.0 ), clamp( ( abs( fract(
    h + vec3( 3.0, 2.0, 1.0 ) / 3.0 ) * 6.0 - 3.0 ) - 1.0 ), 0.0, 1.0 ), s ) * v;
}

float udRoundBox( vec3 p, vec3 b, float r )
{
  return length(max(abs(p)-b,0.0))-r;
}

float distSphere(vec3 p, float radius) {
    return length(p) - radius;
}

float sdPlane( vec3 p, vec4 n )
{
  return dot(p,n.xyz) + n.w;
}

float sdTorus( vec3 p, vec2 t )
{
  vec2 q = vec2(length(p.xy)-t.x,p.z);
  return length(q)-t.y;
}

float sdTriPrism( vec3 p, vec2 h )
{
    vec3 q = abs(p);
    return max(q.z-h.y,max(q.x*0.866025+p.y*0.5,-p.y)-h.x*0.5);
}

float sdCone( vec3 p, vec2 c )
{
    float q = length(p.xy);
    return dot(c,vec2(q,p.z));
}

mat3 calcLookAtMatrix( in vec3 ro, in vec3 ta, in float roll )
{
    vec3 ww = normalize( ta - ro );
    vec3 uu = normalize( cross(ww,vec3(sin(roll),cos(roll),0.0) ) );
    vec3 vv = normalize( cross(uu,ww));
    return mat3( uu, vv, ww );
}

mat3 xrotate(float t) {
    return mat3(1.0, 0.0, 0.0,
                0.0, cos(t), -sin(t),
                0.0, sin(t), cos(t));
}

mat3 yrotate(float t) {
    return mat3(cos(t), 0.0, -sin(t),
                0.0, 1.0, 0.0,
                sin(t), 0.0, cos(t));
}

mat3 zrotate(float t) {
    return mat3(cos(t), -sin(t), 0.0,
                sin(t), cos(t), 0.0,
                0.0, 0.0, 1.0);
}

float smin( float a, float b, float k )
{
    float res = exp( -k*a ) + exp( -k*b );
    return -log( res )/k;
}

float opS( float d1, float d2 )
{
    return max(-d1,d2);
}

mat3 fullRotate( vec3 r ){
   return xrotate( r.x ) * yrotate( r.y ) * zrotate( r.z );
}

float rotatedBox( vec3 p , vec3 r , vec3 size , float rad ){
    vec3 q = fullRotate( r ) * p;
    return udRoundBox( q , size , rad );
}

vec2 opU( vec2 d1, vec2 d2 ){
    return (d1.x<d2.x) ? d1 : d2;
}

vec2 map( vec3 pos ){
    vec3 size = vec3( 5.0, .1 , 5.0 );
    vec3 r = vec3( 0.,0.,0. );
    vec2 res = vec2( 1.0, 1.0 );
    float box = rotatedBox( pos - vec3(0.0,-0.5,0.0), r , size , .001 );
    float t1 = box;
    float time = TIME * speed;
    for ( int i = 0; i < 12; i++ )
    {
        float i_f = float(i);
        vec3 pos0 = xrotate( time*0.2 + sin(i_f)*50.0 ) * pos;
        pos0 = pos0 + vec3(0.0 + cos(time*0.1+i_f*0.3)*0.5,-0.1 + sin(time + i_f * 50.0),2.2 + sin(time*0.3 + i_f));
        float prism = sdTriPrism( pos0, vec2(0.2 + cos(time + i_f*0.1)*0.1,0.7) );
        t1 = smin( prism, t1, 6.0 );
    }
    t1  = opS(sdTorus( pos * yrotate( 3.14159*0.5), vec2(2.36 + sin(time*0.1)*0.5,0.2 + cos(time*0.5)*0.2) ), t1 );
    t1  = smin(sdTorus( (pos+vec3(0.0,-0.6,0.0)) * yrotate( 3.14159*0.5), vec2(2.5,0.02 + cos(time*5.0 + pos.y*2.0)*0.01) ), t1, 6.0 );
    t1  = smin(sdTorus( (pos+ vec3( 0.0,-0.6,sin(time*0.3))) * yrotate( 3.14159*0.5), vec2(1.75,0.05 + sin(pos.y*3.0 + time)*0.2) ), t1, 10.0 );
    t1  = smin(sdTorus( pos * yrotate( 3.14159*0.5), vec2(1.5,0.1) ), t1, 5.0 );
    res.x = t1;
    return res;
}

float shadow_v( in vec3 ro, in vec3 rd )
{
    const float k = 2.0;
    const int maxSteps = 50;
    float t = 0.0;
    float res = 1.0;
    for(int i = 0; i < maxSteps; ++i) {
        float d = map(ro + rd*t).x;
        if(d < INTERSECTION_PRECISION) return 0.0;
        res = min( res, k*d/t );
        t += d;
    }
    return res;
}

float ambientOcclusion( in vec3 ro, in vec3 rd )
{
    const int maxSteps = 7;
    const float stepSize = 0.05;
    float t = 0.0;
    float res = 0.0;
    float d0 = map(ro).x;
    for(int i = 0; i < maxSteps; ++i) {
        float d = map(ro + rd*t).x;
        float diff = max(d-d0, 0.0);
        res += diff;
        t += stepSize;
    }
    return res;
}

vec3 calcNormal( in vec3 pos ){
    vec3 eps = vec3( 0.001, 0.0, 0.0 );
    vec3 nor = vec3(
        map(pos+eps.xyy).x - map(pos-eps.xyy).x,
        map(pos+eps.yxy).x - map(pos-eps.yxy).x,
        map(pos+eps.yyx).x - map(pos-eps.yyx).x );
    return normalize(nor);
}

bool renderRayMarch(vec3 rayOrigin, vec3 rayDirection, out vec3 color ) {
    float t = 0.0;
    vec3 lightDir = normalize(vec3(1.0,0.4,0.0));
    for(int i = 0; i < NUM_OF_TRACE_STEPS; ++i) {
        vec3 currPos = rayOrigin + rayDirection * t;
        float d = map(currPos).x;
        if(d < INTERSECTION_PRECISION) {
            vec3 normal = calcNormal( currPos );
            float shadowVal = shadow_v( currPos - rayDirection* 0.01, lightDir  );
            float ao = ambientOcclusion( currPos - normal*0.01, normal );
            float ndotl = abs(dot( -rayDirection, normal ));
            float rim = pow(1.0-ndotl, 1.5);
            color = vec3( 1.0);
            color = mix( vec3(0.7,0.6,0.5), color, rim*0.3 );
            color *= vec3(mix(0.2,1.0,shadowVal));
            color *= vec3(mix(0.2,1.0,ao));
            return true;
        }
        t += d;
    }
    return false;
}

void main()
{
    float time = TIME * speed;
    vec2 p = (-RENDERSIZE.xy + 2.0*gl_FragCoord.xy)/RENDERSIZE.y;
    float an = 0.3 + time*0.3;
    vec3 ro = vec3(5.0*sin(an),1.5,5.0*cos(an));
    vec3 ta = vec3(0.0,0.5,0.0);
    mat3 camMat = calcLookAtMatrix( ro, ta, 0.0 );
    vec3 rd = normalize( camMat * vec3(p.xy,2.0) );
    vec3 col = vec3(0.7,0.6,0.5) * 0.7;
    renderRayMarch( ro, rd, col );
    gl_FragColor = vec4( col , 1. );
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\Sands'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'Sands.fs'), 'w') as f:
    f.write(content2)
print('Written Sands.fs')
