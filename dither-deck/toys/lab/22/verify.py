import numpy as np
from PIL import Image
import os, time

S = 680; P = 28.0; N = S*S
OUT = os.path.dirname(os.path.abspath(__file__))
SIG2 = 2*0.27**2
PH1 = 0.70          # k where phase 1 (angle sweep) ends
EXP = 2.0
DTH_MAX = 30.0

y, x = np.mgrid[0:S, 0:S].astype(np.float64)
xc = (x - S/2).ravel(); yc = (y - S/2).ravel()

# Gaussian table g(q) = exp(-q/SIG2), q in [0, 0.5]
GT = np.exp(-np.linspace(0, 0.5, 1025)/SIG2).astype(np.float32)

def spot(th_deg):
    th = np.deg2rad(th_deg)
    u = (xc*np.cos(th) + yc*np.sin(th)) / P
    v = (-xc*np.sin(th) + yc*np.cos(th)) / P
    du = u - np.floor(u + 0.5); dv = v - np.floor(v + 0.5)
    q = du*du + dv*dv
    return GT[(q*2048).astype(np.int32).clip(0,1024)]

def params(k):
    if k <= PH1:
        return DTH_MAX*(k/PH1)**EXP, 0.0
    return DTH_MAX, (k-PH1)/(1-PH1)

L3 = spot(90.0)
def field(k):
    dth, w = params(k)
    if dth == 0 and w == 0:
        L = spot(45.0); return L*L
    L1 = spot(45.0 + dth/2); L2 = spot(45.0 - dth/2)
    L = L1*L2
    if w > 0: L = L*((1-w) + w*L3)
    return L

def thresh(L):
    # 55th percentile via 513-bin histogram, black = L >= thr  (exact 02-style)
    h = np.bincount((L*512).astype(np.int32).clip(0,512), minlength=513)
    acc = np.cumsum(h[::-1])[::-1]          # count >= bin
    q = int(np.argmax(acc < N*0.45))        # first bin where tail count < target
    thr = (q-0.5)/512 if q > 0 else 0.0
    return (L >= thr)

states = {0.0:"k000",0.25:"k025",0.5:"k050",0.75:"k075",1.0:"k100"}
for kk,name in states.items():
    bw = thresh(field(kk))
    Image.fromarray(np.where(bw.reshape(S,S),0,255).astype(np.uint8)).save(os.path.join(OUT,f"final_{name}.png"))
    d,w = params(kk); print(f"k={kk:4.2f} dth={d:5.2f} w={w:4.2f} ink={bw.mean():.4f}")

# 200-step granularity sweep
prev = thresh(field(0.0)); worst = 0.0; worstk = 0.0; tot=0
t0=time.time()
for i in range(1,201):
    kk = i/200
    bw = thresh(field(kk))
    fl = np.count_nonzero(bw != prev)/N
    tot += fl
    if fl > worst: worst, worstk = fl, kk
    prev = bw
print(f"worst flip/step = {worst*100:.2f}% at k={worstk:.3f}   mean = {tot/200*100:.2f}%   sweep time {time.time()-t0:.1f}s")
