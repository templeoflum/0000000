# S16 EXCITABLE — final stop generation at n=340
# Barkley model: du = lap(u) + (1/eps)u(1-u)(u-(v+b)/a), dv = u-v
import numpy as np
from PIL import Image
import time, base64, json

n = 340
Y, X = np.mgrid[0:n, 0:n]

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def run(u, v, a=0.75, b=0.02, eps=0.02, dt=0.1, steps=4000, paces=None):
    u = u.astype(np.float32); v = v.astype(np.float32)
    for t in range(steps):
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*(u - v)
        if paces:
            for (P, act, cy, cx, r) in paces:
                if t % P < act:
                    u[(Y-cy)**2+(X-cx)**2 < r*r] = 1.0
    return u, v

def spiral_seed(cells):
    u = np.zeros((n,n), np.float32); v = np.zeros((n,n), np.float32)
    cs = n//cells
    for i in range(cells):
        for j in range(cells):
            y0,y1=i*cs,(i+1)*cs; x0,x1=j*cs,(j+1)*cs
            ym=(y0+y1)//2; xm=(x0+x1)//2
            if (i+j)%2==0:
                u[y0:ym, x0:x1]=1.0; v[y0:y1, xm:x1]=0.5
            else:
                u[ym:y1, x0:x1]=1.0; v[y0:y1, x0:xm]=0.5
    return u, v

states = {}

t0=time.time()
# S0 targets
u,v = run(np.zeros((n,n)), np.zeros((n,n)), steps=3200, paces=[(70,3,n//2,n//2,5)])
states["targets"] = u; print("targets", time.time()-t0)
# S1 ripple (two pacemakers)
u,v = run(np.zeros((n,n)), np.zeros((n,n)), steps=3200,
          paces=[(70,3,n//2,n//2-85,5),(70,3,n//2,n//2+85,5)])
states["ripple"] = u; print("ripple", time.time()-t0)
# S2 pinwheel (single spiral)
u = (X < n//2).astype(np.float32); v = 0.5*(Y < n//2)
u,v = run(u, v, steps=5500)
states["pinwheel"] = u; print("pinwheel", time.time()-t0)
# S3 carousel (2x2 spirals)
u,v = spiral_seed(2)
u,v = run(u, v, steps=4500)
states["carousel"] = u; print("carousel", time.time()-t0)
# S4 fiddleheads (4x4 spirals)
u,v = spiral_seed(4)
u,v = run(u, v, steps=4500)
states["fiddleheads"] = u; print("fiddleheads", time.time()-t0)
# S5 worms (breakup transient, a=0.9 b=0.1)
u,v = spiral_seed(3)
u,v = run(u, v, a=0.9, b=0.1, steps=4500)
states["worms"] = u; print("worms", time.time()-t0)

np.savez("fields.npz", **states)

# two cut conventions for the eye test
for name, u in states.items():
    # deck law: 45th percentile of landscape F=1-u -> ink 0.45 where waves live
    F = 1.0 - np.clip(u, 0, 1)
    thr = np.quantile(F, 0.45)
    cut = (F < thr).astype(np.uint8)*255   # black where wave
    Image.fromarray(255-cut).resize((680,680), Image.NEAREST).save(f"F_{name}_p45.png")
    # natural wave cut: u > 0.5
    cut2 = (u > 0.5).astype(np.uint8)*255
    Image.fromarray(255-cut2).resize((680,680), Image.NEAREST).save(f"F_{name}_wave.png")
    print(name, "ink p45:", (F<thr).mean(), " ink wave:", (u>0.5).mean())
