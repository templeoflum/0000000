# S23 SHIMMER — prototype v2: beats(stronger) / zone / ripple / chevron / checker
import numpy as np
from PIL import Image
import os

S = 340
OUT = os.path.dirname(os.path.abspath(__file__))
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
cx = cy = S / 2
TAU = 2 * np.pi

def norm(f):
    lo, hi = f.min(), f.max()
    return (f - lo) / (hi - lo + 1e-12)

# A: BEATS — symmetric detune ±th/2, carrier vertical, envelope horizontal bands
lam = 13.0
th = np.deg2rad(7.0)
k0 = TAU / lam
A = (np.cos(k0 * (x * np.cos(th / 2) + y * np.sin(th / 2)))
     + np.cos(k0 * (x * np.cos(th / 2) - y * np.sin(th / 2))))
A = norm(A)

# B: ZONE PLATE
r2 = (x - cx) ** 2 + (y - cy) ** 2
rho = 40.0
B = 0.5 + 0.5 * np.cos(np.pi * r2 / rho ** 2)
B = norm(B)

# C: RIPPLE TANK — near sources inside field
d = 65.0
r1 = np.sqrt((x - (cx - d)) ** 2 + (y - cy) ** 2)
r2s = np.sqrt((x - (cx + d)) ** 2 + (y - cy) ** 2)
lamC = 11.0
C = np.cos(TAU * r1 / lamC) + np.cos(TAU * r2s / lamC)
C = norm(C)

# D: CHEVRON — two far sources above the field, nested V fringes (herringbone)
sy = cy - 460.0
sd = 70.0
r1 = np.sqrt((x - (cx - sd)) ** 2 + (y - sy) ** 2)
r2s = np.sqrt((x - (cx + sd)) ** 2 + (y - sy) ** 2)
lamD = 13.0
D = np.cos(TAU * r1 / lamD) + np.cos(TAU * r2s / lamD)
D = norm(D)

# E: CHECKER MOIRE — two square lattices rotated 8 deg
lamE = 13.0
ke = TAU / lamE
al = np.deg2rad(8.0)
xa = (x - cx) * np.cos(al) + (y - cy) * np.sin(al)
ya = -(x - cx) * np.sin(al) + (y - cy) * np.cos(al)
E = np.cos(ke * x) + np.cos(ke * y) + np.cos(ke * xa) + np.cos(ke * ya)
E = norm(E)

L = [A, B, C, D, E]

def threshold(F, frac=0.45):
    thr = np.quantile(F, frac)
    return (F < thr), thr

def blend(k):
    p = k * (len(L) - 1)
    i = min(int(np.floor(p)), len(L) - 2)
    t = p - i
    return L[i] * (1 - t) + L[i + 1] * t

for k in [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]:
    F = blend(k)
    B_, thr = threshold(F)
    Image.fromarray((1 - B_.astype(np.uint8)) * 255).save(
        os.path.join(OUT, f"v2_{k:.3f}.png"))
    print(f"k={k:.3f} ink={B_.mean():.4f}")

prev = None
worst = 0.0
for i in range(201):
    F = blend(i / 200)
    B_, _ = threshold(F)
    if prev is not None:
        worst = max(worst, np.mean(B_ != prev))
    prev = B_
print(f"worst flip per 1/200 step: {worst*100:.2f}%")
