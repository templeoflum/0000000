#!/usr/bin/env python3
"""make_dither.py — SP Atom Dither: an EFFECT atom for the texture layer, grounded on the two references he named
(MTK Ditherx: 12 ordered patterns by luminance or per-channel, quantize, contrast/bias, tint or sampled colour, downsample;
MTK Retrovision: 32 console engines = real hardware palettes at real native resolutions, true cell-block scaling, dither,
scanlines, tint). Nothing animated: every knob is a position. Real matrices, real palettes (glyphs/../qa/palettes.json).
Order of operations = the hardware's: downsample to cells → contrast/bias → ordered dither threshold → quantize (levels or
palette) → scanlines → tint. Alpha passes through."""
import json, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
NAME = "SP Atom Dither"
PAL_FILE = os.path.join(H, "qa", "palettes.json")
ENGINES = [("none", None)]
PALDATA = json.load(open(PAL_FILE)) if os.path.exists(PAL_FILE) else {}
# ── engine table: fixed palettes become vec3 lists; rgb-bit systems become per-channel levels ──
pal_entries, eng_rows, eng_labels = [], [], ["none"]
eng_rows.append((0, 0, 0, 0, 0.0, 0.0))     # kind(0 none,1 fixed,2 bits), start, count, bits, resW, resH
for slug, d in PALDATA.items():
    eng_labels.append(d["name"])
    w, h = d.get("resolution", [0, 0])
    if d.get("palette_kind") == "fixed" and d.get("palette"):
        start = len(pal_entries)
        for hx in d["palette"][:64]:
            hx = hx.lstrip("#"); pal_entries.append(tuple(int(hx[i:i + 2], 16) / 255.0 for i in (0, 2, 4)))
        eng_rows.append((1, start, len(pal_entries) - start, 0, float(w), float(h)))
    else:
        bits = d.get("bits", [3, 3, 3]); b = bits[0] if isinstance(bits, list) else int(bits)
        eng_rows.append((2, 0, 0, int(b), float(w), float(h)))
NE = len(eng_rows)
def glsl_pal():
    if not pal_entries: return "const vec3 PAL[1] = vec3[1](vec3(0.0));\n"
    return f"const vec3 PAL[{len(pal_entries)}] = vec3[{len(pal_entries)}](" + ",".join("vec3(%.3f,%.3f,%.3f)" % c for c in pal_entries) + ");\n"
def glsl_eng():
    s = f"const int ENG_KIND[{NE}] = int[{NE}](" + ",".join(str(r[0]) for r in eng_rows) + ");\n"
    s += f"const int ENG_START[{NE}] = int[{NE}](" + ",".join(str(r[1]) for r in eng_rows) + ");\n"
    s += f"const int ENG_COUNT[{NE}] = int[{NE}](" + ",".join(str(r[2]) for r in eng_rows) + ");\n"
    s += f"const int ENG_BITS[{NE}] = int[{NE}](" + ",".join(str(r[3]) for r in eng_rows) + ");\n"
    s += f"const vec2 ENG_RES[{NE}] = vec2[{NE}](" + ",".join("vec2(%.0f,%.0f)" % (r[4], r[5]) for r in eng_rows) + ");\n"
    return s
INPUTS = [
    {"NAME": "inputImage", "TYPE": "image"},
    {"NAME": "pattern",  "LABEL": "Pattern",  "TYPE": "long", "DEFAULT": 1, "VALUES": list(range(12)),
     "LABELS": ["bayer 2x2", "bayer 4x4", "bayer 8x8", "halftone dots", "halftone lines", "checker", "noise", "hex dots", "crosshatch", "diamond", "rings", "value noise"]},
    {"NAME": "sizev",    "LABEL": "Size",     "TYPE": "float", "DEFAULT": 4.0, "MIN": 1.0, "MAX": 40.0},
    {"NAME": "mode",     "LABEL": "Mode",     "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["luminance", "per channel"]},
    {"NAME": "levels",   "LABEL": "Levels",   "TYPE": "float", "DEFAULT": 2.0, "MIN": 2.0, "MAX": 16.0},
    {"NAME": "contrast", "LABEL": "Contrast", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.25, "MAX": 4.0},
    {"NAME": "bias",     "LABEL": "Bias",     "TYPE": "float", "DEFAULT": 0.0, "MIN": -0.5, "MAX": 0.5},
    {"NAME": "color",    "LABEL": "Color",    "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["sampled", "tinted"]},
    {"NAME": "low",      "LABEL": "Low",      "TYPE": "color", "DEFAULT": [0.0, 0.0, 0.0, 1.0]},
    {"NAME": "high",     "LABEL": "High",     "TYPE": "color", "DEFAULT": [1.0, 1.0, 1.0, 1.0]},
    {"NAME": "dither",   "LABEL": "Dither",   "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "cells",    "LABEL": "Cells",    "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["off", "on"]},
    {"NAME": "engine",   "LABEL": "Engine",   "TYPE": "long", "DEFAULT": 0, "VALUES": list(range(NE)), "LABELS": eng_labels},
    {"NAME": "native",   "LABEL": "Native",   "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["authentic", "x2"]},
    {"NAME": "scan",     "LABEL": "Scan",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "spacing",  "LABEL": "Spacing",  "TYPE": "float", "DEFAULT": 3.0, "MIN": 1.0, "MAX": 12.0},
    {"NAME": "tint",     "LABEL": "Tint",     "TYPE": "long", "DEFAULT": 0, "VALUES": [0, 1, 2, 3, 4, 5, 6], "LABELS": ["none", "amber", "green", "blue", "sepia", "warm lcd", "cool lcd"]},
    {"NAME": "key",      "LABEL": "Key",      "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "mixv",     "LABEL": "Mix",      "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
PALETTE_TABLES
float h21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(h21(i), h21(i + vec2(1, 0)), f.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), f.x), f.y); }
// Bayer by bit interleaving: the exact recursive matrix, any power of two
float bayer(vec2 p, int n) {
    int x = int(mod(p.x, float(n))), y = int(mod(p.y, float(n))); float v = 0.0, s = 0.5;
    for (int i = 0; i < 3; i++) {
        if (i >= (n == 2 ? 1 : (n == 4 ? 2 : 3))) break;
        int xb = (x >> i) & 1, yb = (y >> i) & 1;
        v += float(xb ^ yb) * s; s *= 0.5; v += float(yb) * s; s *= 0.5;
    }
    return v + s;                                            // centre of the cell's slot: (index + 0.5) / n²
}
// the threshold in (0,1) for pixel p (in pattern pixels): the 12 patterns
float threshold(vec2 p, int pat) {
    if (pat == 0) return bayer(p, 2);
    if (pat == 1) return bayer(p, 4);
    if (pat == 2) return bayer(p, 8);
    vec2 c = fract(p / 6.0) - 0.5;                           // a 6-px cell for the analytic patterns
    if (pat == 3) return clamp(length(c) / 0.7071, 0.0, 1.0);                         // halftone dots: grow from the centre
    if (pat == 4) return abs(fract(p.y / 6.0) - 0.5) * 2.0;                             // halftone lines: grow from the row centre
    if (pat == 5) return mod(floor(p.x) + floor(p.y), 2.0) * 0.5 + 0.25;                // checker: two levels
    if (pat == 6) return h21(floor(p));                                                 // noise ordered: white-noise threshold
    if (pat == 7) { vec2 q = p / 6.0; vec2 r = vec2(1.0, 1.732); vec2 a = mod(q, r) - r * 0.5, b = mod(q - r * 0.5, r) - r * 0.5;   // hex dots
                    return clamp(min(length(a), length(b)) / 0.6, 0.0, 1.0); }
    if (pat == 8) { float l1 = abs(fract((p.x + p.y) / 6.0) - 0.5) * 2.0, l2 = abs(fract((p.x - p.y) / 6.0) - 0.5) * 2.0; return min(l1, l2); }   // crosshatch
    if (pat == 9) return clamp((abs(c.x) + abs(c.y)) / 0.7, 0.0, 1.0);                  // diamond: L1 distance
    if (pat == 10) return fract(length(p - 0.5 * RENDERSIZE.xy / max(sizev, 1.0)) / 4.0);   // rings: concentric from the frame centre
    return vnoise(p / 3.0);                                                              // value noise ordered
}
vec3 quantLevels(vec3 v, float t, float Q) { return floor(v * (Q - 1.0) + t) / (Q - 1.0); }
// nearest palette entry, by a perceptual distance (luma-weighted channels), as a real palette match would be judged
vec3 nearestPal(vec3 v, int start, int count) {
    vec3 best = vec3(0.0); float bd = 1e9; const vec3 W = vec3(0.30, 0.59, 0.11) * 3.0;
    for (int i = 0; i < 64; i++) { if (i >= count) break; vec3 c = PAL[start + i]; vec3 e = (v - c) * W; float d = dot(e, e); if (d < bd) { bd = d; best = c; } }
    return best;
}
// ordered dither against an arbitrary palette: the nearest entry, and the entry on the far side of the value; the threshold
// picks between them by where the value sits on the line joining them. A value beyond the palette's end never dithers.
vec3 ditherPal(vec3 v, float t, float amt, int start, int count) {
    vec3 c1 = nearestPal(v, start, count);
    vec3 c2 = nearestPal(clamp(v + (v - c1) * amt, 0.0, 1.0), start, count);
    vec3 d = c2 - c1; float l2 = dot(d, d); if (l2 < 1e-6) return c1;
    float f = clamp(dot(v - c1, d) / l2, 0.0, 1.0);
    return (t < f) ? c2 : c1;
}
void main() {
    vec2 px = gl_FragCoord.xy;
    int eng = int(clamp(float(engine), 0.0, float(NE - 1)));
    int kind = ENG_KIND[eng];
    // ── cells: the sampling grid. An engine's native resolution sets it (true cell-block scaling); else Size; x2 halves the cell ──
    vec2 cellPx = vec2(sizev);
    if (kind > 0) { vec2 res = ENG_RES[eng]; float sc = max(RENDERSIZE.y / res.y, 1.0); if (native == 1) sc *= 0.5; cellPx = vec2(sc); }
    vec2 cell = floor(px / cellPx);
    vec2 samp = (cells == 1 || kind > 0) ? (cell + 0.5) * cellPx : px;      // downsample: one sample per cell
    vec4 src = IMG_NORM_PIXEL(inputImage, samp / RENDERSIZE.xy);
    float a = src.a;
    if (a <= 0.002) { gl_FragColor = vec4(0.0); return; }    // nothing there stays nothing
    vec3 v = src.rgb / a;                                    // the router hands us premultiplied pixels: work on the colour itself
    v = (v - 0.5) * contrast + 0.5 + bias;
    // ── the dither threshold, in pattern pixels = cells ──
    float t = threshold(cell, pattern);
    float td = mix(0.5, t, dither);                          // Dither: 0 = plain quantize, 1 = the full pattern
    vec3 outc;
    if (kind == 0) {
        float Q = floor(levels + 0.5);
        if (mode == 0) { float l = dot(v, vec3(0.299, 0.587, 0.114)); float q = quantLevels(vec3(l), td, Q).x;
            outc = (color == 1) ? mix(low.rgb, high.rgb, q) : clamp(v * (q / max(l, 1e-4)), 0.0, 1.0); }
        else { vec3 q = quantLevels(v, td, Q); outc = (color == 1) ? mix(low.rgb, high.rgb, q) : q; }
    } else if (kind == 2) {                                  // rgb-bit hardware: each channel to its levels, dithered
        float Q = float(1 << ENG_BITS[eng]); outc = quantLevels(clamp(v, 0.0, 1.0), td, Q);
    } else {                                                 // fixed hardware palette: dither toward the nearest entry
        outc = ditherPal(clamp(v, 0.0, 1.0), t, dither, ENG_START[eng], ENG_COUNT[eng]);
    }
    // ── scanlines: darken every 'spacing' rows, by 'scan' ──
    float sl = 1.0 - scan * 0.9 * (0.5 + 0.5 * cos(6.2831853 * px.y / max(spacing, 1.0)));
    outc *= sl;
    // ── tint: a phosphor / LCD cast on the result's luminance ──
    if (tint > 0) { float l = dot(outc, vec3(0.299, 0.587, 0.114)); vec3 tc = vec3(1.0);
        if (tint == 1) tc = vec3(1.0, 0.69, 0.0); else if (tint == 2) tc = vec3(0.2, 1.0, 0.3); else if (tint == 3) tc = vec3(0.35, 0.55, 1.0);
        else if (tint == 4) tc = vec3(1.0, 0.85, 0.62); else if (tint == 5) tc = vec3(0.61, 0.73, 0.06) * 1.3; else tc = vec3(0.55, 0.75, 0.85) * 1.15;
        outc = tc * l; }
    vec3 res = mix(src.rgb / a, clamp(outc, 0.0, 1.0), mixv);
    // Key: a Video Router hands over an opaque frame (measured: alpha 1 everywhere), so the black it carries is not
    // transparency. Key makes it so: alpha follows the RESULT's brightness, dark to Key's threshold becomes open.
    // At 0 alpha is untouched. With a dither the pattern itself becomes the mask, and what is beneath shows through the dots.
    if (key > 0.001) { float l = max(max(res.r, res.g), res.b); a *= smoothstep(0.0, key, l); }
    gl_FragColor = vec4(res * a, a);                         // premultiplied out
}
""".replace("PALETTE_TABLES", glsl_pal() + glsl_eng() + f"const int NE = {NE};\n")
def emit():
    hdr = {"DESCRIPTION": "SP Atom Dither - texture layer effect: 12 ordered dither patterns (real Bayer matrices, halftone, hex, hatch, rings, noise), Size, luminance / per-channel, Levels, Contrast, Bias, sampled or tinted colour, Cells (downsample); Engine = real console palettes at their native resolutions (authentic / x2), Scan(lines), Spacing, Tint, Key (opaque router feed: dark becomes open), Mix. No drives.",
           "CREDIT": "SP atom; references MTK Ditherx / Retrovision", "ISFVSN": "2", "CATEGORIES": ["Stylize"], "INPUTS": INPUTS}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out); open(os.path.join(H, f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs", f"{NE - 1} engines, {len(pal_entries)} palette entries")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(H, "build_wrapper.py"), NAME, "effect"], check=True)
