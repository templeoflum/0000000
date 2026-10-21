"""Adapt the reference bank into Soup; operate on recovery copies, never originals."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import xml.etree.ElementTree as E
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'sp/restored-compositions/soup-restoration'
SOURCE=Path.home()/'Documents/Resolume Arena/Compositions/feedback machine_16x9_1080p.avc'
BASE=OUT/'Soup latest before merge.avc'
a=E.parse(SOURCE).getroot(); tree=E.parse(BASE); b=tree.getroot()
name='generative soup_16x9_1920x1080_60fps'
# Preserve Soup's layer identities, groups, existing clips, levels, and routing.
roles=['feedback','sculpt','field','delay','figure','glyph','texture','grain']
assert [l.find('./Params/Param[@name="Name"]').get('value') for l in b.findall('Layer')]==roles
layers=b.findall('Layer'); oldlayers=a.findall('Layer')
ids={}; counter=max(int(n.get('uniqueId')) for r in [a,b] for n in r.iter() if (n.get('uniqueId') or '').isdigit())+10000

def clone(n):
 global counter
 n=deepcopy(n)
 for x in n.iter():
  if x.get('uniqueId'):
   old=x.get('uniqueId')
   if old not in ids: counter+=1;ids[old]=str(counter)
   x.set('uniqueId',ids[old])
 return n

def chain(n):return n.find('./VideoTrack/RenderPass[@name="RenderPassChain"]')
def fx(n):return [x for x in chain(n) if x.tag=='RenderPass' and x.get('name')!='Transform']
def bypass(e):
 p=e.find('./Params[@name="Params"]')
 if p is None:p=E.SubElement(e,'Params',name='Params')
 q=p.find('./Param[@name="Bypassed"]')
 if q is None:q=E.SubElement(p,'Param',name='Bypassed',T='BOOL',default='0')
 q.set('value','1')

rack=[]
# Old fill and color now share sculpt; retain order within each reference stack.
for sources,target in [([3],0),([0,1],1),([4],2),([2],3),([5],4),([6],5),([],6),([],7),(['composition'],'composition')]:
 dest=b if target=='composition' else layers[target]; ch=chain(dest); existing=fx(dest); used=set(); ordered=[]
 for source in sources:
  for e in fx(a if source=='composition' else oldlayers[source]):
   reuse=next((x for x in existing if id(x) not in used and x.get('uniqueTypeId')==e.get('uniqueTypeId')),None)
   if reuse is not None:used.add(id(reuse));new=reuse
   else:new=clone(e);bypass(new)
   ordered.append(new);rack.append({'from':source,'to':target,'effect':e.get('name'),'reused_existing':reuse is not None})
 for x in existing:ch.remove(x)
 for x in ordered+[x for x in existing if id(x) not in used]:ch.append(x)

# Bank clips are appended in the same deck so Heart navigation sees all of them.
# Native feedback movement is selectable on feedback. Test sources use visual roles.
mainmap={0:0,1:1,2:0,3:0,4:2,5:4,6:5,7:6}
testmap={0:2,1:2,2:2,3:4,4:2,5:4,6:5,7:7}
d=b.findall('Deck')[int(b.get('currentDeckIndex','0'))]
start=int(d.get('numColumns'));nextcol={i:start for i in range(8)};rows=[]
blank=next(c for c in d.findall('Clip') if c.find('.//PrimarySource/VideoSource') is None)
existing_clips={c.get('uniqueId'):E.tostring(c) for c in d.findall('Clip')}
for deck in a.findall('Deck'):
 di=int(deck.get('deckIndex','0'));mapping=mainmap if di==0 else testmap
 for c in deck.findall('Clip'):
  if c.find('.//PrimarySource/VideoSource') is None:continue
  li=int(c.get('layerIndex'));dest=mapping[li];col=nextcol[dest];nextcol[dest]+=1
  n=clone(c);n.set('layerIndex',str(dest));n.set('columnIndex',str(col))
  oldname=n.find('./Params/Param[@name="Name"]');original=oldname.get('value')
  oldname.set('value',f'FM · {original} [{di+1}.{li+1}.{int(c.get("columnIndex"))+1}]')
  for s in n.findall('.//PrimarySource/VideoSource'):
   s.set('width','1920');s.set('height','1080')
   if s.get('type')=='CompositionRouterVideoSource':
    # Reference glitch routers explicitly tap its text layer (3:7).
    for p in s.findall('./Params/*[@name="Input"]'):
     if p.get('value','').startswith('3:'):
      old=int(p.get('value').split(':')[1])-1
      p.set('value','3:'+str(mainmap[old]+1))
  for p in n.findall('./VideoTrack/Params/*'):
   if p.get('name') in ('Width','Height'):p.set('value','1920' if p.get('name')=='Width' else '1080')
  d.append(n);rows.append({'source_deck':di,'source_layer':li,'source_column':int(c.get('columnIndex')),'name':original,'layer':dest+1,'column':col+1,'imported_name':oldname.get('value')})
width=max(nextcol.values())
occupied={(int(c.get('layerIndex')),int(c.get('columnIndex'))) for c in d.findall('Clip')}
for li in range(8):
 for ci in range(start,width):
  if (li,ci) in occupied:continue
  n=deepcopy(blank)
  for x in n.iter():
   if x.get('uniqueId'):counter+=1;x.set('uniqueId',str(counter))
  n.set('layerIndex',str(li));n.set('columnIndex',str(ci));d.append(n)
d.set('numColumns',str(width));d.set('numColumnsWithContent',str(width));d.set('numLayersWithContent','8');b.set('numColumns',str(width))
b.find('CompositionInfo').set('name',name)
for p in b.findall('./Params/Param[@name="Name"]'):p.set('value',name)
for key,val in existing_clips.items():assert E.tostring(next(c for c in d.findall('Clip') if c.get('uniqueId')==key))==val
assert len(rows)==245
assert len(occupied)+8*(width-start)-sum(1 for li,ci in occupied if ci>=start)==len(d.findall('Clip'))
out=OUT/(name+'.avc');tree.write(out,encoding='UTF-8',xml_declaration=True)
report={'output':str(out),'base':str(BASE),'reference':str(SOURCE),'layout':roles,'imported_clips':rows,'rack':rack,'columns':width,'limits':['New persistent effects bypassed; existing effect settings preserved.','Native feedback sources sample the composition; Soup shader-owned history retains its existing semantics.','Reference transport automation and clip effects retained; custom Heart Homes are not fabricated.']}
(OUT/'merge-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'imported':len(rows),'by_layer':dict(Counter(roles[x['layer']-1] for x in rows)),'rack_instances':len(rack),'columns':width,'output':str(out)},indent=2))
