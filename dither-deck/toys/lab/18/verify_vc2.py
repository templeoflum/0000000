# force-continue past swap-reversal: is 1098 a true local optimum?
import numpy as np, time, os
M=136; DENS=0.45; SIG_VC=1.9
rng=np.random.default_rng(18)
nmin=int(round(DENS*M*M))
r=int(np.ceil(3*SIG_VC)); ax=np.arange(-r,r+1)
yy,xx=np.meshgrid(ax,ax,indexing='ij')
k2=np.exp(-(xx**2+yy**2)/(2*SIG_VC*SIG_VC)); k2/=k2.sum()
Km=np.zeros((M,M)); Km[:2*r+1,:2*r+1]=k2; Km=np.roll(Km,(-r,-r),axis=(0,1))
H=np.fft.rfft2(Km)
def energy(P): return np.fft.irfft2(np.fft.rfft2(P.astype(np.float64))*H,s=(M,M))
P=np.zeros((M,M),dtype=np.int8); P.flat[rng.choice(M*M,nmin,replace=False)]=1
E=energy(P)
def totE(): return float((E[P==1]).sum())
t0=time.time()
log=[]
forced=0
mv=0
while mv<80000:
    Emin=np.where(P==1,E,-np.inf); flat_rm=int(np.argmax(Emin))
    ry,rx=flat_rm//M,flat_rm%M
    E=E-np.roll(Km,(ry,rx),axis=(0,1)); P[ry,rx]=0
    Emaj=np.where(P==0,E,np.inf); flat_ad=int(np.argmin(Emaj))
    ay,axx=flat_ad//M,flat_ad%M
    if flat_ad==flat_rm:
        P[ry,rx]=1; E=E+np.roll(Km,(ry,rx),axis=(0,1))
        # instead of stopping, force-swap the tightest cluster to the BEST void
        # that is not itself: remove again, find 2nd-best void
        E=E-np.roll(Km,(ry,rx),axis=(0,1)); P[ry,rx]=0
        Emaj=np.where(P==0,E,np.inf)
        Emaj[ry,rx]=np.inf
        flat_ad=int(np.argmin(Emaj)); ay,axx=flat_ad//M,flat_ad%M
        forced+=1
    P[ay,axx]=1; E=E+np.roll(Km,(ay,axx),axis=(0,1))
    mv+=1
    if mv%5000==0: log.append((mv,round(totE(),1)))
print("forced continuations:",forced)
print("energy trajectory:",log)
print("final E:",round(totE(),1),"time",round(time.time()-t0,1),"s")
from PIL import Image
UP=5
img=np.kron(P,np.ones((UP,UP),dtype=np.uint8))
Image.fromarray(np.where(img,0,255).astype(np.uint8)).save(os.path.join(os.path.dirname(__file__),"mask_forced.png"))
np.save(os.path.join(os.path.dirname(__file__),"mask136_forced.npy"),P)
