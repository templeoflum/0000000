import numpy as np
from PIL import Image
import os

S = 680
P = 24.0
OUT = os.path.dirname(os.path.abspath(__file__))
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
xc, yc = x - S/2, y - S/2
SIG2 = 2*0.27**2

def spot(theta_deg, e=1.0):
    """Gaussian elliptical AM dot spot function; e=1 round, e>1 elongates
       along the cell u-axis toward the line-screen crossover."""
    th = np.deg2rad(theta_deg)
    u = (xc*np.cos(th) + yc*np.sin(th)) / P
    v = (-xc*np.sin(th) + yc*np.cos(th)) / P
    du = u - np.round(u)
    dv = v - np.round(v)
    r2 = (du/e)**2 + (dv*e)**2
    return np.exp(-r2/SIG2)

def render(L, fname):
    thr = np.percentile(L, 55.0)
    bw = (L >= thr)
    Image.fromarray(np.where(bw, 0, 255).astype(np.uint8)).save(os.path.join(OUT, fname))
    return bw.mean()

DTH = 30.0
for e in [1.0, 1.3, 1.6, 2.0, 2.6, 3.4]:
    L1 = spot(45 + DTH/2, e)
    L2 = spot(45 - DTH/2, e)
    cov = render(L1*L2, f"e{e:.1f}_rosette.png")
    print(f"e={e:.1f}  ink={cov:.4f}")

# also re-render the phase-1 states with gaussian round spots for consistency
for dth in [0, 3, 6.5, 12, 18]:
    L1 = spot(45 + dth/2); L2 = spot(45 - dth/2)
    cov = render(L1*L2, f"g_dth{dth:04.1f}.png")
    print(f"dth={dth:5.1f}  ink={cov:.4f}")
