# Robustness: seed & time sensitivity at c=0.20; early-journey states.
import numpy as np
from PIL import Image
import os
import proto
from proto import G, VX, VY, SOLID, Du, Dv, F, KK, DT, lap9, upwind, cut, OUT

def run(c, steps=700, sd=42):
    rng = np.random.RandomState(sd)
    u = np.ones((G, G)); v = np.zeros((G, G))
    m = rng.rand(G, G) < 0.08
    u[m] = 0.5; v[m] = 0.5
    vx, vy = c * VX, c * VY
    u[SOLID] = 1.0; v[SOLID] = 0.0
    for t in range(steps):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u))
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0; v[SOLID] = 0.0
    return v

def save(v, name):
    b, ink = cut(v, 74)
    Image.fromarray((1 - b) * 255).resize((G * 3, G * 3), Image.NEAREST).save(os.path.join(OUT, name))
    print(name, "ink=%.3f" % ink)
    return b

if __name__ == "__main__":
    b1 = save(run(0.20, 700, 42), "D_c020_s42_t700.png")
    b2 = save(run(0.20, 700, 7), "D_c020_s07_t700.png")
    b3 = save(run(0.20, 1400, 42), "D_c020_s42_t1400.png")
    print("seed-flip frac: %.3f  time-flip frac: %.3f" % (np.mean(b1 != b2), np.mean(b1 != b3)))
    save(run(0.05, 700, 42), "D_c005.png")
    save(run(0.10, 700, 42), "D_c010.png")
    save(run(0.30, 700, 42), "D_c030.png")
