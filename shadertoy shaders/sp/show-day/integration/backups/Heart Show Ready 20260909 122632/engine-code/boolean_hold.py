"""Temporary native boolean holds; explicit edits supersede old releases."""
class BooleanHolds:
 def __init__(self,current,write,read=None):self.current=current;self.write=write;self.read=read or (lambda p:p['value']);self.held={}
 def press(self,fx,name,owner):
  p=fx.params[name]
  if p.get('valuetype') not in ('ParamBool','ParamBoolean'):raise ValueError('Hold requires a boolean control')
  if not self.current(fx,p):raise ValueError('Control target changed')
  key=p['id'];h=self.held.get(key)
  if h is None:
   h=dict(fx=fx,param=p,base=bool(self.read(p)),owners=set());self.held[key]=h
  h['owners'].add(owner);self.write(p,True)
 def release(self,key,owner):
  h=self.held.get(key)
  if not h or owner not in h['owners']:return
  h['owners'].remove(owner)
  if h['owners']:return
  del self.held[key]
  if self.current(h['fx'],h['param']):self.write(h['param'],h['base'])
 def release_owner(self,owner):
  for key in list(self.held):self.release(key,owner)
 def supersede(self,p):self.held.pop(p['id'],None)
