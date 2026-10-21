/*{
  "DESCRIPTION": "SP Study 3 DELAY v10 - 192-frame full-resolution line (3.2s @60fps), two chained atlases. Delay moves only the gap between start points; replay rate never changes.",
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
      "NAME": "delayv",
      "LABEL": "Delay",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.05,
      "MAX": 3.2
    }
  ],
  "PASSES": [
    {
      "TARGET": "cnt",
      "PERSISTENT": true,
      "FLOAT": true,
      "WIDTH": 1,
      "HEIGHT": 1
    },
    {
      "TARGET": "histA",
      "PERSISTENT": true,
      "WIDTH": "$WIDTH*8",
      "HEIGHT": "$HEIGHT*12"
    },
    {
      "TARGET": "histB",
      "PERSISTENT": true,
      "WIDTH": "$WIDTH*8",
      "HEIGHT": "$HEIGHT*12"
    },
    {}
  ]
}*/

vec2 spTileUV(float slot96, vec2 uv) {
    return (vec2(mod(slot96, 8.0), floor(slot96 / 8.0)) + uv) / vec2(8.0, 12.0);
}
void main() {
    vec2 uv = isf_FragNormCoord;
    if (PASSINDEX == 0) {
        vec4 prev = IMG_PIXEL(cnt, vec2(0.5, 0.5));
        float dt = clamp(TIMEDELTA, 0.001, 0.1);
        float sdt = (prev.g <= 0.0) ? dt : mix(prev.g, dt, 0.05);
        gl_FragColor = vec4(mod(prev.r + 1.0, 192.0), sdt, 1.0, 1.0);
    } else if (PASSINDEX == 1) {
        float g = IMG_PIXEL(cnt, vec2(0.5, 0.5)).r;
        vec2 t = floor(uv * vec2(8.0, 12.0));
        float idx = t.y * 8.0 + t.x;
        float activeA = clamp(floor(delayv / max(IMG_PIXEL(cnt, vec2(0.5, 0.5)).g, 0.001) + 0.5), 1.0, 191.0) + 12.0;
        float distA = mod(g - idx + 192.0, 192.0);
        if (g < 95.5 && abs(idx - g) < 0.5) {
            gl_FragColor = IMG_NORM_PIXEL(inputImage, fract(uv * vec2(8.0, 12.0)));
        } else if (distA <= activeA) {
            gl_FragColor = IMG_NORM_PIXEL(histA, uv);   // hold only the window in use
        } else {
            gl_FragColor = vec4(0.0);                   // beyond the knob: no history kept
        }
    } else if (PASSINDEX == 2) {
        float g = IMG_PIXEL(cnt, vec2(0.5, 0.5)).r;
        vec2 t = floor(uv * vec2(8.0, 12.0));
        float idx = t.y * 8.0 + t.x;
        float activeB = clamp(floor(delayv / max(IMG_PIXEL(cnt, vec2(0.5, 0.5)).g, 0.001) + 0.5), 1.0, 191.0) + 12.0;
        float distB = mod(g - (idx + 96.0) + 192.0, 192.0);
        if (g >= 95.5 && abs(idx - (g - 96.0)) < 0.5) {
            gl_FragColor = IMG_NORM_PIXEL(inputImage, fract(uv * vec2(8.0, 12.0)));
        } else if (distB <= activeB) {
            gl_FragColor = IMG_NORM_PIXEL(histB, uv);   // hold only the window in use
        } else {
            gl_FragColor = vec4(0.0);                   // beyond the knob: no history kept
        }
    } else {
        vec4 c0 = IMG_PIXEL(cnt, vec2(0.5, 0.5));
        float N = clamp(floor(delayv / c0.g + 0.5), 1.0, 191.0);
        float slot = mod(c0.r - N + 192.0, 192.0);
        gl_FragColor = (slot < 95.5)
            ? IMG_NORM_PIXEL(histA, spTileUV(slot, uv))
            : IMG_NORM_PIXEL(histB, spTileUV(slot - 96.0, uv));
    }
}
