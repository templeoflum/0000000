# adiabatic parameter-path trajectory through Pearson's labyrinth region
# one continuous honest integration; (F,k) drift slowly along a path:
#   coral(0.062,0.061) -> mid(0.046,0.063) -> hedge(0.037,0.060) -> archipelago(0.029,0.057)
# snapshots along the way become the toy's stops.
import numpy as np
from PIL import Image
import os, time

OUT = os.path.dirname(os.path.abspath(__file__))
DU, DV = 0.21, 0.105
N = 340  # native render lattice (2px grains on 680)

def lap9(a):
    return (0.2*(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))
          + 0.05*(np.roll(a,(1,1),(0,1))+np.roll(a,(1,-1),(0,1))
                 +np.roll(a,(-1,1),(0,1))+np.roll(a,(-1,-1),(0,1))) - a)

def thr45(v):
    t = np.percentile(v, 55.0)
    return v >= t

def save(m, name):
    im = Image.fromarray(np.where(m, 0, 255).astype(np.uint8))
    im = im.resize((680, 680), Image.NEAREST)
    im.save(os.path.join(OUT, name))

# waypoints: (F, k, steps_at_or_sweeping_to_this_point, tag)
PATH = [
    (0.062, 0.061, 2500, "wp0_coral"),
    (0.052, 0.0625, 2000, "wp1_coral2"),
    (0.046, 0.063, 2000, "wp2_mid"),
    (0.041, 0.061, 2000, "wp3_midlab"),
    (0.037, 0.060, 2500, "wp4_hedge"),
    (0.032, 0.058, 2500, "wp5_thin"),
    (0.029, 0.057, 3000, "wp6_archipelago"),
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
    snaps.append(m.copy())
    save(m, f"traj_{tag}_F{Ftar}_k{Ktar}.png")
    print(f"{tag}: cov={m.mean():.3f} vmax={v.max():.3f} vmin={v.min():.3f} t={time.time()-t0:.0f}s", flush=True)

np.save(os.path.join(OUT, "traj_snaps.npy"), np.array(snaps))
# pairwise flip fractions between consecutive stops
print("\npairwise flip fractions between consecutive stops:")
for i in range(len(snaps) - 1):
    d = np.mean(snaps[i] != snaps[i + 1])
    print(f"  {i}->{i+1}: {d:.4f}")
