# stage A: coral -> midlab, checkpoint u,v
import numpy as np, os, time
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
DU, DV = 0.21, 0.105
N = 340

def lap9(a):
    return (0.2*(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))
          + 0.05*(np.roll(a,(1,1),(0,1))+np.roll(a,(1,-1),(0,1))
                 +np.roll(a,(-1,1),(0,1))+np.roll(a,(-1,-1),(0,1))) - a)

def thr45(v): return v >= np.percentile(v, 55.0)

def save(m, name):
    Image.fromarray(np.where(m,0,255).astype(np.uint8)).resize((680,680), Image.NEAREST).save(os.path.join(OUT,name))

PATH = [
    (0.062, 0.061, 2200, "wp0_coral"),
    (0.052, 0.0625, 1500, "wp1_coral2"),
    (0.046, 0.063, 1500, "wp2_mid"),
    (0.041, 0.061, 1500, "wp3_midlab"),
]

rng = np.random.default_rng(7)
u = np.ones((N, N))
v = rng.random((N, N)) * 0.3 * (rng.random((N, N)) < 0.5)
u = 1.0 - 0.5 * (rng.random((N, N)) < 0.5) * rng.random((N, N))

Fcur, Kcur = PATH[0][0], PATH[0][1]
snaps = []
t0 = time.time()
for Ftar, Ktar, steps, tag in PATH:
    F0, K0 = Fcur, Kcur
    for s in range(steps):
        a = (s + 1) / steps
        F = F0 + (Ftar - F0) * a
        K = K0 + (Ktar - K0) * a
        uvv = u * v * v
        u += DU * lap9(u) - uvv + F * (1 - u)
        v += DV * lap9(v) + uvv - (F + K) * v
    Fcur, Kcur = Ftar, Ktar
    m = thr45(v)
    snaps.append(m)
    save(m, f"t2_{tag}.png")
    print(f"{tag} t={time.time()-t0:.0f}s", flush=True)

np.savez(os.path.join(OUT, "ckpt.npz"), u=u, v=v, snaps=np.array(snaps))
print("checkpoint saved")
