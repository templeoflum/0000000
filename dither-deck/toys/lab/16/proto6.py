# S16 — meander regime test: single spiral at larger b (core orbit -> rosette)
import numpy as np
from PIL import Image
import time

n=340
Y,X = np.mgrid[0:n,0:n]
def lap(z):
    return (np.roll(z,1,0)+np.roll(z,-1,0)+np.roll(z,1,1)+np.roll(z,-1,1)-4*z)
def run(u,v,a,b,eps=0.02,dt=0.1,steps=6000):
    u=u.astype(np.float32); v=v.astype(np.float32)
    for t in range(steps):
        du = lap(u)+(1.0/eps)*u*(1-u)*(u-(v+b)/a)
        u = np.clip(u+dt*du,0,1.5); v = v+dt*(u-v)
    return u,v
def show(u,out):
    F=1.0-np.clip(u,0,1); thr=np.quantile(F,0.45)
    cut=((F<thr).astype(np.uint8))*255
    Image.fromarray(255-cut).save(out)
    print(out,"ink",(F<thr).mean())

for b in [0.05,0.07]:
    t0=time.time()
    u=(X<n//2).astype(np.float32); v=0.5*(Y<n//2)
    u,v=run(u,v,0.75,b,steps=5500)
    show(u,f"meander_b{b}.png"); print(b,"t",time.time()-t0)
