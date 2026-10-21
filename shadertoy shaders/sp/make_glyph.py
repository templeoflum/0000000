#!/usr/bin/env python3
"""make_glyph.py — SP Atom Glyph, rebuilt on the data (symbol-glyph-references):
Changizi: ~3 strokes per character, junctions L > T > X, signs shaped for the eye. Morin: cardinal strokes, at most one
oblique, vertical-axis symmetry only. Fiset: terminals are the identity signal. Letter Spirit: a glyph is ROLES filled on a
lattice with baseline / x-height / ascender / descender zones; style is one rule applied to every glyph. Saussure/earcon:
a symbol is a slot in a small closed inventory — so a LANGUAGE seed makes an alphabet of 24 siblings and Glyph picks one.
Chinese stroke order + top-down reading: between two glyphs the strokes write out and in, in order. Tools as styles:
letter (roles), rune (no horizontals), ogham (count x side on a stem), sigil (three letters superposed and merged).
Contained, white, alpha = coverage. No drives."""
import json, os, subprocess, sys

NAME = "SP Atom Glyph"
INPUTS = [
    {"NAME": "style",    "LABEL": "Style",    "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2, 3], "LABELS": ["letter", "rune", "ogham", "sigil"]},
    {"NAME": "language", "LABEL": "Language", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 32.0},
    {"NAME": "glyph",    "LABEL": "Glyph",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 24.0},
    {"NAME": "ends",     "LABEL": "Ends",     "TYPE": "long",  "DEFAULT": 0, "VALUES": [0, 1, 2], "LABELS": ["round", "flat", "serif"]},
    {"NAME": "write",    "LABEL": "Write",    "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "sizev",    "LABEL": "Size",     "TYPE": "float", "DEFAULT": 0.4, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "posx",     "LABEL": "X",        "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "posy",     "LABEL": "Y",        "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "weight",   "LABEL": "Weight",   "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "contrast", "LABEL": "Contrast", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "slant",    "LABEL": "Slant",    "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
    {"NAME": "width",    "LABEL": "Width",    "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "roundv",   "LABEL": "Round",    "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "hand",     "LABEL": "Hand",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "soft",     "LABEL": "Soft",     "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
]
BODY = r"""
float gh(float L, float g, float n) { return fract(sin(dot(vec3(L, g, n), vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
// the lattice: 3 columns x 5 rows. Row 0 descender, 1 baseline, 3 x-height, 4 ascender. Point (i, j) -> (i - 1, j - 2).
vec2 lp(float i, float j) { return vec2(i - 1.0, j - 2.0); }
// ── the glyph grammar: stroke i of glyph g in language L. Returns (a, b) as lattice coords; absent = a == b. ──
// Slot 0 is the post. Slots 1..3 are roles hung on the post: crossbar (L or T with the post), side (closes a counter),
// hook (the one oblique), second post. Slots 4..5 mirror 1..2 about the centre column in a mirroring language.
vec4 strokeOf(float L, float g, int st, int i) {
    float fi = float(i);
    // the language's rules, one for every glyph
    float diagOK = step(gh(L, -1.0, 1.0), 0.6);              // 60 % of languages allow an oblique
    float mirror = step(gh(L, -1.0, 2.0), 0.3);              // 30 % mirror about the vertical axis
    float wide   = step(gh(L, -1.0, 3.0), 0.5);              // crossbars span 2 columns, else 1
    float tall   = 0.15 + 0.25 * gh(L, -1.0, 4.0);           // how often glyphs reach the ascender / descender
    if (st == 1) { diagOK = 1.0; }                           // rune: a tool with no horizontals
    // the post
    float hp = gh(L, g, 0.0);
    float pc = (hp < 0.4) ? 0.0 : ((hp < 0.8) ? 2.0 : 1.0);  // posts favour the sides (b d p q), sometimes the centre (t i)
    float dir = (pc == 2.0) ? -1.0 : 1.0;                    // roles hang toward the other side
    if (pc == 1.0) dir = (gh(L, g, 0.5) < 0.5) ? -1.0 : 1.0;
    float top = 3.0 + step(1.0 - tall, gh(L, g, 1.0));        // ascender?
    float bot = 1.0 - step(1.0 - tall, gh(L, g, 2.0));        // descender?
    if (st == 1) { top = 4.0; bot = 1.0; }                   // runes stand full height
    if (st == 2) {                                           // ogham: a stem, and 1..5 strokes on one side, or across
        if (i == 0) return vec4(lp(1.0, 0.0), lp(1.0, 4.0));
        float n = 1.0 + floor(gh(L, g, 3.0) * 5.0);
        if (fi > n) return vec4(0.0);
        float side = floor(gh(L, g, 4.0) * 3.0);             // 0 left, 1 right, 2 across
        float r = 4.0 - (fi - 0.5) * (3.6 / n) - 0.2;        // spaced down the stem
        float x0 = (side == 1.0) ? 1.0 : 0.0, x1 = (side == 0.0) ? 1.0 : 2.0;
        return vec4(lp(x0, r), lp(x1, r));
    }
    if (i == 0) return vec4(lp(pc, bot), lp(pc, top));
    int j = i; float mirrored = 0.0;
    if (i >= 4) { if (mirror < 0.5 || pc == 1.0) return vec4(0.0); j = i - 3; mirrored = 1.0; }
    float fj = float(j);
    // is this role present? slot 1 nearly always, then fewer: 2..4 strokes a glyph (Changizi's 3)
    float pres = (j == 1) ? 0.95 : ((j == 2) ? 0.55 : 0.3);
    if (gh(L, g, 10.0 + fj) > pres) return vec4(0.0);
    vec4 sgm;
    if (st == 1) {                                           // rune: twigs, obliques off the post
        float r = 1.0 + floor(gh(L, g, 20.0 + fj) * 3.0);    // from row 1, 2 or 3
        float up = (gh(L, g, 30.0 + fj) < 0.5) ? 1.0 : -1.0;
        float d2 = (gh(L, g, 40.0 + fj) < 0.7) ? dir : -dir;
        sgm = vec4(lp(pc, r), lp(pc + d2, r + up));
    } else {
        float role = gh(L, g, 20.0 + fj);
        float rr = 1.0 + floor(gh(L, g, 30.0 + fj) * 3.0);   // a row: baseline, mid, x-height
        float span = 1.0 + wide;
        if (pc == 1.0) span = 1.0;
        if (role < 0.45) {                                   // crossbar
            sgm = vec4(lp(pc, rr), lp(pc + dir * span, rr));
        } else if (role < 0.7 && j > 1 && gh(L, g, 21.0) < 0.45) {   // side: closes a counter, only once slot 1 laid a crossbar
            float r0 = 1.0 + floor(gh(L, g, 40.0 + fj) * 2.0);
            sgm = vec4(lp(pc + dir * span, r0), lp(pc + dir * span, r0 + 1.0));
        } else if (role < 0.7) {                             // no crossbar to close against: be a crossbar instead
            sgm = vec4(lp(pc, rr), lp(pc + dir * span, rr));
        } else if (role < 0.85 && diagOK > 0.5 && j == 1) {  // the one oblique: a hook off a terminal
            float r0 = (gh(L, g, 50.0) < 0.5) ? top : bot; float up = (r0 == top) ? -1.0 : 1.0;
            sgm = vec4(lp(pc, r0), lp(pc + dir, r0 + up));
        } else {                                             // second post
            sgm = vec4(lp(pc + dir * span, 1.0), lp(pc + dir * span, 3.0));
        }
    }
    if (mirrored > 0.5) { sgm.x = -sgm.x; sgm.z = -sgm.z; }
    return sgm;
}
float strokeSDF(vec2 p, vec2 a, vec2 b, float r, int endStyle, float exA, float exB) {
    vec2 ba = b - a; float len = length(ba); if (len < 1e-4) return 1e9;
    vec2 u = ba / len;
    if (endStyle != 0) { a -= u * max(exA, 0.0); b += u * max(exB, 0.0); ba = b - a; len = length(ba); }   // square caps run through corners
    vec2 pa = p - a;
    float along = dot(pa, u), perp = abs(dot(pa, vec2(-u.y, u.x)));
    float d;
    if (endStyle == 0) { float h = clamp(along / len, 0.0, 1.0); d = length(pa - ba * h) - r; }
    else { vec2 q = vec2(abs(along - 0.5 * len) - 0.5 * len, perp - r); d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0); }
    if (endStyle == 2 && abs(u.x) < 0.3) {                   // serif: a small bar across each FREE end of a vertical
        vec2 s = vec2(0.28, r * 0.6);
        vec2 qa = vec2(perp - s.x, abs(along) - s.y), qb = vec2(perp - s.x, abs(along - len) - s.y);
        if (exA == 0.0) d = min(d, length(max(qa, 0.0)) + min(max(qa.x, qa.y), 0.0));
        if (exB == 0.0) d = min(d, length(max(qb, 0.0)) + min(max(qb.x, qb.y), 0.0));
    }
    return d;
}
// the fillet: a solid wedge in the concave corner where two stroke edges meet (corner c, this stroke along u with half-width ri,
// the other along v with half-width rj): the k-square in that corner minus the circle of radius k — a real inner radius
float fillet(vec2 p, vec2 c, vec2 u, vec2 v, float ri, float rj, float k) {
    // the concave corner: where this stroke's edge (offset ri toward v) meets the other's edge (offset rj toward u)
    vec2 ni = normalize(v - u * dot(u, v)), nj = normalize(u - v * dot(u, v));
    vec2 ei = c + ni * ri, ej = c + nj * rj;
    float den = u.x * v.y - u.y * v.x; if (abs(den) < 1e-4) return 1e9;
    float t = ((ej.x - ei.x) * v.y - (ej.y - ei.y) * v.x) / den;
    vec2 corner = ei + u * t;
    vec2 q = p - corner;
    float x = dot(q, u), y = dot(q, v);
    float ov = 0.06;                                         // the wedge runs a little into both strokes: no seam
    return max(max(max(x - k, y - k), max(-x - ov, -y - ov)), k - length(vec2(k - x, k - y)));
}
// does lattice point q meet stroke s (an endpoint, or a point along it)?
int meets(vec2 q, vec4 s) {
    if (s.x == s.z && s.y == s.w) return 0;
    if (length(q - s.xy) < 0.02 || length(q - s.zw) < 0.02) return 2;   // a corner
    vec2 a = s.xy, b = s.zw; vec2 ab = b - a; float l2 = dot(ab, ab);
    float t = dot(q - a, ab) / l2;
    return (t > 0.0 && t < 1.0 && length(q - (a + ab * t)) < 0.02) ? 1 : 0;   // a tee
}
// Hand: each lattice point drifts a little, per language; strokes that share a point stay joined (workmanship of risk)
vec2 handPt(vec2 q, float L, float hnd) { return q + (vec2(gh(L, q.x, q.y + 7.0), gh(L, q.y, q.x + 3.0)) - 0.5) * hnd * 0.3; }
// one glyph, written to 'ext' of its strokes in stroke order (post first): 0 = blank, 1 = whole
float glyphSDF(vec2 p, float L, float g, int st, float ext, float wgt, float ctr, int endStyle, float NS, float rnd, float hnd) {
    float d = 1e9;
    vec4 S[6];
    for (int i = 0; i < 6; i++) S[i] = strokeOf(L, g, st, i);
    for (int i = 0; i < 6; i++) {
        vec4 s = S[i];
        if (s.x == s.z && s.y == s.w) continue;
        float e = clamp(ext * NS - float(i), 0.0, 1.0);      // this stroke's written length, in order
        e = e * e * (3.0 - 2.0 * e);
        if (e <= 0.001) continue;
        float horiz = 1.0 - abs(normalize(s.zw - s.xy).y);   // Contrast: horizontals and obliques thinner than the posts
        float r = wgt * (1.0 - ctr * 0.65 * horiz) * smoothstep(0.0, 0.25, e) * (0.5 + 0.5 * e);   // a stroke grows from nothing
        // ends: -1 = still being written (no cap dressing), 0 = free (serif allowed), r = a corner (square cap runs r past it)
        float exA = 0.0, exB = (e > 0.999) ? 0.0 : -1.0;
        for (int j = 0; j < 6; j++) { if (j == i) continue;
            vec4 sj = S[j]; float ej = clamp(ext * NS - float(j), 0.0, 1.0); if (ej <= 0.001) continue;   // only strokes that exist yet
            int mA = meets(s.xy, sj), mB = meets(s.zw, sj);
            if (mA == 1) exA = -1.0; else if (mA == 2 && exA == 0.0) exA = r;      // a body under the point covers it: no extension, no serif
            if (e > 0.999) { if (mB == 1) exB = -1.0; else if (mB == 2 && exB == 0.0) exB = r; } }
        vec2 a = handPt(s.xy, L, hnd), b = mix(a, handPt(s.zw, L, hnd), e);
        float sd = strokeSDF(p, a, b, r, endStyle, exA, exB);
        d = min(d, sd);
        if (rnd > 0.001 && e > 0.999) {                     // Round: fillets in the concave corners of this stroke's joins
            float k = rnd * 0.3; vec2 u = normalize(b - a);
            for (int j = 0; j < 6; j++) { if (j == i) continue;
                vec4 sj = S[j]; float ej = clamp(ext * NS - float(j), 0.0, 1.0); if (ej <= 0.999) continue;
                float hj = 1.0 - abs(normalize(sj.zw - sj.xy).y); float rj = wgt * (1.0 - ctr * 0.65 * hj);
                vec2 ja = handPt(sj.xy, L, hnd), jb = handPt(sj.zw, L, hnd); vec2 uj = normalize(jb - ja);
                for (int end = 0; end < 2; end++) {
                    vec2 c = (end == 0) ? a : b; vec2 ui = (end == 0) ? u : -u;   // into this stroke from its end
                    int m = meets((end == 0) ? s.xy : s.zw, sj); if (m == 0) continue;
                    if (abs(dot(ui, uj)) > 0.3) continue;                        // fillets only where strokes meet near square
                    if (m == 2) { vec2 far = (length(c - ja) < length(c - jb)) ? jb : ja; vec2 v = normalize(far - c);
                                  d = min(d, fillet(p, c, ui, v, r, rj, k)); }
                    else { d = min(d, fillet(p, c, ui, uj, r, rj, k)); d = min(d, fillet(p, c, ui, -uj, r, rj, k)); }
                } }
        }
    }
    return d;
}
void main() {
    vec2 px = gl_FragCoord.xy - 0.5 * RENDERSIZE.xy;
    float mn = min(RENDERSIZE.x, RENDERSIZE.y);
    float wgt = 0.05 + weight * 0.25;
    float unit = (0.06 + sizev * 0.94) * mn * 0.5 / (4.0 + 2.0 * wgt);   // one lattice unit in pixels: 4 rows tall fit
    float wid = 0.6 + width * 0.8;                           // Width: the columns' spacing
    vec2 half_ = vec2((1.0 + wgt + 0.3 + abs(slant) * 0.8) * wid, 2.0 + wgt) * unit;
    vec2 room = max(0.5 * RENDERSIZE.xy - half_ - 2.0, vec2(0.0));
    vec2 p = (px - vec2(posx, posy) * room) / unit;
    p.x = (p.x - p.y * slant * 0.4) / wid;                   // Slant: an italic shear about the mid-line
    float L = floor(language);
    float g = floor(glyph), bl = fract(glyph);
    float aa = (1.0 / unit) * (1.0 + soft * 12.0);
    // the writing: the old glyph writes out (last stroke first), then the new one writes in, stroke by stroke
    float outE = (1.0 - smoothstep(0.0, 0.7, bl)) * write, inE = smoothstep(0.3, 1.0, bl) * write;   // they overlap: never blank
    float d = 1e9;
    if (style == 3) {                                        // sigil: three letters of the language superposed and merged
        for (int k = 0; k < 3; k++) {
            float gk = mod(g + float(k) * 7.0, 24.0), gk1 = mod(g + 1.0 + float(k) * 7.0, 24.0);
            d = min(d, glyphSDF(p, L, gk, 0, outE, wgt, contrast, ends, 6.0, roundv, hand));
            d = min(d, glyphSDF(p, L, gk1, 0, inE, wgt, contrast, ends, 6.0, roundv, hand));
        }
    } else {
        d = min(d, glyphSDF(p, L, g, style, outE, wgt, contrast, ends, 6.0, roundv, hand));
        d = min(d, glyphSDF(p, L, g + 1.0, style, inE, wgt, contrast, ends, 6.0, roundv, hand));
    }
    float v = 1.0 - smoothstep(-aa, aa, d);
    gl_FragColor = vec4(vec3(v), v);
}
"""
def emit():
    hdr = {"DESCRIPTION": "SP Atom Glyph - a glyph synth, one voice: Style (letter/rune/ogham/sigil), Language (the alphabet), Glyph (which of 24; between two, the strokes write out and in, in order), Ends (round/flat/serif), Write (0 blank to 1 whole, in stroke order), Size, X/Y (contained), Weight, Contrast, Slant, Width, Round (joins), Hand (the hand's drift), Soft. Grounded: ~3 strokes, roles on a baseline lattice, cardinal strokes, one oblique at most. White, alpha = coverage. No drives.",
           "CREDIT": "SP atom", "ISFVSN": "2", "CATEGORIES": ["Generator"], "INPUTS": INPUTS}
    out = "/*" + json.dumps(hdr, indent=2) + "*/\n" + BODY
    D = os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{NAME}/Resource"); os.makedirs(D, exist_ok=True)
    open(f"{D}/{NAME}.fs", "w").write(out)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}.fs"), "w").write(out)
    json.dump({}, open(f"{D}/{NAME}.sp.json", "w"))
    print("wrote", f"{D}/{NAME}.fs")
emit()
if "--build" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wrapper.py"), NAME, "source"], check=True)
