# S19 TOPO prototype — octave terrain, k = spectral exponent, contours at 45th pct
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 340
rng_global = np.random.RandomState(19)

def octave(spacing, seed):
    """value noise: random lattice at given px spacing, smoothstep-interpolated."""
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
FJ = 2.0 ** np.arange(len(SPACINGS))   # octave base frequencies

def field(aexp):
    w = FJ ** (-aexp)
    w = w / np.sqrt((w**2).sum())
    H = np.zeros((G, G))
    for wj, Bj in zip(w, OCTS):
        H += wj * Bj
    return H / H.std()

def contours(H, P):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0          # triangle ridges, 0 at contour line
    thr = np.percentile(F, 45.0)       # exact 45th percentile (02's law)
    B = F < thr
    return B, thr

def save(B, name):
    img = np.where(B, 0, 255).astype(np.uint8)
    Image.fromarray(img).resize((680, 680), Image.NEAREST).save(os.path.join(OUT, name))

# scan spectral exponent to find the distinct regime ladder
P = 0.9
for aexp in [1.6, 1.3, 1.1, 0.9, 0.7, 0.5, 0.3, 0.1, -0.1]:
    H = field(aexp)
    B, thr = contours(H, P)
    save(B, f"scan_a{aexp:+.2f}.png")
    print(f"a={aexp:+.2f}  ink={B.mean():.4f}  thr={thr:.3f}")
