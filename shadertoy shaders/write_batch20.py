import os

# --- Bird VS Mankind ---
# Inlined Common pass (quaternion math, SDF primitives, FractalSpace, map)
# Replaced buffer-based physics/camera with auto-animated flythrough
# Removed VR pass, keyboard input, collision detection
# Renamed: dist -> dist_g, box -> box_v, fog -> fog_g
content1 = r"""/*{
    "DESCRIPTION": "Fractal city flythrough with animated bird creature.",
    "CREDIT": "Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define maxStepRayMarching 50
#define fractalSteps 12
#define FOV 1.4
#define speedOfLight 300.0

float dist_g = 1000.0;
vec3 ro;
float fog_g = 0.;

// Quaternion math
vec4 NormQuat(vec4 q){
    float lenSQ = dot(q, q);
    return q / lenSQ;
}

vec4 BuildQuat(vec3 axis, float angle){
    angle *= 0.5;
    float s = sin(angle);
    return NormQuat(vec4(axis*s, cos(angle)));
}

vec4 MulQuat(vec4 q1, vec4 q2){
    vec4 res;
    res.w   = q1.w*q2.w - dot(q1.xyz, q2.xyz);
    res.xyz = q1.w*q2.xyz + q2.w*q1.xyz + cross(q1.xyz, q2.xyz);
    return NormQuat(res);
}

vec3 Rotate(vec4 q, vec3 v){
    vec3 t = 2.*cross(q.xyz, v);
    return v + q.w*t + cross(q.xyz, t);
}

// SDF primitives
float sphere_v(vec3 ray, vec3 pos, float radius){
    return length(ray-pos) - radius;
}

float cylinder_v(vec3 ray, vec3 pos, float radius, float height){
    return max(length(ray.xy-pos.xy) - radius, abs(ray.z-pos.z)-height);
}

float box_v(vec3 ray, vec3 pos, vec3 size){
    ray = abs(ray-pos) - size;
    return max(max(ray.x,ray.y),ray.z);
}

mat2 rz2(float a){float c=cos(a),s=sin(a);return mat2(c,s,-s,c);}

vec3 FractalSpace(vec3 pos, float time){
    pos *= 0.1;
    float s=3.;
    for(int i=0;i<fractalSteps;i++){
        pos.xy=abs(pos).xy-s;
        pos.xy *= rz2(1.4-0.01*time);
        pos.xz *= rz2(time*0.018);
        pos.yz *= rz2(time*0.005);
        s=s/1.3;
    }
    return pos;
}

float map_v(vec3 pos, vec3 lPos, float time){
    float rayDist = 0.;
    pos = FractalSpace(pos,time);
    pos.xy += .05;

    vec3 pos1 = pos;
    pos1.x = abs(pos.x);
    vec3 pos2 = pos;

    pos.xyz = abs(pos.xyz);
    pos.z -= .01;

    // Ground
    rayDist = box_v(pos,vec3(0.0,0.0,-0.1),vec3(2.,10.0,0.1));
    // Roads
    rayDist = max(rayDist,-box_v(pos,vec3(0.0,0.0,0.0),vec3(0.02,10.0,0.002)));
    rayDist = max(rayDist,-box_v(pos,vec3(0.0,0.0,0.0),vec3(10.,0.02,0.002)));
    rayDist = max(rayDist,-box_v(pos,vec3(0.15,0.0,0.0),vec3(0.01,10.0,0.002)));
    rayDist = max(rayDist,-box_v(pos,vec3(0.0,0.15,0.0),vec3(10.,0.01,0.002)));

    // Big building
    vec3 b2 = pos;
    b2.xy -= 0.22;
    b2 = abs(b2);
    rayDist = min(rayDist,box_v(b2,vec3(0.,0.,0.0),vec3(0.05,0.05,0.1)));
    rayDist = min(rayDist,box_v(b2,vec3(0.,0.,0.05),vec3(0.04,0.04,0.1)));

    // Paris building
    vec3 b1 = pos;
    b1.xy -= vec2(0.22,0.08);
    b1 = abs(b1);
    float XYsize = max(0.,.5*pos.z-0.02);
    float Zsize = max(0.,0.4*max(b1.x,b1.y)-0.01);
    rayDist = min(rayDist,box_v(b1,vec3(0.,0.,0.0),vec3(0.05-XYsize,0.05-XYsize,0.06-Zsize)));
    rayDist = max(rayDist,-box_v(b1,vec3(0.0,0.0,0.05),vec3(0.02+XYsize,0.02+XYsize,0.05)));
    rayDist = min(rayDist,box_v(b1,vec3(0.02,0.04,0.046),vec3(0.005,0.009,0.008)));
    rayDist = min(rayDist,box_v(b1,vec3(0.04,0.01,0.05),vec3(0.005,0.001,0.008)));
    b1.xy *= 0.56;
    b1 = abs(b1-0.02);
    rayDist = max(rayDist,-box_v(b1,vec3(0.01,0.01,0.01),vec3(0.003,0.003,0.008)));

    // Garden walls
    vec3 b0 = pos1;
    b0.xy -= 0.08;
    rayDist = min(rayDist,box_v(b0,vec3(0.,0.,0.005),vec3(0.05,0.05,0.005)));
    rayDist = max(rayDist,-box_v(b0,vec3(0.,0.,0.006),vec3(0.048,0.048,0.005)));

    // Garden trees
    float noise = 1.+0.1*length(sin(pos*2000.0))+0.2*length(sin(pos*900.0));
    b0.xy = abs(b0.xy);
    b0.xy -= 0.02;
    b0.xy = abs(b0.xy);
    b0 -= vec3(0.01,0.01,0.02);
    rayDist = min(rayDist,cylinder_v(b0,vec3(0.,0.,-0.01),0.001,0.006));
    b0*=noise;
    rayDist = min(rayDist,sphere_v(b0,vec3(0.),0.008));

    // Parking
    vec3 b3 = pos2;
    b3.xy -= vec2(0.08,-0.08);
    b3 = abs(b3);
    rayDist = min(rayDist,box_v(b3,vec3(0.,0.,0.033),vec3(0.05,0.05,0.033)));
    rayDist = max(rayDist,-box_v(b3,vec3(0.,0.0,0.064),vec3(0.049,0.049,0.006)));
    rayDist = min(rayDist,box_v(b3,vec3(0.,0.,0.02),vec3(0.051,0.051,0.002)));
    rayDist = min(rayDist,box_v(b3,vec3(0.,0.,0.04),vec3(0.051,0.051,0.002)));
    rayDist = max(rayDist,-box_v(b3,vec3(0.022,0.,0.033),vec3(0.01,0.051,0.003)));
    rayDist = max(rayDist,-box_v(b3,vec3(0.,0.022,0.033),vec3(0.051,0.01,0.003)));
    rayDist = max(rayDist,-box_v(b3,vec3(0.022,0.,0.053),vec3(0.01,0.051,0.003)));
    rayDist = max(rayDist,-box_v(b3,vec3(0.,0.022,0.053),vec3(0.051,0.01,0.003)));

    // Square
    vec3 b4 = pos2;
    b4.xy -= vec2(0.08,-0.22);
    b4 = abs(b4);
    rayDist = min(rayDist,box_v(b4,vec3(0.,0.,0.003),vec3(0.05,0.05,0.003)));
    rayDist = max(rayDist,-box_v(b4,vec3(0.,0.,0.004),vec3(0.049,0.049,0.004)));
    rayDist = max(rayDist,-box_v(b4,vec3(0.,0.,0.004),vec3(0.051,0.01,0.004)));
    rayDist = max(rayDist,-box_v(b4,vec3(0.,0.,0.004),vec3(0.01,0.051,0.004)));

    vec3 cone = b4;
    vec3 stairs = b4;
    rayDist = min(rayDist,cylinder_v(b4,vec3(0.,0.,0.015),0.015,0.006));
    cone.xy += (cone.z-0.021);
    rayDist = min(rayDist,cylinder_v(cone,vec3(0.,0.,0.027),0.015,0.006));
    stairs.xy += floor(stairs.z * 800.0)/800.0;
    rayDist = min(rayDist,box_v(stairs,vec3(0.018,0.018,0.0),vec3(0.01,0.01,0.01)));
    rayDist = min(rayDist,box_v(stairs,vec3(0.00,0.0,0.01),vec3(0.01,0.01,0.02)));

    // Business building
    vec3 b5 = pos2;
    b5.xy -= vec2(-0.08,-0.22);
    b5.xy *= 1.+2.0*floor(b5.z * 50.0)/50.0;
    b5.xy *= rz2(b5.z);
    rayDist = min(rayDist,box_v(b5,vec3(0.,0.,0.15),vec3(0.05,0.05,0.15)));

    // Bird
    if (length(lPos) < 2.){
        lPos *= 0.1;
        lPos.x *= 2.0;
        float rep = 0.002;
        lPos.x = rep-abs(abs(lPos.x)-rep);
        float flap = sin(time*40.0+lPos.x*600.0);
        float feathers = -lPos.y*4000.;
        lPos.z += abs(mod((feathers),1.)-0.5)*0.2*lPos.z;
        feathers = -lPos.x*2000.;
        lPos.z += abs(mod((feathers),1.)-0.5)*0.2*lPos.z;
        lPos.x *= pow(abs(lPos.x*500.),2.);
        lPos.xz *= rz2(-.5);
        lPos.y += flap*0.0004;
        lPos.z -= 0.001;
        lPos.yz += 0.003;
        rep = -0.0001;
        lPos.y = rep-abs(abs(lPos.y)-rep);
        float size = 0.0005;
        rayDist = min(rayDist,sphere_v(lPos,vec3(0.002,0,lPos.z),size*((1.-pow(abs(lPos.z*200.),2.)))));
    }

    fog_g = pos.z;
    return rayDist;
}

vec4 GetNormal(vec3 pos, vec3 lpos, vec4 shipQuat, float time){
    vec2 e = vec2(0.003,0.) * length(pos-ro);
    float o = map_v(pos,lpos,time);
    return vec4(normalize(vec3(
        map_v(pos+e.xyy,lpos+Rotate(shipQuat,e.xyy),time) - o,
        map_v(pos+e.yxy,lpos+Rotate(shipQuat,e.yxy),time) - o,
        map_v(pos+e.yyx,lpos+Rotate(shipQuat,e.yyx),time) - o)),o);
}

void main(){
    float time = TIME * speed;
    vec2 uv = (gl_FragCoord.xy - RENDERSIZE.xy*0.5)/RENDERSIZE.yy;

    // Auto-animated camera
    vec3 camPos = vec3(
        3.0 * sin(time * 0.15),
        2.0 + sin(time * 0.1) * 1.5,
        time * 0.5 + 10.0
    );
    vec4 camQuat = BuildQuat(vec3(1.,0.,0.), 1.57);
    // Add gentle pitch/yaw
    camQuat = MulQuat(BuildQuat(vec3(0.,1.,0.), sin(time*0.12)*0.3), camQuat);
    camQuat = MulQuat(BuildQuat(vec3(1.,0.,0.), sin(time*0.08)*0.15), camQuat);

    vec3 dpos = Rotate(camQuat, vec3(0.,0.,0.1));

    vec3 rd = vec3(0.,0.,9.);
    rd = Rotate(BuildQuat(vec3(1,0,0),-uv.y*FOV),rd);
    rd = Rotate(BuildQuat(vec3(0,1,0),uv.x*FOV),rd);

    vec3 lro = vec3(0.,0.,-.1);
    vec3 lrd = rd;

    ro = camPos;
    rd = Rotate(camQuat,rd);

    vec3 mp = ro;
    vec3 lmp = lro;

    int i;
    for (i=0; i<maxStepRayMarching; i++){
        dist_g = map_v(mp, lmp+dpos*0.005, time-(length(ro-mp)/speedOfLight));
        if(dist_g < 0.0001) break;
        mp += rd*dist_g;
        lmp += lrd*dist_g;
    }

    float ma = 1.-float(i)/80.;

    vec4 pos = vec4(mp, ma);
    float height = fog_g;
    vec3 normal = GetNormal(pos.xyz, lmp+dpos*0.005, camQuat, time-(length(ro-pos.xyz)/speedOfLight)).xyz;

    vec3 lightPOV = vec3(1.,1.,1.);
    vec3 lightPOV2 = vec3(-1.,-1.,1.);
    vec3 lightPOV3 = vec3(0.,0.,1.);

    vec3 camDir = normalize(ro-pos.xyz);

    pos.w *= pos.w * pos.w;

    // Diffuse
    vec3 finalCol = (1.2+dot(normal,lightPOV)) * vec3(0.,.6,1.);
    finalCol +=  (1.2+dot(normal,lightPOV2)) * vec3(.5,.4,0.);
    finalCol +=  (1.2+dot(normal,lightPOV3)) * vec3(.5,.0,0.);
    finalCol *= 0.4;

    if (height < 0.0 && pos.w > 0.01)
        finalCol *= 0.5;
    else
        finalCol += pow(max(0.,dot(normal,camDir)),10.)*1.;

    vec3 fogCol = normalize(rd) + 1.8;
    float rayLgth = length(pos.xyz-ro) * 0.005;
    finalCol = mix(finalCol*pos.w, fogCol, rayLgth*0.5);

    gl_FragColor = vec4(min(vec3(1.),finalCol), 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Bird VS Mankind'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Bird VS Mankind.fs'), 'w') as f:
    f.write(content1)
print('Written Bird VS Mankind.fs')
print('Batch 20 complete: 1 shader written')
