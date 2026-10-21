# S19 TOPO prototype 2 — thin contour lines (own ink law), exponent scan
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 340

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

SPACINGS = [256, 128, 64, 32, 16, 8, 4, 2]
OCTS = [octave(s, 100+i) for i, s in enumerate(SPACINGS)]
FJ = 2.0 ** np.arange(len(SPACINGS))

def field(aexp):
    w = FJ ** (-aexp)
    w = w / np.sqrt((w**2).sum())
    H = np.zeros((G, G))
    for wj, Bj in zip(w, OCTS):
        H += wj * Bj
    return H / H.std()

def contours(H, P, pct):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0
    thr = np.percentile(F, pct)
    return F < thr

def save(B, name):
    img = np.where(B, 0, 255).astype(np.uint8)
    Image.fromarray(img).resize((680, 680), Image.NEAREST).save(os.path.join(OUT, name))

P = 0.9
for pct in [10, 14]:
    for aexp in [1.6, 1.2, 0.8, 0.5, 0.25]:
        B = contours(field(aexp), P, pct)
        save(B, f"thin_p{pct}_a{aexp:+.2f}.png")
        print(f"pct={pct} a={aexp:+.2f} ink={B.mean():.4f}")
