#!/usr/bin/env python3
"""sheets.py — render each system's glyphs as a contact sheet (real strokes, drawn as they are) for looking."""
import json, os, sys
from PIL import Image, ImageDraw
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "systems.json")))
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
def sheet(key, cols=16, cell=96, limit=None):
    gl = S[key]["glyphs"][:limit]
    rows = (len(gl) + cols - 1) // cols
    im = Image.new("L", (cols * cell, rows * cell), 0); dr = ImageDraw.Draw(im)
    for i, g in enumerate(gl):
        ox, oy = (i % cols) * cell, (i // cols) * cell
        xs = [x for st in g["strokes"] for x, y in st]; ys = [y for st in g["strokes"] for x, y in st]
        if not xs: continue
        w = max(xs) - min(xs); h = max(ys) - min(ys); sc = (cell * 0.7) / max(w, h, 1e-3)
        cx = (max(xs) + min(xs)) / 2; cy = (max(ys) + min(ys)) / 2
        for st in g["strokes"]:
            pts = [(ox + cell / 2 + (x - cx) * sc, oy + cell / 2 - (y - cy) * sc) for x, y in st]
            if len(pts) == 1: pts = pts * 2
            dr.line(pts, fill=255, width=3, joint="curve")
    im.save(os.path.join(OUT, f"sheet_{key}.png")); return im.size
for k in S: print(k, sheet(k, limit=256))
