import os

# --- [phreax] quantum field ---
# Image pass is self-contained raymarching. Common has color palettes.
# Key changes:
# - Unrolled typed arrays (vec3[]) into accessor functions with if-else chains
# - Replaced .length() with explicit constants
# - Replaced tanh() with x/(1.0+abs(x)) approximation
# - Replaced cubemap texture(iChannel0, rd) with procedural sky
# - Replaced triplanar bump texture(iChannel1,...) with procedural noise
# - Replaced iTime -> TIME*speed, iResolution -> RENDERSIZE
# - Removed highp qualifiers (not needed in ISF)
# - Renamed: map -> map_v, saturate -> saturate_v, random -> random_v
content1 = r"""/*{
    "DESCRIPTION": "Quantum field visualization with iridescent raymarching.",
    "CREDIT": "phreax/jiagual / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.141592
#define TAU (2.*PI)
#define SIN(x) (sin(x)*.5+.5)
#define BUMP_EPS 0.004
#define sabsk(x, k) sqrt(x * x + k * k)
#define sabs(x) (sabsk(x, .1))
#define S(a, b, x) smoothstep(a, b, x)
#define PAL 1

const float NOISE_GRANULARITY = 0.5/255.0;

float tt, g_mat;
vec3 ro;

mat2 rot(float a) { return mat2(cos(a), -sin(a), sin(a), cos(a)); }

float saturate_v(float x) {
    return clamp(x, 0., 1.);
}

float random_v(vec2 coords) {
   return fract(sin(dot(coords.xy, vec2(12.9898,78.233))) * 43758.5453);
}

vec3 invGamma(vec3 col) {
    return pow(col, vec3(2.2));
}

vec3 gamma_v(vec3 col) {
    return pow(col, vec3(1./2.2));
}

float box(vec3 p, vec3 r) {
  vec3 d = abs(p) - r;
  return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float smin(float a, float b, float k) {
  float h = clamp((a-b)/k * .5 + .5, 0.0, 1.0);
  return mix(a, b, h) - h*(1.-h)*k;
}

float pMod1(float p, float size) {
    float halfsize = size*0.5;
    float c = floor((p + halfsize)/size);
    p = mod(p + halfsize, size) - halfsize;
    return p;
}

vec2 pMod2(inout vec2 p, vec2 size) {
    vec2 c = floor((p + size*0.5)/size);
    p = mod(p + size*0.5,size) - size*0.5;
    return c;
}

float pModInterval1(inout float p, float size, float start, float stop) {
    float halfsize = size*0.5;
    float c = floor((p + halfsize)/size);
    p = mod(p+halfsize, size) - halfsize;
    if (c > stop) {
        p += size*(c - stop);
        c = stop;
    }
    if (c < start) {
        p += size*(c - start);
        c = start;
    }
    return c;
}

vec3 g_p;

float smax( float a, float b, float k )
{
    float h = max(k-abs(a-b),0.0);
    return max(a, b) + h*h*0.25/k;
}

// === Color palette system (unrolled typed arrays) ===

vec3 rgb2hsl(vec3 color) {
    float r = color.r;
    float g = color.g;
    float b = color.b;
    float mx = max(max(r, g), b);
    float mn = min(min(r, g), b);
    float h, s, l;
    l = (mx + mn) / 2.0;
    if (mx == mn) {
        h = s = 0.0;
    } else {
        float d = mx - mn;
        s = l > 0.5 ? d / (2.0 - mx - mn) : d / (mx + mn);
        if (mx == r) {
            h = (g - b) / d + (g < b ? 6.0 : 0.0);
        } else if (mx == g) {
            h = (b - r) / d + 2.0;
        } else {
            h = (r - g) / d + 4.0;
        }
        h /= 6.0;
    }
    return vec3(h, s, l);
}

// Unrolled color palettes as accessor functions
vec3 getColors1(int i) {
    if (i == 0) return vec3(84, 13, 110) / 255.0;
    if (i == 1) return vec3(238, 66, 102) / 255.0;
    if (i == 2) return vec3(255, 210, 63) / 255.0;
    if (i == 3) return vec3(59, 206, 172) / 255.0;
    return vec3(14, 173, 105) / 255.0;
}

vec3 getColors2(int i) {
    if (i == 0) return vec3(27, 231, 255) / 255.0;
    if (i == 1) return vec3(110, 235, 131) / 255.0;
    if (i == 2) return vec3(228, 255, 26) / 255.0;
    if (i == 3) return vec3(255, 184, 0) / 255.0;
    return vec3(255, 87, 20) / 255.0;
}

vec3 getColors3(int i) {
    if (i == 0) return vec3(241, 91, 181) / 255.0;
    if (i == 1) return vec3(0.957,0.576,0.263);
    if (i == 2) return vec3(241, 91, 181) / 255.0;
    if (i == 3) return vec3(254, 228, 64) / 255.0;
    return vec3(0, 245, 212) / 255.0;
}

vec3 getColors4(int i) {
    if (i == 0) return vec3(0.169, 0.761, 0.718);
    if (i == 1) return vec3(0.357, 0.518, 0.008);
    if (i == 2) return vec3(0.604, 0.851, 0.259);
    if (i == 3) return vec3(0.820, 0.235, 0.196);
    return vec3(0.522, 0.075, 0.020);
}

vec3 getColors5(int i) {
    if (i == 0) return vec3(237, 174, 73) / 255.0;
    if (i == 1) return vec3(209, 73, 91) / 255.0;
    if (i == 2) return vec3(0, 121, 140) / 255.0;
    if (i == 3) return vec3(48, 99, 142) / 255.0;
    return vec3(0, 61, 91) / 255.0;
}

vec3 getColors6(int i) {
    if (i == 0) return vec3(0, 204, 255) / 255.0;
    if (i == 1) return vec3(0, 255, 204) / 255.0;
    if (i == 2) return vec3(255, 255, 0) / 255.0;
    if (i == 3) return vec3(255, 0, 204) / 255.0;
    return vec3(204, 0, 255) / 255.0;
}

vec3 getColors7(int i) {
    if (i == 0) return vec3(176.,29.,30.) / 255.;
    if (i == 1) return vec3(241.,104.,38.) / 255.;
    if (i == 2) return vec3(234.,211.,95.) / 255.;
    if (i == 3) return vec3(0.,187.,173.) / 255.;
    if (i == 4) return vec3(0.,107.,228.) / 255.;
    return vec3(126.,99.,180.) / 255.;
}

vec3 getColorFromPalette(int palette, int i) {
    if (palette == 0) return getColors1(i);
    if (palette == 1) return getColors2(i);
    if (palette == 2) return getColors3(i);
    if (palette == 3) return getColors4(i);
    if (palette == 4) return getColors5(i);
    if (palette == 5) return getColors6(i);
    return getColors7(i);
}

int getPaletteLen(int palette) {
    if (palette == 6) return 6;
    return 5;
}

vec3 getColorRamp(int palette, float x) {
    x = fract(x);
    int colorCount = getPaletteLen(palette);
    float stepSize = 1.0/float(colorCount);
    int stepId = int(x/stepSize);
    vec3 c0 = getColorFromPalette(palette, int(mod(float(stepId), float(colorCount))));
    vec3 c1 = getColorFromPalette(palette, int(mod(float(stepId+1), float(colorCount))));
    vec3 col = mix(c0, c1, smoothstep(0., 1., pow(x/stepSize-float(stepId), pow(1.0, float(colorCount)+1.))));
    return col;
}

vec3 getPal(int pal, float x) {
    return getColorRamp(pal, x);
}

float smoothNoise21(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float n00 = dot(vec2(cos(dot(i, vec2(127.1, 311.7))), sin(dot(i, vec2(127.1, 311.7)))), f - vec2(0.0, 0.0));
    float n01 = dot(vec2(cos(dot(i + vec2(0.0, 1.0), vec2(127.1, 311.7))), sin(dot(i + vec2(0.0, 1.0), vec2(127.1, 311.7)))), f - vec2(0.0, 1.0));
    float n10 = dot(vec2(cos(dot(i + vec2(1.0, 0.0), vec2(127.1, 311.7))), sin(dot(i + vec2(1.0, 0.0), vec2(127.1, 311.7)))), f - vec2(1.0, 0.0));
    float n11 = dot(vec2(cos(dot(i + vec2(1.0, 1.0), vec2(127.1, 311.7))), sin(dot(i + vec2(1.0, 1.0), vec2(127.1, 311.7)))), f - vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(n00, n10, u.x), mix(n01, n11, u.x), u.y);
}

// === Main shader ===

float cubeGrid3d(vec3 p, float s, float tc) {
    float ss = 1.41;
    s *= ss;
    float s2 = s/7.;
    float s3 = s2-.08*S(1., 2., tt);
    float g = s2*2.0;
    float N = 3.;
    float idW = pModInterval1(p.z, g, -N, N);
    float idH = pModInterval1(p.y, g, -N, N);
    float idZ = pModInterval1(p.x, g, -N, N);
    float time = TIME * speed;
    float sm = mix(1., 0.04, SIN(idW*(.2)+idH*mix(1.1, .1, SIN(.4*tt))+idZ*mix(.2, .5, SIN(.8*tt+PI)) + 2.*tt+4.)*S(1., 2.5, time));
    float d = box(p, vec3(s3*sm))-.05*sm;
    return d*mix(.4, 1., sm);
}

float caps( vec3 p, float h, float r )
{
  p.y -= clamp( p.y, 0.0, h );
  return length( p ) - r;
}

float map_v(vec3 p) {
    p.y += 2.;
    p.xy = vec2(atan(p.y, p.x)*2.8, length(p.xy)*1.5);
    p.x = sabsk(p.x, .5);
    float d = 1e4;
    float n = smoothNoise21(p.xy*.2-tt*.4);
    float n2 = smoothNoise21(p.xy*.2-tt*.2+5.);
    p.xy *= rot(.5+0.05*sin(tt*.4));
    p.z += 2.*n;
    d = box(p, vec3(1000., 1000., .7));
    p.x -= .2*tt + .2*sin(.5*tt);
    p.y += .2*sin(p.z*5.+.5*tt);
    pMod2(p.xy, vec2(.4));
    g_p = p;
    p.yz = p.zy;
    p.y += 3.78-3.*n2;
    d = smin(d, caps(p, 4.*mix(.8, 1., n2),1.*(.8-.7*sin(n2+tt))*S(-1.4 - 3.*n,7., p.y)), 1.2);
    return d*.5;
}

vec3 getNormal(vec3 p) {
    vec2 eps = vec2(0.001, 0.0);
    return normalize(vec3(map_v(p + eps.xyy) - map_v(p - eps.xyy),
                          map_v(p + eps.yxy) - map_v(p - eps.yxy),
                          map_v(p + eps.yyx) - map_v(p - eps.yyx)));
}

vec3 raymarch(vec3 ro, vec3 rd, float steps) {
    float mat = 0., t = 0., d = 0.;
    vec3 p = ro;
    for(float i=.0; i<120.; i++) {
        if (i >= steps) break;
        d = map_v(p);
        mat = g_mat;
        if(abs(d) < 0.0001 || t > 100.) break;
        t += d;
        p += rd*d;
    }
    return vec3(t, mat, t);
}

float softshadow( in vec3 ro, in vec3 rd, in float mint, in float tmax )
{
    float res = 1.0;
    float t = mint;
    for( int i=0; i<1; i++ )
    {
        float h = map_v( ro + rd*t );
        res = min( res, 8.0*h/t );
        t += h*.25;
        if( h<0.001 || t>tmax ) break;
    }
    return clamp( res, 0., 1. );
}

float calcAO(vec3 p, vec3 n)
{
    float sca = 2.0, occ = 0.0;
    for( int i=0; i<5; i++ ){
        float hr = 0.01 + float(i)*0.5/4.0;
        float dd = map_v(n * hr + p);
        occ += (hr - dd)*sca;
        sca *= 0.7;
    }
    return clamp( 1.0 - occ, 0.0, 1.0 );
}

vec3 getRayDir(vec2 uv, vec3 p, vec3 l, float z) {
    vec3 f = normalize(l - p),
         r = normalize(cross(vec3(0, 1, 0), f)),
         u = cross(f, r),
         c = p + f * z,
         i = c + uv.x * r + uv.y * u,
         rd = normalize(i - p);
    return rd;
}

// Procedural triplanar noise replacing texture bump
float procNoise3D(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898, 78.233, 45.543))) * 43758.5453);
}

vec3 tex3D_proc( in vec3 p, in vec3 n ){
    n = max((abs(n) - 0.2)*7., 0.001);
    n /= (n.x + n.y + n.z);
    float xy = procNoise3D(p * 3.7 + vec3(0.0, 0.0, 1.23));
    float zx = procNoise3D(p * 3.7 + vec3(1.23, 0.0, 0.0));
    float yz = procNoise3D(p * 3.7 + vec3(0.0, 1.23, 0.0));
    return vec3(yz*n.x + zx*n.y + xy*n.z);
}

vec3 texBump_proc( in vec3 p, in vec3 n, float bf){
    const vec2 e = vec2(0.002, 0);
    mat3 m = mat3( tex3D_proc(p - e.xyy, n), tex3D_proc(p - e.yxy, n), tex3D_proc(p - e.yyx, n));
    vec3 coeffs = vec3(0.299*SIN(tt), 0.587, 0.114*SIN(.7*tt));
    vec3 g = coeffs*m;
    g = (g - dot(tex3D_proc(p, n), coeffs) )/e.x; g -= n*dot(n, g);
    return normalize( n + g*bf );
}

void cam(inout vec3 p) {
    // no-op
}

vec4 subsurface(vec3 o, vec3 dir){
    vec3 p = o;
    float e = 0.0;
    for(int i = 0; i < 7; ++i){
        float d = map_v(p);
        e += -d;
        if(d > -0.001)
            break;
        p -= d*dir;
    }
    return vec4(p, e);
}

// Procedural environment replacing cubemap
vec3 procEnv(vec3 rd) {
    float t = 0.5 + 0.5 * rd.y;
    vec3 sky = mix(vec3(0.1, 0.1, 0.15), vec3(0.3, 0.4, 0.6), t);
    float sun = pow(max(dot(rd, normalize(vec3(1.0, 0.5, -0.5))), 0.0), 32.0);
    return sky + vec3(sun * 0.3);
}

void main()
{
    vec2 uv = (gl_FragCoord.xy - .5*RENDERSIZE.xy)/RENDERSIZE.y;
    float time = TIME * speed;

    tt = time;
    float zoom = 9.;
    vec3 lp = vec3(5., 2.*sin(tt*.5), -7.),
         lp2 = vec3(-5., -1, -8.);

    vec3 col = vec3(0);

    float px = -.0*tt;
    ro = vec3(px, -8.  - SIN(.5*tt)*10., -12. + SIN(tt)*3.);
    vec3 lookat = vec3(px, 0, 0);

    cam(ro);

    vec3 rd = getRayDir(uv, ro, lookat, 1.5);

    float mat = 0., t = 0., d = 0.;

    vec2 e = vec2(0.0035, -0.0035);

    vec3 lc1 = vec3(0.702,1.000,0.965);
    vec3 lc2 = vec3(1.000,0.929,0.678);

    for(float i = 0.; i < 1.; i++) {
        float steps = i > 0. ? 50. : 120.;
        vec3 rm = raymarch(ro, rd, steps);

        mat = rm.y;
        vec3 pp = g_p;

        vec3 p = ro + rm.x*rd;
        vec3 n = normalize( e.xyy*map_v(p+e.xyy) + e.yyx*map_v(p+e.yyx) +
                            e.yxy*map_v(p+e.yxy) + e.xxx*map_v(p+e.xxx));

        n = texBump_proc(pp*2., n, .05);
        if(rm.x < 50.) {

            vec3 l = normalize(lp-p);
            vec3 l2 = normalize(lp2-p);
            float dif = max(dot(n, l), .0);
            float dif2 = max(dot(n, l2), .0);
            float spe = pow(max(dot(reflect(-rd, n), -l), .0),40.);

            float fre = pow(clamp(1.0 + dot(n, rd), 0.0, 1.0), 2.0);

            float sss = smoothstep(0., 1., map_v(p + l * .4)) / .4;
            float sss2 = smoothstep(0., 1., map_v(p + l2 * .4)) / .4;

            vec3 h = normalize(mix(-n, rd, 0.5));
            vec4 sv = subsurface(p+h*0.02, rd);
            float sss3 = max(0.0, 1.0-2.0*sv.w);

            float difO = dif;
            dif = mix(dif, sss3, 0.5);
            dif2 = mix(dif2, sss3, 0.5);

            vec3 light = .5*(dif*lc1 + dif2*lc2);

            col = light*getColorRamp(PAL, .1*dif-length(p)*0.05-length(pp)*.5*mix(.0, 1., SIN(.5*tt))+.5*tt + smoothNoise21(p.xz*.4)*.15 + p.z*.1)*1.;

            col = mix(col, col*S(-4., 2., pp.y), .5);
            float ao = calcAO(p, n);

            col = mix(col, col*(1.-ao), .3);

            rd = reflect(rd, n);
            // Procedural environment reflection instead of cubemap
            vec3 refl = procEnv(rd);
            refl = pow(refl, vec3(1./1.5));
            col = mix(col, 1.5*col*refl.rgb, .2);
            float tf = rm.x;

            float fog = exp(-tf*tf*0.04);
            col = mix(col, vec3(0), fog);
        }
    }

    col += mix(-NOISE_GRANULARITY, NOISE_GRANULARITY, random_v(uv));
    col *= mix(.2, 1., (1.5-pow(dot(uv, uv), .5)));

    col = pow(col*1.8, vec3(2.3));

    // tanh replacement: x/(1+abs(x))
    vec3 tc = col*1.4;
    col = tc / (1.0 + abs(tc));
    col = gamma_v(col);

    gl_FragColor = vec4(col, 1.);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\[phreax] quantum field'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, '[phreax] quantum field.fs'), 'w') as f:
    f.write(content1)
print('Written [phreax] quantum field.fs')
print('Batch 18 complete: 1 shader written')
