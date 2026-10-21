"""Restore only verified, serialized clip programs; layer/group geometry is excluded."""
import argparse,json,time,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from authored import NUM,equal
from bridge import request,animation

def read(path):return json.loads(request(path,'GET'))
def put(pid,**values):request(f'/parameter/by-id/{pid}','PUT',values)
def differences(p,native,phase):
 out=[]
 if p['type'] in NUM:
  if phase.get('phase_source')!=p['source']:out.append('source')
  for k in ('in','out'):
   if not equal(native.get(k),p[k]):out.append(k)
 if p.get('source')=='timeline':
  fields=phase.get('parameters',{})
  for k,v in p['fields'].items():
   if k=='PlayDirection' and p['fields']['PlayMode']=='Bounce':continue
   if not equal(fields.get(k,{}).get('value'),v):out.append(k)
 elif not equal(native.get('value'),p['value']):out.append('value')
 return out

def restore(p,live,phase):
 pid=p['id']
 if p.get('source')=='timeline':
  if phase.get('phase_source')!='timeline':animation(dict(cmd='animation_set',id=pid,source='timeline'))
  fields={k:v for k,v in p['fields'].items() if k not in ('PlayDirection','Max Distance','Interval')}
  data=animation(dict(cmd='animation_set',id=pid,fields=fields,**{'in':p['in'],'out':p['out']}))
  extra={k:v for k,v in p['fields'].items() if k in ('Max Distance','Interval')}
  if extra:data=animation(dict(cmd='animation_set',id=pid,fields=extra))
  put(pid,value=p['in']+(p['out']-p['in'])*p.get('phase',0))
  put(data['parameters']['PlayDirection']['id'],value=p['fields']['PlayDirection'])
 elif p['type'] in NUM:
  animation(dict(cmd='animation_set',id=pid,source='static',**{'in':p['in'],'out':p['out']}));put(pid,value=p['value'])
 else:put(pid,value=p['value'])

def run(apply=False):
 profiles=json.loads(Path('authored-clips.json').read_text());snapshot=json.loads(Path('/tmp/heart-authored-current-native.json').read_text())
 native_clips={c['id']:c for l in snapshot['layers'] for c in l.get('clips',[]) if c.get('video')}
 report=dict(applied=apply,epoch=profiles['epoch'],clips=[],errors=[],totals=dict(parameters=0,timelines=0,changed=0,restored_timelines=0))
 if str(read('/parameter/by-id/'+profiles['epoch'])['id'])!=profiles['epoch']:raise ValueError('Composition identity changed')
 started=time.monotonic()
 for i,c in enumerate(profiles['clips'].values()):
  record=dict(id=c['id'],name=c['name'],changes=[],verified=0);report['clips'].append(record)
  try:
   clip=read(f"/composition/clips/by-id/{c['id']}")
   if clip.get('video',{}).get('description')!=native_clips[c['id']]['video'].get('description'):raise ValueError('Clip content changed')
   native={}
   for t in c['targets']:
    if t['identity'][0]=='source':params=clip['video'].get('sourceparams',{})
    else:
     fx=next((e for e in clip['video'].get('effects',[]) if 'effect:'+str(e['id'])==t['id'] and e['name']==t['identity'][-1]),None)
     if not fx:raise ValueError('Clip effect changed')
     params={**(fx.get('params') or {}),**(fx.get('mixer') or {})}
    for p in t['params']:
     q=params.get(p['name'])
     if not q or any(q.get(k)!=v for k,v in [('id',p['id']),('valuetype',p['type'])]) or any(q.get(k,0 if k=='min' else 1)!=p[k] for k in ('min','max')):raise ValueError('Parameter contract changed')
     native[p['id']]=q
   ps=[p for t in c['targets'] for p in t['params']]
   def phase(p):return read(f"/parameter/by-id/{p['id']}/phase-source") if p['type'] in NUM else {}
   with ThreadPoolExecutor(max_workers=4) as pool:phases=list(pool.map(phase,ps))
   for p,phase_before in zip(ps,phases):
    n=native[p['id']];delta=differences(p,n,phase_before);report['totals']['parameters']+=1;report['totals']['timelines']+=p.get('source')=='timeline'
    if delta:
     item=dict(id=p['id'],name=p['name'],differences=delta,before=n,phase_before=phase_before,original=p);record['changes'].append(item);report['totals']['changed']+=1
     if apply:
      restore(p,n,phase_before)
      after=animation(dict(cmd='animation_get',id=p['id'])) if p['type'] in NUM else dict(parameter=read(f"/parameter/by-id/{p['id']}"))
      bad=differences(p,after['parameter'],after)
      if bad:raise ValueError(str(p['id'])+' did not restore '+str(bad))
      item['verified']=True
      if p.get('source')=='timeline' and phase_before.get('phase_source')!='timeline':report['totals']['restored_timelines']+=1
    record['verified']+=1
  except Exception as ex:report['errors'].append(dict(clip=c['id'],name=c['name'],error=str(ex)))
  if (i+1)%20==0:print(json.dumps(dict(clips=i+1,**report['totals'],errors=len(report['errors']))),flush=True)
  Path('checks/authored-native-repair-2026-09-11.json').write_text(json.dumps(report,indent=2)+'\n')
 report['seconds']=round(time.monotonic()-started,2);Path('checks/authored-native-repair-2026-09-11.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(**report['totals'],errors=report['errors'],seconds=report['seconds'])),flush=True)
 if report['errors']:raise SystemExit(1)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args();run(args.apply)
