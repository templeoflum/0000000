import asyncio,json,urllib.request
from pathlib import Path
import websockets
P=Path(__file__).parent;B='http://localhost:8080/api/v1'
def req(path,method='GET',body=None):
 raw=None if body is None else body.encode();r=urllib.request.urlopen(urllib.request.Request(B+path,data=raw,method=method,headers={'Content-Type':'text/plain'}),timeout=6);data=r.read();return json.loads(data) if data else None
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  s=json.loads(await w.recv());P.joinpath('before-heart.json').write_text(json.dumps(s));fx={f['key']:f for f in s['fx']};f=fx['layer/figure~1/effect/LinearCloner~1'];c=req('/composition');l=c['layers'][4];col=next(i+1 for i,x in enumerate(l['clips']) if not x.get('video') and not x.get('audio'));old=next(x['col'] for x in s['clips'] if x['layer']==5)
  async def drain():
   async for _ in w:pass
  task=asyncio.create_task(drain())
  async def send(cmd,**kw):await w.send(json.dumps(dict(cmd=cmd,**kw)))
  async def params(effect,vals):
   for name,value in vals.items():await send('fx_param',key=effect['key'],instance=effect['instance'],name=name,value=value)
  try:
   await send('hold',on=True)
   for x in s['layers']:await send('opacity',layer=x['i'],value=1 if x['i']==5 else 0)
   for e in s['fx']:
    if e.get('has_amount') and (e['scope']=='C' or e['layer']==5):await send('fx_amount',key=e['key'],instance=e['instance'],value=1 if e['key']==f['key'] else 0)
   for e in s['fx']:
    if e['scope']=='L' and e['layer']==5 and '/effect/Transform~' in e['key']:await params(e,{'Position X':0,'Position Y':0,'Scale':100,'Scale W':100,'Scale H':100,'Rotation X':0,'Rotation Y':0,'Rotation Z':0,'Anchor X':0,'Anchor Y':0,'Anchor Z':0})
   path=f'/composition/layers/5/clips/{col}';req(path+'/open','POST',P.joinpath('anchor.png').resolve().as_uri());req(path+'/connect','POST','')
   await params(f,{'Clones':1,'Tails':1,'Center':0,'Tail Length':.5,'Start Scale':100,'End Scale':100,'Start Rotation':0,'End Rotation':0,'Distribution':50,'Distortion':0,'Tail Rotation':0,'Master Rotation':0,'Delay Enabled':False});await asyncio.sleep(2)
   cases=[{'Center':c,'Tail Length':t,'Clones':n,'Master Rotation':r} for c,t,n,r in [(0,.5,1,0),(.5,.5,1,0),(-.5,.5,1,0),(0,1,1,0),(.5,1,1,0),(0,.5,7,0),(.5,.5,7,0),(-.5,.5,7,0),(.5,.5,7,90)]]
   for i,case in enumerate(cases):
    await params(f,case);await asyncio.sleep(.5);P.joinpath(f'{i}.png').write_bytes(urllib.request.urlopen(B+'/composition/monitors/1/snapshot.png',timeout=6).read());print(i,case,flush=True)
   P.joinpath('cases.json').write_text(json.dumps(cases,indent=2))
  finally:
   req(f'/composition/layers/5/clips/{old}/connect','POST','');req(f'/composition/layers/5/clips/{col}/clear','POST','');await params(f,{'Center':0,'Tail Length':.5,'Clones':7,'Master Rotation':0,'Start Scale':80,'End Scale':45});await send('hold',on=False);task.cancel()
asyncio.run(main())
