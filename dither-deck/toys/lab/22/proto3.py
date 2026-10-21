import numpy as np
from PIL import Image
import os

S = 680
P = 28.0
OUT = os.path.dirname(os.path.abspath(__file__))
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
xc, yc = x - S/2, y - S/2
SIG2 = 2*0.27**2

def spot(theta_deg):
    th = np.deg2rad(theta_deg)
    u = (xc*np.cos(th) + yc*np.sin(th)) / P
    v = (-xc*np.sin(th) + yc*np.cos(th)) / P
    du = u - np.round(u); dv = v - np.round(v)
    return np.exp(-(du*du+dv*dv)/SIG2)

def render(L, fname):
    thr = np.percentile(L, 55.0)
    bw = (L >= thr)
    Image.fromarray(np.where(bw,0,255).astype(np.uint8)).save(os.path.join(OUT,fname))
    return bw.mean()

L1 = spot(30.0); L2 = spot(60.0); L3 = spot(90.0)
for w in [0.0, 0.35, 0.7, 1.0]:
    L = L1*L2*((1-w)+w*L3)
    print(f"w={w:.2f}  ink={render(L, f'w{w:.2f}_third.png'):.4f}")

# phase-1 endpoint with P=28 at 30deg for comparison
print(f"P28 dth30 ink={render(L1*L2,'p28_dth30.png'):.4f}")
