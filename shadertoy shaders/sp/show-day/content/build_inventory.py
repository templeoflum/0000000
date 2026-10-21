"""Read-only deterministic reconciliation. Writes only sibling inventory/check files."""
import json,re,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
AUD=ROOT/'sp/audit'; PATCH=Path('/Users/donovan/Documents/Resolume Wire/Patches')
def rel(p):
 try:return str(p.relative_to(ROOT))
 except ValueError:return str(p)
def read(p):return json.loads(p.read_text())
ledger=read(AUD/'shader-coverage-batch1/coverage.json')
rows=ledger['clips']
rows=rows+([] if any(r['source']=='Heart Capsule' and r['layer']==5 and r['col']==73 for r in rows) else [dict(deck=1,layer=5,col=73,name='Heart Capsule',source='Heart Capsule',controls={},other_controls={},provenance='sp/audit/capsule-repair/live-results.json')])
# Extract installed graph resources, not unused files beside the active resource.
patches=collections.defaultdict(list)
for p in PATCH.glob('*/*.wire'):
 try:
  graph=read(p)['patch']; name=graph['meta']['displayName']; nodes=graph['nodes']; resources=[]
  for nid,n in nodes.items():
   a=n.get('attributes',{}).get('fragment-shader',{}).get('value',{})
   path=a.get('path',{}).get('main')
   if not path:continue
   f=p.parent/path; inputs=[];err=None
   if f.exists():
    try:
     t=f.read_text(); start=t.index('{'); h=json.JSONDecoder().raw_decode(t[start:])[0];inputs=h.get('INPUTS',[])
    except Exception as e:err=type(e).__name__
   wires=[]
   for c in graph.get('connections',[]):
    if str(c['to'][0])!=str(nid):continue
    src=nodes.get(str(c['from'][0]),{}); at=src.get('attributes',{})
    wires.append(dict(input=c['to'][1],from_node=src.get('name'),node_id=c['from'][0],minimum=at.get('min',{}).get('value'),maximum=at.get('max',{}).get('value')))
   resources.append(dict(path=rel(f),exists=f.exists(),sha256=hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None,header_error=err,declared_inputs=inputs,connections=wires,unwired_declared_inputs=[i.get('NAME') for i in inputs if i.get('NAME') not in {w['input'] for w in wires}]))
  patches[name].append(dict(path=rel(p),identifier=graph['meta'].get('identifier'),resources=resources))
 except (ValueError,KeyError,TypeError):continue
# Only attach records explicitly naming this source; never infer by address alone.
evidence=collections.defaultdict(list)
folders=[AUD/f'shader-coverage-batch{i}' for i in range(1,12)]+[AUD/s for s in ['source-repair','field-controls','final-inputs','klein-repair','melting-repair','color-wheel-repair','capsule-repair','recovery-profiles']]
for folder in folders:
 for p in folder.glob('*.json'):
  if p.name not in {'live-results.json','live.json','live-remaining.json','field-no-controls.json','figure-no-controls.json','choices.json','static-choice.json','relaunch-results.json','all-controls.json'}:continue
  try:d=read(p)
  except ValueError:continue
  if not isinstance(d,list):continue
  for r in d:
   if not isinstance(r,dict) or not isinstance(r.get('source'),str):continue
   s=r['source']; imgs=[]
   if 'col' in r:
    layer=r.get('layer',3 if p.name=='field-no-controls.json' else 5 if p.name=='figure-no-controls.json' else None)
    if layer:
     imgs=[rel(f) for f in folder.glob('*.png') if re.search(rf'L{layer}C{r["col"]}(?:-|\.)',f.name)]
   evidence[s].append(dict(path=rel(p),kind='factory_recovery' if p.name in {'live.json','live-remaining.json'} and folder.name in {'recovery-profiles','capsule-repair'} else 'historical_control_or_output_sample',record=r,images=imgs))
replacements=dict(zip(['RainbowRingCubicTwist','Spikeball_v2','Crystal Drops','HypnoWorm','Torus thingy','QField2','QuarternionSwell','Paper Fractal','VectorFromHell','Concentrip','TwoFiftySixBiatch','Kali - ancient temple','Kali liberation of the true self','Klein Bottle (3D)','Melting Fractal','Color Wheel','SP Figure'],['SP Figure Ring Source','SP Figure Spike Source','SP Figure Crystal Source','Heart HypnoWorm','Heart Torus','Heart Quaternion Field','Heart Quaternion Swell','Heart Paper Fractal','Heart Vector Lattice','Heart Concentrip','Heart Puls Lattice','Heart Ancient Temple','Heart Kali Liberation','Heart Klein Bottle','Heart Melting Fractal','Heart Color Wheel','Heart Capsule']))
# Table findings carry exact source identity; preserve their date/context and supersede known stale issues below.
findings=collections.defaultdict(list)
for p in [f/'REPORT.md' for f in folders if (f/'REPORT.md').exists()]:
 for line in p.read_text().splitlines():
  parts=[v.strip() for v in line.strip('|').split('|')]
  if line.startswith('|') and len(parts)>=4 and re.match(r'L[358]C\d+',parts[0]):
   findings[parts[1]].append(dict(path=rel(p),address=parts[0],probe=parts[2],finding=parts[-1]))
roles={1:'Feedback',2:'Sculpt',3:'Field',4:'Delay',5:'Figure',6:'Glyph',7:'Texture',8:'Grain'}
source_rows=collections.defaultdict(list)
for r in rows:source_rows[r['source']].append(r)
registered=set(read(ROOT/'sp/engine/native_sources.json'))
result=[]
for s,instances in sorted(source_rows.items()):
 controls={k:v for r in instances for k,v in r.get('controls',{}).items()}; others={k:v for r in instances for k,v in r.get('other_controls',{}).items()}
 es=evidence[s]; ps=patches.get(s,[])
 # Capsule postdates the mutable census. Use only its actual control list; do not invent ranges.
 if s=='Heart Capsule':controls={n:{'valuetype':'ParamRange','range_evidence':'installed graph'} for n in ['Turn','Outline','Material','Float','Tilt']}
 eligible=list(controls); speedonly=bool(eligible) and all(k.lower()=='speed' for k in eligible)
 slot='speed_only' if speedonly else 'numeric_or_choice_exposed' if controls else 'no_eligible_source_controls_in_snapshot'
 gaps=[]
 if speedonly:gaps.append('No exposed shape control; Speed readback does not establish phase-continuous modulation or visible structure control.')
 if others:gaps.append('Non-continuous native controls need separate access/trigger checks; not continuous-drive certification.')
 if not controls:gaps.append('No numeric source controls in census; routing/static/native resources and clip effects must be considered separately.')
 if any(r['unwired_declared_inputs'] for p in ps for r in p['resources']):gaps.append('Installed shader declares unwired inputs; see graph connections. Unwired may be intentional, unused, fixed, or compound: not automatically a repair.')
 recovery=[e for e in es if e['kind']=='factory_recovery']
 role=sorted({roles[r['layer']] for r in instances});proposed=' / '.join(role)+' (placement only; visual role unverified)'
 if s in ['Gradient Bars','Tunnelines','Rings','Metaballs','Hopf fibers SP']:proposed='Field candidate from sampled composition output; preserve per-instance settings'
 if s=='SP State Test':proposed='Diagnostic; exclude from performance selection'
 if s=='Heart Kali Liberation':proposed='Field provisional; dark rest; Figure containment unverified'
 if s.startswith('Heart ') and s!='Heart Kali Liberation':proposed=' / '.join(role)+' copy; sampled output, not exhaustive acceptance'
 action='Root: audition one meaningful structural control, then Home/relaunch on chosen show set; otherwise defer.'
 if speedonly:action='Use as time-animated content with Speed held steady; defer a separately named structural-control copy until wanted.'
 if not controls:action='Keep routing/utility review separate; inspect installed graph before proposing input exposure.'
 if s in replacements:action='Prefer existing replacement '+replacements[s]+'; preserve original and settings; verify current identity before selecting.'
 if recovery:action='Root: verify current source identity, visible factory/saved Home and integrated effect recovery; existing factory cycle is historical evidence.'
 if 'Glyph' in role and role==['Glyph']:action='Deferred Glyph; no show-day promotion without rendered evidence.'
 result.append(dict(source=s,instances=[dict(address=f'D{r.get("deck",1)} L{r["layer"]}C{r["col"]}',clip_name=r.get('name'),role=roles[r['layer']],numeric_controls=r.get('controls',{}),other_controls=r.get('other_controls',{}),historical_rendered_status=r.get('rendered_status'),provenance=r.get('provenance','sp/audit/shader-coverage-batch1/coverage.json')) for r in instances],role=proposed,actual_interface=dict(classification=slot,native_controls=controls,other_controls=others,enrolled_now=s in registered,installed_patch_candidates=ps,identity_caveat='Installed displayName match; graph resource references inspected. Current live occupancy not queried.'),control_gaps=gaps,replacement=replacements.get(s),evidence=es,historical_findings=findings[s],readiness='historical_factory_recovery_and_sampled_output' if recovery else 'historical_samples_only' if es else 'unknown',next_action=action))
# Current adjudications keep historical defects visible without presenting them as current copy failures.
for r in result:
 s=r['source']; r['current_adjudication']=[]
 if r['replacement']:
  r['current_adjudication'].append(dict(finding='Original finding retained; existing separately named replacement available. Verify its identity, do not edit original.',replacement=r['replacement'],evidence='sp/show-day/PLAN.md'))
 if r['readiness']=='historical_factory_recovery_and_sampled_output':
  r['current_adjudication'].append(dict(finding='Older Home-unverified statements superseded by named factory recovery records; saved-user Home/relaunch still unknown.',evidence='sp/audit/capsule-repair/REPORT.md' if s=='Heart Capsule' else 'sp/audit/recovery-profiles/REPORT.md'))
 if s in {'SP Field','SP Atom Grain'}:
  r['current_adjudication'].append(dict(finding='White/static diagnosis invalidated: alpha-corrected original outputs visibly change. No source repair warranted for this diagnosis.',evidence='sp/audit/white-output/REPORT.md'))
 if s=='Checkered':
  r['current_adjudication'].append(dict(finding='Old startup range excursions superseded by 40/40 narrow-range startup checks; per-instance useful ranges still require review.',evidence='sp/audit/range-followup/REPORT.md'))
 if s in {'GeodesicTiling','Melty Boi','ShaderLamb','Creation','cubes + spheres','ocean waves','Potential Energy','Space Warping Portals'}:
  r['next_action']='See source-specific observed output, actual wiring and smallest useful next step in sp/show-day/content/PRIORITIES.md.'
obj=dict(schema_version=1,as_of='2026-09-09',scope='Saved census reconciled with later named repair/recovery evidence and installed graph interfaces. No live queries or GPU work.',census_path='sp/audit/shader-coverage-batch1/coverage.json',census_note='Mutable historical ledger currently holds 299 entries / 194 source descriptions, despite original report saying 282/177. Capsule is already present in this updated ledger; its later audit supplements interface/recovery evidence. Counts are not fresh live occupancy.',limits=['Descriptions identify source families, not guaranteed unique shader files; patch UUIDs recorded separately.','Native control ranges are per-instance snapshots; declared ISF inputs and actual Wire connections are separate.','Sampled output is not full-range, performance, containment, saved Home, or relaunch certification.','Historical first-pass delivery misses remain recorded; September 9 handoff and control-reliability report supersede global unresolved queue/range diagnoses.','SP Atom Grain and SP Field white/static diagnoses invalidated by alpha-corrected review.','14 Heart-named factory recovery copies differ from 18 total navigation copies including four SP Figure sources.'],counts=dict(source_descriptions=len(result),documented_instances=len(rows),control_classes=dict(collections.Counter(r['actual_interface']['classification'] for r in result)),readiness=dict(collections.Counter(r['readiness'] for r in result))),sources=result)
(OUT/'CURRENT-INVENTORY.json').write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps(obj['counts'],indent=2))
