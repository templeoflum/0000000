"""Read-only saved composition extraction; no route-value interpretation."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FILES = ['sp/engine/patches/_route_readback.avc', 'sp/engine/patches/Feedback checked.avc', 'sp/design/heart-performance-plan/Heart Performance.avc', 'sp/restored-compositions/portal.avc', 'sp/restored-compositions/treehouse.avc']
def name(e):
    p=e.find('Params/Param[@name="Name"]')
    return p.get('value',p.get('default')) if p is not None else e.get('name')
def effects(e):
    return [{'name':p.get('name'),'type_id':p.get('uniqueTypeId'), 'controls':[{'kind':v.tag,'name':v.get('name'),'value':v.get('value')} for v in p.findall('.//Params/*') if v.tag in ('ParamRange','ParamChoice','ParamColor','ParamEvent','ParamTrigger')]} for p in e.findall('VideoTrack/RenderPass/RenderPass')]
result=[]
for rel in FILES:
    raw=(ROOT/rel).read_bytes();root=ET.fromstring(raw)
    layers=sorted(root.findall('Layer'),key=lambda l:int(l.get('layerIndex')))
    row={'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'saved_evidence_only':True,'layers':[{'index':l.get('layerIndex'),'name':name(l),'effects':effects(l)} for l in layers], 'composition_effects':effects(root),'routes':[]}
    for deck in root.findall('Deck'):
        for clip in deck.findall('Clip'):
            source=clip.find('VideoTrack/PrimarySource/VideoSource')
            if source is None:continue
            if source.get('type') not in ('CompositionRouterVideoSource','VideoSourceFeedback'):continue
            row['routes'].append({'deck_index':deck.get('deckIndex'),'layer_index':clip.get('layerIndex'),'column_index':clip.get('columnIndex'),'clip':name(clip),'source_type':source.get('type'),'settings':[dict(p.attrib,kind=p.tag) for p in source.findall('Params/*')], 'effects':effects(clip)})
    result.append(row)
(OUT/'SAVED-INVENTORY.json').write_text(json.dumps(result,indent=2)+'\n')
for row in result:
    print(row['path'], 'layers:',len(row['layers']),'routes:',len(row['routes']))
    for route in row['routes']:
        print(' ',route['layer_index'],route['column_index'],route['clip'],[(v['name'],v.get('value')) for v in route['settings']])
