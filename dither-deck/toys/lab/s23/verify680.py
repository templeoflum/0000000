# S23 SHIMMER — final 680x680 verification + renders (exact JS-intended math)
import numpy as np
from PIL import Image
import os, time

S = 680
OUT = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
cx = cy = S / 2
TAU = 2 * np.pi

def norm(f):
    lo, hi = f.min(), f.max()
    return (f - lo) / (hi - lo + 1e-12)

lam = 26.0
th = np.deg2rad(7.0)
k0 = TAU / lam
A = norm(np.cos(k0 * (x * np.cos(th / 2) + y * np.sin(th / 2)))
         + np.cos(k0 * (x * np.cos(th / 2) - y * np.sin(th / 2))))

r2 = (x - cx) ** 2 + (y - cy) ** 2
rho = 80.0
B = norm(0.5 + 0.5 * np.cos(np.pi * r2 / rho ** 2))

d = 130.0
r1 = np.sqrt((x - (cx - d)) ** 2 + (y - cy) ** 2)
r2s = np.sqrt((x - (cx + d)) ** 2 + (y - cy) ** 2)
lamC = 22.0
C = norm(np.cos(TAU * r1 / lamC) + np.cos(TAU * r2s / lamC))

sy = cy - 920.0
sd = 140.0
r1 = np.sqrt((x - (cx - sd)) ** 2 + (y - sy) ** 2)
r2s = np.sqrt((x - (cx + sd)) ** 2 + (y - sy) ** 2)
lamD = 26.0
D = norm(np.cos(TAU * r1 / lamD) + np.cos(TAU * r2s / lamD))

lamE = 26.0
ke = TAU / lamE
al = np.deg2rad(8.0)
xa = (x - cx) * np.cos(al) + (y - cy) * np.sin(al)
ya = -(x - cx) * np.sin(al) + (y - cy) * np.cos(al)
E = norm(np.cos(ke * x) + np.cos(ke * y) + np.cos(ke * xa) + np.cos(ke * ya))

L = [A, B, C, D, E]
print(f"precompute: {time.time()-t0:.1f}s")

def blend(k):
    p = k * 4
    i = min(int(p), 3)
    t = p - i
    return L[i] * (1 - t) + L[i + 1] * t

def threshold(F, frac=0.45):
    return F < np.quantile(F, frac)

for k in [0.0, 0.25, 0.5, 0.75, 1.0, 0.125, 0.375, 0.625, 0.875]:
    B_ = threshold(blend(k))
    Image.fromarray((1 - B_.astype(np.uint8)) * 255).save(
        os.path.join(OUT, f"f680_{k:.3f}.png"))
    print(f"k={k:.3f} ink={B_.mean():.4f}")

# 200-step granularity
prev = None
worst = 0.0
wi = -1
for i in range(201):
    B_ = threshold(blend(i / 200))
    if prev is not None:
        fl = np.mean(B_ != prev)
        if fl > worst: worst, wi = fl, i
    prev = B_
print(f"worst flip per 1/200 step: {worst*100:.2f}% at step {wi}")
