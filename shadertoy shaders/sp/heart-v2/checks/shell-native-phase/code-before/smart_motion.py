"""Existing Heart Smart Param math, extracted unchanged; no runtime/storage imports."""
import math, threading
from motion import recipe_rate
PHI = (1 + 5 ** 0.5) / 2; E_ = math.e; PI = math.pi
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131]
FAMILIES = ["per-slot","unison","near-unison","harmonic","just intonation","septimal","undecimal","powers of 2","powers of 3",
            "cross-base 2v3","pendulum wave","fibonacci","lucas","coprime primes","prime stacks","CF approximants","metallic","near-phi","irrationals"]
RATIO_LIB = {"1:1":1.0,"1:2":0.5,"1:4":0.25,"2:3":2/3,"3:4":0.75,"4:5":0.8,"5:6":5/6,"3:5":0.6,"1/phi":1/PHI,"1/sqrt2":2**-0.5,"1/pi":1/PI,
             "1:3":1/3,"2:5":0.4,"5:8":0.625,"8:13":8/13,"3:2":1.5}
JI=[(1,1),(16,15),(9,8),(6,5),(5,4),(4,3),(45,32),(3,2),(8,5),(5,3),(15,8),(2,1)]
SEP=[(7,6),(7,5),(7,4),(8,7),(9,7),(10,7),(12,7),(14,9),(21,16),(49,48)]
UND=[(11,8),(11,6),(11,7),(11,9),(11,10),(13,8),(13,12),(13,7),(13,9),(13,11)]
CF=[(3,2),(22,7),(7,5),(333,106),(17,12),(355,113),(41,29),(103993,33102),(99,70),(239,169)]
IRR=[1/PHI,2**-0.5,1/PI,1/E_,3**-0.5,5**-0.5,PI/4,E_/PI,PI/E_]
def fibpair(k,a=1,b=1):
    for _ in range(k): a,b=b,a+b
    return a/b
def term(f,k):
    """catalog family f, term k → ratio (cycles per heart turn)"""
    k=max(k,0)
    if f==1: return 1.0
    if f==2: n=8+k; return (n+1)/n
    if f==3: return 1/(k+1)
    if f==4: p,q=JI[k%12]; return p/q
    if f==5: p,q=SEP[k%10]; return p/q
    if f==6: p,q=UND[k%10]; return p/q
    if f==7: return 2.0**-(k%12)
    if f==8: return 3.0**-(k%8)
    if f==9: a=1+k%4; b=1+(k//4)%3; return 2**a/3**b
    if f==10: return (8+k)/8
    if f==11: return fibpair(k)
    if f==12: return fibpair(k,2,1)
    if f==13: return 1/PRIMES[k%32]
    if f==14: j=k%31; return PRIMES[j]/PRIMES[j+1]
    if f==15: p,q=CF[k%10]; return p/q
    if f==16: n=1+k; return 1/((n+math.sqrt(n*n+4))/2)
    if f==17: return (1/PHI)*(1+0.013*k)
    if f==18: return IRR[k%9]
    return 1.0

def fract(x): return x-math.floor(x)

def bump(ph): return 0.5-0.5*math.cos(ph*2*PI)
def tri(ph): return 1-abs(2*fract(ph)-1)
def arc(a,b): return ((b-a+0.5)%1.0)-0.5           # shortest signed arc on the ring, b-a
class Slot:
    """one driven parameter. Phase is INTEGRATED (φ += x·dH) so any config change can be MORPHED:
    the effective config is a blend prev→target over morph seconds. Everything the output depends on
    is either blended linearly (x, lo, hi, manual, drive amount, shape weight) or unwrapped before
    blending (phase terms), so the value is continuous through every change."""
    def __init__(s,name,cyclic):
        s.name=name; s.cyclic=cyclic; s.ids={}; s.cfg={}; s.drive=False
        s.ownership_lock=threading.RLock();s.claim_epoch=0;s.claim_inflight=False;s.phase_checked=None
        s.phi=0.0; s.phi_fm=0.0; s.rot=0.0; s.prev=None; s.target=None; s.t0=0; s.dur=3.0
    def eff_cfg(s,g):
        """target 'physical' config from cfg+globals: x (cycles/turn), o, lo, hi, manual, shape, drive"""
        c=s.cfg; i=s.index; k=c.get('family_slot',i)*g['spread']+g['seed']
        recipe=g.get('relationship')
        r = recipe_rate(recipe,s.name,i) if recipe else (RATIO_LIB.get(c['ratio'],1.0) if g['pattern']==0 else term(g['pattern'],k))
        rf= RATIO_LIB.get(c['ratio'],1.0) if g['pattern']==0 else term(g['pattern'],k+1)
        m=c['mult']; m = math.copysign(1.0,m if m!=0 else 1) if abs(m)<1 else m
        speed=g.get('speed',1.)
        return {'x':speed*m*r,'xf':speed*rf,'o':c['offset'],'lo':c['lo'],'hi':c['hi'],'manual':c['manual'],'shape':float(c['shape']),'drive':1.0 if s.drive else 0.0,'depth':g['depth'],'fm':g['fm']}
    def retarget(s,g,now):
        t=s.eff_cfg(g)
        if not hasattr(s,'reset_pose'):s.reset_pose=s.cfg['manual']
        if s.target is None: s.prev=s.target=t; return
        if t!=s.target:
            s.prev=s.blend(now)
            # Inactive bounds have no contribution to output. Adopt the requested
            # range before fading a drive in, avoiding excursions through old limits.
            # A running or fading-out drive retains its continuous range morph.
            if s.prev['drive']==0.0:
                s.prev=dict(s.prev,lo=t['lo'],hi=t['hi'])
            s.target=t; s.t0=now      # morph FROM the current effective config
    def blend(s,now):
        if s.prev is None: return s.target
        u=1.0 if s.dur<=0 else min(1.0,(now-s.t0)/s.dur); u=0.5-0.5*math.cos(u*PI)   # smooth ease
        a,b=s.prev,s.target; e={k:a[k]+(b[k]-a[k])*u for k in a if k not in('o','manual')}
        e['o']=a['o']+arc(a['o'],b['o'])*u
        e['manual']=(a['manual']+arc(a['manual'],b['manual'])*u) if s.cyclic else (a['manual']+(b['manual']-a['manual'])*u)
        return e
    def step(s,dH,now):
        e=s.blend(now); s.phi+=e['x']*dH; s.phi_fm+=e['xf']*dH
        if s.drive:s._resting=False
        if s.cyclic and not getattr(s,'_resting',False): s.rot+=e['drive']*(1-e['shape'])*e['x']*dH     # the rotation ACTUALLY performed this frame (never blends a large number)
        return e
    def value(s,e):
        c=s.cfg
        ph=s.phi+e['o']
        if e['fm']>0: ph+=e['fm']*0.25*bump(s.phi_fm+0.37*s.index)
        a=e['drive']; w=e['shape']; depth=e['depth']; lo,hi,manual=e['lo'],e['hi'],e['manual']
        if s.cyclic:
            fmt=(e['fm']*0.25*bump(s.phi_fm+0.37*s.index)) if e['fm']>0 else 0.0
            sway=depth*(hi-lo)*bump(ph)
            return fract(manual + s.rot + a*((1-w)*fmt + w*sway))
        sh=(1-w)*tri(ph)+w*bump(ph)
        return manual + a*depth*((lo+(hi-lo)*sh)-manual)
