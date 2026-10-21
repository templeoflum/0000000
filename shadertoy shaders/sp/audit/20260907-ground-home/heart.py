#!/usr/bin/env python3
"""heart.py — THE HEART. External smart-param engine for Resolume Arena.
Law (kit ratio.js): φ = fract(H·m·r + o), H = heart turns (integrated from Arena BPM: 1 turn = 1 bar).
64-bit, deterministic, jump-free. Reads slot config from the clip's own params (Pattern/Seed/Spread/
Depth/FM + per-slot Ratio/Mult/Offset/Shape/Lo/Hi/Lock), takes over by switching the shader's Drive
toggles off, then writes the slot VALUES into Arena by parameter id every frame.
"""
import json, math, time, sys, threading, urllib.request, re, asyncio, queue, copy
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from concurrent.futures import ThreadPoolExecutor
from delivery import LatestValues
from motion import recipe_rate, animated_home, speed_value
BASE = "http://localhost:8080/api/v1"
FPS = 240.0                     # write faster than Arena renders so every render frame sees a fresh value (no clock beat)
TEMPO_ID = None
DRIVE_ALL = '--all' in sys.argv     # engine owns drive flags; --all = every slot driven (shader toggles are display-only once taken over)
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
        s.phi=0.0; s.phi_fm=0.0; s.rot=0.0; s.prev=None; s.target=None; s.t0=0; s.dur=3.0
    def eff_cfg(s,g):
        """target 'physical' config from cfg+globals: x (cycles/turn), o, lo, hi, manual, shape, drive"""
        c=s.cfg; i=s.index; k=i*g['spread']+g['seed']
        recipe=g.get('relationship')
        r = recipe_rate(recipe,s.name,i) if recipe else (RATIO_LIB.get(c['ratio'],1.0) if g['pattern']==0 else term(g['pattern'],k))
        rf= RATIO_LIB.get(c['ratio'],1.0) if g['pattern']==0 else term(g['pattern'],k+1)
        m=c['mult']; m = math.copysign(1.0,m if m!=0 else 1) if abs(m)<1 else m
        speed=g.get('speed',1.)
        return {'x':speed*m*r,'xf':speed*rf,'o':c['offset'],'lo':c['lo'],'hi':c['hi'],'manual':c['manual'],'shape':float(c['shape']),'drive':1.0 if s.drive else 0.0,'depth':g['depth'],'fm':g['fm']}
    def retarget(s,g,now):
        t=s.eff_cfg(g)
        if s.target is None: s.prev=s.target=t; return
        if t!=s.target:
            s.prev=s.blend(now); s.target=t; s.t0=now      # morph FROM the current effective config
    def blend(s,now):
        if s.prev is None: return s.target
        u=1.0 if s.dur<=0 else min(1.0,(now-s.t0)/s.dur); u=0.5-0.5*math.cos(u*PI)   # smooth ease
        a,b=s.prev,s.target; e={k:a[k]+(b[k]-a[k])*u for k in a if k not in('o','manual')}
        e['o']=a['o']+arc(a['o'],b['o'])*u
        e['manual']=(a['manual']+arc(a['manual'],b['manual'])*u) if s.cyclic else (a['manual']+(b['manual']-a['manual'])*u)
        return e
    def step(s,dH,now):
        e=s.blend(now); s.phi+=e['x']*dH; s.phi_fm+=e['xf']*dH
        if s.cyclic: s.rot+=e['drive']*(1-e['shape'])*e['x']*dH     # the rotation ACTUALLY performed this frame (never blends a large number)
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
ATOM_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"atoms.json")
def load_atoms():
    try: return json.load(open(ATOM_FILE))
    except Exception: return {}
ATOMS=load_atoms()
MOTION_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"motion.json")
try: MOTION=json.load(open(MOTION_FILE))
except Exception: MOTION={}
try: SWEETSPOTS=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"sweetspots.json")))
except Exception: SWEETSPOTS={}
def motion_key(clip): return f"{getattr(clip,'atom',None) or clip.name}:{clip.name}"
def motion_save(clip,key,value):
    if key=='speed':value=speed_value(value)
    MOTION.setdefault(motion_key(clip),{})[key]=copy.deepcopy(value)
    clip.g[key]=copy.deepcopy(value)
    tmp=MOTION_FILE+'.tmp'
    with open(tmp,'w') as f:json.dump(MOTION,f,indent=1)
    os.replace(tmp,MOTION_FILE)
    for sl in clip.slots:sl.retarget(clip.g,time.perf_counter())
ATOM_DIRTY=threading.Event()
def save_atoms(): ATOM_DIRTY.set()
def persist_atoms():
    while True:
        ATOM_DIRTY.wait(); time.sleep(0.15); ATOM_DIRTY.clear()
        try:
            data=json.dumps(ATOMS,indent=1)
            tmp=ATOM_FILE+'.tmp'
            with open(tmp,'w') as f: f.write(data)
            os.replace(tmp,ATOM_FILE)
        except Exception as exc: event(f"atom save failed: {exc}")
def atom_sections(cj):
    """(section name, params) for the clip's SP source and each SP effect that atoms.json knows"""
    v=cj.get('video') or {}; out=[]
    d=v.get('description')
    if d in ATOMS: out.append((d, v.get('sourceparams') or {}))
    for e in (v.get('effects') or []):
        if e.get('name') in ATOMS: out.append((e['name'], e.get('params') or {}))
    return out
def is_sp(cj):
    """an SP clip: carries ' Drive' slots itself, or is an ATOM listed in atoms.json (the heart holds its slot config)"""
    return any(k.endswith(' Drive') for k in allparams(cj)) or bool(atom_sections(cj))
def allparams(cj):
    """sourceparams + any clip EFFECT's params that carry SP slots (' Drive') — everything-SP:
    a native source (e.g. Feedback) becomes an SP clip via an SP Wire effect on the clip."""
    v=cj.get('video') or {}
    sp=dict(v.get('sourceparams') or {})
    for e in (v.get('effects') or []):
        pr=e.get('params') or {}
        if any(k.endswith(' Drive') for k in pr): sp.update(pr)
    return sp
def clip_schema(cj):
    groups=[('source',allparams(cj))]+atom_sections(cj)
    return tuple((section,n,p.get('id'),p.get('valuetype'),p.get('min'),p.get('max'),tuple(p.get('options') or []))
                 for section,pr in groups for n,p in pr.items() if isinstance(p,dict) and 'id' in p)

class Clip:
    """one connected SP clip: discovers slots from its sourceparams (+ SP effect params)"""
    def __init__(s,layer,col,cj):
        s.schema=clip_schema(cj)
        s.layer,s.col=layer,col; s.name=cj['name']['value']; sp=allparams(cj); s.sp=sp
        s.gids={k:sp[k]['id'] for k in ('Pattern','Seed','Spread','Depth','FM') if k in sp}
        names=[k[:-6] for k in sp if k.endswith(' Drive')]
        s.atom=None; acfg={}; s.asec={}
        if not names:
            secs=atom_sections(cj)
            if secs:
                s.atom=secs[0][0]                                  # the first section holds _global; every section contributes knobs
                for name,params in secs:
                    for n,p in params.items():
                        if n not in ATOMS[name] and isinstance(p,dict) and p.get('valuetype') in ('ParamRange','ParamFloat','ParamInt','ParamChoice'):
                            ATOMS[name][n]={'cyclic':False,'drive':False,'ratio':'1:4','mult':1,'offset':0,'shape':1,'lo':0,'hi':1}
                            save_atoms()
                    for n,cfg in ATOMS[name].items():
                        if n=='_global' or n in acfg or n not in params: continue
                        acfg[n]=cfg; s.asec[n]=name; sp[n]=params[n]  # the knob's live param (source or effect), by name
                names=list(acfg)
        s.slots=[]
        for i,n in enumerate(names):
            if s.atom:
                a=acfg[n]; sl=Slot(n, bool(a.get('cyclic'))); sl.index=i; sl.acfg=a
                sl.ids={'':sp[n]['id']}; sl.pmin=float(sp[n].get('min',0.0)); sl.pmax=float(sp[n].get('max',1.0))
                if sp[n].get('valuetype')=='ParamChoice':                 # a picker: the 0..1 signal walks the option list
                    sl.choices=list(sp[n].get('options') or []); sl.pmin=0.0; sl.pmax=1.0
                sl.shape_opts=['rotate','sway'] if sl.cyclic else ['loop','sway']
            else:
                sl=Slot(n, sp.get(n+' Shape',{}).get('options',[''])[0]=='rotate'); sl.index=i
                sl.ids={key:sp[n+(' '+key if key else '')]['id'] for key in ('','Drive','Lock','Ratio','Mult','Offset','Shape','Lo','Hi') if (n+(' '+key if key else '')) in sp}
            s.slots.append(sl)
        s.taken=False; s.history=[]; s.morph=3.0; s.home=None; s.arm=arm_default(); s.auto=0; s._auto_n=None
        sets=load_armsets().get(s.name,{})
        if '_last' in sets: s.arm=arm_from(sets['_last'])
        if not s.atom:
            for sl in s.slots: sl.shape_opts=sp[sl.name+' Shape'].get('options',['0','1'])
    def refresh(s,cj):
        sp=allparams(cj)
        if s.atom:
            G=ATOMS[s.atom].setdefault('_global',{'pattern':0,'seed':0,'spread':1,'depth':1.0,'fm':0.0})
            g={'pattern':int(G.get('pattern',0)),'seed':int(G.get('seed',0)),'spread':int(G.get('spread',1)),'depth':float(G.get('depth',1.0)),'fm':float(G.get('fm',0.0))}
            for name,params in atom_sections(cj):                     # refresh the live params of every section
                for n in params:
                    if n in s.asec and s.asec[n]==name: sp[n]=params[n]
            for sl in s.slots:
                n=sl.name; a=sl.acfg; span=max(sl.pmax-sl.pmin,1e-9)
                if hasattr(sl,'choices'): live=(sp[n].get('index',0)/max(len(sl.choices)-1,1)) if len(sl.choices)>1 else 0.0
                else: live=(float(sp[n]['value'])-sl.pmin)/span                     # the knob, normalised to the slot's 0..1 signal
                sl.cfg={'manual':sl.cfg.get('manual',live) if s.taken else live,'drive':sl.drive if s.taken else bool(a.get('drive',False)),
                        'ratio':a.get('ratio','1:1'),'mult':float(a.get('mult',1.0)),'offset':float(a.get('offset',0.0)),'shape':int(a.get('shape',1)),
                        'lo':float(a.get('lo',0.0)),'hi':float(a.get('hi',1.0)),'lock':bool(a.get('lock',False))}
            g.update(MOTION.get(motion_key(s),{})); s.g=g; now=time.perf_counter()
            for sl in s.slots: sl.dur=s.morph; sl.retarget(g,now)
            return
        g={'pattern':sp['Pattern']['index'] if 'Pattern' in sp else 11,'seed':int(sp['Seed']['value']) if 'Seed' in sp else 0,'spread':int(sp['Spread']['value']) if 'Spread' in sp else 1,
           'depth':sp['Depth']['value'] if 'Depth' in sp else 1.0,'fm':sp['FM']['value'] if 'FM' in sp else 0.0}
        for sl in s.slots:
            n=sl.name
            sl.cfg={'manual':sl.cfg.get('manual',sp[n]['value']) if s.taken else sp[n]['value'],
                    'drive':sl.drive if s.taken else sp[n+' Drive']['value'],'ratio':sp.get(n+' Ratio',{}).get('value','1:1'),'mult':sp.get(n+' Mult',{}).get('value',1.0),
                    'offset':sp.get(n+' Offset',{}).get('value',0.0),'shape':sp.get(n+' Shape',{}).get('index',1),'lo':sp.get(n+' Lo',{}).get('value',0.0),'hi':sp.get(n+' Hi',{}).get('value',1.0),'lock':sp.get(n+' Lock',{}).get('value',False)}
        if hasattr(s,'g') and s.g!=g:
            for k in g:
                if g[k]!=s.g[k]: event(f"{s.name}: {k} → {sp[k[0].upper()+k[1:]]['value'] if k in ('pattern','seed','spread') else g[k]}")
        for sl in s.slots:
            old=getattr(sl,'_cfg_prev',None)
            if old:
                for k in ('ratio','mult','offset','shape','lo','hi','lock'):
                    if old[k]!=sl.cfg[k]: event(f"{s.name}/{sl.name}: {k} → {sl.cfg[k]}")
            sl._cfg_prev=dict(sl.cfg)
        g.update(MOTION.get(motion_key(s),{})); s.g=g
        now=time.perf_counter()
        for sl in s.slots: sl.dur=s.morph; sl.retarget(g,now)
    def takeover(s,put):
        # remember the shader's Drive flags as OUR drive flags, then switch the shader's off so it shows manual (= our written value)
        for sl in s.slots:
            sl.drive=(True if DRIVE_ALL else sl.cfg['drive']) if not s.atom else sl.cfg['drive']   # atoms: their config says which knobs move
            if 'Drive' in sl.ids: put_http(sl.ids['Drive'],False)
        s.taken=True
        resume=RESUME.pop((s.layer+1,s.col+1),None)
        if resume:
            for sl in s.slots:
                old=next((x for x in resume['slots'] if x['name']==sl.name),None)
                if old:
                    sl.drive=old['drive']; sl.cfg['manual']=old['v']
                    sl.prev=None; sl.target=None; sl.retarget(s.g,time.perf_counter())
        h=load_homes().get(s.name)
        if h: s.home=h; event(f"{s.name}: home loaded")
        else: threading.Thread(target=set_home,args=(s,),daemon=True).start()

import random
def wcfg(clip,sl,key,v,snap):
    """write one slot config field: to its Arena id (slot shaders) or into the heart's atoms.json (atoms)"""
    if key in sl.ids: snap.setdefault(sl.ids[key],cur_val(sl.ids[key])); put_http(sl.ids[key],v); return
    k=key.lower()
    if key=='Shape' and isinstance(v,str): v=sl.shape_opts.index(v) if v in sl.shape_opts else int(float(v))
    if key in ('Lo','Hi','Mult','Offset'): v=float(v)
    snap.setdefault(f"cfg:{sl.name}:{k}",sl.acfg.get(k)); sl.acfg[k]=v; save_atoms()
def wglob(clip,key,v,snap):
    if key.lower() in ('speed','relationship'):
        motion_save(clip,key.lower(),v); return
    if key in clip.gids: snap.setdefault(clip.gids[key],cur_val(clip.gids[key])); put_http(clip.gids[key],v); return
    if not getattr(clip,'atom',None): return
    G=ATOMS[clip.atom].setdefault('_global',{}); k=key.lower()
    if key=='Pattern': v=FAMILIES.index(v) if isinstance(v,str) and v in FAMILIES else int(v)
    else: v=int(v) if key in ('Seed','Spread') else float(v)
    snap.setdefault(f"glob:{k}",G.get(k)); G[k]=v; save_atoms()
def slot_out(sl,v):
    """the slot's 0..1 signal in the knob's own units: a float in its range, or an option's name for a picker"""
    if hasattr(sl,'choices') and sl.choices: return sl.choices[min(len(sl.choices)-1,max(0,int(round(v*(len(sl.choices)-1)))))]
    return (sl.pmin+v*(sl.pmax-sl.pmin)) if hasattr(sl,'pmin') else v
def wval(sl,v):
    """write the slot's VALUE in the knob's own units"""
    put_http(sl.ids[''], slot_out(sl,v))
def cur_val(pid): return json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{pid}",timeout=1)).get('value')
def undo_snap(clip,snap):
    for k,v in snap.items():
        if isinstance(k,str) and k.startswith('cfg:'):
            _,name,key=k.split(':'); [setattr(x,'acfg',{**x.acfg,key:v}) or ATOMS[clip.atom].__setitem__(name,x.acfg) for x in clip.slots if x.name==name]
        elif isinstance(k,str) and k.startswith('glob:'): ATOMS[clip.atom]['_global'][k[5:]]=v
        else: put_http(int(k) if isinstance(k,str) else k,v)
    save_atoms()
MULTS=[1,1,1,1,1,2,-1,-1]          # bias slow; sign = direction
CATS=["timing","motion","range","drive","look"]
GLOBAL=["pattern","timing"]
ARM_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"armsets.json")
def save_last(c):
    sets=load_armsets(); sets.setdefault(c.name,{})['_last']=arm_json(c.arm); json.dump(sets,open(ARM_FILE,"w"),indent=1)
_AS={"t":0,"v":{}}
def load_armsets_cached():
    if time.time()-_AS["t"]>1: _AS["t"]=time.time(); _AS["v"]=load_armsets()
    return _AS["v"]
def load_armsets():
    try: return json.load(open(ARM_FILE))
    except Exception: return {}
def fire(clip,seed=None,arm=None,respect_locks=True):
    """Fire every ARMED cell of the clip's shuffle matrix; write results into Arena (panel reflects). One snapshot → one undo."""
    rng=random.Random(seed); snap={}; before=capture_state(clip)
    def cur(pid): return json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{pid}",timeout=1)).get('value')
    def w(pid,v): snap.setdefault(pid,cur(pid)); put_http(pid,v)
    g=clip.gids
    if arm is None: arm=clip.arm
    fired=[]
    if 'pattern' in arm['global']: wglob(clip,'Relationship',None,{}); wglob(clip,'Pattern',FAMILIES[rng.randrange(1,19)],snap); fired.append('pattern')
    if 'timing' in arm['global']: wglob(clip,'Seed',str(rng.randrange(32)),snap); wglob(clip,'Spread',str(rng.choice([1,1,1,2,2,3,4])),snap); fired.append('seed/spread')
    for sl in clip.slots:
        if respect_locks and sl.cfg.get('lock'): continue      # 🔒 locked axes are untouchable
        cats=arm['slots'].get(sl.name,set())
        if not cats: continue
        if 'timing' in cats: wcfg(clip,sl,'Ratio',rng.choice(list(RATIO_LIB.keys())),snap)
        if 'motion' in cats: wcfg(clip,sl,'Mult',float(rng.choice(MULTS)),snap); wcfg(clip,sl,'Offset',rng.random(),snap); wcfg(clip,sl,'Shape',rng.choice(sl.shape_opts),snap)
        if 'range' in cats:
            low,high=sorted((sl.cfg['lo'],sl.cfg['hi']))
            width=(high-low)*rng.uniform(0.4,1.0); low=rng.uniform(low,high-width)
            wcfg(clip,sl,'Lo',low,snap); wcfg(clip,sl,'Hi',low+width,snap)
        if 'drive' in cats: sl.drive=rng.random()>0.35; sl.retarget(clip.g,time.perf_counter())
        if 'look' in cats:
            sl.cfg['manual']=rng.uniform(min(sl.cfg['lo'],sl.cfg['hi']),max(sl.cfg['lo'],sl.cfg['hi'])); sl.retarget(clip.g,time.perf_counter())
            if not sl.drive: snap.setdefault(sl.ids[''],cur(sl.ids[''])); wval(sl,sl.cfg['manual'])
        fired.append(f"{sl.name}[{''.join(c[0] for c in CATS if c in cats)}]")
    if not fired: event(f"{clip.name}: nothing armed"); return
    clip.history.append(before); clip.history=clip.history[-20:]
    event(f"{clip.name}: shuffle "+" ".join(fired))
IRRATIONAL_RATIOS={'1/phi','1/sqrt2','1/pi'}
def timing_fire(clip,mode,seed=None):
    """The timing triangle: ⊙ unison baseline · ♩ harmonic shuffle · ∞ irrational shuffle.
    Touches ONLY the timing fabric (ratio/mult/offset/shape) — never ranges, drives, or values.
    Sets Pattern → per-slot so slot ratios rule. The Slot integrator morphs every change smoothly."""
    rng=random.Random(seed); snap={}; before=capture_state(clip)
    def cur(pid): return json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{pid}",timeout=1)).get('value')
    def w(pid,v): snap.setdefault(pid,cur(pid)); put_http(pid,v)
    harmonic=[k for k in RATIO_LIB.keys() if k not in IRRATIONAL_RATIOS]
    irr=[k for k in RATIO_LIB.keys() if k in IRRATIONAL_RATIOS]
    wglob(clip,'Relationship',None,{}); wglob(clip,'Pattern','per-slot',snap)
    for sl in clip.slots:
        if sl.cfg.get('lock'): continue
        W=lambda key,v,sl=sl: wcfg(clip,sl,key,v,snap)
        if mode=='unison':
            W('Ratio','1:1'); W('Mult',1.0); W('Offset',0.0)
            W('Shape',sl.shape_opts[0] if sl.cyclic else sl.shape_opts[-1])
        elif mode=='harmonic':
            W('Ratio',rng.choice(harmonic)); W('Mult',float(rng.choice([1,1,1,2,-1]))); W('Offset',rng.choice([0.0,0.25,0.5,0.75])); W('Shape',rng.choice(sl.shape_opts))
        else:
            W('Ratio',rng.choice(irr)); W('Mult',float(rng.choice([1,1,-1,2]))); W('Offset',rng.random()); W('Shape',rng.choice(sl.shape_opts))
    clip.history.append(before); clip.history=clip.history[-20:]
    event(f"{clip.name}: timing {'⊙ unison' if mode=='unison' else ('♩ '+mode if mode=='harmonic' else '∞ '+mode)}")
def arm_default(): return {'global':set(),'slots':{}}
def arm_json(a): return {'global':sorted(a['global']),'slots':{k:sorted(v) for k,v in a['slots'].items() if v}}
def arm_from(j): return {'global':set(j.get('global',[])),'slots':{k:set(v) for k,v in j.get('slots',{}).items()}}
HOME_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"home.json")
def load_homes():
    try: return json.load(open(HOME_FILE))
    except Exception: return {}
def set_home(clip):
    vals=capture_state(clip)
    vals['sweet_home']=True
    homes=load_homes(); homes[clip.name]=vals; json.dump(homes,open(HOME_FILE,"w"),indent=1); clip.home=vals; event(f"{clip.name}: home set")
def axis_good_set(clip,name):
    homes=load_homes(); h=homes.get(clip.name) or capture_state(clip)
    if h.get('version')!=2: h=capture_state(clip)
    h['slots'][name]=capture_state(clip)['slots'][name]
    homes[clip.name]=h; json.dump(homes,open(HOME_FILE,"w"),indent=1); clip.home=h
    event(f"{clip.name}/{name}: good saved")
def axis_good_go(clip,name):
    h=clip.home or load_homes().get(clip.name)
    if not h: return
    if h.get('version')==2:
        if name in h['slots']: apply_state(clip,{'version':2,'slots':{name:h['slots'][name]}},f"{name} return")
        return
    sl=next(x for x in clip.slots if x.name==name)
    ids={str(pid) for k,pid in sl.ids.items() if k!='Drive'}
    apply_state(clip,{k:v for k,v in h.items() if k in ids or k in ('manual:'+name,'drive:'+name)},f"{name} return")
def go_home(clip):
    h=clip.home or load_homes().get(clip.name)
    before=capture_state(clip)
    if h and h.get('sweet_home'): target=h
    else:
        # Profiles are edited while refining instruments; a Home press uses the latest bindings.
        try:
            with open(os.path.join(os.path.dirname(__file__),'sweetspots.json')) as f: profiles=json.load(f)
        except (OSError,ValueError): profiles=SWEETSPOTS
        profile=profiles.get(clip.atom or clip.name)
        if not profile:
            # Unrefined/new controls stay still; only familiar motion axes get a modest starting window.
            candidates={'Turn','Spin','Tumble','Sway','Bob','Travel','Drift','Hue','Weight','Slant','Amount','Flicker'}
            bindings={}
            for sl in clip.slots:
                if sl.name not in candidates or hasattr(sl,'choices'):continue
                v=before['slots'][sl.name]['pose']%1 if sl.cyclic else before['slots'][sl.name]['pose']
                bindings[sl.name]={'center':v,'range':[max(0,v-.04),min(1,v+.04)],'cyclic':sl.cyclic}
            profile={'speed':.25,'bindings':bindings}
        if not profile['bindings']:event(f"{clip.name}: set a motion Home in Edit first");return
        profile=copy.deepcopy(profile)
        for sl in clip.slots:
            option=profile.get('choices',{}).get(sl.name)
            choices=getattr(sl,'choices',[])
            if option in choices:
                profile.setdefault('static',{})[sl.name]=choices.index(option)/max(1,len(choices)-1)
        target=animated_home(before,profile)
    clip.history.append(before);clip.history=clip.history[-20:]
    apply_state(clip,target,"animated Home")
PRESET_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"presets.json")
def load_presets():
    try: return json.load(open(PRESET_FILE))
    except Exception: return {}
_PS={"t":0,"v":{}}
def load_presets_cached():
    if time.time()-_PS["t"]>1: _PS["t"]=time.time(); _PS["v"]=load_presets()
    return _PS["v"]
def capture_state(clip):
    """Portable engine state, keyed by semantic slot names instead of transient Arena IDs."""
    return {'version':2,'global':dict({'speed':1.,'relationship':None},**copy.deepcopy(clip.g)), 'slots':{
        sl.name:{'config':copy.deepcopy(sl.cfg),'drive':sl.drive,
                 'pose':sl.cfg['manual']+sl.rot if sl.cyclic else sl.cfg['manual']}
        for sl in clip.slots}}
def apply_state(clip,h,label="preset"):
    if h.get('version')==2:
        if 'global' in h:
            wglob(clip,'Relationship',h['global'].get('relationship'),{})
            wglob(clip,'Speed',h['global'].get('speed',1.),{})
        for k,v in h.get('global',{}).items():
            wglob(clip,'FM' if k=='fm' else k.capitalize(),FAMILIES[int(v)] if k=='pattern' else v,{})
        clip.g.update(h.get('global',{}))
        for sl in clip.slots:
            saved=h.get('slots',{}).get(sl.name)
            if saved is None: continue
            cfg=saved['config']
            for k in ('ratio','mult','offset','shape','lo','hi','lock'):
                if k in cfg: wcfg(clip,sl,k.capitalize(),sl.shape_opts[int(cfg[k])] if k=='shape' else cfg[k],{})
            sl.cfg.update(cfg); sl.drive=bool(saved['drive'])
            sl.cfg['manual']=((saved['pose']-sl.rot)%1.0) if sl.cyclic else saved['pose']
            sl.retarget(clip.g,time.perf_counter())
    else:
        # Legacy homes remain readable; only allow IDs belonging to this live clip.
        valid={pid for pid in clip.gids.values()}|{pid for sl in clip.slots for pid in sl.ids.values()}
        for k,v in h.items():
            if k.startswith('manual:'):
                for sl in clip.slots:
                    if sl.name==k[7:]: sl.cfg['manual']=((v-sl.rot)%1.0) if sl.cyclic else v
            elif k.startswith('drive:'):
                for sl in clip.slots:
                    if sl.name==k[6:]: sl.drive=bool(v)
            elif k.isdigit() and int(k) in valid: put_http(int(k),v)
        for sl in clip.slots: sl.retarget(clip.g,time.perf_counter())
    event(f"{clip.name}: → {label} (morphing)")
def preset_save(clip,pad,name=None):
    ps=load_presets(); state=capture_state(clip)
    state['label']=(str(name).strip()[:80] if name else '') or ps.get(clip.name,{}).get(str(pad),{}).get('label',f'Variation {pad}')
    ps.setdefault(clip.name,{})[str(pad)]=state
    json.dump(ps,open(PRESET_FILE,"w"),indent=1); _PS["t"]=0; event(f"{clip.name}: preset {pad} saved")
def preset_go(clip,pad):
    h=load_presets().get(clip.name,{}).get(str(pad))
    if not h: event(f"{clip.name}: preset {pad} empty"); return
    apply_state(clip,h,f"preset {pad}")
def preset_mom(clip,pad,on):
    held=getattr(clip,'_held_presets',{})
    key=str(pad)
    if on:
        h=load_presets().get(clip.name,{}).get(key)
        if not h or key in held: return
        if not held: clip._return_state=capture_state(clip)
        held[key]=copy.deepcopy(h); clip._held_presets=held
        apply_state(clip,h,f"visit {pad}")
    elif key in held:
        was_top=key==next(reversed(held)); del held[key]
        if was_top: apply_state(clip,next(reversed(held.values())) if held else clip._return_state,"return")
        if not held: clip._return_state=None

def undo(clip):
    if not clip.history: return
    snap=clip.history.pop()
    if snap.get('version')==2: apply_state(clip,snap,"undo")
    else: undo_snap(clip,snap)
    event(f"{clip.name}: undo")
def put_http(pid,v):
    req=urllib.request.Request(f"{BASE}/parameter/by-id/{pid}",data=json.dumps({"value":v}).encode(),method="PUT",headers={"Content-Type":"application/json"})
    urllib.request.urlopen(req,timeout=1).read()
def connect_clip(layer,col):
    req=urllib.request.Request(f"{BASE}/composition/layers/{layer}/clips/{col}/connect",data=b'',method="POST")
    urllib.request.urlopen(req,timeout=1).read()
OUT=LatestValues()
RESCAN=threading.Event()
RESCAN_L=threading.Event()
PUSHED={}
CLIPS={}
H_now=[0.0]
LAYERS=[]   # [{i,name,id_opacity,id_bypass,opacity,clip}]
FX={}       # key "L6/3" or "C/2" → Effect
FX_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"fx.json")
class Effect:
    """an Arena effect with an ENVELOPE (0→1) the engine owns, written to its Opacity. attack/release, modes, quantize, reverse-on-repress."""
    def __init__(s,key,scope,layer,idx,name,id_opacity,id_bypass,opmax):
        s.key,s.scope,s.layer,s.idx,s.name=key,scope,layer,idx,name; s.id_opacity=id_opacity; s.id_bypass=id_bypass; s.opmax=opmax
        s.colors={}
        s.env=0.0; s.target=0.0; s.held=False; s.pending=None; s.hold_until=None; s.last_written=None
        s.cfg={"attack":0.5,"release":1.0,"mode":"latch","quant":0,"hold":0.0,"key":"","bypass0":True,"bind":None}
        cf=load_fx().get(key); 
        if cf: s.cfg.update(cf)
    def press(s,H):
        c=s.cfg; m=c["mode"]
        act={"latch": (lambda: setattr(s,"target",0.0 if (s.target if abs(s.target-s.env)>1e-6 else s.env)>0.5 else 1.0)),
             "momentary": (lambda: (setattr(s,"held",True),setattr(s,"target",1.0))),
             "oneshot": (lambda: (setattr(s,"env",1.0),setattr(s,"target",1.0),setattr(s,"last_written",None),setattr(s,"hold_until",H*STATE['bars']+c["hold"])))}[m]   # FLASH to full, then spring back
        if c["quant"]>0: s.pending=(math.floor(H*STATE['bars']/c["quant"])+1)*c["quant"]; s.pending_act=act
        else: act()
    def release(s):
        if s.cfg["mode"]=="momentary": s.held=False; s.target=0.0; s.pending=None
    def step(s,dt,H):
        c=s.cfg
        if s.pending is not None and H*STATE['bars']>=s.pending: s.pending=None; s.pending_act()
        if c["mode"]=="oneshot" and s.hold_until is not None and H*STATE['bars']>=s.hold_until: s.target=0.0; s.hold_until=None
        if s.last_written is None:   # forced write (a flash)
            v=s.env*s.opmax
            if c["bypass0"] and s.id_bypass and getattr(s,'bypassed',False) and v>0.0005: put(s.id_bypass,False); s.bypassed=False
            put(s.id_opacity,v); s.last_written=v
        if abs(s.target-s.env)<1e-6: return
        rate=dt/max(0.01,c["attack"] if s.target>s.env else c["release"])
        s.env=min(s.target,s.env+rate) if s.target>s.env else max(s.target,s.env-rate)
        v=s.env*s.opmax
        if s.last_written is None or abs(v-s.last_written)>1e-4:
            if c["bypass0"] and s.id_bypass and getattr(s,'bypassed',False) and v>0.0005: put(s.id_bypass,False); s.bypassed=False   # un-bypass BEFORE the first non-zero write
            put(s.id_opacity,v); s.last_written=v
            if c["bypass0"] and s.id_bypass and v<=0.0005 and not getattr(s,'bypassed',False): put(s.id_bypass,True); s.bypassed=True
def load_fx():
    try: return json.load(open(FX_FILE))
    except Exception: return {}
def save_fx():
    json.dump({k:e.cfg for k,e in FX.items()},open(FX_FILE,"w"),indent=1)
def discover_fx(comp):
    seen=set()
    def add(scope,layer,effects):
        for j,e in enumerate(effects):
            if e.get('name')=='Transform' or 'Opacity' not in e.get('params',{}): continue
            key=f"{scope}{layer or ''}/{j+1}"; seen.add(key)
            op=e['params']['Opacity']; byp=e.get('bypassed',{}).get('id')
            if key in FX and FX[key].id_opacity!=op['id']: del FX[key]
            if key not in FX:
                fx=FX[key]=Effect(key,scope,layer,j+1,e.get('display_name',e['name']),op['id'],byp,op.get('max',1.0))
                cur=0.0 if e.get('bypassed',{}).get('value') else op['value']/max(1e-6,op.get('max',1.0))   # ADOPT current state: never write on discovery
                fx.env=cur; fx.target=1.0 if cur>0.5 else 0.0; fx.last_written=cur*fx.opmax
                if fx.target!=fx.env: fx.target=fx.env   # hold wherever it is until pressed
                fx.bypassed=bool(e.get('bypassed',{}).get('value'))
            else: FX[key].name=e.get('display_name',e['name']); FX[key].id_opacity=op['id']; FX[key].id_bypass=byp
            FX[key].colors={n:{'id':p['id'],'value':p['value']} for n,p in e.get('params',{}).items() if isinstance(p,dict) and p.get('valuetype')=='ParamColor'}
    add("C",None,comp['video']['effects'])
    for i,l in enumerate(comp['layers']): add("L",i+1,l['video']['effects'])
    for k in list(FX):
        if k not in seen: del FX[k]                     # (pid, value) → Arena over one persistent WebSocket
def put(pid,v):
    OUT.put((pid,v))
def ws_writer():
    async def run():
        while True:
            reader = None
            try:
                async with websockets.connect("ws://localhost:8080/api/v1",max_size=None) as ws:
                    STATE["arena_connected"]=True
                    async def drain():
                        async for m in ws:
                            try:
                                obj=json.loads(m)
                                if isinstance(obj,dict) and 'layers' in obj:
                                    PUSHED["comp"]=obj; RESCAN.set()
                            except (ValueError,TypeError): pass
                    reader=asyncio.create_task(drain())
                    while not reader.done():
                        for pid,v in OUT.take(64):
                            await ws.send(json.dumps({"action":"set","parameter":f"/parameter/by-id/{pid}","value":v}))
                        await asyncio.sleep(1/240)
                    await reader
            except Exception as e:
                print("[heart] ws writer reconnect:",e,flush=True)
            finally:
                if reader:
                    reader.cancel()
                    await asyncio.gather(reader,return_exceptions=True)
                STATE["arena_connected"]=False; OUT.clear(); RESCAN.set()
            await asyncio.sleep(1)
    asyncio.new_event_loop().run_until_complete(run())
# ── status page: the seed of the control surface ──
STATE={"H":0,"bpm":0,"fps":0,"worst":0,"clips":[],"events":[],"bars":8,"hold":False,"arena_connected":False}   # bars per heart-turn (surface control)
SURFACE_FILE=os.path.join(os.path.dirname(__file__),'surface.json')
try:
    with open(SURFACE_FILE) as f: STATE['surface']=json.load(f)
except (OSError,ValueError): STATE['surface']={}
MUTATIONS=ThreadPoolExecutor(max_workers=1,thread_name_prefix='heart-actions')
WATCHERS=set()
def event(msg):
    STATE["events"].append(f"{time.strftime('%H:%M:%S')} {msg}"); STATE["events"]=STATE["events"][-40:]; print("[heart]",msg,flush=True)
PAGE=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"status.html")).read()
class H(SimpleHTTPRequestHandler):
    def do_GET(s):
        page=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"status.html")).read()
        s.send_response(200); s.send_header("Content-Type","text/html"); s.end_headers(); s.wfile.write(page.encode())
    def log_message(s,*a): pass
def status_server():
    threading.Thread(target=lambda: HTTPServer(("127.0.0.1",8765),H).serve_forever(),daemon=True).start()
    async def run():
        async def handler(ws):
            owned_holds={}; owned_fx=set()
            WATCHERS.add(ws); print(f"[heart] surface connected ({len(WATCHERS)})",flush=True)
            try:
                async for m in ws:
                    print("[heart] surface cmd:",m[:120],flush=True)
                    try:
                        d=json.loads(m)
                        if d['cmd']=='fx_color':
                            fx=FX[d['key']]; color=fx.colors[d['name']]; value=str(d['value'])
                            if len(value)!=7 or value[0]!='#' or any(ch not in '0123456789abcdefABCDEF' for ch in value[1:]): raise ValueError('Invalid color')
                            color['value']=value+'ff'; put(color['id'],color['value']); continue
                        if d['cmd']=='fx_amount':
                            fx=FX[d['key']]; value=float(d['value'])
                            if not math.isfinite(value): raise ValueError('Invalid amount')
                            fx.pending=None; fx.hold_until=None; fx.target=max(0.,min(1.,value)); continue
                        if d['cmd']=='fx_press': FX[d['key']].press(H_now[0]); owned_fx.add(d['key']); continue
                        if d['cmd']=='fx_release': FX[d['key']].release(); owned_fx.discard(d['key']); continue
                        if d['cmd']=='fx_cfg': FX[d['key']].cfg.update(d['cfg']); save_fx(); continue
                        if d['cmd']=='opacity':
                            L=next(x for x in LAYERS if x['i']==d['layer']); L['opacity']=float(d['value']); L['_hold']=time.time(); put(L['id_opacity'],float(d['value'])); continue
                        if d['cmd']=='bypass':
                            L=next(x for x in LAYERS if x['i']==d['layer']); L['bypass']=bool(d['on']); put_http(L['id_bypass'],bool(d['on'])); continue
                        if d['cmd']=='surface_cfg':
                            STATE['surface'].update(d['value'])
                            tmp=SURFACE_FILE+'.tmp'
                            with open(tmp,'w') as f: json.dump(STATE['surface'],f,indent=2)
                            os.replace(tmp,SURFACE_FILE); continue
                        if d['cmd']=='hold': STATE['hold']=bool(d['on']); continue
                        if d['cmd']=='bars': STATE['bars']=max(0.25,float(d['bars'])); event(f"heart: 1 turn = {STATE['bars']:g} bars"); continue
                        if d['cmd']=='clip_nav':
                            L=next(x for x in LAYERS if x['i']==d['layer']); cols=[c['col'] for c in L.get('clips',[])]
                            if cols:
                                cur=L.get('ccol',0)
                                if d['dir']=='rand': nc=random.choice([c for c in cols if c!=cur] or cols)
                                else:
                                    i=cols.index(cur) if cur in cols else (-1 if d['dir']=='next' else 0)
                                    nc=cols[(i+(1 if d['dir']=='next' else -1))%len(cols)]
                                await asyncio.get_event_loop().run_in_executor(MUTATIONS,connect_clip,d['layer'],nc)
                            continue
                        if d['cmd']=='launch':                      # launch a clip by name: the surface sends its layer + column
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,connect_clip,int(d['layer']),int(d['col'])); continue
                        if d['cmd']=='autopilot':
                            L=next(x for x in LAYERS if x['i']==d['layer'])
                            if L.get('id_ap'):
                                L['ap']=3 if d['on'] else 0
                                await asyncio.get_event_loop().run_in_executor(MUTATIONS,put_http,L['id_ap'],"Play Random Clip" if d['on'] else "Off")
                                event(f"L{d['layer']}: autopilot {'random' if d['on'] else 'off'}")
                            continue
                        key=(d['layer']-1,d['col']-1); c=CLIPS.get(key)
                        if not c: continue
                        if d['cmd']=='fire': await asyncio.get_event_loop().run_in_executor(MUTATIONS,fire,c,d.get('seed'))
                        elif d['cmd']=='arm':
                            a=c.arm
                            if d.get('slot')=='global': tgt=a['global']
                            else: tgt=a['slots'].setdefault(d['slot'],set())
                            (tgt.add if d['on'] else tgt.discard)(d['cat']); save_last(c)
                        elif d['cmd']=='arm_row':
                            if d['slot']=='global': c.arm['global']=set(GLOBAL) if d['on'] else set()
                            else: c.arm['slots'][d['slot']]=set(CATS) if d['on'] else set()
                            save_last(c)
                        elif d['cmd']=='arm_col':
                            if d['cat'] in CATS:
                                for sl in c.slots: (c.arm['slots'].setdefault(sl.name,set()).add if d['on'] else c.arm['slots'].setdefault(sl.name,set()).discard)(d['cat'])
                            if d['cat'] in GLOBAL: (c.arm['global'].add if d['on'] else c.arm['global'].discard)(d['cat'])
                            save_last(c)
                        elif d['cmd']=='arm_clear': c.arm=arm_default(); save_last(c)
                        elif d['cmd']=='armset_save': sets=load_armsets(); sets.setdefault(c.name,{})[d['name']]=arm_json(c.arm); json.dump(sets,open(ARM_FILE,"w"),indent=1); event(f"{c.name}: arm set '{d['name']}' saved")
                        elif d['cmd']=='armset_recall': c.arm=arm_from(load_armsets().get(c.name,{}).get(d['name'],{})); save_last(c); event(f"{c.name}: arm set '{d['name']}'")
                        elif d['cmd']=='armset_delete': sets=load_armsets(); sets.get(c.name,{}).pop(d['name'],None); json.dump(sets,open(ARM_FILE,"w"),indent=1)
                        elif d['cmd']=='auto': c.auto=float(d['bars']); c._auto_n=None; event(f"{c.name}: auto shuffle every {c.auto:g} bars" if c.auto else f"{c.name}: auto off")
                        elif d['cmd']=='undo': await asyncio.get_event_loop().run_in_executor(MUTATIONS,undo,c)
                        elif d['cmd']=='drive': 
                            sl=[x for x in c.slots if x.name==d['slot']][0]; sl.drive=bool(d['on']); event(f"{c.name}/{sl.name}: drive {'on' if sl.drive else 'off'}"); sl.retarget(c.g,time.perf_counter())
                        elif d['cmd']=='morph': c.morph=float(d['seconds']); event(f"{c.name}: morph {c.morph:.1f}s")
                        elif d['cmd']=='home_set': await asyncio.get_event_loop().run_in_executor(MUTATIONS,set_home,c)
                        elif d['cmd']=='home': await asyncio.get_event_loop().run_in_executor(MUTATIONS,go_home,c)
                        elif d['cmd']=='speed': await asyncio.get_event_loop().run_in_executor(MUTATIONS,motion_save,c,'speed',speed_value(d['value']))
                        elif d['cmd']=='choice':
                            sl=next(x for x in c.slots if x.name==d['slot']); options=getattr(sl,'choices',[])
                            if d['option'] not in options: raise ValueError('Unknown option')
                            c.history.append(capture_state(c)); c.history=c.history[-20:]
                            sl.drive=False; sl.cfg['manual']=options.index(d['option'])/max(1,len(options)-1); sl.prev=None
                        elif d['cmd']=='manual':
                            sl=[x for x in c.slots if x.name==d['slot']][0]; sl.cfg['manual']=float(d['value']); sl.retarget(c.g,time.perf_counter())
                        elif d['cmd']=='preset_save': await asyncio.get_event_loop().run_in_executor(MUTATIONS,preset_save,c,d['pad'],d.get('name'))
                        elif d['cmd']=='preset_go': await asyncio.get_event_loop().run_in_executor(MUTATIONS,preset_go,c,d['pad'])
                        elif d['cmd']=='preset_mom':
                            hk=(d['layer'],d['col'],d['pad'])
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,preset_mom,c,d['pad'],bool(d['on']))
                            if d['on']: owned_holds[hk]=c
                            else: owned_holds.pop(hk,None)
                        elif d['cmd']=='fire_cat':
                            cat=d['cat']
                            if cat=='all': a={'global':{'pattern','timing'},'slots':{sl.name:set(CATS) for sl in c.slots}}
                            elif cat=='pattern': a={'global':{'pattern'},'slots':{}}
                            elif cat=='timing': a={'global':{'timing'},'slots':{sl.name:{'timing'} for sl in c.slots}}
                            else: a={'global':set(),'slots':{sl.name:{cat} for sl in c.slots}}
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda cc=c,aa=a: fire(cc,None,aa))
                        elif d['cmd']=='fire_slot':
                            a={'global':set(),'slots':{d['slot']:set(CATS)}}
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda cc=c,aa=a: fire(cc,None,aa,False))
                        elif d['cmd']=='slot_cfg':
                            sl=[x for x in c.slots if x.name==d['slot']][0]
                            v=bool(d['value']) if d['key']=='Lock' else d['value']
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda: wcfg(c,sl,d['key'],v,{}))
                        elif d['cmd']=='global_cfg':
                            if d['key'] in ('Pattern','Seed','Spread'): await asyncio.get_event_loop().run_in_executor(MUTATIONS,motion_save,c,'relationship',None)
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda: wglob(c,d['key'],d['value'],{}))
                        elif d['cmd']=='timing':
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,timing_fire,c,d['mode'])
                        elif d['cmd']=='good_set': await asyncio.get_event_loop().run_in_executor(MUTATIONS,axis_good_set,c,d['slot'])
                        elif d['cmd']=='good_go': await asyncio.get_event_loop().run_in_executor(MUTATIONS,axis_good_go,c,d['slot'])
                    except Exception as e: print("[heart] cmd error:",e,flush=True)
            finally:
                WATCHERS.discard(ws)
                for (_,_,pad),c in list(owned_holds.items()):
                    try: await asyncio.get_event_loop().run_in_executor(MUTATIONS,preset_mom,c,pad,False)
                    except Exception: pass
                for key in owned_fx:
                    if key in FX: FX[key].release()
        async with websockets.serve(handler,"127.0.0.1",8766):
            while True:
                msg=json.dumps(STATE)
                for w in list(WATCHERS):
                    try: await w.send(msg)
                    except Exception: WATCHERS.discard(w)
                await asyncio.sleep(1/15)
    asyncio.new_event_loop().run_until_complete(run())
def get_comp(): return json.load(urllib.request.urlopen(BASE+"/composition",timeout=2))
def get_clip(li,ci): return json.load(urllib.request.urlopen(f"{BASE}/composition/layers/{li+1}/clips/{ci+1}",timeout=2))
def get_bpm(): return json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{TEMPO_ID}",timeout=2))["value"]

# ── clip size follows the composition (2026-09-02): generative clips keep the resolution they were
#    created at; a comp resize (screen change) leaves them mismatched and containment fails. Arena
#    re-derives the other dimension on each write (aspect lock), so write height, then width, verify.
def match_clip_sizes(comp):
    try:
        W=comp['video']['width']['value']; H=comp['video']['height']['value']; n=0
        for attempt in range(3):
            bad=0
            for l in comp['layers']:
                for cl in l['clips']:
                    v=cl.get('video')
                    if not v or (v['width']['value']==W and v['height']['value']==H): continue
                    bad+=1; put_http(v['height']['id'],H); time.sleep(0.05); put_http(v['width']['id'],W); time.sleep(0.05); n+=1
            if not bad: break
            time.sleep(0.4); comp=get_comp()
        if n: event(f"comp {int(W)}x{int(H)}: resized {n} clip(s) to match")
    except Exception as e: event(f"match_clip_sizes: {e}")

RESUME={}
if os.environ.get('SP_RESUME_STATUS'):
    with open(os.environ['SP_RESUME_STATUS']) as f: resume=json.load(f)
    RESUME={(c['layer'],c['col']):c for c in resume['clips']}
    STATE['bars']=resume.get('bars',8)
def main():
    global TEMPO_ID
    H=0.0; last=time.perf_counter(); clips={}; comp=get_comp(); TEMPO_ID=comp['tempocontroller']['tempo']['id']; bpm=comp['tempocontroller']['tempo']['value']
    frames=0; t_report=time.time(); lag=0.0
    def scan():
        # light loop (4 Hz): bpm + per-clip refresh of known clips. heavy loop (every 3 s): full composition to discover connections.
        nonlocal comp,bpm,clips
        t_full=0; t_follow=0
        def rediscover(src):
            nonlocal comp,clips
            comp=src; live={}
            for li,l in enumerate(comp['layers']):
                for ci,cc in enumerate(l['clips']):
                    if 'Connected' in str(cc['connected']['value']) and cc['video'] and is_sp(cc):
                        key=(li,ci); old=clips.get(key)
                        live[key]=old if old and old.schema==clip_schema(cc) else Clip(li,ci,cc)
            for key,c0 in clips.items():
                if key not in live: event(f"released {c0.name!r}")
            clips=live; CLIPS.clear(); CLIPS.update(live)
        size_ids=(comp['video']['width']['id'],comp['video']['height']['id']); last_size=[None]; t_size=[0.0]
        while True:
            try:
                bpm=get_bpm()
                if time.time()-t_size[0]>2.0:                # comp size poll (2 cheap by-id reads)
                    t_size[0]=time.time()
                    sz=tuple(json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{i}",timeout=1))['value'] for i in size_ids)
                    if sz!=last_size[0] and '--match-sizes' in sys.argv:
                        last_size[0]=sz
                        threading.Thread(target=match_clip_sizes,args=(get_comp(),),daemon=True).start()
                if RESCAN.is_set():
                    RESCAN.clear(); RESCAN_L.set(); t_full=time.time()
                    rediscover(PUSHED.get('comp') or get_comp())
                    t_follow=time.time()+1.4              # the dump races the connect: look again at settled state
                elif t_follow and time.time()>=t_follow:
                    t_follow=0; RESCAN_L.set(); rediscover(get_comp())
                for (li,ci),c in list(clips.items()):
                  try:
                    cj=get_clip(li,ci)
                    if 'Connected' not in str(cj['connected']['value']):      # transition finished → clip left the layer
                        event(f"released {c.name!r}"); del clips[(li,ci)]; CLIPS.pop((li,ci),None); continue
                    if c.schema!=clip_schema(cj):
                        RESUME[(li+1,ci+1)]={'slots':[{'name':sl.name,'drive':sl.drive,'v':sl.value(sl.blend(time.perf_counter()))} for sl in c.slots if sl.target]}
                        c=Clip(li,ci,cj); clips[(li,ci)]=c; CLIPS[(li,ci)]=c
                        event(f"{c.name}: parameter layout refreshed; new controls start still")
                    c.refresh(cj)
                    if not c.taken: c.takeover(put); event(f"took over L{li+1}C{ci+1} {c.name!r}: {len(c.slots)} slots")
                  except Exception as e:
                    if '404' in str(e):                                   # Arena re-numbered its ids (reload / restart): forget and rediscover
                        event(f"{c.name}: ids gone (404) → rescan"); del clips[(li,ci)]; CLIPS.pop((li,ci),None)
                        try: rediscover(get_comp())
                        except Exception as e2: event(f"rescan failed: {e2}")
                        continue
                    if not getattr(c,'_warned',False): c._warned=True; event(f"{c.name}: skipped ({e}) — old clip instance? re-add it from the Sources tab")
                # layers strip
                if comp and (not LAYERS or RESCAN_L.is_set()):
                    RESCAN_L.clear(); LAYERS.clear()
                    for i,l in enumerate(comp['layers']):
                        LAYERS.append({"i":i+1,"name":l['name']['value'],"id_opacity":l['video']['opacity']['id'],"id_bypass":l['bypassed']['id'],"opacity":l['video']['opacity']['value'],"bypass":l['bypassed']['value'],"clip":""})
                    LAYERS.reverse(); discover_fx(comp)
                for L in LAYERS:
                    if time.time()-L.get('_hold',0)>0.6:      # don't fight a fader mid-drag
                        L['opacity']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_opacity']}",timeout=1))['value']
                    L['bypass']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_bypass']}",timeout=1))['value']
                    if L.get('id_ap'):
                        try: L['ap']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_ap']}",timeout=1)).get('index',0)
                        except Exception: pass
                    if L.get('_cids'):   # connected col: poll per-clip (the comp dump races the connect, so it can't be trusted for this)
                        cc=pv=0
                        for col,cid in L['_cids']:
                            try:
                                v=str(json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{cid}",timeout=1)).get('value',''))
                                if 'eviewing' in v: pv=col; break   # incoming clip (Previewing / Connected & previewing) wins during a transition
                                if v=='Connected' and not cc: cc=col
                            except Exception: pass
                        cc=pv or cc
                        L['ccol']=cc; L['clip']=next((c['name'] for c in L.get('clips',[]) if c['col']==cc),"")
                if comp:
                    for L in LAYERS:
                        l=comp['layers'][L['i']-1]; L.setdefault('clip',next((c['name']['value'] for c in l['clips'] if 'Connected' in str(c['connected']['value'])),""))
                        L['clips']=[{"col":ci+1,"name":c['name']['value']} for ci,c in enumerate(l['clips']) if c.get('video')]
                        L['_cids']=[(ci+1,c['connected']['id']) for ci,c in enumerate(l['clips']) if c.get('video') and c['connected'].get('id')]
                        L.setdefault('ccol',next((ci+1 for ci,c in enumerate(l['clips']) if 'Connected' in str(c['connected']['value'])),0))
                        ap=l.get('autopilot',{}).get('target',{})
                        L['id_ap']=ap.get('id'); L.setdefault('ap',ap.get('index',0))
            except Exception as e: print("[heart] scan error:",e,flush=True)
            time.sleep(0.25)
    threading.Thread(target=persist_atoms,daemon=True).start()
    threading.Thread(target=scan,daemon=True).start()
    threading.Thread(target=ws_writer,daemon=True).start()
    threading.Thread(target=status_server,daemon=True).start()
    print(f"[heart] running. bpm={bpm} (1 turn = 1 bar). status: http://localhost:8765",flush=True)
    step=1/FPS; next_t=time.perf_counter(); worst=0; next_status=0.0
    while True:
        now=time.perf_counter(); dt=now-last if last<now else step; last=now
        dH=(0.0 if STATE['hold'] else dt*bpm/60.0/4.0/STATE['bars']); H+=dH  # 1 turn = N bars; integrate: speed/bars-change immune (kit law)
        t0=time.perf_counter(); snap=[]; publish=now>=next_status
        if publish: next_status=now+1/15
        for c in list(clips.values()):
            if c.auto>0:
                n=math.floor(H*STATE['bars']/c.auto)
                if c._auto_n is None: c._auto_n=n
                elif n!=c._auto_n: c._auto_n=n; MUTATIONS.submit(fire,c)
            if publish: cs={"name":c.name,"layer":c.layer+1,"col":c.col+1,"pattern":FAMILIES[c.g['pattern']] if hasattr(c,'g') else '',"g":getattr(c,'g',{}),"morph":c.morph,"home":bool(c.home),"arm":arm_json(c.arm),"auto":c.auto,"armsets":[k for k in load_armsets_cached().get(c.name,{}) if k!='_last'],"presets":sorted(load_presets_cached().get(c.name,{}).keys()),"preset_names":{k:v.get("label",f"Variation {k}") for k,v in load_presets_cached().get(c.name,{}).items()},"slots":[]}
            for sl in c.slots:
                if not sl.cfg or sl.target is None: continue
                e=sl.step(dH,now); v=sl.value(e)
                morphing=sl.prev is not None and (now-sl.t0)<sl.dur
                # write only what moves, at most 60×/s per knob (Arena's frame rate): more just backs the socket up and arrives in bursts
                if abs(v-getattr(sl,'_lastv',9.0))>1e-6 and (now-getattr(sl,'_lastt',0.0))>=1/60.0:
                    outv=slot_out(sl,v)
                    if outv!=getattr(sl,'_lastout',None): put(sl.ids[''],outv); sl._lastout=outv   # a picker writes only when the option changes
                    sl._lastv=v; sl._lastt=now
                if publish: cs["slots"].append({"name":sl.name,"choices":getattr(sl,"choices",[]),"v":round(v,4),"drive":sl.drive,"morphing":sl.prev is not None and (now-sl.t0)<sl.dur,"cyc":sl.cyclic,"ratio":sl.cfg['ratio'],"mult":sl.cfg['mult'],"offset":sl.cfg['offset'],"shape":sl.cfg['shape'],"lo":sl.cfg['lo'],"hi":sl.cfg['hi'],"lock":sl.cfg['lock']})
            if publish: snap.append(cs)
        for e in list(FX.values()): e.step(dt,H)
        worst=max(worst,time.perf_counter()-t0); frames+=1
        H_now[0]=H
        if publish: STATE.update({"H":round(H,3),"bpm":bpm,"clips":snap,"queue":OUT.qsize(),"delivery":OUT.metrics(),"layers":[{k:v for k,v in L.items() if not k.startswith('_') and not k.startswith('id_')} for L in LAYERS],
                      "fx":[{"key":e.key,"scope":e.scope,"layer":e.layer,"lname":next((L['name'] for L in LAYERS if L['i']==e.layer),""),"name":e.name,"colors":e.colors,"env":round(e.env,3),"target":e.target,"pending":e.pending is not None,"bypassed":getattr(e,'bypassed',False),"cfg":e.cfg} for e in FX.values()]})
        if time.time()-t_report>2:
            STATE["fps"]=round(frames/(time.time()-t_report),1); STATE["worst"]=round(worst*1000,2)
            print(f"[heart] H={H:8.3f}  bpm={bpm}  fps={STATE['fps']}  worst frame={STATE['worst']}ms  queue={OUT.qsize()}  clips={[c.name for c in clips.values()]}",flush=True); frames=0; t_report=time.time(); worst=0
        next_t+=step; d=next_t-time.perf_counter()
        if d>0: time.sleep(d)
        else: next_t=time.perf_counter()
if __name__=="__main__": main()
