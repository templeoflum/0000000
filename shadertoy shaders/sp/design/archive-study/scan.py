from pathlib import Path
import xml.etree.ElementTree as ET, json
from collections import Counter, defaultdict
base=Path('/Users/donovan/Documents/Resolume Arena'); out=Path(__file__).parent

def params(n):
 return {x.get('name'):x.get('value',x.get('default')) for p in n.findall('Params') if p.get('name')=='Params' for x in p}
def stack(n):
 chain=n.find('./VideoTrack/RenderPass[@name="RenderPassChain"]')
 if chain is None:return []
 return [{'effect':e.get('name'),'bypass':params(e).get('Bypassed','unspecified'),
          'animated':dict(Counter(x.tag for x in e.iter() if x.tag.startswith('PhaseSource') and x.tag!='PhaseSourceStatic'))}
         for e in chain.findall('RenderPass')]
rows=[];errors=[]
for f in sorted((base/'Compositions').rglob('*.avc')):
 try:
  r=ET.parse(f).getroot();info=r.find('CompositionInfo')
  scopes=[{'scope':'composition','stack':stack(r)}]
  for i,g in enumerate(r.findall('Group')):scopes.append({'scope':f'group {i+1}','stack':stack(g)})
  for l in r.findall('Layer'):scopes.append({'scope':f"layer {int(l.get('layerIndex','0'))+1}",'group':l.get('layerGroup'),'name':params(l).get('Name'),'stack':stack(l)})
  clipfx=Counter();sources=Counter();examples=[]
  for c in r.iter('Clip'):
   st=stack(c)
   clipfx.update(e['effect'] for e in st if e['effect']!='Transform')
   for v in c.iter('VideoSource'):sources.update([v.get('type',v.get('name','?'))])
   if st and len(examples)<12 and any(e['effect']!='Transform' for e in st):examples.append({'clip':c.attrib,'stack':st})
  rows.append({'file':str(f),'name':info.get('name') if info is not None else f.stem,'size':[info.get('width'),info.get('height')] if info is not None else [],'layers':r.get('numLayers'),'decks':r.get('numDecks'),'midi_preset':params(r).get('MidiShortcutPreset','unspecified'),'scopes':scopes,'clip_effects':dict(clipfx),'sources':dict(sources),'clip_examples':examples})
 except Exception as e:errors.append({'file':str(f),'error':str(e)})
maps=[]
for f in sorted((base/'Shortcuts/MIDI').glob('*.xml')):
 r=ET.parse(f).getroot();items=[]
 for s in r.iter('Shortcut'):
  p=s.find('./ShortcutPath[@name="InputPath"]');raw=s.find('RawInputMessage');sub=s.find('Subtarget')
  items.append({'path':p.get('path') if p is not None else None,'device':s.get('inputDeviceName'),'behaviour_raw':s.get('behaviour'),'key_raw':raw.get('key') if raw is not None else None,'subtarget':sub.attrib if sub is not None else None,'param_type':s.get('paramNodeName')})
 maps.append({'file':str(f),'name':r.get('name'),'items':items})
result={'compositions':rows,'midi':maps,'errors':errors}
(out/'inventory.json').write_text(json.dumps(result,indent=2))
counts=Counter(e['effect'] for row in rows for scope in row['scopes'] for e in scope['stack'] if e['effect']!='Transform')
print('Parsed',len(rows),'errors',errors,'preset references',Counter(r['midi_preset'] for r in rows))
print('Installed stack instances',counts.most_common(30))
for m in maps:
 counts=Counter('/effects/'+s['path'].split('/effects/')[1].split('/')[0] if s['path'] and '/effects/' in s['path'] else 'other' for s in m['items'])
 print(m['name'],len(m['items']),counts)
for row in rows:
 print(row['name'],row['layers'],'layers',row['midi_preset'],' | '.join(s['scope']+':'+','.join(e['effect'] for e in s['stack'] if e['effect']!='Transform') for s in row['scopes'] if any(e['effect']!='Transform' for e in s['stack'])))
