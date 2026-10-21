import os

content = """/*{
    "DESCRIPTION": "Heptanion dual-quaternion compression with gizmo visualization.",
    "CREDIT": "ENDESGA / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

#define tau 6.283185307179586476925286766559
#define e_const (exp(1.))
#define E(x) ((e_const - exp(1. - x)) / (e_const - 1.))

#define quat vec4
#define lquat vec3

quat quat_add( quat a, quat b ) { return quat( a.xyz + b.xyz, a.w + b.w ); }
quat quat_mul( quat a, quat b ) { return quat( a.w * b.xyz + b.w * a.xyz + cross( a.xyz, b.xyz ), a.w * b.w - dot( a.xyz, b.xyz ) ); }

quat new_quat( vec3 axis, float angle ) {
    return quat( normalize( axis ) * sin( angle / 2. ), cos( angle / 2. ) );
}

lquat quat_to_lquat( quat q ) {
    float a = acos( clamp( q.w, -1.0, 1.0 ) );
    float sina = sin( a );
    if( sina < .0001 ) return lquat( 0 );
    return normalize( q.xyz ) * a;
}

quat lquat_to_quat( lquat lq ) {
    float len = length( lq );
    if( len < .0001 ) return quat( 0, 0, 0, 1 );
    return quat( normalize( lq ) * sin( len ), cos( len ) );
}

struct hepta {
    lquat r;
    quat d;
};

lquat lquat_mul( lquat a, lquat b ) {
    float l = length( a );
    quat q1 = quat( normalize( a ) * sin( l ), cos( l ) );
    l = length( b );
    vec3 axis2 = ( l < .0001 ) ? vec3( 0 ) : normalize( b );
    quat q2 = quat( axis2 * sin( l ), cos( l ) );
    return normalize( q1.w * q2.xyz + q2.w * q1.xyz + cross( q1.xyz, q2.xyz ) ) *
        acos( clamp( q1.w * q2.w - dot( q1.xyz, q2.xyz ), -1.0, 1.0 ) );
}

hepta hepta_mul( hepta a, hepta b ) {
    return hepta( a.r + b.r, quat_add( quat_mul( lquat_to_quat( a.r ), b.d ), quat_mul( a.d, lquat_to_quat( b.r ) ) ) );
}

hepta hepta_trans( hepta a, hepta b ) {
    return hepta( lquat_mul( a.r, b.r ), quat_add( quat_mul( lquat_to_quat( a.r ), b.d ), quat_mul( a.d, lquat_to_quat( b.r ) ) ) );
}

vec3 vec_trans( vec3 p, hepta d ) {
    return hepta_mul( hepta_mul( d, hepta( lquat( 0 ), quat( p, 0 ) ) ), hepta( -d.r, quat( d.d.xyz, -d.d.w ) ) ).d.xyz;
}

hepta hepta_slerp( hepta dq1, hepta dq2, float t ) {
    quat dq1r = lquat_to_quat( dq1.r );
    quat dq2r = lquat_to_quat( dq2.r );
    float dp = dot( dq1r, dq2r );
    if( dp < 0. ) { dq1r = -dq1r; dq1.d = -dq1.d; dp = -dp; }
    float o = acos( clamp( dp, -1., 1. ) );
    float iso = 1./sin( o );
    if( iso > 10000. ) { dq1r = mix( dq1r, dq2r, t ); dq1.d = mix( dq1.d, dq2.d, t ); }
    else {
        float s1 = sin( ( 1. - t ) * o ) * iso;
        float s2 = sin( t * o ) * iso;
        dq1r = s1 * dq1r + s2 * dq2r;
        dq1.d = s1 * dq1.d + s2 * dq2.d;
    }
    dq1.r = quat_to_lquat( dq1r );
    return dq1;
}

hepta new_hepta_ypr( float yaw, float pitch, float roll, vec3 pos ) {
    quat dir = quat_mul( new_quat( vec3( 0, 0, 1 ), yaw ),
        quat_mul( new_quat( vec3( 1, 0, 0 ), pitch ), new_quat( vec3( 0, 1, 0 ), roll ) ) );
    return hepta( quat_to_lquat( dir ), quat_mul( quat( pos, 0 ), dir ) * .5 );
}

hepta new_hepta( vec3 axis, float angle, vec3 pos ) {
    quat dir = new_quat( axis, angle );
    return hepta( quat_to_lquat( dir ), quat_mul( quat( pos, 0 ), dir ) * .5 );
}

vec3 light_dir = vec3( 0 );

void sphere_h( vec3 ro, vec3 rd, vec3 pos, float rad, vec3 rgb, inout vec4 rgbd ) {
    vec3 oc = ro - pos;
    float b = dot( oc, rd );
    float c = dot( oc, oc ) - rad * rad;
    float h = b * b - c;
    if( h < 0. ) return;
    h = sqrt( h );
    float t = -b - h;
    vec3 p = ro + t * rd;
    vec3 normal = normalize( p - pos );
    float diff = max( dot( normal, light_dir ), .2 );
    float d = 1. - ( 1. / distance( ro, p ) );
    if( d <= rgbd.w ) { rgbd.w = d; rgbd.rgb = diff * rgb; }
}

void cylinder_h( vec3 ro, vec3 rd, vec3 pos_a, vec3 pos_b, float rad, vec3 rgb, inout vec4 rgbd ) {
    vec3 ba = pos_b - pos_a;
    vec3 oa = ro - pos_a;
    vec3 m0 = cross( rd, ba );
    vec3 m1 = cross( oa, ba );
    float md = dot( m0, m0 );
    float b = 2. * dot( m0, m1 );
    float bd = dot( ba, ba );
    float h = b * b - 4. * md * ( dot( m1, m1 ) - rad * rad * bd );
    if( h < 0. ) return;
    h = sqrt( h );
    float t = ( -b - h ) / ( 2. * md );
    float y = dot( oa, ba ) + t * dot( rd, ba );
    if( y > 0. && y < bd ) {
        vec3 p = ro + rd * t;
        float d = 1. - ( 1. / distance( ro, p ) );
        if( d <= rgbd.w ) { rgbd.w = d; rgbd.rgb = max( dot( normalize( p - ( pos_a + ba * y / bd ) ), light_dir ), .2 ) * rgb; }
    }
}

vec4 hash_h( float n ) {
    vec4 x = fract( sin( vec4( n + 1., n + 3., n + 5., n + 7. ) ) * 43758.5453 );
    return 2. * x - 1.;
}

void main() {
    float time = TIME * speed;
    vec2 uv = ( gl_FragCoord.xy - RENDERSIZE.xy * .5 ) / RENDERSIZE.y;
    vec3 ro = vec3(cos(time * -.25) * 3.0, sin(time * -.25) * 3.0, 0.0);
    vec3 center_dir = normalize(-ro);
    vec3 right = normalize(cross(center_dir, vec3(0.0, 0.0, 1.0)));
    float sc = tan(tau*.125);
    vec3 rd = normalize(uv.x * sc * right + center_dir + uv.y * sc * vec3(0,0,1));
    light_dir = normalize((-rd + vec3( -1, -1, 1 )) * .5);

    vec3 tlogquat00 = normalize( hash_h( floor( time ) ).xyz );
    vec3 tlogquat0 = normalize( hash_h( floor( time ) + 1.).xyz );
    vec3 tlogquat1 = normalize( hash_h( floor( time ) + 2.).xyz );
    vec3 tlogquat2 = normalize( hash_h( floor( time ) + 3. ).xyz );
    vec3 tlogquat3 = normalize( hash_h( floor( time ) + 4. ).xyz );
    vec3 tlogquat4 = normalize( hash_h( floor( time ) + 5. ).xyz );
    vec3 tlogquat5 = normalize( hash_h( floor( time ) + 6.).xyz );

    vec3 logquat0 = (tlogquat00 + tlogquat1) * tau;
    vec3 logquat1 = (tlogquat0 +  tlogquat2) * tau;
    vec3 logquat2 = (tlogquat1 +  tlogquat3) * tau;
    vec3 logquat3 = (tlogquat2 +  tlogquat4) * tau;
    vec3 logquat4 = (tlogquat3 +  tlogquat5) * tau;

    vec3 tpos00 = normalize( hash_h( floor( time ) ).xyz );
    vec3 tpos0 = normalize( hash_h( floor( time ) + 1. ).xyz );
    vec3 tpos1 = normalize( hash_h( floor( time ) + 2. ).xyz );
    vec3 tpos2 = normalize( hash_h( floor( time ) + 3. ).xyz );
    vec3 tpos3 = normalize( hash_h( floor( time ) + 4. ).xyz );
    vec3 tpos4 = normalize( hash_h( floor( time ) + 5. ).xyz );
    vec3 tpos5 = normalize( hash_h( floor( time ) + 6. ).xyz );

    vec3 pos0 = (tpos00 + tpos0 + tpos1) * .5;
    vec3 pos1 = (tpos0 + tpos1 + tpos2) * .5;
    vec3 pos2 = (tpos1 + tpos2 + tpos3) * .5;
    vec3 pos3 = (tpos2 + tpos3 + tpos4) * .5;
    vec3 pos4 = (tpos3 + tpos4 + tpos5) * .5;

    hepta tdq0 = new_hepta_ypr( logquat0.x, logquat0.y, logquat0.z, pos0 );
    hepta tdq1 = new_hepta_ypr( logquat1.x, logquat1.y, logquat1.z, pos1 );
    hepta tdq2 = new_hepta_ypr( logquat2.x, logquat2.y, logquat2.z, pos2 );
    hepta tdq3 = new_hepta_ypr( logquat3.x, logquat3.y, logquat3.z, pos3 );
    hepta tdq4 = new_hepta_ypr( logquat4.x, logquat4.y, logquat4.z, pos4 );

    hepta dq1 = hepta_slerp( tdq0, tdq2, .5 );
    hepta dq2 = hepta_slerp( tdq1, tdq3, .5 );
    hepta dq3 = hepta_slerp( tdq2, tdq4, .5 );

    float smoothtime = (mod(time, 1.) + smoothstep( 0., 1., fract( time ) )) * .5;

    hepta h1 = hepta_slerp(dq1, dq2, smoothtime);
    hepta h15 = hepta_slerp( dq2, dq3, smoothtime * .5 );
    hepta h2 = hepta_slerp( dq2, dq3, smoothtime );

    h1 = hepta_trans( h1, new_hepta( vec3( 1 ), time * 12., vec3( 0 ) ) );

    vec4 rgbd = vec4( 0, 0, 0, 1 );

    vec3 s1 = vec_trans( vec3( 0 ), h1 );
    vec3 s15 = vec_trans( vec3( 0 ), h15 );
    vec3 s2 = vec_trans( vec3( 0 ), h2 );
    vec3 ds1 = vec_trans( vec3( 0 ), dq1 );
    vec3 ds2 = vec_trans( vec3( 0 ), dq2 );
    vec3 ds3 = vec_trans( vec3( 0 ), dq3 );
    vec3 ds15 = mix( ds1, ds2, smoothtime );

    sphere_h( ro, rd, ds15, .00625, vec3( 1, 1, 0 ), rgbd );
    cylinder_h( ro, rd, ds15, ds2, .0125, vec3( 1, 1, 0 ), rgbd );
    sphere_h( ro, rd, ds2, .025, vec3( 1, 1, 0 ), rgbd );
    cylinder_h( ro, rd, s1, ds15, .0125, vec3( 1, 1, 0 ), rgbd );
    sphere_h( ro, rd, ds15, .0125, vec3( 1, 1, 0 ), rgbd );
    cylinder_h( ro, rd, ds2, s15, .00625, vec3( 1, 0, 1 ), rgbd );
    sphere_h( ro, rd, s15, .00625, vec3( 1, 0, 1 ), rgbd );
    cylinder_h( ro, rd, s15, s2, .00625, vec3( 1, 0, 1 ), rgbd );
    sphere_h( ro, rd, s2, .00625, vec3( 1, 0, 1 ), rgbd );
    sphere_h( ro, rd, ds3, .025, vec3( 1,0,1 ), rgbd );
    sphere_h( ro, rd, s1, .15, vec3( 1 ), rgbd );

    vec3 sx = vec_trans( vec3( .25, 0, 0 ), dq2 );
    cylinder_h( ro, rd, ds2, sx, .0125, vec3( 1, 0, 0 ), rgbd );
    sphere_h( ro, rd, sx, .025, vec3( 1., 0, 0 ), rgbd );
    vec3 sy = vec_trans( vec3( 0, .25, 0 ), dq2 );
    cylinder_h( ro, rd, ds2, sy, .0125, vec3( 0, 1, 0 ), rgbd );
    sphere_h( ro, rd, sy, .025, vec3( 0, 1, 0 ), rgbd );
    vec3 sz = vec_trans( vec3( 0, 0, .25 ), dq2 );
    cylinder_h( ro, rd, ds2, sz, .0125, vec3( 0, 0, 1 ), rgbd );
    sphere_h( ro, rd, sz, .025, vec3( 0, 0, 1 ), rgbd );

    vec3 sx2 = vec_trans( vec3( .5, 0, 0 ), h1 );
    cylinder_h( ro, rd, s1, sx2, .05, vec3( 1, 0, 0 ), rgbd );
    sphere_h( ro, rd, sx2, .075, vec3( 1., 0, 0 ), rgbd );
    vec3 sy2 = vec_trans( vec3( 0, .5, 0 ), h1 );
    cylinder_h( ro, rd, s1, sy2, .05, vec3( 0, 1, 0 ), rgbd );
    sphere_h( ro, rd, sy2, .075, vec3( 0, 1, 0 ), rgbd );
    vec3 sz2 = vec_trans( vec3( 0, 0, .5 ), h1 );
    cylinder_h( ro, rd, s1, sz2, .05, vec3( 0, 0, 1 ), rgbd );
    sphere_h( ro, rd, sz2, .075, vec3( 0, 0, 1 ), rgbd );

    gl_FragColor = vec4( E(rgbd.rgb), 1.0 );
}
"""

path = r'C:\Users\User\Documents\Resolume Wire\Patches\HEPTANION transformation'
os.makedirs(path, exist_ok=True)
with open(os.path.join(path, 'HEPTANION transformation.fs'), 'w') as f:
    f.write(content)
print('Written HEPTANION transformation.fs')
