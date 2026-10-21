"""Gray-Scott stripe-regime sweep. S13's integrator: Du=0.21, Dv=0.105,
9-point Laplacian (0.2 orth, 0.05 diag), dt=1, periodic edges.
Sweep (F,kill) points on a 224^2 lattice, render v thresholded at the
per-frame 55th percentile (ink=0.45) into a montage."""
import numpy as np
from PIL import Image
import time, os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 224
DU, DV = 0.21, 0.105

def lap9(z):
    return (0.2*(np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1))
           +0.05*(np.roll(np.roll(z,1,0),1,1)+np.roll(np.roll(z,1,0),-1,1)
                 +np.roll(np.roll(z,-1,0),1,1)+np.roll(np.roll(z,-1,0),-1,1))
           -z)

def run(F, kill, steps, seed=7):
    rng = np.random.default_rng(seed)
    u = np.ones((G,G)); v = np.zeros((G,G))
    # 8% static: random patches seeded with u~0.5, v~0.25
    for _ in range(int(0.08*G*G/64)):
        y = rng.integers(0, G-8); x = rng.integers(0, G-8)
        u[y:y+8, x:x+8] = 0.5 + 0.05*rng.standard_normal((8,8))
        v[y:y+8, x:x+8] = 0.25 + 0.05*rng.standard_normal((8,8))
    for _ in range(steps):
        uvv = u*v*v
        u += DU*lap9(u) - uvv + F*(1-u)
        v += DV*lap9(v) + uvv - (F+kill)*v
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
    return v

def to_bits(v, tone=0.45):
    thr = np.quantile(v, 1-tone)
    return (v < thr)  # ink = True

points = [(F,k) for F in (0.025,0.030,0.035,0.040,0.045)
               for k in (0.058,0.060,0.062,0.064)]
cells = []
for F,k in points:
    t0 = time.time()
    v = run(F, k, 3000)
    b = to_bits(v)
    print(f"F={F:.3f} kill={k:.3f}  ink={b.mean():.3f}  ({time.time()-t0:.1f}s)", flush=True)
    cells.append((f"F={F} k={k}", b))

cols = 4; rows = len(cells)//cols
M = np.zeros((rows*G, cols*G), dtype=np.uint8)
for idx,(name,b) in enumerate(cells):
    r, c = divmod(idx, cols)
    M[r*G:(r+1)*G, c*G:(c+1)*G] = np.where(b, 0, 255)
Image.fromarray(M).save(os.path.join(OUT, "sweep1.png"))
print("saved sweep1.png")
