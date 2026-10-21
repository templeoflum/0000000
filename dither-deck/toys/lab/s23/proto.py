# S23 SHIMMER — offline prototype
# five waypoint interference landscapes, linear blend, per-frame 45th-percentile threshold.
import numpy as np
from PIL import Image
import os

S = 340  # proto grid (final = 680)
OUT = os.path.dirname(os.path.abspath(__file__))

y, x = np.mgrid[0:S, 0:S].astype(np.float64)
cx = cy = S / 2
TAU = 2 * np.pi

def norm(f):  # map to [0,1]
    lo, hi = f.min(), f.max()
    return (f - lo) / (hi - lo + 1e-12)

# A: BEATS — two plane waves detuned 3 deg, lambda=12 (proto scale)
lam = 12.0
th = np.deg2rad(2.5)
k0 = TAU / lam
A = np.cos(k0 * x) + np.cos(k0 * (x * np.cos(th) + y * np.sin(th)))
A = norm(A)

# B: ZONE PLATE — fresnel chirp cos(pi r^2 / rho^2), rho=40 proto (=> 9 cycles at edge)
r2 = (x - cx) ** 2 + (y - cy) ** 2
rho = 40.0
B = 0.5 + 0.5 * np.cos(np.pi * r2 / rho ** 2)
B = norm(B)

# C: RIPPLE TANK — two point sources, hyperbolic fringes
d = 65.0
r1 = np.sqrt((x - (cx - d)) ** 2 + (y - cy) ** 2)
r2s = np.sqrt((x - (cx + d)) ** 2 + (y - cy) ** 2)
lamC = 11.0
C = np.cos(TAU * r1 / lamC) + np.cos(TAU * r2s / lamC)
C = norm(C)

# D: HEX LATTICE — three plane waves 120 deg apart
lamD = 13.0
kk = TAU / lamD
D = (np.cos(kk * x)
     + np.cos(kk * (x * np.cos(2 * np.pi / 3) + y * np.sin(2 * np.pi / 3)))
     + np.cos(kk * (x * np.cos(4 * np.pi / 3) + y * np.sin(4 * np.pi / 3))))
D = norm(D)

# E: CHECKER MOIRE — two square lattices (4 waves), one rotated 8 deg
lamE = 13.0
ke = TAU / lamE
al = np.deg2rad(8.0)
xa = x * np.cos(al) + y * np.sin(al)
ya = -x * np.sin(al) + y * np.cos(al)
E = np.cos(ke * x) + np.cos(ke * y) + np.cos(ke * xa) + np.cos(ke * ya)
E = norm(E)

L = [A, B, C, D, E]
names = ["beats", "zoneplate", "ripple", "hex", "checker"]

def threshold(F, frac=0.45):
    thr = np.quantile(F, frac)
    return (F < thr), thr

def blend(k):
    p = k * (len(L) - 1)
    i = min(int(np.floor(p)), len(L) - 2)
    t = p - i
    return L[i] * (1 - t) + L[i + 1] * t

# render states
for k in [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]:
    F = blend(k)
    B_, thr = threshold(F)
    img = Image.fromarray((1 - B_.astype(np.uint8)) * 255)
    img.save(os.path.join(OUT, f"state_{k:.3f}.png"))
    print(f"k={k:.3f} ink={B_.mean():.4f} thr={thr:.3f}")

# granularity: 200-step sweep
prev = None
worst = 0.0
for i in range(201):
    F = blend(i / 200)
    B_, _ = threshold(F)
    if prev is not None:
        fl = np.mean(B_ != prev)
        worst = max(worst, fl)
    prev = B_
print(f"worst flip per 1/200 step: {worst*100:.2f}%")
