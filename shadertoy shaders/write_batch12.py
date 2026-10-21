import os

# --- 16 Dimensional Julia (Sedenion) ---
content1 = r"""/*{
    "DESCRIPTION": "16 Dimensional Julia fractal using sedenion algebra.",
    "CREDIT": "rodolphito / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const vec4 pi = vec4(0.0, 1.5707963268, 3.1415926536, 6.2831853072);

float qsl(vec4 q){return dot(q,q);}
float qsil(vec4 q){return dot(q.yzw,q.yzw);}
vec4 qconj(vec4 q){q.x=-q.x;return-q;}
vec4 qmul(vec4 a,vec4 b){return vec4(a.x*b.x-dot(a.yzw,b.yzw),b.yzw*a.x+a.yzw*b.x+cross(a.yzw,b.yzw));}
vec4 qsqr(vec4 q){return vec4(q.x*q.x-qsil(q),2.0*q.x*q.yzw);}

float osl(mat2x4 o){return qsl(o[0])+qsl(o[1]);}
float osil(mat2x4 o){return qsil(o[0])+qsl(o[1]);}
mat2x4 oconj(mat2x4 o){o[0].x=-o[0].x;return-o;}
mat2x4 omul(mat2x4 a,mat2x4 b){return mat2x4(qmul(a[0],b[0])-qmul(qconj(b[1]),a[1]),qmul(b[1],a[1])+qmul(a[1],qconj(b[0])));}
mat2x4 osqr(mat2x4 o){return mat2x4(qsqr(o[0])-vec4(qsil(o[1]),vec3(0)),qsqr(o[1])+qmul(o[0],qconj(o[1])));}

mat4 sreal(float a){return mat4(a,vec3(0),vec4(0),vec4(0),vec4(0));}
float ssl(mat4 s){return qsl(s[0])+qsl(s[1])+qsl(s[2])+qsl(s[3]);}
float sl(mat4 s){return sqrt(ssl(s));}
mat4 smul(mat4 a,mat4 b){mat2x4 c=omul(mat2x4(a[0],a[1]),mat2x4(b[0],b[1]))-omul(oconj(mat2x4(b[2],b[3])),mat2x4(a[2],a[3]));mat2x4 d=omul(mat2x4(b[2],b[3]),mat2x4(a[2],a[3]))+omul(mat2x4(a[2],a[3]),oconj(mat2x4(b[0],b[1])));return mat4(c[0],d[1],c[0],d[1]);}
mat4 ssqr(mat4 s){mat2x4 a=osqr(mat2x4(s[0],s[1]))-mat2x4(osil(mat2x4(s[2],s[3])),vec3(0),vec4(0));mat2x4 b=osqr(mat2x4(s[2],s[3]))+omul(mat2x4(s[0],s[1]),oconj(mat2x4(s[2],s[3])));return mat4(a[0],a[1],b[0],b[1]);}

vec3 hsv2rgb(vec3 c){return (2.0-c.y-sin(c.x-pi.xzw/3.0)*c.y)*c.z*0.5;}

mat4 rand3 = mat4(
     8.6324789700e-1,   7.3956859870e-1,
    -5.3717888280e-1,  -3.6349861560e-1,
     1.1642346260e-1,  -7.0595935620e-2,
     1.6893859320e-1,  -5.4608794640e-1,
    -1.0161218400e+0,   3.6012778120e-1,
    -1.3112304220e-2,  -6.1305132510e-1,
     5.6552559430e-1,  -1.1049970990e-2,
     2.0906878620e-1,  -1.1049500920e+0
);

#define fractalIters 5
#define marchingIters 80
#define far 10.0

mat4 f_julia(mat4 s, mat4 c){return ssqr(s) + c;}

float sdf(mat4 p, mat4 c){
    mat4 deriv = sreal(1.0);
    for(int i = 0; i < fractalIters; i++){
        deriv = smul(2.0*p, deriv);
        p = f_julia(p,c);
    }
    float lp = sl(p);
    float rv = 0.5*log(lp)/exp2(float(fractalIters));
    if (rv != rv) return 0.0;
    return rv;
}

vec3 getCol(mat4 s, mat4 c){
    float sc = sdf(s*1.1,c);
    if (sc > 1.0) sc = 1.0;
    float value = 1.0-0.25*ssl(s);
    float satur = value;
    value *= value;
    value *= value;
    value *= sc;
    float sharp = sdf(smul(rand3/sl(rand3),s),c);
    return hsv2rgb(vec3(sharp*50.0,satur,value));
}

vec4 iSphere(vec3 ro, vec3 rd){
    float rdro = dot(rd, ro);
    float disc = rdro*rdro - dot(ro, ro) + 4.0;
    if(disc < 0.0) return vec4(9e9);
    disc = sqrt(disc);
    float d = -rdro - disc;
    return vec4(ro + d*rd, 2.0*disc);
}

vec3 render_v(vec3 ro, vec3 rd, vec4 m){
    vec4 sphere = iSphere(ro, rd);
    mat4 c = mat4(vec4(0.05), vec4(0.05), vec4(0.05), m);
    mat4 p = mat4(vec4(0), vec4(0), vec4(0), sphere.xyz, 0);
    vec3 col = vec3(0.0);
    if(sphere.w < far){
        mat4 dir = mat4(vec4(0), vec4(0), vec4(0), rd, 0);
        float t = 0.0;
        for(int i = 0; i < marchingIters; i++){
            float d = sdf(p,c);
            t += d;
            p += d * dir;
            col += max(0.0,1.0-d)*getCol(p,c);
            if(t > sphere.w) break;
        }
    }
    return col;
}

vec3 rotateView(vec3 v, vec2 ang){
    vec4 t = sin(vec4(ang, ang + 1.5707963268));
    float g = dot(v.yz, t.yw);
    return vec3(v.x * t.z - g * t.x,
                v.y * t.w - v.z * t.y,
                v.x * t.x + g * t.z);
}

void main(){
    float time = TIME * speed;
    vec4 m;
    m.xy = (2.0*gl_FragCoord.xy - RENDERSIZE.xy)/RENDERSIZE.y;
    m.zw = vec2(0.6,0.6)*sin(time*vec2(0.4,0.7)+vec2(0.9,1.5));
    vec3 ro = vec3(0,0,-4);
    vec3 rd = normalize(vec3(m.xy, 3));
    ro = rotateView(ro, vec2(0.5,0.2)*time);
    rd = rotateView(rd, vec2(0.5,0.2)*time);
    gl_FragColor.a = 0.0;
    gl_FragColor.rgb = render_v(ro, rd, m).grb;
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\16 Dimensional Julia (Sedenion)'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, '16 Dimensional Julia (Sedenion).fs'), 'w') as f:
    f.write(content1)
print('Written 16 Dimensional Julia (Sedenion).fs')


# --- Barth Sextic Surfaces ---
content2 = r"""/*{
    "DESCRIPTION": "Barth sextic surface via stereographic projection from S3.",
    "CREDIT": "mla / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const float PI = 3.141592654;
const float phi = 1.618033;
const float phi2 = phi*phi;

vec3 light_v;

vec4 qmul_b(vec4 p, vec4 q) {
  vec3 P = p.xyz, Q = q.xyz;
  return vec4(p.w*Q+q.w*P+cross(P,Q),p.w*q.w-dot(P,Q));
}

vec2 rotate_v(vec2 p, float t) {
  return cos(t)*p + sin(t)*vec2(-p.y,p.x);
}

vec4 transform4(vec3 p3) {
  float time = TIME * speed;
  vec4 p = vec4(p3,0);
  p.w += 1.0;
  p *= 2.0/dot(p,p);
  p.w -= 1.0;
  float k = 0.1*PI*time;
  vec3 axis = vec3(0,0,-1);
  p = qmul_b(p,vec4(sin(k)*axis,cos(k)));
  p.xz = rotate_v(p.xz,0.55);
  return p;
}

float Barth(vec4 p, float K) {
  vec4 p2 = p*p;
  vec3 t = phi2*p2.xyz-p2.yzx;
  float A = 4.0*t.x*t.y*t.z;
  float B = dot(p2.xyz,vec3(1))-p2.w;
  return (1.0-K)*(1.0+2.0*phi)*p2.w*B*B - K*A;
}

float Fun(vec3 p3) {
  vec4 p = transform4(p3);
  return Barth(p, 0.5);
}

vec3 getColor(vec3 r, vec3 n) {
  return smoothstep(0.0,1.0,abs(n));
}

const int iterations = 200;
const float maxincrease = 1.03;
const float maxstep_v = 2.0;
const float minstep = 0.001;
const float initstep = 0.1;
const float maxdist = 20.0;
const float ambient_v = 0.5;
const float diffuse_v = 0.5;
float specpower = 4.0;

vec3 solve(vec3 p0, vec3 r) {
  float st = initstep;
  vec3 color = vec3(0);
  vec3 p = p0;
  float t0 = 0.0, t1;
  float f0 = Fun(p), f1;
  bool bracketed = false;
  for (int i = 0; i < iterations; i++) {
    t1 = t0 + st;
    if (t1 > maxdist) return color;
    p = p0 + t1*r;
    f1 = Fun(p);
    if (f0*f1 <= 0.0) {
      bracketed = true;
      break;
    } else {
      float st0 = st;
      st = f1*st/(f0-f1);
      if (st < 0.0) st = 1.0;
      st = abs(st);
      st = min(st,t1*maxstep_v);
      st = max(st,minstep);
      st = min(st,maxincrease*st0);
      t0 = t1; f0 = f1;
    }
  }
  if (!bracketed) return color;
  for (int i = 0; i < 10; i++) {
    if ((t1-t0)/t0 < minstep) break;
    float t2 = (t0 + t1)/2.0;
    p = p0+t2*r;
    float f2 = Fun(p);
    if (f0*f2 <= 0.0) { t1 = t2; f1 = f2; }
    else { t0 = t2; f0 = f2; }
  }

  float eps = 1e-3;
  vec2 delta = max(t0,1.0)*vec2(eps,0.0);
  p = p0 + t0*r;
  vec3 n = vec3(Fun(p + delta.xyy), Fun(p + delta.yxy), Fun(p + delta.yyx)) - f0;
  n = normalize(n);
  if (dot(r,n) > 0.0) n *= -1.0;
  vec3 baseColor = getColor(r,n);
  color = baseColor * ambient_v;
  float k = dot(light_v,n);
  if (k > 0.0) color += baseColor*diffuse_v*k;
  if (k > 0.0) {
    float specular = pow(max(0.0,dot(reflect(light_v,n),r)),specpower);
    color += 0.8*specular*vec3(1);
  }
  return color;
}

vec3 transform_cam(vec3 p) {
  float time = TIME * speed;
  float ph = time * 0.3;
  float theta = 0.3 * sin(time * 0.17);
  p.yz = rotate_v(p.yz,theta);
  p.zx = rotate_v(p.zx,-ph);
  return p;
}

void main() {
  light_v = vec3(0.5,1,1);
  float camera = 4.0;
  vec3 p = vec3(0,0,camera);
  p = transform_cam(p);
  light_v = transform_cam(light_v);
  light_v = normalize(light_v);
  vec2 uv = (2.0*gl_FragCoord.xy - RENDERSIZE.xy)/RENDERSIZE.y;
  vec3 r = normalize(vec3(uv,-2));
  r = transform_cam(r);
  r = normalize(r);
  vec3 color = solve(p,r);
  color = pow(color,vec3(0.4545));
  gl_FragColor = vec4(color,1);
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\Barth Sextic Surfaces'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'Barth Sextic Surfaces.fs'), 'w') as f:
    f.write(content2)
print('Written Barth Sextic Surfaces.fs')


# --- 9D Field via GPU Shader ---
content3 = r"""/*{
    "DESCRIPTION": "9D spinor field visualization with E8 lattice projection.",
    "CREDIT": "Whodacrunk / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.14159265359
#define E8_SCALE 8.0

vec2 e8Project(vec3 p){
    float ph = (1.0+sqrt(5.0))/2.0;
    mat3 proj = mat3(1.0,ph,ph, ph,1.0,ph, ph,ph,1.0)/(ph+2.0);
    return (proj*p).xy;
}

vec3 chiralSpinor(vec3 p, float t, vec3 audio){
    vec3 a = sin(p*E8_SCALE + t*vec3(1.0,1.618,3.14)*audio.x);
    vec3 b = cos(p*E8_SCALE*2.71 + t*vec3(2.71,1.0,1.618)*audio.y);
    float i = a.x*b.y - a.y*b.x;
    float j = a.y*b.z - a.z*b.y;
    float k = a.z*b.x - a.x*b.z;
    return normalize(vec3(i,j,k))*audio.z;
}

float fractalStrokes(vec2 uv, float t, vec3 audio){
    float sum=0.0, sc=1.0, amp=audio.y*1.5;
    for(int l=0;l<3;l++){
        for(int i=0;i<8;i++){
            float a = float(i)*PI/4.0 + t*0.2 + audio.x*11.5;
            vec2 c = sc*11.0*vec2(cos(a),sin(a));
            float tn = 1.0 + float(i)*2.71 + sin(t*1.618)/2.0;
            float d = length(uv-c);
            sum += exp(-pow((t-tn)*7.0,2.0))/(0.1+d)*amp;
            if(l<2){
                vec2 s = c + sc*0.3*vec2(cos(a*3.0),sin(a*3.0));
                sum += exp(-pow((t-tn-1.0/1.618)*11.0,2.71))/(1.05+length(uv-s))*amp*1.0/1.618;
            }
        }
        sc*=2.71; amp*=3.14;
    }
    return sum;
}

vec3 desaturate(vec3 col, float amount){
    float lum = dot(col, vec3(0.174, 0.528, 0.108));
    return mix(col, vec3(lum), amount);
}

void main(){
    float time = TIME * speed;
    vec2 uv = (gl_FragCoord.xy-0.5*RENDERSIZE)/min(RENDERSIZE.x,RENDERSIZE.y)*1.8;
    vec3 audio = vec3(0.5);
    vec3 p = mod(vec3(uv*3.14,time*0.28)+4.0,8.0)-8.0;
    vec3 spin = chiralSpinor(p,time,audio);
    vec2 proj = e8Project(p);
    float r = length(proj), theta = atan(proj.y,proj.x);
    float vortex = sin(8.0*theta + time*0.11 + r*11.0)*audio.x*2.71;
    float strokes = fractalStrokes(uv,time,audio);
    float psi = vortex*1.618+1.0 + strokes*1.618;
    vec3 field = spin*psi*0.5;

    vec3 col = vec3(
        sin(field.x*1.618 + time*2.71 + field.z*6.0),
        sin(field.y*3.14 + time*6.0 + field.x*10.0),
        sin(field.z*28.0 + time*2.71 + field.y*1.618)
    )*1.618;

    col = desaturate(col, 0.56);
    col *= cos(0.56) - 0.74*sin(length(uv)*11.83/3.14 - time*1.618 + field.x*1.83);
    col *= 0.618;
    gl_FragColor = vec4(col, 1.0);
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\9D Field via GPU Shader'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, '9D Field via GPU Shader.fs'), 'w') as f:
    f.write(content3)
print('Written 9D Field via GPU Shader.fs')

print('Batch 12 complete: 3 shaders written')
