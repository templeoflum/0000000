"""Independent integrated generators and single-input routes. Runtime proof v1."""
import math,threading

class Bank:
 def __init__(self):self.generators={};self.routes={};self.lock=threading.RLock()
 def configure(self,key,rate,now,seconds=1):
  if not isinstance(key,str) or not key or len(key)>80:raise ValueError('Generator ID required')
  if not math.isfinite(rate) or abs(rate)>64 or not math.isfinite(seconds) or not 0<=seconds<=30:raise ValueError('Invalid rate/transition')
  with self.lock:
   g=self.generators.get(key)
   if g is None:
    if len(self.generators)>=64:raise ValueError('Generator bank full')
    g=self.generators[key]={'phase':0.,'value':0.,'rate':rate,'from':rate,'target':rate,'at':now,'seconds':seconds}
   else:g.update({'from':g['rate'],'target':rate,'at':now,'seconds':seconds})
 def advance(self,turns,now):
  with self.lock:
   for g in self.generators.values():
    u=min(1,max(0,(now-g['at'])/g['seconds'])) if g['seconds'] else 1
    g['rate']=g['from']+(g['target']-g['from'])*(.5-.5*math.cos(math.pi*u))
    g['phase']+=g['rate']*turns
    g['value']=.5-.5*math.cos(2*math.pi*(g['phase']%1))
 def bind(self,route,generator,token,start,now,seconds=1,low=0,high=1,destination=None):
  if not isinstance(route,str) or not route or len(route)>80:raise ValueError('Route ID required')
  if not all(math.isfinite(v) for v in (start,seconds,low,high)) or not 0<=seconds<=30 or not 0<=low<=high<=1:raise ValueError('Invalid destination transform')
  with self.lock:
   if generator not in self.generators:raise ValueError('Unknown generator')
   if route not in self.routes and len(self.routes)>=256:raise ValueError('Route bank full')
   self.routes[route]={'generator':generator,'token':token,'start':start,'at':now,'seconds':seconds,'low':low,'high':high,'destination':destination,'status':'connected','value':start}
 def value(self,route,token,now):
  with self.lock:
   r=self.routes.get(route)
   if r is None or r['token']!=token:return None
   u=min(1,max(0,(now-r['at'])/r['seconds'])) if r['seconds'] else 1
   target=r['low']+(r['high']-r['low'])*self.generators[r['generator']]['value']
   r['value']=r['start']+(target-r['start'])*(.5-.5*math.cos(math.pi*u));r['status']='connected'
   return r['value']
 def remove(self,route):
  with self.lock:return self.routes.pop(route,None)
 def reset(self):
  with self.lock:
   for g in self.generators.values():g['phase']=g['value']=0.
 def snapshot(self,valid_tokens):
  with self.lock:
   return {'generators':{k:{'phase':g['phase'],'value':g['value'],'rate':g['rate']} for k,g in self.generators.items()},
           'routes':{k:{n:v for n,v in r.items() if n in ('generator','destination','value')}|{'status':'connected' if r['token'] in valid_tokens else 'unassigned'} for k,r in self.routes.items()}}
