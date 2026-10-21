from pathlib import Path
import json,sys,xml.etree.ElementTree as E
from collections import Counter
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'engine'))
import heart
base=Path.home()/'Documents/Resolume Arena/Compositions'
def params(n,group='Params'):
 return {x.get('name'):x.get('value',x.get('default')) for p in n.findall('Params') if p.get('name')==group for x in p}
def effects(n):
 return [{'name':e.get('name'),'params':params(e),'animation_types':dict(Counter(x.tag for x in e.iter() if x.tag.startswith('PhaseSource') and x.tag!='PhaseSourceStatic'))} for e in n.findall('./VideoTrack/RenderPass[@name="RenderPassChain"]/RenderPass') if e.get('name')!='Transform']
rows=[]
for name in ['feedback machine_16x9_1080p.avc','generative soup_16x9_1920x1080_60fps.avc']:
 r=E.parse(base/name).getroot();clips=[]
 for deck in r.findall('Deck'):
  for c in deck.findall('Clip'):
   sources=c.findall('.//PrimarySource/VideoSource')
   if not sources:continue
   clips.append({'deck':int(deck.get('deckIndex',0))+1,'layer':int(c.get('layerIndex'))+1,'column':int(c.get('columnIndex'))+1,'name':params(c).get('Name'),
    'sources':[{'type':s.get('type'),'settings':params(s,'Settings'),'size':[s.get('width'),s.get('height')]} for s in sources],'effects':effects(c)})
 rows.append({'file':str(base/name),'composition':effects(r),'groups':[{'name':params(g).get('Name'),'effects':effects(g)} for g in r.findall('Group')],
 'layers':[{'index':int(l.get('layerIndex'))+1,'name':params(l).get('Name'),'group':l.get('layerGroup'),'effects':effects(l)} for l in r.findall('Layer')],'clips':clips})
live=json.load(open('/tmp/heart-comparison-live.json'));profiles=json.load(open(root/'engine/sweetspots.json'));coverage=[]
for li,l in enumerate(live['layers']):
 for ci,c in enumerate(l['clips']):
  if not c.get('video'):continue
  secs=heart.atom_sections(c);coverage.append({'layer':li+1,'column':ci+1,'name':c['name']['value'],'source':c['video'].get('description'),'recognized':heart.is_sp(c),'sections':[n for n,p in secs],'factory_home':(secs[0][0] if secs and not any(k.endswith(' Drive') for k in heart.allparams(c)) else c['name']['value']) in profiles,'native_clip_effects':[e['name'] for e in c['video'].get('effects',[]) if e['name']!='Transform' and e['name'] not in heart.ATOMS and not any(k.endswith(' Drive') for k in e.get('params',{}))]})
out=Path(__file__).parent;(out/'inventory.json').write_text(json.dumps({'saved':rows,'live_coverage':coverage},indent=2))
print('Loaded clips',len(coverage),'recognized',sum(x['recognized'] for x in coverage),'factory homes',sum(x['factory_home'] for x in coverage))
print('Not recognized',[(x['layer'],x['column'],x['name']) for x in coverage if not x['recognized']])
print('Recognized without factory Home',[(x['layer'],x['column'],x['name']) for x in coverage if x['recognized'] and not x['factory_home']])
for row in rows:
 print(Path(row['file']).name,'populated source clips',len(row['clips']),'non-Transform effects',sum(len(x['effects']) for x in row['layers'])+len(row['composition'])+sum(len(x['effects']) for x in row['clips']))
