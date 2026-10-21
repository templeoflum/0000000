#!/usr/bin/env python3
"""make_ground.py — SP Atom Ground: the field as a CAMERA over a lit, tiled plane (the crowned build,
regenerated verbatim from the retired shader on 2026-09-03 after the room detour was scrapped)."""
import json, os, subprocess, sys

NAME = "SP Atom Ground"
INPUTS = [
    {"NAME": "tilt", "LABEL": "Tilt", "TYPE": "float", "DEFAULT": -1.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "sway", "LABEL": "Sway", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "bob", "LABEL": "Bob", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "travel", "LABEL": "Travel", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "horizon", "LABEL": "Horizon", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "yaw", "LABEL": "Yaw", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "dolly", "LABEL": "Dolly", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "focal", "LABEL": "Focal mm", "TYPE": "float", "DEFAULT": 35.0, "MIN": 14.0, "MAX": 200.0},
    {"NAME": "proj", "LABEL": "Lens", "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1, 2, 3, 4], "LABELS": ["rectilinear", "stereographic", "equidistant", "equisolid", "orthographic"]},
    {"NAME": "distort", "LABEL": "Distort", "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.6, "MAX": 0.6},
    {"NAME": "scalev", "LABEL": "Scale", "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "gap", "LABEL": "Gap", "TYPE": "float", "DEFAULT": 0.15, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "seamv",   "LABEL": "Seam",    "TYPE": "float", "DEFAULT": 0.15, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "bands", "LABEL": "Bands", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sun", "LABEL": "Sun", "TYPE": "float", "DEFAULT": 0.25, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "height", "LABEL": "Height", "TYPE": "float", "DEFAULT": 0.7, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "relief", "LABEL": "Relief", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "haze", "LABEL": "Haze", "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "soft", "LABEL": "Soft", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""

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
    // the camera: height camH above the plane, lateral position camX, forward position camZ
    float camH = 1.0 + bob * 0.35, camX = sway * 0.6, camZ = travel * 4.0 + D;
    float w = 0.5 / RENDERSIZE.y + soft * 0.35;
    float ground = smoothstep(0.0, w, -d.y);                 // Soft: vanishes into the horizon (never above it)
    if (ground <= 0.0) { gl_FragColor = vec4(0.0); return; }
    float t = camH / max(-d.y, 1e-5);
    float x = camX + d.x * t, z = camZ + d.z * t;            // the point on the plane
    float f_ = 2.0 + scalev * 18.0;
    vec2 cell = vec2(x, z) * f_ * 0.25;
    vec2 g = abs(fract(cell) - 0.5) * 2.0;
    float aa = max(fwidth(cell.x), fwidth(cell.y)) * 1.5;
    float dist = 1.0 - 1.0 / (1.0 + t * 0.12);              // 0 near → 1 far, by ray length
    float detail = 1.0 - haze * dist;
    float seamW = gap * 0.5 * detail;
    float seam = max(smoothstep(1.0 - seamW - aa, 1.0 - seamW + aa, g.x), smoothstep(1.0 - seamW - aa, 1.0 - seamW + aa, g.y));
    float tile = 1.0 - seam * detail;
    float tileTone = mix(seamv, 1.0, tile);                  // Seam: the gap's tone. The floor is solid; a gap is a line, not a hole
    // the sun on the tile lips — relief flips dome ↔ pit as the sun crosses the horizon (the crater illusion)
    float sunA = sun * 2.0 * PI; vec2 L2 = vec2(cos(sunA), sin(sunA));
    float el = (height - 0.5) * 2.0;
    vec2 toSeam = (g.x > g.y) ? vec2(sign(fract(cell.x) - 0.5), 0.0) : vec2(0.0, sign(fract(cell.y) - 0.5));
    float din = 1.0 - max(g.x, g.y);
    float lipW = 0.08 + relief * 0.4;
    float lip = 1.0 - smoothstep(0.0, lipW, din); lip = lip * lip * (3.0 - 2.0 * lip);
    float shade = relief * lip * dot(toSeam, L2) * el * 0.6;
    float band = step(0.5, fract(cell.y * 0.5));
    float bandTone = mix(1.0, 0.72, band * bands);
    float tone = (0.9 + shade) * bandTone * tileTone;
    tone = mix(tone, 0.55, haze * dist * dist);              // Haze: contrast compresses toward a tone
    float v = ground * clamp(tone, 0.0, 1.0);
    gl_FragColor = vec4(vec3(v), ground);                  // opaque wherever the plane is
}
"""
def emit():
    hdr = {"DESCRIPTION": "SP Atom Ground v4 - a real camera over a lit, tiled plane: WORLD: Tilt (roll, full turn), Sway/Bob/Travel; CAMERA: Horizon (pitch), Yaw (turn), Dolly (dolly zoom), Focal mm (35mm-equiv), Lens (rectilinear/stereographic/equidistant/equisolid/orthographic), Distort (Brown-Conrady k1), Scale, Gap, Seam (gap tone; solid floor), Bands, Sun/Height/Relief, Haze, Soft. No drives.",
           "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS,
           }
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), NAME, "source"], check=True)
