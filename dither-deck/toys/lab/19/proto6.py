# S19 TOPO prototype 6 — shield -> archipelago -> folded ranges (advected heightfield)
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 680; BASE = 512.0; P = 0.9; PCT = 13.0
A0, AMID = 1.60, 0.90     # exponent dips mid-journey, returns smooth
LMAX = 46.0               # peak advection in device px

def vnoise_field(sp, seed):
    n = int(np.ceil(G / sp)) + 3
    lat = np.random.RandomState(seed).rand(n, n)
    ys = np.arange(G) / sp; xs = np.arange(G) / sp
    iy = np.floor(ys).astype(int); ix = np.floor(xs).astype(int)
    fy = ys - iy; fx = xs - ix
    sy = fy*fy*(3-2*fy); sx = fx*fx*(3-2*fx)
    aa = lat[np.ix_(iy, ix)];   bb = lat[np.ix_(iy, ix+1)]
    cc = lat[np.ix_(iy+1, ix)]; dd = lat[np.ix_(iy+1, ix+1)]
    top = aa*(1-sx)[None,:] + bb*sx[None,:]
    bot = cc*(1-sx)[None,:] + dd*sx[None,:]
    v = top*(1-sy)[:,None] + bot*sy[:,None]
    return (v - v.mean()) / v.std()

OCTS = [vnoise_field(BASE / (2**i), 100 + i) for i in range(8)]
W1 = vnoise_field(170, 900) * 1.8   # smooth advection field, ~[-1.5,1.5]
W2 = vnoise_field(170, 901) * 1.8

def gather(V, Y, X):
    y = np.clip(Y, 0, G - 1.001); x = np.clip(X, 0, G - 1.001)
    iy = y.astype(int); ix = x.astype(int)
    fy = y - iy; fx = x - ix
    return (V[iy, ix]*(1-fx)*(1-fy) + V[iy, ix+1]*fx*(1-fy)
            + V[iy+1, ix]*(1-fx)*fy + V[iy+1, ix+1]*fx*fy)

YY, XX = np.mgrid[0:G, 0:G].astype(float)

def field(k):
    a = A0 + (AMID - A0) * np.sin(np.pi * min(k * 1.15, 1.0) )  # dips mid, ~back at end
    s = np.clip((k - 0.5) / 0.5, 0, 1)
    lam = LMAX * s * s * (3 - 2 * s)
    H = np.zeros((G, G)); wsum2 = 0.0
    if lam < 0.01:
        for i, v in enumerate(OCTS):
            w = (2.0**i)**(-a); wsum2 += w*w
            H += w * v
    else:
        Y = YY + lam * W1; X = XX + lam * W2
        for i, v in enumerate(OCTS):
            w = (2.0**i)**(-a); wsum2 += w*w
            H += w * gather(v, Y, X)
    H /= np.sqrt(wsum2)
    return (H - H.mean()) / H.std()

def contours(H):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0
    return F < np.percentile(F, PCT)

for k in [0.0, 0.25, 0.5, 0.75, 0.875, 1.0]:
    B = contours(field(k))
    Image.fromarray(np.where(B, 0, 255).astype(np.uint8)).save(
        os.path.join(OUT, f"fold_k{int(round(k*1000)):03d}.png"))
    print(f"k={k:.3f} ink={B.mean():.4f}")

prev = None; worst = 0.0; worstk = 0.0; tot = 0.0; inks = []
for i in range(201):
    k = i / 200
    B = contours(field(k)); inks.append(B.mean())
    if prev is not None:
        fl = np.mean(B != prev); tot += fl
        if fl > worst: worst, worstk = fl, k
    prev = B
print(f"worst flip = {worst*100:.2f}% at k={worstk:.3f}, mean = {tot/200*100:.2f}%, ink {min(inks):.4f}/{max(inks):.4f}")
