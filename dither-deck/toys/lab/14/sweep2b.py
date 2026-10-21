"""Round 2b: per-case saves, batch by CLI args."""
import numpy as np
from PIL import Image
import time, os, sys

OUT = os.path.dirname(os.path.abspath(__file__))
G = 224

def lap9(z):
    return (0.2*(np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1))
           +0.05*(np.roll(np.roll(z,1,0),1,1)+np.roll(np.roll(z,1,0),-1,1)
                 +np.roll(np.roll(z,-1,0),1,1)+np.roll(np.roll(z,-1,0),-1,1))
           -z)

def lap_aniso(z, wx, wy):
    return (wx*(np.roll(z,1,1)+np.roll(z,-1,1)-2*z)
           +wy*(np.roll(z,1,0)+np.roll(z,-1,0)-2*z))

def run2(F, kill, steps, dscale=1.0, aniso=None, seed=7):
    DU, DV = 0.21*dscale, 0.105*dscale
    rng = np.random.default_rng(seed)
    u = np.ones((G,G)); v = np.zeros((G,G))
    for _ in range(int(0.08*G*G/64)):
        y = rng.integers(0, G-8); x = rng.integers(0, G-8)
        u[y:y+8, x:x+8] = 0.5 + 0.05*rng.standard_normal((8,8))
        v[y:y+8, x:x+8] = 0.25 + 0.05*rng.standard_normal((8,8))
    for _ in range(steps):
        uvv = u*v*v
        if aniso:
            lu = lap_aniso(u, aniso[0], aniso[1])
            lv = lap_aniso(v, aniso[0], aniso[1])
        else:
            lu, lv = lap9(u), lap9(v)
        u += DU*lu - uvv + F*(1-u)
        v += DV*lv + uvv - (F+kill)*v
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
    return v

def to_bits(v, tone=0.45):
    thr = np.quantile(v, tone)
    return (v <= thr)

cases = {
    "A": ("A fine   F030 k062 D1",   dict(F=0.030, kill=0.062, dscale=1.0)),
    "B": ("B med    F035 k060 D1",   dict(F=0.035, kill=0.060, dscale=1.0)),
    "C": ("C broad  F035 k060 D2",   dict(F=0.035, kill=0.060, dscale=2.0)),
    "D": ("D broad2 F030 k060 D2.8", dict(F=0.030, kill=0.060, dscale=2.8)),
    "E": ("E aniso x4 F035 k060",    dict(F=0.035, kill=0.060, aniso=(1.0,0.25))),
    "F": ("F aniso x8 F035 k060",    dict(F=0.035, kill=0.060, aniso=(1.0,0.12))),
    "G": ("G aniso x8 F030 k062",    dict(F=0.030, kill=0.062, aniso=(1.0,0.12))),
    "H": ("H dash F045 k063",        dict(F=0.045, kill=0.063)),
    "I": ("I dash F050 k063",        dict(F=0.050, kill=0.063)),
    "J": ("J dash F050 k0635",       dict(F=0.050, kill=0.0635)),
    "K": ("K dash F055 k063",        dict(F=0.055, kill=0.063)),
    "L": ("L aniso y8 F035 k060",    dict(F=0.035, kill=0.060, aniso=(0.12,1.0))),
}
for key in sys.argv[1:]:
    name, kw = cases[key]
    t0=time.time()
    v = run2(steps=3500, **kw)
    b = to_bits(v)
    Image.fromarray(np.where(b,0,255).astype(np.uint8)).save(os.path.join(OUT,f"case_{key}.png"))
    print(f"{name}: ink={b.mean():.3f} ({time.time()-t0:.0f}s)", flush=True)
