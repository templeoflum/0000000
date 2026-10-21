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
import os, uuid
from concurrent.futures import ThreadPoolExecutor
import targets
import feedback
import instruments
import live_presets
import modulation
import dependencies
from patches import Operations, Cancelled, validate_snapshot, composition_signature, open_verified
from delivery import LatestValues
from motion import recipe_rate, animated_home, speed_value
from ownership import OwnershipObserver
from transport import Transport, tempo_value
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
        s.ownership_lock=threading.RLock();s.claim_epoch=0;s.claim_inflight=False;s.phase_checked=None
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
ATOMS.setdefault("SPHeartFeedback",copy.deepcopy(feedback.ATOM))
for source,defaults in instruments.atom_defaults().items(): ATOMS.setdefault(source,defaults)
MOTION_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"motion.json")
try: MOTION=json.load(open(MOTION_FILE))
except Exception: MOTION={}
try: SWEETSPOTS=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"sweetspots.json")))
except Exception: SWEETSPOTS={}
CONTROL_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'controls.json')
try:
    with open(CONTROL_FILE) as f:CONTROL_CONFIG=json.load(f)
except (OSError,ValueError):CONTROL_CONFIG={}
def persist_control(sl):
    if not hasattr(sl,'persist_key'):save_atoms();return
    CONTROL_CONFIG[sl.persist_key]=copy.deepcopy(sl.acfg)
    tmp=CONTROL_FILE+'.tmp'
    with open(tmp,'w') as f:json.dump(CONTROL_CONFIG,f,indent=1)
    os.replace(tmp,CONTROL_FILE)
def motion_key(clip): return 'effect:'+clip.effect_key if hasattr(clip,'effect_key') else f"{getattr(clip,'atom',None) or clip.name}:{clip.name}"
def saved_key(clip): return 'effect:'+clip.effect_key if hasattr(clip,'effect_key') else clip.name
def motion_save(clip,key,value):
    if key=='speed':value=speed_value(value)
    MOTION.setdefault(getattr(clip,'role','')+'/'+motion_key(clip) if hasattr(clip,'role') else motion_key(clip),copy.deepcopy(MOTION.get(motion_key(clip),{})))[key]=copy.deepcopy(value)
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
def legacy_sections(cj):
    v=cj.get('video') or {};sections=[('source',v.get('sourceparams') or {})]
    for _,e,eid in targets.named(v.get('effects',[])):
        if any(k.endswith(' Drive') for k in e.get('params',{})):sections.append(('effect/'+eid,e.get('params',{})))
    return sections
def allparams(cj):
    # Preserve legacy single-section labels; qualify colliding slot groups together.
    from collections import Counter
    sections=legacy_sections(cj)
    counts=Counter(k[:-6] for _,pr in sections for k in pr if k.endswith(' Drive'))
    sp={}
    for section,pr in sections:
        bases=[k[:-6] for k in pr if k.endswith(' Drive')]
        for n,p in pr.items():
            base=next((b for b in sorted(bases,key=len,reverse=True) if n==b or n.startswith(b+' ')),None)
            key=section+' / '+n if base and counts[base]>1 else n
            sp[key]=p
    return sp
def clip_schema(cj):
    groups=[('source',allparams(cj))]+atom_sections(cj)
    return tuple((section,n,p.get('id'),p.get('valuetype'),p.get('min'),p.get('max'),tuple(p.get('options') or []))
                 for section,pr in groups for n,p in pr.items() if isinstance(p,dict) and 'id' in p)

class Clip:
    """one connected SP clip: discovers slots from its sourceparams (+ SP effect params)"""
    def __init__(s,layer,col,cj):
        s.instance=uuid.uuid4().hex
        s.schema=clip_schema(cj)
        s.layer,s.col=layer,col; s.role=cj.get('_heart_layer_role',str(layer+1));s.name=cj['name']['value']; sp=allparams(cj); s.sp=sp
        s.gids={k:sp[k]['id'] for k in ('Pattern','Seed','Spread','Depth','FM') if k in sp}
        names=[k[:-6] for k in sp if k.endswith(' Drive')]
        s.instrument=instruments.get(s.role,(cj.get('video') or {}).get('description'))
        s.atom=None; acfg={}; s.asec={}
        if not names:
            secs=atom_sections(cj)
            if secs:
                s.atom=secs[0][0]                                  # the first section holds _global; every section contributes knobs
                from collections import Counter
                counts=Counter(n for section,params in secs for n in params if n!='Opacity')
                occurrences=Counter()
                for section,params in secs:
                    occurrences[section]+=1
                    for n,p in params.items():
                        if isinstance(p,dict) and p.get('valuetype') in ('ParamEvent','ParamTrigger'):
                            # Events belong to the instrument but never become continuously driven slots.
                            key=n if counts[n]==1 else f"{section} {occurrences[section]} / {n}"
                            sp[key]=p
                            continue
                        if not isinstance(p,dict) or p.get('valuetype') not in ('ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice'):continue
                        if n=='Opacity':continue
                        if n not in ATOMS[section]:
                            ATOMS[section][n]={'cyclic':False,'drive':False,'ratio':'1:4','mult':1,'offset':0,'shape':1,'lo':0,'hi':1}
                            save_atoms()
                        key=n if counts[n]==1 else f"{section} {occurrences[section]} / {n}"
                        acfg[key]=ATOMS[section][n] if counts[n]==1 else copy.deepcopy(ATOMS[section][n])
                        s.asec[key]=(section,occurrences[section],n)
                        sp[key]=p
                names=list(acfg)
        s.slots=[]
        for i,n in enumerate(names):
            if s.atom:
                identity='/'.join(map(str,s.asec[n]));persist_key=s.role+'/'+s.name+'/'+identity
                a=copy.deepcopy(CONTROL_CONFIG.get(persist_key,acfg[n])); sl=Slot(n, bool(a.get('cyclic'))); sl.index=i; sl.acfg=a;sl.persist_key=persist_key
                sl.identity='/'.join(map(str,s.asec[n]));sl.kind=sp[n].get('valuetype');sl.ids={'':sp[n]['id']}; sl.pmin=float(sp[n].get('min',0.0)); sl.pmax=float(sp[n].get('max',1.0))
                if sp[n].get('valuetype')=='ParamChoice':                 # a picker: the 0..1 signal walks the option list
                    sl.choices=list(sp[n].get('options') or []); sl.pmin=0.0; sl.pmax=1.0
                sl.shape_opts=['rotate','sway'] if sl.cyclic else ['loop','sway']
            else:
                sl=Slot(n, sp.get(n+' Shape',{}).get('options',[''])[0]=='rotate'); sl.index=i
                sl.identity=next((section+'/'+raw for section,pr in legacy_sections(cj) for raw,p in pr.items() if isinstance(p,dict) and p.get('id')==sp[n].get('id')),n)
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
            from collections import Counter
            occurrences=Counter()
            for section,params in atom_sections(cj):
                occurrences[section]+=1
                for key,(owner,instance,raw) in s.asec.items():
                    if (section,occurrences[section])==(owner,instance) and raw in params:sp[key]=params[raw]
            for sl in s.slots:
                n=sl.name; a=sl.acfg; span=max(sl.pmax-sl.pmin,1e-9)
                if hasattr(sl,'choices'): live=(sp[n].get('index',0)/max(len(sl.choices)-1,1)) if len(sl.choices)>1 else 0.0
                else: live=(float(sp[n]['value'])-sl.pmin)/span                     # the knob, normalised to the slot's 0..1 signal
                sl.observed=live
                sl.cfg={'manual':sl.cfg.get('manual',live) if s.taken else live,'drive':sl.drive if s.taken else bool(a.get('drive',False)),
                        'ratio':a.get('ratio','1:1'),'mult':float(a.get('mult',1.0)),'offset':float(a.get('offset',0.0)),'shape':int(a.get('shape',1)),
                        'lo':float(a.get('lo',0.0)),'hi':float(a.get('hi',1.0)),'lock':bool(a.get('lock',False))}
            g.update(MOTION.get(s.role+'/'+motion_key(s),MOTION.get(motion_key(s),{})));  s.g=g; now=time.perf_counter()
            for sl in s.slots: sl.dur=s.morph; sl.retarget(g,now)
            return
        g={'pattern':sp['Pattern']['index'] if 'Pattern' in sp else 11,'seed':int(sp['Seed']['value']) if 'Seed' in sp else 0,'spread':int(sp['Spread']['value']) if 'Spread' in sp else 1,
           'depth':sp['Depth']['value'] if 'Depth' in sp else 1.0,'fm':sp['FM']['value'] if 'FM' in sp else 0.0}
        for sl in s.slots:
            n=sl.name
            sl.observed=sp[n]['value']
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
        g.update(MOTION.get(s.role+'/'+motion_key(s),MOTION.get(motion_key(s),{})));  s.g=g
        now=time.perf_counter()
        for sl in s.slots: sl.dur=s.morph; sl.retarget(g,now)
    def takeover(s,put):
        # remember the shader's Drive flags as OUR drive flags, then switch the shader's off so it shows manual (= our written value)
        for sl in s.slots:
            sl.drive=(True if DRIVE_ALL else sl.cfg['drive']) if not s.atom else sl.cfg['drive']   # atoms: their config says which knobs move
            sl.owner='heart'
            if not hasattr(sl,'choices'):
                try:
                    phase=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{sl.ids['']}/phase-source",timeout=1))
                    sl.native_phase=phase.get('phase_source');sl.phase_checked=time.monotonic()
                    if sl.native_phase!='static':sl.owner='resolume';sl.drive=False
                except Exception:sl.owner='unverified';sl.drive=False
            if 'Drive' in sl.ids and sl.owner=='heart':put_http(sl.ids['Drive'],False)
        s.taken=True
        resume=RESUME.pop((s.layer+1,s.col+1),None)
        if resume:
            for sl in s.slots:
                old=next((x for x in resume['slots'] if x['name']==sl.name),None)
                if old:
                    sl.drive=old['drive'] if sl.owner=='heart' else False; sl.cfg['manual']=old.get('base',old['v'])
                    sl.phi=old.get('phase',0.);sl.phi_fm=old.get('phase_fm',0.);sl.rot=old.get('rotation',0.)
                    sl.prev=None; sl.target=None; sl.retarget(s.g,time.perf_counter())
        h=load_homes().get(s.name)
        if h: s.home=h; event(f"{s.name}: home loaded")
        else: threading.Thread(target=set_home,args=(s,False),daemon=True).start()

import random
def wcfg(clip,sl,key,v,snap):
    """write one slot config field: to its Arena id (slot shaders) or into the heart's atoms.json (atoms)"""
    if key in sl.ids: snap.setdefault(sl.ids[key],cur_val(sl.ids[key])); put_http(sl.ids[key],v); return
    k=key.lower()
    if key=='Shape' and isinstance(v,str): v=sl.shape_opts.index(v) if v in sl.shape_opts else int(float(v))
    if key in ('Lo','Hi','Mult','Offset'): v=float(v)
    snap.setdefault(f"cfg:{sl.name}:{k}",sl.acfg.get(k)); sl.acfg[k]=v; sl.cfg[k]=v; persist_control(sl)
    sl.dur=getattr(clip,'morph',sl.dur);sl.retarget(clip.g,time.perf_counter())
def wglob(clip,key,v,snap):
    if key.lower() in ('speed','relationship','timing_mode'):
        motion_save(clip,key.lower(),v); return
    if hasattr(clip,'effect_key'):
        if key=='Pattern':v=FAMILIES.index(v) if isinstance(v,str) and v in FAMILIES else int(v)
        else:v=int(v) if key in ('Seed','Spread') else float(v)
        motion_save(clip,key.lower(),v);return
    if key in clip.gids: snap.setdefault(clip.gids[key],cur_val(clip.gids[key])); put_http(clip.gids[key],v); return
    if not getattr(clip,'atom',None): return
    G=ATOMS[clip.atom].setdefault('_global',{}); k=key.lower()
    if key=='Pattern': v=FAMILIES.index(v) if isinstance(v,str) and v in FAMILIES else int(v)
    else: v=int(v) if key in ('Seed','Spread') else float(v)
    snap.setdefault(f"glob:{k}",G.get(k)); motion_save(clip,k,v)
def slot_out(sl,v):
    """the slot's 0..1 signal in the knob's own units: a float in its range, or an option's name for a picker"""
    if hasattr(sl,'choices') and sl.choices: return sl.choices[min(len(sl.choices)-1,max(0,int(round(v*(len(sl.choices)-1)))))]
    value=(sl.pmin+v*(sl.pmax-sl.pmin)) if hasattr(sl,'pmin') else v
    return round(value) if getattr(sl,'integer',False) or getattr(sl,'kind','') in ('ParamInt','ParamNumber') else value
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
    motion_save(clip,'timing_mode',None)
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
        if 'drive' in cats or 'look' in cats:claim_slot(sl)
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
    motion_save(clip,'timing_mode',mode)
    event(f"{clip.name}: timing {'⊙ unison' if mode=='unison' else ('♩ '+mode if mode=='harmonic' else '∞ '+mode)}")
def arm_default(): return {'global':set(),'slots':{}}
def arm_json(a): return {'global':sorted(a['global']),'slots':{k:sorted(v) for k,v in a['slots'].items() if v}}
def arm_from(j): return {'global':set(j.get('global',[])),'slots':{k:set(v) for k,v in j.get('slots',{}).items()}}
HOME_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"home.json")
def load_homes():
    try: return json.load(open(HOME_FILE))
    except Exception: return {}
def set_home(clip, user_saved=True):
    vals=capture_pose(clip) if user_saved else capture_state(clip)
    vals['sweet_home']=user_saved
    homes=load_homes(); homes[saved_key(clip)]=vals; json.dump(homes,open(HOME_FILE,"w"),indent=1); clip.home=vals; event(f"{clip.name}: home set")
def axis_good_set(clip,name):
    homes=load_homes(); h=homes.get(saved_key(clip)) or capture_state(clip)
    if h.get('version')!=2: h=capture_state(clip)
    h['slots'][name]=capture_state(clip)['slots'][name]
    homes[saved_key(clip)]=h; json.dump(homes,open(HOME_FILE,"w"),indent=1); clip.home=h
    event(f"{clip.name}/{name}: good saved")
def axis_good_go(clip,name):
    h=clip.home or load_homes().get(saved_key(clip))
    if not h: return
    if h.get('version')==2:
        if name in h['slots']: apply_state(clip,{'version':2,'slots':{name:h['slots'][name]}},f"{name} return")
        return
    sl=next(x for x in clip.slots if x.name==name)
    ids={str(pid) for k,pid in sl.ids.items() if k!='Drive'}
    apply_state(clip,{k:v for k,v in h.items() if k in ids or k in ('manual:'+name,'drive:'+name)},f"{name} return")
def home_profile(clip):
    if hasattr(clip,'effect_key'):return {'bindings':{}}
    try:
        with open(os.path.join(os.path.dirname(__file__),'sweetspots.json')) as f:profiles=json.load(f)
    except (OSError,ValueError):profiles=SWEETSPOTS
    profile=feedback.get('Turn') if clip.atom=='SPHeartFeedback' else (instruments.home(getattr(clip,'role',''),clip.atom) or profiles.get(clip.atom or clip.name))
    profile=copy.deepcopy(profile or {'bindings':{}})
    for sl in clip.slots:
        option=profile.get('choices',{}).get(sl.name);choices=getattr(sl,'choices',[])
        if option in choices:profile.setdefault('static',{})[sl.name]=choices.index(option)/max(1,len(choices)-1)
    return profile

def capture_pose(clip):
    """The currently rendered pose, rather than an animated slot's manual base."""
    out=capture_state(clip);now=time.perf_counter()
    for sl in clip.slots:
        v=sl.observed if getattr(sl,'owner','heart')!='heart' else sl.value(sl.blend(now)) if sl.target else out['slots'][sl.name]['pose']
        out['slots'][sl.name]['pose']=v
        out['slots'][sl.name]['config']['manual']=v
    return out

def performance_before(clip):
    out=capture_state(clip)
    out['performance']={'auto':getattr(clip,'auto',0)}
    if hasattr(clip,'effect_key'):
        fx=FX[clip.effect_key]
        out['performance']['effect_target']=fx.pulse_state['baseline'] if fx.pulse_state else fx.return_target if fx.return_target is not None else fx.target
    return out

def go_home(clip,factory=False):
    """Rest at a familiar pose; motion recipes and full exploration belong to Open."""
    h=None if factory else (clip.home or load_homes().get(saved_key(clip)))
    before=performance_before(clip);target=capture_pose(clip);profile=home_profile(clip)
    for sl in clip.slots:
        saved=target['slots'][sl.name];binding=profile['bindings'].get(sl.name)
        if binding:saved['pose']=binding['center']
        if sl.name in profile.get('static',{}):saved['pose']=profile['static'][sl.name]
        if h and h.get('sweet_home'):
            matches=[v for v in h.get('slots',{}).values() if v.get('identity')==getattr(sl,'identity',sl.name)]
            old=matches[0] if len(matches)==1 else h.get('slots',{}).get(sl.name) if not matches else None
            if old and (not old.get('identity') or old.get('identity')==getattr(sl,'identity',sl.name)):
                saved['pose']=old['pose']
            elif h.get('version')!=2 and 'manual:'+sl.name in h:saved['pose']=h['manual:'+sl.name]
        saved['drive']=False;saved['config']['manual']=saved['pose'];saved['config']['drive']=False
    target['performance']={'auto':0}
    if hasattr(clip,'effect_key'):target['performance']['effect_target']=0.
    clip.history.append(before);clip.history=clip.history[-20:]
    for sl in clip.slots:sl.dur=clip.morph
    apply_state(clip,target,'Home · rest')

def open_motion(clip):
    """Explicitly drive every numeric axis, keeping the timing relationships intact."""
    before=performance_before(clip);target=capture_pose(clip);target['global']['depth']=1.
    profile=home_profile(clip)
    # Source framing remains local to the figure. Native effects have no such restriction.
    framing={'Size','X','Y'} if not hasattr(clip,'effect_key') and getattr(clip,'role','')=='figure' else set()
    for sl in clip.slots:
        saved=target['slots'][sl.name]
        if hasattr(sl,'choices'):saved['drive']=False;continue
        limits=profile['bindings'].get(sl.name,{}).get('range',[sl.cfg['lo'],sl.cfg['hi']]) if sl.name in framing else [0.,1.]
        saved['drive']=True;saved['config'].update(drive=True,lo=limits[0],hi=limits[1],lock=False)
    if hasattr(clip,'effect_key'):target['performance']={'effect_target':1.}
    clip.history.append(before);clip.history=clip.history[-20:]
    for sl in clip.slots:sl.dur=clip.morph
    apply_state(clip,target,'Open · full drives')
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
                 'pose':sl.cfg['manual']+sl.rot if sl.cyclic else sl.cfg['manual'],'identity':getattr(sl,'identity',sl.name)}
        for sl in clip.slots}}
def apply_state(clip,h,label="preset"):
    if hasattr(clip,'effect_key') and not current_controller(clip):raise ValueError('Effect target changed')
    if h.get('version')==2:
        if 'global' in h:
            wglob(clip,'Relationship',h['global'].get('relationship'),{})
            wglob(clip,'Speed',h['global'].get('speed',1.),{})
        for k,v in h.get('global',{}).items():
            wglob(clip,'FM' if k=='fm' else k.capitalize(),FAMILIES[int(v)] if k=='pattern' else v,{})
        clip.g.update(h.get('global',{}))
        resolved=set()
        for sl in clip.slots:
            matches=[v for v in h.get('slots',{}).values() if v.get('identity')==getattr(sl,'identity',sl.name)]
            saved=matches[0] if len(matches)==1 else None
            if not matches:
                legacy=h.get('slots',{}).get(sl.name)
                if legacy and not legacy.get('identity'):saved=legacy
            if saved is None: continue
            resolved.update(k for k,v in h.get('slots',{}).items() if v is saved)
            cfg=saved['config']
            for k in ('ratio','mult','offset','shape','lo','hi','lock'):
                if k in cfg: wcfg(clip,sl,k.capitalize(),sl.shape_opts[int(cfg[k])] if k=='shape' else cfg[k],{})
            claim_slot(sl,force=True);sl.cfg.update(cfg); sl.drive=bool(saved['drive'])
            sl.cfg['manual']=((saved['pose']-sl.rot)%1.0) if sl.cyclic else saved['pose']
            sl.retarget(clip.g,time.perf_counter())
        missing=set(h.get('slots',{}))-resolved
        if missing:event(f"{clip.name}: skipped missing or ambiguous preset controls: {', '.join(sorted(missing))}")
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
    performance=h.get('performance',{})
    if 'auto' in performance:clip.auto=performance['auto'];clip._auto_n=None
    if 'effect_target' in performance and hasattr(clip,'effect_key') and current_controller(clip):
        FX[clip.effect_key].manual(performance['effect_target'])
    event(f"{clip.name}: → {label} (morphing)")
def preset_save(clip,pad,name=None):
    ps=load_presets(); state=capture_state(clip)
    state['label']=(str(name).strip()[:80] if name else '') or ps.get(saved_key(clip),{}).get(str(pad),{}).get('label',f'Variation {pad}')
    ps.setdefault(saved_key(clip),{})[str(pad)]=state
    json.dump(ps,open(PRESET_FILE,"w"),indent=1); _PS["t"]=0; event(f"{clip.name}: preset {pad} saved")
def preset_go(clip,pad):
    h=load_presets().get(saved_key(clip),{}).get(str(pad))
    if not h: event(f"{clip.name}: preset {pad} empty"); return
    apply_state(clip,h,f"preset {pad}")
def preset_mom(clip,pad,on):
    held=getattr(clip,'_held_presets',{})
    key=str(pad)
    if on:
        h=load_presets().get(saved_key(clip),{}).get(key)
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
def clear_layer(layer):
    req=urllib.request.Request(f"{BASE}/composition/layers/{layer}/clear",data=b'',method="POST")
    urllib.request.urlopen(req,timeout=2).read()
    for row in LAYERS:
        if row['i']==layer:row.update(clip='',ccol=0,_empty_reads=2)
    RESCAN.set()
def connect_clip(layer,col):
    req=urllib.request.Request(f"{BASE}/composition/layers/{layer}/clips/{col}/connect",data=b'',method="POST")
    urllib.request.urlopen(req,timeout=1).read()
OUT=LatestValues()
RECONNECT=threading.Event()
RESCAN=threading.Event()
RESCAN_L=threading.Event()
PUSHED={}
CLIPS={}
H_now=[0.0]
LAYERS=[]   # [{i,name,id_opacity,id_bypass,opacity,clip}]
def layer_rows(comp,previous):
    """Publish complete rows; never expose an empty intermediate layer inventory."""
    old={l['id_opacity']:l for l in previous};rows=[]
    for i,l in enumerate(comp['layers']):
        pid=l['video']['opacity']['id'];row=dict(old.get(pid,{}))
        clips=[{'col':ci+1,'name':c['name']['value'],'source':c['video'].get('description')} for ci,c in enumerate(l['clips']) if c.get('video')]
        cc=next((ci+1 for ci,c in enumerate(l['clips']) if 'Connected' in str(c['connected']['value']) or 'reviewing' in str(c['connected']['value'])),0)
        row.update(i=i+1,name=l['name']['value'],id_opacity=pid,id_bypass=l['bypassed']['id'],bypass=l['bypassed']['value'],clips=clips)
        if time.time()-row.get('_hold',0)>.6:row['opacity']=l['video']['opacity']['value']
        if cc or pid not in old:row.update(ccol=cc,clip=next((c['name'] for c in clips if c['col']==cc),''))
        row['forms']=instruments.bank(row['name'],clips)
        row['bank']=STATE['surface'].get('banks',{}).get(row['name'],'forms' if row['forms'] else 'all')
        row['_cids']=[(ci+1,c['connected']['id']) for ci,c in enumerate(l['clips']) if c.get('video') and c['connected'].get('id')]
        rows.append(row)
    return list(reversed(rows))

def update_connected_label(row,readings):
    connected=next((col for col,value in readings if value and 'reviewing' in value),0) or next((col for col,value in readings if value=='Connected'),0)
    if connected:
        row['_empty_reads']=0;row['ccol']=connected
        row['clip']=next((c['name'] for c in row.get('clips',[]) if c['col']==connected),row.get('clip',''))
    elif readings and all(value is not None for _,value in readings):
        row['_empty_reads']=row.get('_empty_reads',0)+1
        if row['_empty_reads']>=2:row.update(ccol=0,clip='')
    else:row['_empty_reads']=0
FX_RELEASES={}
FX={}       # key "L6/3" or "C/2" → Effect
FX_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"fx.json")

class EffectMotion:
    """Typed native-effect bindings using the same Slot and relationship engine."""
    def __init__(s,fx):
        s.effect_key=fx.key;s.instance=fx.instance;s.name=fx.name;s.role='effects';s.atom=None;s.instrument=None
        s.gids={};s.slots=[];s.morph=1.;s.history=[];s.home=load_homes().get(saved_key(s));s.auto=0;s._auto_n=None;s.taken=True
        s.g={'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.,'speed':1.,'relationship':None}
        s.g.update(MOTION.get(s.role+'/'+motion_key(s),{}));s.arm=arm_default()

    def refresh(s,fx):
        from urllib.parse import quote
        old={sl.name:sl for sl in s.slots};live=[];source_ids={sl.ids.get('') for c in CLIPS.values() for sl in c.slots}
        for name,p in (fx.params.items() if fx.scope!='S' else []):
            if name=='Opacity' or p.get('id') in source_ids or p.get('valuetype') not in ('ParamRange','ParamFloat','ParamInt','ParamNumber'):continue
            lo,hi=float(p.get('min',0)),float(p.get('max',1))
            if not math.isfinite(lo+hi) or hi<=lo:continue
            schema=(p['id'],p['valuetype'],lo,hi,p.get('view',{}).get('display_units'))
            sl=old.get(name)
            if sl is None or sl.schema!=schema:
                sl=Slot(name,False);sl.schema=schema;sl.index=len(live);sl.identity=fx.key+'/param/'+quote(name,safe='');sl.persist_key='effect/'+sl.identity
                sl.ids={'':p['id']};sl.pmin=lo;sl.pmax=hi;sl.kind=p['valuetype'];sl.integer=sl.kind in ('ParamInt','ParamNumber') or p.get('view',{}).get('display_units')=='integer'
                sl.shape_opts=['loop','sway'];sl.owner='unverified';sl.acfg=copy.deepcopy(CONTROL_CONFIG.get(sl.persist_key,{}))
                sl.cfg={'manual':(float(p['value'])-lo)/(hi-lo),'drive':False,'ratio':'1:1','mult':1.,'offset':0.,'shape':1,'lo':0.,'hi':1.,'lock':False}
                sl.cfg.update({k:v for k,v in sl.acfg.items() if k in ('ratio','mult','offset','shape','lo','hi','lock')})
                sl.dur=s.morph;sl.retarget(s.g,time.perf_counter())
            sl.observed=(float(p['value'])-lo)/(hi-lo);live.append(sl)
        if [id(x) for x in s.slots]!=[id(x) for x in live]:
            for sl in s.slots:
                if sl not in live:OUT.discard(sl.ids[''])
            fx.instance=uuid.uuid4().hex;s.instance=fx.instance
        s.slots=live
        s.arm={'global':set(),'slots':{sl.name:{'timing','motion'} for sl in live}}
        resume=EFFECT_RESUME.pop(fx.key,None)
        if resume and resume.get('binding')==[fx.composition_epoch,fx.native_identity]:
            saved={x['name']:x for x in (resume.get('motion') or {}).get('slots',[])}
            for sl in live:
                old=saved.get(sl.name);p=resume.get('params',{}).get(sl.name,{})
                if not old or p.get('id')!=sl.ids[''] or old.get('owner')!='heart':continue
                try:
                    phase=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{sl.ids['']}/phase-source",timeout=1))
                    if phase.get('phase_source')!='static':continue
                    sl.owner='heart';sl.native_phase='static';sl.phase_checked=time.monotonic()
                    sl.cfg['manual']=old.get('base',old['v']);sl.phi=old.get('phase',0.);sl.phi_fm=old.get('phase_fm',0.);sl.rot=old.get('rotation',0.)
                    sl.drive=bool(old['drive']);sl.prev=sl.target=None;sl.retarget(s.g,time.perf_counter())
                except (OSError,ValueError):pass

def motion_controllers():
    return list(CLIPS.values())+[e.motion for e in list(FX.values()) if getattr(e,'motion',None)]

def current_controller(c):
    if hasattr(c,'effect_key'):return getattr(FX.get(c.effect_key),'motion',None) is c
    return CLIPS.get((c.layer,c.col)) is c

SHARED=modulation.Bank()
LIVE_PRESET_LOCK=threading.RLock()
LIVE_PRESETS=live_presets.Store(os.path.join(os.path.dirname(os.path.abspath(__file__)),"performance-presets"))

def persist_performance(plan):
    """One persistence pass after a live preset commit, never per parameter."""
    for c,g,slots in plan:
        MOTION[getattr(c,'role','')+'/'+motion_key(c)]=copy.deepcopy(c.g)
        for sl,cfg,saved in slots:
            sl.acfg.update({k:sl.cfg[k] for k in ('ratio','mult','offset','shape','lo','hi','lock')})
            if hasattr(sl,'persist_key'):CONTROL_CONFIG[sl.persist_key]=copy.deepcopy(sl.acfg)
    for path,data in ((MOTION_FILE,MOTION),(CONTROL_FILE,CONTROL_CONFIG),(ATOM_FILE,ATOMS)):
        tmp=path+'.tmp'
        with open(tmp,'w') as f:json.dump(data,f,indent=1)
        os.replace(tmp,path)

def shared_token(sl):return (id(sl),getattr(sl,'claim_epoch',0))
def release_shared(sl):
    route=getattr(sl,'shared_route',None)
    if not route:return
    r=SHARED.routes.get(route)
    if r and r['token']==shared_token(sl):
        value=r['value'];SHARED.remove(route);sl.drive=False
        sl.cfg['manual']=(value-sl.rot)%1 if sl.cyclic else value
        sl.prev=sl.target=None;sl.retarget(next(c.g for c in motion_controllers() if sl in c.slots),time.perf_counter())
    sl.shared_route=None

def bind_shared(d):
    validate_surface_target(d)
    c=FX[d['effect']].motion if d.get('effect') else CLIPS[(d['layer']-1,d['col']-1)]
    sl=next(x for x in c.slots if x.name==d['slot'])
    if getattr(sl,'choices',[]) or getattr(sl,'integer',False):raise ValueError('Shared LFO proof supports continuous controls only')
    if getattr(c,'role','')=='figure' and sl.name in ('Size','X','Y'):raise ValueError('Figure placement routing awaits its containment adapter')
    if not isinstance(d.get('route'),str) or not 1<=len(d['route'])<=80:raise ValueError('Route ID required')
    if d['generator'] not in SHARED.generators:raise ValueError('Unknown generator')
    low=float(d.get('low',0));high=float(d.get('high',1));seconds=float(d.get('seconds',1))
    if not all(math.isfinite(v) for v in (low,high,seconds)) or not 0<=low<=high<=1 or not 0<=seconds<=30:raise ValueError('Invalid destination transform')
    claim_slot(sl,False)
    if not current_controller(c) or sl not in c.slots:raise ValueError('Destination changed')
    with LIVE_PRESET_LOCK:
        now=time.perf_counter();start=max(0.,min(1.,getattr(sl,'_lastv',sl.cfg['manual'])))
        old=getattr(sl,'shared_route',None)
        if old:SHARED.remove(old)
        # Reassigning the same route retires its old binding before the new token exists.
        for controller in motion_controllers():
            for previous in controller.slots:
                if previous is not sl and getattr(previous,'shared_route',None)==d['route']:release_shared(previous)
        sl.drive=False;sl.cfg['manual']=(start-sl.rot)%1 if sl.cyclic else start
        sl.prev=sl.target=None;sl.retarget(c.g,now);sl.shared_route=d['route']
        SHARED.bind(d['route'],d['generator'],shared_token(sl),start,now,seconds,low,high,{'effect':d.get('effect'),'layer':d.get('layer'),'col':d.get('col'),'slot':sl.name})
    event('Shared motion '+d['generator']+' → '+c.name+'/'+sl.name)

def step_motion(c,dH,now,publish):
    with LIVE_PRESET_LOCK:return _step_motion(c,dH,now,publish)

def _step_motion(c,dH,now,publish):
    slots=[]
    for sl in c.slots:
        if not sl.cfg or sl.target is None:continue
        owned=getattr(sl,'owner','heart')=='heart' and not getattr(sl,'preset_preparing',False)
        if hasattr(c,'effect_key') and not owned:
            if not publish:continue
            v=sl.observed
        else:
            shared=SHARED.value(getattr(sl,'shared_route',None),shared_token(sl),now) if owned else None
            if shared is not None:v=shared
            else:
                sl.dur=c.morph if sl.drive else sl.dur
                sl.retarget(c.g,now);e=sl.step(dH,now);v=sl.value(e)
            if owned and not PATCH_OPS.busy and STATE.get('arena_connected') and current_controller(c) and abs(v-getattr(sl,'_lastv',9.))>1e-6 and now-getattr(sl,'_lastt',0.)>=1/60:
                outv=slot_out(sl,v)
                if outv!=getattr(sl,'_lastout',None):put(sl.ids[''],outv);sl._lastout=outv
                sl._lastv=v;sl._lastt=now
        if publish:
            slots.append({'name':sl.name,'owner':getattr(sl,'owner','heart'),'choices':getattr(sl,'choices',[]),
                'generator':(SHARED.routes.get(getattr(sl,'shared_route',None)) or {}).get('generator') if SHARED.value(getattr(sl,'shared_route',None),shared_token(sl),now) is not None else None,'v':round(slot_display_value(sl,v),4),'drive':sl.drive,'morphing':sl.prev is not None and now-sl.t0<sl.dur,
                'morph_remaining':round(max(0.,sl.dur-(now-sl.t0)),2) if sl.prev is not None else 0.,
                'morph_progress':round(min(1.,max(0.,(now-sl.t0)/sl.dur)),3) if sl.dur>0 and sl.prev is not None else 1.,
                'cyc':sl.cyclic,'ratio':sl.cfg['ratio'],'mult':sl.cfg['mult'],'offset':sl.cfg['offset'],'shape':sl.cfg['shape'],
                'lo':sl.cfg['lo'],'hi':sl.cfg['hi'],'lock':sl.cfg['lock'],'min':getattr(sl,'pmin',0.),'max':getattr(sl,'pmax',1.),
                'integer':getattr(sl,'integer',False) or getattr(sl,'kind','') in ('ParamInt','ParamNumber'),
                'base':sl.cfg['manual'],'phase':sl.phi,'phase_fm':sl.phi_fm,'rotation':sl.rot})
    return slots

def align_motion(old_beats):
    SHARED.reset()
    now=time.perf_counter()
    for c in motion_controllers():
        c._auto_n=None
        for sl in c.slots:
            sl.phi=sl.phi_fm=sl.rot=0.
            sl._lastv=9.;sl._lastout=None
    for fx in list(FX.values()):
        # Keep pending native-style envelopes at the same musical distance away.
        if fx.pending is not None:fx.pending=max(0.,fx.pending-old_beats/4.)
        if fx.hold_until is not None:fx.hold_until=max(0.,fx.hold_until-old_beats/4.)

def set_tempo(value):
    value=tempo_value(value)
    p=get_comp()['tempocontroller']['tempo']
    put_http(p['id'],value);STATE['bpm']=value
    event(f'Tempo {value:.2f} BPM')

def set_downbeat():
    p=get_comp()['tempocontroller']['resync']
    arena_post(f"/parameter/by-id/{p['id']}/trigger")
    TRANSPORT.downbeat();event('Downbeat · phrase and motion aligned')

class Effect:
    """an Arena effect with an ENVELOPE (0→1) the engine owns, written to its Opacity. attack/release, modes, quantize, reverse-on-repress."""
    def __init__(s,key,scope,layer,idx,name,id_opacity,id_bypass,opmax):
        s.instance=uuid.uuid4().hex
        s.key,s.scope,s.layer,s.idx,s.name=key,scope,layer,idx,name; s.id_opacity=id_opacity; s.id_bypass=id_bypass; s.opmax=opmax
        s.colors={}; s.params={}; s.motion=None;s.pulse_state=None;s.return_target=None; s.owners=set(); s.native_identity=None; s.composition_epoch=None
        s.env=0.0; s.target=0.0; s.held=False; s.pending=None; s.hold_until=None; s.last_written=None
        s.cfg={"attack":0.5,"release":1.0,"mode":"latch","quant":0,"hold":0.0,"key":"","bypass0":True,"bind":None,"pulse_attack":.04,"pulse_hold":.08,"pulse_return":.25}
        cf=load_fx().get(key); 
        if cf: s.cfg.update(cf)
    def press(s,H,owner='default'):
        if owner in s.owners:return
        s.cancel_pulse()
        FX_RELEASES.pop(s.key,None)
        if s.cfg['mode']=='momentary':
            if not s.owners:s.return_target=s.target
            s.owners.add(owner)
        c=s.cfg; m=c["mode"]
        act={"latch": (lambda: setattr(s,"target",0.0 if (s.target if abs(s.target-s.env)>1e-6 else s.env)>0.5 else 1.0)),
             "momentary": (lambda: (setattr(s,"held",True),setattr(s,"target",1.0))),
             "oneshot": (lambda: (setattr(s,"env",1.0),setattr(s,"target",1.0),setattr(s,"last_written",None),setattr(s,"hold_until",H*STATE['bars']+c["hold"])))}[m]   # FLASH to full, then spring back
        # Performance presses are immediate, even with quantization in old saved configs.
        s.pending=None;act()
    def release(s,owner=None):
        if owner is None:s.owners.clear()
        else:s.owners.discard(owner)
        if not s.owners and s.return_target is not None:
            s.held=False;s.target=s.return_target;s.return_target=None;s.pending=None;s.pulse_state=None
    def manual(s,value):
        FX_RELEASES.pop(s.key,None)
        s.pulse_state=None;s.pending=None;s.hold_until=None;s.return_target=None;s.owners.clear();s.held=False;s.target=value
    def cancel_pulse(s):
        if s.pulse_state:s.target=s.pulse_state['baseline'];s.pulse_state=None
    def pulse(s):
        baseline=s.pulse_state['baseline'] if s.pulse_state else s.target
        s.pending=None;s.hold_until=None
        s.pulse_state={'baseline':baseline,'stage':'attack','remaining':max(.016,float(s.cfg['pulse_hold']))}
        s.target=0. if baseline>.5 else 1.
    def step(s,dt,H):
        c=s.cfg
        if s.pending is not None and H*STATE['bars']>=s.pending: s.pending=None; s.pending_act()
        if c["mode"]=="oneshot" and s.hold_until is not None and H*STATE['bars']>=s.hold_until: s.target=0.0; s.hold_until=None
        if s.last_written is None:   # forced write (a flash)
            v=s.env*s.opmax
            if c["bypass0"] and s.id_bypass and getattr(s,'bypassed',False) and v>0.0005: put(s.id_bypass,False); s.bypassed=False
            put(s.id_opacity,v) if s.id_opacity else None; s.last_written=v
        pulse=s.pulse_state
        if pulse and abs(s.target-s.env)<1e-6:
            if pulse['stage']=='attack':pulse['stage']='hold'
            if pulse['stage']=='hold':
                pulse['remaining']-=dt
                if pulse['remaining']<=0:pulse['stage']='return';s.target=pulse['baseline']
            elif pulse['stage']=='return':s.pulse_state=None
        if abs(s.target-s.env)<1e-6: return
        duration=(c['pulse_return'] if pulse['stage']=='return' else c['pulse_attack']) if pulse else (c["attack"] if s.target>s.env else c["release"])
        rate=dt/max(0.01,duration)
        s.env=min(s.target,s.env+rate) if s.target>s.env else max(s.target,s.env-rate)
        v=s.env*s.opmax
        if s.last_written is None or abs(v-s.last_written)>1e-4:
            if c["bypass0"] and s.id_bypass and getattr(s,'bypassed',False) and v>0.0005: put(s.id_bypass,False); s.bypassed=False   # un-bypass BEFORE the first non-zero write
            put(s.id_opacity,v) if s.id_opacity else None; s.last_written=v
            if c["bypass0"] and s.id_bypass and v<=0.0005 and not getattr(s,'bypassed',False): put(s.id_bypass,True); s.bypassed=True
def load_fx():
    try: return json.load(open(FX_FILE))
    except Exception: return {}
def save_fx():
    json.dump({k:e.cfg for k,e in FX.items()},open(FX_FILE,"w"),indent=1)
def discover_fx(comp):
    seen=set()
    epoch=(comp.get("name") or {}).get("id")
    rows=list(targets.effects(comp))
    for li,l,lid in targets.named(comp.get('layers',[])):
        for ci,c,cid in targets.named(l.get('clips',[])):
            if not c.get('video') or not targets.connected(c):continue
            params=targets.controls(c['video'].get('sourceparams'))
            if is_sp(c):params={n:p for n,p in params.items() if p.get('valuetype') not in ('ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice')}
            if params:rows.append(('layer/'+lid+'/clip/'+cid+'/source','S',li+1,0,{'name':'Source · '+c['video'].get('description',''),'params':params}))
    for key,scope,layer,index,e in rows:
        if e.get('name')=='Transform': continue
        seen.add(key); params=targets.controls(e.get('params'))
        op=e.get('params',{}).get('Opacity'); byp=e.get('bypassed',{}).get('id')
        pid=op['id'] if op else None
        oldfx=FX.get(key); restore=None
        same=bool(oldfx is not None and epoch is not None and oldfx.composition_epoch==epoch and e.get('id') is not None and oldfx.native_identity==e.get('id'))
        changed=oldfx is not None and (oldfx.composition_epoch!=epoch or (oldfx.native_identity is not None and e.get('id') is not None and oldfx.native_identity!=e.get('id')))
        if oldfx is not None and (oldfx.id_opacity!=pid or changed):
            if same:restore=oldfx.return_target if oldfx.return_target is not None else oldfx.target
            oldfx.release(); del FX[key]
        if key not in FX:
            fx=FX[key]=Effect(key,scope,layer,index,e.get('display_name',e['name']),pid,byp,op.get('max',1.) if op else 1.)
            # Migrate positional configuration only when the old effect was unambiguous.
            old=load_fx().get(f"{scope}{layer or ''}/{index}")
            if old and scope in ('C','L'): fx.cfg.update(old)
            cur=0. if e.get('bypassed',{}).get('value') else (op['value']/max(1e-6,fx.opmax) if op else 1.)
            fx.env=fx.target=cur;fx.last_written=cur*fx.opmax
            fx.bypassed=bool(e.get('bypassed',{}).get('value'))
        fx=FX[key];fx.id_bypass=byp;fx.params=params
        fx.composition_epoch=epoch;fx.native_identity=e.get('id')
        if fx.motion is None:fx.motion=EffectMotion(fx)
        fx.motion.refresh(fx)
        fx.composition_epoch=epoch;fx.native_identity=e.get('id')
        pending=FX_RELEASES.pop(key,None)
        if restore is not None:fx.manual(restore)
        elif pending is not None and epoch is not None and pending[:2]==(epoch,e.get('id')) and e.get('id') is not None:fx.manual(pending[2])
        fx.colors={n:p for n,p in params.items() if p.get('valuetype')=='ParamColor'}
    for k in list(FX):
        if k not in seen:
            for sl in getattr(FX[k].motion,'slots',[]):OUT.discard(sl.ids[''])
            FX[k].release();del FX[k]
    for k in list(FX_RELEASES):
        if k not in seen:FX_RELEASES.pop(k,None)
    index_slot_owners()
def put(pid,v):
    OUT.put((pid,v))
SLOT_WRITERS={}
def index_slot_owners():
    global SLOT_WRITERS
    SLOT_WRITERS={sl.ids['']:sl for c in motion_controllers() for sl in c.slots if '' in sl.ids}
def ownership_allows_write(pid):
    sl=SLOT_WRITERS.get(pid)
    return sl is None or (getattr(sl,'owner','unverified')=='heart' and not sl.claim_inflight)
def release_native_slot(clip,sl,phase):
    changed=getattr(sl,'owner','unverified')!='resolume'
    sl.owner='resolume';sl.drive=False;sl.cfg['drive']=False;sl._lastout=None;sl._lastv=9.;OUT.discard(sl.ids[''])
    if changed:
        sl.retarget(clip.g,time.perf_counter())
        event(f"{clip.name}/{sl.name}: Resolume {phase} owns motion; Heart released")
def slot_display_value(sl,calculated):
    return getattr(sl,'observed',calculated) if getattr(sl,'owner','heart')!='heart' else calculated
def claim_slot(sl,force=False):
    with sl.ownership_lock:
        # Invalidate probes launched before every explicit performance intent.
        sl.claim_epoch+=1;epoch=sl.claim_epoch
        if hasattr(sl,'choices'):return
        if getattr(sl,'owner','heart')=='heart' and not force:return
        sl.claim_inflight+=1
    try:
        req=urllib.request.Request(f"{BASE}/parameter/by-id/{sl.ids['']}/phase-source",method='DELETE')
        urllib.request.urlopen(req,timeout=2).read()
        if 'Drive' in sl.ids:put_http(sl.ids['Drive'],False)
        with sl.ownership_lock:
            if sl.claim_epoch==epoch:
                sl.owner='heart';sl.native_phase='static';sl.phase_checked=time.monotonic();sl._lastout=None;sl._lastv=9.
    finally:
        with sl.ownership_lock:
            # Also invalidate reads begun during the native request.
            sl.claim_inflight-=1
            if not sl.claim_inflight:sl.claim_epoch+=1

def manual_parameter(p,v):
    if p.get('valuetype') in ('ParamEvent','ParamTrigger'):
        if v:arena_post(f"/parameter/by-id/{p['id']}/trigger")
        return
    matched=False
    for c in motion_controllers():
        for sl in c.slots:
            if sl.ids.get('')==p['id']:
                matched=True
                claim_slot(sl);sl.drive=False;sl.dur=0
                sl.cfg['manual']=(sl.choices.index(v)/max(1,len(sl.choices)-1)) if hasattr(sl,'choices') else (float(v)-getattr(sl,'pmin',0))/max(1e-9,getattr(sl,'pmax',1)-getattr(sl,'pmin',0))
                if sl.cyclic:sl.cfg['manual']=(sl.cfg['manual']-sl.rot)%1.
                sl.prev=None;sl.retarget(c.g,time.perf_counter());sl.prev=sl.target
    if not matched and p.get('valuetype') in ('ParamRange','ParamFloat','ParamInt','ParamNumber') and not p.get('_heart_manual'):
        req=urllib.request.Request(f"{BASE}/parameter/by-id/{p['id']}/phase-source",method='DELETE')
        urllib.request.urlopen(req,timeout=2).read();p['_heart_manual']=True
    put(p['id'],v);p['value']=v
def release_effects():
    for fx in list(FX.values()):
        fx.cancel_pulse();fx.last_written=None
        if fx.return_target is not None:FX_RELEASES[fx.key]=(fx.composition_epoch,fx.native_identity,fx.return_target)
        fx.release()

def configure_effect(fx,changes):
    cfg=dict(fx.cfg);cfg.update(changes)
    if cfg['mode'] not in ('latch','momentary','oneshot'):raise ValueError('Unknown effect mode')
    for key in ('attack','release','hold','quant','pulse_attack','pulse_hold','pulse_return'):
        value=float(cfg[key])
        if not math.isfinite(value) or not 0<=value<=128:raise ValueError('Invalid envelope timing')
        if key.startswith('pulse_') and not (.016 if key=='pulse_hold' else .01)<=value<=10:raise ValueError('Pulse timing must be within the displayed range')
        cfg[key]=value
    fx.release();fx.cfg=cfg;save_fx()
def request_reconnect():
    STATE["arena_connected"]=False
    release_effects()
    OUT.clear(); RECONNECT.set(); RESCAN.set()
    event("Reconnecting to Resolume…")

def ws_writer():
    async def run():
        while True:
            reader = None
            RECONNECT.clear()
            try:
                async with websockets.connect("ws://localhost:8080/api/v1",max_size=None) as ws:
                    STATE["arena_socket"]=True; RESCAN.set()
                    async def drain():
                        async for m in ws:
                            try:
                                obj=json.loads(m)
                                if isinstance(obj,dict) and 'layers' in obj:
                                    PUSHED["comp"]=obj; RESCAN.set()
                            except (ValueError,TypeError): pass
                    reader=asyncio.create_task(drain())
                    while not reader.done() and not RECONNECT.is_set():
                        generation=OUT.generation
                        for pid,v in (OUT.take(64) if STATE.get("arena_connected") else []):
                            if generation!=OUT.generation or not STATE.get("arena_connected"):break
                            if not ownership_allows_write(pid):continue
                            await ws.send(json.dumps({"action":"set","parameter":f"/parameter/by-id/{pid}","value":v}))
                        await asyncio.sleep(1/240)
                    if RECONNECT.is_set(): await ws.close()
                    await reader
            except Exception as e:
                print("[heart] ws writer reconnect:",e,flush=True)
            finally:
                if reader:
                    reader.cancel()
                    await asyncio.gather(reader,return_exceptions=True)
                STATE["arena_socket"]=False; STATE["arena_connected"]=False; release_effects();OUT.clear(); RESCAN.set()
            await asyncio.sleep(1)
    asyncio.new_event_loop().run_until_complete(run())
# ── status page: the seed of the control surface ──
STATE={"H":0,"bpm":0,"fps":0,"worst":0,"clips":[],"events":[],"bars":8,"hold":False,"arena_connected":False,'families':FAMILIES}   # bars per heart-turn (surface control)
TRANSPORT=Transport()
SURFACE_FILE=os.path.join(os.path.dirname(__file__),'surface.json')
try:
    with open(SURFACE_FILE) as f: STATE['surface']=json.load(f)
except (OSError,ValueError): STATE['surface']={}
MUTATIONS=ThreadPoolExecutor(max_workers=1,thread_name_prefix='heart-actions')
PATCH_ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'patches')
PATCH_OPS=Operations()
class UnconfirmedOpen(RuntimeError):pass
def arena_post(path,value=None):
    data=b'' if value is None else str(value).encode()
    req=urllib.request.Request(BASE+path,data=data,method='POST',headers={'Content-Type':'text/plain'})
    urllib.request.urlopen(req,timeout=8).read()
def patch_path(name):
    if not re.fullmatch(r'[\w -]{1,60}',name):raise ValueError('Use letters, numbers, spaces or hyphens for patch names')
    os.makedirs(PATCH_ROOT,exist_ok=True)
    return os.path.join(PATCH_ROOT,name)
def patch_states():
    result={}
    for c in list(CLIPS.values()):
        role=next((L['name'] for L in LAYERS if L['i']==c.layer+1),str(c.layer+1))
        key=role+'/'+c.name
        if key in result:raise ValueError('Ambiguous instrument name: '+key)
        result[key]=capture_state(c)
    return result
def patch_effect_states():
    result={}
    for key,e in list(FX.items()):
        if not e.motion:continue
        owned={sl.name for sl in e.motion.slots if getattr(sl,'owner','unverified')=='heart'}
        if owned:
            saved=capture_state(e.motion);saved['slots']={n:v for n,v in saved['slots'].items() if n in owned};result[key]=saved
    return result
def patch_layers(comp):
    result={}
    for l in comp['layers']:
        role=targets.label(l)
        if role in result:raise ValueError('Duplicate layer name: '+role)
        active=[targets.label(c) for c in l['clips'] if targets.connected(c)]
        if len(active)>1:raise ValueError('Wait for clip transition to finish')
        result[role]={'clip':active[0] if active else None,'level':l['video']['opacity']['value'],'bypass':l['bypassed']['value']}
    return result

def patch_save(name):
    from pathlib import Path
    base=patch_path(name)
    states=patch_states();effect_states=patch_effect_states();comp=get_comp();layers=patch_layers(comp)
    sources,effects=dependency_inventory()
    preflight=Path(PATCH_ROOT)/'_save_preflight.avc'
    capture_native_snapshot(preflight)
    contract=dependencies.build_contract(preflight,comp,layers)
    require_dependencies(contract,preflight,comp,sources,effects,preflight)
    arena_post('/composition/save',Path(base+'.avc').as_uri())
    data={'version':1,'name':name,'composition':Path(base+'.avc').name,'bars':STATE['bars'],'hold':STATE['hold'],'instruments':states,'effects':effect_states,'layers':layers,'signature':composition_signature(get_comp()),'dependencies':contract}
    tmp=base+'.json.tmp'
    with open(tmp,'w') as f:json.dump(data,f,indent=2)
    os.replace(tmp,base+'.json');event('Saved patch '+name)
def patch_names():
    from pathlib import Path
    return sorted(p.stem for p in Path(PATCH_ROOT).glob('*.json') if not p.name.startswith('_'))
def capture_native_snapshot(path):
    """Non-opening readback: save routing without leaving the verification name visible."""
    before=get_comp()['name']
    # A previous verification file must never stand in for a failed fresh save.
    path.unlink(missing_ok=True)
    try:
        arena_post('/composition/save',path.as_uri())
    finally:
        after=get_comp()['name']
        if after.get('id')!=before.get('id'):
            raise RuntimeError('Composition changed during routing readback')
        put_http(after['id'],before['value'])
def dependency_inventory():
    def read(kind):
        with urllib.request.urlopen(BASE+'/'+kind,timeout=5) as response:return json.load(response)
    return read('sources'),read('effects')
def require_dependencies(contract,snapshot,comp,sources,effects,observed=None):
    errors=dependencies.validate_contract(contract,snapshot,live_comp=comp,sources=sources,effects=effects,observed_snapshot_path=observed)
    if errors:raise ValueError('Patch dependencies: '+'; '.join(errors))
def patch_recall(name,token):
    from pathlib import Path
    base=patch_path(name)
    PATCH_OPS.progress(token,'Checking patch '+name)
    with open(base+'.json') as f:data=json.load(f)
    if data.get('version')!=1:raise ValueError('Unsupported patch version')
    snapshot=Path(base+'.avc')
    if not snapshot.is_file():raise ValueError('Composition snapshot missing')
    # Validate saved targets before opening anything. The composition snapshot owns routing.
    import xml.etree.ElementTree as ET
    validate_snapshot(snapshot,data['layers'])
    if 'signature' not in data:raise ValueError('Save this early prototype patch again to add composition verification')
    contract=data.get('dependencies') or dependencies.build_contract(snapshot,layers=data['layers'])
    sources,effects=dependency_inventory()
    require_dependencies(contract,snapshot,None,sources,effects)
    before=patch_states();before_effects=patch_effect_states();before_comp=get_comp();before_signature=composition_signature(before_comp);before_layers=patch_layers(before_comp);before_bars=STATE['bars'];before_hold=STATE['hold']
    recovery=Path(PATCH_ROOT)/'_recovery.avc'
    PATCH_OPS.progress(token,'Saving recovery snapshot')
    PATCH_OPS.write(token,arena_post,'/composition/save',recovery.as_uri())
    recovery_contract=dependencies.build_contract(recovery,before_comp,before_layers)
    opened=False
    def restore(path,states,layers,signature,contract,effect_states=None):
        nonlocal opened
        STATE['arena_connected']=False;OUT.clear()
        PATCH_OPS.progress(token,'Opening '+path.stem+' · waiting for Resolume')
        try:comp=open_verified(arena_post,get_comp,path,signature,lambda:PATCH_OPS.check(token))
        except (TimeoutError, OSError) as exc:
            raise UnconfirmedOpen('The requested composition could not be verified after opening. Inspect Resolume before retrying.') from exc
        opened=True
        comp=get_comp()
        for role,saved in layers.items():
            PATCH_OPS.progress(token,'Restoring layer '+role)
            found=[(i+1,l) for i,l in enumerate(comp['layers']) if targets.label(l)==role]
            if len(found)!=1:raise ValueError('Missing or ambiguous layer '+role)
            li,l=found[0]
            if saved['clip'] is None:PATCH_OPS.write(token,clear_layer,li)
            else:
                matches=[i+1 for i,c in enumerate(l['clips']) if c.get('video') and targets.label(c)==saved['clip']]
                if len(matches)!=1:raise ValueError('Missing or ambiguous clip '+role+'/'+saved['clip'])
                PATCH_OPS.write(token,connect_clip,li,matches[0])
            PATCH_OPS.write(token,put_http,l['video']['opacity']['id'],saved['level'])
            PATCH_OPS.write(token,put_http,l['bypassed']['id'],saved['bypass'])
        PATCH_OPS.progress(token,'Verifying native routing and required effects')
        observed=Path(PATCH_ROOT)/'_route_readback.avc'
        PATCH_OPS.write(token,capture_native_snapshot,observed)
        require_dependencies(contract,path,get_comp(),sources,effects,observed)
        request_reconnect()
        PATCH_OPS.progress(token,'Resolving controls · waiting for connection')
        end=time.monotonic()+15
        while time.monotonic()<end:
            PATCH_OPS.check(token)
            live={next((L['name'] for L in LAYERS if L['i']==c.layer+1),str(c.layer+1))+'/'+c.name:c for c in list(CLIPS.values()) if getattr(c,'taken',False)}
            live_effects={k:e.motion for k,e in list(FX.items()) if e.motion}
            if STATE.get('arena_connected') and set(states)<=set(live) and set(effect_states or {})<=set(live_effects):
                PATCH_OPS.progress(token,'Applying motion relationships')
                for key,state in states.items():PATCH_OPS.write(token,apply_state,live[key],state,'patch '+name)
                for key,state in (effect_states or {}).items():PATCH_OPS.write(token,apply_state,live_effects[key],state,'patch '+name)
                return
            time.sleep(.1)
        raise RuntimeError('Timed out resolving patch instruments')
    try:
        restore(snapshot,data['instruments'],data['layers'],data['signature'],contract,data.get('effects'))
        PATCH_OPS.write(token,STATE.update,{'bars':data.get('bars',8),'hold':data.get('hold',False)})
        event('Recalled patch '+name)
    except (Cancelled,UnconfirmedOpen):
        raise
    except Exception as exc:
        if opened:
            try:
                restore(recovery,before,before_layers,before_signature,recovery_contract,before_effects);PATCH_OPS.write(token,lambda:STATE.update(bars=before_bars,hold=before_hold))
            except Cancelled:raise
            except Exception as recovery_error:raise RuntimeError(f'{exc}; recovery incomplete: {recovery_error}') from exc
        raise RuntimeError(f'{exc}; '+('previous controllable state restored (feedback history cannot be restored)' if opened else 'no confirmed composition change')) from exc
    finally:
        OUT.clear()

WATCHERS=set()
def event(msg):
    STATE["events"].append(f"{time.strftime('%H:%M:%S')} {msg}"); STATE["events"]=STATE["events"][-40:]; print("[heart]",msg,flush=True)
PAGE=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"status.html")).read()
class H(SimpleHTTPRequestHandler):
    def do_GET(s):
        path=s.path.split('?',1)[0]
        files={'/':('status.html','text/html'),'/status.html':('status.html','text/html'),
               '/workspace.js':('workspace.js','text/javascript'),'/workspace.css':('workspace.css','text/css')}
        if path not in files:s.send_error(404);return
        filename,mime=files[path]
        page=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),filename),'rb').read()
        s.send_response(200);s.send_header("Content-Type",mime);s.send_header("Cache-Control","no-store");s.end_headers();s.wfile.write(page)
    def log_message(s,*a): pass
def validate_surface_target(d):
    """A gesture carries the instance it began on, never a replacement at that address."""
    expected=d.get('instance')
    if not expected:return
    if d['cmd'].startswith('fx_') or d.get('effect'):
        if d['cmd']=='fx_release':return  # release is routed through the owning surface
        current=FX.get(d.get('effect') or d.get('key'))
    else:
        current=CLIPS.get((d.get('layer',0)-1,d.get('col',0)-1))
    if current is None or current.instance!=expected:
        raise ValueError('Control target changed; select it again')
async def release_surface_controls(owned_holds,owned_fx,owner):
    # Clear ownership before awaits; a stale client release must not affect a
    # newly discovered effect or issue writes to a clip replaced by recall.
    effects=list(owned_fx.values());owned_fx.clear()
    holds=list(owned_holds.items());owned_holds.clear()
    for fx in effects:fx.release(owner)
    for (_,_,pad),c in holds:
        if not any(current is c for current in CLIPS.values()):continue
        try:await asyncio.get_running_loop().run_in_executor(MUTATIONS,preset_mom,c,pad,False)
        except Exception:pass

def status_server():
    threading.Thread(target=lambda: HTTPServer(("127.0.0.1",8765),H).serve_forever(),daemon=True).start()
    async def run():
        async def handler(ws):
            owned_holds={}; owned_fx={}
            WATCHERS.add(ws); print(f"[heart] surface connected ({len(WATCHERS)})",flush=True)
            try:
                async for m in ws:
                    print("[heart] surface cmd:",m[:120],flush=True)
                    try:
                        d=json.loads(m)
                        if d['cmd'] in ('performance_save','patch_save') and any(SHARED.value(getattr(sl,'shared_route',None),shared_token(sl),time.perf_counter()) is not None for c in motion_controllers() for sl in c.slots):
                            raise ValueError('Shared motion is a live prototype; stop shared routes before saving')
                        if d['cmd']=='mod_stop':
                            with LIVE_PRESET_LOCK:
                                for c in motion_controllers():
                                    for sl in c.slots:release_shared(sl)
                                SHARED.routes.clear()
                            continue
                        if d['cmd']=='mod_generator':
                            rate=float(d.get('speed',1))*float(d.get('mult',1))*RATIO_LIB[d.get('ratio','1:1')]
                            SHARED.configure(d['id'],rate,time.perf_counter(),float(d.get('seconds',1)));continue
                        if d['cmd']=='mod_bind':
                            if PATCH_OPS.busy or not STATE.get('arena_connected'):raise ValueError('Wait for connected controls')
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,bind_shared,d);continue
                        if d['cmd']=='mod_unbind':
                            with LIVE_PRESET_LOCK:
                                for c in motion_controllers():
                                    for sl in c.slots:
                                        if getattr(sl,'shared_route',None)==d['route']:release_shared(sl)
                                SHARED.remove(d['route'])
                            continue
                        if d['cmd'] in ('performance_save','performance_load','performance_undo'):
                            if PATCH_OPS.busy:raise ValueError('Wait for setup loading to finish')
                            if not STATE.get('arena_connected'):raise ValueError('Resolume disconnected')
                            fn={'performance_save':LIVE_PRESETS.save,'performance_load':LIVE_PRESETS.load,'performance_undo':LIVE_PRESETS.undo_last}[d['cmd']]
                            args=([d['name']] if d['cmd']!='performance_undo' else [])+([d.get('seconds',1)] if d['cmd']!='performance_save' else [])
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,fn,sys.modules[__name__],*args);continue
                        if d['cmd']=='patch_recall':PATCH_OPS.submit(lambda token,name=d['name']:patch_recall(name,token));continue
                        if d['cmd']=='patch_save':
                            if PATCH_OPS.busy:raise ValueError('Wait for recall to finish before saving')
                            PATCH_OPS.submit(lambda token,name=d['name']:PATCH_OPS.write(token,patch_save,name));continue
                        validate_surface_target(d)
                        if d['cmd'] not in ('surface_cfg','release_all','fx_release') and PATCH_OPS.busy:PATCH_OPS.cancel()
                        if d['cmd']=='reconnect': request_reconnect(); continue
                        if d['cmd']=='release_all':
                            await release_surface_controls(owned_holds,owned_fx,id(ws));continue
                        if d['cmd']=='tempo':
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,set_tempo,d['value']);continue
                        if d['cmd']=='tap_tempo':
                            value=TRANSPORT.tap()
                            if value is not None:await asyncio.get_running_loop().run_in_executor(MUTATIONS,set_tempo,value)
                            continue
                        if d['cmd']=='downbeat':
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,set_downbeat);continue
                        if d['cmd']=='fx_pulse':
                            FX[d['key']].pulse();continue
                        if d['cmd']=='fx_pair':
                            pair=[FX[k] for k in d['keys']]
                            if len(pair)!=2 or pair[0].layer!=pair[1].layer:raise ValueError('Invalid effect pair')
                            value=0. if any(e.target>.5 for e in pair) else 1.
                            for e in pair:e.manual(value)
                            continue
                        if d['cmd']=='fx_param':
                            fx=FX[d['key']];p=fx.params[d['name']];v=targets.convert(p,d['value'])
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,manual_parameter,p,v);continue
                        if d['cmd']=='fx_color':
                            fx=FX[d['key']]; color=fx.colors[d['name']]; value=str(d['value'])
                            if len(value)!=7 or value[0]!='#' or any(ch not in '0123456789abcdefABCDEF' for ch in value[1:]): raise ValueError('Invalid color')
                            color['value']=value+'ff'; put(color['id'],color['value']); continue
                        if d['cmd']=='fx_amount':
                            fx=FX[d['key']]; value=float(d['value'])
                            if not math.isfinite(value): raise ValueError('Invalid amount')
                            fx.manual(max(0.,min(1.,value))); continue
                        if d['cmd']=='fx_press': FX[d['key']].press(TRANSPORT.beats/4/STATE['bars'],id(ws)); owned_fx[d['key']]=FX[d['key']]; continue
                        if d['cmd']=='fx_release':
                            fx=owned_fx.pop(d['key'],None)
                            if fx is not None:fx.release(id(ws))
                            continue
                        if d['cmd']=='fx_cfg':configure_effect(FX[d['key']],d['cfg']);continue
                        if d['cmd']=='opacity':
                            L=next(x for x in LAYERS if x['i']==d['layer']); L['opacity']=float(d['value']); L['_hold']=time.time(); put(L['id_opacity'],float(d['value'])); continue
                        if d['cmd']=='clear':
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,clear_layer,int(d['layer']));continue
                        if d['cmd']=='bypass':
                            L=next(x for x in LAYERS if x['i']==d['layer']); L['bypass']=bool(d['on']); put_http(L['id_bypass'],bool(d['on'])); continue
                        if d['cmd']=='surface_cfg':
                            STATE['surface'].update(d['value'])
                            tmp=SURFACE_FILE+'.tmp'
                            with open(tmp,'w') as f: json.dump(STATE['surface'],f,indent=2)
                            os.replace(tmp,SURFACE_FILE); continue
                        if d['cmd']=='hold': STATE['hold']=bool(d['on']); continue
                        if d['cmd']=='bars':
                            value=float(d['bars'])
                            if not math.isfinite(value) or not .25<=value<=128:raise ValueError('Phrase must be between ¼ and 128 bars')
                            STATE['bars']=value;event(f"heart: 1 turn = {value:g} bars");continue
                        if d['cmd']=='clip_nav':
                            L=next(x for x in LAYERS if x['i']==d['layer']); cols=[c['col'] for c in (L.get('forms',[]) if L.get('bank')=='forms' else L.get('clips',[]))]
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
                        c=getattr(FX.get(d['effect']),'motion',None) if d.get('effect') else CLIPS.get((d['layer']-1,d['col']-1))
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
                            sl=[x for x in c.slots if x.name==d['slot']][0]
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,claim_slot,sl,bool(d['on']))
                            if not current_controller(c):raise ValueError('Control target changed')
                            sl.drive=bool(d['on']);sl.dur=c.morph;event(f"{c.name}/{sl.name}: drive {'on' if sl.drive else 'off'}"); sl.retarget(c.g,time.perf_counter())
                        elif d['cmd']=='morph': c.morph=float(d['seconds']); event(f"{c.name}: morph {c.morph:.1f}s")
                        elif d['cmd']=='home_set': await asyncio.get_event_loop().run_in_executor(MUTATIONS,set_home,c)
                        elif d['cmd']=='feedback_behavior':
                            if c.atom!='SPHeartFeedback':raise ValueError('Select the Heart feedback instrument')
                            c.history.append(capture_state(c));c.history=c.history[-20:]
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,apply_state,c,animated_home(capture_state(c),feedback.get(d['name'])),d['name']+' feedback')
                        elif d['cmd']=='feedback_reset':
                            if c.atom!='SPHeartFeedback' or 'Reset trails' not in c.sp:raise ValueError('Reset not available on this instrument')
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,manual_parameter,c.sp['Reset trails'],True)
                            event('Feedback reset sent · clears history on next rendered frame')
                        elif d['cmd']=='home': await asyncio.get_event_loop().run_in_executor(MUTATIONS,go_home,c,bool(d.get('factory',False)))
                        elif d['cmd']=='open': await asyncio.get_event_loop().run_in_executor(MUTATIONS,open_motion,c)
                        elif d['cmd']=='speed': await asyncio.get_event_loop().run_in_executor(MUTATIONS,motion_save,c,'speed',speed_value(d['value']))
                        elif d['cmd']=='choice':
                            sl=next(x for x in c.slots if x.name==d['slot']); options=getattr(sl,'choices',[])
                            if d['option'] not in options: raise ValueError('Unknown option')
                            c.history.append(capture_state(c)); c.history=c.history[-20:]
                            sl.drive=False; sl.cfg['manual']=options.index(d['option'])/max(1,len(options)-1); sl.prev=None
                        elif d['cmd']=='manual':
                            sl=[x for x in c.slots if x.name==d['slot']][0];v=float(d['value'])
                            if not math.isfinite(v):raise ValueError('Invalid parameter value')
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,claim_slot,sl)
                            if not current_controller(c):raise ValueError('Control target changed')
                            sl.drive=False;sl.cfg['manual']=(v-sl.rot)%1. if sl.cyclic else max(0.,min(1.,v));sl.dur=0;sl.retarget(c.g,time.perf_counter());sl.prev=sl.target
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
                            if d['key'] in ('Ratio','Mult','Offset','Shape'):await asyncio.get_running_loop().run_in_executor(MUTATIONS,motion_save,c,'timing_mode',None)
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda: wcfg(c,sl,d['key'],v,{}))
                        elif d['cmd']=='global_cfg':
                            await asyncio.get_running_loop().run_in_executor(MUTATIONS,motion_save,c,'timing_mode',None)
                            if d['key'] in ('Pattern','Seed','Spread'): await asyncio.get_event_loop().run_in_executor(MUTATIONS,motion_save,c,'relationship',None)
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,lambda: wglob(c,d['key'],d['value'],{}))
                        elif d['cmd']=='timing':
                            await asyncio.get_event_loop().run_in_executor(MUTATIONS,timing_fire,c,d['mode'])
                        elif d['cmd']=='good_set': await asyncio.get_event_loop().run_in_executor(MUTATIONS,axis_good_set,c,d['slot'])
                        elif d['cmd']=='good_go': await asyncio.get_event_loop().run_in_executor(MUTATIONS,axis_good_go,c,d['slot'])
                    except Exception as e: event("Control not applied: "+str(e))
            finally:
                WATCHERS.discard(ws)
                await release_surface_controls(owned_holds,owned_fx,id(ws))
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
EFFECT_RESUME={}
if os.environ.get('SP_RESUME_STATUS'):
    with open(os.environ['SP_RESUME_STATUS']) as f: resume=json.load(f)
    RESUME={(c['layer'],c['col']):c for c in resume['clips']}
    STATE['bars']=resume.get('bars',8)
    STATE['hold']=bool(resume.get('hold',False))
    STATE['H']=float(resume.get('H',0.))
    EFFECT_RESUME={e['key']:e for e in resume.get('fx',[]) if e.get('motion')}
    TRANSPORT.beats=float(resume.get('transport',{}).get('beats',0.))
def main():
    global TEMPO_ID
    H=STATE['H']; last=time.perf_counter(); clips={}; comp=get_comp(); TEMPO_ID=comp['tempocontroller']['tempo']['id']; bpm=comp['tempocontroller']['tempo']['value']
    frames=0; t_report=time.time(); lag=0.0
    def scan():
        # light loop (4 Hz): bpm + per-clip refresh of known clips. heavy loop (every 3 s): full composition to discover connections.
        nonlocal comp,bpm,clips
        global TEMPO_ID
        t_full=0; t_follow=0
        def rediscover(src):
            nonlocal comp,clips,size_ids
            global TEMPO_ID
            comp=src; live={}
            TEMPO_ID=comp['tempocontroller']['tempo']['id']
            size_ids=(comp['video']['width']['id'],comp['video']['height']['id'])
            for li,l in enumerate(comp['layers']):
                for ci,cc in enumerate(l['clips']):
                    if 'Connected' in str(cc['connected']['value']) and cc['video'] and is_sp(cc):
                        cc=dict(cc,_heart_layer_role=targets.label(l));key=(li,ci); old=clips.get(key)
                        if old and old.schema==clip_schema(cc): live[key]=old
                        else:
                            if old and old.name==cc['name']['value']:
                                RESUME[(li+1,ci+1)]={'slots':[{'name':sl.name,'drive':sl.drive,'v':sl.value(sl.blend(time.perf_counter()))} for sl in old.slots if sl.target]}
                            live[key]=Clip(li,ci,cc)
            for key,c0 in clips.items():
                if key not in live: event(f"released {c0.name!r}")
            OUT.clear()
            clips=live; CLIPS.clear(); CLIPS.update(live);index_slot_owners()
        size_ids=(comp['video']['width']['id'],comp['video']['height']['id']); last_size=[None]; t_size=[0.0]
        while True:
            try:
                # Refresh root IDs before any by-ID reads: those IDs also change on reload.
                if RESCAN.is_set() or time.time()-t_full>=3:
                    RESCAN.clear(); RESCAN_L.set()
                    rediscover(get_comp()); t_full=time.time()
                    t_follow=time.time()+1.4
                elif t_follow and time.time()>=t_follow:
                    t_follow=0; RESCAN_L.set(); rediscover(get_comp())
                bpm=get_bpm()
                if time.time()-t_size[0]>2.0:                # comp size poll (2 cheap by-id reads)
                    t_size[0]=time.time()
                    sz=tuple(json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{i}",timeout=1))['value'] for i in size_ids)
                    if sz!=last_size[0] and '--match-sizes' in sys.argv:
                        last_size[0]=sz
                        threading.Thread(target=match_clip_sizes,args=(get_comp(),),daemon=True).start()
                for (li,ci),c in list(clips.items()):
                  try:
                    cj=get_clip(li,ci)
                    if 'Connected' not in str(cj['connected']['value']):      # transition finished → clip left the layer
                        event(f"released {c.name!r}"); del clips[(li,ci)]; CLIPS.pop((li,ci),None);index_slot_owners(); continue
                    if c.schema!=clip_schema(cj):
                        RESUME[(li+1,ci+1)]={'slots':[{'name':sl.name,'drive':sl.drive,'v':sl.value(sl.blend(time.perf_counter()))} for sl in c.slots if sl.target]}
                        cj=dict(cj,_heart_layer_role=c.role);c=Clip(li,ci,cj); clips[(li,ci)]=c; CLIPS[(li,ci)]=c;index_slot_owners()
                        event(f"{c.name}: parameter layout refreshed; new controls start still")
                    c.refresh(cj)
                    if not c.taken: c.takeover(put); event(f"took over L{li+1}C{ci+1} {c.name!r}: {len(c.slots)} slots")
                  except Exception as e:
                    if '404' in str(e):                                   # Arena re-numbered its ids (reload / restart): forget and rediscover
                        event(f"{c.name}: ids gone (404) → rescan"); del clips[(li,ci)]; CLIPS.pop((li,ci),None);index_slot_owners()
                        try: rediscover(get_comp())
                        except Exception as e2: event(f"rescan failed: {e2}")
                        continue
                    if not getattr(c,'_warned',False): c._warned=True; event(f"{c.name}: skipped ({e}) — old clip instance? re-add it from the Sources tab")
                # layers strip
                if comp and (not LAYERS or RESCAN_L.is_set()):
                    RESCAN_L.clear(); LAYERS[:]=layer_rows(comp,LAYERS); discover_fx(comp)
                for L in LAYERS:
                    if time.time()-L.get('_hold',0)>0.6:      # don't fight a fader mid-drag
                        L['opacity']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_opacity']}",timeout=1))['value']
                    L['bypass']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_bypass']}",timeout=1))['value']
                    if L.get('id_ap'):
                        try: L['ap']=json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{L['id_ap']}",timeout=1)).get('index',0)
                        except Exception: pass
                    if L.get('_cids'):   # connected col: poll per-clip (the comp dump races the connect, so it can't be trusted for this)
                        readings=[]
                        for col,cid in L['_cids']:
                            try:
                                v=str(json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{cid}",timeout=1)).get('value',''))
                                readings.append((col,v))
                                if 'eviewing' in v:break
                            except Exception:readings.append((col,None))
                        update_connected_label(L,readings)
                if comp:
                    for L in LAYERS:
                        l=comp['layers'][L['i']-1]; L.setdefault('clip',next((c['name']['value'] for c in l['clips'] if 'Connected' in str(c['connected']['value'])),""))
                        L['clips']=[{"col":ci+1,"name":c['name']['value'],"source":c['video'].get('description')} for ci,c in enumerate(l['clips']) if c.get('video')]
                        L['forms']=instruments.bank(L['name'],L['clips'])
                        L['bank']=STATE['surface'].get('banks',{}).get(L['name'],'forms' if L['forms'] else 'all')
                        L['_cids']=[(ci+1,c['connected']['id']) for ci,c in enumerate(l['clips']) if c.get('video') and c['connected'].get('id')]
                        L.setdefault('ccol',next((ci+1 for ci,c in enumerate(l['clips']) if 'Connected' in str(c['connected']['value'])),0))
                        ap=l.get('autopilot',{}).get('target',{})
                        L['id_ap']=ap.get('id'); L.setdefault('ap',ap.get('index',0))
                if not STATE.get('arena_connected') and STATE.get('arena_socket'):
                    for c in motion_controllers():
                        for sl in c.slots: sl._lastv=9.; sl._lastout=None
                STATE['arena_connected']=bool(STATE.get('arena_socket')) and not RECONNECT.is_set()
            except Exception as e:
                STATE['arena_connected']=False; OUT.clear(); RESCAN.set()
                print("[heart] scan error:",e,flush=True)
            time.sleep(0.25)
    def read_phase(pid):
        return json.load(urllib.request.urlopen(f"{BASE}/parameter/by-id/{pid}/phase-source",timeout=1)).get('phase_source')
    observer=OwnershipObserver(
        clips=motion_controllers,
        available=lambda:bool(STATE.get('arena_connected')) and not PATCH_OPS.busy,
        generation=lambda:OUT.generation,
        current=lambda c,sl:current_controller(c) and any(x is sl for x in c.slots),
        read_phase=read_phase,release=release_native_slot)
    threading.Thread(target=observer.run,daemon=True,name='heart-ownership').start()
    threading.Thread(target=persist_atoms,daemon=True).start()
    threading.Thread(target=scan,daemon=True).start()
    threading.Thread(target=ws_writer,daemon=True).start()
    threading.Thread(target=status_server,daemon=True).start()
    print(f"[heart] running. bpm={bpm} (1 turn = 1 bar). status: http://localhost:8765",flush=True)
    step=1/FPS; next_t=time.perf_counter(); worst=0; next_status=0.0
    while True:
        now=time.perf_counter(); dt=now-last if last<now else step; last=now
        alignment=TRANSPORT.advance(dt,bpm)
        if alignment is not None:align_motion(alignment);H=0.
        dH=(0.0 if STATE['hold'] else min(.25,dt)*bpm/60.0/4.0/STATE['bars']); H+=dH  # 1 turn = N bars; integrate: speed/bars-change immune (kit law)
        t0=time.perf_counter(); snap=[]; publish=now>=next_status
        if publish: next_status=now+1/15
        SHARED.advance(dH,now)
        for c in list(clips.values()):
            if CLIPS.get((c.layer,c.col)) is not c:continue
            if c.auto>0 and not PATCH_OPS.busy:
                n=math.floor(H*STATE['bars']/c.auto)
                if c._auto_n is None: c._auto_n=n
                elif n!=c._auto_n: c._auto_n=n; MUTATIONS.submit(fire,c)
            if publish: cs={"instance":c.instance,"name":c.name,"layer":c.layer+1,"col":c.col+1,"pattern":FAMILIES[c.g['pattern']] if hasattr(c,'g') else '',"g":getattr(c,'g',{}),"instrument":instruments.summary(c.role,c.atom),"morph":c.morph,"home":bool(c.home),"feedback_behaviors":list(feedback.BEHAVIORS) if c.atom=="SPHeartFeedback" else [],"home_kind":"Home: saved pose" if c.home and c.home.get("sweet_home") else "Home: rest","arm":arm_json(c.arm),"auto":c.auto,"armsets":[k for k in load_armsets_cached().get(c.name,{}) if k!='_last'],"presets":sorted(load_presets_cached().get(c.name,{}).keys()),"preset_names":{k:v.get("label",f"Variation {k}") for k,v in load_presets_cached().get(c.name,{}).items()},"slots":[]}
            slot_snap=step_motion(c,dH,now,publish)
            if publish:cs['slots']=slot_snap
            if publish: snap.append(cs)
        fx_snap=[]
        for fx in list(FX.values()):
            c=fx.motion
            if c is not None:
                slots=step_motion(c,dH,now,publish)
                if publish:fx_snap.append((fx,{'slots':slots,'g':copy.deepcopy(c.g),'morph':c.morph,'home':bool(c.home),'home_kind':'Home: rest + off','arm':arm_json(c.arm)}))
            if not PATCH_OPS.busy and STATE.get('arena_connected'):fx.step(min(.25,dt),TRANSPORT.beats/4/STATE['bars'])
        worst=max(worst,time.perf_counter()-t0); frames+=1
        H_now[0]=H
        if publish: STATE.update({"H":round(H,3),"bpm":bpm,"transport":TRANSPORT.snapshot(STATE["bars"]),"modulation":SHARED.snapshot({shared_token(sl) for c in motion_controllers() for sl in c.slots if getattr(sl,"shared_route",None) and getattr(sl,"owner","heart")=="heart"}),"performance_presets":LIVE_PRESETS.names(),"performance_status":LIVE_PRESETS.status,"patches":patch_names(),"patch_recall_ready":bool(STATE.get("arena_connected")) and not PATCH_OPS.busy,"patch_status":PATCH_OPS.status,"patch_operation":PATCH_OPS.snapshot(),"clips":snap,"queue":OUT.qsize(),"delivery":OUT.metrics(),"layers":[{k:v for k,v in L.items() if not k.startswith('_') and not k.startswith('id_')} for L in LAYERS],
                      "fx":[{"binding":[e.composition_epoch,e.native_identity],"motion":motion,"pulsing":e.pulse_state is not None,"pulse_stage":e.pulse_state["stage"] if e.pulse_state else None,"instance":e.instance,"key":e.key,"scope":e.scope,"layer":e.layer,"lname":next((L['name'] for L in LAYERS if L['i']==e.layer),""),"name":e.name,"colors":e.colors,"params":e.params,"has_amount":e.id_opacity is not None,"env":round(e.env,3),"target":e.target,"pending":e.pending is not None,"bypassed":getattr(e,'bypassed',False),"cfg":e.cfg} for e,motion in fx_snap]})
        if time.time()-t_report>2:
            STATE["fps"]=round(frames/(time.time()-t_report),1); STATE["worst"]=round(worst*1000,2)
            print(f"[heart] H={H:8.3f}  bpm={bpm}  fps={STATE['fps']}  worst frame={STATE['worst']}ms  queue={OUT.qsize()}  clips={[c.name for c in clips.values()]}",flush=True); frames=0; t_report=time.time(); worst=0
        next_t+=step; d=next_t-time.perf_counter()
        if d>0: time.sleep(d)
        else: next_t=time.perf_counter()
if __name__=="__main__": main()
