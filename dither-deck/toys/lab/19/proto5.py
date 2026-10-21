# S19 TOPO prototype 5 — relief shading: exponent sweep + ridge-mix tent (no rephase)
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 680
BASE = 512.0
A0, A1 = 1.60, 0.45
P = 0.9
PCT = 13.0

OCTS = []
for i in range(8):
    sp = BASE / (2 ** i)
    n = int(np.ceil(G / sp)) + 2
    lat = np.random.RandomState(100 + i).rand(n, n)
    ys = np.arange(G) / sp; xs = np.arange(G) / sp
    iy = np.floor(ys).astype(int); ix = np.floor(xs).astype(int)
    fy = ys - iy; fx = xs - ix
    sy = fy*fy*(3-2*fy); sx = fx*fx*(3-2*fx)
    aa = lat[np.ix_(iy, ix)];   bb = lat[np.ix_(iy, ix+1)]
    cc = lat[np.ix_(iy+1, ix)]; dd = lat[np.ix_(iy+1, ix+1)]
    top = aa*(1-sx)[None,:] + bb*sx[None,:]
    bot = cc*(1-sx)[None,:] + dd*sx[None,:]
    v = top*(1-sy)[:,None] + bot*sy[:,None]
    v = (v - v.mean()) / v.std()
    OCTS.append(v)

def field(k):
    a = A0 + (A1 - A0) * k
    rho = 1.0 - abs(2 * k - 1.0)          # relief-shading tent
    H = np.zeros((G, G)); wsum2 = 0.0
    for i, v in enumerate(OCTS):
        w = (2.0 ** i) ** (-a)
        wsum2 += w * w
        H += w * ((1 - rho) * v - rho * np.abs(v))
    H /= np.sqrt(wsum2)
    return (H - H.mean()) / H.std()

def contours(H):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0
    thr = np.percentile(F, PCT)
    return F < thr

def save(B, name):
    Image.fromarray(np.where(B, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))

for k in [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]:
    B = contours(field(k))
    save(B, f"relief_k{int(round(k*1000)):03d}.png")
    print(f"k={k:.3f} ink={B.mean():.4f}")

prev = None; worst = 0.0; worstk = 0.0; tot = 0.0; inks = []
for i in range(201):
    k = i / 200
    B = contours(field(k))
    inks.append(B.mean())
    if prev is not None:
        fl = np.mean(B != prev); tot += fl
        if fl > worst: worst, worstk = fl, k
    prev = B
print(f"worst flip = {worst*100:.2f}% at k={worstk:.3f}, mean = {tot/200*100:.2f}%, "
      f"ink {min(inks):.4f}/{max(inks):.4f}")
