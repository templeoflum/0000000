/*{
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator",
    "Figure"
  ],
  "DESCRIPTION": "Corpus Pinna\u2013Brelstaff Figure. Fixed ring centers, opposing tile tilt, neutral circular plate. External Figure Transform supplies shared breathing; no real spin. Contrast retains at least55% source contrast.",
  "CREDIT": "Adapted from Donovan\u2019s corpus pinna-brelstaff.html; existing Heart Smart Params.",
  "INPUTS": [
    {
      "NAME": "heartRate",
      "LABEL": "Heart Rate (turns/s)",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 2.0
    },
    {
      "NAME": "pattern",
      "LABEL": "Pattern",
      "TYPE": "long",
      "DEFAULT": 11,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18
      ],
      "LABELS": [
        "per-slot",
        "unison",
        "near-unison",
        "harmonic",
        "just intonation",
        "septimal",
        "undecimal",
        "powers of 2",
        "powers of 3",
        "cross-base 2v3",
        "pendulum wave",
        "fibonacci",
        "lucas",
        "coprime primes",
        "prime stacks",
        "CF approximants",
        "metallic",
        "near-phi",
        "irrationals"
      ]
    },
    {
      "NAME": "seed",
      "LABEL": "Seed",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31
      ],
      "LABELS": [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31"
      ]
    },
    {
      "NAME": "spread",
      "LABEL": "Spread",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "LABELS": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8"
      ]
    },
    {
      "NAME": "depth",
      "LABEL": "Depth",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fm",
      "LABEL": "FM",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "shufTiming",
      "LABEL": "Shuffle Timing",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufPattern",
      "LABEL": "Shuffle Pattern",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufMotion",
      "LABEL": "Shuffle Motion",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufRange",
      "LABEL": "Shuffle Range",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufDrives",
      "LABEL": "Shuffle Drives",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufLook",
      "LABEL": "Shuffle Look",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufAll",
      "LABEL": "Shuffle All",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "tilt",
      "LABEL": "Tilt",
      "TYPE": "float",
      "DEFAULT": 0.5333333333333333,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "tiltDrive",
      "LABEL": "Tilt Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "tiltLock",
      "LABEL": "Tilt Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "tiltRatio",
      "LABEL": "Tilt Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "tiltMult",
      "LABEL": "Tilt Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "tiltOffset",
      "LABEL": "Tilt Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "tiltShape",
      "LABEL": "Tilt Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "tiltLo",
      "LABEL": "Tilt Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "tiltHi",
      "LABEL": "Tilt Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrast",
      "LABEL": "Contrast",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrastDrive",
      "LABEL": "Contrast Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "contrastLock",
      "LABEL": "Contrast Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "contrastRatio",
      "LABEL": "Contrast Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "contrastMult",
      "LABEL": "Contrast Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "contrastOffset",
      "LABEL": "Contrast Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrastShape",
      "LABEL": "Contrast Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "contrastLo",
      "LABEL": "Contrast Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrastHi",
      "LABEL": "Contrast Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/
// ─────────────────────────────────────────────────────────────────────────────
// sp.glsl v3 — SMART PARAM for ISF. Paste verbatim below the ISF header.
// Law (kit ratio.js):  φ = fract(H · m · r + o)
//   H heart turns · r ratio · m mult (sign = direction) · o offset · shape saw/cos.
// v3: the RATIO comes from a PATTERN — a catalog family as a GENERATOR of terms
//   (slot i gets term k = i·spread + seed). Families ordered tightest-sync → never-syncs.
//   depth crossfades manual↔driven (live fader). fm phase-modulates the phase (organic).
// Requires uniforms: pattern, seed, spread, depth, fm, shufTiming, shufPattern, shufMotion, shufRange, shufDrives, shufLook, shufAll.
// Precision: H split into whole+fraction; rationals use mod-q arithmetic → exact for days.
// ─────────────────────────────────────────────────────────────────────────────
#define SP_PHI 1.6180339887498949
#define SP_PI  3.1415926535897932
#define SP_E   2.7182818284590452

const float SP_PRIMES[32] = float[](2.,3.,5.,7.,11.,13.,17.,19.,23.,29.,31.,37.,41.,43.,47.,53.,59.,61.,67.,71.,73.,79.,83.,89.,97.,101.,103.,107.,109.,113.,127.,131.);

// per-slot library (pattern 0 = "per-slot": each slot's own Ratio dropdown)
//  0 1:1  1 1:2  2 1:4  3 2:3  4 3:4  5 4:5  6 5:6  7 3:5  8 1/φ  9 1/√2  10 1/π  11 1:3  12 2:5  13 5:8  14 8:13  15 3:2
vec2 spRatio(int i) {
    if (i == 1)  return vec2(1.0, 2.0);   if (i == 2)  return vec2(1.0, 4.0);   if (i == 3)  return vec2(2.0, 3.0);
    if (i == 4)  return vec2(3.0, 4.0);   if (i == 5)  return vec2(4.0, 5.0);   if (i == 6)  return vec2(5.0, 6.0);
    if (i == 7)  return vec2(3.0, 5.0);   if (i == 8)  return vec2(1.0/SP_PHI, -1.0); if (i == 9) return vec2(0.70710678118654752, -1.0);
    if (i == 10) return vec2(1.0/SP_PI, -1.0); if (i == 11) return vec2(1.0, 3.0); if (i == 12) return vec2(2.0, 5.0);
    if (i == 13) return vec2(5.0, 8.0);   if (i == 14) return vec2(8.0, 13.0);  if (i == 15) return vec2(3.0, 2.0);
    return vec2(1.0, 1.0);
}

// ── THE CATALOG as generators. family f, term k → (p,q); q<0 marks an irrational (p = value).
//  1 unison        2 near-unison (n+1):n     3 harmonic 1:n        4 just intonation   5 septimal
//  6 undecimal     7 powers of 2             8 powers of 3         9 cross-base 2^a/3^b 10 pendulum (8+k):8
// 11 fibonacci    12 lucas                  13 coprime primes 1:p 14 prime stacks p:p' 15 CF approximants
// 16 metallic 1/δn 17 near-φ cluster        18 pure irrationals
vec2 spTerm(int f, int k) {
    k = max(k, 0);
    if (f == 1) return vec2(1.0, 1.0);
    if (f == 2) { float n = 8.0 + float(k); return vec2(n + 1.0, n); }
    if (f == 3) return vec2(1.0, float(k + 1));
    if (f == 4) { int j = k - 12 * (k / 12);
        if (j==0) return vec2(1.,1.);   if (j==1) return vec2(16.,15.); if (j==2) return vec2(9.,8.);  if (j==3) return vec2(6.,5.);
        if (j==4) return vec2(5.,4.);   if (j==5) return vec2(4.,3.);   if (j==6) return vec2(45.,32.); if (j==7) return vec2(3.,2.);
        if (j==8) return vec2(8.,5.);   if (j==9) return vec2(5.,3.);   if (j==10) return vec2(15.,8.); return vec2(2.,1.); }
    if (f == 5) { int j = k - 10 * (k / 10);
        if (j==0) return vec2(7.,6.);   if (j==1) return vec2(7.,5.);   if (j==2) return vec2(7.,4.);  if (j==3) return vec2(8.,7.);
        if (j==4) return vec2(9.,7.);   if (j==5) return vec2(10.,7.);  if (j==6) return vec2(12.,7.); if (j==7) return vec2(14.,9.);
        if (j==8) return vec2(21.,16.); return vec2(49.,48.); }
    if (f == 6) { int j = k - 10 * (k / 10);
        if (j==0) return vec2(11.,8.);  if (j==1) return vec2(11.,6.);  if (j==2) return vec2(11.,7.); if (j==3) return vec2(11.,9.);
        if (j==4) return vec2(11.,10.); if (j==5) return vec2(13.,8.);  if (j==6) return vec2(13.,12.); if (j==7) return vec2(13.,7.);
        if (j==8) return vec2(13.,9.);  return vec2(13.,11.); }
    if (f == 7) return vec2(1.0, pow(2.0, float(k - 12 * (k / 12))));
    if (f == 8) return vec2(1.0, pow(3.0, float(k - 8 * (k / 8))));
    if (f == 9) { int a = 1 + k - 4 * (k / 4), b = 1 + (k / 4) - 3 * ((k / 4) / 3); return vec2(pow(2.0, float(a)), pow(3.0, float(b))); }
    if (f == 10) return vec2(8.0 + float(k), 8.0);
    if (f == 11) { float a = 1.0, b = 1.0; for (int n = 0; n < 24; n++) { if (n >= k) break; float c = a + b; a = b; b = c; } return vec2(a, b); }
    if (f == 12) { float a = 2.0, b = 1.0; for (int n = 0; n < 24; n++) { if (n >= k) break; float c = a + b; a = b; b = c; } return vec2(a, b); }
    if (f == 13) return vec2(1.0, SP_PRIMES[k - 32 * (k / 32)]);
    if (f == 14) { int j = k - 31 * (k / 31); return vec2(SP_PRIMES[j], SP_PRIMES[j + 1]); }
    if (f == 15) { int j = k - 10 * (k / 10);   // continued-fraction approximants of √2 and π (alternating)
        if (j==0) return vec2(3.,2.);   if (j==1) return vec2(22.,7.);  if (j==2) return vec2(7.,5.);   if (j==3) return vec2(333.,106.);
        if (j==4) return vec2(17.,12.); if (j==5) return vec2(355.,113.); if (j==6) return vec2(41.,29.); if (j==7) return vec2(103993.,33102.);
        if (j==8) return vec2(99.,70.); return vec2(239.,169.); }
    if (f == 16) { float n = 1.0 + float(k); float d = (n + sqrt(n * n + 4.0)) * 0.5; return vec2(1.0 / d, -1.0); }
    if (f == 17) return vec2((1.0 / SP_PHI) * (1.0 + 0.013 * float(k)), -1.0);
    if (f == 18) { int j = k - 9 * (k / 9);
        float v = 1.0 / SP_PHI; if (j==1) v = 0.70710678; if (j==2) v = 1.0 / SP_PI; if (j==3) v = 1.0 / SP_E; if (j==4) v = 0.57735027;
        if (j==5) v = 0.44721360; if (j==6) v = SP_PI / 4.0; if (j==7) v = SP_E / SP_PI; if (j==8) v = SP_PI / SP_E; return vec2(v, -1.0); }
    return vec2(1.0, 1.0);
}

// phase at heart H for ratio r=(p,q), mult m, offset o
float spPhase(float H, vec2 r, float m, float o) {
    float mm = (abs(m) < 1.0) ? sign(m + 1e-9) : m;
    float Hi = floor(H), Hf = H - Hi;
    if (r.y > 0.0) {   // rational: exact mod-q arithmetic for the whole-turn part
        float mi = floor(abs(mm) + 0.5); float mf = abs(mm) - mi;
        float whole = mod(Hi * mi * r.x, r.y) / r.y;
        float rest  = fract((Hi * mf + Hf * abs(mm)) * r.x / r.y);
        return fract(sign(mm) * (whole + rest) + o);
    }
    return fract(H * mm * r.x + o);   // irrational: free-running
}
float spShape(float ph, int shape) { return (shape == 1) ? 0.5 - 0.5 * cos(ph * 2.0 * SP_PI) : ph; }

// ── SHUFFLE: each category has a seed (a Counter bumped by a button; 0 = manual). Deterministic hashes → recallable.
float spHash(float seed, int slot, float salt) {
    return fract(sin(seed * 12.9898 + float(slot) * 78.233 + salt * 37.719) * 43758.5453);
}
float spCat(float cat) { return cat + 1000.0 * shufAll; }   // Shuffle All folds into every category

// THE smart param v4. lock = exclude this slot from all shuffles.
float sp(float manual, bool drive, bool lock, bool cyc, float H, int i, int ri, float m, float o, int shape, float lo, float hi) {
    // ── effective config (shuffles override unless locked / seed 0) ──
    int   pat = pattern;  int sd = seed;  int spr = spread;
    float sT = spCat(shufTiming), sP = spCat(shufPattern), sM = spCat(shufMotion), sR = spCat(shufRange), sD = spCat(shufDrives), sL = spCat(shufLook);
    if (sP > 0.0) pat = 1 + int(floor(spHash(sP, 0, 1.0) * 18.0));
    if (sT > 0.0) { sd = int(floor(spHash(sT, 0, 2.0) * 32.0)); spr = 1 + int(floor(spHash(sT, 0, 3.0) * 4.0)); }
    if (!lock) {
        if (sL > 0.0) manual = spHash(sL, i, 4.0);
        if (sD > 0.0) drive = drive && (spHash(sD, i, 5.0) > 0.45);
        if (sM > 0.0) {
            float hm = spHash(sM, i, 6.0);
            m = (hm < 0.35) ? 1.0 : (hm < 0.6) ? 2.0 : (hm < 0.75) ? 3.0 : (hm < 0.85) ? 4.0 : (hm < 0.95) ? -1.0 : -2.0;
            shape = (spHash(sM, i, 7.0) > 0.5) ? 1 : 0;
            o = spHash(sM, i, 8.0);
        }
        if (sR > 0.0) { lo = spHash(sR, i, 9.0) * 0.5; hi = min(1.0, lo + 0.3 + spHash(sR, i, 10.0) * 0.7); }
    }
    if (!drive) return manual;
    int k = i * spr + sd;
    vec2 r = (pat == 0) ? spRatio(ri) : spTerm(pat, k);
    float ph = spPhase(H, r, m, o);
    if (fm > 0.0) {
        vec2 rf = (pat == 0) ? spRatio(ri) : spTerm(pat, k + 1);
        float phf = spPhase(H, rf, 1.0, 0.37 * float(i));
        ph = fract(ph + fm * 0.25 * (0.5 - 0.5 * cos(phf * 2.0 * SP_PI)));
    }
    if (cyc) {
        if (shape == 0) return fract(manual + ph);
        return fract(manual + depth * (hi - lo) * (0.5 - 0.5 * cos(ph * 2.0 * SP_PI)));
    }
    float s = (shape == 0) ? 1.0 - abs(2.0 * ph - 1.0) : 0.5 - 0.5 * cos(ph * 2.0 * SP_PI);
    return mix(manual, mix(lo, hi, s), depth);
}
float spMap(float s, float outMin, float outMax) { return outMin + s * (outMax - outMin); }

// Scalar coverage avoids Wire's observed vec2 rectangle-helper width problem.
float pbSquare(float x,float y,float h,float aa){
 float left=smoothstep(-h-aa,-h+aa,x);
 float right=1.0-smoothstep(h-aa,h+aa,x);
 float top=smoothstep(-h-aa,-h+aa,y);
 float bottom=1.0-smoothstep(h-aa,h+aa,y);
 return left*right*top*bottom;
}
void main(){
 float H=TIME*heartRate;
 float tiltAngle=sp(tilt, tiltDrive, tiltLock, false, H, 0, tiltRatio, tiltMult, tiltOffset, tiltShape, tiltLo, tiltHi)*0.7853981633974483;
 float contrastAmount=0.55+0.45*sp(contrast, contrastDrive, contrastLock, false, H, 1, contrastRatio, contrastMult, contrastOffset, contrastShape, contrastLo, contrastHi);
 float shortSide=min(RENDERSIZE.x,RENDERSIZE.y);
 float px=(gl_FragCoord.x-.5*RENDERSIZE.x)/shortSide;
 float py=(.5*RENDERSIZE.y-gl_FragCoord.y)/shortSide;
 float aa=.5/shortSide;
 // Original short-side geometry reduced uniformly by .8 to reserve breathing room.
 float tileHalf=.028*.8;
 float strokeHalf=(1.5/800.0)*.8*.5;
 vec3 field=vec3(207,202,189)/255.0;
 vec3 ink=vec3(43,42,38)/255.0;
 vec3 paper=vec3(246,242,232)/255.0;
 vec3 rgb=field;
 float distanceFromCenter=sqrt(px*px+py*py);
 float alpha=1.0-smoothstep(.36-aa,.36+aa,distanceFromCenter);
 if(alpha<=0.0){gl_FragColor=vec4(0);return;}
 // Angular centers are invariant. No TIME-driven spin, zoom or independent ring phase.
 for(int ring=0;ring<2;ring++){
  int count=ring==0?21:30;
  float radius=ring==0?.22*.8:.37*.8;
  float direction=ring==0?1.0:-1.0;
  for(int i=0;i<30;i++){
   if(i>=count)break;
   float angle=6.283185307179586*float(i)/float(count);
   float cx=cos(angle)*radius;
   float cy=sin(angle)*radius;
   float orientation=angle+1.5707963267948966+direction*tiltAngle;
   float ca=cos(orientation),sa=sin(orientation);
   float dx=px-cx,dy=py-cy;
   float localX=ca*dx+sa*dy;
   float localY=-sa*dx+ca*dy;
   float fill=pbSquare(localX,localY,tileHalf,aa);
   float outer=pbSquare(localX,localY,tileHalf+strokeHalf,aa);
   float inner=pbSquare(localX,localY,tileHalf-strokeHalf,aa);
   float stroke=clamp(outer-inner,0.0,1.0);
   bool dark=(i-2*(i/2))==0;
   vec3 fillColor=mix(field,dark?ink:paper,contrastAmount);
   vec3 strokeColor=mix(field,dark?paper:ink,contrastAmount);
   rgb=mix(rgb,fillColor,fill);
   rgb=mix(rgb,strokeColor,stroke);
  }
 }
 // Original 16px-wide fixation cross scaled with the contained stimulus.
 float horizontal=pbSquare(px,py,.008,aa);
 float thinHorizontal=1.0-smoothstep(.001-aa,.001+aa,abs(py));
 float thinVertical=1.0-smoothstep(.001-aa,.001+aa,abs(px));
 float crossMask=horizontal*max(thinHorizontal,thinVertical);
 rgb=mix(rgb,vec3(184,96,58)/255.0,crossMask);
 gl_FragColor=vec4(rgb,alpha);
}
