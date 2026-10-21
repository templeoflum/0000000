"""Saved controller layouts and gesture ownership over the existing Heart engine."""
import copy,json,math,time
from pathlib import Path

NUM={'ParamRange','ParamFloat','ParamInt','ParamNumber'}
RATES=(.125,.25,.5,1.,2.,4.,8.)

def number(value,low=0.,high=1.):
 if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('Expected a finite number')
 if not low<=value<=high:raise ValueError('Value outside the control range')
 return float(value)

def text(value):
 if not isinstance(value,str) or not value.strip() or len(value)>180:raise ValueError('Choose a short control name')
 return value

class Performance:
 def __init__(self,engine,path=None):
  self.engine=engine;self.path=Path(path) if path else None;self.layouts={};self.active=None;self.resolved={};self.gestures={};self.springs=[];self.inputs={};self.blocked=set();self.serial=0;self.revision=0
  if self.path:
   try:
    data=json.loads(self.path.read_text())
    if data.get('version')==1:self.layouts={r['id']:self.prepare(r,stored=True) for r in data['layouts']}
   except (OSError,ValueError,KeyError,TypeError):self.layouts={}

 def contract(self,pid):
  e=self.engine
  if pid not in e.params:raise ValueError('Target unavailable')
  return json.dumps([e.catalog['epoch'],e.contracts[pid]],separators=(',',':'))

 def member(self,row,stored=False):
  r=copy.deepcopy(row)
  if r.get('follow')=='selection':text(r.get('name'));return r
  if type(r.get('id')) is not int:raise ValueError('Choose a parameter')
  pid=r['id']
  if not r.get('contract'):r['contract']=self.contract(pid)
  elif not stored and self.contract(pid)!=r['contract']:raise ValueError('Mapped target changed; choose its replacement explicitly')
  p=self.engine.params.get(pid,(None,{}))[1]
  if 'low' not in r:r['low']=p.get('min',0)
  if 'high' not in r:r['high']=p.get('max',1)
  number(r['low'],-1e12,1e12);number(r['high'],-1e12,1e12)
  if r['low']>r['high']:raise ValueError('Low must not exceed High')
  r['weight']=number(r.get('weight',1))
  return r

 def prepare(self,layout,stored=False):
  r=copy.deepcopy(layout);text(r.get('id'));text(r.get('name'))
  controls=r.get('controls',[]);inputs=r.get('inputs',[])
  if not isinstance(controls,list) or not 1<=len(controls)<=128:raise ValueError('A layout needs 1–128 controls')
  if not isinstance(inputs,list) or len(inputs)>256:raise ValueError('Too many input assignments')
  ids=set()
  for c in controls:
   key=text(c.get('id'));text(c.get('label',key))
   if key in ids:raise ValueError('Control names must be unique')
   ids.add(key);kind=c.get('kind','continuous');c['kind']=kind
   if kind not in ('continuous','button','rate','intensity'):raise ValueError('Unknown control type')
   if kind=='button':
    for edge in ('press','release'):
     a=c.get(edge)
     if a is None:continue
     if not isinstance(a,dict) or a.get('cmd') not in ('manual','toggle','envelope','drive','gesture','return_home','set_home','launch','hold','downbeat','select'):raise ValueError('Unsupported mapped action')
     if 'binding' in a:a['binding']=self.member(a['binding'],stored)
     elif 'id' in a or a.get('follow')=='selection':
      member={k:a[k] for k in ('id','follow','name','contract') if k in a};a['binding']=self.member(member,stored)
     elif 'target' in a:
      if not stored:
       t=next((t for t in self.engine.catalog['targets'] if t['id']==a['target']),None)
       if not t:raise ValueError('Target unavailable')
       a['anchors']=[self.member({'id':p['id']}) for p in t['params']]
     if a['cmd']=='launch' and not stored:
      layer=next((l for l in self.engine.catalog['layers'] if l['i']==a.get('layer')),None)
      clip=next((x for x in layer['clips'] if x['col']==a.get('col')),None) if layer else None
      if not clip or 'id' not in clip:raise ValueError('Clip unavailable')
      a.update(epoch=self.engine.catalog['epoch'],layer_id=layer['id'],clip_id=clip['id'])
    if not c.get('press'):raise ValueError('Choose a button action')
    if c.get('release'):
     a,b=c['press'],c['release']
     domain=lambda a:'hold' if a['cmd']=='hold' else json.dumps(a.get('binding'),sort_keys=True) if a.get('binding') else None
     if b['cmd'] not in ('manual','envelope','drive','hold') or domain(a) is None or domain(a)!=domain(b):raise ValueError('Momentary release must address the same control')
   else:
    members=c.get('members',[])
    if not isinstance(members,list) or not 1<=len(members)<=128:raise ValueError('Choose the control destinations')
    if len(members)>1 and c.get('balance')!='equal' and any('weight' not in m for m in members):raise ValueError('Set saved member weights or choose equal values')
    c['members']=[self.member(m,stored) for m in members]
    c['entry']=c.get('entry','absolute');c['release']=c.get('release','hold')
    if c['entry'] not in ('absolute','relative','pickup') or c['release'] not in ('hold','zero','home'):raise ValueError('Unknown entry or release behavior')
    c['release_time']=number(c.get('release_time',.15),0,120);c['home']=number(c.get('home',0))
  seen=set()
  for binding in inputs:
   key=(text(binding.get('device')),text(binding.get('control')))
   if key in seen or binding.get('slot') not in ids:raise ValueError('Each input needs one current layout control')
   seen.add(key)
   if binding.get('encoding','absolute') not in ('absolute','twos-complement','binary-offset','sign-magnitude'):raise ValueError('Unknown encoder format')
   if binding.get('behavior','relative') not in ('absolute','relative'):raise ValueError('Unknown axis behavior')
   for name,default,low,high in [('sensitivity',.5,.001,16),('deadzone',.12,0,.95),('threshold',.6,0,1),('hysteresis',.1,0,.5)]:binding[name]=number(binding.get(name,default),low,high)
  surface=r.setdefault('surface',{})
  for group,count in [('faders',4),('pads',8)]:
   slots=surface.setdefault(group,[])
   if not isinstance(slots,list) or len(slots)>count or any(s and s not in ids for s in slots):raise ValueError('Surface region needs an existing control')
   for s in slots:
    if s and (next(c for c in controls if c['id']==s)['kind']=='button')!=(group=='pads'):raise ValueError('Pads need actions; faders need continuous controls')
  return r

 def save(self,layout):
  r=self.prepare(layout);self.layouts[r['id']]=r
  if self.path:
   tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(dict(version=1,layouts=list(self.layouts.values())),indent=2));tmp.replace(self.path)
  return r

 def resolve_member(self,m):
  if m.get('follow')=='selection':
   matches=[p for owner,p in self.engine.params.values() if owner==self.engine.selected and p['name']==m['name']]
   if len(matches)!=1:raise ValueError('Selected target does not expose this control uniquely')
   m=self.member(dict(m,id=matches[0]['id'],follow=None))
  if m['id'] not in self.engine.params or self.contract(m['id'])!=m.get('contract'):raise ValueError('Mapped target unavailable')
  return copy.deepcopy(m)

 def resolve(self,c,follow=False):
  r=copy.deepcopy(c)
  if r['kind']=='button':
   for edge in ('press','release'):
    a=r.get(edge)
    if not a:continue
    if 'binding' in a:
     if a['binding'].get('follow')=='selection' and not follow:continue
     a['binding']=self.resolve_member(a['binding']);a['id']=a['binding']['id']
    for m in a.get('anchors',[]):self.resolve_member(m)
    if a['cmd']=='launch':self.launch_action(a)
   return r
  members=[]
  for m in r['members']:
   if m.get('follow')=='selection' and not follow:members.append(m);continue
   m=self.resolve_member(m);p=self.engine.params[m['id']][1]
   if p['type'] not in NUM or not p['min']<=m['low']<=m['high']<=p['max']:raise ValueError('Mapped numeric range unavailable')
   members.append(m)
  if len({m.get('id') for m in members if 'id' in m})!=sum('id' in m for m in members):raise ValueError('Control destinations must be unique')
  r['members']=members;return r

 def launch_action(self,a):
  e=self.engine;layer=next((l for l in e.catalog['layers'] if l['id']==a.get('layer_id')),None)
  clip=next((c for c in layer['clips'] if c.get('id')==a.get('clip_id')),None) if layer else None
  if a.get('epoch')!=e.catalog['epoch'] or not clip:raise ValueError('Mapped clip unavailable')
  return dict(cmd='launch',layer=layer['i'],col=clip['col'])

 def grab(self,key):
  if key not in self.layouts:raise ValueError('Choose a saved layout')
  commands=self.release();self.active=copy.deepcopy(self.layouts[key]);self.resolved={}
  for c in self.active['controls']:
   try:self.resolved[c['id']]=self.resolve(c)
   except ValueError:self.resolved[c['id']]=None
  self.blocked={source for source,v in self.inputs.items() if v.get('pressed')}
  return commands

 def release(self):
  commands=[]
  for key in list(self.gestures):commands.extend(self.end(key))
  self.active=None;self.resolved={};self.revision+=1;return commands

 def cancel(self,client=None,immediate=False):
  commands=[]
  for key,g in list(self.gestures.items()):
   if client is None or g['client']==client:commands.extend(self.end(key,immediate))
  if immediate:
   keep=[]
   for s in self.springs:
    if client is not None and s.get('client')!=client:keep.append(s);continue
    try:self.resolve_member(s['member'])
    except ValueError:continue
    if self.engine.control_owner.get(s['member']['id'])==s['token']:commands.append(dict(cmd='manual',id=s['member']['id'],value=s['end'],_owner=s['token'],_duration=0))
   self.springs=keep
  if client is None:self.springs.clear();self.inputs.clear();self.blocked.clear()
  else:
   for key in list(self.inputs):
    if key[0]==client:self.inputs.pop(key,None);self.blocked.discard(key)
  return commands

 def prune(self):
  for key,g in list(self.gestures.items()):
   try:self.resolve(g['control'],follow=True)
   except ValueError:self.gestures.pop(key,None);self.blocked.add(key)

 def value(self,c):
  if c['kind'] in ('rate','intensity'):
   ids=[m['id'] for m in c['members'] if 'id' in m]
   value=(self.engine.rate_scale if c['kind']=='rate' else self.engine.intensity_scale).get(ids[0],1) if ids else 1
   return RATES.index(value)/(len(RATES)-1) if c['kind']=='rate' else value
  values=[]
  for m in c.get('members',[]):
   if 'id' not in m or not m['weight'] or m['high']==m['low']:continue
   v=self.engine.current_value(m['id']);values.append((v-m['low'])/((m['high']-m['low'])*m['weight']))
  return min(1,max(0,max(values,default=0)))

 def action(self,a,token,release=False):
  a=copy.deepcopy(a)
  if release and a['cmd']=='hold' and self.engine.global_owner.get('hold')!=token:return []
  if 'binding' in a:
   m=self.resolve_member(a['binding']);pid=m['id']
   if release and self.engine.control_owner.get(pid)!=token:return []
   a['id']=pid
  for m in a.get('anchors',[]):
   self.resolve_member(m)
   if release and self.engine.control_owner.get(m['id'])!=token:return []
  if a['cmd']=='launch':a=self.launch_action(a)
  if a['cmd']=='toggle':
   pid=a['id'];p=self.engine.params[pid][1];v=self.engine.current_value(pid)
   if p['type'] in NUM:v=p['max'] if v<=(p['min']+p['max'])/2 else p['min']
   elif p['type'] in ('ParamBool','ParamBoolean'):v=not bool(v)
   else:raise ValueError('Toggle requires an on/off or numeric control')
   a.update(cmd='manual',value=v)
  a['_owner']=token;return [a]

 def event(self,client,slot,phase,value=None,delta=None,device='surface',control=None):
  key=(client,device,control or slot)
  if phase not in ('seed','begin','move','end'):raise ValueError('Unknown input phase')
  if value is not None:value=number(value)
  if delta is not None:delta=number(delta,-1,1)
  if phase=='seed':self.inputs[key]=dict(pressed=bool(value),value=value);self.blocked.add(key) if value else self.blocked.discard(key);return []
  if phase=='end':self.inputs[key]=dict(pressed=False,value=0);self.blocked.discard(key);return self.end(key)
  if phase=='begin' and not self.inputs.get(key,{}).get('pressed'):self.blocked.discard(key)
  if key in self.blocked:return []
  if not self.active or slot not in self.resolved:raise ValueError('Grab a layout containing this control')
  c=self.resolved[slot]
  if c is None:raise ValueError('Mapped target unavailable')
  self.inputs[key]=dict(pressed=c['kind']=='button',value=value)
  if c['kind']=='button' and key in self.gestures:return []
  g=self.gestures.get(key)
  if not g:
   c=self.resolve(c,follow=True);self.serial+=1;token='input:'+str(self.serial)
   g=dict(client=client,control=c,token=token,start=value,base=self.value(c) if c['kind']!='button' else 0.,value=None,picked=c.get('entry')!='pickup',previous=None)
   self.gestures[key]=g
   if c['kind']=='button':return self.action(c['press'],token)
  c=g['control'];self.resolve(c,follow=True)
  if value is None and delta is None:raise ValueError('Expected a control value')
  v=value if delta is None else min(1,max(0,(g['value'] if g['value'] is not None else g['base'])+delta))
  if c['entry']=='relative' and delta is None:v=min(1,max(0,g['base']+value-(g['start'] if g['start'] is not None else value)))
  if not g['picked']:
   target=self.value(c);previous=g['previous'];g['previous']=v
   if abs(v-target)>.025 and (previous is None or (previous-target)*(v-target)>0):return []
   g['picked']=True
  g['value']=v;commands=[]
  for m in c['members']:
   pid=m['id']
   if c['kind']=='continuous':commands.append(dict(cmd='manual',id=pid,value=m['low']+v*m['weight']*(m['high']-m['low']),_owner=g['token'],_duration=0))
   elif c['kind']=='rate':self.engine.rate_scale[pid]=RATES[min(len(RATES)-1,int(v*len(RATES)))]
   else:self.engine.intensity_scale[pid]=v
  return commands

 def end(self,key,immediate=False):
  g=self.gestures.pop(key,None)
  if not g:return []
  c=g['control'];token=g['token']
  if c['kind']=='button':
   try:
    commands=self.action(c['release'],token,True) if c.get('release') else []
    if immediate:
     for a in commands:
      if a['cmd']=='envelope':
       p=self.engine.params[a['id']][1];cfg=self.engine.envelope_settings.get(a['id'],{});a.update(cmd='manual',value=cfg.get('low',p['min']) if a['direction']=='out' else cfg.get('high',p['max']),_duration=0)
    return commands
   except ValueError:return []
  if c['kind']!='continuous' or c['release']=='hold' or not g['picked']:return []
  commands=[]
  for m in c['members']:
   pid=m['id']
   if self.engine.control_owner.get(pid)!=token:continue
   end=m['low']+(c['home'] if c['release']=='home' else 0)*m['weight']*(m['high']-m['low'])
   if immediate:commands.append(dict(cmd='manual',id=pid,value=end,_owner=token,_duration=0))
   else:self.springs.append(dict(client=g['client'],member=m,token=token,start=self.engine.current_value(pid),end=end,elapsed=0,duration=c['release_time']))
  return commands

 def tick(self,dt):
  if self.engine.hold:return
  keep=[]
  for s in self.springs:
   pid=s['member']['id']
   try:self.resolve_member(s['member'])
   except ValueError:continue
   if self.engine.control_owner.get(pid)!=s['token']:continue
   s['elapsed']+=max(0,dt);u=min(1,s['elapsed']/s['duration']) if s['duration'] else 1
   value=s['start']+(s['end']-s['start'])*(1-(1-u)**2)
   self.engine.manual(pid,value,owner=s['token'],duration=0)
   if u<1:keep.append(s)
  self.springs=keep

 def input(self,client,d):
  device=text(d.get('device'));control=text(d.get('control'))
  if d.get('phase') in ('seed','end'):return self.event(client,'',d['phase'],d.get('value'),device=device,control=control)
  if not self.active:return []
  row=next((i for i in self.active['inputs'] if i['device']==device and i['control']==control),None)
  if not row:return []
  return self.event(client,row['slot'],d.get('phase','move'),d.get('value'),d.get('delta'),device,control)

 def state(self):
  controls=[]
  if self.active:
   for c in self.active['controls']:
    try:self.resolve(self.resolved[c['id']] or c);ready=self.resolved[c['id']] is not None
    except ValueError:ready=False
    value=None
    if ready and c['kind']!='button':
     try:value=self.value(self.resolve(self.resolved[c['id']],follow=True))
     except ValueError:pass
    controls.append(dict(id=c['id'],label=c.get('label',c['id']),kind=c['kind'],ready=ready,value=value,held=any(g['control']['id']==c['id'] for g in self.gestures.values())))
  return dict(revision=self.revision,layouts=[dict(id=r['id'],name=r['name']) for r in self.layouts.values()],active=self.active['id'] if self.active else None,name=self.active['name'] if self.active else '',controls=controls)
