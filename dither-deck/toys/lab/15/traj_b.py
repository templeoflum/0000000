# stage B: resume from checkpoint, hedge -> archipelago
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
    (0.037, 0.060, 2200, "wp4_hedge"),
    (0.032, 0.058, 2000, "wp5_thin"),
    (0.029, 0.057, 2500, "wp6_archipelago"),
]

d = np.load(os.path.join(OUT, "ckpt.npz"))
u, v = d["u"].copy(), d["v"].copy()
snaps = list(d["snaps"])

Fcur, Kcur = 0.041, 0.061
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

S = np.array(snaps)
np.save(os.path.join(OUT, "traj_snaps.npy"), S)
print("\npairwise flip fractions between consecutive stops:")
for i in range(len(S) - 1):
    print(f"  {i}->{i+1}: {np.mean(S[i] != S[i+1]):.4f}")
