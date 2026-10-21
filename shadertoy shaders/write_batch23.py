import os

# --- Resonant Damping ---
# Analytical damped standing wave visualization
# Original uses buffer feedback for 1D wave equation at multiple frequencies
# Replace with analytical standing wave solution
content_rd = r"""/*{
    "DESCRIPTION": "Resonant damping - analytical standing wave visualization.",
    "CREDIT": "Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define N 8.

float ln_v(vec2 U, vec2 a, vec2 b) {
    return length(U-a-(b-a)*clamp(dot(U-a,b-a)/dot(b-a,b-a),0.,1.));
}

// Analytical damped wave solution
float wave(float x, float freq, float damping, float time) {
    return sin(freq * x) * exp(-damping * freq * freq * time) * cos(freq * time);
}

void main() {
    vec2 U = gl_FragCoord.xy;
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    float y = floor(U.y/R.y*N);
    float damping = (y + 0.5) / N;
    damping *= damping;

    float d = 1e9;
    for (float i = -3.; i <= 2.; i++) {
        float x1 = U.x + i;
        float x2 = U.x + i + 1.0;

        // Analytical wave: sum of harmonics with different damping
        float w1 = 0.0;
        float w2 = 0.0;
        for (float h = 1.0; h <= 5.0; h += 1.0) {
            float freq = h * 3.14159 * 2.0 / R.x;
            w1 += wave(x1, freq * 3.0, damping * 0.5, time) / h;
            w2 += wave(x2, freq * 3.0, damping * 0.5, time) / h;
        }

        vec2 a = vec2(x1, (0.5+y)/N*R.y + 2.0*R.y/N * w1 * 0.5);
        vec2 b = vec2(x2, (0.5+y)/N*R.y + 2.0*R.y/N * w2 * 0.5);
        d = min(d, ln_v(U, a, b));
    }

    // Color based on wave amplitude
    float amp = 0.0;
    for (float h = 1.0; h <= 5.0; h += 1.0) {
        float freq = h * 3.14159 * 2.0 / R.x;
        amp += wave(U.x, freq * 3.0, damping * 0.5, time) / h;
    }

    gl_FragColor = mix(sin(-2.0+6.2*amp*0.5+vec4(1,2,3,4)), vec4(1), smoothstep(2.,1.,d));
}
"""

# --- The Schrodinger equation ---
# Analytical Gaussian wave packet
content_se = r"""/*{
    "DESCRIPTION": "Schrodinger equation - analytical wave packet visualization.",
    "CREDIT": "Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.141592653589793

// Analytical Gaussian wave packet solution to free Schrodinger equation
vec2 wavePacket(vec2 pos, float time, vec2 k0, float sigma0) {
    // Spreading Gaussian wave packet
    float sigma2 = sigma0*sigma0 + time*time/(sigma0*sigma0);
    float sigma = sqrt(sigma2);

    vec2 r = pos - k0 * time;
    float envelope = exp(-dot(r,r) / (2.0*sigma2));

    float phase = dot(k0, pos) - 0.5*dot(k0,k0)*time;
    phase += atan(time/(sigma0*sigma0)) * 0.5; // Gouy phase

    return envelope * vec2(cos(phase), sin(phase)) / sqrt(sigma/sigma0);
}

void main() {
    vec2 pos = (gl_FragCoord.xy - 0.5*RENDERSIZE.xy) * 0.1;
    float time = TIME * speed;

    // Multiple wave packets for interference
    vec2 psi = vec2(0.0);
    psi += wavePacket(pos, time, vec2(1.5, 0.5), 3.0);
    psi += wavePacket(pos, time, vec2(-1.0, 1.0), 2.5);
    psi += wavePacket(pos, time * 0.7, vec2(0.5, -1.5), 2.0);

    // Color mapping: phase -> hue, amplitude -> brightness
    vec2 red = vec2(1,0), green = vec2(-0.5,sqrt(3.)*0.5), blue = vec2(-0.5,-sqrt(3.)*0.5);
    vec3 RGB = vec3(dot(psi, red), dot(psi, green), dot(psi, blue));
    gl_FragColor = vec4(RGB*RGB*2., 1.0);
}
"""

# --- eletron's diffraction experiment ---
# Analytical Fraunhofer diffraction pattern
content_ed = r"""/*{
    "DESCRIPTION": "Electron diffraction - analytical single/double slit pattern.",
    "CREDIT": "Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.141592653589793

vec3 hue2rgb(float h) {
    return clamp(abs(mod(6.0*h+vec3(0,4,2),6.0)-3.0)-1.0, 0.0, 1.0);
}

// Potential: double slit
float potential(vec2 p) {
    float wall = step(abs(p.x), 1.0) * step(abs(p.y - 0.0), 0.5);
    float slit1 = step(abs(p.y - 3.0), 1.5);
    float slit2 = step(abs(p.y + 3.0), 1.5);
    float barrier = step(abs(p.x), 0.3) * (1.0 - slit1) * (1.0 - slit2);
    return barrier * 50.0;
}

void main() {
    vec2 p = (gl_FragCoord.xy - 0.5*RENDERSIZE.xy) * 0.05;
    float time = TIME * speed;

    // Analytical wave function: superposition of plane wave + diffraction
    float k = 3.0; // wave number
    vec2 psi = vec2(0.0);

    // Incoming plane wave
    float phase0 = k * p.x - k*k*0.5*time;
    psi += vec2(cos(phase0), sin(phase0)) * exp(-0.01*max(0.0, -p.x));

    // Diffracted waves from two slits
    for (float s = -1.0; s <= 1.0; s += 2.0) {
        vec2 slitPos = vec2(0.0, s * 3.0);
        float r = length(p - slitPos);
        float phase = k * r - k*k*0.5*time;
        float amp = 1.0 / (0.5 + sqrt(r));
        psi += amp * vec2(cos(phase), sin(phase)) * step(0.0, p.x);
    }

    // Barrier absorption
    float pot = potential(p);
    psi *= exp(-pot * 0.1);

    float amplitude = length(psi);
    float phase = atan(psi.y, psi.x) / (2.0*PI);

    vec3 col = 1.5 * amplitude * hue2rgb(phase);
    col += 0.25 * pot / 50.0; // Show barrier

    gl_FragColor = vec4(col, 1.0);
}
"""

# --- Quantum Rain ---
# Analytical wave interference on grid
content_qr = r"""/*{
    "DESCRIPTION": "Quantum rain - wave interference visualization.",
    "CREDIT": "Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

float hash_qr(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void main() {
    vec2 U = gl_FragCoord.xy;
    vec2 R = RENDERSIZE.xy;
    float time = TIME * speed;

    vec2 uv = U / R;
    vec2 p = (U - 0.5*R) / R.y;

    // Simulate quantum rain: interference of circular waves from random sources
    vec2 psi = vec2(0.0);
    for (float i = 0.0; i < 12.0; i++) {
        float t = floor(time * 0.5 + i * 0.37);
        vec2 center = vec2(hash_qr(vec2(i, t)), hash_qr(vec2(t, i))) - 0.5;
        float birth = fract(time * 0.5 + i * 0.37);
        float r = length(p - center);
        float k = 30.0;
        float phase = k * r - k * birth * 2.0;
        float amp = exp(-birth * 3.0) / (0.5 + r * 5.0);
        psi += amp * vec2(cos(phase), sin(phase));
    }

    // Normal-like shading from wave field
    vec2 dx = vec2(1.0/R.x, 0.0);
    vec2 dy = vec2(0.0, 1.0/R.y);

    float amp = length(psi);
    vec3 no = normalize(vec3(
        amp - length(psi * 0.99),
        amp - length(psi * 1.01), 5.0
    ));

    // Reflective coloring
    vec3 re = reflect(no, vec3(0,0,1));
    vec3 col = (0.5 + 0.5*vec3(re.x, re.y, 0.5+0.5*re.z)) *
               sin(atan(amp) * vec3(1,2,3) + vec3(0.5, 1.0, 1.5));

    gl_FragColor = vec4(col, 1.0);
}
"""

shaders = [
    ("Resonant Damping", content_rd),
    ("The Schrodinger equation", content_se),
    ("eletron's diffraction experiment", content_ed),
    ("Quantum Rain", content_qr),
]

for name, content in shaders:
    path = os.path.join(r'C:\Users\User\Documents\Resolume Wire\Patches', name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name + '.fs'), 'w') as f:
        f.write(content)
    print(f'Written {name}.fs')

print(f'Batch 23 complete: {len(shaders)} shaders written')
