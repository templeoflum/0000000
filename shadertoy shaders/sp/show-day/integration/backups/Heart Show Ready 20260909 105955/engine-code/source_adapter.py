"""Schema-driven Open selection and captured recovery poses for existing Smart Params.

No oscillator, timer, or source-specific recipes. Names are heuristics, not visual
certification. Explicit profiles and saved user Homes remain authoritative.
"""
import hashlib,json,math,os,re

def classify(slot, role=''):
    name=re.sub(r'[^a-z0-9]+',' ',slot.name.lower()).strip();words=set(name.split())
    if getattr(slot,'owner','heart')!='heart':return 'external'
    if getattr(slot,'choices',[]) or getattr(slot,'integer',False) or getattr(slot,'kind','') in ('ParamBoolean','ParamChoice','ParamTrigger','ParamInt','ParamNumber'):return 'discrete'
    if words & {'seed','trigger','reset','random','count','iterations','quality','samples','subdivision','subdivisions'}:return 'discrete'
    if words & {'speed','rate','time','timescale','bpm','tempo'}:return 'clock'
    if words & {'camera','cam','fov','azimuth','elevation','pitch','yaw','zoom'}:return 'framing'
    if role=='figure' and words & {'x','y','size','scale','position','distance','translate','translation'}:return 'framing'
    lo,hi=getattr(slot,'pmin',0.),getattr(slot,'pmax',1.)
    if not all(math.isfinite(v) for v in (lo,hi)) or hi<=lo:return 'invalid'
    if words & {'warp','morph','fold','twist','thickness','width','distortion','strength','phase','intensity'}:return 'structure'
    if words & {'hue','saturation','tint','color','colour','glow'}:return 'color'
    return 'continuous'

def selected(clip):
    rank={'structure':0,'color':1,'continuous':2}
    eligible=[(rank[k],i,s.name) for i,s in enumerate(clip.slots) if (k:=classify(s,getattr(clip,'role',''))) in rank]
    return {name for _,_,name in sorted(eligible)[:3]}

def settings(clip,slot,pose):
    if slot.name not in selected(clip):return {'drive':False,'manual':pose}
    # A bounded first gesture around the current pose; native normalization handles
    # differing units. Leave all existing timing/relationship settings intact.
    pose=max(0.,min(1.,pose));lo=max(0.,pose-.15);hi=min(1.,pose+.15)
    return {'drive':True,'lo':lo,'hi':hi,'lock':False}

def key(clip):
    schema=[(getattr(s,'identity',s.name),s.name,getattr(s,'kind',''),getattr(s,'pmin',0.),getattr(s,'pmax',1.),getattr(s,'integer',False),getattr(s,'choices',[])) for s in clip.slots]
    signature=[getattr(clip,'role',''),getattr(clip,'atom',None) or clip.name,getattr(clip,'layer',None),getattr(clip,'col',None),schema]
    return hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()

class Homes:
    def __init__(self,path):
        self.path=path
        try:
            with open(path) as f:self.data=json.load(f)
        except (OSError,ValueError):self.data={}
    def profile(self,clip):return dict(self.data.get(key(clip),{}).get('static',{}))
    def remember(self,clip,pose):
        k=key(clip)
        if k in self.data:return False
        static={n:v['pose'] for n,v in pose['slots'].items() if math.isfinite(v['pose'])}
        record={'source':clip.name,'basis':'captured before first Open; not visual certification','static':static}
        data=dict(self.data);data[k]=record
        tmp=self.path+'.tmp'
        with open(tmp,'w') as f:json.dump(data,f,indent=2)
        os.replace(tmp,self.path);self.data=data;return True
