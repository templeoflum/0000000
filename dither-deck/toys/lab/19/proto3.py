# S19 TOPO prototype 3 — final range + 200-step granularity + states
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))

def build_octaves(G, base):
    def octave(spacing, seed):
        rng = np.random.RandomState(seed)
        n = int(np.ceil(G / spacing)) + 2
        lat = rng.rand(n, n)
        ys = np.arange(G) / spacing
        xs = np.arange(G) / spacing
        iy = np.floor(ys).astype(int); ix = np.floor(xs).astype(int)
        fy = ys - iy; fx = xs - ix
        sy = fy*fy*(3-2*fy); sx = fx*fx*(3-2*fx)
        a = lat[np.ix_(iy, ix)];   b = lat[np.ix_(iy, ix+1)]
        c = lat[np.ix_(iy+1, ix)]; d = lat[np.ix_(iy+1, ix+1)]
        top = a*(1-sx)[None,:] + b*sx[None,:]
        bot = c*(1-sx)[None,:] + d*sx[None,:]
        v = top*(1-sy)[:,None] + bot*sy[:,None]
        v = v - v.mean()
        return v / v.std()
    sp = [base, base/2, base/4, base/8, base/16, base/32, base/64, base/128]
    return [octave(s, 100+i) for i, s in enumerate(sp)]

A0, A1 = 1.75, 0.45
P = 0.9
PCT = 13.0

def field(OCTS, FJ, k):
    a = A0 + (A1 - A0) * k
    w = FJ ** (-a)
    w = w / np.sqrt((w**2).sum())
    H = np.zeros_like(OCTS[0])
    for wj, Bj in zip(w, OCTS):
        H += wj * Bj
    return H / H.std()

def contours(H):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0
    thr = np.percentile(F, PCT)
    return F < thr

def save(B, name, up):
    img = np.where(B, 0, 255).astype(np.uint8)
    Image.fromarray(img).resize((up, up), Image.NEAREST).save(os.path.join(OUT, name))

FJ = 2.0 ** np.arange(8)

for G, tag in [(340, "s"), (680, "f")]:
    OCTS = build_octaves(G, 256 * G // 340)
    # states
    if tag == "f":
        for k in [0.0, 0.25, 0.5, 0.75, 1.0]:
            B = contours(field(OCTS, FJ, k))
            save(B, f"state_k{int(k*100):03d}.png", 680)
            print(f"k={k:.2f} ink={B.mean():.4f}")
    # granularity: 200-step sweep
    prev = None
    worst = 0.0; worstk = 0.0; tot = 0.0
    inks = []
    for i in range(201):
        k = i / 200
        B = contours(field(OCTS, FJ, k))
        inks.append(B.mean())
        if prev is not None:
            fl = np.mean(B != prev)
            tot += fl
            if fl > worst: worst, worstk = fl, k
        prev = B
    print(f"[{tag} G={G}] worst flip/1-200 step = {worst*100:.2f}% at k={worstk:.3f}, "
          f"mean={tot/200*100:.2f}%, ink min/max={min(inks):.4f}/{max(inks):.4f}")
