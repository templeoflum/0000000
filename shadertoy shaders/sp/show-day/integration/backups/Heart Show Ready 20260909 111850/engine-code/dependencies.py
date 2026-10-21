"""Offline, versioned active-patch dependency checks. No transport or mutations.

build_contract(path, live_comp=None, layers=patch['layers']) -> JSON-safe dict.
validate_contract(contract, path, live_comp=None, sources=None, effects=None,
                  observed_snapshot_path=None) -> list[str] (empty means passed).
Inventory arguments are mandatory evidence for validation. REST route omission
fails live validation unless a fresh, independently saved native snapshot is given.
"""
import re
import xml.etree.ElementTree as ET


class ContractError(ValueError):
    pass


def _value(x):
    return x.get('value') if isinstance(x, dict) else x


def _name(x):
    return _value(x.get('name'))


def _xml_name(x):
    p = x.find('Params/Param[@name="Name"]')
    return p.get('value') if p is not None else x.get('name')


def _unique(items, key, context):
    out = {}
    for item in items:
        k = key(item)
        if k in out:
            raise ContractError(f'{context}: duplicate identity {k}')
        out[k] = item
    return out


def _identifier(s):
    # UUID spelling alone is case-insensitive. Never strip prefixes (e.g. c_),
    # remove whitespace, or infer identity from a display label.
    if re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', s or ''):
        return s.lower()
    return s


def _effects(node):
    result = []
    for e in node.findall('VideoTrack/RenderPass/RenderPass'):
        uid = e.get('uniqueTypeId')
        if not uid:
            raise ContractError('Effect native identifier missing')
        result.append({'name': e.get('name'), 'id': _identifier(uid)})
    return result


def _dimensions(node):
    return [float(node.get(k)) for k in ('width', 'height')]


def _xml_contract(path, layers):
    root = ET.parse(path).getroot()
    ordered_layers = sorted(root.findall('Layer'), key=lambda l: int(l.get('layerIndex')))
    _unique(ordered_layers, lambda l: l.get('layerIndex'), 'layer indices')
    xml_layers = _unique(ordered_layers, _xml_name, 'layers')
    if not isinstance(layers, dict):
        raise ContractError('Saved layers mapping required')
    layers = {name: {'clip': settings.get('clip')} for name, settings in layers.items()}
    groups = []
    for i, g in enumerate(root.findall('Group')):
        groups.append({'index': i, 'members': [n for n, l in xml_layers.items()
                       if l.get('layerGroup') == str(i)], 'effects': _effects(g)})
    info = root.find('CompositionInfo')
    if info is None:
        raise ContractError('Composition dimensions unavailable')
    result = {'version': 1, 'layers': layers, 'dimensions': _dimensions(info),
              'layer_order': list(xml_layers), 'groups': groups, 'composition_effects': _effects(root),
              'layer_effects': {n: _effects(l) for n, l in xml_layers.items()},
              'instruments': []}
    decks = [d for d in root.findall('Deck') if d.get('deckIndex', '0') == root.get('currentDeckIndex', '0')]
    if len(decks) != 1:
        raise ContractError('Current deck missing or ambiguous')
    clips = decks[0].findall('Clip')
    for name, settings in layers.items():
        if name not in xml_layers:
            raise ContractError(f'Layer missing: {name}')
        wanted = settings.get('clip')
        if not wanted:
            continue
        layer = xml_layers[name]
        matches = [c for c in clips if c.get('layerIndex') == layer.get('layerIndex')
                   and _xml_name(c) == wanted]
        if len(matches) != 1:
            raise ContractError(f'{name}/{wanted}: clip missing or ambiguous')
        clip = matches[0]
        source = clip.find('VideoTrack/PrimarySource/VideoSource')
        if source is None:
            raise ContractError(f'{name}/{wanted}: video source unavailable')
        kind = source.get('type')
        item = {'layer': name, 'clip': wanted, 'dimensions': _dimensions(source),
                'effects': _effects(clip), 'source_type': kind}
        if kind == 'CompositionRouterVideoSource':
            # This exact built-in mapping is evidenced by native XML and /sources.
            item['source_id'] = 'COMPOSITION_ROUTER_SRC'
            route = source.find('Params/ParamChoice[@name="Input"]')
            # Omitted Input is native default serialization, not an inferred
            # semantic endpoint. Fresh serialization must preserve this state.
            item['route_serialized'] = route.get('value') if route is not None else None
            item['route_settings'] = [{k: p.get(k) for k in ('name', 'value', 'default') if p.get(k) is not None}
                                      for p in source.findall('Params/*')]
        elif kind == 'VideoSourceFeedback':
            # Arena native Feedback, evidenced by /sources and saved native XML.
            item['source_id'] = 'FEEDBACK_SRC'
        elif kind == 'GeneratorVideoSource':
            gen = source.find('RenderPass')
            if gen is None or not gen.get('uniqueTypeId'):
                raise ContractError(f'{name}: generator identifier unavailable')
            item['source_id'] = _identifier(gen.get('uniqueTypeId'))
        else:
            raise ContractError(f'{name}: unsupported source type {kind}')
        result['instruments'].append(item)
    return result


def _live_clip(live, item):
    layers = _unique(live.get('layers', []), _name, 'live layers')
    layer = layers.get(item['layer'])
    if layer is None:
        raise ContractError(f"Live layer missing: {item['layer']}")
    clips = [c for c in layer.get('clips', []) if _name(c) == item['clip']]
    if len(clips) != 1:
        raise ContractError(f"{item['layer']}/{item['clip']}: live clip missing or ambiguous")
    return clips[0]


def _route(clip):
    p = (clip.get('video', {}).get('sourceparams') or {}).get('Input')
    if not isinstance(p, dict):
        return None
    value, opts = p.get('value'), p.get('options')
    # Semantic choice labels only; no raw numeric runtime IDs / ordinal guesses.
    if isinstance(value, str) and isinstance(opts, list) and value in opts and not re.fullmatch(r'\d+(?::\d+)?', value):
        return value
    return None


def build_contract(snapshot_path, live_comp=None, layers=None):
    contract = _xml_contract(snapshot_path, layers)
    if live_comp is not None:
        for item in contract['instruments']:
            clip = _live_clip(live_comp, item)
            item['source_description'] = clip.get('video', {}).get('description')
            if 'route_serialized' in item:
                semantic = _route(clip)
                if semantic is not None:
                    item['route_semantic'] = semantic
    return contract


def _core(contract):
    # Live display labels are supporting evidence, never plugin identity.
    return {**contract, 'instruments': [{k: v for k, v in i.items()
            if k not in ('route_semantic', 'source_description')} for i in contract['instruments']]}


def validate_contract(contract, snapshot_path, live_comp=None, sources=None, effects=None,
                      observed_snapshot_path=None):
    """Return actionable errors. observed snapshot must be fresh after native open.

    Without live_comp this checks saved XML and installation only, not live routing.
    Caller must not present offline success as post-open verification.
    """
    errors = []
    try:
        if contract.get('version') != 1:
            raise ContractError('Unsupported dependency contract version')
        expected = _core(contract)
        if _xml_contract(snapshot_path, contract['layers']) != expected:
            errors.append('Snapshot dependency/routing contract changed')
        observed_ok = False
        if observed_snapshot_path is not None:
            observed_ok = _xml_contract(observed_snapshot_path, contract['layers']) == expected
            if not observed_ok:
                errors.append('Observed native snapshot dependency/routing mismatch')
        inventories = {}
        for kind, inventory in [('sources', sources), ('effects', effects)]:
            if not isinstance(inventory, dict) or not isinstance(inventory.get('video'), list):
                errors.append(f'Installed {kind} inventory unavailable')
                inventories[kind] = set()
            else:
                inventories[kind] = {_identifier(x.get('idstring')) for x in inventory['video']}
        required_fx = contract['composition_effects'] + [e for v in contract['layer_effects'].values() for e in v]
        required_fx += [e for g in contract['groups'] for e in g['effects']]
        for item in contract['instruments']:
            if item['source_id'] not in inventories['sources']:
                errors.append(f"Missing source plugin: {item['source_id']} ({item['layer']})")
            required_fx += item['effects']
        for fx in required_fx:
            if fx['id'] not in inventories['effects']:
                errors.append(f"Missing effect plugin: {fx['id']} ({fx['name']})")
        if live_comp is None:
            return list(dict.fromkeys(errors))
        if observed_snapshot_path is None:
            errors.append('Live native plugin identifiers unavailable; fresh native snapshot required')
        def dims(video):
            return [_value(video.get(k)) for k in ('width', 'height')]
        def stack(node):
            return [x.get('name') for x in node.get('video', {}).get('effects', [])]
        def check_stack(node, wanted, where):
            if stack(node) != [x['name'] for x in wanted]:
                errors.append(f'{where}: effect order mismatch')
        if dims(live_comp.get('video', {})) != contract['dimensions']:
            errors.append('Live composition dimensions mismatch')
        check_stack(live_comp, contract['composition_effects'], 'Composition')
        live_layers = _unique(live_comp.get('layers', []), _name, 'live layers')
        if list(live_layers) != contract['layer_order']:
            errors.append('Live layer order mismatch; router ordinals may target different layers')
        for name, fx in contract['layer_effects'].items():
            check_stack(live_layers.get(name, {}), fx, name)
        groups = live_comp.get('layergroups')
        if not isinstance(groups, list) or len(groups) != len(contract['groups']):
            errors.append('Live group count mismatch')
        else:
            for g, wanted in zip(groups, contract['groups']):
                if [_name(l) for l in g.get('layers', [])] != wanted['members']:
                    errors.append(f"Group {wanted['index'] + 1}: membership mismatch")
                check_stack(g, wanted['effects'], f"Group {wanted['index'] + 1}")
        for item in contract['instruments']:
            clip = _live_clip(live_comp, item)
            where = f"{item['layer']}/{item['clip']}"
            if dims(clip.get('video', {})) != item['dimensions']:
                errors.append(f'{where}: source dimensions mismatch')
            check_stack(clip, item['effects'], where)
            if item.get('source_description') and clip.get('video', {}).get('description') != item['source_description']:
                errors.append(f'{where}: source description mismatch')
            if 'route_serialized' in item:
                route = _route(clip)
                if route is not None and 'route_semantic' in item:
                    if route != item['route_semantic']:
                        errors.append(f'{where}: router input mismatch')
                elif not observed_ok:
                    errors.append(f'{where}: router input unavailable; fresh native snapshot required')
    except (ContractError, ET.ParseError, OSError, KeyError, TypeError, ValueError) as exc:
        errors.append(f'Dependency evidence invalid: {exc}')
    return list(dict.fromkeys(errors))
