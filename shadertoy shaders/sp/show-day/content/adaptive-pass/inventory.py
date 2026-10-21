import json,sys,pathlib,collections
from types import SimpleNamespace as N
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT/'sp/engine'))
import source_adapter as adapter
from clip_catalog import SLOT_TYPES
c=json.loads((ROOT/'sp/show-day/content/live-current-20260909.json').read_text());profiles=json.loads((ROOT/'sp/engine/sweetspots.json').read_text());rows=[]
for i,l in enumerate(c['layers']):
 role=l['name']['value']
 for j,clip in enumerate(l['clips']):
  v=clip.get('video') or {};name=v.get('description')
  if not name:continue
  slots=[N(name=n,kind=s.get('valuetype',''),pmin=s.get('min',0),pmax=s.get('max',1),integer=s.get('view',{}).get('display_units')=='integer',choices=s.get('options',[]),owner='heart') for n,s in (v.get('sourceparams') or {}).items()]
  source=N(name=name,slots=[s for s in slots if s.kind in SLOT_TYPES],role=role);selected=adapter.selected(source)
  rows.append(dict(layer=i+1,col=j+1,source=name,role=role,authored_profile=name in profiles,automatic_candidates=sorted(selected),controls={s.name:adapter.classify(s,role) for s in slots},status='schema proposal; live ownership and output not certified'))
(P/'inventory.json').write_text(json.dumps(rows,indent=2));unique={r['source']:r for r in rows};counts=collections.Counter('authored profile' if r['authored_profile'] else 'automatic candidates' if r['automatic_candidates'] else 'manual/routing/review' for r in unique.values());print(len(rows),'clip instances;',len(unique),'source descriptions;',dict(counts))
