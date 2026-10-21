import numpy as np, os
from PIL import Image
d=os.path.dirname(os.path.abspath(__file__))
M=136; UP=5; S=M*UP
P=np.load(os.path.join(d,"mask136.npy")).astype(np.float64)
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
def upsample(F):
    top=F[np.ix_(y0m,x0m)]*(1-fx)+F[np.ix_(y0m,x1m)]*fx
    bot=F[np.ix_(y1m,x0m)]*(1-fx)+F[np.ix_(y1m,x1m)]*fx
    return top*(1-fy)+bot*fy
rngj=np.random.default_rng(7)
JIT=rngj.random((S,S))*1e-4
def state(k):
    sig=7.0*(k**2.0)
    F=upsample(conv2(P,sig))+JIT
    t=np.quantile(F,0.45)
    return F<t
for i in (0,25,50,75,100):
    B=state(i/100)
    Image.fromarray(np.where(B,0,255).astype(np.uint8)).save(os.path.join(d,f'final_k{i:03d}.png'))
    print(i/100,'ink',round(float(B.mean()),4),'sigma',round(7.0*(i/100)**2.5,3))
