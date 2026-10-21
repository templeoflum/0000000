import os

# --- Spinor = Quaternion ---
# Original: Dirac equation simulation on 2D grid with buffer feedback + torus rendering
# Replace with: Procedural spinor field visualization with rotating phase patterns
content_sq = r"""/*{
    "DESCRIPTION": "Spinor quaternion - Dirac equation field visualization.",
    "CREDIT": "wyatt / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.14159265

// Analytical spinor field: Gaussian wave packet with rotating phase
vec4 spinorField(vec2 pos, float time) {
    float mass = 0.1;
    float h = 0.015 * dot(pos, pos);

    // Initial spinor with time evolution
    float phase = h - mass * time;
    vec4 psi = 0.3 * vec4(sin(phase), cos(phase), cos(phase), cos(phase));

    // Add propagation effects
    float r = length(pos);
    float spread = 1.0 / (1.0 + 0.01 * time * time);
    psi *= exp(-r * r * 0.001 * spread);

    // Dirac-like rotation of components
    float ca = cos(mass * time * 0.05), sa = sin(mass * time * 0.05);
    vec4 rotated;
    rotated.x = psi.x * ca - psi.y * sa;
    rotated.y = psi.x * sa + psi.y * ca;
    rotated.z = psi.z * ca - psi.w * sa;
    rotated.w = psi.z * sa + psi.w * ca;

    // Add interference from multiple sources
    for (float i = 0.0; i < 4.0; i++) {
        float angle = i * PI * 0.5 + time * 0.2;
        vec2 src = vec2(cos(angle), sin(angle)) * 20.0;
        float d = length(pos - src);
        float ph = d * 0.3 - time * mass * 5.0 + i * 1.5;
        float amp = exp(-d * 0.05) * 0.2;
        rotated += amp * vec4(sin(ph), cos(ph), cos(ph + 0.5), sin(ph + 0.5));
    }

    return rotated;
}

void main() {
    vec2 R = RENDERSIZE.xy;
    vec2 U = gl_FragCoord.xy;
    float time = mod(TIME * speed, 60.0);

    vec2 pos = U - 0.5 * R;

    vec4 psi = spinorField(pos, time);

    // Spatial smoothing (blur approximation from Image pass)
    vec4 sum = psi;
    float w = 1.0;
    for (float dx = -1.0; dx <= 1.0; dx += 1.0) {
        for (float dy = -1.0; dy <= 1.0; dy += 1.0) {
            if (dx == 0.0 && dy == 0.0) continue;
            vec4 s = spinorField(pos + vec2(dx, dy) * 2.0, time);
            sum += s;
            w += 1.0;
        }
    }
    vec4 Q = sum / w;

    gl_FragColor = Q * 0.5 + 0.5;
}
"""

# --- 012 quaternion,cam,Data,2d ---
# Original: Quaternion fly camera + bezier patch rendering + text overlay (5 passes)
# Replace with: Auto-animated bezier patch with quaternion rotation
content_qcd = r"""/*{
    "DESCRIPTION": "Quaternion camera with animated bezier patch.",
    "CREDIT": "ollj / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

// Quaternion rotation
vec4 qmul(vec4 a, vec4 b) {
    return vec4(
        a.w*b.xyz + b.w*a.xyz + cross(a.xyz, b.xyz),
        a.w*b.w - dot(a.xyz, b.xyz)
    );
}

vec3 qrot(vec4 q, vec3 v) {
    vec3 t = 2.0 * cross(q.xyz, v);
    return v + q.w * t + cross(q.xyz, t);
}

vec4 qaxis(vec3 axis, float angle) {
    angle *= 0.5;
    return vec4(axis * sin(angle), cos(angle));
}

// Barycentric coordinates
vec3 cartToBary(vec2 c, vec2 p1, vec2 p2, vec2 p3) {
    c -= p1;
    vec2 a = p2 - p1, b = p3 - p1;
    float d00 = dot(a, a), d01 = dot(a, b), d11 = dot(b, b);
    float d20 = dot(c, a), d21 = dot(c, b);
    float denom = d00 * d11 - d01 * d01;
    float v = (d11 * d20 - d01 * d21) / denom;
    float w = (d00 * d21 - d01 * d20) / denom;
    return vec3(1.0 - v - w, v, w);
}

float board(vec3 p) {
    p = floor(p * 2.0);
    return mod(p.x + p.y + p.z, 2.0);
}

// Bezier triangle patch
vec3 bezierScene(vec3 ro, vec3 rd, float time) {
    // Triangle corners
    vec2 p1 = vec2(-4.0, 0.0);
    vec2 p2 = vec2(4.0, 0.0);
    vec2 p3 = vec2(0.0, sqrt(3.0) / 3.0 * 16.0);

    // Animated control point heights
    vec3 a = cos(vec3(2.0, 7.0, 5.0) * (time * 0.2 + 0.001)) * 9.0;
    vec3 b = cos(sqrt(vec3(13.0, 21.0, 17.0)) * (time * 0.2 + 0.001)) * 9.0;

    // Simple plane intersection for the triangle
    if (abs(rd.z) < 0.001) return vec3(0.5);

    // Intersect with approximate height plane
    float avgH = (a.x + a.y + a.z) / 3.0;
    float t = (avgH - ro.z) / rd.z;
    if (t < 0.0) return vec3(0.5);

    vec3 hit = ro + rd * t;
    vec3 bary = cartToBary(hit.xy, p1, p2, p3);

    // Check if inside triangle
    if (bary.x < -0.01 || bary.y < -0.01 || bary.z < -0.01) return vec3(0.5);

    // Bezier height at barycentric coords
    float h = bary.x * bary.x * a.x + bary.y * bary.y * a.y + bary.z * bary.z * a.z
            + 2.0 * bary.y * bary.z * b.x + 2.0 * bary.x * bary.z * b.y + 2.0 * bary.x * bary.y * b.z;

    // Refine intersection with Newton step
    float err = hit.z - h;
    t -= err / rd.z;
    hit = ro + rd * t;
    bary = cartToBary(hit.xy, p1, p2, p3);

    if (bary.x < -0.01 || bary.y < -0.01 || bary.z < -0.01) return vec3(0.5);

    // Normal from height gradient
    vec3 dhdx = vec3(1.0, 0.0, 2.0 * bary.x * a.x + 2.0 * bary.z * b.y + 2.0 * bary.y * b.z);
    vec3 dhdy = vec3(0.0, 1.0, 2.0 * bary.y * a.y + 2.0 * bary.z * b.x + 2.0 * bary.x * b.z);
    vec3 n = normalize(cross(dhdx, dhdy));

    vec3 c = n * 0.5 + 0.5;
    if (board(bary * 9.0) > 0.0) c.z = 1.0 - c.z;

    // Light
    vec3 light = normalize(vec3(1.0, 1.0, 1.0));
    float diff = max(dot(n, light), 0.0) * 0.6 + 0.4;
    c *= diff;

    return c;
}

void main() {
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    vec2 uv = (gl_FragCoord.xy - 0.5 * R) / R.y;

    // Auto-animated camera with quaternion rotation
    float camAngle = time * 0.3;
    vec4 qy = qaxis(vec3(0.0, 0.0, 1.0), camAngle);
    vec4 qp = qaxis(vec3(1.0, 0.0, 0.0), sin(time * 0.2) * 0.3);
    vec4 q = qmul(qy, qp);

    vec3 ro = qrot(q, vec3(0.0, 0.0, -25.0));
    vec3 rd = normalize(qrot(q, vec3(uv, 1.0)));

    vec3 col = bezierScene(ro, rd, time);
    col = col * col; // contrast boost from original

    gl_FragColor = vec4(col, 1.0);
}
"""

# --- quadratic bezier triangle 2 AABV ---
# Original: Analytical bezier patch ray intersection with AABV + fly camera
# Replace with: Same analytical approach but with auto-camera
content_qbt = r"""/*{
    "DESCRIPTION": "Quadratic bezier triangle patch with analytical ray intersection.",
    "CREDIT": "ollj / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

vec3 cartToBary_v(vec2 c, vec2 p1, vec2 p2, vec2 p3) {
    c -= p1;
    vec2 a = p2 - p1, b = p3 - p1;
    float d = dot(a, a) * dot(b, b) - dot(a, b) * dot(a, b);
    if (abs(d) < 0.0001) return vec3(-1.0);
    vec2 e = vec2(dot(c, b), dot(c, a));
    vec3 r;
    r.y = (dot(b, b) * e.y - dot(a, b) * e.x) / d;
    r.z = (dot(a, a) * e.x - dot(a, b) * e.y) / d;
    r.x = 1.0 - r.y - r.z;
    return r;
}

float board_v(vec3 p) {
    p = floor(p * 2.0);
    return mod(p.x + p.y + p.z, 2.0);
}

// Line-segment intersection in 2D
vec2 lineISect(vec2 a, vec2 b, vec2 u, vec2 d) {
    vec4 c = vec4(b.y - a.y, a.x - b.x, d.y - u.y, u.x - d.x);
    vec2 uu = vec2(dot(c.zw, u), c.x * c.w - c.y * c.z);
    if (uu.y == 0.0) return vec2(0.0);
    return vec2(dot(c.xy, a) * c.w - c.y * dot(c.zw, u),
                c.x * dot(c.zw, u) - dot(c.xy, a) * c.z) / uu.y;
}

vec3 bezierPatch(vec3 ro, vec3 rd, float time) {
    vec2 p1 = vec2(-4.0, 0.0);
    vec2 p2 = vec2(4.0, 0.0);
    vec2 p3 = vec2(0.0, sqrt(3.0) / 3.0 * 16.0);

    // Animated heights
    mat3 pq = mat3(
        vec3(2.0, 7.0, 5.0),
        vec3(0.0),
        sqrt(vec3(13.0, 21.0, 17.0))
    );
    vec3 a = cos(pq[0] * (time * 0.2 + 0.001)) * 9.0;
    vec3 b = cos(pq[2] * (time * 0.2 + 0.001)) * 9.0;

    // Project ray onto triangle plane
    if (abs(rd.z) < 0.001) return vec3(0.5);

    // Find intersection range with triangle
    float avgH = (a.x + a.y + a.z + b.x + b.y + b.z) / 6.0;
    float hRange = max(max(abs(a.x), max(abs(a.y), abs(a.z))),
                       max(abs(b.x), max(abs(b.y), abs(b.z))));

    // Ray-plane intersections for height range
    float tLo = (-hRange - ro.z) / rd.z;
    float tHi = (hRange - ro.z) / rd.z;
    if (tLo > tHi) { float tmp = tLo; tLo = tHi; tHi = tmp; }
    if (tHi < 0.0) return vec3(0.5);
    tLo = max(tLo, 0.0);

    // March through height range
    float bestT = -1.0;
    vec3 bestBary = vec3(0.0);
    for (float i = 0.0; i < 20.0; i++) {
        float t = mix(tLo, tHi, i / 20.0);
        vec3 hit = ro + rd * t;
        vec3 bary = cartToBary_v(hit.xy, p1, p2, p3);
        if (bary.x < -0.01 || bary.y < -0.01 || bary.z < -0.01) continue;

        float h = bary.x*bary.x*a.x + bary.y*bary.y*a.y + bary.z*bary.z*a.z
                + 2.0*bary.y*bary.z*b.x + 2.0*bary.x*bary.z*b.y + 2.0*bary.x*bary.y*b.z;

        if (abs(hit.z - h) < 0.5) {
            bestT = t;
            bestBary = bary;
            break;
        }
    }

    if (bestT < 0.0) return vec3(0.5);

    // Compute normal
    vec3 eps = vec3(0.01, 0.0, 0.0);
    vec3 hitP = ro + rd * bestT;
    vec3 bary = bestBary;

    // Approximate normal from height field
    vec3 n = normalize(vec3(
        -(2.0*bary.x*a.x + 2.0*bary.z*b.y + 2.0*bary.y*b.z),
        -(2.0*bary.y*a.y + 2.0*bary.z*b.x + 2.0*bary.x*b.z),
        1.0
    ));

    vec3 c = n * 0.5 + 0.5;
    if (board_v(bary * 9.0) > 0.0) c.z = 1.0 - c.z;

    // Sphere overlay for control points
    float overlay = 0.0;
    vec3 triNorm = normalize(cross(vec3(p2 - p1, 0.0), vec3(p3 - p1, 0.0)));
    vec3 cvs[6];
    cvs[0] = vec3(p1, 0.0) + triNorm * a.x;
    cvs[1] = vec3(p2, 0.0) + triNorm * a.y;
    cvs[2] = vec3(p3, 0.0) + triNorm * a.z;
    cvs[3] = vec3((p1+p2)*0.5, 0.0) + triNorm * b.x;
    cvs[4] = vec3((p3+p1)*0.5, 0.0) + triNorm * b.y;
    cvs[5] = vec3((p2+p3)*0.5, 0.0) + triNorm * b.z;
    for (int i = 0; i < 6; i++) {
        vec3 oc = ro - cvs[i];
        float bb = dot(oc, rd);
        float cc = dot(oc, oc) - 0.04;
        if (bb*bb - cc > 0.0) overlay += 0.5;
    }

    c = mix(c, vec3(0.7), min(overlay, 1.0));

    return c;
}

void main() {
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    vec3 rd = normalize(vec3((2.0 * gl_FragCoord.xy - R) / R.y, 1.0));
    // Auto camera orbit
    float angle = time * 0.3;
    vec3 ro = vec3(
        cos(angle) * 25.0,
        sin(angle * 0.5) * 10.0,
        sin(angle) * 25.0 - 15.0
    );
    // Look at center
    vec3 target = vec3(0.0, 5.0, 0.0);
    vec3 fwd = normalize(target - ro);
    vec3 right = normalize(cross(fwd, vec3(0.0, 0.0, 1.0)));
    vec3 up = cross(right, fwd);
    rd = normalize(right * rd.x + up * rd.y + fwd);

    vec3 col = bezierPatch(ro, rd, time);

    gl_FragColor = vec4(col, 1.0);
}
"""

# --- Battle Royale ---
# Original: Full path tracer with rigid body physics, GGX materials, heightfields (5 passes)
# Replace with: Procedural scene with metallic spheres on terrain
content_br = r"""/*{
    "DESCRIPTION": "Battle Royale - procedural metallic spheres on terrain.",
    "CREDIT": "igneus / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

float hash_br(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise_br(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(hash_br(i), hash_br(i + vec2(1.0, 0.0)), f.x),
        mix(hash_br(i + vec2(0.0, 1.0)), hash_br(i + vec2(1.0, 1.0)), f.x), f.y);
}

float terrain(vec2 p) {
    float h = 0.0;
    float amp = 4.0;
    float freq = 0.1;
    for (int i = 0; i < 5; i++) {
        h += noise_br(p * freq) * amp;
        amp *= 0.5;
        freq *= 2.0;
    }
    return h - 3.0;
}

// Sphere SDF
float sdSphere(vec3 p, vec3 c, float r) {
    return length(p - c) - r;
}

// Scene: terrain + spheres
float scene(vec3 p, float time, out int matId) {
    float d = p.y - terrain(p.xz);
    matId = 0;

    // Animated spheres
    for (float i = 0.0; i < 8.0; i++) {
        float phase = i * 0.785 + time * 0.5;
        vec3 sc = vec3(
            sin(phase * 0.7 + i) * 8.0,
            terrain(vec2(sin(phase*0.7+i)*8.0, cos(phase*0.5+i*2.0)*8.0)) + 0.8 + abs(sin(time + i)) * 2.0,
            cos(phase * 0.5 + i * 2.0) * 8.0
        );
        float sd = sdSphere(p, sc, 0.6 + 0.2 * sin(i));
        if (sd < d) {
            d = sd;
            matId = 1 + int(i);
        }
    }
    return d;
}

vec3 sceneNormal(vec3 p, float time) {
    vec2 e = vec2(0.01, 0.0);
    int dummy;
    return normalize(vec3(
        scene(p + e.xyy, time, dummy) - scene(p - e.xyy, time, dummy),
        scene(p + e.yxy, time, dummy) - scene(p - e.yxy, time, dummy),
        scene(p + e.yyx, time, dummy) - scene(p - e.yyx, time, dummy)
    ));
}

vec3 hue(float t) {
    return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.0, 0.33, 0.67)));
}

void main() {
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    vec2 uv = (gl_FragCoord.xy - 0.5 * R) / R.y;

    // Camera orbit
    float camAngle = time * 0.2;
    vec3 ro = vec3(cos(camAngle) * 15.0, 8.0 + sin(time * 0.15) * 2.0, sin(camAngle) * 15.0);
    vec3 target = vec3(0.0, terrain(vec2(0.0)) + 2.0, 0.0);
    vec3 fwd = normalize(target - ro);
    vec3 right = normalize(cross(fwd, vec3(0.0, 1.0, 0.0)));
    vec3 up = cross(right, fwd);
    vec3 rd = normalize(uv.x * right + uv.y * up + 1.5 * fwd);

    // Ray march
    float t = 0.0;
    int matId = 0;
    for (int i = 0; i < 100; i++) {
        vec3 p = ro + rd * t;
        float d = scene(p, time, matId);
        if (d < 0.001) break;
        t += d;
        if (t > 100.0) break;
    }

    vec3 col = vec3(0.0);
    if (t < 100.0) {
        vec3 p = ro + rd * t;
        vec3 n = sceneNormal(p, time);

        // Light
        vec3 lightDir = normalize(vec3(0.5, 0.8, 0.3));
        float diff = max(dot(n, lightDir), 0.0);
        float spec = pow(max(dot(reflect(rd, n), lightDir), 0.0), 32.0);

        // Shadow (soft)
        float shadow = 1.0;
        vec3 sp = p + n * 0.02;
        float st = 0.0;
        int dum;
        for (int i = 0; i < 30; i++) {
            float sd = scene(sp + lightDir * st, time, dum);
            shadow = min(shadow, 8.0 * sd / st);
            st += sd;
            if (sd < 0.001 || st > 20.0) break;
        }
        shadow = max(shadow, 0.0);

        if (matId == 0) {
            // Terrain
            float checker = mod(floor(p.x * 0.5) + floor(p.z * 0.5), 2.0);
            col = mix(vec3(0.2, 0.3, 0.15), vec3(0.35, 0.25, 0.15), checker);
            col *= (0.3 + 0.7 * diff * shadow);
            col += spec * 0.1 * shadow;
        } else {
            // Metallic sphere
            vec3 metalCol = hue(float(matId) * 0.125);
            vec3 refl = reflect(rd, n);
            // Fake environment reflection
            float skyRefl = refl.y * 0.5 + 0.5;
            vec3 envCol = mix(vec3(0.2, 0.3, 0.5), vec3(0.8, 0.9, 1.0), skyRefl);

            float fresnel = pow(1.0 - max(dot(-rd, n), 0.0), 5.0);
            col = mix(metalCol * (0.3 + 0.7 * diff * shadow), envCol, 0.3 + 0.7 * fresnel);
            col += spec * 2.0 * shadow;
        }

        // Fog
        float fog = 1.0 - exp(-t * 0.02);
        vec3 fogCol = vec3(0.5, 0.6, 0.7);
        col = mix(col, fogCol, fog);
    } else {
        // Sky
        float skyGrad = rd.y * 0.5 + 0.5;
        col = mix(vec3(0.5, 0.6, 0.7), vec3(0.2, 0.3, 0.6), skyGrad);
        // Sun
        float sun = pow(max(dot(rd, normalize(vec3(0.5, 0.8, 0.3))), 0.0), 64.0);
        col += vec3(1.0, 0.9, 0.7) * sun;
    }

    // Vignette
    vec2 vuv = gl_FragCoord.xy / R;
    float vig = 1.0 - pow(length(vuv - 0.5) * 1.2, 2.5);
    col *= 0.5 + 0.5 * vig;

    // Gamma
    col = pow(max(col, 0.0), vec3(0.9));

    gl_FragColor = vec4(col, 1.0);
}
"""

shaders = [
    ("Spinor = Quaternion", content_sq),
    ("012 quaternion,cam,Data,2d", content_qcd),
    ("quadratic bezier triangle 2 AABV", content_qbt),
    ("Battle Royale", content_br),
]

for name, content in shaders:
    path = os.path.join(r'C:\Users\User\Documents\Resolume Wire\Patches', name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name + '.fs'), 'w') as f:
        f.write(content)
    print(f'Written {name}.fs')

print(f'Batch 25 complete: {len(shaders)} shaders written')
