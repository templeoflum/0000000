# S21 prototype 3: 8-stop ladder [0,.6,1.2,2,3,4.5,6.5,10], non-degenerate small stops
import numpy as np
from PIL import Image
import os, base64, re

OUT = os.path.dirname(os.path.abspath(__file__))
S = 680
CX = CY = S / 2.0
LAM = 24.0
R0 = 24.0
DECAY = 0.4

yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)

def field(d):
    x1, x2 = CX - d / 2.0, CX + d / 2.0
    r1 = np.sqrt((xx - x1) ** 2 + (yy - CY) ** 2)
    r2 = np.sqrt((xx - x2) ** 2 + (yy - CY) ** 2)
    a1 = (LAM / (r1 + R0)) ** DECAY
    a2 = (LAM / (r2 + R0)) ** DECAY
    return a1 * np.cos(2 * np.pi * r1 / LAM) + a2 * np.cos(2 * np.pi * r2 / LAM)

def stopfield(d):
    F = field(d)
    t = np.percentile(F, 45.0)
    return (F < t).astype(np.uint8)

STOPS_LAM = [0, 0.6, 1.2, 2, 3, 4.5, 6.5, 10]
stops = [stopfield(dl * LAM) for dl in STOPS_LAM]
extra = stopfield(12 * LAM)  # candidate tail
Image.fromarray((1 - extra) * 255, "L").save(os.path.join(OUT, "p3_d12.png"))

mos = np.full((2 * 340 + 12, 5 * 340 + 48), 128, dtype=np.uint8)
tiles = stops + [extra, stopfield(0.9 * LAM)]
for idx, B in enumerate(tiles):
    small = (1 - B[::2, ::2]) * 255
    r, c = divmod(idx, 5)
    mos[r * 352:r * 352 + 340, c * 352:c * 352 + 340] = small
Image.fromarray(mos, "L").save(os.path.join(OUT, "montage3.png"))

for i, (dl, B) in enumerate(zip(STOPS_LAM, stops)):
    Image.fromarray((1 - B) * 255, "L").save(os.path.join(OUT, f"p3_stop_{i}_d{dl}.png"))

# granularity with 8 stops (7 gaps)
html = open(r"C:\Users\User\Documents\0000000\dither-deck\toys\02.html", encoding="utf8").read()
m = re.search(r'const b64="([^"]+)"', html)
raw = base64.b64decode(m.group(1))
bn = np.array([(raw[2*i] | (raw[2*i+1] << 8)) + 0.5 for i in range(128*128)]) / (128*128)
BN = bn.reshape(128, 128)
BNt = np.tile(BN, (6, 6))[:S, :S]

NS = len(stops)
prev = None; worst = 0.0; worst_k = -1; flips = []
for step in range(201):
    k = step / 200.0
    p = k * (NS - 1)
    D = min(int(np.floor(p)), NS - 2)
    f = p - D
    A, B = stops[D], stops[D + 1]
    cur = np.where(A == B, A, np.where(BNt < f, B, A))
    if prev is not None:
        fr = (cur != prev).mean()
        flips.append(fr)
        if fr > worst: worst, worst_k = fr, k
    prev = cur
print(f"8 stops / 7 gaps: worst={worst:.4f} at k={worst_k:.3f} mean={np.mean(flips):.4f}")
for i in range(NS - 1):
    print(f"gap {STOPS_LAM[i]}->{STOPS_LAM[i+1]}: diff={(stops[i]!=stops[i+1]).mean():.4f}")
