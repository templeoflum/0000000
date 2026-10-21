/*{
  "DESCRIPTION": "Heart feedback with movement, hue, inversion, fold, detail and RGB decay inside persistent history. Reset trails clears history once on the next rendered frame; no timed pulse.",
  "CREDIT": "SP study",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "inputImage",
      "LABEL": "Input",
      "TYPE": "image"
    },
    {
      "NAME": "zoomv",
      "LABEL": "Zoom",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.8,
      "MAX": 1.2
    },
    {
      "NAME": "rotz",
      "LABEL": "Rotate",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -30.0,
      "MAX": 30.0
    },
    {
      "NAME": "dx",
      "LABEL": "Drift X",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.02,
      "MAX": 0.02
    },
    {
      "NAME": "dy",
      "LABEL": "Drift Y",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.02,
      "MAX": 0.02
    },
    {
      "NAME": "cx",
      "LABEL": "Center X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cy",
      "LABEL": "Center Y",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gainv",
      "LABEL": "Gain",
      "TYPE": "float",
      "DEFAULT": 0.97,
      "MIN": 0.8,
      "MAX": 1.0
    },
    {
      "NAME": "floorv",
      "LABEL": "Floor",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.1
    },
    {
      "NAME": "keyv",
      "LABEL": "Key",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 0.5
    },
    {
      "NAME": "hueStep",
      "LABEL": "Loop Hue",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": -10,
      "MAX": 10
    },
    {
      "NAME": "invertMix",
      "LABEL": "Loop Invert",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "foldMix",
      "LABEL": "Loop Fold",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": 0,
      "MAX": 1
    },
    {
      "NAME": "detail",
      "LABEL": "Loop Detail",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": -1,
      "MAX": 1
    },
    {
      "NAME": "redDecay",
      "LABEL": "Red Decay",
      "TYPE": "float",
      "DEFAULT": 1,
      "MIN": 0.8,
      "MAX": 1
    },
    {
      "NAME": "greenDecay",
      "LABEL": "Green Decay",
      "TYPE": "float",
      "DEFAULT": 1,
      "MIN": 0.8,
      "MAX": 1
    },
    {
      "NAME": "blueDecay",
      "LABEL": "Blue Decay",
      "TYPE": "float",
      "DEFAULT": 1,
      "MIN": 0.8,
      "MAX": 1
    },
    {
      "NAME": "shufReset",
      "LABEL": "Reset trails",
      "TYPE": "float",
      "DEFAULT": 0,
      "MIN": 0,
      "MAX": 9999
    }
  ],
  "PASSES": [
    {
      "TARGET": "acc",
      "PERSISTENT": true
    },
    {
      "TARGET": "resetLatch",
      "PERSISTENT": true,
      "FLOAT": true,
      "WIDTH": 1,
      "HEIGHT": 1
    },
    {}
  ]
}*/

float spLum(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

vec3 hueRotate(vec3 c, float degrees) {
    vec3 axis=vec3(0.577350269); float a=radians(degrees);
    return clamp(c*cos(a)+cross(axis,c)*sin(a)+axis*dot(axis,c)*(1.0-cos(a)),0.0,1.0);
}
void main() {
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {
        // Write zero into the actual persistent target, not merely its output mix.
        if(abs(IMG_NORM_PIXEL(resetLatch,vec2(.5)).r-shufReset)>.5){gl_FragColor=vec4(0.0);return;}
        vec4 live = IMG_NORM_PIXEL(inputImage, uv);          // the layer above, via the Router
        vec2 puv = uv;                                       // where the loop reads its past

        float asp = RENDERSIZE.x / RENDERSIZE.y;
        vec2 ctr = vec2(cx, cy);
        vec2 q = (uv - ctr) * vec2(asp, 1.0);
        float a = -rotz * 0.017453293;
        q = mat2(cos(a), -sin(a), sin(a), cos(a)) * q / zoomv;   // inverse per-pass map
        puv = q / vec2(asp, 1.0) + ctr - vec2(dx, dy);
        puv.x=mix(puv.x,abs(puv.x-.5)+.5,foldMix);
        float inside = (puv.x >= 0.0 && puv.x <= 1.0 && puv.y >= 0.0 && puv.y <= 1.0) ? 1.0 : 0.0;
        vec3 col = IMG_NORM_PIXEL(acc, clamp(puv, 0.0, 1.0)).rgb * inside;   // outside the frame: no signal

        if(abs(detail)>.001){
            vec2 px=1.0/RENDERSIZE;
            vec3 soft=(IMG_NORM_PIXEL(acc,clamp(puv+vec2(px.x,0),0.0,1.0)).rgb
                      +IMG_NORM_PIXEL(acc,clamp(puv-vec2(px.x,0),0.0,1.0)).rgb
                      +IMG_NORM_PIXEL(acc,clamp(puv+vec2(0,px.y),0.0,1.0)).rgb
                      +IMG_NORM_PIXEL(acc,clamp(puv-vec2(0,px.y),0.0,1.0)).rgb)*.25*inside;
            col=detail<0.0?mix(col,soft,-detail):clamp(col+(col-soft)*detail,0.0,1.0);
        }
        col=hueRotate(col,hueStep);
        // Keep empty history empty; inversion acts on existing trails.
        col=mix(col,(vec3(1.0)-col)*step(.001,max(col.r,max(col.g,col.b))),invertMix);
        col = max(col * gainv * vec3(redDecay,greenDecay,blueDecay) - floorv, 0.0);                // the learned level base, in the loop
        vec3 outc = max(live.rgb, col);                       // dry never attenuated
        gl_FragColor = vec4(outc, 1.0);
    } else if(PASSINDEX==1){
        gl_FragColor=vec4(shufReset,0.0,0.0,1.0);
    } else {
        vec3 c = IMG_NORM_PIXEL(acc, uv).rgb;
        float lum = spLum(c);
        float a = (keyv < 0.001) ? 1.0 : smoothstep(keyv * 0.8, keyv * 1.2, lum);   // Key: at the mix
        gl_FragColor = vec4(c, a);
    }
}
