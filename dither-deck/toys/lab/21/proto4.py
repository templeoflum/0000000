# decay comparison at d=6.5lam and d=10lam: exponent 0.5 (exact 1/sqrt(r)) vs 0.4
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 680; CX = CY = S/2.0; LAM = 24.0; R0 = 24.0
yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)

def stopfield(d, dec):
    x1, x2 = CX - d/2, CX + d/2
    r1 = np.sqrt((xx-x1)**2 + (yy-CY)**2); r2 = np.sqrt((xx-x2)**2 + (yy-CY)**2)
    F = (LAM/(r1+R0))**dec*np.cos(2*np.pi*r1/LAM) + (LAM/(r2+R0))**dec*np.cos(2*np.pi*r2/LAM)
    t = np.percentile(F, 45.0)
    return (F < t).astype(np.uint8)

mos = np.full((680, 680*2+12), 128, dtype=np.uint8)
for j, dec in enumerate([0.5, 0.4]):
    B = stopfield(6.5*LAM, dec)
    mos[:, j*692:j*692+680] = (1-B)*255
Image.fromarray(mos, "L").save(os.path.join(OUT, "decay_d65.png"))

mos2 = np.full((680, 680*2+12), 128, dtype=np.uint8)
for j, dec in enumerate([0.5, 0.4]):
    B = stopfield(10*LAM, dec)
    mos2[:, j*692:j*692+680] = (1-B)*255
Image.fromarray(mos2, "L").save(os.path.join(OUT, "decay_d10.png"))
print("saved")
