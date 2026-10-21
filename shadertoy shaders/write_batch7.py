import os

# --- Quantum Field Theory ---
# Refactored to avoid vec4[2] typed array return
content1 = r"""/*{
    "DESCRIPTION": "Quantum fluctuations and a particle on a wave surface.",
    "CREDIT": "David654 / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define FOV 60.0
#define MAX_DIST 32.0
#define MAX_STEPS 512
#define CAMERA_POS vec3(0, 0, -10)
#define LIGHT_POS vec3(0, 100, -100)
#define WAVE_ITERATIONS 12

const float PI = 3.1415926;
const float EPSILON = 0.001;

vec3 rotateX(in vec3 v, in float theta)
{
    float s = sin(theta);
    float c = cos(theta);
    return v *= mat3(1, 0, 0, 0, c, -s, 0, s, c);
}

vec3 rotateY(in vec3 v, in float theta)
{
    float s = sin(theta);
    float c = cos(theta);
    return v *= mat3(c, 0, s, 0, 1, 0, -s, 0, c);
}

vec3 rotateZ(in vec3 v, in float theta)
{
    float s = sin(theta);
    float c = cos(theta);
    return v *= mat3(c, -s, 0, s, c, 0, 0, 0, 1);
}

vec3 mouseControl(in vec3 p)
{
    float time = TIME * speed;
    float mx = 0.3 * sin(time * 0.2);
    float my = 0.15 * cos(time * 0.15) + 0.25;
    p = rotateX(p, -my * PI * 0.5 - 0.5);
    p = rotateZ(p, -mx * 2.0 * PI + PI);
    return p;
}

vec2 wavedx(vec2 position, vec2 direction, float frequency, float timeshift)
{
  float x = dot(direction, position) * frequency + timeshift;
  float wave = sin(x);
  float dx = cos(x);
  return vec2(wave, -dx);
}

float getWaves(vec2 position)
{
  float time = TIME * speed;
  float wavePhaseShift = length(position) * 0.1;
  float iter = 0.0;
  float frequency = 1.0;
  float timeMultiplier = 2.0;
  float weight = 1.0;
  float sumOfValues = 0.0;
  float sumOfWeights = 0.0;
  for(int i=0; i < WAVE_ITERATIONS; i++) {
    vec2 p = vec2(sin(iter), cos(iter));
    vec2 res = wavedx(position, p, frequency, time * timeMultiplier + wavePhaseShift);
    position += p * res.y * weight * 0.05;
    sumOfValues += res.x * weight;
    sumOfWeights += weight;
    weight = mix(weight, 0.0, 0.1);
    frequency *= 1.22;
    timeMultiplier *= 1.07;
    iter += 1232.399963;
  }
  return sumOfValues / sumOfWeights;
}

float particle(vec3 p)
{
    float time = TIME * speed;
    return 4.0*exp(-(p.x * p.x + p.y * p.y));
}

float toggle(float x, float value)
{
    return 0.5 + atan(x * x - value * value) / PI;
}

vec3 getSDF(vec3 p)
{
    float time = TIME * speed;
    p = mouseControl(p);
    float sdf = p.z + toggle(time, 2.0) * particle(p) + 0.8*getWaves(p.xy);
    vec3 res = vec3(abs(sdf), 0, 0);
    return res;
}

float saturate_v (float x)
{
    return min(1.0, max(0.0,x));
}
vec3 saturate_v3 (vec3 x)
{
    return min(vec3(1.,1.,1.), max(vec3(0.,0.,0.),x));
}

vec3 jet(float w)
{
    float x = saturate_v(w);
    vec3 c;
    if (x < 0.25)
        c = vec3(0.0, 4.0 * x, 1.0);
    else if (x < 0.5)
        c = vec3(0.0, 1.0, 1.0 + 4.0 * (0.25 - x));
    else if (x < 0.75)
        c = vec3(4.0 * (x - 0.5), 1.0, 0.0);
    else
        c = vec3(1.0, 1.0 + 4.0 * (0.75 - x), 0.0);
    return saturate_v3(c);
}

vec3 getColor(vec3 p)
{
    p = mouseControl(p);
    return jet(abs(p.z) * 0.5);
}

vec3 getNormal(vec3 p)
{
    vec2 e = vec2(EPSILON, 0.0);
    vec3 n = vec3(getSDF(p).x) - vec3(getSDF(p - e.xyy).x, getSDF(p - e.yxy).x, getSDF(p - e.yyx).x);
    return normalize(n);
}

float getSoftShadow(vec3 p, vec3 lightPos)
{
    float res = 1.0;
    float dist = EPSILON;
    float lightSize = 0.03;
    for(int i = 0; i < MAX_STEPS; i++)
    {
        vec3 hit = getSDF(p + lightPos * dist);
        res = min(res, hit.x / (dist * lightSize));
        dist += hit.x;
        if(hit.x < EPSILON || dist > 60.0) break;
    }
    return clamp(res, 0.0, 1.0);
}

float getAmbientOcclusion(vec3 p, vec3 normal)
{
    float occ = 0.0;
    float weight = 1.0;
    for(int i = 0; i < 8; i++)
    {
        float len = 0.01 + 0.02 * float(i * i);
        float dist = getSDF(p + normal * len).x;
        occ += (len - dist) * weight;
        weight *= 0.85;
    }
    return 1.0 - clamp(0.6 * occ, 0.0, 1.0);
}

vec3 getLight(vec3 p, vec3 rd, vec3 lightPos)
{
    vec3 finalCol = vec3(0, 0, 0);
    vec3 v = -rd;
    vec3 n = getNormal(p);
    vec3 col = getColor(p);
    vec3 l = normalize(lightPos - p);
    vec3 R = reflect(-l, n);
    vec3 ambient = col * 0.1;
    vec3 diffuse = col * clamp(dot(l, n), 0.0, 1.0);
    float shadow = getSoftShadow(p + n * 0.02, lightPos);
    float occ = getAmbientOcclusion(p, n);
    vec3 back = 0.05 * col * clamp(dot(n, -l), 0.0, 1.0);
    finalCol = (ambient + back) * occ + (diffuse ) * shadow;
    return finalCol;
}

// Refactored: return object as vec4 instead of vec4[2]
vec4 rayMarch(vec3 ro, vec3 rd)
{
    vec3 object_v = vec3(0.0);
    for(int i = 0; i < MAX_STEPS; i++)
    {
        vec3 p = ro + object_v.x * rd;
        vec3 hit = getSDF(p);
        object_v.x += hit.x * 0.085;
        object_v.y = hit.y;
        object_v.z = hit.z;
        if(abs(hit.x) < EPSILON || object_v.x > float(MAX_DIST)) break;
    }
    return vec4(object_v, 0);
}

vec3 render_v(in vec2 uv)
{
    vec3 ro = CAMERA_POS;
    float invTanFOV = 1.0 / (tan(FOV / 2.0 * PI / 180.0));
    vec3 rd = normalize(vec3(uv, invTanFOV));
    vec4 object_v = rayMarch(ro, rd);
    vec3 col;
    if(object_v.x < float(MAX_DIST))
    {
        vec3 p = ro + object_v.x * rd;
        col = getLight(p, rd, LIGHT_POS);
    }
    else
    {
        col = vec3(0);
    }
    float blendFactor = smoothstep(0.0, MAX_DIST, object_v.x);
    col = vec3(mix(col, vec3(0), blendFactor));
    return col;
}

void main()
{
    vec2 uv = (2.0 * gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
    vec3 col = render_v(uv);
    gl_FragColor = vec4(col, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quantum Field Theory'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Quantum Field Theory.fs'), 'w') as f:
    f.write(content1)
print('Written Quantum Field Theory.fs')
