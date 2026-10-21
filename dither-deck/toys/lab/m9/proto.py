# M9 prototype: bond of studies 10 and 11 — the AM/FM axis.
# one ruling (64px cells), one tone (0.45). the bond axis is the ORDER in
# which a cell's grains are claimed as ink: rank field morphs from
# radial-from-centre (11's press dot) to Bayer's recursive nest ranks
# (10's ordered screen). threshold at exact 45th percentile (02's law).
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))

S = 680
GRAIN = 2
G = S // GRAIN          # 340x340 grains
CELL = 64               # px
CG = CELL // GRAIN      # 32 grains per cell
TONE = 0.45

# --- Bayer 32x32 nest (10's recursive construction) ---
def bayer(n):
    b = np.array([[0, 2], [3, 1]], dtype=np.int64)
    while b.shape[0] < n:
        m = b.shape[0]
        nb = np.empty((2*m, 2*m), dtype=np.int64)
        nb[:m, :m] = 4*b + 0
        nb[:m, m:] = 4*b + 2
        nb[m:, :m] = 4*b + 3
        nb[m:, m:] = 4*b + 1
        b = nb
    return b

B = bayer(CG)                                # 32x32, values 0..1023
Uby = (B + 0.5) / (CG*CG)                    # uniformized nest rank

# --- AM radial rank, uniformized within the cell (11's dot as a rank field) ---
yy, xx = np.mgrid[0:CG, 0:CG].astype(np.float64)
r2 = (xx - (CG/2 - 0.5))**2 + (yy - (CG/2 - 0.5))**2
flat = r2.ravel()
order = np.argsort(flat, kind="stable")
rank = np.empty_like(order)
rank[order] = np.arange(flat.size)
Uam = ((rank + 0.5) / flat.size).reshape(CG, CG)

# sanity: threshold each parent at its own 45th percentile
def percentile_threshold(U, tone=TONE):
    thr = np.quantile(U, tone)
    return U < thr

dot = percentile_threshold(Uam)
nest = percentile_threshold(Uby)
print("cell ink: dot %.4f nest %.4f" % (dot.mean(), nest.mean()))

# --- whole field by tiling (wrap at edges, periodic screen) ---
fy, fx = np.mgrid[0:G, 0:G]
UAM = Uam[fy % CG, fx % CG]
UBY = Uby[fy % CG, fx % CG]

def field(w):
    U = (1-w)*UAM + w*UBY
    thr = np.quantile(U, TONE)
    return U < thr, U

def to_img(on):
    a = np.kron(on.astype(np.uint8)*255, np.ones((GRAIN, GRAIN), np.uint8))
    return Image.fromarray(255 - a, mode="L")   # ink = black

# journey states
for name, w in [("k000", 0.0), ("k025", 0.25), ("k050", 0.5),
                ("k075", 0.75), ("k100", 1.0)]:
    on, U = field(w)
    to_img(on).save(os.path.join(OUT, name + ".png"))
    print(name, "ink=%.4f" % on.mean())

# --- granularity: 200-step sweep, worst flip fraction ---
prev = None
worst = 0.0
worst_at = -1
tot = 0.0
for i in range(201):
    w = i / 200
    on, _ = field(w)
    if prev is not None:
        f = np.mean(on != prev)
        tot += f
        if f > worst:
            worst, worst_at = f, w
    prev = on
print("worst flip per 1/200 step: %.4f at w=%.3f (mean %.4f)" % (worst, worst_at, tot/200))
