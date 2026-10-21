# time-journey refinement at F=0.037 k=0.060 — find snapshot times with
# genuinely distinct structures, and test whether long integration coarsens.
import numpy as np, os, time, base64, json
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
DU, DV = 0.21, 0.105
N = 340
F, K = 0.037, 0.060

def lap9(a):
    return (0.2*(np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))
          + 0.05*(np.roll(a,(1,1),(0,1))+np.roll(a,(1,-1),(0,1))
                 +np.roll(a,(-1,1),(0,1))+np.roll(a,(-1,-1),(0,1))) - a)

def thr45(v): return v >= np.percentile(v, 55.0)

def save(m, name):
    Image.fromarray(np.where(m,0,255).astype(np.uint8)).resize((680,680), Image.NEAREST).save(os.path.join(OUT,name))

SNAP_TIMES = [250, 600, 900, 1500, 2500, 4500, 7000]

rng = np.random.default_rng(7)
u = np.ones((N, N))
v = rng.random((N, N)) * 0.3 * (rng.random((N, N)) < 0.5)
u = 1.0 - 0.5 * (rng.random((N, N)) < 0.5) * rng.random((N, N))

snaps, tags = [], []
tprev = 0
t0 = time.time()
for ts in SNAP_TIMES:
    for _ in range(ts - tprev):
        uvv = u * v * v
        u += DU * lap9(u) - uvv + F * (1 - u)
        v += DV * lap9(v) + uvv - (F + K) * v
    tprev = ts
    m = thr45(v)
    snaps.append(m); tags.append(f"t{ts}")
    save(m, f"j_t{ts}.png")
    print(f"t={ts}: cov={m.mean():.4f} wall={time.time()-t0:.0f}s", flush=True)

S = np.array(snaps)
np.save(os.path.join(OUT, "journey_snaps.npy"), S)
print("\npairwise flip fractions:")
for i in range(len(S) - 1):
    print(f"  {tags[i]} -> {tags[i+1]}: {np.mean(S[i] != S[i+1]):.4f}")
