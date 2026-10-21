import numpy as np, time, os
from PIL import Image

S = 680; N = S*S
OUT = os.path.dirname(os.path.abspath(__file__))
y, x = np.mgrid[0:S, 0:S].astype(np.float64)
xc = (x - S/2).ravel(); yc = (y - S/2).ravel()

def run(P, SIG, W0, label, render=False):
    SIG2 = 2*SIG*SIG
    GT = np.exp(-np.linspace(0, 0.5, 1025)/SIG2).astype(np.float32)
    def spot(th_deg):
        th = np.deg2rad(th_deg)
        u = (xc*np.cos(th) + yc*np.sin(th)) / P
        v = (-xc*np.sin(th) + yc*np.cos(th)) / P
        du = u - np.floor(u + 0.5); dv = v - np.floor(v + 0.5)
        q = du*du + dv*dv
        return GT[(q*2048).astype(np.int32).clip(0,1024)]
    def params(k):
        return 30.0*k, (0.0 if k <= W0 else (k-W0)/(1-W0))
    L3 = spot(90.0)
    def field(k):
        dth, w = params(k)
        L1 = spot(45.0 + dth/2); L2 = spot(45.0 - dth/2)
        L = L1*L2
        if w > 0: L = L*((1-w) + w*L3)
        return L
    def thresh(L):
        h = np.bincount((L*512).astype(np.int32).clip(0,512), minlength=513)
        acc = np.cumsum(h[::-1])[::-1]
        q = int(np.argmax(acc < N*0.45))
        thr = (q-0.5)/512 if q > 0 else 0.0
        return (L >= thr)
    prev = thresh(field(0.0)); worst=0.0; worstk=0.0; inks=[]
    for i in range(0,201):
        kk = i/200
        bw = thresh(field(kk))
        inks.append(bw.mean())
        if i:
            fl = np.count_nonzero(bw!=prev)/N
            if fl>worst: worst, worstk = fl, kk
        prev = bw
        if render and i in (0,50,100,150,200):
            Image.fromarray(np.where(bw.reshape(S,S),0,255).astype(np.uint8)).save(os.path.join(OUT,f"{label}_k{i:03d}.png"))
    print(f"{label}: worst={worst*100:.2f}% at k={worstk:.3f}  ink [{min(inks):.4f},{max(inks):.4f}]")

t0=time.time()
run(30.0, 0.24, 0.72, "m_p30s24", render=True)
print(f"{time.time()-t0:.0f}s")

t0=time.time()
run(30.0, 0.22, 0.72, "m_p30s22")
run(30.0, 0.20, 0.72, "m_p30s20")
run(32.0, 0.22, 0.72, "m_p32s22")
print(f"{time.time()-t0:.0f}s")
