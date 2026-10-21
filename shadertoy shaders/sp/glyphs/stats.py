#!/usr/bin/env python3
"""stats.py — measure the real systems with the research's yardsticks (Changizi strokes/junctions, Morin orientations
and symmetry, Fiset terminals) so the atom's grammar is extracted, not assumed. Writes glyphs/stats.json."""
import json, math, os, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, "systems.json")))

def seglen(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])
def resample(st, step=0.04):
    """polyline → points every 'step' along its length (so curves count by length, not by vertex count)"""
    out = [st[0]]; acc = 0.0
    for a, b in zip(st, st[1:]):
        L = seglen(a, b)
        if L < 1e-9: continue
        n = int(L / step)
        for k in range(1, n + 1):
            t = k * step / L; out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    if out[-1] != st[-1]: out.append(st[-1])
    return out
def orient_class(a, b):
    ang = abs(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) % 180
    d = min(ang, abs(ang - 90), abs(ang - 180))
    return "cardinal" if d <= 15 else "oblique"
def curvature_share(st):
    """share of the stroke's length spent turning (angle change between successive resampled segments > 8°)"""
    pts = resample(st); turn = 0.0; tot = 0.0
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        L = seglen(a, b); tot += L
        a1 = math.atan2(b[1] - a[1], b[0] - a[0]); a2 = math.atan2(c[1] - b[1], c[0] - b[0])
        if abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi) > math.radians(8): turn += L
    return turn / tot if tot > 0 else 0.0
def near_body(p, st, tol):
    """distance from p to polyline st (excluding its own ends)"""
    best = 9e9
    for a, b in zip(st, st[1:]):
        ab = [b[0] - a[0], b[1] - a[1]]; l2 = ab[0] ** 2 + ab[1] ** 2
        if l2 < 1e-12: continue
        t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / l2))
        q = [a[0] + ab[0] * t, a[1] + ab[1] * t]; best = min(best, seglen(p, q))
    return best
def junctions(strokes, tol=0.06):
    """L: two stroke ENDS meet; T: an end meets another stroke's body; X: two bodies cross (segment intersection away from ends)"""
    L = T = X = 0; ends = []
    for i, st in enumerate(strokes): ends += [(i, st[0]), (i, st[-1])]
    # L
    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            if ends[a][0] != ends[b][0] and seglen(ends[a][1], ends[b][1]) < tol: L += 1
    # T
    for i, p in ends:
        for j, st in enumerate(strokes):
            if j == i: continue
            if near_body(p, st, tol) < tol and seglen(p, st[0]) > tol and seglen(p, st[-1]) > tol: T += 1
    # X: proper segment crossings between strokes
    def cross(a, b, c, d):
        def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)
    for i in range(len(strokes)):
        for j in range(i + 1, len(strokes)):
            for a, b in zip(strokes[i], strokes[i][1:]):
                for c, d in zip(strokes[j], strokes[j][1:]):
                    if cross(a, b, c, d) and min(seglen(a, c), seglen(a, d), seglen(b, c), seglen(b, d)) > tol: X += 1
    return L, T, X
def terminals(strokes, tol=0.06):
    """free ends: stroke ends that meet nothing"""
    n = 0
    for i, st in enumerate(strokes):
        for p in (st[0], st[-1]):
            free = True
            for j, o in enumerate(strokes):
                if j == i: continue
                if near_body(p, o, tol) < tol: free = False; break
            if free and seglen(st[0], st[-1]) > tol: n += 1
    return n
def mirror_score(strokes):
    """vertical-axis symmetry: fraction of resampled points whose mirror lies on the glyph"""
    pts = [p for st in strokes for p in resample(st)]
    if len(pts) < 4: return 0.0
    xs = [p[0] for p in pts]; cx = (max(xs) + min(xs)) / 2; w = max(xs) - min(xs) + 1e-6
    hits = 0
    for p in pts:
        m = [2 * cx - p[0], p[1]]
        if min(near_body(m, st, 1) for st in strokes) < 0.05 * max(w, 1): hits += 1
    return hits / len(pts)

out = {}
for key, sysd in S.items():
    gl = [g for g in sysd["glyphs"] if g["strokes"]]
    if key in ("latin_simplex", "latin_times", "latin_gothic", "latin_cursive", "greek", "cyrillic"):
        gl = [g for g in gl if g["label"].isalpha()]                  # letters only, not punctuation
    if key == "hanzi": gl = gl[:400]
    sc = Counter(); orient = Counter(); Lj = Tj = Xj = 0; term = []; mir = []; asp = []; curv = []; ink = []
    for g in gl:
        strokes = [st for st in g["strokes"] if len(st) >= 2]
        sc[len(strokes)] += 1
        for st in strokes:
            pts = resample(st)
            for a, b in zip(pts, pts[1:]): orient[orient_class(a, b)] += seglen(a, b)
            curv.append(curvature_share(st))
        L, T, X = junctions(strokes); Lj += L; Tj += T; Xj += X
        term.append(terminals(strokes)); mir.append(mirror_score(strokes))
        xs = [x for st in strokes for x, y in st]; ys = [y for st in strokes for x, y in st]
        asp.append((max(xs) - min(xs)) / max(max(ys) - min(ys), 1e-6))
        ink.append(sum(seglen(a, b) for st in strokes for a, b in zip(st, st[1:])))
    n = len(gl); tot = sum(orient.values()) or 1
    out[key] = {"name": sysd["name"], "n": n,
        "strokes_mean": round(sum(k * v for k, v in sc.items()) / n, 2), "strokes_hist": dict(sorted(sc.items())),
        "cardinal_share": round(orient["cardinal"] / tot, 2), "oblique_share": round(orient["oblique"] / tot, 2),
        "curved_share": round(sum(curv) / max(len(curv), 1), 2),
        "junctions_LTX_per_glyph": [round(Lj / n, 2), round(Tj / n, 2), round(Xj / n, 2)],
        "terminals_mean": round(sum(term) / n, 2), "mirror_mean": round(sum(mir) / n, 2),
        "aspect_mean": round(sum(asp) / n, 2), "ink_mean": round(sum(ink) / n, 2)}
    print(f"{key:15s} n={n:4d} strokes {out[key]['strokes_mean']:4.1f}  card {out[key]['cardinal_share']:.2f} obl {out[key]['oblique_share']:.2f} curved {out[key]['curved_share']:.2f}  L/T/X {out[key]['junctions_LTX_per_glyph']}  term {out[key]['terminals_mean']:.1f} mirror {out[key]['mirror_mean']:.2f} aspect {out[key]['aspect_mean']:.2f}")
json.dump(out, open(os.path.join(H, "stats.json"), "w"), indent=1)
