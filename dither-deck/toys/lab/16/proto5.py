# S16 — breakup storm: organized spirals seeded into breakup regime, frozen transient
import numpy as np
from PIL import Image

def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)

def show(u, out, n):
    img = (np.clip(u,0,1)*255).astype(np.uint8)
    Image.fromarray(img).resize((n*2,n*2), Image.NEAREST).save(out)

def run(u, v, a, b, eps=0.02, dt=0.1, steps=6000, n=170, mark=None):
    cov=[]
    for t in range(steps):
        du = lap(u) + (1.0/eps)*u*(1-u)*(u - (v+b)/a)
        u = np.clip(u + dt*du, 0, 1.5)
        v = v + dt*(u - v)
        if t % 1000 == 999: cov.append(round(float((u>0.5).mean()),3))
    return u, v, cov

def spiral_seed(n, cells):
    u = np.zeros((n,n)); v = np.zeros((n,n))
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

n=170
for a,b in [(1.1,0.19),(1.0,0.13),(0.9,0.1)]:
    u,v = spiral_seed(n,3)
    u,v,cov = run(u,v,a,b,steps=5000,n=n)
    show(u, f"brk_a{a}_b{b}.png", n); print("a",a,"b",b,"cov",cov)
