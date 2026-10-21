"""Reference clip programs and bounded variations of their native timelines."""
import copy, math, random
from smart_motion import RATIO_LIB

NUM={'ParamRange','ParamFloat','ParamInt','ParamNumber'}

def equal(a,b):
    if type(a) is bool or type(b) is bool:return a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-5)
    return a==b

def xml_program(p, native):
    """Only serialized controls are authoritative; never invent missing defaults."""
    kind=native['valuetype'];raw=p.get('value',p.get('default'))
    if raw is None:return None
    if kind in NUM:value=float(raw)
    elif kind=='ParamChoice':
        index=int(raw)
        if not 0<=index<len(native.get('options',[])):return None
        value=native['options'][index]
    elif kind in ('ParamBool','ParamBoolean'):value=raw not in ('0','false')
    elif kind=='ParamColor':
        if any(x.tag.startswith('PhaseSource') and x.tag!='PhaseSourceStatic' for x in p.iter()):return None
        color=int(raw);value='#'+''.join(f'{(color>>shift)&255:02x}' for shift in (0,8,16,24))
    else:return None
    out=dict(id=native['id'],name=p.get('name'),type=kind,min=native.get('min',0),max=native.get('max',1),value=value)
    if kind not in NUM:return out
    if not out['min']<=value<=out['max']:return None
    phase=next((x for x in p if x.tag.startswith('PhaseSource')),None)
    source=phase.tag if phase is not None else 'PhaseSourceStatic'
    if source not in ('PhaseSourceStatic','PhaseSourceTimeline'):return None
    out['source']='timeline' if source=='PhaseSourceTimeline' else 'static'
    bounds=p.find('./ValueRange[@name="startStop"]')
    out['in']=float(bounds.get('min')) if bounds is not None else out['min']
    out['out']=float(bounds.get('max')) if bounds is not None else out['max']
    if not all(out['min']<=out[k]<=out['max'] for k in ('in','out')):return None
    if source=='PhaseSourceTimeline':
        duration=p.find('DurationSource')
        seconds=float(duration.get('userDuration','5')) if duration is not None else 5.
        fields=dict(Duration=seconds,Speed=1.,PlayMode='Loop',PlayDirection='>',DurationIsScalable=True)
        choices={'PlayMode':['Loop','Bounce','Random','Play Once & Clear','Play Once & Hold'],'PlayDirection':['<','||','>']}
        for x in phase.findall('./Params/*'):
            name=x.get('name');v=x.get('value',x.get('default'))
            if v is None or name=='BPM':continue
            if name in choices:v=choices[name][int(v)]
            elif x.get('T')=='BOOL':v=v not in ('0','false')
            else:v=float(v)
            fields[name]=v
        if fields['DurationIsScalable'] and duration is not None:fields['Duration']*=float(duration.get('scale','1'))
        out.update(fields=fields,phase=float(phase.get('phase','0')))
    return out

def variation(programs, action, rate=1, rng=random):
    """Move existing timing pairs within compatible loops; keep each range/shape."""
    result=copy.deepcopy(programs)
    if action not in ('original','shuffle','rate','resume','pause'):raise ValueError('Unknown original-clip action')
    if not isinstance(rate,(float,int)) or isinstance(rate,bool) or rate not in (.125,.25,.5,1,2,4,8):raise ValueError('Choose a musical rate')
    loops=[p for p in result if p.get('source')=='timeline']
    if action=='shuffle':
        buckets={}
        for p in loops:
            if p['fields']['PlayMode'] in ('Loop','Bounce'):
                buckets.setdefault(p['fields']['PlayMode'],[]).append(p)
        for members in buckets.values():
            timing=[(p['fields']['Duration'],p['fields']['Speed']) for p in members];rng.shuffle(timing)
            for p,(duration,speed) in zip(members,timing):
                p['fields'].update(Duration=duration,Speed=speed);p['phase']=rng.random()
    for p in loops:
        p['fields']['Duration']/=rate
        if p['fields']['PlayMode']=='Random':
            for key in ('Max Distance','Interval'):
                if key in p['fields']:p['fields'][key]/=rate
        if not .001<=p['fields']['Duration']<=604800:raise ValueError('Original timing exceeds native limits at this rate')
        if action=='pause':p['fields']['PlayDirection']='||'
    return result if action=='original' else loops

class Authored:
    def __init__(self,data=None):
        self.data=data or {};self.profiles=self.data.get('clips',{});self.runtime={};self.rates={};self.paused=set();self.busy=set();self.directions={}
    def profile(self,catalog,clip_id):
        if catalog['epoch']!=self.data.get('epoch'):return None
        return self.profiles.get(str(clip_id))
    def targets(self,catalog,clip_id):
        profile=self.profile(catalog,clip_id)
        if not profile:raise ValueError('No matching original clip program')
        result=[];actual={t['id']:t for t in catalog['targets']}
        for t in profile['targets']:
            live=actual.get(t['id'])
            if not live or [live.get(k) for k in ('kind','scope','layer_id','clip_id','effect_name')]!=t['identity']:raise ValueError('Original clip destination changed')
            params={p['id']:p for p in live['params']}
            for p in t['params']:
                q=params.get(p['id'])
                if not q or any(q.get(k)!=p.get(k) for k in ('name','type','min','max')):raise ValueError('Original clip parameter changed')
            result.append(t)
        return result
    def annotate(self,catalog):
        for t in catalog['targets']:
            profile=self.profile(catalog,t.get('clip_id'))
            if not profile:continue
            try:targets=self.targets(catalog,t['clip_id'])
            except ValueError:continue
            reference=next((x for x in targets if x['id']==t['id']),None)
            if targets:
                t['authored']=dict(clip_id=t['clip_id'],reference=profile['reference'],loops=sum(p.get('source')=='timeline' for x in targets for p in x['params']))
                native={p['id']:p for p in (reference or {}).get('params',[])}
                for p in t['params']:
                    if p['id'] in native:p['authored']=native[p['id']]
    def plans(self,engine,clip_id,action,rate=1,ids=None):
        targets=self.targets(engine.catalog,clip_id)
        parameters=[p for t in targets for p in t['params'] if ids is None or p['id'] in ids]
        if action!='original' and ids is None:parameters=[p for p in parameters if not engine.slots.get(p['id']) or not engine.slots[p['id']].cfg.get('lock')]
        if action=='shuffle':parameters=[p for p in parameters if p['id'] not in self.paused and p['id'] not in engine.owned]
        if action=='rate':parameters=[p for p in parameters if p['id'] not in engine.owned]
        base=self.runtime.get(str(clip_id),{}) if action in ('shuffle','rate','pause','resume') else {}
        parameters=[copy.deepcopy(base.get(str(p['id']),p)) for p in parameters]
        return variation(parameters,action,rate)

def heart_seed(p, bpm=120):
    """Translate an authored sweep into Heart controls; bounds stay exact."""
    ref=p.get('authored',{});span=p['max']-p['min']
    if not ref:return None
    timeline=ref.get('source')=='timeline'
    value=max(p['min'],min(p['max'],ref.get('value',p['value'])))
    low,high=sorted((ref.get('in',p['min']),ref.get('out',p['max']))) if timeline else (value,value)
    low=max(p['min'],min(p['max'],low));high=max(low,min(p['max'],high))
    fields=ref.get('fields',{});period=max(1.,min(256.,fields.get('Duration',16)*(2 if fields.get('PlayMode')=='Bounce' else 1)))
    wanted=32*60/max(20,bpm)/period
    ratio,mult=min(((r,m) for r in RATIO_LIB for m in (1,2,4,8,16)),key=lambda pair:abs(math.log2(max(1e-9,RATIO_LIB[pair[0]]*pair[1]/wanted))))
    if fields.get('PlayDirection')=='<':mult=-mult
    return dict(lo=(low-p['min'])/span,hi=(high-p['min'])/span,manual=(max(low,min(high,value))-p['min'])/span,ratio=ratio,mult=mult,offset=ref.get('phase',0)%1,shape=.8,drive=timeline and high>low)
