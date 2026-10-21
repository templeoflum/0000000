# S16 EXCITABLE — Barkley model prototype
# du/dt = lap(u) + (1/eps) u(1-u)(u - (v+b)/a)
# dv/dt = u - v
# Barkley 1991 Physica D 49:61-70
import numpy as np
from PIL import Image
import sys

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def run(seed_cfg, a=0.75, b=0.02, eps=0.02, dt=0.1, steps=4000, n=170,
        snap_every=None, pace=None, out="out.png"):
    rng = np.random.default_rng(7)
    u = np.zeros((n,n)); v = np.zeros((n,n))
    if seed_cfg == "noise":
        u = (rng.random((n,n)) < 0.25).astype(float) * 1.0
        v = 0.1*rng.random((n,n))
    elif seed_cfg == "half":
        u[:, :n//2] = 1.0
    elif seed_cfg == "break":
        # plane wave then break: u=1 top half, run separately before break
        pass
    snaps = []
    for t in range(steps):
        # Barkley semi-implicit-ish: explicit Euler
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        dv = u - v
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*dv
        if pace and t % pace[1] < pace[2]:
            r = pace[3]
            cy, cx = n//2, n//2
            yy, xx = np.ogrid[:n,:n]
            u[(yy-cy)**2+(xx-cx)**2 < r*r] = 1.0
        if snap_every and t % snap_every == 0:
            snaps.append(u.copy())
    return u, v, snaps

def show(u, out, n=170):
    img = (np.clip(u,0,1)*255).astype(np.uint8)
    Image.fromarray(img).resize((n*2,n*2), Image.NEAREST).save(out)

if __name__ == "__main__":
    # try spiral turbulence from noise, a few eps values
    for eps in [0.02, 0.04, 0.06, 0.08]:
        u,v,_ = run("noise", eps=eps, steps=3000, n=170)
        show(u, f"noise_eps{eps}.png")
        print("eps", eps, "u frac>0.5:", (u>0.5).mean())
