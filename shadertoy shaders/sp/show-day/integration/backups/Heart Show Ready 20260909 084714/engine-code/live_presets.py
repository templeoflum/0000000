"""JSON-only performance recall. No composition IO, discovery or reconnect."""
import copy,json,math,re,time
from pathlib import Path

class Store:
    def __init__(self,root):self.root=Path(root);self.status='';self.undo=None;self._names=[];self._listed=0
    def path(self,name):
        if not re.fullmatch(r'[\w -]{1,60}',name):raise ValueError('Use letters, numbers, spaces or hyphens')
        return self.root/(name+'.json')
    def names(self):
        if time.monotonic()-self._listed>2:
            self._names=sorted(p.stem for p in self.root.glob('*.json'));self._listed=time.monotonic()
        return self._names
    def controllers(self,h):
        out={}
        for c in list(h.CLIPS.values()):
            role=next((l['name'] for l in h.LAYERS if l['i']==c.layer+1),str(c.layer+1))
            key='source/'+role+'/'+c.name
            if key in out:raise ValueError('Ambiguous source '+key)
            out[key]=c
        out.update({k:e.motion for k,e in list(h.FX.items()) if e.motion})
        return out
    def capture(self,h):
        states={}
        for key,c in self.controllers(h).items():
            saved=h.capture_state(c)
            if hasattr(c,'effect_key'):
                owned={sl.name for sl in c.slots if getattr(sl,'owner','unverified')=='heart'}
                saved['slots']={k:v for k,v in saved['slots'].items() if k in owned}
            if saved['slots']:states[key]=saved
        return {'version':1,'kind':'heart-performance','targets':states,
                'amounts':{k:e.target for k,e in list(h.FX.items()) if e.id_opacity is not None}}
    def save(self,h,name):
        path=self.path(name);data=self.capture(h);data['name']=name
        self.root.mkdir(exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,allow_nan=False));tmp.replace(path)
        self._listed=0;self.status='Saved '+name;h.event(self.status)
    def load(self,h,name,seconds=1):
        data=json.loads(self.path(name).read_text());self.apply(h,data,seconds)
        self.status='Applied '+name+(' · '+self.status if self.status else '');h.event(self.status)
    def apply(self,h,data,seconds=1):
        if data.get('version')!=1 or data.get('kind')!='heart-performance':raise ValueError('Not a performance preset')
        seconds=float(seconds)
        if not math.isfinite(seconds) or not 0<=seconds<=30:raise ValueError('Transition must be 0–30 seconds')
        live=self.controllers(h);plan=[];skipped=[]
        for key,saved in data['targets'].items():
            c=live.get(key)
            if c is None:skipped.append(key);continue
            g=copy.deepcopy(saved['global']);h.speed_value(g.get('speed',1))
            if not all(isinstance(v,(int,float)) and math.isfinite(v) for k,v in g.items() if k not in ('relationship','timing_mode')):raise ValueError('Invalid motion settings')
            slots=[]
            for name,v in saved['slots'].items():
                matches=[sl for sl in c.slots if v.get('identity',name)==getattr(sl,'identity',sl.name)]
                if len(matches)!=1:skipped.append(key+'/'+name);continue
                sl=matches[0];cfg=copy.deepcopy(v['config'])
                for k in ('manual','mult','offset','shape','lo','hi'):
                    if not isinstance(cfg.get(k), (int,float)) or not math.isfinite(cfg[k]):raise ValueError('Invalid '+name+'/'+k)
                if cfg['ratio'] not in h.RATIO_LIB or not 0<=cfg['lo']<=cfg['hi']<=1 or cfg['shape'] not in (0,1) or not math.isfinite(v['pose']):raise ValueError('Invalid parameter relationship '+name)
                slots.append((sl,cfg,v))
            if slots:plan.append((c,g,slots))
        amounts=[]
        for key,value in data.get('amounts',{}).items():
            if not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1:raise ValueError('Invalid effect amount')
            e=h.FX.get(key)
            if e is None:skipped.append(key);continue
            if abs(e.target-value)>1e-6:amounts.append((e,value,e.instance))
        # Ownership IO happens before the short commit; existing Heart drives keep running.
        previous=self.capture(h)
        preparing=[sl for c,g,slots in plan for sl,cfg,v in slots if getattr(sl,'owner','heart')!='heart']
        for sl in preparing:sl.preset_preparing=True
        try:
            for c,g,slots in plan:
                for sl,cfg,v in slots:
                    if getattr(sl,'owner','heart')!='heart':
                        h.claim_slot(sl,force=False)
            if any(not h.current_controller(c) or any(sl not in c.slots for sl,_,_ in slots) for c,_,slots in plan) or any(h.FX.get(e.key) is not e or e.instance!=i for e,v,i in amounts):raise ValueError('Targets changed; preset not applied')
            now=time.perf_counter()
            with h.LIVE_PRESET_LOCK:
                for c,g,slots in plan:
                    c.morph=seconds;c.g.update(g)
                    for sl,cfg,v in slots:
                        sl.dur=seconds;sl.cfg.update(cfg);sl.drive=bool(v['drive'])
                        sl.cfg['manual']=(v['pose']-sl.rot)%1 if sl.cyclic else v['pose']
                        sl.retarget(c.g,now)
                    c.auto=0;c._auto_n=None
                for e,value,_ in amounts:e.manual(value)
            # Keep restart state durable with one batch, after the motion commit.
            h.persist_performance(plan)
            self.undo=previous;self.status=('Skipped '+', '.join(skipped)) if skipped else ''
            return {'targets':len(plan),'skipped':skipped}
        finally:
            for sl in preparing:sl.preset_preparing=False

    def undo_last(self,h,seconds=1):
        if self.undo is None:return
        data=self.undo;self.apply(h,data,seconds);self.status='Preset undone';h.event(self.status)
