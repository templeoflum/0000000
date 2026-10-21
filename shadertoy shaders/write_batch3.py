import os

# --- Spinor Belt Trick ---
content1 = r"""/*{
    "DESCRIPTION": "Dirac belt trick demonstrating 3D rotation Z2 fundamental group with spinors.",
    "CREDIT": "cancrizans / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const float gamma_v = 2.2;
const vec3 gamma_vec = gamma_v * vec3(1.,1.,1.);
const vec3 col_x = pow(vec3(209., 48., 107.)/255., gamma_vec);
const vec3 col_y = pow(vec3(52., 235., 186.)/255., gamma_vec);
const vec3 col_z = pow(vec3(125., 57., 219.)/255., gamma_vec);
const vec3 col_sky = pow(vec3(0.2,0.2,0.2),gamma_vec);
const vec3 col_core = pow(vec3(0.8,.8,.8), gamma_vec);

vec2 rot2d(vec2 v, float angle){
    float s = sin(angle);
    float c = cos(angle);
    return vec2(c*v.x - s*v.y, s*v.x + c*v.y);
}

vec3 rot_v(vec3 v, float azimuth, float altitude){
    vec3 u = v;
    u.yz = rot2d(u.yz, altitude);
    u.xz = rot2d(u.xz, azimuth);
    return u;
}

vec2 smin_v( float a, float b, float k )
{
    float h = 1.0 - min( abs(a-b)/(4.0*k), 1.0 );
    float w = h*h;
    float m = w*0.5;
    float s = w*k;
    return (a<b) ? vec2(a-s,m) : vec2(b-s,1.0-m);
}

float sdf_box( vec3 p, vec3 b, float r )
{
  vec3 q = abs(p) - b + r;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0) - r;
}

vec4 imuli(vec3 v, vec3 w){
    return vec4(cross(v,w),-dot(v,w));
}

vec4 qmuli(vec4 q, vec3 v){
    return q.w * vec4(v,0.) + imuli(q.xyz, v);
}

vec4 qmulq(vec4 q, vec4 p){
    return q * p.w + qmuli(q,p.xyz);
}

vec4 qconj(vec4 q){
    return vec4(-q.xyz,q.w);
}

vec3 adjoint_v(vec4 q, vec3 x){
    return qmulq(qmuli(q, x), qconj(q) ).xyz;
}

struct Surface{
    float sdf;
    vec3 color;
};

Surface sunion(Surface a, Surface b){
    if (a.sdf < b.sdf) return a;
    return b;
}

Surface smooth_union(Surface a, Surface b, float k){
    vec2 smoothing = smin_v(a.sdf,b.sdf,k);
    return Surface(smoothing.x, mix(a.color, b.color, smoothing.y));
}

Surface sdf_axes(vec3 p){
    const float size_v = 0.5;
    const vec3 b = vec3(40.,size_v, size_v);
    const float r = 0.1;
    return sunion(
        Surface(sdf_box(p, b.xyz, r), col_x),
        sunion(
            Surface(sdf_box(p, b.yzx, r), col_y),
            Surface(sdf_box(p, b.zxy, r), col_z)
            )
        );
}

float rotation_angle_at_r2(float r2){
    return 6.28318530718 * smoothstep(0.,1.,1. /(1.+0.01*r2));
}

vec4 quaternion_at_r2(float r2, float lambda){
    float rangle = rotation_angle_at_r2(r2);
    float c = cos(rangle*0.5);
    float s = sin(rangle*0.5);
    float cl = cos(lambda);
    float sl = sin(lambda);
    vec4 base_q = vec4(cl*s,sl,0.,cl*c);
    vec4 q = base_q;
    q.wy = rot2d(q.wy, -lambda);
    return q;
}

Surface scene(vec3 pos, float time){
    float st = 2.*smoothstep(0.,1.,fract(0.65+0.1*time))-1.;
    float lambda = 1.57079632679 * (st*st*st);
    vec4 q = quaternion_at_r2(dot(pos,pos), lambda);
    vec3 x = adjoint_v(q,pos);
    Surface box_s = Surface(sdf_box(x, vec3(1.,1.,1.), 0.2), col_core);
    Surface axes = sdf_axes(x);
    Surface surf = smooth_union(box_s,axes,0.02);
    Surface sky = Surface( - (length(pos)-26.0), col_sky);
    surf = smooth_union(surf, sky,3.0);
    return surf;
}

const vec3 light_v = normalize(vec3(1.,-2.,0.3));

vec3 march(vec3 cam, vec3 ray, float time){
    float t = 2.0;
    int it=0;
    for (it=0; it<1000; it++){
        if (t > 100.) break;
        vec3 pos = cam + ray*t;
        Surface surf = scene(pos, time);
        float dist = surf.sdf;
        if (dist < 0.01){
            const float delta = 0.002;
            float ndotl = (scene(pos-delta*light_v, time).sdf-dist)/delta;
            float ao = pow(clamp(50./float(it),0.,1.),0.5);
            vec3 shading = 0.7*vec3(1.1,1.1,1.)*smoothstep(-0.3,1.0,ndotl)+ ao*vec3(0.4,0.4,0.7);
            return surf.color * shading;
        }
        t += 0.2*dist;
    }
    return vec3(1.,0.,1.);
}

void main()
{
    float time = TIME * speed;
    vec2 viewport = (gl_FragCoord.xy - 0.5*RENDERSIZE.xy)/RENDERSIZE.y;
    vec3 cam = vec3(0.,0.,-25.);
    vec3 ray = normalize(vec3(viewport, 1.5));
    float azimuth = 0.7 + time * 0.0425;
    float altitude = 0.4;
    cam = rot_v(cam, azimuth, altitude);
    ray = rot_v(ray, azimuth, altitude);
    vec3 col = march(cam,ray, time);
    gl_FragColor = vec4(pow(col,1./gamma_v * vec3(1.,1.,1.)),1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Spinor Belt Trick'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Spinor Belt Trick.fs'), 'w') as f:
    f.write(content1)
print('Written Spinor Belt Trick.fs')

# --- 4D Rounded box (Bluey) ---
content2 = r"""/*{
    "DESCRIPTION": "Raymarched 3D hyperslice of a 4D rounded box with quaternion rotation.",
    "CREDIT": "ollj + iq / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define blueBright (vec3(127,200,245)/255.)
#define grey vec3(1.,.8,.6)

#define dd(a) dot(a,a)
#define sat(a) clamp(a,0.,1.)

float sdBox(vec4 p,vec4 b){p=abs(p)-b;
 return min(max(max(p.x,p.y),max(p.z,p.w)),0.)+dd(max(p,0.));}

mat4 q2m(vec4 q){return mat4(q.x,-q.y,-q.z,-q.w,q.y, q.x,-q.w, q.z
                            ,q.z, q.w, q.x,-q.y,q.w,-q.z, q.y, q.x);}

float map_f(vec3 pos, float time
){vec4 p = vec4(pos,0.5*sin(time*0.513));
 vec4 a=normalize(cos(.2*time*vec4(1.0,1.7,1.1,1.5)+vec4(0.0,1.0,5.0,4.0)));
 vec4 b=normalize(cos(.2*time*vec4(1.9,1.7,1.4,1.3)+vec4(3.0,2.0,6.0,5.0)));
 p=q2m(b)*p*q2m(a);
 return sqrt(sdBox(p,vec4(.8,.5,.7,.2)))-.16;
 }

vec3 calcNormal(vec3 u,in float t
){vec2 e=vec2(1.,-1.)*.5773;const float p=.00025;
 return normalize(e.xyy*map_f(u+e.xyy*p,t)+e.yyx*map_f(u+e.yyx*p,t)
                 +e.yxy*map_f(u+e.yxy*p,t)+e.xxx*map_f(u+e.xxx*p,t));}

float calcSoftshadow(vec3 u,vec3 d,float a,float b,float t
){float r=1.,m=a;
 for(int i=0;i<32;i++
 ){float h=map_f(u+d*m,t);r=min(r,16.*h/m);m+=clamp(h,.01,.25);if(r<.001||m>b)break;}
  return sat(r);}

vec2 intersect( in vec3 ro, in vec3 rd, in float time
){vec2 res = vec2(1e20,-1.0);
 {float t = (-1.0-ro.y)/rd.y;if( t>0.0 ) res = vec2(t,1.0);}
 {float tmax = min(6.0,res.x);
  float t = 0.4;
  for( int i=0; i<128; i++
  ){vec3 pos = ro + t*rd;
   float h = map_f(pos, time);
   if( h<0.001 || t>tmax ) break;
   t += h;
   }
  if( t<tmax && t<res.x ) res = vec2(t,2.0);
  }
  return res;}

float checkersGradBox( in vec2 p, in vec2 dpdx, in vec2 dpdy ){
    vec2 w = abs(dpdx)+abs(dpdy) + 0.001;
    vec2 i = 2.0*(abs(fract((p-0.5*w)*0.5)-0.5)-abs(fract((p+0.5*w)*0.5)-0.5))/w;
    return 0.5 - 0.5*i.x*i.y;
}

void main()
{
    float time = TIME * speed;
    vec3 tot = vec3(0.0);
    vec2 p = (2.0*gl_FragCoord.xy-RENDERSIZE.xy)/RENDERSIZE.y;

    vec3 ro = vec3(-0.5,0.0,2.5);
    vec3 rd = normalize( vec3(p,-1.8) );
    vec2 px = (-RENDERSIZE.xy+2.0*(gl_FragCoord.xy+vec2(1.0,0.0)))/RENDERSIZE.y;
    vec2 py = (-RENDERSIZE.xy+2.0*(gl_FragCoord.xy+vec2(0.0,1.0)))/RENDERSIZE.y;
    vec3 rdx = normalize( vec3(px,-1.8) );
    vec3 rdy = normalize( vec3(py,-1.8) );

    vec2 tm = intersect( ro, rd, time );
    vec3 col = vec3(0.6,0.75,0.85) - 0.97*rd.y;
    if( tm.y>0.0 ){
        vec3 pos = ro + tm.x*rd;
        vec3 nor = (tm.y<1.5)?vec3(0.0,1.0,0.0):calcNormal(pos,time);
        vec3 color_v=blueBright;
        vec3 lig = normalize(vec3(0.8,0.4,0.6));
        float dif = clamp( dot(nor,lig), 0.0, 1.0 );
        vec3  hal = normalize(lig-rd);
        float sha = calcSoftshadow( pos+0.001*nor, lig, 0.001, 4.0, time );
        float amb = 0.6 + 0.4*nor.y;
        float bou = clamp(-nor.y,0.0,1.0);
        float spe = clamp(dot(nor,hal),0.0,1.0);
        col  = color_v*dif*sha*3.5;
        col += vec3(0.12,0.18,0.24)*amb*4.;
        col += vec3(0.30,0.20,0.10)*bou*2.;

        if( pos.y<-.99 ){
            vec3 dpdx = ro.y*(rd/rd.y-rdx/rdx.y);
            vec3 dpdy = ro.y*(rd/rd.y-rdy/rdy.y);
            float f = checkersGradBox( 2.0*pos.xz, 2.0*dpdx.xz, 2.0*dpdy.xz );
            col *= 0.2 + f*vec3(0.05);
        }
        else col *= 0.25;

        col += 0.2*pow(spe,8.0)*dif*sha;
        col = mix( col, vec3(0.6,0.7,0.8), 1.0-exp(-0.001*tm.x*tm.x) );
    }

    tot += col;
    tot = pow( tot, vec3(0.45) );
    tot = clamp(tot,0.0,1.0);
    tot = tot*tot*(3.0-2.0*tot);

    gl_FragColor = vec4( tot, 1.0 );
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\4D Rounded box (Bluey)'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, '4D Rounded box (Bluey).fs'), 'w') as f:
    f.write(content2)
print('Written 4D Rounded box (Bluey).fs')
