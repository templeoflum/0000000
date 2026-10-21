# Gray-Scott labyrinth regime sweep — offline prototype for S15 MAZE
# equations: du = Du*lap(u) - u*v^2 + F*(1-u)
#            dv = Dv*lap(v) + u*v^2 - (F+k)*v
# 9-point laplacian (0.2 orth, 0.05 diag), dt=1, periodic, Du=0.21 Dv=0.105 (deck's S13 values)
import numpy as np
from PIL import Image
import os, time

OUT = os.path.dirname(os.path.abspath(__file__))
DU, DV = 0.21, 0.105
N = 256  # lattice

def lap9(a):
    return (0.2*(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))
          + 0.05*(np.roll(a,(1,1),(0,1))+np.roll(a,(1,-1),(0,1))
                 +np.roll(a,(-1,1),(0,1))+np.roll(a,(-1,-1),(0,1))) - a)

def run(F, K, steps, seed=7, u=None, v=None):
    rng = np.random.default_rng(seed)
    if u is None:
        u = np.ones((N, N))
        v = np.zeros((N, N))
        # 8% static seed like S13
        v = rng.random((N, N)) * 0.3 * (rng.random((N, N)) < 0.5)
        u = 1.0 - 0.5 * (rng.random((N, N)) < 0.5) * rng.random((N, N))
    for _ in range(steps):
        uvv = u * v * v
        u += DU * lap9(u) - uvv + F * (1 - u)
        v += DV * lap9(v) + uvv - (F + K) * v
    return u, v

def thr45(v):
    t = np.percentile(v, 55)  # ink (black) = v above threshold, 45% black
    return (v >= t)

def save(img_bool, name):
    im = Image.fromarray((np.where(img_bool, 0, 255)).astype(np.uint8))
    im = im.resize((680, 680), Image.NEAREST)
    im.save(os.path.join(OUT, name))

if __name__ == "__main__":
    regimes = [
        (0.029, 0.057, "lab_a"),
        (0.037, 0.060, "lab_b"),
        (0.062, 0.061, "coral"),
        (0.026, 0.051, "chaos_edge"),
        (0.030, 0.055, "low_f"),
        (0.046, 0.063, "mid"),
    ]
    for F, K, tag in regimes:
        t0 = time.time()
        u, v = run(F, K, 4000)
        m = thr45(v)
        save(m, f"sweep_{tag}_F{F}_k{K}.png")
        # also save raw v normalized for inspection
        vn = ((v - v.min()) / (np.ptp(v) + 1e-9) * 255).astype(np.uint8)
        Image.fromarray(vn).resize((680, 680), Image.NEAREST).save(os.path.join(OUT, f"sweep_{tag}_raw.png"))
        print(f"{tag} F={F} k={K}  cov={m.mean():.3f}  vrange=({v.min():.3f},{v.max():.3f})  {time.time()-t0:.1f}s")
