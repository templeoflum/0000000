"""Cold-path discovery process. Never runs in the timing or output process."""
import json, urllib.request, urllib.error, copy, sys, time, re
from concurrent.futures import ThreadPoolExecutor
NUM={'ParamRange','ParamFloat','ParamInt','ParamNumber'}
SUPPORTED=NUM|{'ParamChoice','ParamBool','ParamBoolean','ParamEvent','ParamTrigger','ParamColor'}
def label(o):
 n=o.get('name','');return n.get('value','') if isinstance(n,dict) else n

def discover(c):
 targets=[];layers=[];stage_members={};stage_groups=[];group_members={};groups=[]
 for g in (c.get("layergroups",c.get("groups")) or []):
  members=[m["id"] if isinstance(m,dict) else m for m in (g.get("layers") or [])]
  groups.append(dict(id=g["id"],name=label(g),members=members,stage=label(g).startswith("__stage__")))
  for mid in members:group_members[mid]=g["id"]
  if label(g).startswith("__stage__"):
   stage_groups.append(g["id"])
   for member in (g.get("layers") or []):stage_members[member["id"] if isinstance(member,dict) else member]=g["id"]
 def target(id,name,kind,params,**context):
  rows=[]
  for name_,p in (params or {}).items():
   if not isinstance(p,dict) or 'id' not in p or p.get('valuetype') not in SUPPORTED:continue
   t=p['valuetype'];lo=p.get('min',0);hi=p.get('max',1)
   if t in NUM and (not isinstance(lo,(int,float)) or not isinstance(hi,(int,float)) or hi<=lo):continue
   row=dict(id=p['id'],name=name_,type=t,min=lo,max=hi,value=p.get('value'),options=p.get('options',[]))
   if t in NUM:row.update({key:p[key] for key in ('in','out') if key in p})
   rows.append(row)
  if rows:targets.append(dict(id=str(id),label=name,kind=kind,params=rows,**context))
 def effects(owner,video,**context):
  for position,e in enumerate((video or {}).get('effects') or [],1):
   params=dict(e.get('params') or {});params.update(e.get('mixer') or {});bp=e.get('bypassed')
   if bp:params['Bypass']={**bp,'valuetype':'ParamBoolean'}
   params=dict(sorted(params.items(),key=lambda item:({'Bypass':0,'Opacity':1,'Blend Mode':2}.get(item[0],3))))
   target('effect:'+str(e['id']),owner+' / '+label(e),'effect',params,title=str(position)+' · '+label(e),effect_name=label(e),effect_id=e['id'],position=position,**context)
 def native(owner,video):
  video=video or {}
  params={k:p for k,p in owner.items() if isinstance(p,dict) and p.get('valuetype') in SUPPORTED}
  params.update({k:p for k,p in video.items() if isinstance(p,dict) and p.get('valuetype') in SUPPORTED})
  if video.get('opacity'):params['Level']={**video['opacity'],'valuetype':'ParamRange','min':0,'max':1};params.pop('opacity',None)
  if owner.get('bypassed'):params['Hidden']={**owner['bypassed'],'valuetype':'ParamBoolean'};params.pop('bypassed',None)
  for section in ('transition','autopilot'):
   for key,value in (owner.get(section) or {}).items():
    if isinstance(value,dict) and value.get('valuetype') in SUPPORTED:params[section+' · '+key]=value
  for key in ('width','height','selected','colorid'):params.pop(key,None)
  return params
 target('composition:'+str(c['name']['id']),'Composition','composition',native(c,c.get('video',{})),scope='composition',title='Parameters')
 cross=c.get('crossfader') or {}
 target('crossfader:'+str(cross.get('id','')), 'Crossfader','crossfader',{**{k:v for k,v in cross.items() if isinstance(v,dict) and v.get('valuetype') in SUPPORTED},**(cross.get('mixer') or {})},scope='crossfader',title='A / B')
 effects('Composition',c.get('video',{}),scope='composition')
 for g in (c.get('layergroups',c.get('groups')) or []):
  scope='stage' if g['id'] in stage_groups else 'composition'
  target('group:'+str(g['id']),label(g),'group',native(g,g.get('video',{})),scope=scope,group_id=g['id'],title=label(g)+' · Controls')
  effects(label(g),g.get('video',{}),scope=scope,group=label(g),group_id=g['id'])
 for i,l in enumerate(c.get('layers',[]),1):
  name=label(l);v=l.get('video') or {};clips=[];active=0;playing=l.get('active_clip');playing_id=playing.get('id') if isinstance(playing,dict) else None
  target('layer:'+str(l['id']),name,'layer',native(l,v),scope='layer',layer=i,title='Parameters');effects(name,v,scope='layer',layer=i)
  for col,clip in enumerate(l.get('clips') or [],1):
   video=clip.get('video')
   if not video:continue
   clips.append(dict(col=col,id=clip['id'],name=label(clip),description=video.get('description','')))
   if playing_id is not None:
    if clip['id']!=playing_id:continue
    clip=playing;video=clip.get('video') or video
   elif 'active_clip' in l or not str((clip.get('connected') or {}).get('value','')).startswith('Connected'):continue
   active=col
   target('clip:'+str(clip['id']),name+' / '+label(clip),'clip',native(clip,video),scope='clip',layer=i,clip=col,clip_id=clip['id'],description=video.get('description',''),title='Clip controls')
   target('source:'+str(clip['id']),name+' / '+label(clip),'source',video.get('sourceparams',{}),scope='clip',layer=i,clip=col,clip_id=clip['id'],description=video.get('description',''),title='Source · '+label(clip));effects(name+' / '+label(clip),video,scope='clip',layer=i,clip=col,clip_id=clip['id'])
  layers.append(dict(i=i,name=name,clips=clips,active=active,id=l['id'],stage=stage_members.get(l['id']),group_id=group_members.get(l['id'])))
 for t in targets:
  if t.get('layer'):t['stage']=layers[t['layer']-1]['stage'];t['layer_id']=layers[t['layer']-1]['id'];t['group_id']=layers[t['layer']-1].get('group_id')
 return dict(type='catalog',epoch=str(c['name']['id']),targets=targets,layers=layers,groups=groups,tempo=c.get('tempocontroller',{}))

def refresh_active(catalog,active):
 """Refresh playing sources by stable layer ID without fetching the clip grid."""
 result=copy.deepcopy(catalog);changed=False
 def structure(targets):
  return [dict({k:v for k,v in t.items() if k not in ('params','authored','native_phase_clip')},params=[{k:v for k,v in p.items() if k not in ('value','authored','native_phase')} for p in t['params']]) for t in targets]
 for layer in result['layers']:
  if layer['id'] not in active:continue
  clip=active[layer['id']];col=0;targets=[]
  if clip and clip.get('id') and clip.get('video'):
   known=next((c for c in layer['clips'] if c['id']==clip['id']),None)
   if known is None:return dict(needs_full=True)
   col=known['col']
   stub=dict(id=layer['id'],name=layer['name'],clips=[{} for _ in range(col-1)]+[clip],active_clip=clip)
   found=discover(dict(name={'id':catalog['epoch']},layers=[stub]))
   targets=[t for t in found['targets'] if t.get('scope')=='clip']
   for t in targets:t.update(layer=layer['i'],layer_id=layer['id'],stage=layer.get('stage'),group_id=layer.get('group_id'))
  old=[t for t in result['targets'] if t.get('scope')=='clip' and t.get('layer_id')==layer['id']]
  if layer['active']==col and structure(old)==structure(targets):continue
  changed=True;layer['active']=col;layer.pop('pending_clip',None)
  result['targets']=[t for t in result['targets'] if not (t.get('scope')=='clip' and t.get('layer_id')==layer['id'])]+targets
 result['_changed']=changed
 return result

def read_active(layer):
 try:
  with urllib.request.urlopen(f"http://127.0.0.1:8080/api/v1/composition/layers/by-id/{layer['id']}/clips/active",timeout=3) as f:clip=json.load(f)
 except urllib.error.HTTPError as ex:
  if ex.code!=404:raise
  clip=None
 return layer['id'],clip

def native_phases(result, policy, previous=None):
 """Opted-in clips use paused native timelines; config contains no look values."""
 previous=previous or {};old={p['id']:p for t in previous.get('targets',[]) for p in t['params']}
 fresh=time.monotonic()-previous.get('_phase_checked',0)>=3
 result['_phase_checked']=time.monotonic() if fresh else previous['_phase_checked']
 jobs=[]
 for t in result['targets']:
  t.pop('native_phase_clip',None)
  for p in t['params']:p.pop('native_phase',None)
  ref=next((r for r in policy.get('clips',[]) if r['clip_id']==t.get('clip_id') and r['layer_id']==t.get('layer_id')),None)
  source=next((s for s in result['targets'] if s['kind']=='source' and s.get('clip_id')==t.get('clip_id')),None)
  if not ref or not source or source.get('description')!=ref['description']:continue
  if t['kind']!='source':continue
  t['native_phase_clip']=True
  for p in t['params']:
   if p['type'] not in NUM:continue
   route=dict(layer=t['layer'],clip=t['clip'],clip_id=t['clip_id'],source=ref['osc_source'],description=ref['description'],name=p['name'],min=p['min'],max=p['max'])
   if not fresh and p['id'] in old:
    if old[p['id']].get('native_phase'):p['native_phase']=route
   else:jobs.append((p,route))
 def inspect(job):
  p,route=job
  try:
   with urllib.request.urlopen(f"http://127.0.0.1:8080/api/v1/parameter/by-id/{p['id']}/phase-source",timeout=2) as f:a=json.load(f)
   if a.get('phase_source')=='timeline' and a.get('parameters',{}).get('PlayDirection',{}).get('value')=='||':p['native_phase']=route
  except (OSError,ValueError):pass
 with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(inspect,jobs))
 def modes(c):return [(t['id'],t.get('native_phase_clip'),[(p['id'],p.get('native_phase')) for p in t['params']]) for t in c.get('targets',[])]
 if modes(result)!=modes(previous):result['_changed']=True
 return result

if __name__=='__main__':
 from pathlib import Path
 if Path(__file__).with_name('api-paused.json').exists():raise SystemExit('Heart API paused after Resolume memory incident')
 catalog={}
 if '--active' in sys.argv:
  catalog=json.load(sys.stdin)
  with ThreadPoolExecutor(max_workers=4) as pool:active=dict(pool.map(read_active,catalog['layers']))
  result=refresh_active(catalog,active)
 else:
  with urllib.request.urlopen('http://127.0.0.1:8080/api/v1/composition',timeout=12) as f:c=json.load(f)
  result=discover(c)
 try:policy=json.loads(Path(__file__).with_name('native-phase.json').read_text())
 except (OSError,ValueError):policy={}
 result=native_phases(result,policy,catalog)
 print(json.dumps(result,separators=(',',':')))
