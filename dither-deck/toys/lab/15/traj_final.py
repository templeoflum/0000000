# FINAL trajectory for S15 MAZE — one continuous Gray-Scott integration.
# Phase 1 (time axis @ F=0.037,k=0.060, Pearson's labyrinthine regime):
#   static -> dots -> worms -> braid -> young maze -> hedge maze
# Phase 2 (adiabatic parameter sweep to F=0.062,k=0.061, Pearson's 'coral'):
#   hedge -> transition -> brickwork
# stops are thresholded at the 55th percentile of v  => ink = 0.45 exactly.
import numpy as np, os, time, base64, json
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

# (F_target, k_target, steps_to_run, snapshot_tag_or_None)
SEG = [
    (0.037, 0.060,   80, "s0_static"),
    (0.037, 0.060,  170, "s1_dots"),
    (0.037, 0.060,  250, "s2_worms"),
    (0.037, 0.060,  400, "s3_braid"),
    (0.037, 0.060,  600, "s4_young"),
    (0.037, 0.060, 1000, "s5_hedge"),
    (0.050, 0.062, 1500, "s6_shift"),
    (0.062, 0.061, 1500, "s7_brickwork"),
]

rng = np.random.default_rng(7)
u = np.ones((N, N))
v = rng.random((N, N)) * 0.3 * (rng.random((N, N)) < 0.5)
u = 1.0 - 0.5 * (rng.random((N, N)) < 0.5) * rng.random((N, N))

Fcur, Kcur = SEG[0][0], SEG[0][1]
snaps, tags = [], []
t0 = time.time()
for Ftar, Ktar, steps, tag in SEG:
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
    snaps.append(m); tags.append(tag)
    save(m, f"fin_{tag}.png")
    print(f"{tag}: cov={m.mean():.4f} t={time.time()-t0:.0f}s", flush=True)

S = np.array(snaps)
np.save(os.path.join(OUT, "final_snaps.npy"), S)
with open(os.path.join(OUT, "final_tags.json"), "w") as f: json.dump(tags, f)

print("\nink per stop:", [f"{s.mean():.4f}" for s in S])
print("pairwise flip fractions:")
for i in range(len(S) - 1):
    print(f"  {tags[i]} -> {tags[i+1]}: {np.mean(S[i] != S[i+1]):.4f}")

# bitpack MSB-first like S13 and base64 the concatenation-ready strings
def pack(m):
    flat = m.astype(np.uint8).ravel()
    pad = (-flat.size) % 8
    if pad: flat = np.concatenate([flat, np.zeros(pad, np.uint8)])
    b = np.packbits(flat)  # MSB first
    return base64.b64encode(b.tobytes()).decode()

packed = [pack(m) for m in S]
with open(os.path.join(OUT, "frames_b64.json"), "w") as f: json.dump(packed, f)
print("frames packed:", [len(p) for p in packed])
