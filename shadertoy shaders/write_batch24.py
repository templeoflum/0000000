import os

# --- Quantum Zappy Sphere ---
# Original: Cubemap cellular automaton on sphere + cascading blur (6 passes)
# Replace with: procedural reaction-diffusion-like pattern on sphere with glow
content_qzs = r"""/*{
    "DESCRIPTION": "Quantum zappy sphere - animated reaction-diffusion pattern on a sphere.",
    "CREDIT": "frisk256 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

float hash_qz(vec3 p) {
    return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

vec3 shine(vec3 c) {
    return (c * (1.0 - length(c)) - 0.014) * 4.0;
}

// Procedural animated pattern on sphere surface
vec3 spherePattern(vec3 d, float time) {
    // Multi-scale noise on sphere
    vec3 c = vec3(0.0);
    float s = 1.0;
    for (float i = 0.0; i < 4.0; i++) {
        vec3 p = d * s + vec3(time * 0.3 * (i + 1.0));
        float n1 = hash_qz(floor(p * 3.0));
        float n2 = hash_qz(floor(p * 3.0) + vec3(1.0));
        float n3 = hash_qz(floor(p * 3.0) + vec3(0.0, 1.0, 0.0));
        vec3 nc = vec3(n1, n2, n3);
        nc = nc / (length(nc) + 0.01);
        // Reaction-diffusion-like mixing
        nc.xyz += (nc.yzx * nc.zxy) * 0.72 - (nc.xyz * nc.yzx + nc.xyz * nc.zxy) * 1.5;
        nc = clamp(nc, 0.0, 1.0);
        nc /= length(nc) + 0.01;
        c += nc / (s * 2.0);
        s *= 2.0;
    }
    return c;
}

void main() {
    vec2 r = RENDERSIZE.xy;
    float time = TIME * speed;
    vec4 fragColor = vec4(0.0);

    vec2 p = (gl_FragCoord.xy - r / 2.0) / r.y * 2.1;
    vec3 d = vec3(p, 0.0);
    if (1.0 - dot(d.xy, d.xy) < 0.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    d.z = sqrt(1.0 - dot(d.xy, d.xy) * 0.999999);

    // Rotate sphere
    float rsp = 1.3;
    float ca = cos(time * rsp), sa = sin(time * rsp);
    vec2 xz = d.xz;
    d.x = xz.x * ca - xz.y * sa;
    d.z = xz.x * sa + xz.y * ca;

    vec3 pattern = spherePattern(d, time);
    vec3 j = shine(pattern);
    fragColor.xyz = j;
    fragColor = mix(fragColor, max(fragColor, 0.0), 0.5);

    // Bloom approximation: sample nearby and add glow
    vec3 glow = vec3(0.0);
    for (float bx = -2.0; bx <= 2.0; bx += 1.0) {
        for (float by = -2.0; by <= 2.0; by += 1.0) {
            vec2 bp = (gl_FragCoord.xy + vec2(bx, by) * 3.0 - r / 2.0) / r.y * 2.1;
            vec3 bd = vec3(bp, 0.0);
            if (1.0 - dot(bd.xy, bd.xy) >= 0.0) {
                bd.z = sqrt(1.0 - dot(bd.xy, bd.xy) * 0.999999);
                vec2 bxz = bd.xz;
                bd.x = bxz.x * ca - bxz.y * sa;
                bd.z = bxz.x * sa + bxz.y * ca;
                vec3 bp2 = spherePattern(bd, time);
                glow += max(shine(bp2), 0.0) * 0.04;
            }
        }
    }
    fragColor.xyz += glow * 2.0 + glow * glow * 3.0;

    gl_FragColor = vec4(max(fragColor.xyz, 0.0), 1.0);
}
"""

# --- Superfluid helium ---
# Original: 128^3 cubemap simulation of Landau-Ginzburg equation with vortex rings
# Replace with: procedural vortex ring visualization with phase coloring
content_sfh = r"""/*{
    "DESCRIPTION": "Superfluid helium - procedural quantum vortex ring visualization.",
    "CREDIT": "michael0884 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.14159265

vec3 hsv2rgb_v(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * rgb * (3.0 - 2.0 * rgb);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

float sdTorus_v(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

// Procedural vortex field
float vortexField(vec3 p, float time) {
    float d = 1e9;
    // Multiple vortex rings at different positions and orientations
    for (float i = 0.0; i < 6.0; i++) {
        float phase = i * 1.047 + time * 0.3;
        float radius = 10.0 + i * 3.3;
        float thick = 1.5;
        vec3 offset = vec3(
            sin(phase * 0.7) * 15.0,
            cos(phase * 1.1) * 10.0 - 5.0,
            sin(phase * 0.5 + 1.0) * 15.0
        );
        // Rotate the torus
        vec3 q = p - offset;
        float ca = cos(phase), sa = sin(phase);
        float tmp = q.x;
        q.x = tmp * ca - q.y * sa;
        q.y = tmp * sa + q.y * ca;

        float td = sdTorus_v(q, vec2(radius, thick));
        d = min(d, td);
    }
    return d;
}

float phaseField(vec3 p, float time) {
    float phase = 0.0;
    for (float i = 0.0; i < 6.0; i++) {
        float ph = i * 1.047 + time * 0.3;
        vec3 offset = vec3(
            sin(ph * 0.7) * 15.0,
            cos(ph * 1.1) * 10.0 - 5.0,
            sin(ph * 0.5 + 1.0) * 15.0
        );
        vec3 q = p - offset;
        float r = length(q.xz);
        float angle = atan(q.z, q.x);
        phase += angle / (1.0 + length(q) * 0.1);
    }
    return phase;
}

void main() {
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    // Camera
    vec2 angles = vec2(0.4 * time, PI * 0.5 + 0.5 * sin(0.35 * time));
    float sp = sin(angles.x), cp = cos(angles.x);
    float st = sin(angles.y), ct = cos(angles.y);
    vec3 front = vec3(cp * ct, st, sp * ct);
    vec3 right = vec3(-sp, 0.0, cp);
    vec3 up = cross(right, front);
    vec3 cpos = -front * 75.0;
    cpos.y += 0.75 + cos(time * 0.153 * PI) * 0.08;

    vec2 uv = (gl_FragCoord.xy - R * 0.5) / R.y * 2.0;
    vec3 ray = normalize(right * uv.x + up * uv.y + front);

    // Volume ray march
    vec4 c = vec4(0.0, 0.0, 0.0, 1.0);
    float td = 0.0;
    for (int i = 0; i < 75; i++) {
        vec3 p = cpos + ray * td;
        // Check bounds
        vec3 halfBox = vec3(64.0);
        vec3 ob = abs(p) - halfBox;
        float outside = length(max(ob, 0.0));
        if (outside > 0.1) {
            td += outside;
            continue;
        }

        float vf = vortexField(p, time);
        float rho = abs(1.0 - exp(-vf * 0.5));
        float alpha = smoothstep(1.0, 0.3, rho);
        float angle = phaseField(p, time) / (2.0 * PI);
        vec3 col = hsv2rgb_v(vec3(angle, 1.0, rho));

        float dtd = 1.0 / (0.4 + 10.0 * rho * rho * rho);
        td += dtd;
        c.w *= alpha;
        if (c.w < 0.01) break;
        c.xyz += 8.0 * col * col * (1.0 - alpha) * dtd;
    }

    // Background
    if (c.w > 0.01) {
        // Procedural sky
        float sky = ray.y * 0.5 + 0.5;
        c.xyz += 0.5 * mix(vec3(0.1, 0.15, 0.3), vec3(0.4, 0.5, 0.7), sky);
    }

    // tanh approximation
    vec3 tc = c.xyz;
    gl_FragColor = vec4(tc / (1.0 + abs(tc)), 1.0);
}
"""

# --- Landau-Ginzburg 3D ---
# Original: Alternating Euler Schrodinger integration in 3D grid via buffers
# Replace with: procedural 3D vortex filament volume rendering
content_lg3d = r"""/*{
    "DESCRIPTION": "Landau-Ginzburg 3D - procedural quantum vortex filaments.",
    "CREDIT": "wyatt / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

// Procedural vortex filament field
float hash_lg(vec3 p) {
    return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

// Smooth noise
float noise_lg(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float n = mix(
        mix(mix(hash_lg(i), hash_lg(i + vec3(1,0,0)), f.x),
            mix(hash_lg(i + vec3(0,1,0)), hash_lg(i + vec3(1,1,0)), f.x), f.y),
        mix(mix(hash_lg(i + vec3(0,0,1)), hash_lg(i + vec3(1,0,1)), f.x),
            mix(hash_lg(i + vec3(0,1,1)), hash_lg(i + vec3(1,1,1)), f.x), f.y), f.z);
    return n;
}

// Vortex line distance
float vortexLine(vec3 p, vec3 a, vec3 b) {
    vec3 ab = b - a;
    float t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0);
    return length(p - a - t * ab);
}

float vortexField_lg(vec3 p, float time) {
    float d = 1e9;
    // Generate procedural vortex filaments
    for (float i = 0.0; i < 8.0; i++) {
        float phase = i * 0.785 + time * 0.2;
        vec3 a = vec3(
            sin(phase * 1.3) * 20.0,
            cos(phase * 0.9) * 15.0,
            sin(phase * 0.7 + 2.0) * 20.0
        );
        vec3 b = vec3(
            sin(phase * 1.3 + 1.5) * 20.0,
            cos(phase * 0.9 + 1.5) * 15.0,
            sin(phase * 0.7 + 3.5) * 20.0
        );
        d = min(d, vortexLine(p, a, b));
    }
    // Add some curved filaments
    for (float i = 0.0; i < 4.0; i++) {
        float phase = i * 1.57 + time * 0.15;
        float r = 15.0 + i * 3.0;
        vec3 center = vec3(sin(phase) * 5.0, cos(phase * 0.7) * 5.0, 0.0);
        // Approximate torus as vortex ring
        vec2 q = vec2(length(p.xz - center.xz) - r, p.y - center.y);
        d = min(d, length(q) - 1.5);
    }
    return d;
}

void main() {
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;
    float N = R.y > 400.0 ? 10.0 : 8.0;
    vec3 mi = 0.5 * vec3(R / N, N * N);

    vec3 p = vec3(0.0, 0.0, -0.8 * R.x / N);
    vec3 d = normalize(vec3((gl_FragCoord.xy - 0.5 * R) / R.y, 1.0));

    // Auto-rotate camera
    float ca = cos(0.2 * time), sa = sin(0.2 * time);
    vec2 tmp;
    tmp = p.xz; p.x = tmp.x * ca - tmp.y * sa; p.z = tmp.x * sa + tmp.y * ca;
    tmp = d.xz; d.x = tmp.x * ca - tmp.y * sa; d.z = tmp.x * sa + tmp.y * ca;

    vec4 Q = vec4(0.0);
    for (int i = 0; i < 120; i++) {
        vec3 o = abs(p) - mi;
        float m = length(max(o, 0.0));
        if (m < 0.1) {
            // Sample vortex field
            float vf = vortexField_lg(p, time);
            float rho = 1.0 - exp(-abs(vf) * 0.3);
            Q += 0.02 * rho;
            p += d * exp(-6.0 * rho);
        } else {
            p += d * max(o.x, max(o.y, o.z));
        }
    }

    gl_FragColor = Q;
}
"""

shaders = [
    ("Quantum Zappy Sphere", content_qzs),
    ("Superfluid helium", content_sfh),
    ("Landau-Ginzburg 3D", content_lg3d),
]

for name, content in shaders:
    path = os.path.join(r'C:\Users\User\Documents\Resolume Wire\Patches', name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name + '.fs'), 'w') as f:
        f.write(content)
    print(f'Written {name}.fs')

print(f'Batch 24 complete: {len(shaders)} shaders written')
