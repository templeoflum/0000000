import numpy as np
from PIL import Image
import os

S = 680
P = 24.0          # screen ruling period, px
OUT = os.path.dirname(os.path.abspath(__file__))

y, x = np.mgrid[0:S, 0:S].astype(np.float64)
# rotate about field centre so the moire breathes symmetrically
xc, yc = x - S/2, y - S/2

def dot_screen(theta_deg, p=P):
    """Euclidean (round) AM dot spot function, value in [0,1], 1 at dot centre.
       cell units: r folded to nearest cell centre; R=0.5 cell."""
    th = np.deg2rad(theta_deg)
    u = (xc*np.cos(th) + yc*np.sin(th)) / p
    v = (-xc*np.sin(th) + yc*np.cos(th)) / p
    du = u - np.round(u)
    dv = v - np.round(v)
    r2 = du*du + dv*dv
    return np.clip(1.0 - r2/0.25, 0.0, 1.0)   # R = 0.5 cell

def render(L, fname):
    thr = np.percentile(L, 55.0)   # black = top 45% of landscape  (ink 0.45)
    bw = (L >= thr)
    cov = bw.mean()
    Image.fromarray(np.where(bw, 0, 255).astype(np.uint8)).save(os.path.join(OUT, fname))
    return cov

for dth in [0, 4, 8, 16, 24, 30, 38, 45]:
    L1 = dot_screen(45 + dth/2)
    L2 = dot_screen(45 - dth/2)
    cov = render(L1*L2, f"dth{dth:02d}_product.png")
    lam = P/(2*np.sin(np.deg2rad(dth/2))) if dth > 0 else np.inf
    print(f"dth={dth:5.1f}  moire cell={lam:7.1f}px  ink={cov:.4f}")
