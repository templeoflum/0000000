# S16 — candidate stop states at n=170
import numpy as np
from PIL import Image

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def show(u, out, n):
    img = (np.clip(u,0,1)*255).astype(np.uint8)
    Image.fromarray(img).resize((n*2,n*2), Image.NEAREST).save(out)

def run(u, v, a=0.75, b=0.02, eps=0.02, dt=0.1, steps=4000, paces=None, n=170):
    # paces: list of (period, active_steps, cy, cx, r)
    for t in range(steps):
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*(u - v)
        if paces:
            for (P, act, cy, cx, r) in paces:
                if t % P < act:
                    yy, xx = np.ogrid[:n,:n]
                    u[(yy-cy)**2+(xx-cx)**2 < r*r] = 1.0
    return u, v

n = 170
Y, X = np.mgrid[0:n,0:n]

# S1: dual pacemaker interference (ripple tank)
u = np.zeros((n,n)); v = np.zeros((n,n))
u, v = run(u, v, steps=3500, paces=[(70,3,n//2,n//2-45,4),(70,3,n//2,n//2+45,4)], n=n)
show(u, "S1_ripple.png", n); print("ripple", (u>0.5).mean())

# S3: 2x2 spiral lattice, alternating chirality
def spiral_seed(n, cells):
    u = np.zeros((n,n)); v = np.zeros((n,n))
    cs = n//cells
    for i in range(cells):
        for j in range(cells):
            y0,y1 = i*cs,(i+1)*cs; x0,x1 = j*cs,(j+1)*cs
            ym=(y0+y1)//2; xm=(x0+x1)//2
            ch = 1 if (i+j)%2==0 else -1
            if ch>0:
                u[y0:ym, x0:x1] = 1.0
                v[y0:y1, xm:x1] = 0.5
            else:
                u[ym:y1, x0:x1] = 1.0
                v[y0:y1, x0:xm] = 0.5
    return u, v

for cells, name, steps in [(2,"S3_spiral4",5000),(4,"S4_spiral16",5000)]:
    u, v = spiral_seed(n, cells)
    u, v = run(u, v, steps=steps, n=n)
    show(u, f"{name}.png", n); print(name, (u>0.5).mean())

# S5/S6: noise breakup storm, frozen transient — try b=0.03 and 0.05
rng = np.random.default_rng(11)
for b, steps in [(0.02,3000),(0.03,3000),(0.05,3000)]:
    u = (rng.random((n,n)) < 0.22).astype(float)
    v = 0.08*rng.random((n,n))
    u, v = run(u, v, b=b, steps=steps, n=n)
    show(u, f"storm_b{b}.png", n); print("storm b", b, (u>0.5).mean())
