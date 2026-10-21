import os

content = r"""/*{
    "DESCRIPTION": "Poincare Disk with IIS fractal on a sphere.",
    "CREDIT": "soma_arc / Shadertoy",
    "ISFVSN": "2",
    "CATEGORIES": ["Generator"],
    "INPUTS": [
        {"NAME": "speed", "LABEL": "Speed", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0}
    ]
}*/

vec2 rand2n(vec2 co, float sampleIndex) {
    vec2 seed = co * (sampleIndex + 1.0);
    seed+=vec2(-1,1);
    return vec2(fract(sin(dot(seed.xy ,vec2(12.9898,78.233))) * 43758.5453),
                 fract(cos(dot(seed.xy ,vec2(4.898,7.23))) * 23421.631));
}

vec3 hsv2rgb(vec3 c){
    const vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

const float PI = 3.14159265359;
const float fourPI = 12.566368;
const float EPSILON = 0.001;

const vec3 BLACK = vec3(0);
const vec3 WHITE = vec3(1.);
const vec3 GREEN = vec3(0, .78, 0);

const float NO_HIT = 9999999.;

const int MTL_PLANE = 0;
const int MTL_SPHERE = 1;
const int MTL_CYLINDER = 2;
const int MTL_RECT = 3;
int g_mtl = -1;
const vec3 ambientFactor = vec3(0.1);

vec4 intersectPlane(vec3 p, vec3 n,
                    vec3 rayOrigin, vec3 rayDir, vec4 isect){
    float d = -dot(p, n);
    float v = dot(n, rayDir);
    float t = -(dot(n, rayOrigin) + d) / v;
    if(EPSILON < t && t < isect.x){
        g_mtl = MTL_PLANE;
        return vec4(t, n);
    }
    return isect;
}

vec4 intersectSphere(vec3 sphereCenter, float radius,
                      vec3 rayOrigin, vec3 rayDir, vec4 isect){
  vec3 v = rayOrigin - sphereCenter;
  float b = dot(rayDir, v);
  float c = dot(v, v) - radius * radius;
  float d = b * b - c;
  if(d >= 0.){
    float s = sqrt(d);
    float t = -b - s;
    if(t <= EPSILON) t = -b + s;
    if(EPSILON < t && t < isect.x){
      g_mtl = MTL_SPHERE;
      vec3 p = (rayOrigin + t * rayDir);
      return vec4(t, normalize(p - sphereCenter));
    }
  }
  return isect;
}

vec2 circleInverse(vec2 pos, vec2 circlePos, float circleR){
    return ((pos - circlePos) * circleR * circleR)/(length(pos - circlePos) * length(pos - circlePos) ) + circlePos;
}

bool revCircle = false;
bool revCircle2 = false;
vec2 cPos1 = vec2(1.2631, 0);
vec2 cPos2 = vec2(0, 1.2631);
float cr1 = 0.771643;
float cr2 = 0.771643;
const int ITERATIONS = 50;
float colCount = 0.;
bool outer = false;

int IIS(vec2 pos){
    colCount = 0.;
    bool fund = true;
    int invCount = 1;
    for(int i = 0 ; i < ITERATIONS ; i++){
        fund = true;
        if (pos.x < 0.){
            pos *= vec2(-1, 1);
            invCount++;
            fund = false;
        }
        if(pos.y < 0.){
            pos *= vec2(1, -1);
            invCount++;
            fund = false;
        }
        if(revCircle){
            if(distance(pos, cPos1) > cr1 ){
                pos = circleInverse(pos, cPos1, cr1);
                invCount++;
                colCount++;
                fund = false;
            }
        }else{
            if(distance(pos, cPos1) < cr1 ){
                pos = circleInverse(pos, cPos1, cr1);
                invCount++;
                colCount++;
                fund = false;
            }
        }
        if(revCircle2){
            if(distance(pos, cPos2) > cr2 ){
                pos = circleInverse(pos, cPos2, cr2);
                invCount++;
                colCount++;
                fund = false;
            }
        }else{
            if(distance(pos, cPos2) < cr2 ){
                pos = circleInverse(pos, cPos2, cr2);
                invCount++;
                colCount++;
                fund = false;
            }
        }
        if(fund){
            if(length(pos) > 1.5){
                outer = true;
                return invCount;
            }
            return invCount;
        }
    }
    return invCount;
}

vec4 getIntersection(vec3 eye, vec3 ray){
    vec4 isect = vec4(NO_HIT);
    isect = intersectPlane(vec3(0, 0., 0.), vec3(0, 1, 0),
                            eye, ray, isect);
    isect = intersectSphere(vec3(0, 0, 0), 1.,
                            eye, ray, isect);
    return isect;
}

bool visible(vec3 eye, vec3 target){
    vec3 v = normalize(target - eye);
    return getIntersection(eye, v).x == NO_HIT;
}

const vec3 LIGHT_DIR = normalize(vec3(0.0, 1., 0.5));
const float transparency = 0.6;
const int MAX_TRACE_DEPTH = 7;

vec3 calcColor(vec3 eye, vec3 ray){
    vec3 l = BLACK;
    float coeff = 1.0;
    for (int depth = 0 ; depth < MAX_TRACE_DEPTH ; depth++){
        vec4 isect = getIntersection(eye, ray);
        if(isect.x != NO_HIT){
            vec3 matColor = WHITE;
            vec3 intersection = eye + ray * isect.x;
            vec3 normal = isect.yzw;
            if(g_mtl == MTL_PLANE){
                matColor = vec3(0.7);
                int d = IIS(intersection.xz);
                if(d == 0){
                    matColor += vec3(0.,0.,0.);
                }else{
                    if(mod(float(d), 2.) == 0.){
                        if(outer){
                            matColor = hsv2rgb(vec3(0.25 , 1., 1.));
                        }else{
                            matColor = hsv2rgb(vec3(0. , 1., 1.));
                        }
                    }else{
                        if(outer){
                            matColor = hsv2rgb(vec3(0.75 , 1., 1.));
                        }else{
                            matColor = hsv2rgb(vec3(0.5 , 1., 1.));
                        }
                    }
                }
            }else if(g_mtl == MTL_SPHERE){
                matColor = vec3(0.7, 0.4, 0.4);
            }else if(g_mtl == MTL_CYLINDER){
                matColor = GREEN;
            }else if(g_mtl == MTL_RECT){
                matColor = GREEN;
            }
            vec3 diffuse = clamp(dot(normal, LIGHT_DIR), 0., 1.) * matColor;
            vec3 ambient = matColor * ambientFactor;
            if(g_mtl == MTL_SPHERE || g_mtl == MTL_RECT){
                coeff *= transparency;
                l += (diffuse + ambient) * coeff;
                eye = intersection + ray * 0.01;
                continue;
            }else{
                l += (diffuse + ambient) * coeff;
            }
        }
        break;
    }
    return l;
}

const float DISPLAY_GAMMA_COEFF = 1. / 2.2;
vec3 gammaCorrect(vec3 rgb) {
    return vec3((min(pow(rgb.r, DISPLAY_GAMMA_COEFF), 1.)),
                (min(pow(rgb.g, DISPLAY_GAMMA_COEFF), 1.)),
                (min(pow(rgb.b, DISPLAY_GAMMA_COEFF), 1.)));
}

vec3 calcRay (const vec3 eye, const vec3 target,
              const vec3 up, const float fov,
              const float width, const float height, const vec2 coord){
  float imagePlane = (height * .5) / tan(radians(fov) * .5);
  vec3 v = normalize(target - eye);
  vec3 focalXAxis = normalize(cross(v, up));
  vec3 focalYAxis = normalize(cross(v, focalXAxis ));
  vec3 center = v * imagePlane;
  vec3 origin = center - (focalXAxis * (width  * .5)) - (focalYAxis * (height * .5));
  return normalize(origin + (focalXAxis * coord.x) + (focalYAxis * (height - coord.y)));
}

vec2 reverseStereoProject(vec3 pos){
    return vec2(pos.x / (1. - pos.z), pos.y / (1. - pos.z));
}

vec3 getCircleFromSphere(vec3 upper, vec3 lower){
    vec2 p1 = reverseStereoProject(upper);
    vec2 p2 = reverseStereoProject(lower);
    return vec3((p1 + p2) / 2., distance(p1, p2)/ 2.);
}

const float SAMPLE_NUM = 20.;

void main(){
    float time = TIME * speed;

    float x = 0.57735;
    float bendX = 0.;
    mat3 xRotate = mat3(1, 0, 0,
                        0, cos(bendX), -sin(bendX),
                        0, sin(bendX), cos(bendX));
    float bendY = 0.;
    mat3 yRotate = mat3(cos(bendY), 0, sin(bendY),
                         0, 1, 0,
                         -sin(bendY), 0, cos(bendY));
    float y = .57735;
    vec3 c1 = getCircleFromSphere(vec3(0, y, sqrt(1. - y * y))* xRotate,
                                  vec3(0, y, -sqrt(1. - y * y))* xRotate);
    vec3 c2 = getCircleFromSphere(vec3(x, 0, sqrt(1. - x * x)) * yRotate,
                                  vec3(x, 0, -sqrt(1. - x * x)) * yRotate);
    cr1 = c1.z;
    cr2 = c2.z;
    cPos1 = c1.xy;
    cPos2 = c2.xy;
    if(y > cPos1.y) revCircle = true;
    if(x > cPos2.x) revCircle2 = true;

    float dist = 2.;
    vec3 eye = vec3(dist * sin(time), 1.5, dist * cos(time));
    vec3 target = vec3(0);
    vec3 up = vec3(0, 1, 0);
    float fov = 60.;

    vec3 sum = vec3(0);
    for(float i = 0. ; i < SAMPLE_NUM ; i++){
        vec2 coordOffset = rand2n(gl_FragCoord.xy, i);
        vec3 ray = calcRay(eye, target, up, fov,
                           RENDERSIZE.x, RENDERSIZE.y,
                           gl_FragCoord.xy + coordOffset);
        sum += calcColor(eye, ray);
    }
    vec3 col = (sum/SAMPLE_NUM);
    gl_FragColor = vec4(gammaCorrect(col), 1.);
}
"""

path = r'C:\Users\User\Documents\Resolume Wire\Patches\Poincare Disk'
os.makedirs(path, exist_ok=True)
with open(os.path.join(path, 'Poincare Disk.fs'), 'w') as f:
    f.write(content)
print('Written Poincare Disk.fs')
