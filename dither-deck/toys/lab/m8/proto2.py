# Variant test: (a) grow from seed with advection, long time
#               (b) grow the coat pure, then switch the flow on (couple-after-birth)
import numpy as np
from PIL import Image
import os, sys
from proto import G, R, VX, VY, SOLID, Du, Dv, F, KK, DT, lap9, upwind, seed, cut, OUT

def run_a(c, steps):
    u, v = seed()
    vx, vy = c * VX, c * VY
    u[SOLID] = 1.0; v[SOLID] = 0.0
    for t in range(steps):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u) - upwind(u, vx, vy))
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0; v[SOLID] = 0.0
    return u, v

def run_b(c, grow=520, coupled=600):
    u, v = seed()
    u[SOLID] = 1.0; v[SOLID] = 0.0
    for t in range(grow):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u))
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v)
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0; v[SOLID] = 0.0
    if c > 0:
        vx, vy = c * VX, c * VY
        for t in range(coupled):
            uvv = u * v * v
            u += DT * (Du * lap9(u) - uvv + F * (1 - u) - upwind(u, vx, vy))
            v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
            np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
            u[SOLID] = 1.0; v[SOLID] = 0.0
    return u, v

def save(u, v, name):
    b, ink = cut(v, 74)
    img = Image.fromarray((1 - b) * 255).resize((G * 3, G * 3), Image.NEAREST)
    img.save(os.path.join(OUT, name))
    # spatial ink in 4x4 blocks to judge barren regions
    bs = b.reshape(4, G // 4, 4, G // 4).mean(axis=(1, 3))
    print(name, "ink=%.3f" % ink, "block-ink min=%.2f max=%.2f" % (bs.min(), bs.max()))

if __name__ == "__main__":
    u, v = run_a(0.16, 1500); save(u, v, "A_c016_t1500.png")
    u, v = run_a(0.22, 1500); save(u, v, "A_c022_t1500.png")
    u, v = run_b(0.16); save(u, v, "B_c016.png")
    u, v = run_b(0.25); save(u, v, "B_c025.png")
    u, v = run_b(0.35); save(u, v, "B_c035.png")
