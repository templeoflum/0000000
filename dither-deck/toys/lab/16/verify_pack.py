# S16 — verify laws + bitpack frames for embedding
import numpy as np, base64, json

n = 340
F = np.load("fields.npz")
order = ["targets","ripple","pinwheel","carousel","fiddleheads","worms"]
frames = []
for name in order:
    u = F[name]
    land = 1.0 - np.clip(u, 0, 1)
    thr = np.quantile(land, 0.45)
    on = (land < thr).astype(np.uint8)   # 1 = black ink
    frames.append(on)
    print(name, "ink:", on.mean())

BN = np.load("bn_new.npy")  # 128x128 order in [0,1]
BNN = 128
bntile = np.tile(BN.reshape(BNN,BNN), (int(np.ceil(n/BNN)),)*2)[:n,:n]

NS = len(frames)
worst = 0.0; worst_at = None
prev = None
for step in range(201):
    k = step/200.0
    p = k*(NS-1)
    D = min(int(np.floor(p)), NS-2)
    f = max(0.0, p-D)
    A, B = frames[D], frames[D+1]
    img = np.where(A==B, A, np.where(bntile < f, B, A))
    if prev is not None:
        flips = (img != prev).mean()
        if flips > worst: worst, worst_at = flips, step
    prev = img
print("worst flip fraction per 1/200 step:", worst, "at step", worst_at)
print("adjacent stop diffs:", [float((frames[i]!=frames[i+1]).mean()) for i in range(NS-1)])

# bitpack MSB-first like S13, base64
out = []
for on in frames:
    bits = on.flatten()
    by = np.zeros(n*n//8, dtype=np.uint8)
    for b in range(8):
        by |= (bits[b::8] << (7-b)).astype(np.uint8)
    out.append(base64.b64encode(by.tobytes()).decode())
json.dump(out, open("frames.json","w"))
print("packed", NS, "frames, each b64 len", len(out[0]))
