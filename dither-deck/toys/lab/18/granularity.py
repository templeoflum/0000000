# granularity + ink for the planned S18 pipeline:
# sigma(k) = SIGMAX*k^2 ; per-apply exact toroidal gaussian on 136^2 ;
# bilinear upsample to 680^2 ; threshold at exact 45th percentile.
import numpy as np, os
from PIL import Image
M=136; UP=5; S=M*UP; SIGMAX=7.0
P=np.load(os.path.join(os.path.dirname(__file__),"mask136.npy")).astype(np.float64)
def conv2(A,sig):
    if sig==0: return A.copy()
    r=int(np.ceil(3*sig)); ax=np.arange(-r,r+1)
    yy,xx=np.meshgrid(ax,ax,indexing='ij')
    k2=np.exp(-(xx**2+yy**2)/(2*sig*sig)); k2/=k2.sum()
    Km=np.zeros((M,M)); Km[:2*r+1,:2*r+1]=k2; Km=np.roll(Km,(-r,-r),axis=(0,1))
    return np.fft.irfft2(np.fft.rfft2(A)*np.fft.rfft2(Km),s=(M,M))
# precompute bilinear index maps once
ys=(np.arange(S)+0.5)/UP-0.5; xs=(np.arange(S)+0.5)/UP-0.5
y0=np.floor(ys).astype(int); x0=np.floor(xs).astype(int)
fy=(ys-y0)[:,None]; fx=(xs-x0)[None,:]
y0m=y0%M; y1m=(y0+1)%M; x0m=x0%M; x1m=(x0+1)%M
def upsample(F):
    top=F[np.ix_(y0m,x0m)]*(1-fx)+F[np.ix_(y0m,x1m)]*fx
    bot=F[np.ix_(y1m,x0m)]*(1-fx)+F[np.ix_(y1m,x1m)]*fx
    return top*(1-fy)+bot*fy
def state(k):
    F=upsample(conv2(P,SIGMAX*k*k))
    t=np.quantile(F,0.45)
    return F<t
prev=None; worst=0; worstk=0; covs=[]
for i in range(201):
    k=i/200
    B=state(k); covs.append(B.mean())
    if prev is not None:
        fl=np.mean(B!=prev)
        if fl>worst: worst,worstk=fl,k
    prev=B
    if i in (0,50,100,150,200):
        Image.fromarray(np.where(B,0,255).astype(np.uint8)).save(
            os.path.join(os.path.dirname(__file__),f"journey_k{i:03d}.png"))
print("ink min/max:",min(covs),max(covs))
print(f"worst flip fraction per 1/200 step: {worst:.4f} at k={worstk:.3f}")
