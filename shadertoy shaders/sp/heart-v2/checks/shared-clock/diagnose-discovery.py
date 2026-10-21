import asyncio,json,urllib.request,copy
from pathlib import Path
import websockets,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scan import refresh_active,read_active
async def main():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  while True:
   m=json.loads(await ws.recv())
   if m['type']=='catalog':c=m;break
 l=next(l for l in c['layers'] if l.get('stage') and l['active'])
 lid,clip=await asyncio.to_thread(read_active,l);r=refresh_active(c,{lid:clip})
 def structure(t):return dict({k:v for k,v in t.items() if k not in ('params','authored','native_phase_clip')},params=[{k:v for k,v in p.items() if k not in ('value','in','out','authored','native_phase','animation','_phase_checked')} for p in t['params']])
 old={t['id']:structure(t) for t in c['targets'] if t.get('scope')=='clip' and t.get('layer_id')==lid};new={t['id']:structure(t) for t in r['targets'] if t.get('scope')=='clip' and t.get('layer_id')==lid}
 (Path(__file__).parent/'discovery-diff.json').write_text(json.dumps(dict(old=old,new=new,layer=l,changed=r.get('_changed')),indent=2))
 for tid in old.keys()|new.keys():
  a,b=old.get(tid,{}),new.get(tid,{})
  for k in a.keys()|b.keys():
   if a.get(k)!=b.get(k):print(tid,k,json.dumps(a.get(k)),json.dumps(b.get(k)))
 print('changed',r.get('_changed'),'targets',len(old),len(new),'active',l['active'])
asyncio.run(main())
