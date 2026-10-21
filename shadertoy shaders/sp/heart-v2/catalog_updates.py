"""Small catalogue changes; clip grids and unrelated targets stay shared."""


def merge_patches(first, second):
    """Apply changes in order, retaining only the latest target/layer state."""
    if first['epoch'] != second['epoch']: raise ValueError('Catalogue epoch changed')
    targets = {t['id']: t for t in first.get('targets', [])}
    removed = set(first.get('remove', []))
    for tid in second.get('remove', []): targets.pop(tid, None); removed.add(tid)
    for target in second.get('targets', []): targets.pop(target['id'], None); targets[target['id']] = target
    layers = {l['id']: l for l in first.get('layers', [])}
    for layer in second.get('layers', []): layers[layer['id']] = dict(layers.get(layer['id'], {}), **layer)
    result = dict(epoch=first['epoch'], remove=sorted(removed), targets=list(targets.values()), layers=list(layers.values()), stage_only=bool(first.get('stage_only') and second.get('stage_only')))
    if 'native_phase_mode' in first or 'native_phase_mode' in second: result['native_phase_mode'] = second.get('native_phase_mode', first.get('native_phase_mode'))
    return result


def clip_patch(before, after, layer_id):
    old=[t for t in before['targets'] if t.get('scope')=='clip' and t.get('layer_id')==layer_id]
    new=[t for t in after['targets'] if t.get('scope')=='clip' and t.get('layer_id')==layer_id]
    layer=next(l for l in after['layers'] if l['id']==layer_id)
    return dict(epoch=after['epoch'], remove=[t['id'] for t in old], targets=new,
                layers=[dict(id=layer_id,active=layer['active'])], stage_only=bool(layer.get('stage')))


def apply_patch(catalog, patch):
    if patch['epoch']!=catalog['epoch']:
        raise ValueError('Catalogue epoch changed')
    replaced=set(patch.get('remove',[]))|{t['id'] for t in patch.get('targets',[])}
    layers={l['id']:l for l in patch.get('layers',[])}
    result=dict(catalog,targets=[t for t in catalog['targets'] if t['id'] not in replaced]+patch.get('targets',[]),
                layers=[dict(l,**{k:v for k,v in layers[l['id']].items() if k!='id'}) if l['id'] in layers else l for l in catalog['layers']])
    for layer in result['layers']:
        if layer['id'] in layers and 'active' in layers[layer['id']]:layer.pop('pending_clip',None)
    if 'native_phase_mode' in patch:result['native_phase_mode']=patch['native_phase_mode']
    return result
