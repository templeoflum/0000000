# S16 — find self-sustaining breakup regime (Barkley parameter map)
import numpy as np
from PIL import Image

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def show(u, out, n):
    img = (np.clip(u,0,1)*255).astype(np.uint8)
    Image.fromarray(img).resize((n*2,n*2), Image.NEAREST).save(out)

def run(u, v, a, b, eps=0.02, dt=0.1, steps=6000, n=170):
    cov = []
    for t in range(steps):
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*(u - v)
        if t % 2000 == 1999: cov.append((u>0.5).mean())
    return u, v, cov

n = 170
rng = np.random.default_rng(11)
for a, b in [(0.9,0.06),(0.9,0.1),(1.0,0.13),(1.1,0.19)]:
    u = (rng.random((n,n)) < 0.22).astype(float)
    v = 0.08*rng.random((n,n))
    u, v, cov = run(u, v, a, b, n=n)
    show(u, f"break_a{a}_b{b}.png", n); print("a",a,"b",b,"cov trajectory",cov)
