"""Portable relationship recipes; physical parameter ranges belong to clip bindings."""
import copy, math

def recipe_rate(recipe, name, fallback_index):
    index=recipe.get('members',{}).get(name,fallback_index)
    if recipe['kind']=='pendulum':
        base=max(1,float(recipe.get('base',17)))
        return (base+index*float(recipe.get('step',1)))/base
    raise ValueError('Unknown relationship recipe')

def animated_home(state, profile):
    out=copy.deepcopy(state)
    members={name:i for i,name in enumerate(profile['bindings'])}
    out['global'].update(pattern=0,seed=0,spread=1,depth=1.,fm=0.,speed=profile.get('speed',.25),
                         relationship={'kind':'pendulum','base':17,'step':1,'members':members})
    for name,saved in out['slots'].items():
        binding=profile['bindings'].get(name)
        saved['drive']=bool(binding)
        if not binding:continue
        cfg=saved['config']; lo,hi=binding['range']; center=binding['center']
        shape=binding.get('shape',1)
        cfg.update(ratio='1:1',mult=1.,offset=members[name]/max(len(members),1),shape=shape,lo=lo,hi=hi,lock=False)
        # A cyclic sway is an additive offset from the manual pose, unlike a bounded scalar.
        saved['pose']=(center-(hi-lo)/2)%1 if binding.get('cyclic') and shape==1 else center
    return out

def speed_value(value):
    value=float(value)
    if not math.isfinite(value) or not .0625<=value<=16:raise ValueError('Speed must be between 1/16× and 16×')
    return value
