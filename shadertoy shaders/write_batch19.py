import os

# --- BloOoOoOoOoOom ---
# Buffer A has all rendering, Image is just gamma encode - merge them
# Key changes:
# - Replaced ALL uint/bitwise hash functions with float-based hashes
# - Removed floatBitsToUint, uintBitsToFloat, hex constants
# - Removed temporal accumulation (textureLod self-read)
# - Removed iTimeDelta (replaced with 1/60)
# - Removed FUNC4_UINT macro
# - Kept Spherical Fibonacci Mapping (all float math)
# - Kept sphere intersection, projection (all float math)
# - Renamed: Hash -> hash_f, PI -> PI_C (conflict with ISF)
content1 = r"""/*{
    "DESCRIPTION": "Animated bloom spheres using Spherical Fibonacci Mapping.",
    "CREDIT": "TinyTexel / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define SPOT_COUNT_MUL 12.0

#define PixelCount RENDERSIZE.xy

#define rsqrt inversesqrt
#define clamp01(x) clamp(x, 0.0, 1.0)

const float Pi_c = 3.14159265359;
const float Pi2_c  = Pi_c * 2.0;
const float Pi05_c = Pi_c * 0.5;

float Pow2(float x) {return x*x;}
float Pow3(float x) {return x*x*x;}
float Pow4(float x) {return Pow2(Pow2(x));}

vec2 AngToVec(float ang)
{
    return vec2(cos(ang), sin(ang));
}

float SqrLen2(float v) {return v * v;}
float SqrLen2v(vec2  v) {return dot(v, v);}
float SqrLen3(vec3  v) {return dot(v, v);}

vec3 GammaEncode(vec3 x) {return pow(x, vec3(1.0 / 2.2));}

// Float-based hash replacing uint hash system
float hash_f1(float n) { return fract(sin(n) * 43758.5453123); }
float hash_f2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
float hash_f3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453123); }

// Returns value in [-1, 1)
float hash_signed(vec3 p) { return hash_f3(p) * 2.0 - 1.0; }

float Intersect_Ray_Sphere(
vec3 rp, vec3 rd,
vec3 sp, float sr2,
out vec2 t)
{
    rp -= sp;

    float a = dot(rd, rd);
    float b = 2.0 * dot(rp, rd);
    float c = dot(rp, rp) - sr2;

    float D = b*b - 4.0*a*c;

    if(D < 0.0) return 0.0;

    float sqrtD = sqrt(D);
    t = (-b + vec2(-sqrtD, sqrtD)) / a * 0.5;

    if(c < 0.0) t.xy = t.yx;

    return t.x > 0.0 || c < 0.0 ? 1.0 : -1.0;
}

// Spherical Fibonacci Mapping
const float PHI_c = 1.6180339887498948482045868343656;

float madfrac_f( float a, float b) { return a*b - floor(a*b); }
vec2  madfrac_v2( vec2 a, float b) { return a*b - floor(a*b); }

float sf2id(vec3 p, float n)
{
    float phi = min(atan(p.y, p.x), Pi_c), cosTheta = p.z;

    float k  = max(2.0, floor( log(n * Pi_c * sqrt(5.0) * (1.0 - cosTheta*cosTheta))/ log(PHI_c*PHI_c)));
    float Fk = pow(PHI_c, k)/sqrt(5.0);

    vec2 F = vec2( floor(Fk + 0.5), floor(Fk * PHI_c + 0.5) );

    vec2 ka = -2.0*F/n;
    vec2 kb = 2.0*Pi_c*madfrac_v2(F+1.0, PHI_c-1.0) - 2.0*Pi_c*(PHI_c-1.0);
    mat2 iB = mat2( ka.y, -ka.x, -kb.y, kb.x ) / (ka.y*kb.x - ka.x*kb.y);

    vec2 c = floor( iB * vec2(phi, cosTheta - (1.0-1.0/n)));
    float d = 8.0;
    float j = 0.0;
    for( int s=0; s<4; s++ )
    {
        vec2 uv = vec2( float(s-2*(s/2)), float(s/2) );

        float cosTheta2 = dot(ka, uv + c) + (1.0-1.0/n);

        cosTheta2 = clamp(cosTheta2, -1.0, 1.0)*2.0 - cosTheta2;
        float i = floor(n*0.5 - cosTheta2*n*0.5);
        float phi2 = 2.0*Pi_c*madfrac_f(i, PHI_c-1.0);
        cosTheta2 = 1.0 - (2.0*i + 1.)/n;
        float sinTheta = sqrt(1.0 - cosTheta2*cosTheta2);

        vec3 q = vec3( cos(phi2)*sinTheta, sin(phi2)*sinTheta, cosTheta2);
        float squaredDistance = dot(q-p, q-p);
        if (squaredDistance < d)
        {
            d = squaredDistance;
            j = i;
        }
    }
    return j;
}

vec3 id2sf( float i, float n)
{
    float phi = 2.0*Pi_c*madfrac_f(i,PHI_c);
    float zi = 1.0 - (2.0*i+1.)/n;
    float sinTheta = sqrt( 1.0 - zi*zi);
    return vec3( cos(phi)*sinTheta, sin(phi)*sinTheta, zi);
}

float ProjSphereArea(float rdz, vec3 p, float rr)
{
    float zz = p.z * p.z;
    float ll = dot(p, p);

    return Pi_c * rdz*rdz * rr * rsqrt(abs(Pow3(rr - zz) / (rr - ll)));
}

vec4 ProjDisk(vec3 rd, vec3 p, vec3 n, float rr)
{
    vec3 np0 = n * p.xyz;
    vec3 np1 = n * p.yzx;
    vec3 np2 = n * p.zxy;

    mat3 k_mat = mat3(vec3( np0.y + np0.z,  np2.x        ,  np1.x        ),
                      vec3(-np2.y        ,  np1.y        , -np0.x - np0.z),
                      vec3(-np1.z        , -np0.x - np0.y,  np2.z        ));

    vec3 u =     k_mat * rd;
    vec3 k = u * k_mat;

    float nrd = dot(n, rd);
    float nrd_rr = nrd * rr;

    float v = dot(u, u) - nrd * nrd_rr;
    vec3  g =    (k     - n   * nrd_rr) * 2.0;

    return vec4(g.xy, 0.0, v);
}

float Sph(float x, float rr) { return sqrt(rr - x*x); }
float SphX0(float d, float rr0, float rr1) { return 0.5 * (d + (rr0 - rr1) / d); }

vec3 EvalSceneCol(vec3 cpos, mat3 cam_mat, float focalLen, vec2 uv0, float time)
{
    const vec3 cBG = vec3(0.0);

    vec2 uv2 = uv0 - PixelCount.xy * 0.5;

    vec3 rdir0 = vec3(uv2, focalLen);
    vec3 rdir = normalize(cam_mat * rdir0);

    float rdir0S = 0.5 * PixelCount.x;
    rdir0 /= rdir0S;

    vec2 t;
    float hit = Intersect_Ray_Sphere(cpos, rdir, vec3(0.0), 1.0, t);

    if(hit <= 0.0) return cBG;

    vec3 pf = cpos + rdir * t.x;

    float rra = 0.0;

    vec3 p2;
    float rr;
    {
        const float s = SPOT_COUNT_MUL;
        const float n = 1024.0*s;

        float id = sf2id(pf.xzy, n);
              p2 = id2sf(id,     n).xzy;

        float u = id / n;

        float arg = (-u* 615.5*2.0*s) + time * 1.0;

        rra = sin(arg);
        rra = (Pow2(rra)*2.-1.);
        rra = Pow2(rra);

        rr = 0.0025/s * rra;
    }

    vec3 n2 = normalize(p2);

    const float maskS = 0.5;

    if(SqrLen3(pf - p2) > rr) return cBG;

    float d = length(p2);

    float x0 = SphX0(d, 1.0, rr);
    vec3 d0c = n2 * x0;

    float d0rr = 1.0 - x0*x0;

    vec3 dp_c = (d0c - cpos) * cam_mat;
    vec3 dn_c = n2 * cam_mat;

    vec4 r = ProjDisk(rdir0, dp_c, dn_c, d0rr);

    float cmask = clamp01(-r.w * rsqrt(dot(r.xy, r.xy))*rdir0S * maskS);

    float cmask2 = 0.0;
    {
        vec3 d1c = n2 * (x0 - 0.008);

        vec4 r2 = ProjDisk(rdir0, (d1c - cpos) * cam_mat, n2 * cam_mat, (1.0 - x0*x0)*rra);
        cmask2 = clamp01(-r2.w * rsqrt(dot(r2.xy, r2.xy))*rdir0S * maskS);
    }

    float A = ProjSphereArea(rdir0.z, dp_c, d0rr);
    A *= rdir0S*rdir0S;

    float NdV = abs(dot(dn_c, normalize(dp_c)));

    A *= NdV;

    A *= NdV;
    cmask *= clamp01((A -2.0)*0.125);

    const vec3 cB = vec3(0.1, 0.35, 1.0);

    return mix(cBG, mix(cB*1.2, vec3(0.4, -0.15, -0.05), cmask2), cmask);
}


void main()
{
    vec2 uv0 = gl_FragCoord.xy;
    vec3 col = vec3(0.0);

    vec2 uv = uv0.xy - 0.5;

    float time = TIME * speed;
    float noise = hash_signed(vec3(uv * 0.435 + 0.847, time * 0.435 + 0.847)) * 0.5;

    float dt = 1.0 / 60.0;
    time += dt * noise;

    vec2 ang = vec2(Pi_c * 0.0, -Pi_c * 0.3);

    ang.x += time * 0.15*1.5;
    ang.y += sin(time * 0.27 * Pi_c) * 0.1;

    float fov = Pi_c * 0.5;

    mat3 cam_mat;
    float focalLen;
    {
        float sinPhi   = sin(ang.x);
        float cosPhi   = cos(ang.x);
        float sinTheta = sin(ang.y);
        float cosTheta = cos(ang.y);

        vec3 front = vec3(cosPhi * cosTheta,
                                   sinTheta,
                          sinPhi * cosTheta);

        vec3 right = vec3(-sinPhi, 0.0, cosPhi);
        vec3 up    = cross(right, front);

        focalLen = PixelCount.x * 0.5 * tan(Pi05_c - fov * 0.5);

        cam_mat = mat3(right, up, front);
    }

    vec3 cpos = -cam_mat[2] * (exp2(-0.3));

    cpos.y += .75;
    cpos.y += cos(time * 0.153 * Pi_c*1.0) * 0.08;

    col = EvalSceneCol(cpos, cam_mat, focalLen, uv0, time);

    // Apply bloom multiplier and gamma (merged from Image pass)
    col *= 8.0;
    col = GammaEncode(clamp01(col));

    gl_FragColor = vec4(col, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\BloOoOoOoOoOom'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'BloOoOoOoOoOom.fs'), 'w') as f:
    f.write(content1)
print('Written BloOoOoOoOoOom.fs')
print('Batch 19 complete: 1 shader written')
