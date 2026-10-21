/*{
  "DESCRIPTION": "SP Atom Void - a medium with no surface: dust as points in an infinite 3D lattice, walked by the ray, seen through the field camera (Tilt, Sway/Bob/Travel, Horizon, Yaw, Dolly, Focal mm, Lens, Distort). Density, Size, Reach, Haze, Soft. No drives.",
  "CREDIT": "SP atom",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "tilt",
      "LABEL": "Tilt",
      "TYPE": "float",
      "DEFAULT": -1.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "sway",
      "LABEL": "Sway",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "bob",
      "LABEL": "Bob",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "travel",
      "LABEL": "Travel",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "horizon",
      "LABEL": "Horizon",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "yaw",
      "LABEL": "Yaw",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "dolly",
      "LABEL": "Dolly",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -1.0,
      "MAX": 1.0
    },
    {
      "NAME": "focal",
      "LABEL": "Focal mm",
      "TYPE": "float",
      "DEFAULT": 35.0,
      "MIN": 14.0,
      "MAX": 200.0
    },
    {
      "NAME": "proj",
      "LABEL": "Lens",
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
        "rectilinear",
        "stereographic",
        "equidistant",
        "equisolid",
        "orthographic"
      ]
    },
    {
      "NAME": "distort",
      "LABEL": "Distort",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.6,
      "MAX": 0.6
    },
    {
      "NAME": "density",
      "LABEL": "Density",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sizev",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "reach",
      "LABEL": "Reach",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "haze",
      "LABEL": "Haze",
      "TYPE": "float",
      "DEFAULT": 0.3,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "soft",
      "LABEL": "Soft",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

#define PI 3.14159265
vec3 h3(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.xxy + p.yxx) * p.zyx); }
void main() {
    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    // image plane in millimetres: the frame height is the 24 mm sensor height
    vec2 mmv = vec2((uv.x - 0.5) * asp, uv.y - 0.5) * 24.0;
    // Brown–Conrady on normalized coordinates (r = 1 at the frame's half-height)
    vec2 nrm = mmv / 12.0; float r2 = dot(nrm, nrm);
    nrm *= (1.0 + distort * r2 + 0.25 * distort * distort * r2 * r2);
    mmv = nrm * 12.0;
    // Dolly zoom: move forward by D, compensate the focal so a subject at R keeps its size
    float R = 3.0, D = dolly * 2.4;
    float f = focal * max(R - D, 0.3) / R;
    // the ray for this image point, by lens mapping: image radius r (mm) → angle θ off the axis
    float rr = length(mmv); vec2 dirxy = (rr > 1e-6) ? mmv / rr : vec2(0.0);
    float th;
    if (proj == 0) th = atan(rr / f);
    else if (proj == 1) th = 2.0 * atan(rr / (2.0 * f));
    else if (proj == 2) th = rr / f;
    else if (proj == 3) th = 2.0 * asin(clamp(rr / (2.0 * f), 0.0, 1.0));
    else th = asin(clamp(rr / f, 0.0, 1.0));
    vec3 d = vec3(sin(th) * dirxy, cos(th));
    // Horizon: the camera's pitch, a full turn (0 level, +0.5 straight down, -0.5 straight up, the ends level again upside down)
    float pitch = -horizon * PI;
    float cp = cos(pitch), sp = sin(pitch);
    d = vec3(d.x, d.y * cp + d.z * sp, -d.y * sp + d.z * cp);   // rotate about x: looking down puts the horizon up the frame
    float yw = yaw * PI;                                     // Yaw: turn round on the plane (±180°), about the up axis
    d = vec3(d.x * cos(yw) + d.z * sin(yw), d.y, -d.x * sin(yw) + d.z * cos(yw));
    // ── the WORLD: Tilt rolls the world itself (a full turn, the slider's ends are level). The lens has already shaped the ray;
    //    the rolled world is seen THROUGH it, so a barrel lens bends a tilted horizon the way it would in a real camera ──
    float roll = (tilt + 1.0) * PI;
    d = vec3(d.x * cos(roll) - d.y * sin(roll), d.x * sin(roll) + d.y * cos(roll), d.z);
    // ── the VOID: no surface, a medium. Dust as real points in an infinite lattice of cells, one mote per cell at a
    //    random spot; the ray walks the cells it passes through (3D DDA), so motes exist in every direction and Travel
    //    goes on forever with nothing recycling. Depth cues: motes shrink with distance, motion parallax, Haze. ──
    vec3 cam = vec3(sway * 0.6, bob * 0.35, travel * 4.0 + D);   // Travel: a phase — one full knob = one lattice period (8 cells), so it loops seamlessly
    float c = 0.5;                                           // the cell
    float keep = mix(0.9, 0.15, density);                    // a cell holds a mote when its seed clears this
    float rad = (0.02 + sizev * 0.12) * c;                   // mote radius, world units: it shrinks with distance by itself
    float range = 4.0 + reach * 28.0;
    float pxa = (1.0 + soft * 6.0) / RENDERSIZE.y * (24.0 / f);   // one pixel, as an angle
    vec3 cell = floor(cam / c);
    vec3 stp = sign(d); vec3 ad = max(abs(d), vec3(1e-5));
    vec3 tDelta = c / ad;
    vec3 tMax = ((cell + max(stp, 0.0)) * c - cam) / d;
    tMax = mix(tMax, vec3(1e9), step(abs(d), vec3(1e-5)));
    float v = 0.0, tcur = 0.0;
    for (int i = 0; i < 72; i++) {
        vec3 cellp = vec3(cell.x, cell.y, mod(cell.z, 8.0));   // periodic along travel
        vec3 r3 = h3(cellp);
        if (r3.x > keep) {
            float m = min(rad * 1.5 + 0.02, 0.45 * c) / c;   // the mote sits wholly inside its cell: no cut at the cell wall
            vec3 ctr = (cell + m + h3(cellp + 7.0) * (1.0 - 2.0 * m)) * c;
            vec3 oc = ctr - cam; float b = dot(oc, d);
            if (b > 0.0) {
                float dist2 = dot(oc, oc) - b * b;           // closest approach, squared
                float aa = pxa * b;                          // the pixel's footprint at this depth
                float disc = 1.0 - smoothstep(rad - aa, rad + aa, sqrt(max(dist2, 0.0)));
                float far = 1.0 - exp(-b * 0.10);
                float fade = (1.0 - haze * far) * (1.0 - smoothstep(range * 0.7, range, b));
                v = max(v, disc * fade);
            }
        }
        // step to the next cell along the ray
        if (tMax.x < tMax.y && tMax.x < tMax.z) { tcur = tMax.x; cell.x += stp.x; tMax.x += tDelta.x; }
        else if (tMax.y < tMax.z) { tcur = tMax.y; cell.y += stp.y; tMax.y += tDelta.y; }
        else { tcur = tMax.z; cell.z += stp.z; tMax.z += tDelta.z; }
        if (tcur > range || v >= 0.999) break;
    }
    v = clamp(v, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), v);
}
