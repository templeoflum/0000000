/*{
  "DESCRIPTION": "Heart control-ready Field copy; original shader body preserved. Quaternion Field \u2014 no positions, only orientations. Wide parameter ranges for unexpected results.",
  "CREDIT": "Quaternion field",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "speed",
      "TYPE": "float",
      "LABEL": "Speed",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fieldScale",
      "TYPE": "float",
      "LABEL": "Field Scale",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hueSpeed",
      "TYPE": "float",
      "LABEL": "Hue Speed",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "axis1Freq",
      "TYPE": "float",
      "LABEL": "Axis 1 Freq",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "axis2Freq",
      "TYPE": "float",
      "LABEL": "Axis 2 Freq",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "axis3Freq",
      "TYPE": "float",
      "LABEL": "Axis 3 Freq",
      "DEFAULT": 0.3,
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
      "NAME": "brightness",
      "TYPE": "float",
      "LABEL": "Brightness",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "saturation",
      "TYPE": "float",
      "LABEL": "Saturation",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "meanRadius",
      "TYPE": "float",
      "LABEL": "Mean Radius",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sampleDist",
      "TYPE": "float",
      "LABEL": "Sample Distance",
      "DEFAULT": 0.1,
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

float qdist(vec4 a, vec4 b) {
  return acos(clamp(abs(dot(a, b)), 0.0, 1.0));
}

vec4 qaxis(vec3 axis, float angle) {
  float h = angle * 0.5;
  return vec4(cos(h), normalize(axis) * sin(h));
}

vec4 qfield(vec2 p, float t, float s, float f1, float f2, float f3, float c) {
  vec3 ax1 = normalize(vec3(
    sin(p.y * s * 0.7 * f1 + t * 0.11 * f1),
    cos(p.x * s * 0.5 * f1 + t * 0.07 * f1),
    sin(t * 0.09 * f1 + p.x * s * 0.3 * f1)
  ));
  float ang1 = p.x * s * 1.3 * f1 + p.y * s * 0.8 * f1 + t * 0.17 * f1;

  vec3 ax2 = normalize(vec3(
    cos(ang1 * (0.5 + c * 2.0) + p.y * s * 1.1 * f2),
    sin(p.x * s * 0.9 * f2 + t * 0.13 * f2),
    cos(t * 0.19 * f2 + p.y * s * 0.6 * f2 + c * ang1 * 0.4)
  ));
  float ang2 = p.y * s * 1.1 * f2 - p.x * s * 0.6 * f2 + t * 0.23 * f2 + ang1 * c * 0.3;

  vec3 ax3 = normalize(vec3(
    sin(ang1 * (0.3 + c * 0.5) + ang2 * (0.4 + c * 0.4)),
    cos(ang2 * 0.6 * f3 + p.x * s * 0.4 * f3),
    sin(p.x * s * 1.2 * f3 - p.y * s * 0.8 * f3 + t * 0.31 * f3)
  ));
  float ang3 = (ang1 + ang2) * 0.5 + t * 0.13 * f3;

  return normalize(qmul(qmul(qaxis(ax1,ang1), qaxis(ax2,ang2)), qaxis(ax3,ang3)));
}

void main() {
  vec2 uv = gl_FragCoord.xy;

  // All remapped to wide ranges via squaring for exponential feel
  float t  = TIME * (speed * speed * 3.0);
  float s  = 0.0002 + fieldScale * fieldScale * 0.04;
  float ep = 0.3 + sampleDist * sampleDist * 60.0;
  float mr = 5.0 + meanRadius * meanRadius * 300.0;

  // Per-axis frequencies — exponential remap so low values are usable
  float f1 = 0.01 + axis1Freq * axis1Freq * 8.0;
  float f2 = 0.01 + axis2Freq * axis2Freq * 8.0;
  float f3 = 0.01 + axis3Freq * axis3Freq * 8.0;

  vec4 q0 = qfield(uv, t, s, f1, f2, f3, coupling);

  vec4 qx = qfield(uv + vec2(ep, 0.0), t, s, f1, f2, f3, coupling);
  vec4 qy = qfield(uv + vec2(0.0, ep), t, s, f1, f2, f3, coupling);
  vec4 qd = qfield(uv + vec2(ep, ep),  t, s, f1, f2, f3, coupling);

  float dx    = qdist(q0, qx);
  float dy    = qdist(q0, qy);
  float dd    = qdist(q0, qd);
  float curl  = abs(dx - dy);
  float div   = (dx + dy) * 0.5;
  float aniso = abs(dx - dy) / (dx + dy + 0.001);

  vec4 qf1 = qfield(uv + vec2( mr,  0.0), t, s, f1, f2, f3, coupling);
  vec4 qf2 = qfield(uv + vec2(-mr,  0.0), t, s, f1, f2, f3, coupling);
  vec4 qf3 = qfield(uv + vec2(  0.0,  mr), t, s, f1, f2, f3, coupling);
  vec4 qf4 = qfield(uv + vec2(  0.0, -mr), t, s, f1, f2, f3, coupling);
  vec4 qmean  = normalize(qf1 + qf2 + qf3 + qf4);
  float fromMean = qdist(q0, qmean);

  float hue = q0.w * 0.5 + 0.5;
  hue = mod(hue + t * (hueSpeed * hueSpeed * 0.3), 1.0);

  float satScale  = 0.1 + saturation * saturation * 15.0;
  float sat = smoothstep(0.0, 0.4, curl * satScale + aniso * 0.5);

  float brightScale = 0.1 + brightness * brightness * 5.0;
  float val = smoothstep(0.0, 0.8, div * brightScale);
  val += fromMean * (0.1 + brightness * 0.4);
  val  = clamp(val, 0.0, 1.0);
  val  = pow(val, 0.75);

  vec3 hsv = vec3(hue, sat, val);
  vec4 K   = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
  vec3 pp  = abs(fract(hsv.xxx + K.xyz) * 6.0 - K.www);
  vec3 rgb = hsv.z * mix(K.xxx, clamp(pp - K.xxx, 0.0, 1.0), hsv.y);

  float depth = 1.0 - fromMean / PI * 0.6;
  rgb *= depth;

  float bound = smoothstep(0.0, 0.15, dd * 4.0);
  rgb = mix(rgb * 0.3, rgb, bound);

  gl_FragColor = vec4(rgb, 1.0);
}