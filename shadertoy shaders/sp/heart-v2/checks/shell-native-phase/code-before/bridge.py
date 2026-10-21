"""Isolated Arena output. Latest continuous values; ordered discrete actions."""
import asyncio,json,sys,urllib.request,urllib.error,time,os,math
import websockets
BASE=os.environ.get('HEART_V2_ARENA','http://127.0.0.1:8080/api/v1')
WS_URL=os.environ.get('HEART_V2_SOCKET',BASE.replace('http://','ws://').replace('https://','wss://'))
MAX_SUBSCRIPTIONS=256
MAX_ACTIONS=64
RECONNECT_DELAYS=(5,15)
def report(**kw):print(json.dumps(kw,separators=(',',':')),flush=True)
def request(path,method='POST',value=None):
 data=None if value is None else json.dumps(value).encode()
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,method=method,headers={'Content-Type':'application/json'}),timeout=3) as f:return f.read()
SOURCES={'static','timeline','bpm_sync','composition_fft','external_fft','entity_fft','crossfader','clip_position','transition','dashboard'}
def animation(m):
 """Inspect fresh native metadata; never accept client-supplied parameter paths/IDs."""
 pid=int(m['id']);path=f'/parameter/by-id/{pid}';phase=path+'/phase-source'
 def read():
  data=json.loads(request(phase,'GET'));data['parameter']=json.loads(request(path,'GET'));return data
 if m['cmd']=='animation_get':return read()
 source=m.get('source');fields=m.get('fields',{})
 if source is not None and source not in SOURCES:raise ValueError('Unsupported animation source')
 if not isinstance(fields,dict):raise ValueError('Expected animation fields')
 if source=='dashboard' and (type(m.get('dial')) is not int or not 1<=m['dial']<=8):raise ValueError('Dashboard dial must be 1–8')
 if source is not None:
  payload={'phase_source':source}
  if source=='dashboard':payload['dial']=m['dial']
  request(phase,'PUT',payload)
 data=read()
 if source is not None:
  deadline=time.monotonic()+1.5
  while data.get('phase_source')!=source or (source=='dashboard' and data.get('dial')!=m['dial']):
   if time.monotonic()>=deadline:raise ValueError('Resolume did not confirm animation source')
   time.sleep(.04);data=read()
 params=data.get('parameters') or {};writes=[]
 for key,value in fields.items():
  if key not in params:raise ValueError('Animation control unavailable: '+key)
  p=params[key];kind=p.get('valuetype')
  if kind=='ParamChoice':
   if value not in p.get('options',[]):raise ValueError('Invalid animation choice')
  elif kind in ('ParamBoolean','ParamBool'):
   if type(value) is not bool:raise ValueError('Expected boolean')
  elif kind in ('ParamRange','ParamFloat','ParamInt','ParamNumber','ParamInteger'):
   if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('Expected finite animation number')
   if not p.get('min',-float('inf'))<=value<=p.get('max',float('inf')):raise ValueError('Animation number outside range')
  else:raise ValueError('Unsupported animation control type')
  writes.append((f"/parameter/by-id/{int(p['id'])}",{'value':value}))
 bounds={k:m[k] for k in ('in','out') if k in m}
 if bounds:
  p=data['parameter']
  for value in bounds.values():
   if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not p['min']<=value<=p['max']:raise ValueError('Animation range outside parameter limits')
  writes.append((path,bounds))
 for url,value in writes:request(url,'PUT',value)
 def equal(a,b):
  return math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-7) if isinstance(a,(float,int)) and isinstance(b,(float,int)) else a==b
 data=read();deadline=time.monotonic()+1.5
 while not (all(equal((data.get('parameters') or {}).get(k,{}).get('value'),v) for k,v in fields.items()) and all(equal(data['parameter'].get(k),v) for k,v in bounds.items())):
  if time.monotonic()>=deadline:raise ValueError('Resolume did not confirm animation controls')
  time.sleep(.04);data=read()
 return data
async def main():
 from pathlib import Path
 if not os.environ.get('HEART_V2_SOCKET') and not os.environ.get('HEART_V2_ARENA') and Path(__file__).with_name('api-paused.json').exists():
  report(connected=False,armed=False,error='Heart API paused after Resolume memory incident');return
 pending={};claimed=set();allowed=set();numeric=set();epoch=None;armed=False;queue=asyncio.Queue(maxsize=MAX_ACTIONS);connected=False;generation=0;output_lock=asyncio.Lock();released=set();versions={};observed=set();observed_order=[];samples={};reconnect=asyncio.Event();output_ready=asyncio.Event()
 async def commands():
  nonlocal epoch,armed,allowed,numeric,generation,observed,observed_order
  while True:
   line=await asyncio.to_thread(sys.stdin.readline)
   if not line:raise SystemExit
   m={}
   try:
    m=json.loads(line);cmd=m['cmd']
    if cmd=='bind':
     new_allowed=set(m['ids']);new_numeric=set(m.get('numeric',[]))
     keep=set(m.get('keep',[]))&allowed&new_allowed
     keep={pid for pid in keep if (pid in numeric)==(pid in new_numeric)}
     for pid in (allowed|new_allowed)-keep:versions[pid]=versions.get(pid,0)+1
     epoch=m['epoch'];allowed=new_allowed;numeric=new_numeric
     samples.clear()
     claimed.intersection_update(keep);released.intersection_update(keep)
     for pid in set(pending)-keep:pending.pop(pid,None)
     if m.get('reset',False):generation+=1
    elif cmd=='observe' and m['epoch']==epoch:
     ids=list(dict.fromkeys(pid for pid in m.get('ids',[]) if pid in allowed));observed_order=ids[:MAX_SUBSCRIPTIONS];observed=set(observed_order)
     if len(ids)>MAX_SUBSCRIPTIONS:report(error=f'Native readback limited to {MAX_SUBSCRIPTIONS} parameters; narrow the visible scope')
     for pid in set(samples)-observed:samples.pop(pid,None)
    elif cmd=='reconnect':reconnect.set()
    elif cmd=='arm':armed=bool(m['on']);pending.clear();claimed.clear();generation+=1
    elif cmd in ('animation_get','animation_set','claim'):
     if m['id'] not in allowed:report(rpc=m['rpc'],error='Parameter unavailable');continue
     if cmd in ('animation_set','claim'):
      if not armed or not connected:report(rpc=m['rpc'],error='Arm v2 first');continue
      pid=m['id'];released.add(pid);pending.pop(pid,None);claimed.discard(pid);versions[pid]=versions.get(pid,0)+1
     queue.put_nowait((generation,m,versions.get(m['id'],0)))
    elif cmd=='values' and armed and connected and m['epoch']==epoch:
     for pid,v in m['values']:
      if pid in allowed:released.discard(pid);pending[pid]=v
     output_ready.set()
    elif cmd=='request':
     if not armed or not connected:
      if 'rpc' in m:report(rpc=m['rpc'],error='Arm v2 first')
      continue
     queue.put_nowait((generation,m,versions.get(m.get('parameter'),0)))
   except asyncio.QueueFull:report(**dict(error='Native action queue is full; action rejected',**({'rpc':m['rpc']} if 'rpc' in m else {})))
   except Exception as e:report(**dict(error=str(e),**({'rpc':m['rpc']} if 'rpc' in m else {})))
 async def actions():
  while True:
   gen,m,version=await queue.get();pid=m.get('id',m.get('parameter'))
   if not connected or gen!=generation or (not armed and m['cmd']!='animation_get') or (pid is not None and (pid not in allowed or version!=versions.get(pid,0))):
    if 'rpc' in m:report(rpc=m['rpc'],error='Connection or ownership changed')
    continue
   try:
    if m['cmd'] in ('animation_get','animation_set','claim'):
     # Reads do not block continuous output. Writes wait for an in-flight claim/send.
     if m['cmd'] in ('animation_set','claim'):
      async with output_lock:
       if gen!=generation or not armed or pid not in allowed or version!=versions.get(pid,0):raise ValueError('Ownership changed')
       if m['cmd']=='claim':
        await asyncio.to_thread(request,f'/parameter/by-id/{pid}/phase-source','DELETE')
        if gen!=generation or not armed or pid not in allowed or version!=versions.get(pid,0):raise ValueError('Ownership changed')
        claimed.add(pid);data={'ok':True}
       else:data=await asyncio.to_thread(animation,m)
     else:data=await asyncio.to_thread(animation,m)
     report(rpc=m['rpc'],data=data)
    else:
     await asyncio.to_thread(request,m['path'],m.get('method','POST'),m.get('value'))
     if 'rpc' in m:report(rpc=m['rpc'],data={'ok':True})
   except Exception as e:report(**dict(error=str(e),**({'rpc':m['rpc']} if 'rpc' in m else {})))
 async def http_output():
  """Small by-ID requests avoid Arena's unsolicited full-composition broadcasts."""
  nonlocal connected,armed,generation
  failures=0;missing={}
  while True:
   opened=None
   try:
    while not allowed:await asyncio.sleep(.05)
    # The discovered IDs also provide a cheap native health check.
    await asyncio.to_thread(request,f'/parameter/by-id/{next(iter(allowed))}','GET')
    opened=time.monotonic();health_at=opened;connected=True;claimed.clear();report(connected=True)
    while connected:
     try:await asyncio.wait_for(output_ready.wait(),.5)
     except TimeoutError:
      if allowed and time.monotonic()-health_at>=3:
       await asyncio.to_thread(request,f'/parameter/by-id/{next(iter(allowed))}','GET');health_at=time.monotonic()
      continue
     output_ready.clear();tick=time.perf_counter();batch=list(pending);gen=generation;sent=0
     for pid in batch:
      version=versions.get(pid,0)
      async with output_lock:
       if not armed or gen!=generation:break
       if pid not in allowed or pid in released or pid not in pending:continue
       if missing.get(pid)==version:pending.pop(pid,None);continue
       try:
        if pid in numeric and pid not in claimed:
         await asyncio.to_thread(request,f'/parameter/by-id/{pid}/phase-source','DELETE')
         if not armed or gen!=generation:break
         if pid not in allowed or version!=versions.get(pid,0) or pid in released:continue
         claimed.add(pid)
        value=pending.pop(pid)
        await asyncio.to_thread(request,f'/parameter/by-id/{pid}','PUT',{'value':value})
        sent+=1
       except urllib.error.HTTPError as ex:
        if ex.code==404:missing[pid]=version;report(error=f'Parameter {pid} is no longer available',refresh=True)
        else:raise
     if sent:report(sent=sent,work_ms=round((time.perf_counter()-tick)*1000,2))
     if pending:output_ready.set()
   except urllib.error.HTTPError as ex:report(error='Native output: '+str(ex),refresh=ex.code==404)
   except Exception as ex:report(error='Native output: '+str(ex))
   connected=False;armed=False;generation+=1;pending.clear();claimed.clear();report(connected=False,armed=False)
   if opened is not None and time.monotonic()-opened>=30:failures=0
   failures+=1
   if failures>len(RECONNECT_DELAYS):
    reconnect.clear();report(error='Resolume connection paused after 3 failures; use Refresh to retry');await reconnect.wait();reconnect.clear();failures=0
   else:await asyncio.sleep(RECONNECT_DELAYS[failures-1])
 async def http_observation():
  cursor=0;semaphore=asyncio.Semaphore(4)
  async def read(pid,version):
   async with semaphore:
    try:
     data=json.loads(await asyncio.to_thread(request,f'/parameter/by-id/{pid}','GET'))
     if pid in observed and versions.get(pid,0)==version:return [pid,data['value']]
    except Exception:return None
  while True:
   if connected and observed_order:
    # Keep selected controls responsive; rotate through other visible controls.
    ids=[pid for pid in observed_order if pid in allowed];front=ids[:8];tail=ids[8:]
    part=[tail[(cursor+i)%len(tail)] for i in range(min(8,len(tail)))] if tail else []
    cursor+=len(part);sample_epoch=epoch
    values=await asyncio.gather(*(read(pid,versions.get(pid,0)) for pid in front+part))
    values=[v for v in values if v is not None]
    if values and sample_epoch==epoch:report(native_epoch=sample_epoch,native_values=values)
   await asyncio.sleep(.1)
 async def socket():
  nonlocal connected,armed,generation
  failures=0
  while True:
   opened=None
   try:
    async with websockets.connect(WS_URL,max_size=128*1024*1024,compression=None,max_queue=1,open_timeout=5,close_timeout=2) as ws:
     opened=time.monotonic()
     connected=True;claimed.clear();samples.clear();subscriptions={};confirmed=set();last_report=0.;report(connected=True)
     async def drain():
      while True:
       # Only decode small, explicitly subscribed parameter replies.
       raw=await ws.recv(decode=False)
       if len(raw)>65536:continue
       try:m=json.loads(raw)
       except (ValueError,UnicodeDecodeError):continue
       pid=m.get('id');kind=m.get('type')
       if pid not in observed or subscriptions.get(pid)!=versions.get(pid,0):continue
       if kind=='parameter_subscribed':confirmed.add(pid)
       if kind in ('parameter_subscribed','parameter_update') and pid in confirmed and 'value' in m:samples[pid]=m['value']
     receiver=asyncio.create_task(drain())
     try:
      while not receiver.done():
       tick=time.perf_counter();batch=[(pid,v,versions.get(pid,0)) for pid,v in pending.items()];pending.clear();gen=generation
       for pid,value,version in batch:
        async with output_lock:
         if not armed or gen!=generation:break
         if pid not in allowed or version!=versions.get(pid,0):continue
         if pid in released:continue
         if pid in numeric and pid not in claimed:
          try:await asyncio.to_thread(request,f'/parameter/by-id/{pid}/phase-source','DELETE')
          except Exception as e:report(error=f'Cannot claim {pid}: {e}');continue
          if not armed or gen!=generation:break
          if pid not in allowed or version!=versions.get(pid,0) or pid in released:continue
          claimed.add(pid)
         value=pending.pop(pid,value)
         await ws.send(json.dumps({'action':'set','parameter':f'/parameter/by-id/{pid}','value':value}))
       if batch:report(sent=len(batch),work_ms=round((time.perf_counter()-tick)*1000,2))
       # Scope changes are bounded so subscription work cannot flood the output loop.
       stale=[pid for pid,version in subscriptions.items() if pid not in observed or pid not in allowed or version!=versions.get(pid,0)]
       for pid in stale[:32]:
        subscriptions.pop(pid,None);confirmed.discard(pid);samples.pop(pid,None)
        await ws.send(json.dumps({'action':'unsubscribe','parameter':f'/parameter/by-id/{pid}'}))
       if not stale:
        for pid in list((observed&allowed)-subscriptions.keys())[:32]:
         subscriptions[pid]=versions.get(pid,0);confirmed.discard(pid)
         await ws.send(json.dumps({'action':'subscribe','parameter':f'/parameter/by-id/{pid}'}))
       if samples and tick-last_report>=.1:
        items=list(samples.items())[:128]
        report(native_epoch=epoch,native_values=items)
        for pid,value in items:samples.pop(pid,None)
        last_report=tick
       await asyncio.sleep(max(0,1/60-(time.perf_counter()-tick)))
     finally:receiver.cancel();await asyncio.gather(receiver,return_exceptions=True)
   except Exception as e:report(error=str(e))
   connected=False;armed=False;generation+=1;pending.clear();claimed.clear();report(connected=False,armed=False)
   if opened is not None and time.monotonic()-opened>=30:failures=0
   failures+=1
   # A failing handshake resends Arena's large initial catalog. Stop after three
   # attempts; a deliberate Refresh grants a new connection attempt budget.
   if failures>len(RECONNECT_DELAYS):
    reconnect.clear();report(error='Resolume connection paused after 3 failures; use Refresh to retry')
    await reconnect.wait();reconnect.clear();failures=0
   else:await asyncio.sleep(RECONNECT_DELAYS[failures-1])
 transport=os.environ.get('HEART_V2_TRANSPORT','websocket' if os.environ.get('HEART_V2_SOCKET') else 'http')
 await asyncio.gather(commands(),actions(),socket()) if transport=='websocket' else await asyncio.gather(commands(),actions(),http_output(),http_observation())
if __name__=='__main__':asyncio.run(main())
