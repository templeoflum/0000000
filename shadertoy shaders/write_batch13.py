import os

# --- Terrian ---
# Merged Buffer A (terrain renderer) + Image (vignette) into single pass
# Replaced texcube(iChannel1,...) with procedural noise coloring
# Removed #ifdef AA temporal accumulation block
# Replaced min(0,iFrame) with 0 in loop bounds
# Pre-computed sun_dir normalize() for const global
content1 = r"""/*{
    "DESCRIPTION": "Terrain with water, clouds, and procedural materials.",
    "CREDIT": "EvilRyu / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define PI 3.14159265

float hash1(vec2 p)
{
    p  = 50.0*fract( p*0.3183099 );
    return fract( p.x*p.y*(p.x+p.y) );
}

float noise(vec2 x)
{
    vec2 p = floor(x);
    vec2 w = fract(x);
    vec2 u = w*w*w*(w*(w*6.0-15.0)+10.0);

    float a = hash1(p+vec2(0,0));
    float b = hash1(p+vec2(1,0));
    float c = hash1(p+vec2(0,1));
    float d = hash1(p+vec2(1,1));

    return -1.0+2.0*(a + (b-a)*u.x + (c-a)*u.y + (a - b - c + d)*u.x*u.y);
}

const mat2 m2 = mat2(  0.80,  0.60,
                      -0.60,  0.80 );

float cloud(vec2 x)
{
    float f = 2.;
    float s = 0.5;
    float a = 0.0;
    float b = 0.5;
    for(int i=0; i<3; i++)
    {
        float n = noise(x);
        a += b*n;
        b *= s;
        x = f*m2*x;
    }
    return a;
}

float terrian(vec2 p)
{
    p*=0.0045;
    float f = 2.;
    float s = 0.5;
    float a = 0.0;
    float b = 0.5;
    for(int i=0; i<9; i++)
    {
        float n = noise(p);
        a += b*n;
        b *= s;
        p = f*m2*p;
    }

    a=smoothstep(-0.5,0.7,a);

    return a*300.;
}

vec3 terrian_normal(vec2 pos, float t)
{
    vec2 e = vec2(0.001*t,0.0);
    return normalize(vec3(terrian(pos-e.xy)-terrian(pos+e.xy),
                           2.0*e.x,
                           terrian(pos-e.yx)-terrian(pos+e.yx)));
}

float march_terrian(vec3 ro, vec3 rd, float tmin, float tmax)
{
    float t = tmin;
    vec3 p=ro+t*rd;
    float d=p.y-terrian(p.xz);

    float sgn=sign(d);
    float told=t;
    bool bisect=false;

    for (int i=0;i<256;i++)
    {
        if(abs(d)<0.002*t || t>tmax) break;
        if(sign(d)!=sgn)
        {
            bisect=true;
            break;
        }

        told=t;
        if(d>1.)t+=d*0.4;
        else t+=log(abs(d)+1.1)*1.;
        p=ro+t*rd;
        d=p.y-terrian(p.xz);
    }

    if(bisect)
    {
        float m = 0.;
        p=ro+told*rd;
        sgn=sign(p.y-terrian(p.xz));
        for(int i=0; i<6; i++)
        {
            m=(told+t)*.5;
            p=ro+rd*m;
            d=p.y-terrian(p.xz);
            if(abs(d)<0.002*t)break;
            d*sgn<0. ? t=m : told=m;
        }
        t=(told+t)*.5;
    }
    return t;
}

float water(vec2 p)
{
    float time = TIME * speed;
    p*=0.05;
    float f = 2.;
    float s = 0.4;
    float a = 0.0;
    float b = 0.5;
    for(int i=0; i<5; i++)
    {
        float n = noise(vec2(p.x+10.,p.y-time*2.));
        a += b*n;
        b *= s;
        p = f*m2*p;
    }
    return 3.*a;
}

vec3 water_normal(vec2 pos, float t)
{
    vec2 e=vec2(1e-7*t*t*t,0.0);
    return normalize(vec3(water(pos-e.xy)-water(pos+e.xy),
                          2.0*e.x,
                          water(pos-e.yx)-water(pos+e.yx)));
}

float intersect_water(vec3 ro, vec3 rd)
{
    float t=2000.;
    if(rd.y <-0.01)
    {
        float t0=-(ro.y-20.)/rd.y;
        t=min(t,t0);
    }
    return t;
}

// Pre-computed: normalize(vec3(-1., 1.5, -.6)) = vec3(-1,1.5,-0.6)/1.9
const vec3 sun_dir = vec3(-0.526316, 0.789474, -0.315789);
const vec3 sun_col = vec3(2.0);

// Procedural rock/earth texture replacing texcube(iChannel1,...)
vec4 texcube_proc(vec3 p, vec3 n)
{
    float n1 = noise(p.xy * 3.7) * 0.5 + 0.5;
    float n2 = noise(p.xz * 5.3 + 1.7) * 0.5 + 0.5;
    float n3 = noise(p.yz * 7.1 + 3.1) * 0.5 + 0.5;
    vec3 col_xy = vec3(0.45 + 0.3*n1, 0.40 + 0.20*n1, 0.35 + 0.15*n1);
    vec3 col_xz = vec3(0.48 + 0.25*n2, 0.42 + 0.20*n2, 0.38 + 0.15*n2);
    vec3 col_yz = vec3(0.43 + 0.28*n3, 0.38 + 0.22*n3, 0.33 + 0.18*n3);
    return vec4(col_xy*abs(n.z) + col_xz*abs(n.y) + col_yz*abs(n.x), 1.0);
}

float bump_v(vec3 p, vec3 n)
{
    return dot(texcube_proc(0.25*p, n).xyz, vec3(0.299, 0.587, 0.114));
}

vec3 bump_mapping(vec3 p, vec3 n, float weight)
{
    vec2 e = vec2(2.0/RENDERSIZE.y, 0.0);
    vec3 g=vec3(bump_v(p-e.xyy, n)-bump_v(p+e.xyy, n),
                bump_v(p-e.yxy, n)-bump_v(p+e.yxy, n),
                bump_v(p-e.yyx, n)-bump_v(p+e.yyx, n))/(e.x*2.0);
    g=(g-n*dot(g,n));
    return normalize(n+g*weight);
}

float terrian_shadow(vec3 ro, vec3 rd, vec2 fragCoord)
{
    float res=1.0;
    float t=.5+0.5*hash1(fragCoord);
    float h;
    for(int i=0;i<20;i++)
    {
        vec3 p=ro+t*rd;
        h=p.y-terrian(p.xz);
        res=min(16.0*h/t, res);
        t+=clamp(h,1.+.1*t,30.);
        if(res<0.001*t)
            break;
    }
    return clamp(res, 0., 1.);
}

vec3 terrian_material(vec3 pos, vec3 n)
{
    float tree_pdf=smoothstep(0.,.5,n.y);
    tree_pdf*=1.-smoothstep(20.,50.,pos.y);
    vec3 mate=pow(texcube_proc(pos*0.008, n).xyz,vec3(3.));
    mate=mix(mate, .05*vec3(.7, 1., .2), tree_pdf);
    tree_pdf=smoothstep(0.2,.3,n.y)*smoothstep(50.,200.,pos.y);
    mate=mix(mate, .08*vec3(.5, 1., .2), tree_pdf);
    return mate;
}

vec3 render_terrian(vec3 ro, vec3 rd, float t, vec2 fragCoord)
{
    vec3 pos=ro+t*rd;
    vec3 n=terrian_normal(pos.xz, t);

    vec3 sky=vec3(0.2,0.7,1.);

    vec3 mate=terrian_material(pos, n);
    n=bump_mapping(pos*.1,n,0.15);
    float sha=terrian_shadow(pos+.5*n, sun_dir, fragCoord);
    float dif=max(0.,dot(n,sun_dir));
    float bac=max(0.,dot(n,-sun_dir));
    float amb=max(0.,dot(n,vec3(0,1,0)));
    vec3 Lo=6.0*dif*sun_col*sha;
    Lo+=0.5*bac*sun_col;
    Lo+=3.5*amb*sky;
    Lo*=smoothstep(-1.,10.,pos.y);
    return Lo*mate*0.2;
}

vec3 render_water(vec3 ro, vec3 rd, float t, float t1, vec2 fragCoord, vec3 sky)
{
    vec3 pos=ro+t*rd;
    vec3 n=water_normal(pos.xz, t);

    vec3 mate=vec3(.8,.9,1.)*0.5;

    float sha=terrian_shadow(pos+.1*n, sun_dir, fragCoord);
    float dif=max(0.,dot(n,sun_dir));
    float amb=max(0.,dot(n,vec3(0,1,0)));
    float fre=clamp(1.0+dot(rd,n), .0, 1.);
    vec3 refl=reflect(rd,n);
    float spe=max(0.0, pow(clamp(dot(sun_dir, refl), 0.0, 1.0), 5.0));

    vec3 Lo=4.0*dif*sun_col*sha;
    Lo+=1.*amb*sky;
    Lo+=2.5*pow(fre,8.)*vec3(1.);
    Lo+=2.5*spe*vec3(1.);
    vec3 col=Lo*mate*0.2;

    float t_terrian=march_terrian(pos+1.*n, refl, 0.5, 500.);
    vec3 reflcol=sky*.5;

    float falloff=0.;

    if(t_terrian<500.)
    {
        falloff=1.-smoothstep(0.5,500.,t_terrian);
        reflcol=.4*falloff*falloff*render_terrian(pos+1.*n, refl, t_terrian, fragCoord);
    }

    vec3 refrcol=render_terrian(ro, rd, t1, fragCoord);

    falloff=1.-smoothstep(0.5,500.,t1-t);
    col=mix(col,refrcol,falloff*falloff);

    col=mix(col, reflcol, fre);
    return col;
}

vec3 render_sky(vec3 ro, vec3 rd)
{
    vec3 col=0.9*vec3(0.4,0.65,1.0)-rd.y*vec3(0.4,0.36,0.4);

    float t=(1000.0-ro.y)/rd.y;
    if(t>0.0)
    {
        vec2 uv=(ro+t*rd).xz-vec2(4710.,235.);
        float cl=cloud(uv*0.0015);
        float dl=smoothstep(-0.2,0.6,cl);
        col=mix(col, vec3(1.0), 0.6*dl);
    }

    float sun=clamp(dot(sun_dir,rd), 0.0, 1.0);
    col+=0.6*vec3(1.0,0.6,0.3)*pow(sun, 32.0);

    return col;
}

vec3 scene_v(vec3 ro, vec3 rd, vec2 fragCoord, out float t)
{
    vec3 bg=vec3(.6,.8,1.1);
    vec3 col=render_sky(ro, rd);
    float t0=intersect_water(ro,rd);
    float t1=march_terrian(ro, rd, 50., 2000.);
    t=min(t0,t1);

    if(t>=2000.) return col;

    if(t1<t0)
    {
        col=render_terrian(ro, rd, t1, fragCoord);
    }
    else
    {
        col=render_water(ro, rd, t0, t1, fragCoord, col);
    }

    float sun=clamp(dot(sun_dir,rd), 0.0, 1.0);
    col+=0.25*vec3(1.0,0.4,0.2)*pow(sun, 4.0);
    col=mix(col,bg, 1.0-exp(-1.5e-7*t*t) );

    return col;
}

vec3 tonemap(vec3 x)
{
    const float a = 2.51;
    const float b = 0.03;
    const float c = 2.43;
    const float d = 0.59;
    const float e = 0.14;
    return (x * (a * x + b)) / (x * (c * x + d) + e);
}

mat3 camera_v(vec3 ro, vec3 ta)
{
    vec3 f=normalize(ta-ro);
    vec3 r=normalize(cross(f,vec3(0,1,0)));
    vec3 u=normalize(cross(r,f));
    return mat3(r,u,f);
}

void main()
{
    float time = TIME * speed;
    vec2 q=gl_FragCoord.xy/RENDERSIZE.xy;
    vec2 p=q*2.-1.;
    p.x*=RENDERSIZE.x/RENDERSIZE.y;
    vec3 ro=vec3(0.,100.,-time*100.);
    vec3 ta=ro+vec3(0,-0.1,-1.);

    mat3 cam=camera_v(ro, ta);
    vec3 rd=normalize(cam*vec3(p.xy,PI/2.));

    float t=0.;
    vec3 col=scene_v(ro,rd,gl_FragCoord.xy, t);

    col=tonemap(col);
    col=pow(clamp(col,0.0,1.0),vec3(0.45));
    col=pow(col,vec3(0.85,1.,0.95));

    // Vignette from Image pass
    col *= 0.5 + 0.5*pow( 16.0*q.x*q.y*(1.0-q.x)*(1.0-q.y), 0.05 );

    gl_FragColor = vec4(col, 1.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Terrian'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Terrian.fs'), 'w') as f:
    f.write(content1)
print('Written Terrian.fs')


# --- qexp lsd ---
# Used Buffer A code directly (pure math, no inputs needed)
# Skipped Image post-processing (Gaussian blur + fwidth edge detection)
# which requires float[] typed array and fwidth - both unsupported
content2 = r"""/*{
    "DESCRIPTION": "Quaternion exponential fractal with sphere inversion.",
    "CREDIT": "pb / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define rot(x) mat2(cos(x+vec4(0,11,33,0)))

#define H(h)  (  cos(  h/5. + 4.*vec3(1,3,2)   )*.8  )

#define R RENDERSIZE

#define ex exp(w.x)
#define cy cos(w.y)
#define sy sin(w.y)
#define cz cos(w.z)
#define sz sin(w.z)
#define cw cos(w.w)
#define sw sin(w.w)

void main() {
    vec2 U = gl_FragCoord.xy;
    vec3 c = vec3(0);
    vec4 rd = normalize( vec4(U-.5*R.xy, .6*R.y, 0.));

    float dotp_v, totdist=0., tt=TIME*speed;

    for (float i=0.; i<20.; i++) {

        vec4 p = vec4( rd*totdist) ;

        p.z  += 2.;
        p.x += 2.;
        p.y -= 5.;

        p.xz *= rot( 1.4*(1.+.2*sin(tt/9.) ) ) ;
        p.xy *= rot( -.6 * (1.+.2*sin(tt/11.)) ) ;

        vec4 w = vec4(0, 0, 3.*sin(tt/11.), 3.*cos(tt/11.));
        vec4 dz = vec4(0);
        vec4 z;

        for (float j=0.; j<4.; j++) {

                z = vec4(
                        ex*(cy*cz*cw - sy*sz*sw),
                        ex*(sy*cz*cw + cy*sz*sw),
                        ex*(cy*sz*cw - sy*cz*sw),
                        ex*(sy*sz*cw + cy*cz*sw)
                        );

                dz = vec4(z.x*dz.x-z.y*dz.y-z.z*dz.z-z.w*dz.w,
                          z.x*dz.y+z.y*dz.x+z.z*dz.w-z.w*dz.z,
                          z.x*dz.z-z.y*dz.w+z.z*dz.x+z.w*dz.y,
                          z.x*dz.w+z.y*dz.z-z.z*dz.y+z.w*dz.x);

                dz.x += 1. ;

                dotp_v = max(1./dot(z.xy,z.xy),.01);

                dz *= dotp_v;

                w = z * dotp_v + p ;

        }

        float ddz = clamp(dot(dz,dz),1e-3,1e5);
        float ddw = clamp(dot(w,w),1e-3,1e5);

        float dist_v = pow(ddw/ddz,.001) * log(ddw);

        float stepsize = dist_v/2.;
        totdist += stepsize;

        c += H( log(ddz) ) * exp(-i*i*dist_v*dist_v*1e-3);
    }

    c = 1. - exp(-c*c);
    gl_FragColor = vec4(c, 1.0);
}
"""

path2 = r'C:\Users\User\Documents\Resolume Wire\Patches\qexp lsd'
os.makedirs(path2, exist_ok=True)
with open(os.path.join(path2, 'qexp lsd.fs'), 'w') as f:
    f.write(content2)
print('Written qexp lsd.fs')


# --- Quaternion controls ---
# Replaced buffer-stored camera state with auto-animated orbit
# Replaced texelFetch reads with computed camera position
# Replaced fwidth(p)+0.001 with vec2(0.02) in checkersGradBox
# Removed keyboard input dependency
content3 = r"""/*{
    "DESCRIPTION": "Quaternion-controlled checkerboard plane with raymarching.",
    "CREDIT": "Zabidon / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

const float EPSILON_Q = 0.001;

float plane_v(vec3 p) {
    return p.y;
}

vec2 map_v(vec3 pos) {
    vec2 res = vec2(plane_v(pos), 1.0);
    return res;
}

float checkersGradBox( in vec2 p )
{
    // fwidth replaced with constant
    vec2 w = vec2(0.02);
    vec2 i = 2.0*(abs(fract((p-0.5*w)*0.5)-0.5)-abs(fract((p+0.5*w)*0.5)-0.5))/w;
    return 0.5 - 0.5*i.x*i.y;
}

vec2 marchRay(in vec3 ro, in vec3 rd) {
    float tmin = 1.0;
    float tmax = 30.0;

    float t = tmin;
    float m = -1.0;
    for (int i=0; i<64; i++) {
        float precis = 0.0004*t;
        vec2 res = map_v(ro+rd*t);
        if (res.x < precis || t > tmax) {
            break;
        }
        t += res.x;
        m = res.y;
    }

    if( t>tmax ) m=-1.0;
    return vec2( t, m );
}

void main() {
    float time = TIME * speed;

    // Auto-animated camera orbit
    float angle = time * 0.5;
    float radius = 5.0;
    vec3 position = vec3(radius * sin(angle), 1.5 + 0.5 * sin(time * 0.3), radius * cos(angle));

    vec3 target = vec3(0.0, 0.0, 0.0);
    vec3 forward = normalize(target - position);
    vec3 right_v = normalize(cross(forward, vec3(0.0, 1.0, 0.0)));
    vec3 up = cross(right_v, forward);

    vec3 ray = normalize(mat3(right_v, up, forward) * vec3(
        (gl_FragCoord.xy - RENDERSIZE.xy * 0.5) / RENDERSIZE.x,
        0.3
    ));

    vec3 backgroundColor = ray;

    vec2 factors = marchRay(position, ray);
    vec3 pos = position + factors.x * ray;

    vec3 color = vec3(checkersGradBox(pos.xz));
    float t = factors.x;
    color = mix( color, backgroundColor, 1.0-exp( -0.0002*t*t*t ) );
    gl_FragColor = vec4(color, 1.0);
}
"""

path3 = r'C:\Users\User\Documents\Resolume Wire\Patches\Quaternion controls'
os.makedirs(path3, exist_ok=True)
with open(os.path.join(path3, 'Quaternion controls.fs'), 'w') as f:
    f.write(content3)
print('Written Quaternion controls.fs')

print('Batch 13 complete: 3 shaders written')
