/*{
  "DESCRIPTION": "Heart bounded Figure source. Shared Figure Transform owns size and placement. Raymarched spikeball with symmetry directions.",
  "CREDIT": "Patapom / Shadertoy",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "speed",
      "LABEL": "Speed",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 3.0
    },
    {
      "NAME": "quatW",
      "LABEL": "Quat W",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatX",
      "LABEL": "Quat X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatY",
      "LABEL": "Quat Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "quatZ",
      "LABEL": "Quat Z",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "spikeSharp",
      "LABEL": "Spike Sharpness",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

mat3 quatToMat(vec4 q) {
    float q2 = dot(q,q);
    q = q2 > 1e-10 ? q * inversesqrt(q2) : vec4(0.0,0.0,0.0,1.0);
    float xx = q.x*q.x, yy = q.y*q.y, zz = q.z*q.z;
    float xy = q.x*q.y, xz = q.x*q.z, yz = q.y*q.z;
    float wx = q.w*q.x, wy = q.w*q.y, wz = q.w*q.z;
    return mat3(
        1.0 - 2.0*(yy+zz), 2.0*(xy+wz),     2.0*(xz-wy),
        2.0*(xy-wz),        1.0 - 2.0*(xx+zz), 2.0*(yz+wx),
        2.0*(xz+wy),        2.0*(yz-wx),     1.0 - 2.0*(xx+yy)
    );
}

float spikeball(vec3 p, float t) {
    vec3 c[19];
    c[0] = vec3(1,0,0); c[1] = vec3(0,1,0); c[2] = vec3(0,0,1);
    c[3] = vec3(.577,.577,.577); c[4] = vec3(-.577,.577,.577);
    c[5] = vec3(.577,-.577,.577); c[6] = vec3(.577,.577,-.577);
    c[7] = vec3(0,.357,.934); c[8] = vec3(0,-.357,.934);
    c[9] = vec3(.934,0,.357); c[10] = vec3(-.934,0,.357);
    c[11] = vec3(.357,.934,0); c[12] = vec3(-.357,.934,0);
    c[13] = vec3(0,.851,.526); c[14] = vec3(0,-.851,.526);
    c[15] = vec3(.526,0,.851); c[16] = vec3(-.526,0,.851);
    c[17] = vec3(.851,.526,0); c[18] = vec3(-.851,.526,0);
    float MinDistance = 9999.0;
    float sharpBase = mix(0.8, 2.5, spikeSharp);
    for (int i = 3; i < 19; i++) {
        float d = clamp(dot(p, c[i]), -1.0, 1.0);
        vec3 proj = d * c[i];
        d = abs(d);
        float Distance2Spike = length(p - proj);
        float sd = sharpBase + 0.6 * sin(t * 8.0);
        float SpikeThickness = 0.1 * exp(-sd * d);
        float Distance = Distance2Spike - SpikeThickness;
        MinDistance = min(MinDistance, Distance);
    }
    return MinDistance;
}

float Distance(vec3 p, float t) {
    return spikeball(p, t);
}

void main() {
    float t = TIME * speed * 0.1;
    vec2 uv = (2.0 * gl_FragCoord.xy - RENDERSIZE.xy) / min(RENDERSIZE.x, RENDERSIZE.y);

    mat3 rot = quatToMat(vec4(quatX, quatY, quatZ, quatW));

    vec3 ro = rot * vec3(0.0, 0.0, 4.0);
    vec3 rd = rot * normalize(vec3(uv, -2.5));

    float r = 0.0;
    float hitDist = -1.0;
    vec3 p = ro;
    for (int i = 0; i < 64; i++) {
        float l = Distance(p, t);
        p += l * rd;
        r += abs(l);
        if (abs(l) < 0.0001 * r) { hitDist = r; break; }
        if (r > 40.0) break;
    }

    if (hitDist < 0.0) {
        gl_FragColor = vec4(0.0);
        return;
    }

    vec2 epsilon = vec2(0.001, 0.0);
    float pd = Distance(p, t);
    vec3 n = normalize(vec3(
        Distance(p + epsilon.xyy, t) - pd,
        Distance(p + epsilon.yxy, t) - pd,
        Distance(p + epsilon.yyx, t) - pd
    ));

    vec3 light = rot * normalize(vec3(0.6, 0.7, -0.5));
    float diff = max(dot(n, light), 0.0);
    float rim = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
    vec3 col = vec3(0.9, 0.95, 1.0) * diff + vec3(0.3, 0.4, 0.5) * rim + vec3(0.05);
    col = pow(col, vec3(0.4545));

    gl_FragColor = vec4(col, 1.0);
}
