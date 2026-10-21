import os

# --- Balls and Springs ---
# Image pass has all rendering (raymarching with SDF)
# Buffer A has physics simulation - replaced with procedural animation
# 8 balls in cube arrangement connected by 12 springs
# Replaced Loadv4 buffer reads with procedural ball positions
# Replaced mouse rotation with auto-rotation
# Removed iFrame, texture reads, iChannelResolution
# Renamed: nSpring arrays -> unrolled
content1 = r"""/*{
    "DESCRIPTION": "Elastic balls connected by springs in a rotating box.",
    "CREDIT": "dr2 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

mat3 QToRMat(vec4 q)
{
    mat3 m;
    float a1, a2, s;
    s = q.w * q.w - 0.5;
    m[0][0] = q.x * q.x + s;  m[1][1] = q.y * q.y + s;  m[2][2] = q.z * q.z + s;
    a1 = q.x * q.y;  a2 = q.z * q.w;  m[0][1] = a1 + a2;  m[1][0] = a1 - a2;
    a1 = q.x * q.z;  a2 = q.y * q.w;  m[2][0] = a1 + a2;  m[0][2] = a1 - a2;
    a1 = q.y * q.z;  a2 = q.x * q.w;  m[1][2] = a1 + a2;  m[2][1] = a1 - a2;
    return 2. * m;
}

float PrBoxDf(vec3 p, vec3 b){
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.) + length(max(d, 0.));
}

float PrSphDf(vec3 p, float s){
    return length(p) - s;
}

float PrCylEEDf(vec3 p, vec3 e1, vec3 e2, float r){
    vec3 u;
    p -= e1;
    u = e2 - e1;
    return length(p - clamp(dot(p, u) / dot(u, u), 0., 1.) * u) - r;
}

vec3 HsvToRgb(vec3 c){
    vec3 p;
    p = abs(fract(c.xxx + vec3(1., 2./3., 1./3.)) * 6. - 3.);
    return c.z * mix(vec3(1.), clamp(p - 1., 0., 1.), c.y);
}

const float pi_c = 3.14159;
const int nMol = 8;
const int nSpring = 12;
float dstFar, hbLen;
int idObj;

// Procedural ball positions replacing physics simulation
vec3 pMol[8];
vec3 pSpring0[24]; // 2 per spring = 24
float wSpring0[12];
vec3 rdSign;
vec3 ltDir;

vec3 getBallInitPos(int n) {
    float spLen = 1.5;
    float fme = 2.0;
    float fm = float(n);
    return spLen * floor(vec3(mod(fm, fme), mod(fm, fme*fme)/fme, fm/(fme*fme))) - 0.5*(fme-1.0);
}

vec3 getBallPos(int n, float time) {
    vec3 base = getBallInitPos(n);
    float fn = float(n);
    // Procedural oscillation around initial position
    float phase = fn * 1.7 + 0.3;
    vec3 offset = vec3(
        sin(time * 1.3 + phase) * 0.4,
        sin(time * 1.1 + phase * 1.5) * 0.3 - 0.2 * sin(time * 0.5),
        sin(time * 0.9 + phase * 0.7) * 0.35
    );
    return base + offset;
}

float ObjDf(vec3 p) {
    vec3 q, eLen, eShift;
    float dMin, d, eWid, sLen;
    dMin = dstFar;
    sLen = hbLen - 0.5;
    eWid = 0.04;
    eShift = vec3(0., sLen, sLen);
    eLen = vec3(sLen + eWid, eWid, eWid);
    vec4 fVec = sLen * vec4(rdSign, 0.);
    d = min(min(PrBoxDf(p - fVec.xww, eLen.yxx),
       PrBoxDf(p - fVec.wyw, eLen.xyx)), PrBoxDf(p - fVec.wwz, eLen.xxy));
    if (d < dMin) { dMin = d; idObj = 1; }
    q = abs(p);
    d = min(min(PrBoxDf(q - eShift, eLen), PrBoxDf(q - eShift.yxz, eLen.yxz)),
       PrBoxDf(q - eShift.yzx, eLen.yzx));
    if (d < dMin) { dMin = d; idObj = 2; }
    for (int n = 0; n < nSpring; n++) {
        d = PrCylEEDf(p, pSpring0[2*n], pSpring0[2*n+1], wSpring0[n]);
        if (d < dMin) { dMin = d; idObj = 3; }
    }
    for (int n = 0; n < nMol; n++) {
        d = PrSphDf(p - pMol[n], 0.45);
        if (d < dMin) { dMin = d; idObj = 10 + n; }
    }
    return dMin;
}

float ObjRay(vec3 ro, vec3 rd) {
    float dHit = 0., d;
    for (int j = 0; j < 100; j++) {
        d = ObjDf(ro + dHit * rd);
        dHit += d;
        if (d < 0.001 || dHit > dstFar) break;
    }
    return dHit;
}

vec3 ObjNf(vec3 p) {
    vec4 v;
    const vec3 e = vec3(0.0002, -0.0002, 0.);
    v = vec4(ObjDf(p + e.xxx), ObjDf(p + e.xyy),
       ObjDf(p + e.yxy), ObjDf(p + e.yyx));
    return normalize(vec3(v.x - v.y - v.z - v.w) + 2. * v.yzw);
}

float ObjAO(vec3 ro, vec3 rd) {
    float ao = 0., d;
    for (int j = 0; j < 5; j++) {
        d = 0.1 + float(j) / 8.;
        ao += max(0., d - 3. * ObjDf(ro + rd * d));
    }
    return 0.3 + 0.7 * clamp(1. - 0.1 * ao, 0., 1.);
}

vec3 ShowScene(vec3 ro, vec3 rd) {
    vec4 objCol;
    vec3 col, vn, w;
    float dstHit, ao;
    int idObjT;
    idObj = -1;
    rdSign = sign(rd);
    dstHit = ObjRay(ro, rd);
    if (idObj < 0) dstHit = dstFar;
    if (dstHit < dstFar) {
        ro += rd * dstHit;
        idObjT = idObj;
        vn = ObjNf(ro);
        idObj = idObjT;
        if (idObj == 1) {
            w = smoothstep(0., 0.1, abs(fract(1.95 * ro + 0.5) - 0.5));
            objCol = vec4(mix(vec3(0.5, 0.5, 0.2), vec3(0.4, 0.4, 1.),
               dot(abs(vn) * w.yzx * w.zxy, vec3(1.))), 0.4);
        } else if (idObj == 2) objCol = vec4(0.5, 0.5, 0.2, 0.4);
        else if (idObj == 3) objCol = vec4(0.7, 0.6, 0.6, 1.);
        else objCol = vec4(HsvToRgb(vec3(float(idObj - 10) / float(nMol), 1., 1.)), 1.);
        ao = ObjAO(ro, vn);
        col = objCol.rgb * (0.4 + 0.6 * ao * max(dot(vn, ltDir), 0.)) +
           objCol.a * ao * pow(max(0., dot(ltDir, reflect(rd, vn))), 128.);
    } else col = vec3(0., 0.1, 0.);
    return clamp(col, 0., 1.);
}

void GetMols(float time) {
    // Spring pair indices (unrolled)
    // 0-1, 0-2, 1-3, 2-3, 4-5, 4-6, 5-7, 6-7, 0-4, 1-5, 2-6, 3-7
    int mp0[12]; int mp1[12];
    mp0[0]=0; mp1[0]=1; mp0[1]=0; mp1[1]=2; mp0[2]=1; mp1[2]=3;
    mp0[3]=2; mp1[3]=3; mp0[4]=4; mp1[4]=5; mp0[5]=4; mp1[5]=6;
    mp0[6]=5; mp1[6]=7; mp0[7]=6; mp1[7]=7; mp0[8]=0; mp1[8]=4;
    mp0[9]=1; mp1[9]=5; mp0[10]=2; mp1[10]=6; mp0[11]=3; mp1[11]=7;

    for (int n = 0; n < nMol; n++) pMol[n] = getBallPos(n, time);
    hbLen = 3.0;
    float spLen = 1.5;
    for (int n = 0; n < nSpring; n++) {
        pSpring0[2*n] = pMol[mp0[n]];
        pSpring0[2*n+1] = pMol[mp1[n]];
        float sd = length(pSpring0[2*n+1] - pSpring0[2*n]) / spLen;
        wSpring0[n] = clamp(0.2 * (1. - sd * sd), 0.05, 0.2);
    }
}

void main() {
    float time = TIME * speed;
    vec2 canvas = RENDERSIZE.xy;
    vec2 uv = 2. * gl_FragCoord.xy / canvas - 1.;
    uv.x *= canvas.x / canvas.y;

    vec3 col;
    vec2 ut = abs(uv) - vec2(1.);
    if (max(ut.x, ut.y) > 0.003) col = vec3(0.82);
    else {
        dstFar = 100.;

        // Auto-rotating view quaternion
        vec3 euler = 0.2 * time * pi_c * vec3(0.27, 0.34, 0.11);
        float a1 = 0.5 * euler.y;
        float a2 = 0.5 * (euler.x - euler.z);
        float a3 = 0.5 * (euler.x + euler.z);
        float s1 = sin(a1); float c1 = cos(a1);
        vec4 qtVu = normalize(vec4(s1*cos(a2), s1*sin(a2), c1*sin(a3), c1*cos(a3)));

        mat3 vuMat = QToRMat(qtVu);
        vec3 rd = normalize(vec3(uv, 8.)) * vuMat;
        vec3 ro = vec3(0., 0., -35.) * vuMat;
        ltDir = normalize(vec3(1., 1.5, -1.2)) * vuMat;
        GetMols(time);
        col = ShowScene(ro, rd);
    }
    gl_FragColor = vec4(col, 1.);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Balls and Springs'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Balls and Springs.fs'), 'w') as f:
    f.write(content1)
print('Written Balls and Springs.fs')
print('Batch 21 complete: 1 shader written')
