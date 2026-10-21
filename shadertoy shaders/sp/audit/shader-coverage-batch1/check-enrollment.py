import sys,json,copy
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]/'engine'))
import heart
c=json.loads((P/'deck-1.json').read_text());enrolled=json.loads((P.parents[1]/'engine/native_sources.json').read_text());results=[]
with patch.object(heart,'save_atoms'):
 for l,layer in enumerate(c['layers']):
  for col,cj in enumerate(layer['clips']):
   v=cj.get('video') or {}
   if v.get('description') not in enrolled:continue
   clip=heart.Clip(l,col,copy.deepcopy(cj));names={s.name for s in clip.slots};expected={k for k,p in v.get('sourceparams',{}).items() if p.get('valuetype') in ('ParamRange','ParamFloat','ParamInt','ParamNumber','ParamChoice') and k!='Opacity'}
   results.append(dict(layer=l+1,col=col+1,source=v['description'],slots=len(names),expected=len(expected),ok=expected<=names))
(P/'enrollment-checks.json').write_text(json.dumps(results,indent=2));assert all(r['ok'] for r in results);print(len(results),'clip schemas passed;',sum(r['slots'] for r in results),'slots exposed')
