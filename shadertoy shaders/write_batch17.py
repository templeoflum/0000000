import os

# --- Wriggly ---
# Buffer A has all rendering (tentacles with potential fields, blackbody radiation)
# Image pass is just blur post-process - skip it, use Buffer A directly
# Replaced iMouse camera with auto-orbiting camera
# Replaced textureLod bump with procedural noise
# Renamed: normal -> normal_v
# Removed DRAW_SLICE debug mode, motion blur line
content1 = r"""/*{
    "DESCRIPTION": "Tentacle creature with potential field separation and blackbody radiation.",
    "CREDIT": "huwbowles / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

struct CamData
{
    vec3 ro;
    vec3 rd;
};
void computePixelRay( in vec2 p, out CamData cam );
vec3 blackbody_v(float t);

// tentacle temperature (the bright pulses)
float tentTemp( float idx, float z )
{
    float time = TIME * speed;
    float phase = 8./(idx*.5+1.);
    float freq = 10./(idx*.4+1.);
    float s = .5+.5*sin(1.*z+freq*time + 0.*phase);
    return smoothstep(0.99,1.,s);
}

float ten_r;

float GetAngle( float i, float t )
{
    float time = TIME * speed;
    float amp = .75;
    t += amp*sin(1.*t + 4.*time + float(i));
    t += .5*time;
    float dir = mod(i,2.) < 0.5 ? 1. : -1.;
    return dir * (1./(.5*i+1.)+1.) * t + i/2.;
}

#define POS_CNT 5
vec2 pos_v[POS_CNT];

float Potential( int numNodes, vec2 x )
{
    if( numNodes == 0 ) return 0.;

    float res = 0.;
    float k = 8.;
    for( int i = 0; i < POS_CNT; i++ )
    {
        if( i == numNodes ) break;
        res += exp( -k * length( pos_v[i]-x ) );
    }
    return -log(res) / k;
}

void ComputePos_Soft( float t, float z )
{
    float a0 = GetAngle( 0., t );
    vec2 d0 = vec2(cos(a0),sin(a0));
    float r0 = ten_r;
    pos_v[0] = r0 * d0;

    for( int i = 1; i < POS_CNT; i++ )
    {
        float a = GetAngle( float(i), t );
        vec2 d = vec2(cos(a),sin(a));
        float r = ten_r;

        float bloat = tentTemp( float(i), z );

        for( int j = 0; j < 5; j++ )
        {
            r += 2.*ten_r/(1.-bloat*.2)-Potential(i,r*d);
        }

        pos_v[i] = r * d;
    }
}

// Procedural bump noise replacing textureLod
float procBump(vec2 U) {
    return fract(sin(dot(U, vec2(12.9898, 78.233))) * 43758.5453);
}

float dTentacle( vec3 a, vec3 b, vec3 x, out bool inTents, out float minIdx, out vec3 ori, out vec3 ri, out vec3 up )
{
    vec3 BA = b - a;
    float ba2 = dot( BA, BA );
    float t = dot( x - a, BA ) / ba2;
    ori = a + t*BA;

    float d2 = dot( x - ori, x - ori );
    float max_r = ten_r * (2.+float(POS_CNT));
    if( d2 > max_r )
    {
        inTents = false;
        return sqrt(d2) - (max_r-ten_r);
    }
    inTents = true;

    float ba = sqrt(ba2);
    vec3 BA_n = BA / ba;

    up = normalize( vec3(0.,1.,0.) - BA_n.y*BA_n );
    ri = cross( up, BA_n );

    vec2 off_local = vec2( dot( x - ori, ri ), dot( x - ori, up ) );

    float winding = 2.;
    ComputePos_Soft( winding * t * ba, x.z );
    float d = 1000.;
    for( int i = 0; i < POS_CNT; i++ )
    {
        float bloat = tentTemp( float(i), x.z );
        float di = (1.-.4*bloat)*length( off_local - pos_v[i] );
        if( di < d )
        {
            d = di;
            minIdx = float(i);
        }
    }

    float r = .25*ten_r;
    vec2 U = vec2(4.*t,.5);
    r *= sqrt( procBump(U) );
    return .2*(d - r);
}

float dScene( vec3 x, out bool inTents, out float minIdx, out vec3 o, out vec3 ri, out vec3 up )
{
    float dtent = dTentacle( vec3(0.,0.,-2.5), vec3(0.,0.,2.5), x, inTents, minIdx, o, ri, up );
    return dtent;
}

vec3 normal_v( vec3 p )
{
    vec2 dd = vec2(0.01,0.);
    bool dum; float dum2;
    vec3 o, dr, du;
    float c = dScene(p,dum,dum2,o,dr,du);
    return normalize(
        vec3( dScene(p+dd.xyy,dum,dum2,o,dr,du)-c, dScene(p+dd.yxy,dum,dum2,o,dr,du)-c, dScene(p+dd.yyx,dum,dum2,o,dr,du)-c )
        );
}

#define ZFAR 15.
#define RM_STEPS 70
float rayMarch( CamData cd, out float stepsInTents, out float minIdx, out vec3 o, out vec3 ri, out vec3 up )
{
    stepsInTents = 0.;
    float t = 0.;
    for( int i = 0; i < RM_STEPS; i++ )
    {
        if( t > ZFAR ) break;
        bool intents;
        float d = dScene( cd.ro + t*cd.rd, intents, minIdx, o, ri, up );
        if( abs(d) < 0.02 ) break;
        t += d;
        if( intents )
            stepsInTents += 1.;
    }

    return t;
}

void main()
{
    float time = TIME * speed;
    ten_r = 0.08;

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    uv = 2. * uv - 1.;
    uv.x *= RENDERSIZE.x/RENDERSIZE.y;

    vec4 fragColor = vec4(0.05);

    CamData cd;
    computePixelRay( uv, cd );

    float stepCnt;
    float minIdx;
    vec3 o, ri, up;
    float z = rayMarch( cd, stepCnt, minIdx, o, ri, up );

    if( z < ZFAR )
    {
        vec3 pt = cd.ro + z*cd.rd;
        vec3 n = normal_v(pt);

        fragColor.xyz = vec3(.2);
        fragColor.xyz *= mix(0.5,1.,clamp( dot( n, -cd.rd ), 0., 1. ));

        float ao = 1. - .5*smoothstep( 0.1, .2, stepCnt/float(RM_STEPS) );
        fragColor = mix( fragColor, ao*fragColor, .4 );

        float alph = atan( n.y, n.x );
        alph += pt.z*7.;
        alph = mod( alph, 2.*3.141592654 );
        float onSpiral = smoothstep(0.2,0.,abs(fract(7.5*alph/(2.*3.141592654))-.5));
        fragColor.xyz *= mix( 1., .8, onSpiral );

        float temp = tentTemp( minIdx, pt.z );
        fragColor.xyz += 2.*max(1.-onSpiral,0.05) * blackbody_v(temp);

        int minIdxi = int(minIdx);
        for( int i = 0; i < POS_CNT; i++ )
        {
            if( i == minIdxi )
                continue;

            float tempi = tentTemp( float(i), pt.z );

            vec3 lpos = o + pos_v[i].x*ri + pos_v[i].y*up;
            vec3 l = lpos - pt;
            float ndotl = dot(n,l);
            if( ndotl > 0. )
            {
                ndotl = ndotl/length(l);
                fragColor.xyz += pow(tempi,2.) * .75 * ndotl * vec3(1.,.7,0.4);
            }
        }

        fragColor.xyz *= exp(-.1*z);
        fragColor.a = 1.;
    }
    else
    {
        fragColor.a = 0.;
    }

    // Background blend for transparent areas
    float uvr = 2.*length(gl_FragCoord.xy/RENDERSIZE.xy - .5);
    vec3 bg = .15-.07*vec3(uvr);
    bg.r *= .75;
    fragColor.xyz = mix(bg, fragColor.xyz, fragColor.a);
    fragColor.xyz *= 2.;

    gl_FragColor = vec4(fragColor.xyz, 1.0);
}

void computePixelRay( in vec2 p, out CamData cam )
{
    float time = TIME * speed;
    float camRadius = 3.8;
    // Auto-orbiting camera
    float theta = time * 0.3;
    float xoff = camRadius * cos(theta);
    float zoff = camRadius * sin(theta);
    cam.ro = vec3(xoff, 3. + 0.5*sin(time*0.2), zoff);

    vec3 target = vec3(0.,0.,0.);

    vec3 fo = normalize(target-cam.ro);
    vec3 ri = normalize(vec3(fo.z, 0., -fo.x ));
    vec3 up = normalize(cross(fo,ri));

    float fov = .45;
    cam.rd = normalize(fo + fov*p.x*ri + fov*p.y*up);
}

#define TEMPERATURE 3800.
vec3 blackbody_v(float t)
{
    t *= TEMPERATURE;

    float u = ( 0.860117757 + 1.54118254e-4 * t + 1.28641212e-7 * t*t )
            / ( 1.0 + 8.42420235e-4 * t + 7.08145163e-7 * t*t );

    float v = ( 0.317398726 + 4.22806245e-5 * t + 4.20481691e-8 * t*t )
            / ( 1.0 - 2.89741816e-5 * t + 1.61456053e-7 * t*t );

    float x = 3.0*u / (2.0*u - 8.0*v + 4.0);
    float y = 2.0*v / (2.0*u - 8.0*v + 4.0);
    float z = 1.0 - x - y;

    float Y = 1.0;
    float X = Y / y * x;
    float Z = Y / y * z;

    mat3 XYZtoRGB = mat3(3.2404542, -1.5371385, -0.4985314,
                        -0.9692660,  1.8760108,  0.0415560,
                         0.0556434, -0.2040259,  1.0572252);

    return XYZtoRGB * vec3(X,Y,Z) * pow(t * 0.0004, 4.0);
}
"""

path1 = r'C:\Users\User\Documents\Resolume Wire\Patches\Wriggly'
os.makedirs(path1, exist_ok=True)
with open(os.path.join(path1, 'Wriggly.fs'), 'w') as f:
    f.write(content1)
print('Written Wriggly.fs')
print('Batch 17 complete: 1 shader written')
