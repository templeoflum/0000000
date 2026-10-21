import os

# --- 4-space rotations ---
# D4 Coxeter group, bitwise ops replaced with arithmetic,
# keyboard/mouse replaced with auto-animation
content1 = r"""/*{
    "DESCRIPTION": "4D Coxeter group rotations visualized via stereographic projection.",
    "CREDIT": "Matthew Arcus / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

// D4 Coxeter group
const int PQ = 3, QR = 3, RS = 2;
const int PS = 2, QS = 3, RP = 2;
const int NFOLDS = 4;

const float rotationtime = 2.0;
const float pausetime = 1.0;
const int starttime = 0;
const float linescale = 1.5;
const float camera_d = 6.0;

#define POINTWIDTH 0.04
#define EDGEWIDTH 0.02
#define MAXDIST 20.0
#define NSTEPS 200
#define MAXSTEP 0.5
#define FFACTOR 0.75
#define PRECISION 0.001
#define PI 3.141592654

bool eq_f(float a, float b) { return abs(a-b) < 1e-4; }
bool eq_v3(vec3 a, vec3 b) { return eq_f(a.x,b.x) && eq_f(a.y,b.y) && eq_f(a.z,b.z); }
bool eq_v4(vec4 a, vec4 b) { return eq_f(a.x,b.x) && eq_f(a.y,b.y) && eq_f(a.z,b.z) && eq_f(a.w,b.w); }

vec4 qmul(vec4 p, vec4 q) {
  vec3 P = p.xyz, Q = q.xyz;
  return vec4(p.w*Q+q.w*P+cross(P,Q), p.w*q.w-dot(P,Q));
}
vec4 qconj(vec4 p) { return vec4(-p.xyz,p.w); }

vec4 applyreflection(vec4 pl, vec4 x) {
  return -qmul(pl,qmul(qconj(x),pl))/dot(pl,pl);
}
vec4 applyrotation(vec4 p, vec4 x, vec4 q) {
  return qmul(p,qmul(x,q));
}
float facecosine(int x) { return -cos(PI/float(x)); }

vec4 istereographic(vec3 p, out float k) {
  k = 2.0/(1.0+dot(p,p));
  return vec4(k*p, k-1.0);
}

vec4 closest_v(vec4 p, vec4 a, vec4 b) {
  p -= a; b -= a;
  float h = dot(p,b)/dot(b,b);
  h = clamp(h,0.0,1.0);
  return a + h*b;
}

float sdist_2(vec4 p, vec4 q) { return length(p-q); }
float sdist_3(vec4 p, vec4 q, vec4 r) {
  return sdist_2(p, normalize(closest_v(p,q,r)));
}

vec4 slerp_v(vec4 p, float t) {
  if (p == vec4(0,0,0,1)) return p;
  if (p.w < 0.0) p = -p;
  float alpha = acos(p.w);
  float theta = t*alpha;
  vec4 r = vec4(sin(theta)*p.xyz, cos(theta)*sin(alpha));
  return normalize(r);
}

vec2 rotate_v(in vec2 p, in float t) {
  return p * cos(-t) + vec2(p.y, -p.x) * sin(-t);
}

// mat2 inverse
mat2 inv2(mat2 m) {
  float d = m[0][0]*m[1][1] - m[0][1]*m[1][0];
  return mat2(m[1][1], -m[0][1], -m[1][0], m[0][0]) / d;
}

// mat3 inverse
mat3 inv3(mat3 m) {
  vec3 a = m[0], b = m[1], c = m[2];
  vec3 r0 = cross(b, c);
  vec3 r1 = cross(c, a);
  vec3 r2 = cross(a, b);
  float d = dot(a, r0);
  return mat3(
    r0.x/d, r1.x/d, r2.x/d,
    r0.y/d, r1.y/d, r2.y/d,
    r0.z/d, r1.z/d, r2.z/d
  );
}

// mat4 inverse via cofactor expansion
mat4 inv4(mat4 m) {
  float s0 = m[0][0]*m[1][1] - m[1][0]*m[0][1];
  float s1 = m[0][0]*m[1][2] - m[1][0]*m[0][2];
  float s2 = m[0][0]*m[1][3] - m[1][0]*m[0][3];
  float s3 = m[0][1]*m[1][2] - m[1][1]*m[0][2];
  float s4 = m[0][1]*m[1][3] - m[1][1]*m[0][3];
  float s5 = m[0][2]*m[1][3] - m[1][2]*m[0][3];
  float c5 = m[2][2]*m[3][3] - m[3][2]*m[2][3];
  float c4 = m[2][1]*m[3][3] - m[3][1]*m[2][3];
  float c3 = m[2][1]*m[3][2] - m[3][1]*m[2][2];
  float c2 = m[2][0]*m[3][3] - m[3][0]*m[2][3];
  float c1 = m[2][0]*m[3][2] - m[3][0]*m[2][2];
  float c0 = m[2][0]*m[3][1] - m[3][0]*m[2][1];
  float invdet = 1.0/(s0*c5 - s1*c4 + s2*c3 + s3*c2 - s4*c1 + s5*c0);
  mat4 r;
  r[0][0] = ( m[1][1]*c5 - m[1][2]*c4 + m[1][3]*c3) * invdet;
  r[0][1] = (-m[0][1]*c5 + m[0][2]*c4 - m[0][3]*c3) * invdet;
  r[0][2] = ( m[3][1]*s5 - m[3][2]*s4 + m[3][3]*s3) * invdet;
  r[0][3] = (-m[2][1]*s5 + m[2][2]*s4 - m[2][3]*s3) * invdet;
  r[1][0] = (-m[1][0]*c5 + m[1][2]*c2 - m[1][3]*c1) * invdet;
  r[1][1] = ( m[0][0]*c5 - m[0][2]*c2 + m[0][3]*c1) * invdet;
  r[1][2] = (-m[3][0]*s5 + m[3][2]*s2 - m[3][3]*s1) * invdet;
  r[1][3] = ( m[2][0]*s5 - m[2][2]*s2 + m[2][3]*s1) * invdet;
  r[2][0] = ( m[1][0]*c4 - m[1][1]*c2 + m[1][3]*c0) * invdet;
  r[2][1] = (-m[0][0]*c4 + m[0][1]*c2 - m[0][3]*c0) * invdet;
  r[2][2] = ( m[3][0]*s4 - m[3][1]*s2 + m[3][3]*s0) * invdet;
  r[2][3] = (-m[2][0]*s4 + m[2][1]*s2 - m[2][3]*s0) * invdet;
  r[3][0] = (-m[1][0]*c3 + m[1][1]*c1 - m[1][2]*c0) * invdet;
  r[3][1] = ( m[0][0]*c3 - m[0][1]*c1 + m[0][2]*c0) * invdet;
  r[3][2] = (-m[3][0]*s3 + m[3][1]*s1 - m[3][2]*s0) * invdet;
  r[3][3] = ( m[2][0]*s3 - m[2][1]*s1 + m[2][2]*s0) * invdet;
  return r;
}

bool tryorthogonal(vec4 p, vec4 q, mat2 m, vec4 r, out vec4 result) {
  vec2 a = m*vec2(dot(r,p),dot(r,q));
  result = r - a[0]*p - a[1]*q;
  return dot(result,result) > 1e-3;
}

vec4 findorthogonal(vec4 p, vec4 q) {
  mat2 m = inv2(mat2(dot(p,p),dot(p,q),dot(p,q),dot(q,q)));
  vec4 result;
  if (tryorthogonal(p,q,m,vec4(1,0,0,0),result)) return result;
  else if (tryorthogonal(p,q,m,vec4(0,1,0,0),result)) return result;
  else if (tryorthogonal(p,q,m,vec4(0,0,1,0),result)) return result;
  return vec4(0);
}

void rotate4(vec4 p0, vec4 p1, vec4 q0, vec4 q2,
             out vec4 left, out vec4 right) {
  if (eq_v4(p0,p1)) {
    if (eq_v4(q0,q2)) {
      left = vec4(0,0,0,1); right = vec4(0,0,0,1); return;
    }
    vec4 t = p0; p0 = q0; q0 = t;
    t = p1; p1 = q2; q2 = t;
  }
  vec4 sv = p0-p1;
  vec4 q1 = applyreflection(sv,q0);
  vec4 tv = !eq_v4(q1,q2) ? q1-q2 : findorthogonal(p1,q2);
  left = normalize(qmul(tv,qconj(sv)));
  right = normalize(qmul(qconj(sv),tv));
}

// Global state
vec4 P = vec4(0), Q = vec4(0), R = vec4(0), S = vec4(0);
vec4 gp = vec4(0), gq = vec4(0), gr = vec4(0), gs = vec4(0);
vec4 point_v = vec4(0);
vec4 ppoint = vec4(0), qpoint = vec4(0);
vec4 rpoint = vec4(0), spoint = vec4(0);
vec4 qleft = vec4(0), qright = vec4(0);

int tryreflect(inout vec4 p, vec4 q) {
  float t = dot(p,q);
  if (t >= 0.0) return 0;
  p -= 2.0*t*q;
  return 1;
}

vec4 fold(vec4 p) {
  for (int i = 0; i < NFOLDS; i++) {
    p.x = abs(p.x);
    int k = tryreflect(p,Q);
    k += tryreflect(p,R);
    k += tryreflect(p,S);
    if (k == 0) break;
  }
  return p;
}

void solveangles(vec4 quad) {
  float A = facecosine(PQ);
  float B = facecosine(QR);
  float C = facecosine(RP);
  float D = facecosine(PS);
  float E = facecosine(QS);
  float F = facecosine(RS);
  P = vec4(1,0,0,0);
  float a = A;
  float b = sqrt(1.0 - a*a);
  Q = vec4(a,b,0,0);
  float c = C, d = (B-a*c)/b;
  float e = sqrt(1.0 - c*c - d*d);
  R = vec4(c,d,e,0);
  mat3 m3 = inv3(mat3(P.xyz,Q.xyz,R.xyz));
  // Need transpose: inv3 gives inverse, we need inverse of transpose
  // Original: mat3 m3 = inverse(transpose(mat3(P.xyz,Q.xyz,R.xyz)));
  // = (M^T)^-1 = (M^-1)^T
  // So: inv3(transpose(mat3(...)))
  // But let me just do: transpose of columns P,Q,R = rows P,Q,R
  // mat3(P.xyz,Q.xyz,R.xyz) has P.xyz as column 0
  // transpose of that has P.xyz as row 0
  // We want inverse of the transposed matrix
  // inv(M^T) = (inv(M))^T
  // So: transpose(inv3(mat3(P.xyz,Q.xyz,R.xyz)))
  // Actually, original code: inverse(transpose(mat3(P.xyz,Q.xyz,R.xyz)))
  // Let M = mat3(P.xyz,Q.xyz,R.xyz), then M^T has P as row0
  // inverse(M^T) = (M^-1)^T
  // I already computed m3 = inv3(M), so I need transpose(m3)
  // But wait - the result m3 is used as: vec3 S3 = m3*vec3(D,E,F)
  // In original: m3 = inverse(transpose(M)), S3 = m3 * vec3(D,E,F)
  // With my approach: m3_correct = transpose(inv3(M))
  // Hmm, this is getting confusing. Let me just recompute properly.

  // Original: inverse(transpose(mat3(P.xyz, Q.xyz, R.xyz)))
  // mat3(P.xyz, Q.xyz, R.xyz) = M where col0=P.xyz, col1=Q.xyz, col2=R.xyz
  // transpose(M) = M^T where row0=P.xyz, row1=Q.xyz, row2=R.xyz
  // inverse(M^T) solves M^T * x = b, i.e. x such that P.x*x0+P.y*x1+P.z*x2 = b0 etc.
  // = (M^-1)^T
  // So we need transpose of inv3(mat3(P.xyz,Q.xyz,R.xyz))

  // Recompute correctly:
  mat3 m3inv = inv3(mat3(P.xyz,Q.xyz,R.xyz));
  // We want inverse(transpose(M)) = transpose(inverse(M)) = transpose(m3inv)
  // But GLSL mat3 * vec3 does M*v (column vector), so:
  // transpose(m3inv) * vec3(D,E,F)
  // = vec3(dot(row0_of_transpose, DEF), ...) = vec3(dot(col0_of_m3inv, DEF), ...)
  // Actually: transpose(A) * v = A^T * v
  // But in GLSL, mat3 stores columns, so m3inv[0] is column 0
  // transpose(m3inv) has m3inv[0] as row 0 instead
  // GLSL doesn't have transpose... wait, it does. But I'm avoiding built-in transpose.
  // Let me just compute S3 manually:
  vec3 DEF = vec3(D,E,F);
  vec3 S3 = vec3(dot(m3inv[0], DEF), dot(m3inv[1], DEF), dot(m3inv[2], DEF));

  S = vec4(S3, sqrt(1.0 - dot(S3,S3)));

  // Solve for vertices: inverse(transpose(mat4(P,Q,R,S)))
  // Same approach: inv4(mat4(P,Q,R,S)) gives M^-1
  // inverse(M^T) = (M^-1)^T
  // Vertices are columns of (M^-1)^T = rows of M^-1
  mat4 m4inv = inv4(mat4(P,Q,R,S));
  // Columns of (M^-1)^T = rows of M^-1
  // Row i of m4inv = vec4(m4inv[0][i], m4inv[1][i], m4inv[2][i], m4inv[3][i])
  gp = normalize(vec4(m4inv[0][0], m4inv[1][0], m4inv[2][0], m4inv[3][0]));
  gq = normalize(vec4(m4inv[0][1], m4inv[1][1], m4inv[2][1], m4inv[3][1]));
  gr = normalize(vec4(m4inv[0][2], m4inv[1][2], m4inv[2][2], m4inv[3][2]));
  gs = normalize(vec4(m4inv[0][3], m4inv[1][3], m4inv[2][3], m4inv[3][3]));

  // Wythoff point
  // Original: point = normalize(m * quad) where m = inverse(transpose(M4))
  // m * quad: columns of m are rows of M^-1
  // So m * quad = sum of quad[i] * column_i_of_m = sum of quad[i] * row_i_of_M^-1
  // = transpose(M^-1) * quad
  vec4 pt = vec4(
    dot(vec4(m4inv[0][0],m4inv[0][1],m4inv[0][2],m4inv[0][3]), quad),
    dot(vec4(m4inv[1][0],m4inv[1][1],m4inv[1][2],m4inv[1][3]), quad),
    dot(vec4(m4inv[2][0],m4inv[2][1],m4inv[2][2],m4inv[2][3]), quad),
    dot(vec4(m4inv[3][0],m4inv[3][1],m4inv[3][2],m4inv[3][3]), quad)
  );
  point_v = normalize(pt);

  ppoint = normalize(point_v - dot(point_v,P)*P);
  qpoint = normalize(point_v - dot(point_v,Q)*Q);
  rpoint = normalize(point_v - dot(point_v,R)*R);
  spoint = normalize(point_v - dot(point_v,S)*S);
}

vec4 randomfold(vec4 p, int seed) {
  for (int i = 0; i < 8; i++) {
    int side = int(mod(float(seed), 4.0));
    seed = seed / 4;
    if (side == 0) p.x = -p.x;
    else if (side == 1) p -= 2.0*dot(p,Q)*Q;
    else if (side == 2) p -= 2.0*dot(p,R)*R;
    else p -= 2.0*dot(p,S)*S;
  }
  return p;
}

vec4 map_v(vec3 pos, out float k) {
  vec4 p4 = istereographic(pos,k);
  p4 = applyrotation(qleft,p4,qright);
  p4 = fold(p4);
  return p4;
}

float eval_v(vec3 pos) {
  float pwidth = POINTWIDTH*linescale;
  float ewidth = EDGEWIDTH*linescale;
  float k;
  vec4 p4 = map_v(pos,k);
  float d = 1e8;
  d = min(d, sdist_2(p4,point_v)-pwidth);
  d = min(d, sdist_3(p4,point_v,ppoint)-ewidth);
  d = min(d, sdist_3(p4,point_v,qpoint)-ewidth);
  d = min(d, sdist_3(p4,point_v,rpoint)-ewidth);
  d = min(d, sdist_3(p4,point_v,spoint)-ewidth);
  return d/k;
}

vec3 calcNormal_v(vec3 p, float t) {
  float eps = 0.002;
  vec2 e = vec2(eps, 0.0);
  return normalize(vec3(eval_v(p+e.xyy)-eval_v(p-e.xyy),
                        eval_v(p+e.yxy)-eval_v(p-e.yxy),
                        eval_v(p+e.yyx)-eval_v(p-e.yyx)));
}

float march_v(in vec3 ro, in vec3 rd) {
  float t = 0.25;
  for (int i = 0; i < NSTEPS; i++) {
    vec3 p = ro + rd * t;
    float d = eval_v(p);
    d *= FFACTOR;
    d = min(MAXSTEP, d);
    t += d;
    if (d < t*PRECISION) return t;
    if (t > MAXDIST) break;
  }
  return 1e8;
}

vec3 getcolor_v(vec3 pos) {
  float pwidth = POINTWIDTH*linescale;
  float ewidth = EDGEWIDTH*linescale;
  float k;
  vec4 p4 = map_v(pos,k);
  float d0, d = 1e8;
  int id = 0;
  d0 = sdist_2(p4,point_v)-pwidth;
  if (d0 < d) { d = d0; id = 1; }
  d0 = sdist_3(p4,point_v,ppoint)-ewidth;
  if (d0 < d) { d = d0; id = 2; }
  d0 = sdist_3(p4,point_v,qpoint)-ewidth;
  if (d0 < d) { d = d0; id = 3; }
  d0 = sdist_3(p4,point_v,rpoint)-ewidth;
  if (d0 < d) { d = d0; id = 4; }
  d0 = sdist_3(p4,point_v,spoint)-ewidth;
  if (d0 < d) { d = d0; id = 5; }
  if (id == 1) return vec3(0.02);
  if (id == 2) return vec3(1,0,0);
  if (id == 3) return vec3(0,1,0);
  if (id == 4) return vec3(0,0,1);
  if (id == 5) return vec3(1,1,0);
  return vec3(0);
}

void makequaternions_v(int seed) {
  float time = TIME * speed;
  vec4 p1 = randomfold(gp,seed);
  vec4 q1 = randomfold(gq,seed);
  vec4 r1 = randomfold(gr,seed);
  vec4 s1 = randomfold(gs,seed);
  vec4 left0, right0;
  rotate4(gp,p1,gq,q1,left0,right0);
  vec4 r0 = applyrotation(left0,gr,right0);
  vec4 s0 = applyrotation(left0,gs,right0);
  vec4 left1, right1;
  rotate4(r0,r1,s0,s1,left1,right1);
  qleft = qmul(left1,left0);
  qright = qmul(right0,right1);
  if (qleft.w < 0.0 && qright.w < 0.0) {
    qleft = -qleft;
    qright = -qright;
  }
  float t = mod(time, rotationtime+pausetime);
  t = min(t/rotationtime, 1.0);
  qleft = slerp_v(qleft, t);
  qright = slerp_v(qright, t);
}

vec3 transform_v(in vec3 p, bool dorotate) {
  float time = TIME * speed;
  float theta = 0.3 * sin(time * 0.15);
  p.yz = rotate_v(p.yz, -theta);
  if (dorotate) {
    p.zx = rotate_v(p.zx, time * 0.2);
  }
  return p;
}

vec3 ACESFilm2_v(vec3 color){
  mat3 m1 = mat3(
    0.59719, 0.07600, 0.02840,
    0.35458, 0.90834, 0.13383,
    0.04823, 0.01566, 0.83777);
  mat3 m2 = mat3(
    1.60475, -0.10208, -0.00327,
    -0.53108,  1.10813, -0.07276,
    -0.07367, -0.00605,  1.07602);
  vec3 v = m1 * color;
  vec3 a = v * (v + 0.0245786) - 0.000090537;
  vec3 b = v * (0.983729 * v + 0.4329510) + 0.238081;
  return pow(clamp(m2 * (a / b), 0.0, 1.0), vec3(1.0 / 2.2));
}

void main() {
  float time = TIME * speed;
  vec4 quad = vec4(1.0);
  solveangles(quad);
  int seed = starttime + int((time+30.0)/(rotationtime+pausetime));
  makequaternions_v(seed);
  vec2 screenpos = (2.0*gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
  vec3 ro = vec3(0,0,-camera_d);
  vec3 rd = vec3(screenpos,2.0);
  vec3 li = vec3(0.5, 0.8, -3.0);
  ro = transform_v(ro, true);
  rd = normalize(transform_v(rd, true));
  li = normalize(transform_v(li, true));
  float t = march_v(ro,rd);
  vec3 color = vec3(0);
  if (t < 1e8) {
    vec3 pos = ro + t*rd;
    vec3 n = calcNormal_v(pos,t);
    color = 0.5*getcolor_v(pos);
    float diffuse = clamp(dot(n, li), 0.0, 1.0);
    color *= diffuse;
    float specular = pow(max(0.0,dot(reflect(li,n),rd)), 4.0);
    color += 0.3*specular*vec3(1);
  }
  color = ACESFilm2_v(color);
  gl_FragColor = vec4(color, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\4-space rotations'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, '4-space rotations.fs'), 'w') as f:
    f.write(content1)
print('Written 4-space rotations.fs')

print('Batch 15 complete: 1 shader written')
