# S16 — clean spiral seeding + pacemaker targets
import numpy as np
from PIL import Image

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def show(u, out, n):
    img = (np.clip(u,0,1)*255).astype(np.uint8)
    Image.fromarray(img).resize((n*2,n*2), Image.NEAREST).save(out)

def run(u, v, a=0.75, b=0.02, eps=0.02, dt=0.1, steps=4000, pace=None, n=170):
    for t in range(steps):
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*(u - v)
        if pace and t % pace[0] < pace[1]:
            yy, xx = pace[2]
            u[yy*yy+xx*xx < pace[3]**2] = 1.0
    return u, v

n = 170
yy, xx = np.mgrid[:n,:n] - n//2, np.mgrid[:n,:n].copy()
Y, X = np.mgrid[0:n,0:n]
Yc, Xc = Y-n//2, X-n//2

# 1) single spiral: quarter-plane seed
u = (X < n//2).astype(float); v = 0.5*(Y < n//2)
u, v = run(u, v, steps=5000, n=n)
show(u, "spiral1.png", n); print("spiral1 cov", (u>0.5).mean())

# 2) target pattern: pacemaker, dt pace every P steps
for P in [60, 120]:
    u = np.zeros((n,n)); v = np.zeros((n,n))
    u, v = run(u, v, steps=4000, pace=(P, 3, (Yc, Xc), 4), n=n)
    show(u, f"target_P{P}.png", n); print("target", P, (u>0.5).mean())

# 3) spiral turbulence: noise seed, run long
rng = np.random.default_rng(3)
u = (rng.random((n,n)) < 0.22).astype(float)
v = 0.08*rng.random((n,n))
u, v = run(u, v, steps=8000, n=n)
show(u, "turb_long.png", n); print("turb", (u>0.5).mean())
