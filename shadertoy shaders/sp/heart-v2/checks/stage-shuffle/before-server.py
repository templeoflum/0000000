#!/usr/bin/env python3
"""Heart v2: small timing loop, isolated discovery and output, compact surface state."""
import asyncio,json,math,random,time,sys,os,copy,urllib.request,hashlib
from pathlib import Path
from collections import deque
import websockets
from smart_motion import Slot,RATIO_LIB,FAMILIES
from performance import Performance
from play_actions import PlayActions,effect_parameters,hit_bindings
from authored import Authored,heart_seed
from session_controls import SessionControls,native_program,same_program
ROOT=Path(__file__).resolve().parent
def surface_document():
 body=(ROOT/'index.html').read_bytes()
 assets=b''.join((ROOT/name).read_bytes() for name in ('controllers.js','performance_surface.js','performance.css','playing.js','playing.css') if (ROOT/name).exists())
 return body,hashlib.sha256(body+assets).hexdigest()

NUM={'ParamRange','ParamFloat','ParamInt','ParamNumber'}

def finite(value,lo,hi):
 if isinstance(value,bool):raise ValueError('Expected a number')
 value=float(value)
 if not math.isfinite(value):raise ValueError('Expected a finite number')
 return max(lo,min(hi,value))

def native_drive_range(p):
 """Native In/Out are the authored sweep; min/max are only hardware limits."""
 try:
  bounds=[finite((float(p.get(key,default))-p['min'])/(p['max']-p['min']),0,1) for key,default in (('in',p['min']),('out',p['max']))]
  return tuple(sorted(bounds))
 except (TypeError,ValueError):return 0.,1.

class Engine:
 def __init__(self):
  self.session=SessionControls(self)
  self.authored=Authored();self.clip_starts=set();self.phase_starts=set();self.rack_flash={};self.library={}
  self.rack_config={};self.pending_hits={};self.rack_returns={};self.rack_levels={}
  self.play_actions=PlayActions(self);self.contracts={};self.control_owner={};self.control_serial=0;self.global_owner={};self.rate_scale={};self.intensity_scale={};self.performance=Performance(self)
  self.retained=set();self.binding_reset=True;self.launch_serial=0;self.launches={}
  self.envelopes={};self.envelope_settings={};self.homes={};self.watched=set();self.switches={};self.switch_serial=0;self.observed={}
  self.catalog={'type':'catalog','epoch':'','targets':[],'layers':[]};self.params={};self.slots={};self.groups={};self.owned=set();self.selected='';self.armed=False;self.connected=False;self.hold=False;self.bpm=120.;self.error='';self.revision=0;self.lastout={};self.gaps=deque(maxlen=600);self.work=deque(maxlen=600);self.bridgework=0;self.sent=0;self.scan_ms=0
 def reconcile(self,catalog,launching=False,scan_started=None):
  catalog=copy.deepcopy(catalog)
  self.authored.annotate(catalog)
  phase_clips={t['clip_id'] for t in catalog['targets'] if t.get('native_phase_clip')}
  for t in catalog['targets']:
   if catalog.get('native_phase_mode') or t.get('clip_id') in phase_clips:
    t.pop('authored',None)
    for p in t['params']:p.pop('authored',None)
  if self.library.get('epoch')==catalog['epoch']:
   for layer in catalog['layers']:
    for clip in layer['clips']:
     ref=self.library.get('clips',{}).get(str(clip['id']))
     if ref and ref['layer_id']==layer['id'] and ref['name']==clip['name'] and ref['description']==clip.get('description'):
      clip.update({k:ref[k] for k in ('family','variant','primary')})
  catalog['motion_families']=FAMILIES;catalog['motion_ratios']=list(RATIO_LIB)
  catalog['effect_rack']=self.rack_config if self.rack_config.get('epoch')==catalog['epoch'] else {}
  self.binding_reset=catalog['epoch']!=self.catalog['epoch']
  if self.binding_reset:self.launches.clear();self.clip_starts.clear();self.phase_starts.clear();self.session.cancel();self.session.loops.clear()
  for lid,launch in list(self.launches.items()):
   layer=next((l for l in catalog['layers'] if l['id']==lid),None)
   active=next((c for c in layer['clips'] if c['col']==layer['active']),None) if layer else None
   complete=not launching and (not layer['active'] if layer and launch['col']==0 else bool(active and active['col']==launch['col'] and (launch['id'] is None or active.get('id')==launch['id'])))
   if not layer or complete or time.monotonic()-launch['started']>10:
    self.launches.pop(lid,None)
    if layer and not complete:self.error='Clip launch was not confirmed; showing the current clip'
   else:
    catalog['targets']=[t for t in catalog['targets'] if not (t.get('scope')=='clip' and t.get('layer')==layer['i'])]
    layer['active']=0;layer['pending_clip']=launch['col']
  params={p['id']:(t['id'],p) for t in catalog['targets'] for p in t['params']}
  def contracts(c):
   return {p['id']:(t['id'],t['kind'],t.get('scope'),t.get('layer_id'),t.get('clip_id'),p['name'],p['type'],p['min'],p['max'],p.get('options',[]),p.get('native_phase')) for t in c['targets'] for p in t['params']}
  before,after=contracts(self.catalog),contracts(catalog);self.contracts=after
  self.retained={pid for pid in params if not self.binding_reset and bool(self.catalog.get('native_phase_mode'))==bool(catalog.get('native_phase_mode')) and before.get(pid)==after[pid]}
  self.rack_returns={pid:record for pid,record in self.rack_returns.items() if pid in self.retained and after.get(pid)==record['contract']}
  self.rack_levels={pid:value for pid,value in self.rack_levels.items() if pid in self.retained}
  self.observed={pid:sample for pid,sample in self.observed.items() if pid in self.retained and (scan_started is None or sample[1]>=scan_started)}
  changed=self.binding_reset or before!=after
  for t in catalog['targets']:self.groups.setdefault(t['id'],dict(pattern=0,spread=1,seed=0,depth=1.,fm=0.,speed=1.))
  self.switches={pid:sw for pid,sw in self.switches.items() if pid in self.retained}
  for pid,sw in list(self.switches.items()):
   if pid not in params:self.switches.pop(pid,None);continue
   p=params[pid][1]
   if not sw['pending'] and p['value']==sw['value']:self.switches.pop(pid,None)
   elif time.monotonic()<sw['until']:p['value']=sw['value']
   elif not sw['pending']:self.switches.pop(pid,None)
  oldslots=self.slots;newslots={}
  for pid,(target,p) in params.items():
   if p['type'] not in NUM:continue
   same=pid in self.retained
   if same:
    newslots[pid]=oldslots[pid]
    if not p.get('native_phase') and not newslots[pid].cfg.get('range_authored'):
     lo,hi=native_drive_range(p);newslots[pid].cfg.update(lo=lo,hi=hi)
   else:
    self.envelopes.pop(pid,None);self.envelope_settings.pop(pid,None)
    lo,hi=native_drive_range(p)
    sl=Slot(p['name'],False);sl.index=sum(1 for x in newslots if params[x][0]==target);sl.cfg=dict(ratio='1:1',mult=1.,offset=0.,shape=1,lo=lo,hi=hi,manual=finite((float(p['value'])-p['min'])/(p['max']-p['min']),0,1),lock=False,range_authored=False);sl.dur=.2;newslots[pid]=sl;self.owned.discard(pid)
    seed=heart_seed(p,self.bpm)
    if seed:sl.cfg.update({k:v for k,v in seed.items() if k!='drive'},range_authored=True)
    if p.get('native_phase'):
     sl.cfg.update(lo=0.,hi=1.,manual=self.native_position(p,p['value']),range_authored=False)
     sl.phi=math.acos(1-2*sl.cfg['manual'])/(2*math.pi)
   self.groups.setdefault(target,dict(pattern=0,spread=1,seed=0,depth=1.,fm=0.,speed=1.))
   newslots[pid].retarget(self.groups[target],time.perf_counter())
  self.envelopes={pid:v for pid,v in self.envelopes.items() if pid in newslots};self.envelope_settings={pid:v for pid,v in self.envelope_settings.items() if pid in newslots}
  self.params=params;self.slots=newslots;self.catalog=catalog;self.owned.intersection_update(params);self.groups={k:v for k,v in self.groups.items() if any(t['id']==k for t in catalog['targets'])}
  tempo=catalog.get('tempo',{}).get('tempo',{}).get('value')
  if isinstance(tempo,(int,float)) and not self.armed:self.bpm=finite(tempo,20,500)
  if changed:
   self.revision+=1;self.lastout={pid:v for pid,v in self.lastout.items() if pid in self.retained}
   self.control_owner={pid:v for pid,v in self.control_owner.items() if pid in self.retained}
   self.rate_scale={pid:v for pid,v in self.rate_scale.items() if pid in self.retained};self.intensity_scale={pid:v for pid,v in self.intensity_scale.items() if pid in self.retained}
   self.performance.prune()
  for t in catalog['targets']:
   if not catalog.get('native_phase_mode') and ((t.get('authored') and t.get('layer_id') in self.authored.data.get('auto_layers',[])) or t.get('native_phase_clip')) and any(p['id'] not in self.retained for p in t['params']):self.clip_starts.add(t['clip_id'])
  self.clip_starts.intersection_update(t['clip_id'] for t in catalog['targets'] if t.get('authored') or t.get('native_phase_clip'))
  self.phase_starts.intersection_update(pid for pid,(_,p) in params.items() if p.get('native_phase'))
  if catalog.get('native_phase_mode'):self.phase_starts.update(pid for pid,(_,p) in params.items() if p.get('native_phase') and pid not in self.retained)
  if self.selected not in self.groups:self.selected=next((t['id'] for t in catalog['targets'] if t['kind']=='source'),next(iter(self.groups),''))
  return changed
 def reset_clip(self,clip_id):
  refs=self.authored.targets(self.catalog,clip_id);values=[];now=time.perf_counter()
  for target in refs:
   tid=target['id'];self.groups[tid]=dict(pattern=0,spread=1,seed=0,depth=1.,fm=0.,speed=1.)
   for ref in target['params']:
    pid=ref['id'];p=self.params[pid][1]
    if ref.get('source')=='native':continue
    self.claim(pid);self.envelopes.pop(pid,None);self.lastout.pop(pid,None);self.rate_scale.pop(pid,None);self.intensity_scale.pop(pid,None)
    if pid in self.slots:
     sl=self.slots[pid];seed=heart_seed(p,self.bpm)
     if not seed:continue
     sl.cfg.update({k:v for k,v in seed.items() if k!='drive'},range_authored=True);sl.drive=seed['drive'];sl.phi=sl.phi_fm=0;sl.prev=sl.target=None;sl.dur=0;sl.retarget(self.groups[tid],now);self.owned.add(pid)
     # A startup frame is bounded before the output worker claims the native timeline.
     v=p['min']+sl.value(sl.target)*(p['max']-p['min']);values.append((pid,v));self.lastout[pid]=v
    elif p['type'] not in ('ParamEvent','ParamTrigger'):
     values.append((pid,ref['value']));p['value']=ref['value']
  return values
 def binding(self):
  tempo=self.catalog.get('tempo',{});extra=[p['id'] for p in tempo.values() if isinstance(p,dict) and p.get('id')]
  return dict(cmd='bind',epoch=self.epoch,ids=list(self.params)+extra,numeric=list(self.slots),keep=list(self.retained)+extra,reset=self.binding_reset,phases={pid:p['native_phase'] for pid,(_,p) in self.params.items() if p.get('native_phase')})
 @staticmethod
 def native_position(p,value):
  a,b=p.get('in',p['min']),p.get('out',p['max'])
  return finite((value-a)/(b-a),0,1) if a!=b else .5
 def phase_clip(self,clip_id):
  return any(t.get('native_phase_clip') and t.get('clip_id')==clip_id for t in self.catalog['targets'])
 def start_phases(self,clip_id):
  for pid,(_,p) in self.params.items():
   if p.get('native_phase',{}).get('clip_id')==clip_id:self.drive(pid,True)
 def drive_ready(self,p):
  return bool(p.get('native_phase')) if self.catalog.get('native_phase_mode') else True
 def start_prepared(self):
  for pid in tuple(self.phase_starts):
   self.phase_starts.discard(pid)
   if pid in self.params and self.params[pid][1].get('native_phase'):self.drive(pid,True)
 def begin_launch(self,li,col):
  layer=next((l for l in self.catalog['layers'] if l['i']==li),None)
  clip=next((c for c in layer['clips'] if c['col']==col),None) if layer else None
  if not layer or (col!=0 and not clip):raise ValueError('Clip unavailable')
  self.launch_serial+=1
  self.launches[layer['id']]=dict(col=col,id=clip.get('id') if clip else None,started=time.monotonic(),serial=self.launch_serial)
  catalog=copy.deepcopy(self.catalog)
  catalog['targets']=[t for t in catalog['targets'] if not (t.get('scope')=='clip' and t.get('layer')==li)]
  next(l for l in catalog['layers'] if l['i']==li)['active']=0
  self.reconcile(catalog,launching=True)
  return layer['id'],self.launch_serial
 @property
 def epoch(self):return self.catalog['epoch']+':'+str(self.revision)
 def disarm(self):
  self.session.cancel()
  self.armed=False;self.performance.cancel();self.play_actions.release();self.control_owner.clear();self.envelopes.clear();self.pending_hits.clear();self.rack_returns.clear();self.owned.clear();self.lastout.clear()
  for sl in self.slots.values():sl.drive=False
 def claim(self,pid,owner=None):
  if owner is None:self.control_serial+=1;owner='direct:'+str(self.control_serial)
  if self.rack_returns.get(pid,{}).get('owner')!=owner:self.rack_returns.pop(pid,None)
  self.control_owner[pid]=owner;return owner
 def drive(self,pid,on,owner=None):
  if pid not in self.slots:raise ValueError('Numeric parameter unavailable')
  now=time.perf_counter();sl=self.slots[pid];target,p=self.params[pid]
  t=next(t for t in self.catalog['targets'] if t['id']==target)
  if on and not self.drive_ready(p):raise ValueError('Set Timeline and pause it in Resolume to prepare this drive')
  if on and t.get('native_phase_clip') and t['kind']=='source' and not p.get('native_phase'):raise ValueError('Set a paused Timeline in Resolume to prepare this drive')
  self.claim(pid,owner);self.envelopes.pop(pid,None)
  if on:
   if not sl.drive:
    # Start from the current native position, including direct Resolume edits.
    native=self.observed.get(pid,(self.current_value(pid),0))[0]
    sl.cfg['manual']=self.native_position(p,native) if p.get('native_phase') else finite((native-p['min'])/(p['max']-p['min']),0,1)
    sl.drive=False;sl.retarget(self.groups[target],now);sl.prev=sl.target
   sl.drive=True;self.owned.add(pid)
  else:
   current=self.current_value(pid)
   sl.cfg['manual']=sl.value(sl.blend(now)) if p.get('native_phase') else finite((current-p['min'])/(p['max']-p['min']),0,1);sl.drive=False
  sl.dur=.15;sl.retarget(self.groups[target],now)
 def drive_all(self,data):
  if data.get('epoch')!=self.catalog['epoch']:raise ValueError('Composition changed; choose a current target')
  target=next((t for t in self.catalog['targets'] if t['id']==data.get('target')),None)
  if not target or target.get('stage') or target.get('scope')=='stage':raise ValueError('Drive target unavailable')
  slots=[(p['id'],self.slots[p['id']]) for p in target['params'] if p['id'] in self.slots and self.drive_ready(p) and not self.slots[p['id']].cfg.get('lock') and self.slots[p['id']].cfg['lo']<self.slots[p['id']].cfg['hi'] and (not target.get('native_phase_clip') or p.get('native_phase'))]
  if not slots:return
  on=data.get('on',not all(sl.drive for pid,sl in slots))
  if not isinstance(on,bool):raise ValueError('Drive all requires on or off')
  for pid,sl in slots:
   if sl.drive!=on:self.drive(pid,on)
 def parameter_lock(self,data):
  pid=int(data['id'])
  if data.get('epoch')!=self.catalog['epoch'] or pid not in self.slots:raise ValueError('Parameter changed; refresh its controls')
  if not isinstance(data['on'],bool):raise ValueError('Lock requires on or off')
  self.slots[pid].cfg['lock']=data['on']
 def set_hold(self,on=None,owner=None):
  if owner is None:self.control_serial+=1;owner='direct:'+str(self.control_serial)
  self.global_owner['hold']=owner;self.hold=not self.hold if on is None else bool(on)
 def current_value(self,pid):
  p=self.params[pid][1]
  return self.lastout.get(pid,p['value']) if pid in self.owned else p['value']
 def native_values(self,epoch,values):
  if epoch!=self.epoch:return
  now=time.perf_counter()
  for pid,value in values:
   if pid==self.catalog.get('tempo',{}).get('tempo',{}).get('id'):
    if isinstance(value,(int,float)):self.bpm=finite(value,20,500)
    continue
   if pid not in self.params:continue
   p=self.params[pid][1]
   if p['type'] in NUM and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)):continue
   self.observed[pid]=(value,now)
   if pid not in self.owned and pid not in self.switches:p['value']=value
 def manual(self,pid,value,owner=None,duration=.025):
  if pid not in self.params:raise ValueError('Target no longer exists')
  target,p=self.params[pid];kind=p['type']
  if kind in NUM:
   v=finite(value,p['min'],p['max']);self.claim(pid,owner);self.observed.pop(pid,None);self.envelopes.pop(pid,None);sl=self.slots[pid];sl.drive=False;sl.cfg['manual']=self.native_position(p,v) if p.get('native_phase') else (v-p['min'])/(p['max']-p['min']);sl.dur=duration;sl.retarget(self.groups[target],time.perf_counter());self.owned.add(pid);return None
  if kind=='ParamColor':
   if not isinstance(value,str) or len(value) not in (7,9) or value[0]!='#' or any(c not in '0123456789abcdefABCDEF' for c in value[1:]):raise ValueError('Expected hex color')
   value=value.lower()
   if len(value)==7:value+=str(p['value'])[7:9] if isinstance(p['value'],str) and len(p['value'])==9 else 'ff'
  elif kind=='ParamChoice':
   if value not in p['options']:raise ValueError('Unknown choice')
  elif not isinstance(value,bool):raise ValueError('Expected on/off')
  self.claim(pid,owner)
  if kind not in ('ParamEvent','ParamTrigger'):
   self.switch_serial+=1;self.switches[pid]=dict(value=value,pending=True,serial=self.switch_serial,until=time.monotonic()+3);p['value']=value
  return value
 def confirm_switch(self,pid,serial,value,error=''):
  sw=self.switches.get(pid)
  if not sw or sw['serial']!=serial:return
  sw.update(value=value,pending=False,until=time.monotonic()+2)
  if pid in self.params:self.params[pid][1]['value']=value
  if error:self.error=error
 def gesture(self,target,action,mode='harmonic',owner=None):
  if action=='hold':self.set_hold(owner=owner);return
  if target not in self.groups:raise ValueError('Select a current target')
  now=time.perf_counter();g=self.groups[target]
  kind=next(t['kind'] for t in self.catalog['targets'] if t['id']==target)
  if action not in ('open','settle','shuffle'):raise ValueError('Unknown action')
  if action=='shuffle':self.shuffle_drives([target],mode);return
  for pid,sl in self.slots.items():
   if self.params[pid][0]!=target or sl.cfg.get('lock'):continue
   if not self.drive_ready(self.params[pid][1]):continue
   if any(t['id']==target and t.get('native_phase_clip') for t in self.catalog['targets']) and not self.params[pid][1].get('native_phase'):continue
   if action=='open' and kind in ('effect','layer','clip','composition') and self.params[pid][1]['name'] in ('Opacity','Level'):continue
   self.claim(pid,owner)
   if action=='open':sl.drive=True;self.owned.add(pid);g['depth']=1.
   elif action=='settle':
    sl.cfg['manual']=0. if kind=='effect' and self.params[pid][1]['name']=='Opacity' else sl.value(sl.blend(now));sl.drive=False
    if kind=='effect' and self.params[pid][1]['name']=='Opacity':self.owned.add(pid)
   if action in ('open','settle'):self.envelopes.pop(pid,None)
   sl.dur=.2;sl.retarget(g,now)
 def shuffle_drives(self,targets,mode='harmonic'):
  now=time.perf_counter()
  for target in targets:
   slots=[sl for pid,sl in self.slots.items() if self.params[pid][0]==target and sl.drive and pid in self.owned and not sl.cfg.get('lock')]
   if not slots:continue
   g=self.groups[target];order=[sl.cfg.get('family_slot',sl.index) for sl in slots];random.shuffle(order);phase=random.random()
   ratios=['1:1'] if mode=='unison' else [r for r in RATIO_LIB if r.startswith('1/')==(mode=='irrational')]
   for sl,index in zip(slots,order):
    if g['pattern']==0:sl.cfg['ratio']=random.choice(ratios)
    else:sl.cfg['family_slot']=index
    sl.cfg['offset']=phase if g['pattern']==1 or (g['pattern']==0 and mode=='unison') else random.random()
    sl.dur=.3;sl.retarget(g,now)
 def bank_targets(self):
  return [t for t in self.catalog['targets'] if t['kind'] in ('source','effect') and not t.get('stage') and t.get('scope')!='stage' and any(p['id'] in self.slots for p in t['params'])]
 def drive_bank_action(self,data):
  if data.get('epoch')!=self.catalog['epoch']:raise ValueError('Composition changed; refresh the Drive bank')
  action=data.get('action')
  if action not in ('shuffle','family','rate','drive'):raise ValueError('Unknown Drive bank action')
  if 'layer_id' in data:
   lid=int(data['layer_id'])
   if not any(l['id']==lid and not l.get('stage') for l in self.catalog['layers']):raise ValueError('Layer unavailable')
   targets=[t['id'] for t in self.bank_targets() if t.get('layer_id')==lid]
  else:
   targets=[t['id'] for t in self.bank_targets() if t['id']==data.get('target')]
   if not targets:raise ValueError('Drive target unavailable')
  if action=='drive':
   for target in targets:self.drive_all(dict(data,target=target))
  elif action=='shuffle':self.shuffle_drives(targets)
  elif action=='family':
   pattern=finite(data['pattern'],0,len(FAMILIES)-1)
   if pattern!=int(pattern):raise ValueError('Choose a relationship family')
   for target in targets:self.relationship(target,dict(pattern=int(pattern),seconds=.3))
  else:
   rate=finite(data['rate'],.03125,16)
   for target in targets:self.settings(target,dict(rate=rate))
 def settings(self,target,data):
  if target not in self.groups:raise ValueError('Select a current target')
  if self.catalog.get('native_phase_mode') and ('lo' in data or 'hi' in data):raise ValueError('Edit In/Out in Resolume')
  if any(t['id']==target and t.get('native_phase_clip') for t in self.catalog['targets']) and ('lo' in data or 'hi' in data):raise ValueError('Edit this clip’s ranges in Resolume')
  g=self.groups[target];ranges=[]
  for pid,sl in self.slots.items():
   if self.params[pid][0]!=target:continue
   lo=finite(data.get('lo',sl.cfg['lo']),0,1);hi=finite(data.get('hi',sl.cfg['hi']),0,1)
   if lo>hi:raise ValueError('Low must not exceed High')
   ranges.append((sl,lo,hi))
  amount=finite(data.get('amount',g['depth']),0,1);rate=finite(data.get('rate',g['speed']),.03125,16)
  g.update(depth=amount,speed=rate)
  for sl,lo,hi in ranges:
   sl.cfg.update(lo=lo,hi=hi)
   if 'lo' in data or 'hi' in data:sl.cfg['range_authored']=True
   sl.dur=.15;sl.retarget(g,time.perf_counter())
 def relationship(self,target,data):
  if target not in self.groups:raise ValueError('Select a current target')
  update={}
  for name,lo,hi in [('pattern',0,len(FAMILIES)-1),('spread',0,16),('seed',0,127),('fm',0,4)]:
   if name in data:
    v=finite(data[name],lo,hi)
    if name!='fm' and v!=int(v):raise ValueError('Relationship steps must be whole numbers')
    update[name]=v if name=='fm' else int(v)
  seconds=finite(data.get('seconds',.3),0,10)
  self.groups[target].update(update)
  if 'pattern' in update:self.groups[target].pop('relationship',None)
  for pid,sl in self.slots.items():
   if self.params[pid][0]==target:sl.dur=seconds;sl.retarget(self.groups[target],time.perf_counter())
 def parameter_motion(self,pid,data):
  if pid not in self.slots:raise ValueError('Choose a numeric parameter')
  update={}
  if 'ratio' in data:
   if data['ratio'] not in RATIO_LIB:raise ValueError('Unknown ratio')
   update['ratio']=data['ratio']
  if 'mult' in data:
   value=finite(data['mult'],-16,16)
   if 0<abs(value)<.001:raise ValueError('Use zero or a multiplier magnitude of at least 0.001')
   update['mult']=value
  for name in ('offset','shape'):
   if name in data:update[name]=finite(data[name],0,1)
  sl=self.slots[pid];sl.cfg.update(update);sl.dur=finite(data.get('seconds',.3),0,10);sl.retarget(self.groups[self.params[pid][0]],time.perf_counter())
 def home_key(self,target):return self.catalog['epoch']+'|'+target
 def set_home(self,target):
  if target not in self.groups:raise ValueError('Select a current target')
  now=time.perf_counter();saved={}
  for pid,(owner,p) in self.params.items():
   if owner!=target or p['type'] in ('ParamEvent','ParamTrigger'):continue
   sl=self.slots.get(pid);value=self.lastout.get(pid,p['value']) if pid in self.owned else p['value']
   if sl and pid in self.owned and not sl.drive:value=(p.get('in',p['min'])+sl.cfg['manual']*(p.get('out',p['max'])-p.get('in',p['min']))) if p.get('native_phase') else p['min']+sl.cfg['manual']*(p['max']-p['min'])
   row=dict(type=p['type'],min=p['min'],max=p['max'],value=value,phase_mode=bool(p.get('native_phase')))
   if sl:row.update(cfg=copy.deepcopy(sl.cfg),drive=sl.drive,phi=sl.phi)
   saved[str(pid)]=row
  self.homes[self.home_key(target)]=dict(group=copy.deepcopy(self.groups[target]),params=saved)
 def return_home(self,target,owner=None):
  home=self.homes.get(self.home_key(target))
  if not home:raise ValueError('Set Home for this target first')
  for key,row in home['params'].items():
   current=self.params.get(int(key))
   if not current or current[0]!=target or any(current[1][k]!=row[k] for k in ('type','min','max')):raise ValueError('Parameters changed. Set a new Home for this target.')
   if bool(current[1].get('native_phase'))!=row.get('phase_mode',False):raise ValueError('Animation mode changed. Set a new Home for this target.')
  self.groups[target]=copy.deepcopy(home['group']);now=time.perf_counter();discrete=[]
  for key,row in home['params'].items():
   pid=int(key);self.claim(pid,owner);self.envelopes.pop(pid,None);sl=self.slots.get(pid)
   if sl:
    sl.cfg=copy.deepcopy(row['cfg']);p=self.params[pid][1];sl.drive=row['drive'] and self.drive_ready(p)
    if p.get('native_phase'):sl.cfg.update(lo=0.,hi=1.,range_authored=False)
    elif not sl.drive:sl.cfg['manual']=(row['value']-row['min'])/(row['max']-row['min'])
    sl.dur=.3;sl.retarget(self.groups[target],now);self.owned.add(pid)
   else:discrete.append((pid,row['value']));self.params[pid][1]['value']=row['value']
  return discrete
 def param_range(self,pid,lo,hi):
  if self.catalog.get('native_phase_mode'):raise ValueError('Edit In/Out in Resolume')
  if self.params[pid][1].get('native_phase'):raise ValueError('Edit In/Out in Resolume')
  lo=finite(lo,0,1);hi=finite(hi,0,1)
  if lo>hi:raise ValueError('Low must not exceed High')
  sl=self.slots[pid];sl.cfg.update(lo=lo,hi=hi,range_authored=True);sl.dur=.1;sl.retarget(self.groups[self.params[pid][0]],time.perf_counter())
 def envelope_config(self,pid,data):
  target,p=self.params[pid]
  if p['type'] not in NUM or p['name']!='Opacity' or not any(t['id']==target and t['kind']=='effect' for t in self.catalog['targets']):raise ValueError('Choose an effect opacity')
  cfg=dict(self.envelope_settings.get(pid,dict(in_time=1.,out_time=1.,curve='smooth',low=p['min'],high=p['max'])))
  for key in ('in_time','out_time','low','high'):
   if key in data:cfg[key]=finite(data[key],.01 if key.endswith('_time') else p['min'],120 if key.endswith('_time') else p['max'])
  if 'curve' in data:cfg['curve']=data['curve']
  if cfg['curve'] not in ('linear','smooth','ease-in','ease-out'):raise ValueError('Unknown envelope curve')
  if cfg['low']>=cfg['high']:raise ValueError('Envelope low must be below high')
  self.envelope_settings[pid]=cfg;return cfg
 def envelope(self,pid,direction,owner=None):
  if direction not in ('in','out'):raise ValueError('Choose IN or OUT')
  cfg=self.envelope_config(pid,{})
  self.claim(pid,owner)
  old=self.envelopes.get(pid);p=self.params[pid][1]
  current=self.lastout.get(pid,p['value']) if pid in self.owned else p['value']
  start=cfg['low'] if direction=='in' else cfg['high']
  end=cfg['high'] if direction=='in' else cfg['low']
  if not old or old['direction']!=direction:start=current
  duration=cfg[direction+'_time']*abs(end-start)/(cfg['high']-cfg['low'])
  self.envelopes[pid]=dict(direction=direction,start=start,end=end,elapsed=0.,duration=duration,curve=cfg['curve'],progress=0.)
  self.slots[pid].drive=False;self.owned.add(pid)
 def effect_pulse(self,pid,amount,seconds,owner=None,key='',end=0.):
  self.envelope_config(pid,{})
  amount=finite(amount,0,1);seconds=finite(seconds,.05,4)
  self.manual(pid,amount,owner=owner,duration=0)
  self.envelopes[pid]=dict(direction='pulse',start=amount,end=finite(end,0,1),elapsed=0.,duration=seconds,curve='smooth',progress=0.,rack_key=key)
 def rack_pulse_baseline(self,binding):
  pid=binding['opacity'];previous=self.rack_returns.get(pid)
  if previous and self.control_owner.get(pid)==previous['owner']:return copy.deepcopy(previous)
  sl=self.slots[pid];p=self.params[pid][1]
  value=self.current_value(pid) if pid in self.owned else self.rack_value(pid)
  if pid in self.owned and not sl.drive:value=p['min']+sl.cfg['manual']*(p['max']-p['min'])
  return dict(value=value,bypass=bool(self.rack_value(binding['bypass'])),bypass_id=binding['bypass'],contract=copy.deepcopy(self.contracts[pid]),bypass_contract=copy.deepcopy(self.contracts[binding['bypass']]))
 def rack_value(self,pid):
  return self.current_value(pid) if self.switches.get(pid,{}).get('pending') else self.observed.get(pid,(self.current_value(pid),0))[0]
 def rack_plan(self,data):
  if data.get('epoch')!=self.catalog['epoch']:raise ValueError('Composition changed; refresh the rack')
  row=next((r for r in self.catalog.get('effect_rack',{}).get('rows',[]) if r['id']==data.get('row')),None)
  if not row:raise ValueError('Rack row unavailable')
  for bindings in ([row['color']] if row['color'] else [])+[p['bindings'] for p in row['pads']]:hit_bindings(self,dict(epoch=self.catalog['epoch'],bindings=bindings))
  for c in row.get('controls',[]):self.session.control(row['id'],c['id'])
  action=data.get('action');values=[];events=[]
  def write(pad,on):
   if pad.get('mode')=='pulse':
    for b in pad['bindings']:values.append((b['opacity'],0.))
   elif pad.get('mode')=='latch':
    for b in pad['bindings']:values.extend([(b['opacity'],1.),(b['bypass'],False),(b['latch'],on)])
   elif pad.get('mode')=='toggle':
    for b in pad['bindings']:
     pid=b['opacity'];previous=self.rack_returns.get(pid);level=previous['value'] if previous else self.rack_value(pid)
     if level>0:self.rack_levels[pid]=level
     if on and level<=0:level=self.rack_levels.get(pid,1.);values.append((pid,level))
     elif previous:values.append((pid,level))
     values.append((b['bypass'],not on))
   else:
    for b in pad['bindings']:values.extend([(b['opacity'],1.),(b['bypass'],not on)])
  if action=='clear':
   for pad in row['pads']:
    if pad.get('clear',True):write(pad,False)
   for b in row['color']:values.append((b['opacity'],0.))
  else:
   pad=next((p for p in row['pads'] if p['id']==data.get('pad')),None)
   if not pad:raise ValueError('Rack control unavailable')
   if action=='opacity':
    amount=finite(data['amount'],0,1)
    for b in pad['bindings']:
     level=self.rack_returns.get(b['opacity'],{}).get('value',self.rack_value(b['opacity']))
     if level>0:self.rack_levels[b['opacity']]=level
     if amount>0:self.rack_levels[b['opacity']]=amount
     values.append((b['opacity'],amount))
   elif action=='trigger' and pad.get('mode')=='trigger':
    if not all(not self.rack_value(b['bypass']) and self.rack_value(b['opacity'])>0 for b in pad['bindings']):raise ValueError('Turn LUT on before Decon')
    events=[b['event'] for b in pad['bindings']]
   elif action==('latch' if pad.get('mode')=='latch' else 'enable'):
    if type(data.get('on')) is not bool:raise ValueError('Choose On or Off')
    write(pad,data['on'])
   else:raise ValueError('Rack action unavailable')
  return values,events
 def rack_state(self):
  result={}
  for row in self.catalog.get('effect_rack',{}).get('rows',[]):
   ready=True
   try:
    if row['color']:hit_bindings(self,dict(epoch=self.catalog['epoch'],bindings=row['color']))
    for pad in row['pads']:hit_bindings(self,dict(epoch=self.catalog['epoch'],bindings=pad['bindings']))
    for c in row.get('controls',[]):self.session.control(row['id'],c['id'])
   except (ValueError,KeyError):ready=False
   levels=[self.observed.get(b['opacity'],(self.rack_value(b['opacity']),0))[0] for b in row['color']] if ready else []
   active={pad['id']:any(self.envelopes.get(b['opacity'],{}).get('rack_key')==row['id']+':'+pad['id'] and self.envelopes[b['opacity']]['progress']<1 for b in pad['bindings']) for pad in row['pads']}
   enabled={};latched={};pad_levels={}
   if ready:
    for pad in row['pads']:
     amounts=[self.rack_value(b['opacity']) for b in pad['bindings']];pad_levels[pad['id']]=dict(value=amounts[0],mixed=max(amounts)-min(amounts)>.02)
     for b,amount in zip(pad['bindings'],amounts):
      if amount>0 and b['opacity'] not in self.rack_returns:self.rack_levels[b['opacity']]=amount
     enabled[pad['id']]=all(not self.rack_value(b['bypass']) and self.rack_value(b['opacity'])>0 for b in pad['bindings'])
     if pad.get('mode')=='latch':latched[pad['id']]=all(bool(self.rack_value(b['latch'])) for b in pad['bindings']);active[pad['id']]=latched[pad['id']]
     elif pad.get('mode')=='trigger':active[pad['id']]=self.rack_flash.get((row['id'],pad['id']),0)>time.monotonic()
   controls={c['id']:dict(value=self.rack_value(c['bindings'][0]['parameter']),mixed=len({round(float(self.rack_value(b['parameter'])),4) if b['type'] in NUM else self.rack_value(b['parameter']) for b in c['bindings']})>1) for c in row.get('controls',[])} if ready else {}
   result[row['id']]=dict(controls=controls,levels=pad_levels,ready=ready,color=levels[0] if levels else 0,mixed=bool(levels and max(levels)-min(levels)>.02),active=active,enabled=enabled,latched=latched)
  return result
 def envelope_value(self,pid,dt,now):
  env=self.envelopes[pid];env['elapsed']+=max(0,dt)
  u=min(1.,env['elapsed']/env['duration']) if env['duration'] else 1.
  env['progress']=u
  curve=env['curve'];shaped=u*u*(3-2*u) if curve=='smooth' else u*u if curve=='ease-in' else 1-(1-u)**2 if curve=='ease-out' else u
  value=env['start']+(env['end']-env['start'])*shaped
  sl=self.slots[pid];target,p=self.params[pid];sl.cfg['manual']=(value-p['min'])/(p['max']-p['min']);sl.dur=0;sl.retarget(self.groups[target],now)
  return value
 def tick(self,dt,now):
  start=time.perf_counter();out=[]
  if self.armed and self.connected:
   self.performance.tick(dt)
   for pid in tuple(self.owned):
    if pid not in self.slots:continue
    sl=self.slots[pid];target,p=self.params[pid]
    if self.hold and self.envelopes.get(pid,{}).get('direction')!='pulse':continue
    if pid in self.envelopes:v=self.envelope_value(pid,dt,now)
    else:
     e=sl.step(min(dt,.05)*self.bpm/60/32*self.rate_scale.get(pid,1),now);e=dict(e,depth=e['depth']*self.intensity_scale.get(pid,1));v=max(0,min(1,sl.value(e)))
     if p.get('native_phase'):
      if pid not in self.lastout or abs(v-getattr(sl,'sent_phase',float('inf')))>1e-7:
       out.append((pid,{'phase':v}));sl.sent_phase=v;self.lastout[pid]=p.get('in',p['min'])+v*(p.get('out',p['max'])-p.get('in',p['min']))
      continue
     v=p['min']+v*(p['max']-p['min'])
    if p['type'] in ('ParamInt','ParamNumber'):v=round(v)
    endpoint=pid in self.envelopes and self.envelopes[pid]['progress']==1 and self.lastout.get(pid)!=v
    if endpoint or abs(v-self.lastout.get(pid,float('inf')))>1e-7:out.append((pid,v));self.lastout[pid]=v
  self.work.append((time.perf_counter()-start)*1000);self.gaps.append(dt*1000);return out
 def observation_ids(self,watches,native_watches):
  priority={b[k] for row in self.catalog.get('effect_rack',{}).get('rows',[]) for b in row['color']+[b for pad in row['pads'] for b in pad['bindings']] for k in ('opacity','bypass','latch') if k in b}
  priority.update(p['id'] for t in self.catalog['targets'] if (t['kind']=='layer' and not t.get('stage')) or t['kind']=='crossfader' for p in t['params'] if p['name'].lower() in ('level','hidden','phase'))
  priority.update(b['parameter'] for row in self.catalog.get('effect_rack',{}).get('rows',[]) for control in row.get('controls',[]) for b in control['bindings'])
  requested={pid for pid,(target,p) in self.params.items() if target==self.selected}
  for client,targets in watches.items():
   subset=native_watches.get(client)
   requested.update(pid for pid,(target,p) in self.params.items() if target in targets and (subset is None or pid in subset))
  return tuple(sorted((requested|priority)&self.params.keys(),key=lambda pid:(pid not in priority,self.params[pid][0]!=self.selected,pid)))
 def state(self):
  values={};now=time.perf_counter()
  for pid,(target,p) in self.params.items():
   if target!=self.selected and target not in self.watched:continue
   sl=self.slots.get(pid);v=self.lastout.get(pid,p['value']) if pid in self.owned else p['value']
   if pid in self.observed and not self.switches.get(pid,{}).get('pending'):v=self.observed[pid][0]
   motion=dict({k:sl.cfg[k] for k in ('ratio','mult','offset','shape')},cycles_per_beat=sl.blend(now)['x']*self.rate_scale.get(pid,1)/32) if sl else None
   values[pid]={'envelope':self.envelopes.get(pid),'envelope_config':self.envelope_settings.get(pid),'value':v,'pending':self.switches.get(pid,{}).get('pending',False),'drive':bool(sl and sl.drive),'locked':bool(sl and sl.cfg.get('lock')),'lo':sl.cfg['lo'] if sl else 0,'hi':sl.cfg['hi'] if sl else 1,'rate':self.groups.get(target,{}).get('speed',1),'owned':pid in self.owned,'owner':'Heart' if pid in self.owned else 'Native','rate_scale':self.rate_scale.get(pid,1),'intensity_scale':self.intensity_scale.get(pid,1),'motion':motion}
   if p.get('native_phase') or self.catalog.get('native_phase_mode'):
    values[pid]['lo'],values[pid]['hi']=native_drive_range(p);values[pid]['native_phase']=bool(p.get('native_phase'))
  percentile=lambda a:round(sorted(a)[int((len(a)-1)*.95)],2) if a else 0
  counts={}
  for pid in self.owned:
   if pid in self.slots and self.slots[pid].drive:
    target=self.params[pid][0];counts[target]=counts.get(target,0)+1
  bank={t['id']:dict(count=counts.get(t['id'],0),pattern=self.groups[t['id']]['pattern'],rate=self.groups[t['id']]['speed']) for t in self.bank_targets()}
  for target in self.bank_targets():
   slots=[self.slots[p['id']] for p in target['params'] if p['id'] in self.slots and self.drive_ready(p) and not self.slots[p['id']].cfg.get('lock') and self.slots[p['id']].cfg['lo']<self.slots[p['id']].cfg['hi'] and (not target.get('native_phase_clip') or p.get('native_phase'))]
   bank[target['id']].update(eligible=len(slots),active=sum(sl.drive for sl in slots))
  originals={str(t['clip_id']):dict(busy=t['clip_id'] in self.authored.busy,rate=self.authored.rates.get(str(t['clip_id']),1)) for t in self.catalog['targets'] if t.get('authored')}
  return dict(type='state',session=self.session.state(),authored=originals,effect_rack=self.rack_state(),capabilities=['envelopes','surface_reload','performance_layouts','playing','color','group_levels','drive_bank','drive_all','effect_hits','authored_clips','rack_controls','tap_tempo','rack_sequence','scoped_recovery','crossfader','scoped_readback'],drive_bank=bank,performance=self.performance.state(),homes=[t for t in self.groups if self.home_key(t) in self.homes],home=self.home_key(self.selected) in self.homes,group=self.groups.get(self.selected,{}),groups={k:v for k,v in self.groups.items() if k==self.selected or k in self.watched},connected=self.connected,armed=self.armed,hold=self.hold,bpm=self.bpm,values=values,error=self.error,selected=self.selected,metrics=dict(tick_p95_ms=percentile(self.gaps),work_p95_ms=percentile(self.work),scan_ms=round(self.scan_ms),bridge_work_ms=self.bridgework,sent=self.sent,owned=len(self.owned)))

async def main():
 if (ROOT/'api-paused.json').exists():
  print('Heart API paused after Resolume memory incident; inspect api-paused.json before reconnecting.',flush=True);return
 e=Engine()
 e.performance=Performance(e,ROOT/'layouts.json')
 try:e.library=json.loads((ROOT/'clip-library.json').read_text())
 except (OSError,ValueError):pass
 try:e.rack_config=json.loads((ROOT/'effect-rack.json').read_text())
 except (OSError,ValueError):pass
 try:e.homes=json.loads((ROOT/'homes.json').read_text())
 except (OSError,ValueError):pass
 try:e.session.preferences=json.loads((ROOT/'session-settings.json').read_text())
 except (OSError,ValueError):pass
 try:e.session.returns=json.loads((ROOT/'recovery.json').read_text())
 except (OSError,ValueError):pass
 rpc_pending={};rpc_serial=0;sequence_tasks={}
 reload_until=0.
 clients=set();watches={};native_watches={};rescan=asyncio.Event();full_scan=True;bridge=await asyncio.create_subprocess_exec(sys.executable,str(ROOT/'bridge.py'),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
 async def send(m):bridge.stdin.write((json.dumps(m,separators=(',',':'))+'\n').encode());await bridge.stdin.drain()
 observation=None
 async def observe():
  nonlocal observation
  ids=e.observation_ids(watches,native_watches)
  tempo=e.catalog.get('tempo',{}).get('tempo',{}).get('id');ids=((tempo,)+ids) if tempo else ids;key=(e.epoch,ids)
  if key==observation:return
  observation=key;e.observed={pid:v for pid,v in e.observed.items() if pid in ids}
  await send(dict(cmd='observe',epoch=e.epoch,ids=ids))
 async def animation_rpc(m):
  nonlocal rpc_serial
  rpc_serial+=1;key=rpc_serial;future=asyncio.get_running_loop().create_future();rpc_pending[key]=future
  try:
   await send(dict(m,rpc=key));return await asyncio.wait_for(future,15)
  finally:rpc_pending.pop(key,None)
 async def broadcast(m):
  message=json.dumps(m,separators=(',',':'))
  for ws in list(clients):
   try:await asyncio.wait_for(ws.send(message),.15)
   except Exception:clients.discard(ws)
 async def bridge_read():
  nonlocal full_scan
  while line:=await bridge.stdout.readline():
   m=json.loads(line)
   if 'rpc' in m:
    future=rpc_pending.get(m['rpc'])
    if future and not future.done():
     if 'error' in m:future.set_exception(ValueError(m['error']))
     else:future.set_result(m['data'])
    continue
   if 'connected' in m:
    e.connected=m['connected']
    if not e.connected:e.disarm();e.observed.clear()
   if 'native_values' in m:e.native_values(m.get('native_epoch'),m['native_values'])
   if 'error' in m:e.error=m['error']
   for pid in m.get('phase_stopped',[]):
    if pid in e.slots:e.slots[pid].drive=False;e.owned.discard(pid);e.lastout.pop(pid,None)
   if m.get('refresh'):full_scan=True;rescan.set()
   e.sent+=m.get('sent',0);e.bridgework=m.get('work_ms',e.bridgework)
  e.connected=False;e.disarm();e.error='Output worker stopped; restart v2'
 async def scan():
  nonlocal full_scan
  while True:
   if (ROOT/'api-paused.json').exists():await asyncio.sleep(2);continue
   rescan.clear();t=time.perf_counter();launch_serial=e.launch_serial;child=None;full=full_scan or not e.catalog['targets'];full_scan=False
   try:
    snapshot=copy.deepcopy(e.catalog);snapshot['_phase_priority']=[pid for pid,(target,p) in e.params.items() if target==e.selected]
    child=await asyncio.create_subprocess_exec(sys.executable,str(ROOT/'scan.py'),*(('--previous',) if full else ('--active',)),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    raw,err=await asyncio.wait_for(child.communicate(json.dumps(snapshot).encode()),16)
    if child.returncode:raise RuntimeError(err.decode()[-250:])
    if launch_serial!=e.launch_serial:rescan.set();continue
    catalog=json.loads(raw);e.scan_ms=(time.perf_counter()-t)*1000
    checked={p['id']:p for target in catalog.get('targets',[]) for p in target['params']}
    for pid,(_,p) in e.params.items():
     if pid in checked and '_phase_checked' in checked[pid]:p['_phase_checked']=checked[pid]['_phase_checked']
    if catalog.get('needs_full'):full_scan=True;continue
    if catalog.pop('_changed',True) or e.launches:
     changed=e.reconcile(catalog,scan_started=t)
     if changed:await send(e.binding())
     await start_clips()
     await observe()
     await broadcast(e.catalog)
   except Exception as ex:e.error='Discovery: '+str(ex)
   finally:
    if child is not None and child.returncode is None:
     child.kill();await child.wait()
   try:await asyncio.wait_for(rescan.wait(),1)
   except TimeoutError:pass
 async def sequence_fire(d):
  key=d['row']
  try:
   if e.session.valid(d):await execute(d)
  except Exception as ex:
   if e.session.valid(d):e.session.stop(key);e.error=str(ex)
  finally:sequence_tasks.pop(key,None)
 async def tick():
  previous=time.perf_counter();deadline=previous
  while True:
   now=time.perf_counter();dt=now-previous;values=e.tick(dt,now);previous=now
   if e.armed and e.connected:
    for d in e.session.due(dt):
     if d['row'] not in sequence_tasks:sequence_tasks[d['row']]=asyncio.create_task(sequence_fire(d))
     else:e.session.loop(d['row'])['skipped']+=1
   if values:await send(dict(cmd='values',epoch=e.epoch,values=values))
   if not e.session.busy:
    for pid,record in list(e.rack_returns.items()):
     if e.envelopes.get(pid,{}).get('progress')==1 and not record.get('finishing'):
      record['finishing']=True;e.pending_hits[pid]=record['owner'];e.session.inflight+=1
      asyncio.create_task(restore_rack_pulse(pid,record))
   deadline+=1/120
   await asyncio.sleep(max(0,deadline-time.perf_counter()))
   if time.perf_counter()-deadline>.05:deadline=time.perf_counter()
 async def publish():
  while True:await broadcast(e.state());await asyncio.sleep(.1)
 async def surface_updates():
  previous=None;stamp=None
  while True:
   if (ROOT/'api-paused.json').exists():
    e.disarm();e.connected=False
    if bridge.returncode is None:
     bridge.terminate();await bridge.wait()
    e.error='Heart traffic paused by memory guard; check Resolume memory before restarting Heart'
   try:
    current=tuple((p.stat().st_mtime_ns,p.stat().st_size,p.stat().st_ino) for p in (ROOT/n for n in ('index.html','controllers.js','performance_surface.js','performance.css','playing.js','playing.css')) if p.exists())
    if current!=stamp:
     _,revision=surface_document();stamp=current
     if revision!=previous:await broadcast(dict(type='surface_version',version=revision));previous=revision
   except OSError:pass
   await asyncio.sleep(2)

 async def confirm_switch(pid,serial,expected):
  deadline=time.monotonic()+1.5;actual=expected
  def read():
   with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}',timeout=1) as response:return json.load(response)['value']
  try:
   while time.monotonic()<deadline:
    await asyncio.sleep(.04)
    sw=e.switches.get(pid)
    if not sw or sw['serial']!=serial:return
    actual=await asyncio.to_thread(read)
    if actual==expected:e.confirm_switch(pid,serial,actual);return
   e.confirm_switch(pid,serial,actual,'Resolume did not confirm the switch; showing its actual value')
  except Exception as ex:e.confirm_switch(pid,serial,actual,'Switch confirmation unavailable: '+str(ex))
 async def apply_authored(d):
  if d.get('epoch')!=e.catalog['epoch']:raise ValueError('Composition changed; choose the current clip')
  cid=int(d['clip_id']);e.authored.targets(e.catalog,cid)
  targets=[t['id'] for t in e.catalog['targets'] if t.get('clip_id')==cid and t.get('authored') and t['kind'] in ('source','effect')]
  action=d['action']
  if action=='original':
   values=e.reset_clip(cid)
   if values:await send(dict(cmd='values',epoch=e.epoch,values=values))
  elif action=='shuffle':e.shuffle_drives(targets)
  elif action=='rate':
   for target in targets:e.settings(target,dict(rate=d['rate']))
  else:raise ValueError('Choose Reset, Shuffle or Rate')

 async def start_clips():
  if not e.armed or not e.connected:return
  e.start_prepared()
  for cid in tuple(e.clip_starts):
   e.clip_starts.discard(cid)
   if e.phase_clip(cid):e.start_phases(cid);continue
   e.authored.busy.add(cid)
   try:await apply_authored(dict(epoch=e.catalog['epoch'],clip_id=cid,action='original'))
   finally:e.authored.busy.discard(cid)

 async def restore_rack_pulse(pid,record):
  owner=record['owner'];bypass=record['bypass_id']
  def current():return e.armed and e.connected and e.control_owner.get(pid)==owner and e.control_owner.get(bypass)==owner and e.contracts.get(pid)==record['contract'] and e.contracts.get(bypass)==record['bypass_contract']
  try:
   # Bypass first keeps an originally hidden effect hidden when its native
   # opacity is restored. All writes remain owned by this particular hit.
   for target,value in [(bypass,record['bypass']),(pid,record['value'])]:
    if not current():return
    await animation_rpc(dict(cmd='request',parameter=target,path=f'/parameter/by-id/{target}',method='PUT',value={'value':value}))
    if not current():return
    e.manual(target,value,owner=owner,duration=0);e.observed.pop(target,None)
    if target in e.slots:e.lastout[target]=value
    else:e.confirm_switch(target,e.switches[target]['serial'],value)
  except Exception as ex:e.error='Rack return: '+str(ex)
  finally:
   if e.rack_returns.get(pid) is record:e.rack_returns.pop(pid,None)
   if e.pending_hits.get(pid)==owner:e.pending_hits.pop(pid,None)
   e.session.inflight-=1

 async def execute(d):
  if e.session.busy and d.get('_recovery')!=e.session.operation['token']:raise ValueError('Recovery in progress')
  tracked=d['cmd']!='recovery' and '_recovery' not in d
  if tracked:e.session.inflight+=1
  try:return await execute_action(d)
  finally:
   if tracked:e.session.inflight-=1

 async def execute_action(d):
  if not e.armed or not e.connected:raise ValueError('Arm v2 first')
  cmd=d['cmd'];owner=d.get('_owner')
  if not e.session.valid(d):return
  if cmd=='rack_sequence':
   e.session.configure(d);tmp=ROOT/'session-settings.json.tmp';tmp.write_text(json.dumps(e.session.preferences));tmp.replace(ROOT/'session-settings.json');return
  if cmd=='rack_parameter':
   if d.get('epoch')!=e.catalog['epoch']:raise ValueError('Composition changed')
   control=e.session.control(d['row'],d['control']);kind=control.get('type',control['bindings'][0]['type']);value=d['value'];epoch=e.epoch
   if kind in NUM:value=finite(value,control['min'],control['max'])
   elif kind=='ParamBoolean':
    if type(value) is not bool:raise ValueError('Expected on/off')
   elif not any(type(value) is type(option) and value==option for option in control['options']):raise ValueError('Unknown choice')
   guards={b['parameter']:copy.deepcopy(e.contracts[b['parameter']]) for b in control['bindings']}
   for b in control['bindings']:
    pid=b['parameter']
    if kind in NUM:
     e.claim(pid);e.envelopes.pop(pid,None);e.slots[pid].drive=False;e.owned.discard(pid);e.lastout.pop(pid,None)
     await animation_rpc(dict(cmd='animation_set',id=pid,source='static'))
    if not e.armed or not e.connected or e.epoch!=epoch or not e.session.valid(d) or any(e.contracts.get(p)!=guard for p,guard in guards.items()):raise ValueError('Rack control destination changed')
    e.session.control(d['row'],d['control'])
   for b in control['bindings']:
    pid=b['parameter'];e.manual(pid,value,duration=0);e.observed.pop(pid,None)
    if kind in NUM:e.lastout[pid]=value
   await send(dict(cmd='values',epoch=e.epoch,values=[(b['parameter'],value) for b in control['bindings']]))
   if kind not in NUM:
    for b in control['bindings']:
     pid=b['parameter'];asyncio.create_task(confirm_switch(pid,e.switches[pid]['serial'],value))
   return
  if cmd=='rack_fire':
   if d.get('epoch')!=e.catalog['epoch']:raise ValueError('Composition changed; refresh the rack')
   row=e.session.row(d['row']);pad=next((p for p in row['pads'] if p['id']==d['pad']),None)
   if not pad:raise ValueError('Rack pad unavailable')
   if not e.rack_state()[row['id']]['ready']:raise ValueError('Rack section offline')
   if pad.get('mode') in ('pulse','toggle'):
    await execute(dict(cmd='effect_hit',epoch=e.catalog['epoch'],bindings=pad['bindings'],key=row['id']+':'+pad['id'],_rack_restore=True,_rack_toggle=pad.get('mode')=='toggle' or pad.get('contrast_hit') is True,amount=d.get('amount',.65),beats=d.get('beats',.25),**({'_loop':d['_loop']} if '_loop' in d else {})))
   else:await execute(dict(cmd='rack_control',epoch=e.catalog['epoch'],row=row['id'],pad=pad['id'],action='trigger',**({'_loop':d['_loop']} if '_loop' in d else {})))
   return
  if cmd=='recovery':
   if d.get('epoch')!=e.catalog['epoch']:raise ValueError('Composition changed; refresh the return')
   name=d['name'];action=d['action']
   if action=='clear':
    e.session.clear(name);tmp=ROOT/'recovery.json.tmp';tmp.write_text(json.dumps(e.session.returns));tmp.replace(ROOT/'recovery.json');return
   token=e.session.begin(name,action)
   try:
    if action=='capture':
     semaphore=asyncio.Semaphore(4);fresh={};programs={};params=e.session.recovery_parameters()
     async def read(pid):
      async with semaphore:
       e.session.check(token,stable=True)
       def fetch():
        with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}',timeout=2) as f:parameter=json.load(f)
        program=None
        if pid in e.slots and not e.catalog.get('native_phase_mode'):
         with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}/phase-source',timeout=2) as f:program=native_program(json.load(f),parameter)
        return parameter['value'],program
       value,program=await asyncio.to_thread(fetch);e.session.check(token,stable=True);fresh[pid]=value
       if program:programs[pid]=program
     await asyncio.gather(*(read(pid) for ids in params.values() for pid in ids))
     e.session.capture(name,fresh,token,programs);tmp=ROOT/'recovery.json.tmp';tmp.write_text(json.dumps(e.session.returns));tmp.replace(ROOT/'recovery.json');return
    # Stop invalidates queued hits. Let a gate already being prepared clean up
    # before restoring the saved values or launching a different clip.
    deadline=time.monotonic()+12
    while e.session.inflight or e.pending_hits or e.launches or e.clip_starts or e.authored.busy:
     e.session.check(token)
     if time.monotonic()>deadline:raise ValueError('Current changes did not finish; try the return again')
     await asyncio.sleep(.025)
    e.session.check(token);snapshot=e.session.prepare_return(name)
    for item in snapshot['layers']:
     e.session.check(token);e.session.validate(snapshot)
     layer=next(l for l in e.catalog['layers'] if l['id']==item['id']);clip=item['clip'];actual=next((c for c in layer['clips'] if c['col']==layer['active']),None)
     if (actual or {}).get('id')!=(clip or {}).get('id'):
      await execute(dict(cmd='launch',layer_id=layer['id'],_recovery=token,**({'clip_id':clip['id']} if clip else {'col':0})))
      deadline=time.monotonic()+12
      while layer['id'] in e.launches or (clip and (clip['id'] in e.clip_starts or clip['id'] in e.authored.busy)):
       e.session.check(token)
       if time.monotonic()>deadline:raise ValueError('Recovery clip did not launch')
       await asyncio.sleep(.025)
    programs=[(int(pid),item['native_animation']) for target in snapshot['targets'].values() for pid,item in target['params'].items() if item.get('native_animation')]
    values=e.session.apply_return(snapshot,token)
    if values:await send(dict(cmd='values',epoch=e.epoch,values=values))
    for pid,value in values:
     if pid not in e.slots and pid in e.switches:asyncio.create_task(confirm_switch(pid,e.switches[pid]['serial'],value))
    for pid,program in programs:
     e.session.check(token);e.session.validate(snapshot,require_active=True)
     actual=await animation_rpc(dict(cmd='animation_set',id=pid,fields={}));e.session.check(token);e.session.validate(snapshot,require_active=True)
     current=native_program(actual,actual['parameter'])
     if not same_program(current,program):
      # Duration controls determine the valid ranges of some timeline fields.
      first={k:program['fields'][k] for k in ('DurationType','DurationIsScalable','Duration') if k in program['fields']}
      actual=await animation_rpc(dict(cmd='animation_set',id=pid,**{k:v for k,v in program.items() if k!='fields'},fields=first));e.session.check(token);e.session.validate(snapshot,require_active=True)
      later={k:v for k,v in program['fields'].items() if k not in first}
      if later.get('PlayMode')=='Bounce' and later.get('PlayDirection') in ('<','>'):later.pop('PlayDirection')
      if later:actual=await animation_rpc(dict(cmd='animation_set',id=pid,fields=later));e.session.check(token);e.session.validate(snapshot,require_active=True)
     e.session.validate(snapshot,require_active=True);e.params[pid][1]['value']=actual['parameter']['value'];e.observed[pid]=(actual['parameter']['value'],time.perf_counter())
   finally:e.session.end(token)
   return
  if cmd=='manual':
   pid=int(d['id']);v=e.manual(pid,d['value'],owner=owner,duration=d.get('_duration',.025))
   if v is not None:
    p=e.params[pid][1]
    if p['type'] in ('ParamEvent','ParamTrigger'):
     if v:await send(dict(cmd='request',parameter=pid,path=f'/parameter/by-id/{pid}/trigger'))
    else:
     await send(dict(cmd='values',epoch=e.epoch,values=[(pid,v)]))
     asyncio.create_task(confirm_switch(pid,e.switches[pid]['serial'],v))
  elif cmd=='rack_control':
   if d.get('action')=='clear':e.session.stop(d['row'])
   values,events=e.rack_plan(d);epoch=e.epoch;guards={pid:e.contracts[pid] for pid in [p for p,v in values]+events}
   def valid():return e.session.valid(d) and e.armed and e.connected and e.epoch==epoch and all(e.contracts.get(pid)==contract for pid,contract in guards.items())
   for pid,value in values:
    if not valid():raise ValueError('Rack destination changed')
    if pid in e.slots:
     e.claim(pid);e.envelopes.pop(pid,None);e.slots[pid].drive=False;e.owned.discard(pid);e.lastout.pop(pid,None)
     await animation_rpc(dict(cmd='animation_set',id=pid,source='static'))
    if not valid():raise ValueError('Rack destination changed')
    await animation_rpc(dict(cmd='request',parameter=pid,path=f'/parameter/by-id/{pid}',method='PUT',value={'value':value}))
    if not valid():raise ValueError('Rack destination changed')
    e.manual(pid,value,duration=0);e.observed.pop(pid,None)
    if pid in e.slots:e.lastout[pid]=value
    elif pid in e.switches:asyncio.create_task(confirm_switch(pid,e.switches[pid]['serial'],value))
   for pid in events:
    if not valid():raise ValueError('Rack destination changed')
    # Recheck the rack after preparation. A trigger never changes bypass or amount.
    e.rack_plan(d)
    await animation_rpc(dict(cmd='request',parameter=pid,path=f'/parameter/by-id/{pid}/trigger'))
   if events:e.rack_flash[d['row'],d['pad']]=time.monotonic()+.15
  elif cmd in ('effect_hit','effect_color'):
   bindings=hit_bindings(e,d)
   amount=finite(d.get('amount',1),0,1)
   if cmd=='effect_color':
    values=[]
    for b in bindings:
     pid=b['opacity'];e.manual(pid,amount,duration=0);e.lastout[pid]=amount;values.append((pid,amount))
     if e.current_value(b['bypass']):
      e.manual(b['bypass'],False);asyncio.create_task(confirm_switch(b['bypass'],e.switches[b['bypass']]['serial'],False))
     values.append((b['bypass'],False))
    await send(dict(cmd='values',epoch=e.epoch,values=values));return
   seconds=finite(d.get('beats',.25),.125,4)*60/e.bpm
   seconds=finite(seconds,.05,4)
   e.control_serial+=1;hit_owner='hit:'+str(e.control_serial)
   guards={b['opacity']:copy.deepcopy(e.contracts[b['opacity']]) for b in bindings}
   returns={b['opacity']:e.rack_pulse_baseline(b) for b in bindings} if d.get('_rack_restore') else {}
   for b in bindings:
    pid=b['opacity'];e.claim(pid,hit_owner);e.pending_hits[pid]=hit_owner;e.envelopes.pop(pid,None);e.owned.discard(pid);e.lastout.pop(pid,None)
    if pid in returns:e.rack_returns[pid]=dict(returns[pid],owner=hit_owner,finishing=False)
   def current(b):return e.armed and e.connected and e.control_owner.get(b['opacity'])==hit_owner and e.contracts.get(b['opacity'])==guards[b['opacity']]
   prepared=[]
   try:
    for b in bindings:
     pid=b['opacity']
     if not current(b) or not e.session.valid(d):raise ValueError('Effect ownership changed')
     await animation_rpc(dict(cmd='claim',id=pid))
     if not current(b) or not e.session.valid(d):raise ValueError('Effect ownership changed')
     await animation_rpc(dict(cmd='request',parameter=b['bypass'],path=f"/parameter/by-id/{b['bypass']}",method='PUT',value={'value':False}))
     e.manual(b['bypass'],False,owner=hit_owner);e.confirm_switch(b['bypass'],e.switches[b['bypass']]['serial'],False)
     if not current(b) or not e.session.valid(d):raise ValueError('Effect ownership changed')
     prepared.append(b)
     base=returns.get(pid,{});end=base.get('value',0) if not base.get('bypass',True) else 0;peak=end*(1-amount) if d.get('_rack_toggle') and end>0 else max(amount,end)
     await animation_rpc(dict(cmd='request',parameter=pid,path=f'/parameter/by-id/{pid}',method='PUT',value={'value':peak}))
    for b in bindings:
     if not current(b) or not e.session.valid(d):raise ValueError('Effect ownership changed')
     if cmd=='effect_hit' and 'event' in b:
      await animation_rpc(dict(cmd='request',parameter=b['event'],path=f"/parameter/by-id/{b['event']}/trigger"))
    for b in bindings:
     if not current(b) or not e.session.valid(d):raise ValueError('Effect ownership changed')
     if cmd=='effect_hit':
      base=returns.get(b['opacity'],{});end=base.get('value',0) if not base.get('bypass',True) else 0
      e.effect_pulse(b['opacity'],end*(1-amount) if d.get('_rack_toggle') and end>0 else max(amount,end),seconds,owner=hit_owner,key=str(d.get('key','')),end=end)
     else:e.manual(b['opacity'],amount,owner=hit_owner,duration=0)
   except Exception:
    for b in prepared:
     if current(b) and b['opacity'] in returns:
      record=e.rack_returns.get(b['opacity'])
      if record:e.session.inflight+=1;await restore_rack_pulse(b['opacity'],record)
     elif current(b):
      e.manual(b['opacity'],0,owner=hit_owner,duration=0)
      try:await animation_rpc(dict(cmd='request',parameter=b['opacity'],path=f"/parameter/by-id/{b['opacity']}",method='PUT',value={'value':0}))
      except Exception:pass
    raise
   finally:
    for b in bindings:
     if e.pending_hits.get(b['opacity'])==hit_owner:e.pending_hits.pop(b['opacity'],None)
     if e.rack_returns.get(b['opacity'],{}).get('owner')==hit_owner and b['opacity'] not in e.envelopes:e.rack_returns.pop(b['opacity'],None)
  elif cmd=='set_home':
   e.set_home(d['target']);tmp=ROOT/'homes.json.tmp';await asyncio.to_thread(tmp.write_text,json.dumps(e.homes));tmp.replace(ROOT/'homes.json')
  elif cmd=='return_home':
   values=e.return_home(d['target'],owner=owner)
   if values:await send(dict(cmd='values',epoch=e.epoch,values=values))
  elif cmd=='envelope':e.envelope(int(d['id']),d['direction'],owner=owner)
  elif cmd=='envelope_config':e.envelope_config(int(d['id']),d.get('settings',{}))
  elif cmd=='range':
   pid=int(d['id']);e.param_range(pid,d['lo'],d['hi']);p=e.params[pid][1]
  elif cmd=='authored':await apply_authored(d)
  elif cmd=='drive':e.drive(int(d['id']),bool(d['on']),owner=owner)
  elif cmd=='drive_all':e.drive_all(d)
  elif cmd=='parameter_lock':e.parameter_lock(d)
  elif cmd=='gesture':e.gesture(d['target'],d['action'],d.get('mode','harmonic'),owner=owner)
  elif cmd=='settings':e.settings(d['target'],d)
  elif cmd=='relationship':e.relationship(d['target'],d)
  elif cmd=='parameter_motion':e.parameter_motion(int(d['id']),d)
  elif cmd=='drive_bank':e.drive_bank_action(d)
  elif cmd in ('launch','layer_action'):
   layer=next((l for l in e.catalog['layers'] if l['id']==int(d['layer_id'])),None) if 'layer_id' in d else next((l for l in e.catalog['layers'] if l['i']==int(d['layer'])),None)
   if not layer:raise ValueError('Layer unavailable')
   li=layer['i']
   if cmd=='layer_action':
    action=d['action'];clips=layer['clips']
    if 'eligible' in d:
     eligible=set(int(x) for x in d['eligible']);clips=[c for c in clips if c['id'] in eligible]
    if any(c.get('family') for c in clips):
     families={}
     for c in clips:
      key=c.get('family') or str(c['id'])
      if key not in families or c['col']==layer['active'] or (c.get('primary') and families[key]['col']!=layer['active']):families[key]=c
     clips=list(families.values())
    if action=='eject':col=0
    elif action not in ('previous','next','random'):raise ValueError('Unknown layer action')
    elif not clips:raise ValueError('No eligible clips')
    elif action=='random':col=random.choice([c for c in clips if c['col']!=layer['active']] or clips)['col']
    else:
     index=next((i for i,c in enumerate(clips) if c['col']==layer['active']),-1 if action=='next' else 0)
     col=clips[(index+(1 if action=='next' else -1))%len(clips)]['col']
   elif 'clip_id' in d:
    clip=next((c for c in layer['clips'] if c['id']==int(d['clip_id'])),None)
    if not clip:raise ValueError('Clip moved or unavailable')
    col=clip['col']
   else:col=int(d['col'])
   lid,serial=e.begin_launch(li,col)
   clip_id=e.launches[lid]['id']
   await send(e.binding());await observe();await broadcast(e.catalog)
   try:
    if col==0:await animation_rpc(dict(cmd='request',path=f'/composition/layers/by-id/{lid}/clear'))
    elif clip_id is None:raise ValueError('Refresh the clip catalog before launching')
    else:await animation_rpc(dict(cmd='request',path=f'/composition/clips/by-id/{clip_id}/connect'))
   except Exception:
    if e.launches.get(lid,{}).get('serial')==serial:e.launches.pop(lid,None)
    raise
   finally:rescan.set()
  elif cmd=='effect_action':
   ids=effect_parameters(e,d['ids']);direction=d['direction']
   if direction not in ('in','out'):raise ValueError('Choose IN or OUT')
   for pid in ids:e.envelope(pid,direction,owner=owner)
  elif cmd=='group_level':
   if d.get('epoch')!=e.catalog['epoch']:raise ValueError('Composition changed; rebuild this group')
   value=finite(d['value'],0,1);members=[]
   for m in d['members']:
    pid=int(m['id']);item=e.params.get(pid)
    if not item or pid not in e.slots or item[1]['name'] not in ('Level','Opacity','master'):raise ValueError('Group member unavailable')
    if item[0]!=m['target']:raise ValueError('Group destination changed')
    weight=finite(m['weight'],0,1);p=item[1];members.append((pid,p['min']+value*weight*(p['max']-p['min'])))
   if not members:raise ValueError('Choose group members')
   for pid,value in members:e.manual(pid,value,owner=owner)
  elif cmd=='motion_scale':
   targets=set(str(t) for t in d['targets'])
   if not targets or not targets.issubset(e.groups):raise ValueError('Motion scope unavailable')
   value=finite(d['value'],0,8)
   if d['mode']=='rate':
    if value not in (.125,.25,.5,1,2,4,8):raise ValueError('Choose a musical rate')
    destination=e.rate_scale
   elif d['mode']=='intensity':value=finite(value,0,1);destination=e.intensity_scale
   else:raise ValueError('Choose Rate or Intensity')
   for pid,(target,p) in e.params.items():
    if target in targets and pid in e.slots:destination[pid]=value
  elif cmd=='tempo':
   e.bpm=finite(d['value'],20,500);p=e.catalog.get('tempo',{}).get('tempo',{})
   if p.get('id'):await send(dict(cmd='request',method='PUT',path=f"/parameter/by-id/{p['id']}",value={'value':e.bpm}))
  elif cmd=='tap_tempo':
   p=e.catalog.get('tempo',{}).get('tempo_tap',{})
   if not p.get('id'):raise ValueError('Native tap tempo unavailable')
   now=time.monotonic()
   if now-getattr(e,'last_tap',0)<.1:return
   e.last_tap=now
   await animation_rpc(dict(cmd='request',parameter=p['id'],path=f"/parameter/by-id/{p['id']}/trigger"))
  elif cmd=='downbeat':
   e.session.downbeat()
   for sl in e.slots.values():sl.phi=sl.phi_fm=0
   p=e.catalog.get('tempo',{}).get('resync',{})
   if p.get('id'):await animation_rpc(dict(cmd='request',parameter=p['id'],path=f"/parameter/by-id/{p['id']}/trigger"))
  elif cmd=='select':e.selected=str(d['target'])
  elif cmd=='hold':e.set_hold(d.get('on'),owner)
  else:raise ValueError('Unknown control')

 async def finish_inputs(client=None):
  e.session.cancel()
  pulse_ids={pid for pid,env in e.envelopes.items() if env['direction']=='pulse'}|set(e.pending_hits)
  returns={pid:copy.deepcopy(e.rack_returns[pid]) for pid in pulse_ids if pid in e.rack_returns}
  for pid in pulse_ids:e.claim(pid)
  e.pending_hits.clear()
  pulses=[]
  for pid in pulse_ids:
   if pid not in e.slots:continue
   if pid in returns:pulses.append(dict(cmd='manual',id=returns[pid]['bypass_id'],value=returns[pid]['bypass']))
   pulses.append(dict(cmd='manual',id=pid,value=returns[pid]['value'] if pid in returns else 0,_duration=0))
  for action in e.performance.cancel(client,immediate=True)+e.play_actions.release(client,immediate=True)+pulses:
   if not e.armed or not e.connected:continue
   await execute(action)
   if action['cmd']=='manual':
    pid=action['id'];value=action['value']
    await animation_rpc(dict(cmd='request',parameter=pid,method='PUT',path=f'/parameter/by-id/{pid}',value={'value':value}))

 async def handler(ws):
  nonlocal reload_until,full_scan
  client=str(id(ws));clients.add(ws);await ws.send(json.dumps(e.catalog));await ws.send(json.dumps(dict(type='surface_version',version=surface_document()[1])))
  try:
   async for raw in ws:
    try:
     d=json.loads(raw);cmd=d['cmd'];e.error=''
     if cmd=='surface_reload':
      allowed=not e.armed and e.connected
      if allowed:reload_until=time.monotonic()+2
      await ws.send(json.dumps(dict(type='surface_reload',allowed=allowed,request=d.get('request'))));continue
     if cmd=='select':e.selected=str(d['target']);await observe();continue
     if cmd=='watch':
      targets=d.get('targets',[]);subset=d.get('native_ids')
      if not isinstance(targets,list) or any(not isinstance(t,str) for t in targets):raise ValueError('Choose current watch targets')
      if 'native_ids' in d and (not isinstance(subset,list) or any(type(pid) is not int for pid in subset)):raise ValueError('Choose native parameter IDs')
      watches[client]=set(targets)
      if 'native_ids' in d:native_watches[client]=set(subset)
      else:native_watches.pop(client,None)
      e.watched=set().union(*watches.values());await observe();continue
     if cmd=='refresh':full_scan=True;rescan.set();await send(dict(cmd='reconnect'));continue
     if cmd=='layout_save':
      saved=e.performance.save(d['layout']);await ws.send(json.dumps(dict(type='layout',layout=saved)));continue
     if cmd=='layout_get':
      await ws.send(json.dumps(dict(type='layout_active' if d.get('active') else 'layout',layout=e.performance.active if d.get('active') else e.performance.layouts.get(d['id']))));continue
     if cmd in ('layout_grab','layout_release'):
      commands=e.performance.grab(d['id']) if cmd=='layout_grab' else e.performance.release()
      for action in commands:
       if e.armed and e.connected:await execute(action)
      continue
     if cmd in ('control','input','input_release'):
      if not e.armed or not e.connected:raise ValueError('Arm v2 first')
      if cmd=='input_release':commands=e.performance.cancel(client)
      elif cmd=='input':commands=e.performance.input(client,d)
      else:commands=e.performance.event(client,str(d['slot']),d.get('phase','move'),d.get('value'),d.get('delta'))
      for action in commands:await execute(action)
      continue
     if cmd in ('effect_press','effect_release'):
      if cmd=='effect_press':
       if not e.armed or not e.connected:raise ValueError('Arm v2 first')
       e.play_actions.begin(client,str(d['key']),d['ids'])
      else:
       for action in e.play_actions.release(client,d.get('key')):
        if e.armed and e.connected:await execute(action)
      continue
     if cmd in ('animation_get','animation_set'):
      pid=int(d['id'])
      if pid not in e.slots:raise ValueError('Animation requires a numeric parameter')
      if cmd=='animation_set':
       if e.session.busy:raise ValueError('Recovery in progress')
       if not e.armed or not e.connected:raise ValueError('Arm v2 first')
       e.claim(pid);e.envelopes.pop(pid,None);e.owned.discard(pid);e.lastout.pop(pid,None);e.slots[pid].drive=False
      message={k:d[k] for k in ('source','dial','fields','in','out') if k in d};message.update(cmd=cmd,id=pid)
      try:
       data=await animation_rpc(message)
       if pid in e.params:e.params[pid][1]['value']=data.get('parameter',{}).get('value',e.params[pid][1]['value'])
       await ws.send(json.dumps(dict(type='animation',id=pid,data=data)))
      except Exception as ex:
       await ws.send(json.dumps(dict(type='animation',id=pid,error=str(ex))));raise
      continue
     if cmd=='arm':
      if d['on']:
       if time.monotonic()<reload_until:raise ValueError('Surface update in progress; arm again in a moment')
       proc=await asyncio.create_subprocess_exec('ps','-axo','args',stdout=asyncio.subprocess.PIPE);text=(await proc.communicate())[0].decode()
       if any('heart.py --all' in line for line in text.splitlines()):raise ValueError('V1 engine is still running. V2 stays read-only to avoid competing writers.')
       if not e.connected:raise ValueError('Resolume is not connected')
       if time.monotonic()<reload_until:raise ValueError('Surface update in progress; arm again in a moment')
       e.armed=True
      else:
       try:await finish_inputs()
       finally:e.disarm();await send(dict(cmd='arm',on=False))
       continue
      await send(dict(cmd='arm',on=e.armed))
      e.phase_starts.update(pid for pid,(_,p) in e.params.items() if p.get('native_phase'))
      e.clip_starts.update(t['clip_id'] for t in e.catalog['targets'] if (t.get('authored') and t.get('layer_id') in e.authored.data.get('auto_layers',[])) or t.get('native_phase_clip'))
      if 'autostart' in d:e.clip_starts.intersection_update(int(cid) for cid in d['autostart'])
      await start_clips();rescan.set();continue
     if not e.armed or not e.connected:raise ValueError('Arm v2 first')
     await execute({k:v for k,v in d.items() if not k.startswith('_')})
    except Exception as ex:e.error=str(ex)
  finally:
   clients.discard(ws)
   watches.pop(client,None);native_watches.pop(client,None);e.watched=set().union(*watches.values())
   await observe()
   if not clients:
    try:await finish_inputs(client)
    except Exception as ex:e.error='Input release: '+str(ex)
    finally:e.disarm();await send(dict(cmd='arm',on=False))
   else:
    for action in e.performance.cancel(client)+e.play_actions.release(client):
     if e.armed and e.connected:
      try:await execute(action)
      except Exception as ex:e.error=str(ex)
 async def http(reader,writer):
  try:
   request=await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'),3);path=request.split(b' ')[1].decode().split('?')[0]
   name={'/':'index.html','/progress':'progress.html','/progress.json':'progress.json','/controllers.js':'controllers.js','/performance_surface.js':'performance_surface.js','/performance.css':'performance.css','/playing.js':'playing.js','/playing.css':'playing.css'}.get(path)
   if not name:writer.write(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
   else:
    body,version=surface_document() if name=='index.html' else ((ROOT/name).read_bytes(),None)
    if version:body=body.replace(b'<head>',('<head><meta name="heart-surface-version" content="'+version+'">').encode(),1)
    kind='application/json' if name.endswith('.json') else 'application/javascript' if name.endswith('.js') else 'text/css' if name.endswith('.css') else 'text/html; charset=utf-8';writer.write(f'HTTP/1.1 200 OK\r\nContent-Type: {kind}\r\nContent-Length: {len(body)}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n'.encode()+body)
   await writer.drain()
  except Exception:pass
  finally:writer.close()
 try:
  async with await asyncio.start_server(http,'127.0.0.1',8875), websockets.serve(handler,'127.0.0.1',8876,compression=None,max_size=262144):
   print('Heart v2 http://localhost:8875 · dashboard /progress · starts read-only',flush=True)
   await asyncio.gather(scan(),tick(),publish(),bridge_read(),surface_updates())
 finally:
  if bridge.returncode is None:bridge.terminate();await bridge.wait()
if __name__=='__main__':asyncio.run(main())
