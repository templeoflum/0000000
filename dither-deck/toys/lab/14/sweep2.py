"""Round 2: wavelength scaling, anisotropic diffusivity, stripe->dot breakup."""
import numpy as np
from PIL import Image
import time, os

OUT = os.path.dirname(os.path.abspath(__file__))
G = 224

def lap9(z):
    return (0.2*(np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1))
           +0.05*(np.roll(np.roll(z,1,0),1,1)+np.roll(np.roll(z,1,0),-1,1)
                 +np.roll(np.roll(z,-1,0),1,1)+np.roll(np.roll(z,-1,0),-1,1))
           -z)

def lap_aniso(z, wx, wy):
    # anisotropic: separate x/y second differences (5-point)
    return (wx*(np.roll(z,1,1)+np.roll(z,-1,1)-2*z)
           +wy*(np.roll(z,1,0)+np.roll(z,-1,0)-2*z))

def run(F, kill, steps, dscale=1.0, aniso=None, seed=7):
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
            lu = lap_aniso(u, DU*aniso[0], DU*aniso[1])
            lv = lap_aniso(v, DV*aniso[0], DV*aniso[1])
        else:
            lu, lv = lap9(u), lap9(v)
        u += DU*0 + lu*dscale if False else u # noop
        u += lu*1.0*0 # noop
        # apply
        du = lu - uvv + F*(1-u); dv = lv + uvv - (F+kill)*v
        # NOTE: lap9 already carries the D weighting? No - S13 multiplies D outside.
        u += du; v += dv
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
    return v

def run2(F, kill, steps, dscale=1.0, aniso=None, seed=7):
    """correct version: lu is unit Laplacian; multiply by D outside"""
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
    thr = np.quantile(v, 1-tone)
    return (v <= thr)

cases = [
    ("A fine   F030 k062 D1",   dict(F=0.030, kill=0.062, dscale=1.0)),
    ("B med    F035 k060 D1",   dict(F=0.035, kill=0.060, dscale=1.0)),
    ("C broad  F035 k060 D2",   dict(F=0.035, kill=0.060, dscale=2.0)),
    ("D broad2 F030 k060 D2.8", dict(F=0.030, kill=0.060, dscale=2.8)),
    ("E aniso x4 F035 k060",    dict(F=0.035, kill=0.060, aniso=(1.0,0.25))),
    ("F aniso x8 F035 k060",    dict(F=0.035, kill=0.060, aniso=(1.0,0.12))),
    ("G aniso x8 F030 k062",    dict(F=0.030, kill=0.062, aniso=(1.0,0.12))),
    ("H dash F045 k063",        dict(F=0.045, kill=0.063)),
    ("I dash F050 k063",        dict(F=0.050, kill=0.063)),
    ("J dash F050 k0635",       dict(F=0.050, kill=0.0635)),
    ("K dash F055 k063",        dict(F=0.055, kill=0.063)),
    ("L aniso y8 F035 k060",    dict(F=0.035, kill=0.060, aniso=(0.12,1.0))),
]
cells = []
for name, kw in cases:
    t0=time.time()
    v = run2(steps=4000, **kw)
    b = to_bits(v)
    print(f"{name}: ink={b.mean():.3f} ({time.time()-t0:.0f}s)", flush=True)
    cells.append((name, b))

cols=3; rows=(len(cells)+cols-1)//cols
M=np.full((rows*G, cols*G), 128, dtype=np.uint8)
for idx,(name,b) in enumerate(cells):
    r,c=divmod(idx,cols)
    M[r*G:(r+1)*G, c*G:(c+1)*G]=np.where(b,0,255)
Image.fromarray(M).save(os.path.join(OUT,"sweep2.png"))
print("saved")
