import asyncio,json,sys
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from catalog_updates import apply_patch
async def read():
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  c=None;wanted=set();s=None
  await ws.send(json.dumps(dict(cmd='client_capabilities',catalog_patches=True)))
  async with asyncio.timeout(15):
   while True:
    m=json.loads(await ws.recv())
    if m['type']=='catalog':c=m
    elif m['type']=='catalog_patch' and c:c=apply_patch(c,m['patch'])
    elif m['type']=='state':s=m
    if not c:continue
    targets={t['id'] for t in c['targets'] if any(p.get('native_phase') for p in t['params'])}
    if targets!=wanted:
     wanted=targets;await ws.send(json.dumps(dict(cmd='watch',targets=sorted(targets),native_ids=[])))
    pids={str(p['id']) for t in c['targets'] if t['id'] in targets for p in t['params']}
    if s and pids.issubset(s['values']) and targets.issubset(s['groups']):break
  (Path(__file__).parent/'current-heart.json').write_text(json.dumps(dict(catalog=c,state=s)))
  print(json.dumps(dict(armed=s['armed'],selected=s['selected'],groups={k:g for k,g in s['groups'].items() if k in targets},stage=s['stage_motion'],scopes=s['motion_multipliers'],prepared=sum(v.get('native_phase',False) for v in s['values'].values()),nondefault=sum(v.get('motion',{}).get('ratio','1:1')!='1:1' for v in s['values'].values() if v.get('motion')),error=s['error'])))
asyncio.run(read())
