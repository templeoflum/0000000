"""Read-only scoped Arena target discovery and strict value conversion.

Names plus occurrence distinguish repeated instances. Reordering unlike effects is
stable; swapping indistinguishable duplicates requires explicit rebinding.
"""
from urllib.parse import quote
from collections import Counter
import math


def label(obj, fallback=''):
    value=obj.get('name', fallback)
    return str(value.get('value', fallback) if isinstance(value, dict) else value)


def named(items):
    counts=Counter()
    for index, item in enumerate(items):
        name=label(item, str(index+1)); counts[name]+=1
        yield index, item, quote(name, safe='')+'~'+str(counts[name])


def connected(clip):
    return 'Connected' in str(clip.get('connected',{}).get('value',''))


def effect_groups(comp, active_only=True):
    yield 'composition', 'C', None, comp.get('video',{}).get('effects',[])
    for _, group, gid in named(comp.get('layergroups',comp.get('groups',[]))):
        yield 'group/'+gid, 'G', None, group.get('video',{}).get('effects',[])
    for li, layer, lid in named(comp.get('layers',[])):
        base='layer/'+lid
        yield base, 'L', li+1, layer.get('video',{}).get('effects',[])
        for ci, clip, cid in named(layer.get('clips',[])):
            if clip.get('video') and (not active_only or connected(clip)):
                yield base+'/clip/'+cid, 'K', li+1, clip['video'].get('effects',[])


def effects(comp, active_only=True):
    for base, scope, layer, items in effect_groups(comp,active_only):
        for index, effect, eid in named(items):
            yield base+'/effect/'+eid, scope, layer, index+1, effect


SUPPORTED={'ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice','ParamBool','ParamBoolean','ParamColor','ParamTrigger','ParamEvent'}


def controls(params):
    return {name:dict(p) for name,p in (params or {}).items()
            if isinstance(p,dict) and 'id' in p and p.get('valuetype') in SUPPORTED}


def convert(p, value):
    kind=p.get('valuetype')
    if kind=='ParamChoice':
        if value not in p.get('options',[]): raise ValueError('Unknown option')
        return value
    if kind in ('ParamBool','ParamBoolean','ParamTrigger','ParamEvent'):
        if not isinstance(value,bool): raise ValueError('Expected boolean')
        return value
    if kind=='ParamColor':
        if not isinstance(value,str) or len(value) not in (7,9) or value[0]!='#' or any(c not in '0123456789abcdefABCDEF' for c in value[1:]):
            raise ValueError('Expected hex color')
        return value+'ff' if len(value)==7 else value
    if kind not in ('ParamRange','ParamFloat','ParamInt','ParamNumber'): raise ValueError('Unsupported parameter')
    if isinstance(value,bool): raise ValueError('Expected number')
    value=float(value)
    if not math.isfinite(value): raise ValueError('Non-finite value')
    value=max(float(p.get('min',value)),min(float(p.get('max',value)),value))
    return round(value) if kind in ('ParamInt','ParamNumber') else value


def inventory(comp):
    """All typed source/effect targets, including inactive clips, for recall preflight."""
    result={}
    for key,scope,layer,index,effect in effects(comp,False):
        for name,p in controls(effect.get('params')).items():
            result[key+'/param/'+quote(name,safe='')]=p
        bypass=effect.get('bypassed')
        if bypass and 'id' in bypass:result[key+'/bypass']=dict(bypass,valuetype='ParamBool')
    for li,l,lid in named(comp.get('layers',[])):
        base='layer/'+lid
        for field,p in [('level',l.get('video',{}).get('opacity')),('bypass',l.get('bypassed'))]:
            if p and 'id' in p:result[base+'/'+field]=dict(p,valuetype='ParamBool' if field=='bypass' else 'ParamRange',min=0,max=1)
        for ci,c,cid in named(l.get('clips',[])):
            if not c.get('video'):continue
            for name,p in controls(c['video'].get('sourceparams')).items():
                result[base+'/clip/'+cid+'/source/'+quote(name,safe='')]=p
    return result
