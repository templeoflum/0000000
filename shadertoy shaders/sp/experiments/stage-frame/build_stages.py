"""Expand a native-saved Wire section graph; keep originals untouched."""
import copy,json,pathlib,uuid,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
T=json.loads((ROOT/'Heart Treehouse Leaves6 POC/Heart Treehouse Leaves6 POC.wire').read_text())
STILL={'.png','.jpg','.jpeg','.tif','.tiff'}
def setv(n,k,v):
 for container in ('constants','attributes'):
  if k in n.get(container,{}):n[container][k]['value']=v;return
 raise KeyError(k)
def param(e,path,default):
 v=e.find(path);return v.get('value',default) if v is not None else default
def build(stage):
 src=ROOT.parents[1]/'restored-compositions'/f'{stage}.avc';r=ET.parse(src).getroot();out=copy.deepcopy(T);p=out['patch'];p['nodes']={};p['connections']=[];p['inputOrder']={'groups':{},'roots':[]};nid=0;sections=[];last=None
 def add(template,name=None):
  nonlocal nid
  n=copy.deepcopy(T['patch']['nodes'][str(template)]);i=nid;nid+=1
  if name:n['name']=name
  n['bounds']['x']=(i%12)*210;n['bounds']['y']=(i//12)*160;n['thumbnail_visible']=False;p['nodes'][str(i)]=n;return i,n
 def edge(a,ap,b,bp):p['connections'].append({'from':[a,ap],'to':[b,bp]})
 global_shuffle,_=add(23,'Shuffle All');global_auto,_=add(24,'Auto All');global_events,_=add(130,'Auto All Events');edge(global_auto,'output',global_events,'input0')
 p['inputOrder']['roots'] += [{'node':global_shuffle},{'node':global_auto}]
 allowed=range(1,21) if stage=='portal' else range(1,19)
 for layer in r.findall('Layer'):
  li=int(layer.get('layerIndex'));name=param(layer,"./Params/*[@name='Name']",f'Section {li}') or f'Section {li}'
  if li not in allowed:continue
  paths=[]
  for clip in r.findall('Deck/Clip'):
   if int(clip.get('layerIndex'))!=li:continue
   v=clip.find('PreloadData/VideoFile')
   if v is not None and pathlib.Path(v.get('value')).suffix.lower() in STILL:paths.append(v.get('value'))
  if not paths:continue
  assert all(pathlib.Path(x).is_file() for x in paths),name
  ids={};nodes={}
  core=[1,3,4,5,6,7,9,10,18,20,21,22,23,24,125,126,130,132]
  mask=layer.find(".//ParamImageFile[@name='Image']")
  if mask is not None:core += [127,128,129]
  for old in core:ids[old],nodes[old]=add(old,f'{name} {T["patch"]["nodes"][str(old)]["name"]}')
  # Keep only the final, verified previous/current path; no obsolete Read helper.
  for c in T['patch']['connections']:
   a,ap=c['from'];b,bp=c['to']
   if a in ids and b in ids and not (a==5 and b==4):edge(ids[a],ap,ids[b],bp)
  join=nodes[9];setv(join,'num-channels',len(paths));join['constants']={f'channel{k}':{'type':'texture2d','value':None} for k in range(len(paths))}
  join['attributes']={k:v for k,v in join['attributes'].items() if not k.startswith('input') or k=='input-type'}
  for k in range(len(paths)):join['attributes'][f'input{k}-dimensions']={'type':'integer','value':1}
  for old in (3,4):setv(nodes[old],'collection-dimensions',len(paths))
  for k,path in enumerate(paths):
   i,n=add(0,f'{name} image {k+1}');v=n['attributes']['image']['value'];v['path']['main']=path
   # PNG source dimensions are taken from the authoritative composition below.
   v['value']['resolution']={'width':3840 if stage=='portal' else 1920,'height':1440}
   edge(i,'output',ids[9],f'channel{k}')
  setv(nodes[5],'seed',li*7919);edge(global_shuffle,'output',ids[5],'input');edge(global_shuffle,'output',ids[7],'restart');edge(global_events,'output0',ids[6],'enabled')
  setv(nodes[5],'argument1',-.499999);setv(nodes[5],'argument2',len(paths)-.500001);setv(nodes[5],'precision',1)
  duration=float(param(layer,"./ClipTransition/Params/*[@name='Duration']",'4.92'))
  setv(nodes[125],'max',max(10,duration));setv(nodes[125],'input',max(.05,duration));setv(nodes[126],'input',1/max(6,duration+.25));setv(nodes[24],'input',True)
  setv(nodes[21],'input',1)
  transition=layer.find("./VideoTrack/ChoosableMixer[@name='Transition']/RenderPass")
  mode=(transition.get('type') if transition is not None else 'Alpha');modes={'LumaKeyI':25,'LumaKey':24,'Difference':16,'DifferenceI':17,'Add':10,'Alpha':11}
  setv(nodes[1],'mode',modes.get(mode,11))
  if mask is not None:
   nodes[127]['attributes']['image']['value']['path']['main']=mask.get('value')
  else:edge(ids[1],'output',ids[22],'input2')
  # Preserve the saved section opacity bounds and bounce duration where present.
  opacity=layer.find("./VideoTrack/Params/*[@name='Opacity']");opacity_default=float(opacity.get('value','1')) if opacity is not None else 1
  stack,sn=add(22,f'{name} Stage Blend');blend=layer.find("./VideoTrack/ChoosableMixer[@name='Blend']/RenderPass");blendname=blend.get('type','Alpha') if blend is not None else 'Alpha';setv(sn,'mode',modes.get(blendname,11))
  edge(ids[22],'output',stack,'input2')
  if last is not None:edge(last,'output',stack,'input1')
  last=stack
  bounds=opacity.find("ValueRange[@name='startStop']") if opacity is not None else None
  timeline=opacity.find('PhaseSourceTimeline') if opacity is not None else None
  if bounds is not None and timeline is not None:
   lo=float(bounds.get('min'));hi=float(bounds.get('max'));d=opacity.find('DurationSource');seconds=float(d.get('userDuration','10')) if d is not None else 10
   osc,on=add(133,f'{name} Opacity Motion');setv(on,'unipolar',True);setv(on,'frequency',1/(2*max(.01,seconds)));setv(on,'amplitude',hi-lo);setv(on,'offset',lo);edge(osc,'output',stack,'opacity2')
  else:setv(sn,'opacity2',opacity_default)
  for old in (21,24,23,125,126):p['inputOrder']['roots'].append({'node':ids[old]})
  sections.append({'layer':li,'name':name,'images':len(paths),'transition':mode,'blend':blendname,'mask':mask.get('value') if mask is not None else None})
 master,mn=add(21,'Frame Level');setv(mn,'input',1);master_mix,_=add(22,'Master Level');edge(last,'output',master_mix,'input2');edge(master,'output',master_mix,'opacity2');p['inputOrder']['roots'].insert(0,{'node':master});output,_=add(19,'Stage Frame Output');edge(master_mix,'output',output,'input')
 p['nextNodeId']=nid;p['meta']['identifier']=str(uuid.uuid4());p['meta']['displayName']=f'Heart {stage.title()} Frame';p['meta']['description']='Full still-image section bank prototype. Native generators and group effects remain in original composition; parity not yet verified.';p['meta']['resolution']={'width':3840 if stage=='portal' else 1920,'height':1440 if stage=='portal' else 1080};p['ui']={'camera':{'x':0,'y':0,'zoom':.2},'selection':[]}
 folder=ROOT/f'Heart {stage.title()} Frame';folder.mkdir(exist_ok=True);file=folder/(folder.name+'.wire');file.write_text(json.dumps(out,indent=2))
 report={'stage':stage,'sections':sections,'images':sum(s['images'] for s in sections),'nodes':nid,'wire':str(file),'status':'generated; native load/render check pending','limitations':['Native outline/detail generators and group effects are not ported; use original composition for exact appearance.','Opacity bounce interpretation and per-clip duration variations require parity checks.']};(folder/'build-report.json').write_text(json.dumps(report,indent=2));print(stage,len(sections),report['images'],nid)
 # Exact fallback, with original settings and native generators, only relinked media.
 import shutil
 fallback=ROOT/'Festival Originals';fallback.mkdir(exist_ok=True);shutil.copy2(src,fallback/f'{stage}.avc')
for stage in ('portal','treehouse'):build(stage)
