/*{
  "DESCRIPTION": "SP Field INDOOR atom - one-point-perspective room: grid / corridor / tiles / blinds. Grayscale, alpha = value. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "room",
      "LABEL": "Room",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1,
        2,
        3
      ],
      "LABELS": [
        "grid",
        "corridor",
        "tiles",
        "blinds"
      ]
    },
    {
      "NAME": "horizon",
      "LABEL": "Horizon",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.2,
      "MAX": 0.8
    },
    {
      "NAME": "vx",
      "LABEL": "Vanish X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.2,
      "MAX": 0.8
    },
    {
      "NAME": "scalev",
      "LABEL": "Scale",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "driftv",
      "LABEL": "Drift",
      "TYPE": "float",
      "DEFAULT": 0.2,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hazev",
      "LABEL": "Haze",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "contrast",
      "LABEL": "Contrast",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "levelv",
      "LABEL": "Level",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.5,
      "MAX": 0.5
    }
  ]
}*/

float spLine(float x, float w) { float g = abs(fract(x) - 0.5); return 1.0 - smoothstep(w, w + 0.02, 0.5 - g); }   // 1 on the line
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    float t = TIME * driftv * 0.6;
    float f = 1.0 + scalev * 5.0;
    float con = 0.2 + contrast * 2.8;
    float v = 0.0;

    if (room == 3) {                                        // BLINDS: light through slats, no perspective
        float y = uv.y * (4.0 + scalev * 20.0) + t;
        float slat = smoothstep(0.45, 0.55, abs(fract(y) - 0.5) * 2.0);
        float sweep = 0.5 + 0.5 * sin(uv.x * 3.0 - t * 0.5);
        v = mix(0.08, 0.6, slat) * (0.6 + 0.4 * sweep);
    } else {
        vec2 d = (uv - vec2(vx, horizon)) * vec2(asp, 1.0); // direction from the vanishing point
        bool floorCeil = abs(d.y) >= abs(d.x);
        float z = 1.0 / max(floorCeil ? abs(d.y) : abs(d.x), 0.002);    // depth along the face
        float u = (floorCeil ? d.x : d.y) * z;              // lateral coordinate on the face
        float depthFade = clamp(z * 0.12, 0.0, 1.0);
        float base = 0.08;
        float lines = 0.0;
        if (room == 0) {                                    // GRID: floor and ceiling ruled, walls dark
            if (floorCeil) lines = max(spLine(u * f * 0.8, 0.04), spLine(z * f * 0.25 + t, 0.04));
        } else if (room == 1) {                             // CORRIDOR: every face ruled, the box reads
            lines = max(spLine(u * f * 0.8, 0.03), spLine(z * f * 0.25 + t, 0.03));
            base = floorCeil ? 0.10 : 0.06;
        } else {                                            // TILES: checker floor, faint ceiling
            if (floorCeil && d.y < 0.0) {
                float c = mod(floor(u * f * 0.8) + floor(z * f * 0.25 + t), 2.0);
                lines = mix(0.15, 0.85, c);
            } else if (floorCeil) lines = 0.12;
        }
        v = base + lines * 0.6;
        v = mix(v, 0.3, hazev * depthFade);                 // far = hazed to mid
    }
    v = clamp((v - 0.35) * con + 0.35 + levelv, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
