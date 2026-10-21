/*{
  "DESCRIPTION": "SP Atom Room - a real camera inside a fixed, lit, tiled box (Left/Right/Floor/Ceiling/Back/Front = where each plane sits, world units); WORLD: Tilt (roll, full turn), Sway/Bob/Travel; CAMERA: Horizon (pitch), Yaw (turn), Dolly (dolly zoom), Focal mm, Lens, Distort; Scale, Gap, Seam (gap tone; solid floor), Bands, Sun/Height/Relief, Haze, Soft. No drives.",
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
      "NAME": "left",
      "LABEL": "Left",
      "TYPE": "float",
      "DEFAULT": 2.2,
      "MIN": 0.3,
      "MAX": 12.0
    },
    {
      "NAME": "right",
      "LABEL": "Right",
      "TYPE": "float",
      "DEFAULT": 2.2,
      "MIN": 0.3,
      "MAX": 12.0
    },
    {
      "NAME": "floory",
      "LABEL": "Floor",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -6.0,
      "MAX": 0.9
    },
    {
      "NAME": "ceily",
      "LABEL": "Ceiling",
      "TYPE": "float",
      "DEFAULT": 2.4,
      "MIN": 1.1,
      "MAX": 12.0
    },
    {
      "NAME": "backz",
      "LABEL": "Back",
      "TYPE": "float",
      "DEFAULT": 8.0,
      "MIN": 0.5,
      "MAX": 40.0
    },
    {
      "NAME": "frontz",
      "LABEL": "Front",
      "TYPE": "float",
      "DEFAULT": 8.0,
      "MIN": 0.5,
      "MAX": 40.0
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
      "NAME": "gap",
      "LABEL": "Gap",
      "TYPE": "float",
      "DEFAULT": 0.15,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "seamv",
      "LABEL": "Seam",
      "TYPE": "float",
      "DEFAULT": 0.15,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bands",
      "LABEL": "Bands",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "sun",
      "LABEL": "Sun",
      "TYPE": "float",
      "DEFAULT": 0.25,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "height",
      "LABEL": "Height",
      "TYPE": "float",
      "DEFAULT": 0.7,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "relief",
      "LABEL": "Relief",
      "TYPE": "float",
      "DEFAULT": 0.0,
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
// ── a REAL camera: 35mm-equivalent focal length on a 36×24 sensor (FOV = 2·atan(sensor/2f)), five lens mappings
//    (rectilinear r=f·tanθ, stereographic r=2f·tan(θ/2), equidistant r=f·θ, equisolid r=2f·sin(θ/2), orthographic
//    r=f·sinθ), Brown–Conrady radial distortion x' = x(1 + k1·r²), and the dolly zoom (Hitchcock): the camera
//    moves forward while the focal length compensates so mid-ground keeps its size — the space itself stretches.
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
    // ── the WORLD (before the camera's pitch, so the horizon and the vanishing point swing round the image center together)
    // Tilt rolls the world: Tilt rolls the world itself (a full turn, the slider's ends are level). The lens has already shaped the ray;
    //    the rolled world is seen THROUGH it, so a barrel lens bends a tilted horizon the way it would in a real camera ──
    float roll = (tilt + 1.0) * PI;
    d = vec3(d.x * cos(roll) - d.y * sin(roll), d.x * sin(roll) + d.y * cos(roll), d.z);
    // Horizon: the camera's pitch, a full turn (0 level, +0.5 straight down, -0.5 straight up, the ends level again upside down)
    float pitch = -horizon * PI;
    float cp = cos(pitch), sp = sin(pitch);
    d = vec3(d.x, d.y * cp + d.z * sp, -d.y * sp + d.z * cp);   // rotate about x: looking down puts the horizon up the frame
    float yw = yaw * PI;                                     // Yaw: the camera turns round inside the room (±180°)
    d = vec3(d.x * cos(yw) + d.z * sin(yw), d.y, -d.x * sin(yw) + d.z * cos(yw));
    // ── ONE WORLD. Floor at y = 0, ceiling at y = roomH, walls at x = ±halfW, back at z = zBack, front at z = zFront: all fixed in the
    //    world. The camera is a point inside it: (camX, camH, camZ). Sway/Bob/Travel/Dolly move that point and nothing else. ──
    // ── THE BOX. Always closed: floor, ceiling, two walls, back and front. Each plane sits where its knob puts it;
    //    the camera is a body inside, kept off every plane. ──
    float xL = -left, xR = right, yF = floory, yC = ceily, zB = backz, zF = -frontz;
    float mg = 0.25;
    float camH = clamp(1.0 + bob * 0.35, yF + mg, yC - mg);
    float camX = clamp(sway * 0.6, xL + mg, xR - mg);
    float camZ = clamp(travel * 4.0 + D, zF + mg, zB - mg);
    vec3 cam = vec3(camX, camH, camZ);
    float w = 0.5 / RENDERSIZE.y + soft * 0.35;
    float sunA = sun * 2.0 * PI, sunE = (height - 0.5) * PI;
    vec3 sun3 = vec3(cos(sunE) * cos(sunA), sin(sunE), cos(sunE) * sin(sunA));
    float tBest = 1e9; vec2 pc = vec2(0.0); float edgeIn = 0.0; int which = -1; vec2 Lp = vec2(0.0); float el = 0.0; float depthCoord = 0.0; float planeA = 1.0;
    // floor y = yF
    if (d.y < -1e-5) { float t = (yF - cam.y) / d.y; vec3 h = cam + d * t;
        if (t > 0.0 && t < tBest && h.x >= xL && h.x <= xR && h.z >= zF && h.z <= zB) { tBest = t; pc = h.xz; depthCoord = h.z; edgeIn = smoothstep(0.0, w, -d.y); which = 0; Lp = sun3.xz; el = sun3.y; } }
    // ceiling y = yC
    if (d.y > 1e-5) { float t = (yC - cam.y) / d.y; vec3 h = cam + d * t;
        if (t > 0.0 && t < tBest && h.x >= xL && h.x <= xR && h.z >= zF && h.z <= zB) { tBest = t; pc = h.xz; depthCoord = h.z; edgeIn = smoothstep(0.0, w, d.y); which = 1; Lp = sun3.xz; el = -sun3.y; } }
    // walls x = xL / xR, floor to ceiling
    if (abs(d.x) > 1e-5) { float wx = (d.x > 0.0) ? xR : xL; float t = (wx - cam.x) / d.x; vec3 h = cam + d * t;
        if (t > 0.0 && t < tBest && h.y >= yF && h.y <= yC && h.z >= zF && h.z <= zB) { tBest = t; pc = h.zy; depthCoord = h.z; edgeIn = smoothstep(0.0, w, abs(d.x)); which = 2; Lp = sun3.zy; el = (d.x > 0.0) ? -sun3.x : sun3.x; } }
    // back / front z = zB / zF
    if (abs(d.z) > 1e-5) { bool bkw = d.z > 0.0; float wz = bkw ? zB : zF; float t = (wz - cam.z) / d.z; vec3 h = cam + d * t;
        if (t > 0.0 && t < tBest && h.x >= xL && h.x <= xR && h.y >= yF && h.y <= yC) { tBest = t; pc = h.xy; depthCoord = h.x; edgeIn = smoothstep(0.0, w, abs(d.z)); which = 3; Lp = sun3.xy; el = bkw ? -sun3.z : sun3.z; } }
    if (which < 0) { gl_FragColor = vec4(0.0); return; }     // open: the sky's, the feedback's
    float ground = edgeIn;
    float t = tBest;
    float f_ = 2.0 + scalev * 18.0;
    vec2 cell = pc * f_ * 0.25;                              // the same tile scale on every plane: seams meet at the corners
    vec2 g = abs(fract(cell) - 0.5) * 2.0;
    float aa = max(fwidth(cell.x), fwidth(cell.y)) * 1.5;
    float dist = 1.0 - exp(-t * 0.09);                      // 0 near → 1 far, by ray length
    float detail = (1.0 - haze * dist) * (1.0 - smoothstep(0.35, 1.0, aa));   // subpixel tiles settle to their mean, no moiré
    float seamW = gap * 0.5 * detail;
    float seam = max(smoothstep(1.0 - seamW - aa, 1.0 - seamW + aa, g.x), smoothstep(1.0 - seamW - aa, 1.0 - seamW + aa, g.y));
    float tile = 1.0 - seam * detail;
    float tileTone = mix(seamv, 1.0, tile);                  // Seam: the gap's tone. The floor is solid; a gap is a line, not a hole
    // relief: the tile lips lit by the sun's in-plane direction, dome or pit by its component along the plane's normal
    float Ll = length(Lp); vec2 L2 = (Ll > 1e-4) ? Lp / Ll : vec2(0.0);
    vec2 toSeam = (g.x > g.y) ? vec2(sign(fract(cell.x) - 0.5), 0.0) : vec2(0.0, sign(fract(cell.y) - 0.5));
    float din = 1.0 - max(g.x, g.y);
    float lipW = 0.08 + relief * 0.4;
    float lip = 1.0 - smoothstep(0.0, lipW, din); lip = lip * lip * (3.0 - 2.0 * lip);
    float shade = relief * lip * dot(toSeam, L2) * Ll * 0.6 * sign(el + 1e-6) ;
    // bands: along the world's depth axis, so they run the length of the room on floor, ceiling and walls
    float band = (which == 3) ? 0.0 : step(0.5, fract(depthCoord * f_ * 0.125));
    float bandTone = mix(1.0, 0.72, band * bands);
    // each plane its own tone, lit by how much the sun faces it
    float faceLit = 0.75 + 0.25 * clamp(el, 0.0, 1.0);
    float tone = (0.9 + shade) * bandTone * tileTone * faceLit;
    tone = mix(tone, 0.55, haze * dist);                     // Haze: contrast compresses toward a tone (Leonardo), nothing more
    ground *= planeA;
    float v = ground * clamp(tone, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), ground);                  // opaque wherever the plane is
}
