/*{
  "DESCRIPTION": "Heart control-ready Field copy; original shader body preserved. Quaternion Field \u2014 dark rotational field with sharp propagating swells. Color emerges at peaks of rotational curvature and propagates as the field evolves. No positions, only orientations.",
  "CREDIT": "Quaternion swell field",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "fieldScale",
      "TYPE": "float",
      "LABEL": "Field Scale",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "speed",
      "TYPE": "float",
      "LABEL": "Speed",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 3.0
    },
    {
      "NAME": "swellThreshold",
      "TYPE": "float",
      "LABEL": "Swell Threshold",
      "DEFAULT": 0.55,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "swellSharpness",
      "TYPE": "float",
      "LABEL": "Swell Sharpness",
      "DEFAULT": 0.6,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hueShift",
      "TYPE": "float",
      "LABEL": "Hue Shift",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "coupling",
      "TYPE": "float",
      "LABEL": "Coupling",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "darkness",
      "TYPE": "float",
      "LABEL": "Darkness",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/



precision highp float;



#define PI  3.14159265358979

#define TAU 6.28318530717959



vec4 qmul(vec4 a, vec4 b) {

  return vec4(

    a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z,

    a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y,

    a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x,

    a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w

  );

}



vec4 qaxis(vec3 ax, float a) {

  return normalize(vec4(cos(a * 0.5), ax * sin(a * 0.5)));

}



float qdist(vec4 a, vec4 b) {

  return acos(clamp(abs(dot(a, b)), 0.0, 1.0));

}



vec4 qfield(vec2 p, float t, float s, float c) {

  // Axis 1 — slow base

  vec3 ax1 = normalize(vec3(

    sin(p.y * s * 0.7 + t * 0.11),

    cos(p.x * s * 0.5 + t * 0.07),

    sin(t * 0.09 + p.x * s * 0.3)

  ));

  float a1 = p.x * s * 1.3 + p.y * s * 0.8 + t * 0.17;



  // Axis 2 — coupled to 1 via coupling

  vec3 ax2 = normalize(vec3(

    cos(a1 * (0.5 + c * 1.5) + p.y * s * 1.1),

    sin(p.x * s * 0.9 + t * 0.13),

    cos(t * 0.19 + p.y * s * 0.6 + c * a1 * 0.3)

  ));

  float a2 = p.y * s * 1.1 - p.x * s * 0.6 + t * 0.23 + a1 * c * 0.25;



  // Axis 3 — coupled to both

  vec3 ax3 = normalize(vec3(

    sin(a1 * (0.3 + c * 0.4) + a2 * (0.4 + c * 0.3)),

    cos(a2 * 0.6 + p.x * s * 0.4),

    sin(p.x * s * 1.2 - p.y * s * 0.8 + t * 0.31)

  ));

  float a3 = (a1 + a2) * 0.5 + t * 0.13;



  vec4 q1 = qaxis(ax1, a1);

  vec4 q2 = qaxis(ax2, a2);

  vec4 q3 = qaxis(ax3, a3);



  return normalize(qmul(qmul(q1, q2), q3));

}



void main() {

  vec2 uv = gl_FragCoord.xy;

  float t  = TIME * (speed * 2);

  float sc = 0.03 + fieldScale * 0.06; // internal scale range

  float c  = coupling;



  // Local samples — tight neighborhood for curvature

  float eps = 1.6;

  vec4 q0 = qfield(uv,                       t, sc, c);

  vec4 qx = qfield(uv + vec2(eps, 0.0),      t, sc, c);

  vec4 qy = qfield(uv + vec2(0.0, eps),      t, sc, c);

  vec4 qd = qfield(uv + vec2(eps, eps),      t, sc, c);

  vec4 qn = qfield(uv + vec2(-eps, -eps),    t, sc, c);



  // Rotational derivatives

  float dx = qdist(q0, qx);

  float dy = qdist(q0, qy);

  float dd = qdist(q0, qd);

  float dn = qdist(q0, qn);



  float div  = (dx + dy) * 0.5;

  float curl = abs(dx - dy);



  // Rotational curvature — second derivative

  // This is where the swell comes from — rapid change in the rate of change

  vec4 qx2 = qfield(uv + vec2(eps * 2.0, 0.0), t, sc, c);

  vec4 qy2 = qfield(uv + vec2(0.0, eps * 2.0), t, sc, c);

  float dx2 = qdist(qx, qx2);

  float dy2 = qdist(qy, qy2);

  float curvX = abs(dx2 - dx);

  float curvY = abs(dy2 - dy);

  float curv  = (curvX + curvY) * 0.5;



  // Wide neighborhood — deviation from local mean

  // Peaks here = field is doing something unusual relative to its surroundings

  float eps2 = 35.0;

  vec4 qf1 = qfield(uv + vec2( eps2,  0.0), t, sc, c);

  vec4 qf2 = qfield(uv + vec2(-eps2,  0.0), t, sc, c);

  vec4 qf3 = qfield(uv + vec2(  0.0,  eps2), t, sc, c);

  vec4 qf4 = qfield(uv + vec2(  0.0, -eps2), t, sc, c);

  vec4 qmean = normalize(qf1 + qf2 + qf3 + qf4);

  float fromMean = qdist(q0, qmean);



  // Combined swell signal

  // div alone is smooth — multiply by curvature to get the sharp peaks

  // fromMean adds the propagation character — deviations travel

  float rawSwell = div * (1.0 + curv * 8.0) + fromMean * 0.4;

  rawSwell = rawSwell / (PI * 0.5); // normalize to approx 0-1



  // Threshold and sharpen — this creates the dark field / sharp swell look

  // Below threshold: near black

  // Above threshold: sharp bright swell

  float thresh = swellThreshold;

  float swell = smoothstep(thresh, thresh + (1.0 - swellSharpness) * 0.4, rawSwell);

  swell = pow(swell, 0.3 + swellSharpness * 2.0);



  // Hue from w component — the "amount" of net rotation

  // Shifts slowly over time, giving the color character of the original

  float hue = mod(q0.w * 0.5 + 0.5 + hueShift + t * 0.03, 1.0);



  // Saturation — high at swell peaks, desaturates toward white at extremes

  float sat = swell * (0.6 + curl * 2.0);

  sat = clamp(sat, 0.0, 1.0);



  // Value — the swell IS the brightness

  // Darkness parameter controls how aggressively the field goes black

  float val = pow(swell, 1.0 + darkness * 2.0);

  val = clamp(val, 0.0, 1.0);



  // HSV to RGB

  vec3 hsv = vec3(hue, sat, val);

  vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);

  vec3 pp = abs(fract(hsv.xxx + K.xyz) * 6.0 - K.www);

  vec3 rgb = hsv.z * mix(K.xxx, clamp(pp - K.xxx, 0.0, 1.0), hsv.y);



  gl_FragColor = vec4(rgb, 1.0);

}