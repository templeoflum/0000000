# Variant C: advect the activator v only; substrate u is gel-immobilized.
# Physical precedent: gel reactors (CIMA etc.) immobilize one species.
import numpy as np
from PIL import Image
import os
from proto import G, VX, VY, SOLID, Du, Dv, F, KK, DT, lap9, upwind, seed, cut, OUT

def run_c(c, steps=700):
    u, v = seed()
    vx, vy = c * VX, c * VY
    u[SOLID] = 1.0; v[SOLID] = 0.0
    for t in range(steps):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u))          # u: no advection
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0; v[SOLID] = 0.0
    return v

def save(v, name):
    b, ink = cut(v, 74)
    Image.fromarray((1 - b) * 255).resize((G * 3, G * 3), Image.NEAREST).save(os.path.join(OUT, name))
    bs = b.reshape(4, G // 4, 4, G // 4).mean(axis=(1, 3))
    print(name, "ink=%.3f" % ink, "block-ink min=%.2f max=%.2f" % (bs.min(), bs.max()))

if __name__ == "__main__":
    for c in [0.10, 0.20, 0.30, 0.45]:
        save(run_c(c), f"C_c{int(c*100):03d}.png")
