import os

# --- Riftborn Flythrough ---
# Merged Buffer A rendering into single ISF pass.
# Camera steering replaced with auto-animated flight path.
# Removed keyboard/mouse/buffer/texture dependencies.
content1 = r"""/*{
    "DESCRIPTION": "Fractal flythrough with truchet octree and Mandelbox shapes.",
    "CREDIT": "eiffie / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define subscale 6.
#define steps 100
#define maxdistance 4.0
#define epsilon 0.003
#define limit 3.0
#define HASHSCALE3 vec3(.6531, .5563, .7498)
#define dot2(p) dot(p,p)
#define eps .00001
#define iterRm 256
#define zFar 80.
#define iterAO 8.
#define iterDfFractal 4.
#define sat(a) clamp(a,.0,1.)

float hash13(vec3 p3){
    p3 = fract(p3 * HASHSCALE3);
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z*15.3023+0.434);
}

#define checktree(k) \
for (j = 0.0; j < k; j++) { \
    vec3 h = floor(r*exp2(j))*exp2(-j); \
    float rand = hash13(h+exp2(-j-1.0)); \
    if (rand >= 0.5) { break; } \
}

float squarering(vec3 p) {
    vec2 q = vec2(abs(length(p.xy)-0.5),abs(p.z));
    float len = length(max(q-0.1667,0.0))+min(max(q.x,q.y)-0.1667,0.0);
    return len;
}

float truchet(vec3 p, int type) {
    vec3 q = abs(p-0.5);
    vec3 q2 = vec3(min(min(q.x,q.y),q.z),0,max(max(q.x,q.y),q.z));
    q = min(q,q.yzx);
    q2.y = max(max(q.x,q.y),q.z);
    float inside = length(abs(q2.yz-vec2(0.0,0.5)))-0.1667;
    float inside2 = length(max(abs(q2.yz-vec2(0.0,0.5)),0.0))-0.1667;
    float outside = length(abs(q2.yz-vec2(0.5,0.5)))-0.3333;
    float len;
    if (type == 0) { len = inside; }
    else if (type == 1) { len = -outside; }
    else if (type == 2) { len = inside2; }
    else {
        len = squarering(p.xyz-vec3(0,0,0.5));
        len = min(len, squarering(p.yzx-vec3(1,0,0.5)));
        len = min(len, squarering(p.zxy-vec3(1,1,0.5)));
    }
    return len;
}

float mapOcreeeTruchet(vec3 p) {
    vec3 fp, lp;
    float len, i, size = 1.0;
    vec3 r = p;
    float j;
    checktree(limit);
    i = j;
    fp = floor(p*exp2(i))*exp2(-i);
    lp = fract(p*exp2(i));
    int type = int(hash13((fp+exp2(-i-1.0))*vec3(0.93,0.89,1.23))*4.0);
    len = truchet(lp,type)*exp2(-i);
    while (i <= limit) {
        fp = floor(p*exp2(i))*exp2(-i);
        lp = fract(p*exp2(i));
        vec3 p2 = p*exp2(i);
        vec3 fp2 = floor(p2-0.5);
        for(int x = 0; x <= 1; x++) {
            for(int y = 0; y <= 1; y++) {
                for(int z = 0; z <= 1; z++) {
                    r = (fp2+vec3(x,y,z))*exp2(-i);
                    if (r != fp) {
                        checktree(i);
                        if (i==j) {
                            vec3 q = abs(p2-fp2-vec3(x,y,z)-0.5);
                            vec3 q2 = vec3(min(min(q.x,q.y),q.z),0,max(max(q.x,q.y),q.z));
                            q = min(q,q.yzx);
                            q2.y = max(max(q.x,q.y),q.z);
                            float outside = length(abs(q2.yz-vec2(0.5,0.5)))-0.3333;
                            len = max(-outside*exp2(-i),len);
                        }
                    }
                }
            }
        }
        size *= 0.5;
        len *= -1.0;
        i++;
    }
    return len;
}

const vec3 sunDir=normalize(vec3(0.7,1.0,-0.7));
const vec3 sunColor=vec3(1.0,0.99,.9);
const vec3 skyColor=vec3(.25,.26,.27);

vec3 Backdrop(in vec3 rd){
    vec3 a = skyColor
        +.05*(rd+sin(rd.yzx*5.+2.4*sin(rd.zxy*3.0)))
        +sunColor*(max(0.0,dot(rd,sunDir))*0.2+pow(max(0.0,dot(rd,sunDir)),256.));
    return .7*a;
}

#define PI acos(-1.)
#define TAU (PI*2.)
#define RID(p,r) (floor((p+r/2.)/r))
#define REP(p,r) (mod(p+r/2., r) - r/2.)

float hash_v(float n){return fract(sin(n)*43758.5453);}

float noise_v(in vec3 x){
    vec3 p=floor(x);
    vec3 f=fract(x);
    f=f*f*(3.-2.*f);
    float n=p.x+p.y*57.+113.*p.z;
    float res=mix(mix(mix(hash_v(n+0.),hash_v(n+1.),f.x),
                      mix(hash_v(n+57.),hash_v(n+58.),f.x),f.y),
                  mix(mix(hash_v(n+113.),hash_v(n+114.),f.x),
                      mix(hash_v(n+170.),hash_v(n+171.),f.x),f.y),f.z);
    return res;
}

mat2 rot(float a){
    float ca=cos(a); float sa=sin(a);
    return mat2(ca,-sa,sa,ca);
}

float sdPlane(vec3 p, vec4 n){return dot(p,n.xyz)-n.w;}

float solid(vec3 p, float s){
    float dist_v=-1000.;
    vec3 dir=vec3(0,1,0);
    float h=3., v=6.;
    mat2 hr=rot(TAU/h);
    mat2 vr=rot(TAU/v);
    for(float jj=0.;jj<v;++jj){
        for(float ii=0.;ii<h;++ii){
            float ran=(hash_v(s+jj*ii)-.5);
            dist_v=max(dist_v,sdPlane(p, vec4(dir,1.+ran)));
            dir.xz*=hr;
        }
        dir.yz*=vr;
    }
    return dist_v;
}

float gd(vec3 p){
    float time = TIME * speed;
    p*=subscale;
    vec3 pid=RID(p, 80.);
    p=REP(p, 80.);
    p.xy*=rot(pid.z*.5);
    p.zy*=rot(pid.x*.5);
    p.xz*=rot(pid.y*.5);
    p.z-=time;
    p.y+=2.;
    p.xy*=rot(p.z*.1);
    p.y-=2.;
    p.xy*=rot(time*.05);
    float dist_v=1000.;
    p*=2.;
    float r=6.;
    vec3 id=RID(p, r);
    p=REP(p, r);
    float nois=noise_v(id);
    float t=time*(nois+.2);
    p.xz*=rot(t);
    p.xy*=rot(t*.5);
    p.yz*=rot(t*.25);
    dist_v=solid(p,nois)*.25;
    dist_v=max(dist_v,length(id.xy)-2.);
    return dist_v/subscale;
}

vec3 Tile(vec3 p){
    vec3 a=vec3(8.0);
    return abs(mod(p,a)-a*0.5)-a*0.25;
}

float DERect(vec4 z,vec3 r){return length(max(abs(z.xyz)-r,0.0))/z.w;}
const float mr=0.5, mxr=0.975, scale_f = 2.52;
const vec3 rc=vec3(3.31,2.79,4.11), rcL=vec3(2.24,1.88,2.84);
const vec4 p0=vec4(4.0,0.0,-4.0,1.0);

float gd1(vec3 p, inout vec4 mcol){
    p=Tile(p);
    vec4 z=vec4(p,1);
    float dG=1e3;
    vec4 mc=vec4(0);
    for(float n=.0;n<5.;n++){
        z.xyz=clamp(z.xyz,-1.0,1.0)*2.0-z.xyz;
        z*=scale_f/clamp(max(dot(z.xy,z.xy),max(dot(z.xz,z.xz),dot(z.yz,z.yz))),mr,mxr);
        z+=p0;
        if(n==3.)mc=vec4(vec3(.5,.3,.2)+z.xyz*.05,.25);
        else if(n==2.)dG=DERect(z,rcL);
    }
    float ds=DERect(z,rc);
    if(dG<ds)mcol+=vec4(0.5,0.6,0.9,0.9)+vec4(z.xyz*0.025,0.0);
    else mcol+=mc;
    return min(dG,ds);
}

vec3 fog_v(float ts,vec3 spc,vec3 fcol){
    float f=min(pow(ts*20./zFar*.2,1.33)*.54,1.);
    return mix(spc,fcol,f);
}

float AO(in vec3 o,in vec3 d,float s){
    float t=.0,a=1.,f,n=.01+.04*s;
    for(float i=.0;i<iterAO;i++){
        f=max(gd(o+d*t)*1.5,n);
        a=min(a,f/t+t*0.5);
        t+=f;
    }
    return a;
}

vec3 SpecOcc(vec3 r,vec3 d,vec3 N,vec3 so,vec3 o,float s,vec4 mcol){
    float l=dot(N,sunDir);
    float shad=AO(so+N*.001,sunDir,s);
    float v=dot(-d,N);
    vec3 cc=vec3(.6,.8,1);
    vec3 lc=vec3(1,.8,.6);
    float cd=exp(-distance(o,so));
    vec3 R=reflect(d,N);
    float spcl=pow(sat(dot(R,sunDir)),10.);
    float spcc=pow(max(.0,dot(R,-d)),1.+cd)*.25;
    r=r*(cd*v*cc+shad*l*lc)+(cd*spcc*cc+shad*spcl*lc)*mcol.a;
    r=sat(r);
    return r;
}

vec3 scene_v(vec3 o,vec3 d,float s){
    float g=gd(o)*s*.5;
    float t=g, ao=1.;
    float f=2./min(RENDERSIZE.x,RENDERSIZE.y);
    vec4 gs_v=vec4(1e6), ts=vec4(-1);
    for(int i=0;i<iterRm;i++){
        g=gd(o+d*t);
        bool ps=g<min(f*t,ao) && ts.w<0.0;
        if(ps){
            gs_v=vec4(abs(g),gs_v.xyz);
            ts=vec4(t,ts.xyz);
        }
        t+=g;
        ao=g;
        if(t>zFar||g<eps)break;
    }
    if(g<f*t && g<gs_v.x){gs_v.x=g;ts.x=t;}
    vec3 c=Backdrop(d);
    vec3 fcol=c;
    for(int i=0;i<4;i++){
        if(ts.x<.0)break;
        float px=f*ts.x;
        vec3 so=o+d*ts.x;
        vec4 mcol=vec4(.0);
        #define g3(a) vec3(gd1(so+a.xyy,mcol),gd1(so+a.yxy,mcol),gd1(so+a.yyx,mcol))
        vec3 ve=vec3(px,0,0);
        vec3 dp=g3(ve), dn=g3(-ve);
        float d1=gd1(so,mcol);
        vec3 N=(dp-dn)/(length(dp-vec3(d1))+length(vec3(d1)-dn));
        vec3 spc=mcol.rgb*0.14;
        spc=SpecOcc(spc,d,N,so,o,s,mcol);
        spc=fog_v(ts.x,spc,fcol);
        c=mix(spc,c,sat(gs_v.x/px));
        gs_v=gs_v.yzwx; ts=ts.yzwx;
    }
    return sat(c*2.);
}

// Quaternion math for camera
vec4 qid(){return vec4(0,0,0,1);}
vec4 qmulq(vec4 q1, vec4 q2){
    return vec4(q1.xyz*q2.w+q2.xyz*q1.w+cross(q1.xyz,q2.xyz),
                q1.w*q2.w-dot(q1.xyz,q2.xyz));
}
vec4 qinv(vec4 q){return vec4(-q.xyz,q.w)/dot(q,q);}
vec3 qmulv(vec4 q, vec3 p){return qmulq(q,qmulq(vec4(p,.0),qinv(q))).xyz;}
vec4 aa2q(vec3 axis, float angle){return vec4(normalize(axis)*sin(angle*0.5),cos(angle*0.5));}

float h12(in vec2 p){
    return fract(TIME*60.0+sin(dot(p,vec2(13.3145,17.7391)))*317.7654321);
}

void main(){
    float time = TIME * speed;
    vec2 uv = (2.0*gl_FragCoord.xy - RENDERSIZE.xy)/RENDERSIZE.y;
    vec3 rd = normalize(vec3(uv, 1.0));

    // Auto-animated camera path
    float angle = time * 0.12;
    float radius = 2.0 + sin(time * 0.07) * 1.5;
    vec3 ro = vec3(
        radius * sin(angle),
        1.0 + sin(time * 0.09) * 1.5,
        time * 0.3
    );

    // Camera orientation from flight direction
    vec3 target = vec3(
        (2.0 + sin((time+0.5) * 0.07) * 1.5) * sin(angle + 0.12*0.5),
        1.0 + sin((time+0.5) * 0.09) * 1.5,
        (time+0.5) * 0.3
    );
    vec3 fw = normalize(target - ro);
    vec3 right_v = normalize(cross(fw, vec3(0,1,0)));
    vec3 up = cross(right_v, fw);
    rd = normalize(rd.x * right_v + rd.y * up + rd.z * fw);

    float s = h12(gl_FragCoord.xy);
    gl_FragColor = vec4(scene_v(ro, rd, s), 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Riftborn Flythrough'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Riftborn Flythrough.fs'), 'w') as f:
    f.write(content1)
print('Written Riftborn Flythrough.fs')

print('Batch 16 complete: 1 shader written')
