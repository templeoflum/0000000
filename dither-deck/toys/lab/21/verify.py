# S21 FINAL verification: decay 0.5 (exact 1/sqrt(r)), ladder [0,.6,1.2,2,3,4.5,6.5,10]
# measures: ink per stop, worst/mean flip per 1/200 step over a 200-step sweep (BN dissolve)
import numpy as np
from PIL import Image
import os, base64, re

OUT = os.path.dirname(os.path.abspath(__file__))
S = 680; CX = CY = S/2.0; LAM = 24.0; R0 = 24.0
yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)

def stopfield(dl):
    d = dl * LAM
    x1, x2 = CX - d/2, CX + d/2
    r1 = np.sqrt((xx-x1)**2 + (yy-CY)**2); r2 = np.sqrt((xx-x2)**2 + (yy-CY)**2)
    F = np.sqrt(LAM/(r1+R0))*np.cos(2*np.pi*r1/LAM) + np.sqrt(LAM/(r2+R0))*np.cos(2*np.pi*r2/LAM)
    t = np.percentile(F, 45.0)
    return (F < t).astype(np.uint8)

STOPS_LAM = [0, 0.6, 1.2, 2, 3, 4.5, 6.5, 10]
stops = [stopfield(dl) for dl in STOPS_LAM]
print("ink per stop:", [f"{B.mean():.4f}" for B in stops])

html = open(r"C:\Users\User\Documents\0000000\dither-deck\toys\02.html", encoding="utf8").read()
raw = base64.b64decode(re.search(r'const b64="([^"]+)"', html).group(1))
bn = np.array([(raw[2*i] | (raw[2*i+1] << 8)) + 0.5 for i in range(128*128)]) / (128*128)
BNt = np.tile(bn.reshape(128,128), (6,6))[:S,:S]

NS = len(stops); prev=None; worst=0; worst_k=-1; flips=[]
for step in range(201):
    k = step/200.0
    p = k*(NS-1); D = min(int(np.floor(p)), NS-2); f = p-D
    A, B = stops[D], stops[D+1]
    cur = np.where(A==B, A, np.where(BNt < f, B, A))
    ink = cur.mean()
    if prev is not None:
        fr = (cur != prev).mean(); flips.append(fr)
        if fr > worst: worst, worst_k = fr, k
    prev = cur
print(f"worst flip per 1/200 step: {worst:.4f} at k={worst_k:.3f}")
print(f"mean flip: {np.mean(flips):.4f}  p95: {np.percentile(flips,95):.4f}")

# save final stop PNGs
for i, (dl, B) in enumerate(zip(STOPS_LAM, stops)):
    Image.fromarray((1-B)*255, "L").save(os.path.join(OUT, f"final_stop{i}_d{dl}.png"))
# a mid-dissolve state for the eye: k=0.635 (worst flip point)
k = 0.635; p = k*(NS-1); D = min(int(np.floor(p)), NS-2); f = p-D
A, B = stops[D], stops[D+1]
cur = np.where(A==B, A, np.where(BNt < f, B, A))
Image.fromarray((1-cur)*255, "L").save(os.path.join(OUT, "final_mid_k0635.png"))
print("saved final stops + mid state")
