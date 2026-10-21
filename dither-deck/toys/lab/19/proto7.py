# S19 TOPO prototype 7 — FINAL hybrid: continent -> archipelago -> badlands -> chevron folds
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 680; BASE = 512.0; P = 0.9; PCT = 13.0
RMAX = 0.85; LMAX = 46.0

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
ABS = [np.abs(v) for v in OCTS]
W1 = vnoise_field(170, 900) * 1.8
W2 = vnoise_field(170, 901) * 1.8
YY, XX = np.mgrid[0:G, 0:G].astype(float)

def sstep(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)

def gather(V, Y, X):
    y = np.clip(Y, 0, G - 1.001); x = np.clip(X, 0, G - 1.001)
    iy = y.astype(int); ix = x.astype(int)
    fy = y - iy; fx = x - ix
    return (V[iy, ix]*(1-fx)*(1-fy) + V[iy, ix+1]*fx*(1-fy)
            + V[iy+1, ix]*(1-fx)*fy + V[iy+1, ix+1]*fx*fy)

def params(k):
    a = 1.60 - 1.05 * np.sin(np.pi * k / 1.3)
    rho = RMAX * sstep((k - 0.30) / 0.40)
    lam = LMAX * sstep((k - 0.55) / 0.45)
    return a, rho, lam

def field(k):
    a, rho, lam = params(k)
    H = np.zeros((G, G)); wsum2 = 0.0
    if lam < 0.01:
        for i in range(8):
            w = (2.0**i)**(-a); wsum2 += w*w
            H += w * ((1-rho) * OCTS[i] - rho * ABS[i])
    else:
        Y = YY + lam * W1; X = XX + lam * W2
        for i in range(8):
            w = (2.0**i)**(-a); wsum2 += w*w
            H += w * ((1-rho) * gather(OCTS[i], Y, X) - rho * gather(ABS[i], Y, X))
    H /= np.sqrt(wsum2)
    return (H - H.mean()) / H.std()

def contours(H):
    u = (H / P) % 1.0
    F = np.abs(u - 0.5) * 2.0
    return F < np.percentile(F, PCT)

for k in [0.0, 0.2, 0.4, 0.55, 0.7, 0.85, 1.0]:
    B = contours(field(k))
    Image.fromarray(np.where(B, 0, 255).astype(np.uint8)).save(
        os.path.join(OUT, f"hyb_k{int(round(k*100)):03d}.png"))
    a, rho, lam = params(k)
    print(f"k={k:.2f} a={a:.2f} rho={rho:.2f} lam={lam:.1f} ink={B.mean():.4f}")

prev = None; worst = 0.0; worstk = 0.0; tot = 0.0; inks = []
for i in range(201):
    k = i / 200
    B = contours(field(k)); inks.append(B.mean())
    if prev is not None:
        fl = np.mean(B != prev); tot += fl
        if fl > worst: worst, worstk = fl, k
    prev = B
print(f"worst flip = {worst*100:.2f}% at k={worstk:.3f}, mean = {tot/200*100:.2f}%, ink {min(inks):.4f}/{max(inks):.4f}")
