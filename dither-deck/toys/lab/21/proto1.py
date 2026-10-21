# S21 prototype 1: the ripple tank — two coherent point sources, k = separation d/lambda
# psi = cos(2*pi*r1/lam)/sqrt(r1+r0) + cos(2*pi*r2/lam)/sqrt(r2+r0)
# each stop thresholded at its own 45th percentile (02's law)
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 680
CX = CY = S / 2.0

LAM = 24.0          # wavelength px
R0 = 24.0           # decay softening: amplitude sqrt(LAM/(r+R0))... use 1/sqrt(r+R0) scaled

yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)

def field(d):
    x1, x2 = CX - d / 2.0, CX + d / 2.0
    r1 = np.sqrt((xx - x1) ** 2 + (yy - CY) ** 2)
    r2 = np.sqrt((xx - x2) ** 2 + (yy - CY) ** 2)
    a1 = np.sqrt(LAM / (r1 + R0))
    a2 = np.sqrt(LAM / (r2 + R0))
    return a1 * np.cos(2 * np.pi * r1 / LAM) + a2 * np.cos(2 * np.pi * r2 / LAM)

def thr45(F):
    return np.percentile(F, 45.0)

stops_lam = [0, 0.75, 1.5, 2.5, 4, 6, 9, 13, 19, 27]
tiles = []
for dl in stops_lam:
    F = field(dl * LAM)
    t = thr45(F)
    B = (F < t).astype(np.uint8)
    cov = B.mean()
    print(f"d/lam={dl:5.2f}  d={dl*LAM:6.1f}px  ink={cov:.4f}")
    tiles.append(B)

# montage: 2 rows x 5 cols, each 340x340 downsampled
mos = np.full((2 * 340 + 12, 5 * 340 + 48, ), 128, dtype=np.uint8)
for idx, B in enumerate(tiles):
    small = B[::2, ::2] * 255
    r, c = divmod(idx, 5)
    y0 = r * (340 + 12)
    x0 = c * (340 + 12)
    mos[y0:y0 + 340, x0:x0 + 340] = 255 - small  # ink = black
Image.fromarray(mos, "L").save(os.path.join(OUT, "montage1.png"))

# also save individual full-res states for eyeballing
for idx, dl in enumerate(stops_lam):
    B = tiles[idx]
    Image.fromarray((1 - B) * 255, "L").save(os.path.join(OUT, f"stop_{idx:02d}_d{dl}.png"))
print("saved montage1.png + stops")
