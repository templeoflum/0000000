# tune sigma schedule + fix k=0 ties (nearest sampling at sigma=0)
import numpy as np, os
from PIL import Image
M=136; UP=5; S=M*UP
P=np.load(os.path.join(os.path.dirname(__file__),"mask136.npy")).astype(np.float64)
def conv2(A,sig):
    if sig==0: return A.copy()
    r=int(np.ceil(3*sig)); ax=np.arange(-r,r+1)
    yy,xx=np.meshgrid(ax,ax,indexing='ij')
    k2=np.exp(-(xx**2+yy**2)/(2*sig*sig)); k2/=k2.sum()
    Km=np.zeros((M,M)); Km[:2*r+1,:2*r+1]=k2; Km=np.roll(Km,(-r,-r),axis=(0,1))
    return np.fft.irfft2(np.fft.rfft2(A)*np.fft.rfft2(Km),s=(M,M))
ys=(np.arange(S)+0.5)/UP-0.5; xs=(np.arange(S)+0.5)/UP-0.5
y0=np.floor(ys).astype(int); x0=np.floor(xs).astype(int)
fy=(ys-y0)[:,None]; fx=(xs-x0)[None,:]
y0m=y0%M; y1m=(y0+1)%M; x0m=x0%M; x1m=(x0+1)%M
yn=np.rint(ys).astype(int)%M; xn=np.rint(xs).astype(int)%M
def upsample(F,nearest=False):
    if nearest: return F[np.ix_(yn,xn)]
    top=F[np.ix_(y0m,x0m)]*(1-fx)+F[np.ix_(y0m,x1m)]*fx
    bot=F[np.ix_(y1m,x0m)]*(1-fx)+F[np.ix_(y1m,x1m)]*fx
    return top*(1-fy)+bot*fy
def state(k,sigmax,p):
    sig=sigmax*(k**p)
    F=upsample(conv2(P,sig),nearest=(sig==0))
    t=np.quantile(F,0.45)
    return F<t
for sigmax,p in [(7.0,2.0),(7.0,2.5),(7.0,3.0),(6.5,2.5),(8.0,3.0)]:
    prev=None; worst=0; wk=0; covs=[]
    for i in range(201):
        B=state(i/200,sigmax,p); covs.append(B.mean())
        if prev is not None:
            fl=np.mean(B!=prev)
            if fl>worst: worst,wk=fl,i/200
        prev=B
    print(f"sigmax={sigmax} p={p}: ink[{min(covs):.4f},{max(covs):.4f}] worstflip={worst:.4f} at k={wk:.3f}")
