#!/usr/bin/env python3
"""make_script.py — SP Atom Script: draws REAL glyphs exactly, from the stroke corpus (glyphs/systems.json), baked into
the shader as constant tables. Strokes are the systems' own polylines in writing order. Script picks the system, Glyph the
character (between two integers the old glyph writes out and the new writes in, stroke by stroke, in the system's order),
Write is the written extent. Weight, Ends, Size, X/Y (contained), Slant, Soft. No grammar, no invention: the data drawn."""
import json, os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, "glyphs", "systems.json")))
SYSTEMS = [  # (key, label, selector, limit)
    ("latin_simplex", "latin", lambda g: g["label"].isalnum(), None),
    ("greek", "greek", lambda g: g["label"].isalpha(), None),
    ("futhark", "futhark", None, None),
    ("ogham", "ogham", None, None),
]
if "--full" in sys.argv:
    SYSTEMS += [("japanese", "kana", None, None), ("hanzi", "hanzi", None, 120)]
NAME = "SP Atom Script"
import math
def smooth(st, corner_deg=50.0, passes=3):
    """Chaikin corner-cutting (a quadratic B-spline: never overshoots), with true corners kept sharp: a vertex that turns
    more than corner_deg stays fixed. Duplicate points are collapsed first. Straight polylines come back unchanged."""
    pts = [st[0]] + [q for p_, q in zip(st, st[1:]) if math.hypot(q[0] - p_[0], q[1] - p_[1]) > 1e-6]
    if len(pts) < 3: return pts
    def ang(a, b, c):
        v1 = (b[0] - a[0], b[1] - a[1]); v2 = (c[0] - b[0], c[1] - b[1])
        n1 = math.hypot(*v1); n2 = math.hypot(*v2)
        if n1 < 1e-9 or n2 < 1e-9: return 0.0
        return math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
    fixed = [True] + [ang(pts[i - 1], pts[i], pts[i + 1]) > corner_deg or ang(pts[i - 1], pts[i], pts[i + 1]) < 1.0 for i in range(1, len(pts) - 1)] + [True]
    if all(fixed): return pts
    for _ in range(passes):
        out = [pts[0]]; nf = [True]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            qa = [0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]]; qb = [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]
            if fixed[i] and i > 0: out.append(a); nf.append(True)          # a corner stays
            if not fixed[i]: out.append(qa); nf.append(False)
            if not fixed[i + 1]: out.append(qb); nf.append(False)
        out.append(pts[-1]); nf.append(True)
        pts, fixed = out, nf
    return [[round(x, 4), round(y, 4)] for x, y in pts]
# ── bake: points, stroke starts, glyph starts, per-system glyph ranges, per-glyph bbox ──
PX, PY, SS, GS, SYS, BB = [], [], [0], [0], [0], []
for key, lab, sel, lim in SYSTEMS:
    gl = [g for g in S[key]["glyphs"] if g["strokes"]]
    if sel: gl = [g for g in gl if sel(g)]
    if lim: gl = gl[:lim]
    for g in gl:
        xs = [x for st in g["strokes"] for x, y in st]; ys = [y for st in g["strokes"] for x, y in st]
        BB += [min(xs), min(ys), max(xs), max(ys)]
        for st in g["strokes"]:
            st = smooth(st) if "--raw" not in sys.argv else st
            for x, y in st: PX.append(x); PY.append(y)
            SS.append(len(PX))
        GS.append(len(SS) - 1)
    SYS.append(len(GS) - 1)
NG = len(GS) - 1; NSYS = len(SYSTEMS)
def farr(name, vals, t="float"):
    body = ",".join(("%.3f" % v).rstrip("0").rstrip(".") if t == "float" else str(int(v)) for v in vals)
    body = body.replace("-0,", "0,")
    return f"const {t} {name}[{len(vals)}] = {t}[{len(vals)}]({body});\n"
DATA = farr("PX", PX) + farr("PY", PY) + farr("SS", SS, "int") + farr("GS", GS, "int") + farr("SYSG", SYS, "int") + farr("BB", BB)
INPUTS = [
    {"NAME": "script", "LABEL": "Script", "TYPE": "long", "DEFAULT": 0, "VALUES": list(range(NSYS)), "LABELS": [lab for _, lab, _, _ in SYSTEMS]},
    {"NAME": "glyph",  "LABEL": "Glyph",  "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "write",  "LABEL": "Write",  "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",  "LABEL": "Size",   "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "posx",   "LABEL": "X",      "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "posy",   "LABEL": "Y",      "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "weight", "LABEL": "Weight", "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "ends",   "LABEL": "Ends",   "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1], "LABELS": ["round", "flat"]},
    {"NAME": "slant",  "LABEL": "Slant",  "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "soft",   "LABEL": "Soft",   "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
DATA_TABLES
// one polyline segment, round or flat ends; the stroke's joins are round by construction (capsules overlap)
float seg(vec2 p, vec2 a, vec2 b, float r, int fl) {
    vec2 ba = b - a; float l2 = dot(ba, ba); if (l2 < 1e-9) return length(p - a) - r;
    vec2 pa = p - a; float h = clamp(dot(pa, ba) / l2, 0.0, 1.0);
    if (fl == 0) return length(pa - ba * h) - r;
    float len = sqrt(l2); vec2 u = ba / len; float al = dot(pa, u), pe = abs(dot(pa, vec2(-u.y, u.x)));
    vec2 q = vec2(abs(al - 0.5 * len) - 0.5 * len, pe - r); return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}
float strokeLen(int s) { float L = 0.0; for (int i = SS[s]; i < SS[s + 1] - 1; i++) L += distance(vec2(PX[i], PY[i]), vec2(PX[i + 1], PY[i + 1])); return L; }
// the glyph g, written to 'ext' of its strokes in the system's order: each stroke grows along its own length
float glyphSDF(vec2 p, int g, float ext, float r, int fl) {
    float d = 1e9; int s0 = GS[g], s1 = GS[g + 1]; float NS = float(s1 - s0);
    for (int s = s0; s < s1; s++) {
        float e = clamp(ext * NS - float(s - s0), 0.0, 1.0); if (e <= 0.0) continue;
        int i0 = SS[s], i1 = SS[s + 1];
        if (i1 - i0 == 1) { d = min(d, length(p - vec2(PX[i0], PY[i0])) - r); continue; }
        float L = strokeLen(s), target = e * L, acc = 0.0;
        for (int i = i0; i < i1 - 1; i++) {
            vec2 a = vec2(PX[i], PY[i]), b = vec2(PX[i + 1], PY[i + 1]); float sl = distance(a, b);
            if (acc + sl <= target) { d = min(d, seg(p, a, b, r, (i == i1 - 2) ? fl : 0)); }
            else { float t = clamp((target - acc) / max(sl, 1e-6), 0.0, 1.0); if (t > 0.0) d = min(d, seg(p, a, mix(a, b, t), r, 0)); break; }
            acc += sl;
            if (i == i0 && fl == 1) d = min(d, seg(p, a, b, r, 1));   // first segment flat at its start
        }
    }
    return d;
}
void main() {
    vec2 px = gl_FragCoord.xy - 0.5 * RENDERSIZE.xy;
    float mn = min(RENDERSIZE.x, RENDERSIZE.y);
    int sy = int(clamp(float(script), 0.0, float(NSYS - 1)));
    int g0 = SYSG[sy], g1 = SYSG[sy + 1]; int n = g1 - g0;
    float gf = clamp(glyph, 0.0, 1.0) * float(n - 1);      // Glyph 0..1 spans the whole script: 0 its first glyph, 1 its last
    int gi = g0 + int(floor(gf)); float bl = fract(gf); int gj = min(gi + 1, g1 - 1);
    // the system's frame: baseline 0, cap 1; the glyph is placed by its own box so it never meets the frame
    float r = 0.02 + weight * 0.12;                          // stroke half-width in glyph units
    float unit = (0.05 + sizev * 0.95) * mn * 0.5 / (1.6 + 2.0 * r);   // cap height 1 → the tall side fits at Size 1
    vec4 bA = vec4(BB[gi * 4], BB[gi * 4 + 1], BB[gi * 4 + 2], BB[gi * 4 + 3]);
    vec4 bB = vec4(BB[gj * 4], BB[gj * 4 + 1], BB[gj * 4 + 2], BB[gj * 4 + 3]);
    vec4 bb = vec4(min(bA.xy, bB.xy), max(bA.zw, bB.zw));    // both glyphs of a morph stay inside
    vec2 c = 0.5 * (bb.xy + bb.zw);
    vec2 half_ = (0.5 * (bb.zw - bb.xy) + r + abs(slant) * 0.3) * unit;
    vec2 room = max(0.5 * RENDERSIZE.xy - half_ - 2.0, vec2(0.0));
    vec2 p = (px - vec2(posx, posy) * room) / unit + c;
    p.x -= (p.y - 0.5) * slant * 0.35;                       // Slant: an italic shear about mid-cap
    float aa = (1.0 / unit) * (1.0 + soft * 10.0);
    float outE = (1.0 - smoothstep(0.0, 0.7, bl)) * write, inE = smoothstep(0.3, 1.0, bl) * write;
    float d = glyphSDF(p, gi, outE, r, ends);
    if (gj != gi && inE > 0.0) d = min(d, glyphSDF(p, gj, inE, r, ends));
    float v = 1.0 - smoothstep(-aa, aa, d);
    gl_FragColor = vec4(vec3(v), v);
}
""".replace("DATA_TABLES", DATA + f"const int NSYS = {NSYS};\n")
def emit():
    hdr = {"DESCRIPTION": f"SP Atom Script - real glyphs drawn exactly from the stroke corpus ({', '.join(l for _, l, _, _ in SYSTEMS)}): Script, Glyph (walks; between two the strokes write out/in in the system's order), Write, Size, X/Y (contained), Weight, Ends, Slant, Soft. Alpha = coverage. No drives.",
           "CREDIT": "SP atom; Hershey fonts (public domain), Make Me a Hanzi (Arphic PL)", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out); open(os.path.join(H, f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs", f"{NG} glyphs, {len(PX)} points, {len(out)//1024} KB")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(H, "build_wrapper.py"), NAME, "source"], check=True)
