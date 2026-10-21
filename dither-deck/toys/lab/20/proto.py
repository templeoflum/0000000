import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 340
C = 17.0          # cell size px -> 20 cells across
NC = int(G / C)   # 20

def hash2(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1442695040) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) & 0xFFFFFFFF
    h = (h * 1274126177) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return h / 4294967296.0

# sites: one jittered per lattice cell, deterministic
sx = np.zeros((NC, NC)); sy = np.zeros((NC, NC))
for j in range(NC):
    for i in range(NC):
        sx[j, i] = (i + 0.5 + 0.42 * (hash2(i, j, 7) - 0.5) * 2) * C
        sy[j, i] = (j + 0.5 + 0.42 * (hash2(i, j, 13) - 0.5) * 2) * C

yy, xx = np.mgrid[0:G, 0:G].astype(np.float64)
px = xx + 0.5; py = yy + 0.5
ci = np.floor(px / C).astype(int); cj = np.floor(py / C).astype(int)

def worley(m):
    """F1,F2 with Minkowski metric of order m (m>=16 ~ Linf)."""
    p1 = np.full((G, G), 1e18); p2 = np.full((G, G), 1e18)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            ii = np.clip(ci + di, 0, NC - 1)
            jj = np.clip(cj + dj, 0, NC - 1)
            dx = np.abs(px - sx[jj, ii]); dy = np.abs(py - sy[jj, ii])
            p = dx ** m + dy ** m
            # insert into two smallest
            mask = p < p1
            p2 = np.where(mask, p1, np.minimum(p2, p))
            p1 = np.where(mask, p, p1)
    F1 = p1 ** (1.0 / m); F2 = p2 ** (1.0 / m)
    return F1, F2

# precompute fields at the needed metric stops
F = {}
for m in (1.0, 1.25, 1.5, 2.0, 3.0, 5.0, 8.0, 16.0):
    F[m] = worley(m)

def med(a): return np.median(a)

def rank01(a):
    """empirical-CDF transform -> uniform[0,1]; crossfading two rank fields
       keeps the 45th-percentile cut sweeping at a bounded, even rate."""
    r = a.ravel().argsort().argsort().astype(np.float64)
    return (r / (r.size - 1)).reshape(a.shape)

def landscape(k):
    """one continuous landscape function of k"""
    def mlerp(m0, m1, t):
        # interpolate in log-m for smoother metric travel
        return np.exp(np.log(m0) * (1 - t) + np.log(m1) * t)
    if k < 0.20:
        t = k / 0.20
        m = mlerp(2.0, 1.0, t)
        stops = [2.0, 1.5, 1.25, 1.0]
        f1 = blend_stops(stops, m, feat=0)
        return f1 / med(F[2.0][0])
    elif k < 0.40:
        t = (k - 0.20) / 0.20
        m = mlerp(1.0, 16.0, t)
        stops = [1.0, 1.25, 1.5, 2.0, 3.0, 5.0, 8.0, 16.0]
        f1 = blend_stops(stops, m, feat=0)
        return f1 / med(F[2.0][0])
    elif k < 0.90:
        t = (k - 0.40) / 0.50
        f1, f2 = F[16.0]
        w = f2 - f1
        a = rank01(f1); b = rank01(w)
        return a * (1 - t) + b * t
    else:
        t = (k - 0.90) / 0.10
        m = mlerp(16.0, 2.0, t)
        stops = [16.0, 8.0, 5.0, 3.0, 2.0]
        w = blend_stops(stops, m, feat=2)
        return w / med(F[16.0][0] * 0 + (F[16.0][1] - F[16.0][0]))

def blend_stops(stops, m, feat):
    """feat 0=F1, 2=F2-F1; linear interp between bracketing stops"""
    stops = sorted(stops)
    if m <= stops[0]: a = b = stops[0]; t = 0
    elif m >= stops[-1]: a = b = stops[-1]; t = 0
    else:
        for i in range(len(stops) - 1):
            if stops[i] <= m <= stops[i + 1]:
                a, b = stops[i], stops[i + 1]
                t = (m - a) / (b - a); break
    def field(mm):
        f1, f2 = F[mm]
        return f1 if feat == 0 else (f2 - f1)
    if a == b: return field(a)
    return field(a) * (1 - t) + field(b) * t

def render(k):
    g = landscape(k)
    thr = np.percentile(g, 45)
    img = (g < thr)
    cov = img.mean()
    return img, cov

states = {}
for k in [0.0, 0.10, 0.20, 0.30, 0.40, 0.65, 0.90, 0.95, 1.0]:
    img, cov = render(k)
    states[k] = img
    Image.fromarray((~img * 255).astype(np.uint8)).save(
        os.path.join(OUT, f"k{k:.3f}.png"))
    print(f"k={k:.3f}  ink={cov:.4f}")

# granularity: 200-step sweep, flip fraction per step
prev = None; worst = 0; tot = 0
for s in range(201):
    k = s / 200
    img, _ = render(k)
    if prev is not None:
        fr = np.mean(img != prev)
        tot += fr
        if fr > worst: worst = fr; worstk = k
    prev = img
print(f"worst flip/step = {worst*100:.2f}% at k={worstk:.3f}, mean = {tot/200*100:.2f}%")
