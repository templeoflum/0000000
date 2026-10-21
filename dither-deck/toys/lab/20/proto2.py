import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 340
S0 = 17.0                      # hex lattice spacing px
NC = int(np.ceil(G / S0)) + 1  # cols
NR = int(np.ceil(G / (S0 * 0.8660254))) + 1  # rows

def hash2(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1442695040) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) & 0xFFFFFFFF
    h = (h * 1274126177) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return h / 4294967296.0

# hex lattice base + fixed hash jitter direction; amplitude is a k-schedule
bx = np.zeros((NR, NC)); by = np.zeros((NR, NC))
ux = np.zeros((NR, NC)); uy = np.zeros((NR, NC))
for j in range(NR):
    for i in range(NC):
        bx[j, i] = (i + 0.5 + 0.5 * (j % 2)) * S0
        by[j, i] = (j + 0.5) * S0 * 0.8660254
        ux[j, i] = (hash2(i, j, 7) - 0.5) * 2
        uy[j, i] = (hash2(i, j, 13) - 0.5) * 2

yy, xx = np.mgrid[0:G, 0:G].astype(np.float64)
px = xx + 0.5; py = yy + 0.5

def worley(m, amp):
    p1 = np.full((G, G), 1e18); p2 = np.full((G, G), 1e18)
    sxp = bx + amp * S0 * ux; syp = by + amp * S0 * uy
    # nearest lattice indices (approx; then scan 3x3 index block)
    rj = np.clip(np.round(py / (S0 * 0.8660254) - 0.5).astype(int), 0, NR - 1)
    ri = np.clip(np.round(px / S0 - 0.5 - 0.5 * (rj % 2)).astype(int), 0, NC - 1)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            jj = np.clip(rj + dj, 0, NR - 1)
            ii = np.clip(ri + di, 0, NC - 1)
            dx = np.abs(px - sxp[jj, ii]); dy = np.abs(py - syp[jj, ii])
            p = dx ** m + dy ** m
            mask = p < p1
            p2 = np.where(mask, p1, np.minimum(p2, p))
            p1 = np.where(mask, p, p1)
    return p1 ** (1.0 / m), p2 ** (1.0 / m)

AMP = 0.36
F = {}
for m in (1.0, 1.25, 1.5, 2.0, 3.0, 5.0, 8.0, 16.0):
    F[m] = worley(m, AMP)
# zero-jitter endpoints for the honeycomb segment
ZH = {}
for m in (2.0, 3.0, 5.0, 8.0, 16.0):
    ZH[m] = worley(m, 0.0)

def med(a): return np.median(a)

def rank01(a):
    r = a.ravel().argsort().argsort().astype(np.float64)
    return (r / (r.size - 1)).reshape(a.shape)

F1N = F[16.0][0]; W16 = F[16.0][1] - F[16.0][0]
RA = rank01(F1N); RB = rank01(W16)
WNORM = med(W16)

def blend_stops(stops, m, feat, table):
    stops = sorted(stops)
    if m <= stops[0]: a = b = stops[0]; t = 0
    elif m >= stops[-1]: a = b = stops[-1]; t = 0
    else:
        for i in range(len(stops) - 1):
            if stops[i] <= m <= stops[i + 1]:
                a, b = stops[i], stops[i + 1]; t = (m - a) / (b - a); break
    def field(mm):
        f1, f2 = table[mm]
        return f1 if feat == 0 else (f2 - f1)
    if a == b: return field(a)
    return field(a) * (1 - t) + field(b) * t

def mlerp(m0, m1, t):
    return np.exp(np.log(m0) * (1 - t) + np.log(m1) * t)

def landscape(k):
    if k < 0.20:
        m = mlerp(2.0, 1.0, k / 0.20)
        f1 = blend_stops([2.0, 1.5, 1.25, 1.0], m, 0, F)
        return f1 / med(F[2.0][0])
    elif k < 0.40:
        m = mlerp(1.0, 16.0, (k - 0.20) / 0.20)
        f1 = blend_stops([1.0, 1.25, 1.5, 2.0, 3.0, 5.0, 8.0, 16.0], m, 0, F)
        return f1 / med(F[2.0][0])
    elif k < 0.90:
        t = (k - 0.40) / 0.50
        return RA * (1 - t) + RB * t
    else:
        t = (k - 0.90) / 0.10
        m = mlerp(16.0, 2.0, t)
        # sites travel jittered -> hex while the metric rounds: interpolate fields
        stops = [16.0, 8.0, 5.0, 3.0, 2.0]
        wj = blend_stops(stops, m, 2, F)      # jittered sites
        wh = blend_stops(stops, m, 2, ZH)     # hex sites
        return (wj * (1 - t) + wh * t) / WNORM

def render(k):
    g = landscape(k)
    thr = np.percentile(g, 45)
    img = (g < thr)
    return img, img.mean()

for k in [0.0, 0.10, 0.20, 0.30, 0.40, 0.65, 0.90, 0.925, 0.95, 0.975, 1.0]:
    img, cov = render(k)
    Image.fromarray((~img * 255).astype(np.uint8)).save(
        os.path.join(OUT, f"h{k:.3f}.png"))
    print(f"k={k:.3f}  ink={cov:.4f}")

prev = None; worst = 0; tot = 0; worstk = 0
for s in range(201):
    k = s / 200
    img, _ = render(k)
    if prev is not None:
        fr = np.mean(img != prev)
        tot += fr
        if fr > worst: worst = fr; worstk = k
    prev = img
print(f"worst flip/step = {worst*100:.2f}% at k={worstk:.3f}, mean = {tot/200*100:.2f}%")
