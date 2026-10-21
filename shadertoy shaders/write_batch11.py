import os

# --- Dodecahedral Permutations ---
# Typed arrays unrolled to accessor functions, fwidth replaced, DEFSWAP inlined
content1 = r"""/*{
    "DESCRIPTION": "Even permutations of 5 elements as rotations of a dodecahedron.",
    "CREDIT": "mla / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const int N_VERTS = 20;

vec3 getVertex(int i) {
    if (i==0) return vec3(0,0,1);
    if (i==1) return vec3(0,0.6667,0.7453);
    if (i==2) return vec3(0.5773,-0.3333,0.7453);
    if (i==3) return vec3(-0.5773,-0.3333,0.7453);
    if (i==4) return vec3(-0.5773,0.7453,0.3333);
    if (i==5) return vec3(-0.9342,0.1274,0.3333);
    if (i==6) return vec3(-0.3568,-0.8727,0.3333);
    if (i==7) return vec3(0.3568,-0.8727,0.3333);
    if (i==8) return vec3(0.9342,0.1273,0.3333);
    if (i==9) return vec3(0.5773,0.7453,0.3333);
    if (i==10) return vec3(0,0,-1);
    if (i==11) return vec3(0,-0.6667,-0.7453);
    if (i==12) return vec3(-0.5773,0.3333,-0.7453);
    if (i==13) return vec3(0.5773,0.3333,-0.7453);
    if (i==14) return vec3(0.5773,-0.7453,-0.3333);
    if (i==15) return vec3(0.9342,-0.1274,-0.3333);
    if (i==16) return vec3(0.3568,0.8727,-0.3333);
    if (i==17) return vec3(-0.3568,0.8727,-0.3333);
    if (i==18) return vec3(-0.9342,-0.1273,-0.3333);
    return vec3(-0.5773,-0.7453,-0.3333); // i==19
}

int getColorIndex(int i) {
    if (i==0) return 0; if (i==1) return 1; if (i==2) return 2;
    if (i==3) return 3; if (i==4) return 4; if (i==5) return 2;
    if (i==6) return 4; if (i==7) return 1; if (i==8) return 4;
    if (i==9) return 3; if (i==10) return 4; if (i==11) return 2;
    if (i==12) return 3; if (i==13) return 1; if (i==14) return 3;
    if (i==15) return 0; if (i==16) return 2; if (i==17) return 0;
    if (i==18) return 1; return 0; // i==19
}

vec3 getColor(int i) {
    if (i==0) return vec3(0);
    if (i==1) return vec3(1,0,0);
    if (i==2) return vec3(0,1,0);
    if (i==3) return vec3(0,0,1);
    if (i==4) return vec3(1,1,0);
    return vec3(0.9); // i==5
}

vec3 qrot(vec3 p, vec4 q) {
    return p + 2.0*cross(q.xyz, cross(q.xyz,p)+q.w*p);
}

vec4 qpow1(vec4 q, float t) {
    if (q.xyz == vec3(0)) return vec4(0,0,0,1);
    float phi = acos(q.w);
    vec3 n = normalize(q.xyz);
    return vec4(sin(t*phi)*n, cos(t*phi));
}

vec4 qmul(vec4 p, vec4 q) {
    vec3 P = p.xyz, Q = q.xyz;
    return vec4(p.w*Q+q.w*P+cross(P,Q), p.w*q.w-dot(P,Q));
}

vec4 qconj(vec4 p) { return vec4(-p.xyz, p.w); }

vec4 qabs(vec4 p) { return p.w >= 0.0 ? p : -p; }

vec4 slerp(vec4 q0, vec4 q1, float t) {
    return qmul(qpow1(qabs(qmul(q1,qconj(q0))),t), q0);
}

void swapI(inout int p, inout int q) { int t = p; p = q; q = t; }
void swapV(inout vec3 p, inout vec3 q) { vec3 t = p; p = q; q = t; }

vec4 getrotation(vec3 p, vec3 q, vec3 r, vec3 s) {
    if (p == r) {
        if (q == s) return vec4(0,0,0,1);
        swapV(p,q); swapV(r,s);
    }
    vec3 n1 = r-p;
    vec4 q1 = vec4(n1,0);
    q = q - 2.0*dot(n1,q)/dot(n1,n1)*n1;
    vec3 n2 = distance(q,s) < 0.01 ? cross(r,q+s) : s-q;
    vec4 q2 = vec4(n2,0);
    vec4 t = qmul(q2,q1);
    return normalize(t);
}

// getvertices: find vertex pair for a permutation triple
vec2 getvertices_v(int p0, int p1, int p2) {
    int vi = 0;
    for (int i = 0; i < 20; i++) {
        if (getColorIndex(i) == p0 && getColorIndex((i+10) - 20 * ((i+10)/20)) == p2) { vi = i; break; }
    }
    int vj = 0;
    for (int j = 0; j < 20; j++) {
        if (getColorIndex(j) == p1 && distance(getVertex(vi), getVertex(j)) < 1.0) { vj = j; break; }
    }
    return vec2(float(vi), float(vj));
}

// getperm: find nth even permutation, return first, second, last elements
vec3 getperm_v(int k) {
    int a0=0, a1=1, a2=2, a3=3, a4=4;
    int p = 24;
    int inversions = 0;
    // i=4
    int k1 = k/p; inversions += 4-k1; k = k - k1*p;
    // shift a[k1] to a[4]
    int tmp;
    if (k1==0) { tmp=a0; a0=a1; a1=a2; a2=a3; a3=a4; a4=tmp; }
    else if (k1==1) { tmp=a1; a1=a2; a2=a3; a3=a4; a4=tmp; }
    else if (k1==2) { tmp=a2; a2=a3; a3=a4; a4=tmp; }
    else if (k1==3) { tmp=a3; a3=a4; a4=tmp; }
    // else k1==4, already in place
    p = p/4; // p=6
    // i=3
    k1 = k/p; inversions += 3-k1; k = k - k1*p;
    if (k1==0) { tmp=a0; a0=a1; a1=a2; a2=a3; a3=tmp; }
    else if (k1==1) { tmp=a1; a1=a2; a2=a3; a3=tmp; }
    else if (k1==2) { tmp=a2; a2=a3; a3=tmp; }
    p = p/3; // p=2
    // i=2
    k1 = k/p; inversions += 2-k1; k = k - k1*p;
    if (k1==0) { tmp=a0; a0=a1; a1=a2; a2=tmp; }
    else if (k1==1) { tmp=a1; a1=a2; a2=tmp; }
    // p=1, i=1: just check parity
    int modcheck = inversions - 2*(inversions/2);
    int kmod = k - 2*(k/2);
    if (modcheck != kmod) { tmp=a0; a0=a1; a1=tmp; }
    return vec3(float(a4), float(a3), float(a0));
}

vec3 istereo(vec2 p2) {
    vec3 p = vec3(p2, 0);
    vec3 centre = vec3(0,0,-1);
    float r2 = 2.0;
    p -= centre;
    p *= r2/dot(p,p);
    p += centre;
    return p;
}

void main() {
    float time = TIME * speed;
    vec2 p2 = (2.0*gl_FragCoord.xy - RENDERSIZE.xy)/RENDERSIZE.y;
    p2 *= 5.0;
    vec3 p = istereo(p2);
    float cycle = 4.0;
    float transition = 2.0;
    int n = int(time/cycle);
    int n60 = n - 60*(n/60);
    int n1_60 = (n+1) - 60*((n+1)/60);
    vec3 perm0 = getperm_v(n60*2);
    vec3 perm1 = getperm_v(n1_60*2);
    vec2 vv0 = getvertices_v(int(perm0.x), int(perm0.y), int(perm0.z));
    vec2 vv1 = getvertices_v(int(perm1.x), int(perm1.y), int(perm1.z));
    vec4 q0 = getrotation(getVertex(0), getVertex(1), getVertex(int(vv0.x)), getVertex(int(vv0.y)));
    vec4 q1 = getrotation(getVertex(0), getVertex(1), getVertex(int(vv1.x)), getVertex(int(vv1.y)));
    float ft = fract(time/cycle);
    float t = smoothstep(1.0, 2.0, transition*ft);
    vec4 q = slerp(q0, q1, t);
    q = normalize(q);
    p = qrot(p, q);
    vec3 col = vec3(0.9);
    float dwidth = 0.3;
    for (int i = 0; i < 20; i++) {
        float d = acos(clamp(dot(p, getVertex(i)), -1.0, 1.0));
        col = mix(getColor(getColorIndex(i)), col, smoothstep(0.0, max(0.01, 0.015), d-dwidth));
    }
    gl_FragColor = vec4(col, 1);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Dodecahedral Permutations'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Dodecahedral Permutations.fs'), 'w') as f:
    f.write(content1)
print('Written Dodecahedral Permutations.fs')


# --- Ray Marching Experiment n35 ---
# Single pass. Cubemap + texture replaced with procedural
content2 = r"""/*{
    "DESCRIPTION": "Ray marched displaced sphere with procedural environment.",
    "CREDIT": "Aiekick / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

float dstef = 0.0;

// Procedural environment
vec3 envColor(vec3 rd) {
    vec3 sky = mix(vec3(0.05,0.1,0.2), vec3(0.4,0.6,0.9), rd.y*0.5+0.5);
    sky += pow(max(dot(rd, normalize(vec3(-0.6,0.7,-0.5))), 0.0), 32.0) * vec3(1,0.9,0.7);
    return sky;
}

// Procedural texture replacement for effect()
vec3 effect(vec2 g)
{
    float t = TIME * speed * 1.5;
    g /= 200.;
    g.x -= t * .015;
    g.y += sin(g.x * 46.5 + t) * .12;
    // Procedural pattern instead of texture
    float n = sin(g.x*30.0)*sin(g.y*30.0)*0.5+0.5;
    n += sin(g.x*60.0+t)*sin(g.y*60.0-t)*0.25;
    vec3 c = vec3(n*0.8, n*0.6, n*0.4);
    c = smoothstep(c+.5, c, vec3(.71));
    return c;
}

#define mPi 3.14159
#define m2Pi 6.28318

vec4 displacement(vec3 p)
{
    vec3 col = effect(p.xz);
    col = clamp(col, vec3(0), vec3(1));
    float dist = dot(col, vec3(0.3));
    return vec4(dist, col);
}

float osphere(vec3 p, float r) { return length(p)-r; }

vec4 map_m(vec3 p)
{
    float scale_v = 1.;
    vec4 disp = displacement(p);
    float y = 1. - smoothstep(0., 1., disp.x) * scale_v;
    float dist = osphere(p, 5.-y);
    return vec4(dist, disp.yzw);
}

vec3 calcNormal(in vec3 pos, float prec)
{
    vec3 eps = vec3(prec, 0., 0.);
    vec3 nor = vec3(
        map_m(pos+eps.xyy).x - map_m(pos-eps.xyy).x,
        map_m(pos+eps.yxy).x - map_m(pos-eps.yxy).x,
        map_m(pos+eps.yyx).x - map_m(pos-eps.yyx).x);
    return normalize(nor);
}

float calcAO(in vec3 pos, in vec3 nor)
{
    float occ = 0.0;
    float sca = 1.0;
    for(int i=0; i<5; i++)
    {
        float hr = 0.01 + 0.12*float(i)/4.0;
        vec3 aopos = nor * hr + pos;
        float dd = map_m(aopos).x;
        occ += -(dd-hr)*sca;
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0*occ, 0.0, 1.0);
}

void main()
{
    float time = TIME * speed;
    float cam_a = 3.3;
    float cam_e = 6.;
    float cam_d = 2.;

    // Auto-orbit
    cam_e = 3.0 + 3.0*sin(time*0.2);
    cam_d = 10.0 + 5.0*cos(time*0.15);

    vec3 camUp = vec3(0,1,0);
    vec3 camView = vec3(0,0,0);
    float li = 0.6;
    float prec = 0.00001;
    float maxd = 50.;
    float refl_i = .6;
    float refr_a = 1.2;
    float refr_i = .8;
    float bii = 0.35;
    float marchPrecision = 0.5;

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy * 2. - 1.;
    uv.x *= RENDERSIZE.x/RENDERSIZE.y;

    vec3 col = vec3(0.);
    vec3 ro = vec3(-sin(cam_a)*cam_d, cam_e+1., cos(cam_a)*cam_d);
    vec3 rov = normalize(camView-ro);
    vec3 u = normalize(cross(camUp,rov));
    vec3 v = cross(rov,u);
    vec3 rd = normalize(rov + uv.x*u + uv.y*v);

    float b = bii;
    float d = 0.;
    vec3 p = ro+rd*d;
    float s = prec;

    for(int i=0; i<250; i++)
    {
        if (s<prec || s>maxd) break;
        s = map_m(p).x*marchPrecision;
        d += s;
        p = ro+rd*d;
    }

    if (d<maxd)
    {
        vec3 n = calcNormal(p, 0.1);
        b = li;
        vec3 ray = reflect(rd, n);
        vec3 cubeRay = envColor(ray) * refl_i;
        ray = refract(ray, n, refr_a);
        cubeRay += envColor(ray) * refr_i;
        col = cubeRay + pow(b,15.);

        float occ = calcAO(p, n);
        vec3 lig = normalize(vec3(-0.6, 0.7, -0.5));
        float amb = clamp(0.5+0.5*n.y, 0.0, 1.0);
        float dif = clamp(dot(n, lig), 0.0, 1.0);
        float bac = clamp(dot(n, normalize(vec3(-lig.x,0.0,-lig.z))), 0.0, 1.0)*clamp(1.0-p.y,0.0,1.0);
        float dom = smoothstep(-0.1, 0.1, cubeRay.y);
        float fre = pow(clamp(1.0+dot(n,rd),0.0,1.0), 2.0);
        float spe = pow(clamp(dot(cubeRay, lig), 0.0, 1.0), 16.0);

        vec3 brdf = vec3(0.0);
        brdf += 1.20*dif*vec3(1.00,0.90,0.60);
        brdf += 1.20*spe*vec3(1.00,0.90,0.60)*dif;
        brdf += 0.30*amb*vec3(0.50,0.70,1.00)*occ;
        brdf += 0.40*dom*vec3(0.50,0.70,1.00)*occ;
        brdf += 0.30*bac*vec3(0.25,0.25,0.25)*occ;
        brdf += 0.40*fre*vec3(1.00,1.00,1.00)*occ;
        brdf += 0.02;
        col = col*brdf;
        col = mix(col, vec3(0.8,0.9,1.0), 1.0-exp(-0.0005*d*d));
        col = mix(col, map_m(p).yzw, 0.5);
    }
    else
    {
        col = envColor(rd);
    }

    gl_FragColor = vec4(col, 1.0);
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\Ray Marching Experiment n35'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'Ray Marching Experiment n35.fs'), 'w') as f:
    f.write(content2)
print('Written Ray Marching Experiment n35.fs')


# --- Quaternion Averaging ---
# Single pass. texelFetch from texture replaced with procedural hash
content3 = r"""/*{
    "DESCRIPTION": "Quaternion averaging with sphere animation.",
    "CREDIT": "Dom Mandy / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

vec4 qmix(vec4 start, vec4 end_v, float weight) {
    float w = 1. - weight - weight,
          d = dot(start, end_v);
    return normalize(2.*weight*end_v*d + start*(w + sqrt(w*w + 4.*d*d*(weight*(1. - weight)))));
}

// Procedural hash replacement for texelFetch
float hash_v(float x, float y) {
    return fract(sin(x*127.1 + y*311.7) * 43758.5453);
}

vec4 quaternion(float x) {
    float q = 3. * hash_v(x, 2.0) - 1.5;
    vec3 n = normalize(vec3(hash_v(x, 1.0), hash_v(x+0.5, 1.0), hash_v(x+1.0, 1.0)) - .5);
    return vec4(cos(q), n * sin(q));
}

vec3 palette(float l, float h) {
    return l + l * vec3(.7874, .2848, .9278) * cos(h - vec3(0, 2.1, 4.2));
}

void main() {
    float time = TIME * speed;
    vec2 U = gl_FragCoord.xy;

    float t = mod(1e-9 + time / 2., 256.),
          f = floor(t),
          m = ceil(t);
    vec4 Q = qmix(quaternion(f), quaternion(mod(m, 256.)), smoothstep(f, m, t));

    vec2 i = RENDERSIZE.xy;
    vec2 uv = U + U - i;
    vec3 eye = vec3(0, 0, -3),
         ray = normalize(vec3(uv * .4 / i.y, 1)),
         up = vec3(0, 1, 0),
         z = normalize(Q.yzw);
    float angle = 2. * atan(length(Q.yzw), Q.x),
          c = cos(angle),
          s = sin(angle);
    eye = cross(z, eye) * s + mix(z * dot(z, eye), eye, c);
    ray = cross(z, ray) * s + mix(z * dot(z, ray), ray, c);

    float d = dot(ray, eye);
    vec3 normal = eye - ray * (d + sqrt(1. + d * d - dot(eye, eye))),
         r = reflect(ray, normal);
    bool is_nan = (normal.x != normal.x);
    vec4 pixel;
    if (is_nan) {
        pixel.rgb = sqrt(palette(pow(.5 + .5 * dot(up, ray), 2.), atan(ray.z, ray.x)));
    } else {
        pixel.rgb = sqrt(mix(vec3(max(0., .5 + .5 * dot(up, normal))),
            palette(2. * pow(.5 + .5 * dot(up, r), 2.) * mix(pow(1. + dot(normal, ray), 5.), 1., .04), atan(r.z, r.x)), .9));
    }
    gl_FragColor = vec4(pixel.rgb, 1.0);
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quaternion Averaging'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, 'Quaternion Averaging.fs'), 'w') as f:
    f.write(content3)
print('Written Quaternion Averaging.fs')

print('Batch 11 complete: 3 shaders written')
