/*{
  "CREDIT": "by mojovideotech",
  "DESCRIPTION": "Heart control-ready copy; original preserved. ",
  "CATEGORIES": [
    "generator",
    "OpArt",
    "spiral"
  ],
  "INPUTS": [
    {
      "NAME": "color1R",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color1G",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color1B",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2R",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2G",
      "TYPE": "float",
      "DEFAULT": 0.8,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "color2B",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gamma",
      "TYPE": "float",
      "DEFAULT": 0.9,
      "MIN": 0.5,
      "MAX": 3.0
    },
    {
      "NAME": "amp1",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.01,
      "MAX": 0.25
    },
    {
      "NAME": "amp2",
      "TYPE": "float",
      "DEFAULT": 0.05,
      "MIN": 0.04,
      "MAX": 0.25
    },
    {
      "NAME": "freq1",
      "TYPE": "float",
      "DEFAULT": -0.5,
      "MIN": -10,
      "MAX": 10
    },
    {
      "NAME": "freq2",
      "TYPE": "float",
      "DEFAULT": 1,
      "MIN": -10,
      "MAX": 10
    },
    {
      "NAME": "phase1",
      "TYPE": "float",
      "DEFAULT": 0.15,
      "MIN": -2.0,
      "MAX": 2.0
    },
    {
      "NAME": "phase2",
      "TYPE": "float",
      "DEFAULT": -1.05,
      "MIN": -2.0,
      "MAX": 2.0
    },
    {
      "NAME": "rate",
      "TYPE": "float",
      "DEFAULT": 1.5,
      "MIN": -5.0,
      "MAX": 5.0
    }
  ]
}*/
const vec2 center=vec2(1.0);

////////////////////////////////////////////////////////////
// HypnoWorm  by mojovideotech
//
// Creative Commons Attribution-NonCommercial-ShareAlike 3.0
////////////////////////////////////////////////////////////
void main() {
    vec3 fc = vec3(vec4(color1R,color1G,color1B,1.0).rbg);
    vec2 uv = 2.0*((gl_FragCoord.xy - 0.5*RENDERSIZE.xy) / min(RENDERSIZE.x,RENDERSIZE.y) + 0.5) - center.xy;
    uv *= 12.0;
    
    vec2 pos = center.xy / RENDERSIZE.xy;

    float T = TIME + rate * 0.1 * dot(uv, uv);
    float totalCoverage = 0.0;

    for(float i = 30.0; i > 0.; --i) {
        pos += vec2(sin(T + (freq1 - i) * phase2) * amp1, cos(T + (freq2 - i) * phase1) * amp2);
        float dist = length(pos - uv) - 0.075 * i;
        float o = step(0.0, -dist);
        totalCoverage += o;
        vec3 incoming = vec3(1.) * (1. - mod(i, 2.));
        // skip mix when colors match to avoid white-on-white noise
        if (length(incoming - fc) > 0.01) {
            fc = mix(fc, incoming, o);
        }
    }

    if (totalCoverage < 0.01) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }

    vec3 cc = vec3(vec4(color1R,color1G,color1B,1.0).gbr * vec4(color2R,color2G,color2B,1.0).rgb);
    vec4 col = vec4(pow(vec4(color2R,color2G,color2B,1.0).rgb, fc.rgb) - cc, 1.0);
    col = pow(max(col, vec4(0.0)), vec4(1.0 / gamma));
    col = clamp(col, 0.0, 1.2);

    gl_FragColor = vec4(col.rgb, 1.0);
}