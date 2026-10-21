"""Restore native Portal image banks in a new Heart composition; originals untouched."""
from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as E
import json
D=Path(__file__).resolve().parent
base=E.parse(D/'Heart before native Portal.avc'); b=base.getroot()
a=E.parse(D.parents[1]/'restored-compositions/portal.avc').getroot()
selected=[1,*range(6,22)]
remap={old:8+i for i,old in enumerate(selected)}
mask_index=8+len(selected); total=mask_index+1
counter=max(int(x.get('uniqueId')) for r in [a,b] for x in r.iter() if (x.get('uniqueId') or '').isdigit())+100000
ids={}
def clone(n):
 global counter
 n=deepcopy(n)
 for x in n.iter():
  old=x.get('uniqueId')
  if old:
   if old not in ids:counter+=1;ids[old]=str(counter)
   x.set('uniqueId',ids[old])
 return n
def param(n,name,value,kind='Param',T='STRING'):
 p=n.find("./Params[@name='Params']")
 if p is None:p=E.SubElement(n,'Params',name='Params')
 x=p.find(f"./*[@name='{name}']")
 if x is None:x=E.SubElement(p,kind,name=name,T=T,default=value)
 x.set('value',value)
 return x
def size(n,w,h):
 for p in n.findall('./VideoTrack/Params/*'):
  if p.get('name') in ['Width','Height']:p.set('value',str(w if p.get('name')=='Width' else h))
# Keep Heart's eight performance layers and existing group exactly intact.
oldlayers=b.findall('Layer'); mask=deepcopy(oldlayers[9]);mask.set('layerIndex',str(mask_index))
for l in oldlayers[8:]:b.remove(l)
newgroup=clone(a.find('Group'));param(newgroup,'Name','Portal Frame');size(newgroup,1920,720)
group_index=len(b.findall('Group')); b.insert(list(b).index(b.find('Group'))+group_index,newgroup)
insert=list(b).index(b.findall('Layer')[-1])+1
for old in selected:
 l=clone(a.findall('Layer')[old]);l.set('layerIndex',str(remap[old]));l.set('layerGroup',str(group_index))
 name=l.find("./Params/Param[@name='Name']");label=name.get('value') if name is not None else f'section {old+1}'
 param(l,'Name','Portal · '+label);param(l,'Ignore Column Trigger','1',T='BOOL');param(l,'Master','1','ParamRange','DOUBLE')
 size(l,1920,720);b.insert(insert,l);insert+=1
b.insert(insert,mask)
sourceclips=a.find('Deck').findall('Clip'); report=[]; missing=[]
for di,d in enumerate(b.findall('Deck')):
 blank=next(c for c in d.findall('Clip') if c.find('.//PrimarySource/VideoSource') is None)
 maskclips=[deepcopy(c) for c in d.findall('Clip') if c.get('layerIndex')=='9']
 for c in list(d.findall('Clip')):
  if int(c.get('layerIndex'))>=8:d.remove(c)
 width=int(d.get('numColumns'))
 if di==0:
  for old in selected:
   for c in sourceclips:
    if int(c.get('layerIndex'))!=old or c.find('.//PrimarySource/VideoSource') is None:continue
    n=clone(c);n.set('layerIndex',str(remap[old]));size(n,1920,720)
    for s in n.findall('.//VideoFormatReaderSource'):
     if not Path(s.get('fileName')).exists():missing.append(s.get('fileName'))
    for x in n.iter():
     for k,v in x.attrib.items():
      if k=='value' and v.startswith('3:') and v[2:].isdigit():
       oldidx=int(v[2:])-1
       if oldidx in remap:x.set(k,'3:'+str(remap[oldidx]+1))
    d.append(n);width=max(width,int(n.get('columnIndex'))+1)
    report.append({'layer':remap[old]+1,'column':int(n.get('columnIndex'))+1,'source_layer':old+1})
 for c in maskclips:c.set('layerIndex',str(mask_index));d.append(c)
 occupied={(int(c.get('layerIndex')),int(c.get('columnIndex'))) for c in d.findall('Clip')}
 for li in range(total):
  for ci in range(width):
   if (li,ci) in occupied:continue
   n=deepcopy(blank)
   for x in n.iter():
    if x.get('uniqueId'):counter+=1;x.set('uniqueId',str(counter))
   n.set('layerIndex',str(li));n.set('columnIndex',str(ci));d.append(n)
 d.set('numLayers',str(total));d.set('numLayersWithContent',str(total if di==0 else 0));d.set('numColumns',str(width))
 if di==0:d.set('numColumnsWithContent',str(max(110,width)))
b.set('numLayers',str(total));name='Heart Portal Native';b.find('CompositionInfo').set('name',name);param(b,'Name',name)
assert not missing,missing
def comparable(n):
 if n is None:return None
 n=deepcopy(n)
 for x in n.iter():x.attrib.pop('uniqueId',None)
 return E.tostring(n)
# Explicit parity checks: preserve native blends, transitions, opacity envelopes, autopilot.
for old in selected:
 src=a.findall('Layer')[old];dst=b.findall('Layer')[remap[old]]
 for path in ['./ClipTransition','./VideoTrack/Params/ParamRange[@name="Opacity"]','./Params[@name="AutoPilot"]']:
  assert comparable(src.find(path))==comparable(dst.find(path)),(old,path)
 for mixer in ['Blend','Transition']:
  src_types=[x.get('type') for x in src.findall(f'./VideoTrack/ChoosableMixer[@name="{mixer}"]/RenderPass')]
  dst_types=[x.get('type') for x in dst.findall(f'./VideoTrack/ChoosableMixer[@name="{mixer}"]/RenderPass')]
  assert src_types==dst_types
for i in range(8):assert E.tostring(oldlayers[i])==E.tostring(b.findall('Layer')[i])
base.write(D/(name+'.avc'),encoding='UTF-8',xml_declaration=True)
(D/'native-portal-report.json').write_text(json.dumps({'composition':name,'layers':total,'mask_layer':mask_index+1,'imported_clips':len(report),'missing_media':missing,'sections':remap,'clips':report},indent=2))
print(json.dumps({'composition':name,'layers':total,'mask_layer':mask_index+1,'imported_clips':len(report),'missing_media':missing}))
