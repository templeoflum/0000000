# BUILD final frames for S15 MAZE
# stops 1-4: one Gray-Scott integration at F=0.037,k=0.060 (Pearson labyrinthine),
#   time stops t = 250 (cow hide), 900 (spore rings), 1500 (flooded maze), 2500 (hedge maze)
# stop 5: fresh seed at F=0.062,k=0.061 (Pearson coral), t=4000 (brickwork)
# also: BN dissolve realism + full 200-step granularity measurement with the deck's
# own NEW blue-noise mask decoded from ../13.html
import numpy as np, os, time, base64, json, re
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

def seed_rng():
    rng = np.random.default_rng(7)
    u = np.ones((N, N))
    v = rng.random((N, N)) * 0.3 * (rng.random((N, N)) < 0.5)
    u = 1.0 - 0.5 * (rng.random((N, N)) < 0.5) * rng.random((N, N))
    return u, v

def steps(u, v, F, K, n):
    for _ in range(n):
        uvv = u * v * v
        u += DU * lap9(u) - uvv + F * (1 - u)
        v += DV * lap9(v) + uvv - (F + K) * v
    return u, v

t0 = time.time()
# stops 1-4
u, v = seed_rng()
times = [250, 900, 1500, 2500]
snaps, tags = [], []
tp = 0
for ts in times:
    u, v = steps(u, v, 0.037, 0.060, ts - tp); tp = ts
    m = thr45(v); snaps.append(m); tags.append(f"hedge_t{ts}")
    print(f"stop {tags[-1]} t={time.time()-t0:.0f}s", flush=True)
# stop 5: coral, fresh seed
u, v = seed_rng()
u, v = steps(u, v, 0.062, 0.061, 4000)
m = thr45(v); snaps.append(m); tags.append("coral_t4000")
print(f"stop coral_t4000 t={time.time()-t0:.0f}s", flush=True)

S = np.array(snaps)
for m, tg in zip(S, tags): save(m, f"final_{tg}.png")

print("\nink per stop:", [f"{s.mean():.4f}" for s in S])
print("pairwise flip fractions:")
for i in range(len(S) - 1):
    print(f"  {tags[i]} -> {tags[i+1]}: {np.mean(S[i] != S[i+1]):.4f}")

# decode the deck's BN mask from ../13.html
src = open(os.path.join(OUT, "..", "..", "13.html"), encoding="utf-8").read()
b64 = re.search(r'const BN=\(\(\)=>\{const b64="([^"]+)"', src).group(1)
raw = base64.b64decode(b64)
n = 128 * 128
BN = np.array([raw[2*i] | (raw[2*i+1] << 8) for i in range(n)], dtype=np.float64)
BN = (BN + 0.5) / n
BN = BN.reshape(128, 128)
BNt = np.tile(BN, (3, 3))[:N, :N]  # tile to 340x340 like the JS (wrap indexing)

# BN dissolve: on(A,B,f) = A==B ? A : (BN < f ? B : A)
def dissolve(A, B, f):
    diff = A != B
    takeB = diff & (BNt < f)
    return np.where(takeB, B, A)

# mid-dissolve eye-check at f=0.5 for each gap
for i in range(len(S) - 1):
    save(dissolve(S[i], S[i+1], 0.5), f"mid_{i}_{i+1}.png")

# full 200-step granularity measurement (5 stops over k in [0,1])
NS = len(S)
prev = None
worst, worst_k = 0.0, None
flips = []
for step in range(201):
    kk = step / 200.0
    p = kk * (NS - 1)
    D = min(int(np.floor(p)), NS - 2)
    f = max(p - D, 0.0)
    cur = dissolve(S[D], S[D+1], f)
    if prev is not None:
        fr = np.mean(cur != prev)
        flips.append(fr)
        if fr > worst: worst, worst_k = fr, kk
    prev = cur
print(f"\n200-step sweep: worst flip per 1/200 step = {worst:.4%} at k={worst_k}")
print(f"mean flip per step = {np.mean(flips):.4%}")

# pack frames MSB-first base64, save JSON for the HTML builder
def pack(m):
    flat = m.astype(np.uint8).ravel()
    pad = (-flat.size) % 8
    if pad: flat = np.concatenate([flat, np.zeros(pad, np.uint8)])
    return base64.b64encode(np.packbits(flat).tobytes()).decode()

packed = [pack(m) for m in S]
with open(os.path.join(OUT, "frames_b64.json"), "w") as fo: json.dump(packed, fo)
print("frames packed:", [len(p) for p in packed], "tags:", tags)
