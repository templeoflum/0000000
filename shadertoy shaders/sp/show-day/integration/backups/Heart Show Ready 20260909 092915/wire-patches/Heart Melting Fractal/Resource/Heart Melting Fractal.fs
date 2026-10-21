/*{
  "IMPORTED": [],
  "CATEGORIES": [
    "Automatically Converted",
    "Shadertoy"
  ],
  "DESCRIPTION": "Heart Melting Fractal: phase-driven folds, orthogonal rotations and fixed source camera. Original preserved.",
  "INPUTS": [
    {
      "NAME": "animSpeed",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Fold Phase"
    },
    {
      "NAME": "rotMix",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Twist Amount"
    },
    {
      "NAME": "orbitSpeed",
      "TYPE": "float",
      "DEFAULT": 0.333,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Orbit Phase"
    },
    {
      "NAME": "camRoll",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Camera Roll"
    },
    {
      "NAME": "coneRadius",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Cone Radius"
    },
    {
      "NAME": "foldOffset",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Fold Offset"
    },
    {
      "NAME": "glowStrength",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0,
      "LABEL": "Glow Strength"
    }
  ],
  "ISFVSN": "2",
  "PASSES": [
    {}
  ]
}*/

#define AA 1
#define MIN_DIST 0.001
#define MAX_DIST 50.
#define PI 3.141592653589793
#define TAU 6.283185307179586

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0))
        + min(max(d.x, max(d.y, d.z)), 0.0);
}

float sdRoundCone(in vec3 p, in float r1, float r2, float h, float coneRad) {
    vec2 q = vec2(length(p.xz), p.y);
    float b = (r1 - r2) / h;
    float a = sqrt(1.0 - b * b);
    float k = dot(q, vec2(-b, a));
    if(k < 0.0) return length(q) - r1 + coneRad;
    if(k > a * h) return length(q - vec2(0.0, h)) - r2;
    return dot(q, vec2(a, b)) - r1;
}

float opUnion(float d1, float d2) { return min(d1, d2); }
vec2 opUnion(vec2 d1, vec2 d2) { return d1.x < d2.x ? d1 : d2; }
vec3 opSymXYZ(vec3 p) { return abs(p); }

float easeInOutQuad(float t) {
    if ((t *= 2.0) < 1.0) return 0.5 * t * t;
    else return -0.5 * ((t - 1.0) * (t - 3.0) - 1.0);
}

mat3 rotate3D(float angle, vec3 axis, float rMix) {
    vec3 a = normalize(axis);
    angle *= 1.0 + rMix;
    float s = sin(angle);
    float c = cos(angle);
    float r = 1.0 - c;
    return mat3(
        a.x * a.x * r + c,
        a.y * a.x * r + a.z * s,
        a.z * a.x * r - a.y * s,
        a.x * a.y * r - a.z * s,
        a.y * a.y * r + c,
        a.z * a.y * r + a.x * s,
        a.x * a.z * r + a.y * s,
        a.y * a.z * r - a.x * s,
        a.z * a.z * r + c
    );
}

void mengerFold(inout vec3 z) {
    float a = min(z.x - z.y, 0.0); z.x -= a; z.y += a;
    a = min(z.x - z.z, 0.0); z.x -= a; z.z += a;
    a = min(z.y - z.z, 0.0); z.y -= a; z.z += a;
}

void boxFold(inout vec3 z, vec3 r, float fo) {
    z.xyz = clamp(z.xyz, -r, r) * 2.0 + fo - z.xyz;
}

float glow = 0.;

vec2 sceneSDF(vec3 p, float aSpeed, float rMix, float fo, float coneRad) {
    float t = TIME * .0 + aSpeed;
    t = easeInOutQuad(mod(t, 1.));
    vec2 d = vec2(10e5, 0);

    for(int i = 0; i < 5; i++) {
        p = opSymXYZ(p);
        mengerFold(p);
        boxFold(p, vec3(.5), fo);
        p.x -= .2;
        p *= rotate3D(t * TAU, vec3(1, 1, 0), rMix);
        p *= .95;
        p *= rotate3D(-t * TAU, vec3(0, 1, 1), rMix);

        float dd = sdRoundCone(p, 1.6, .1, 1.6, coneRad);
        if(i == 3) glow += 0.006 / (0.01 + dd * dd * 5.) / (float(AA * AA) * 10.);
    }
    d = opUnion(d, vec2(sdBox(p, vec3(.8, .1, .1)), 2.));
    return d;
}

mat3 setCamera(in vec3 ro, in vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = normalize(cross(cu, cw));
    return mat3(cu, cv, cw);
}

vec2 castRay(in vec3 ro, in vec3 rd, float aSpeed, float rMix, float fo, float coneRad) {
    float t = MIN_DIST;
    float m = -1.0;
    for(int i = 0; i < 100; i++) {
        float precis = 0.0005 * t;
        vec2 res = sceneSDF(ro + rd * t, aSpeed, rMix, fo, coneRad);
        if(res.x < precis){m=res.y;break;}
        if(t > MAX_DIST)break;
        t += max(res.x * 0.8, MIN_DIST);
    }
    if(t > MAX_DIST) m = -1.0;
    return vec2(t, m);
}

float softshadow(in vec3 ro, in vec3 rd, in float mint, in float tmax, float aSpeed, float rMix, float fo, float coneRad) {
    float res = 1.0;
    float t = mint;
    for(int i = 0; i < 16; i++) {
        float h = sceneSDF(ro + rd * t, aSpeed, rMix, fo, coneRad).x;
        res = min(res, 8.0 * h / t);
        t += clamp(h, 0.02, 0.10);
        if(h < 0.001 || t > tmax) break;
    }
    return clamp(res, 0.0, 1.0);
}

vec3 calcNormal(in vec3 pos, float aSpeed, float rMix, float fo, float coneRad) {
    vec2 e = vec2(1.0, -1.0) * 0.5773 * 0.0005;
    return normalize(
        e.xyy * sceneSDF(pos + e.xyy, aSpeed, rMix, fo, coneRad).x +
        e.yyx * sceneSDF(pos + e.yyx, aSpeed, rMix, fo, coneRad).x +
        e.yxy * sceneSDF(pos + e.yxy, aSpeed, rMix, fo, coneRad).x +
        e.xxx * sceneSDF(pos + e.xxx, aSpeed, rMix, fo, coneRad).x
    );
}

float calcAO(in vec3 pos, in vec3 nor, float aSpeed, float rMix, float fo, float coneRad) {
    float occ = 0.0;
    float sca = 1.0;
    for(int i = 0; i < 5; i++) {
        float hr = 0.01 + 0.12 * float(i) / 4.0;
        vec3 aopos = nor * hr + pos;
        float dd = sceneSDF(aopos, aSpeed, rMix, fo, coneRad).x;
        occ += -(dd - hr) * sca;
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

vec3 computeColor(vec3 ro, vec3 rd, vec3 pos, float d, float m, float aSpeed, float rMix, float fo, float coneRad) {
    vec3 nor = calcNormal(pos, aSpeed, rMix, fo, coneRad);
    vec3 ref = reflect(rd, nor);
    vec3 col = vec3(202, 82, 68) / 255.;
    float occ = calcAO(pos, nor, aSpeed, rMix, fo, coneRad);
    vec3 lig = normalize(vec3(-0.4, 0.7, -0.6));
    float amb = clamp(0.5 + 0.5 * nor.y, 0.0, 1.0);
    float dif = clamp(dot(nor, lig), 0.0, 1.0);
    float bac = clamp(dot(nor, normalize(vec3(-lig.x, 0.0, -lig.z))), 0.0, 1.0) * clamp(1.0 - pos.y, 0.0, 1.0);
    float dom = smoothstep(-0.1, 0.1, ref.y);
    float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 2.0);
    float spe = pow(clamp(dot(ref, lig), 0.0, 1.0), 16.0);
    dif *= softshadow(pos, lig, 0.02, 2.5, aSpeed, rMix, fo, coneRad);
    dom *= softshadow(pos, ref, 0.02, 2.5, aSpeed, rMix, fo, coneRad);
    vec3 lin = vec3(0.0);
    lin += 1.30 * dif * vec3(1.00, 0.80, 0.55);
    lin += 2.00 * spe * vec3(1.00, 0.90, 0.70) * dif;
    lin += 0.40 * amb * vec3(0.40, 0.60, 1.00) * occ;
    lin += 0.50 * dom * vec3(0.40, 0.60, 1.00) * occ;
    lin += 0.50 * bac * vec3(0.25, 0.25, 0.25) * occ;
    lin += 0.25 * fre * vec3(1.00, 1.00, 1.00) * occ;
    col = col * lin;
    return col;
}

vec3 render(in vec3 ro, in vec3 rd, float aSpeed, float rMix, float fo, float coneRad) {
    vec2 res = castRay(ro, rd, aSpeed, rMix, fo, coneRad);
    float distance = res.x;
    float materialID = res.y;
    if(materialID < 0.0) return vec3(-1.0);
    vec3 pos = ro + distance * rd;
    return vec3(clamp(computeColor(ro, rd, pos, distance, materialID, aSpeed, rMix, fo, coneRad), 0.0, 1.0));
}

vec3 effect(vec3 c) {
    c += glow * vec3(242, 223, 126) / 255.;
    return c;
}

void main() {
    glow = 0.;

    // remap all 0-1 inputs to their actual ranges
    float aSpeed    = animSpeed;                    // 0-1, used directly
    float rMix      = mix(-1.0, 1.0, rotMix);      // -1 to 1
    float oSpeed    = mix(0.0, 3.0, orbitSpeed);   // 0 to 3
    float cRoll     = mix(0.0, 10.0, camRoll);     // 0 to 10
    float coneRad   = mix(-5.0, 5.0, coneRadius);  // -5 to 5
    float fo        = mix(-0.4, -0.2, foldOffset); // -1 to 0.18
    float cDist     = 3.0;     // 0.5 to 10
    float gStrength = mix(1.0, 100.0, glowStrength); // 1 to 100

    vec3 ro = vec3(-5, 2.5, -6) * cDist * rotate3D(TIME * .0 + oSpeed * TAU, vec3(0, 1, 0), rMix);
    vec3 ta = vec3(0.0);
    mat3 ca = setCamera(ro, ta, cRoll);
    vec3 color = vec3(0.0);
    bool isBg = false;

    #if AA>1
    for(int m = 0; m < AA; m++)
        for(int n = 0; n < AA; n++) {
            vec2 o = vec2(float(m), float(n)) / float(AA) - 0.5;
            vec2 p = (-RENDERSIZE.xy + 2.0 * (gl_FragCoord.xy + o)) / min(RENDERSIZE.x, RENDERSIZE.y);
    #else
            vec2 p = (-RENDERSIZE.xy + 2.0 * gl_FragCoord.xy) / min(RENDERSIZE.x, RENDERSIZE.y);
    #endif
            vec3 rd = ca * normalize(vec3(p.xy, 2.0));
            vec3 col = render(ro, rd, aSpeed, rMix, fo, coneRad);
            isBg = col.r < 0.0;
            if(isBg) col = vec3(0.0);
            color += col;
    #if AA>1
        }
    color /= float(AA * AA);
    #endif

    color += glow * (0.25 + 2.0*glowStrength) * vec3(242,223,126)/255.;
    color=pow(clamp(color,0.0,1.0),vec3(1.0/2.2));

    if(isBg) {
        float glowAlpha = clamp(glow * gStrength, 0.0, 1.0);
        gl_FragColor = vec4(0.0);
        return;
    }

    gl_FragColor = vec4(color, 1.0);
}