/*{
  "DESCRIPTION": "SP Atom Line - the 1D figure extended: Length/Position 1/Position 2/Angle/End 1/End 2; Signal along the line (flat/gradient/sine/noise/pulse) with Cycles and Rate (integrated); Read = the line samples the layer beneath (1D cross-section); Count/Gap tiling. One pixel thin, never touches the frame. Effect on a Video Router. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "inputImage",
      "LABEL": "Behind",
      "TYPE": "image"
    },
    {
      "NAME": "lengthv",
      "LABEL": "Length",
      "TYPE": "float",
      "DEFAULT": 0.6,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "pos",
      "LABEL": "Position 1",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "pos2",
      "LABEL": "Position 2",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "angle",
      "LABEL": "Angle",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "end1",
      "LABEL": "End 1",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "end2",
      "LABEL": "End 2",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "signal",
      "LABEL": "Signal",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4
      ],
      "LABELS": [
        "flat",
        "gradient",
        "sine",
        "noise",
        "pulse"
      ]
    },
    {
      "NAME": "cycles",
      "LABEL": "Cycles",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.25,
      "MAX": 32.0
    },
    {
      "NAME": "rate",
      "LABEL": "Rate",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "readv",
      "LABEL": "Read",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "count",
      "LABEL": "Count",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 1.0,
      "MAX": 32.0
    },
    {
      "NAME": "gap",
      "LABEL": "Gap",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.95
    }
  ],
  "PASSES": [
    {
      "TARGET": "ph",
      "PERSISTENT": true,
      "FLOAT": true,
      "WIDTH": 1,
      "HEIGHT": 1
    },
    {}
  ]
}*/

#define PI 3.14159265
float smin(float a, float b, float k) { return -k * log(exp(-a / k) + exp(-b / k)); }
float h1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float n1(float x) { float i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f); return mix(h1(i), h1(i + 1.0), f); }
void main() {
    // pass 0: integrate Rate as a phase in cycle units — knob changes only change the speed from now on
    if (PASSINDEX == 0) {
        float prev = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;
        float dt = clamp(TIMEDELTA, 0.0, 0.1);
        gl_FragColor = vec4(fract(prev + dt * rate * abs(rate) * 2.0), 0.0, 0.0, 1.0);
        return;
    }
    float phase = IMG_PIXEL(ph, vec2(0.5, 0.5)).r;

    vec2 suv = isf_FragNormCoord;
    vec2 uv = suv - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;                // LIVE composition aspect
    uv.x *= asp;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    float m = 0.04;
    vec2 lim = hf2 - m;
    float a = angle * 2.0 * PI;
    vec2 dir = vec2(cos(a), sin(a)), nrm = vec2(-dir.y, dir.x);
    vec2 ad = abs(dir) + 1e-4, an = abs(nrm) + 1e-4;
    float k = 0.02;
    float px1 = 1.0 / RENDERSIZE.y;
    float thick = px1 * 0.75;

    // extent: Length contained at this angle; the ends can each pull in toward the center
    float lmax = smin((lim.x - ad.x * thick) / an.x, (lim.y - ad.y * thick) / an.y, k);
    float len_ = mix(0.005, max(lmax, 0.005), lengthv);
    vec2 box = an * len_ + ad * thick;
    vec2 room = max(lim - box, vec2(0.0));
    vec2 p = vec2(pos - 0.5, pos2 - 0.5) * 2.0;
    vec2 off = nrm * p.x + dir * p.y;
    float pl = max(length(p), 1e-5);
    vec2 ao = abs(off) / pl + 1e-5;
    float T = smin(room.x / ao.x, room.y / ao.y, k);
    vec2 c = off * clamp(T, 0.0, 1e3) * min(1.0, 1.0 / pl);
    vec2 q = uv - c;
    float along = dot(q, nrm), across = dot(q, dir);
    float start = -len_ * end1, stop = len_ * end2;          // End 1 / End 2: each end on its own, inside the contained length
    float onLine = (1.0 - smoothstep(thick - px1, thick + px1, abs(across)))
                 * smoothstep(start - px1, start + px1, along) * (1.0 - smoothstep(stop - px1, stop + px1, along));

    // along the line: u in [0,1] over the lit stretch
    float u = (along - start) / max(stop - start, 1e-4);

    // tiling: Count intervals, each dark for its last Gap
    float rep = fract(u * count);
    float tile = 1.0 - step(1.0 - gap, rep);
    if (count <= 1.001 && gap <= 0.001) tile = 1.0;

    // the 1D signal, travelling with the integrated phase
    float s = u * cycles - phase;
    float sig;
    if (signal == 0) sig = 1.0;
    else if (signal == 1) sig = fract(s);
    else if (signal == 2) sig = 0.5 + 0.5 * sin(s * 2.0 * PI);
    else if (signal == 3) sig = n1(s * 4.0 + 7.3);
    else { float f = fract(s); sig = 1.0 - smoothstep(0.0, 0.5, abs(f - 0.5) * 2.0); }

    // the reader: the luminance of what lies beneath this pixel of the line
    vec3 beneath = IMG_NORM_PIXEL(inputImage, suv).rgb;
    float rd = dot(beneath, vec3(0.299, 0.587, 0.114));
    float val = mix(sig, rd, readv);

    float v = onLine * tile * val;
    gl_FragColor = vec4(vec3(v), onLine * tile);
}
