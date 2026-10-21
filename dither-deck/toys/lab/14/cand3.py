"""Round 3: candidate stops at 340^2 (toy resolution)."""
import numpy as np
from PIL import Image
import time, os, sys

OUT = os.path.dirname(os.path.abspath(__file__))
G = 340

def lap9(z):
    return (0.2*(np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1))
           +0.05*(np.roll(np.roll(z,1,0),1,1)+np.roll(np.roll(z,1,0),-1,1)
                 +np.roll(np.roll(z,-1,0),1,1)+np.roll(np.roll(z,-1,0),-1,1))
           -z)

def lap_aniso(z, wx, wy):
    return (wx*(np.roll(z,1,1)+np.roll(z,-1,1)-2*z)
           +wy*(np.roll(z,1,0)+np.roll(z,-1,0)-2*z))

def init(seed=7):
    rng = np.random.default_rng(seed)
    u = np.ones((G,G)); v = np.zeros((G,G))
    for _ in range(int(0.08*G*G/64)):
        y = rng.integers(0, G-8); x = rng.integers(0, G-8)
        u[y:y+8, x:x+8] = 0.5 + 0.05*rng.standard_normal((8,8))
        v[y:y+8, x:x+8] = 0.25 + 0.05*rng.standard_normal((8,8))
    return u, v

def run(F, kill, steps, dscale=1.0, aniso=None, seed=7, snaps=()):
    DU, DV = 0.21*dscale, 0.105*dscale
    u, v = init(seed)
    out = {}
    snaps = set(snaps)
    for t in range(1, steps+1):
        uvv = u*v*v
        if aniso:
            lu = lap_aniso(u, aniso[0], aniso[1]); lv = lap_aniso(v, aniso[0], aniso[1])
        else:
            lu, lv = lap9(u), lap9(v)
        u += DU*lu - uvv + F*(1-u)
        v += DV*lv + uvv - (F+kill)*v
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        if t in snaps: out[t] = v.copy()
    out[steps] = v
    return out

def to_bits(v, tone=0.45):
    thr = np.quantile(v, tone)
    return (v <= thr)

jobs = {
    "dash700":  (dict(F=0.035, kill=0.060), 700),
    "dash1200": (dict(F=0.035, kill=0.060), 1200),
    "E340":     (dict(F=0.035, kill=0.060, aniso=(1.0,0.25)), 4000),
    "F340":     (dict(F=0.035, kill=0.060, aniso=(1.0,0.12)), 4000),
    "F340x6":   (dict(F=0.035, kill=0.060, aniso=(1.0,0.17)), 4000),
}
for key in sys.argv[1:]:
    kw, steps = jobs[key]
    t0=time.time()
    vs = run(steps=steps, **kw)
    v = vs[steps]
    b = to_bits(v)
    Image.fromarray(np.where(b,0,255).astype(np.uint8)).save(os.path.join(OUT,f"cand_{key}.png"))
    print(f"{key}: ink={b.mean():.3f} ({time.time()-t0:.0f}s)", flush=True)
