"""Read-only parameter inventory from the existing whole-composition snapshot."""
SLOT_TYPES={'ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice'}
CONTROL_TYPES=SLOT_TYPES|{'ParamBoolean','ParamEvent','ParamTrigger'}
def exposed(params):
    return {n:p for n,p in (params or {}).items() if isinstance(p,dict) and p.get('valuetype') in CONTROL_TYPES and 'id' in p}
def source_has_controls(clip):
    return bool(exposed((clip.get('video') or {}).get('sourceparams')))
def build(comp):
    rows=[]
    for li,layer in enumerate(comp.get('layers',[]),1):
        for col,clip in enumerate(layer.get('clips',[]),1):
            video=clip.get('video')
            if not video:continue
            controls=[]
            for name,p in exposed(video.get('sourceparams')).items():
                kind=p['valuetype'];controls.append(dict(name=name,id=p['id'],type=kind,min=p.get('min'),max=p.get('max'),options=p.get('options'),mode='momentary' if kind in ('ParamEvent','ParamTrigger') else 'toggle' if kind=='ParamBoolean' else 'choice' if kind=='ParamChoice' else 'continuous'))
            rows.append(dict(layer=li,col=col,clip_id=clip.get('id'),name=clip.get('name',{}).get('value',''),source=video.get('description'),active=str(clip.get('connected',{}).get('value','')).startswith('Connected'),parameters=controls))
    return dict(clips=rows,clip_count=len(rows),parameter_count=sum(len(r['parameters']) for r in rows),scope='Resolume-exposed source parameters; inactive clips are catalogued, not driven')
