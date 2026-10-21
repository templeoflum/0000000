import os

# --- Deep Quantum Time State (sci-fi) ---
content1 = r"""/*{
    "DESCRIPTION": "Quantum cryptography visualization with entanglement and collapse.",
    "CREDIT": "Rodrigo Cal / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

mat2 rotate_m(float a){
    return mat2(cos(a), sin(a), -sin(a), cos(a));
}

float qtime;

struct QuantumState{
    vec3 momentum;
    vec3 position;
};

QuantumState normalizeQ(QuantumState q){
    q.position = normalize(q.position);
    q.momentum = normalize(q.momentum);
    return q;
}

vec3 getQuantumSpin(QuantumState q){
    vec3 ps = q.position;
    float t = qtime;
    ps.zy = rotate_m(q.momentum.x*t) * ps.zy;
    ps.zx = rotate_m(q.momentum.y*t) * ps.zx;
    ps.xy = rotate_m(q.momentum.z*t) * ps.xy;
    return normalize(ps);
}

void getQuantumEntangle(inout QuantumState q1, inout QuantumState q2){
    QuantumState qq;
    qq.momentum.x = dot(q1.momentum.zy, q2.momentum.zy);
    qq.momentum.y = dot(q1.momentum.zx, q2.momentum.zx);
    qq.momentum.z = dot(q1.momentum.xy, q2.momentum.xy);
    qq.position = vec3(0.0);
    q1.momentum = -qq.momentum;
    q2.momentum =  qq.momentum;
}

void getQuantumCollapse(inout QuantumState q1, vec3 angle){
    QuantumState qq;
    qq.momentum.x = dot(q1.momentum.zy, angle.zy);
    qq.momentum.y = dot(q1.momentum.zx, angle.zx);
    qq.momentum.z = dot(q1.momentum.xy, angle.xy);
    qq.position = vec3(0.0);
    q1.momentum = qq.momentum;
}

QuantumState getQuantum(vec3 p){
    QuantumState q;
    q.position = vec3(0.,1.,0.);
    q.momentum = vec3(mod(cos(p.x+p.y+p.z), 1.),
                      mod(cos(p.x+p.y), 1.),
                      mod(cos(p.x), 1.));
    return normalizeQ(q);
}

float sdLine_v(in vec2 p, in vec2 a, in vec2 b){
    vec2 pa = p-a;
    vec2 ba = b-a;
    float sd = dot(pa,ba) / dot(ba,ba);
    float h = clamp(sd, 0.0, 1.0);
    return length(pa - ba*h);
}

void drawState(inout vec4 c, vec2 p, QuantumState q){
    p *= 5.;
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p*vec2(1.,2.)))));
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p*vec2(2.,1.)))));
    c = mix(c,vec4(0.), smoothstep(-0.05,.0, -abs(1.-length(p))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine_v(p, vec2(0.,0.), vec2(0.,1.)))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine_v(p, vec2(0.,0.), vec2(1.,0.)))));
    c = mix(c,vec4(0.), smoothstep(-0.01,.0, (.01-sdLine_v(p, vec2(0.,0.), vec2(-.45)))));
    vec3 spin = getQuantumSpin(q);
    c = mix(c,vec4(0.,0.,1.,1.), smoothstep(-0.01,.0, .01-sdLine_v(p, vec2(0.,0.), spin.xy)));
    c = mix(c,vec4(0.,1.,1.,1.), smoothstep(-0.01,.0, -abs(.02-sdLine_v(p, vec2(0.,0.), spin.xy))));
}

void drawStateColorUp(inout vec4 c, vec2 p, vec4 cor, QuantumState q){
    p *= 5.;
    float d = -1.;
    d = max(d, min(p.y, 1.-length(p)));
    d = max(d, 1.-length(p*vec2(1.,2.)));
    c = mix(c,cor, smoothstep(-0.05,.0, d));
}

void drawStateColorAll(inout vec4 c, vec2 p, vec4 cor, QuantumState q){
    p *= 5.;
    c = mix(c,cor, smoothstep(-0.05,.0, -abs(1.-length(p*vec2(1.,2.)))));
    c = mix(c,cor, smoothstep(-0.05,.0, -abs(1.-length(p*vec2(2.,1.)))));
    c = mix(c,cor, smoothstep(-0.05,.0, (1.-length(p))));
}

void main(){
    float time = TIME * speed;
    vec2 uv = gl_FragCoord.xy/RENDERSIZE.xy;
    vec2 a = vec2(RENDERSIZE.x/RENDERSIZE.y, 1.);
    vec2 p = (uv-.5)*a;
    vec4 c = vec4(1.);
    qtime = fract((time*15.)/30.)*30.;
    QuantumState q1 = getQuantum(vec3(1.,2.,3.));
    QuantumState q2 = getQuantum(vec3(5.,2.,1.));
    if(time > 10.){
        c = mix(c,vec4(1.,.95,.9,1.), smoothstep(-0.01,.0, (.3-sdLine_v(p, vec2(-.5,-1.), vec2(-.5,1.)))));
        c = mix(c,vec4(1.,.95,.9,1.), smoothstep(-0.01,.0, (.3-sdLine_v(p, vec2( .5,-1.), vec2( .5,1.)))));
    }
    if(time > 5.){
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine_v(p, vec2(-1.,0.), vec2(1.,0.)))));
        vec4 cor1 = vec4(0.8,1.,1.,0.);
        drawStateColorAll(c, p-vec2(-0.5,0.),cor1, q1);
        drawStateColorAll(c, p-vec2( 0.5,0.),cor1, q2);
        getQuantumEntangle(q1, q2);
    }
    if(time > 10.){
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine_v(p, vec2(-.5,-1.), vec2(-.5,1.)))));
        c = mix(c,vec4(0.1), smoothstep(-0.01,.0, -abs(.3-sdLine_v(p, vec2( .5,-1.), vec2( .5,1.)))));
        getQuantumCollapse(q1, vec3(0.,1.,0.));
        getQuantumCollapse(q2, vec3(0.,1.,0.));
        vec4 cor1 = vec4(0.5,1.,.9,0.);
        drawStateColorUp(c, p-vec2(-0.5,0.),cor1, q1);
        drawStateColorUp(c, p-vec2( 0.5,0.),cor1, q2);
    }
    drawState(c, p-vec2(-0.5,0.), q1);
    drawState(c, p-vec2(+0.5,0.), q2);
    gl_FragColor = vec4(c.rgb, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Deep Quantum Time State (sci-fi)'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Deep Quantum Time State (sci-fi).fs'), 'w') as f:
    f.write(content1)
print('Written Deep Quantum Time State (sci-fi).fs')

print('Batch 14 complete: 1 shader written')
