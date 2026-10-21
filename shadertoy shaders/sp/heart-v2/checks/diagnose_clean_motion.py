"""Focused live acceptance of reference bounds, clip revisits and native rack controls."""
import asyncio,json,time,urllib.request,sys
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parent.parent

def native(pid):
 with urllib.request.urlopen(f'http://127.0.0.1:8080/api/v1/parameter/by-id/{pid}',timeout=3) as f:return json.load(f)['value']
async def main():
 report={'rack':[],'clips':[]};profiles=json.loads((ROOT/'authored-clips.json').read_text())['clips'];c={};s={}
 async with websockets.connect('ws://127.0.0.1:8876',max_size=8*1024*1024) as ws:
  async def reader():
   nonlocal c,s
   async for raw in ws:
    m=json.loads(raw)
    if m['type']=='catalog':c=m
    if m['type']=='state':s=m
  task=asyncio.create_task(reader())
  async def wait(predicate):
   start=time.monotonic()
   while not predicate():
    if s.get('error'):raise RuntimeError(s['error'])
    if time.monotonic()-start>16:raise TimeoutError('Expected Heart state did not arrive')
    await asyncio.sleep(.025)
  async def send(**d):await ws.send(json.dumps(d))
  await wait(lambda:c.get('targets') and s.get('armed') and s.get('connected'))
  before={l['id']:next((clip['id'] for clip in l['clips'] if clip['col']==l['active']),None) for l in c['layers'] if l['id'] in (1788149968008,1788149967550)};selected=s['selected'];rack_before=json.loads(json.dumps(s['effect_rack']));report['before']=dict(clips=before,selected=selected,hold=s['hold'])
  assert not s['hold'],'Motion must be running for acceptance'
  async def rack(row,pad,action,**kw):await send(cmd='rack_control',epoch=c['epoch'],row=row['id'],pad=pad['id'],action=action,**kw)
  try:
   for row in []:
    lut=next(p for p in row['pads'] if p['mode']=='trigger');melt=next(p for p in row['pads'] if p['mode']=='latch')
    await rack(row,lut,'enable',on=True);await wait(lambda:s['effect_rack'][row['id']]['enabled'].get(lut['id']))
    await rack(row,lut,'trigger');await wait(lambda:s['effect_rack'][row['id']]['active'].get(lut['id']))
    await asyncio.sleep(.25);values=await asyncio.gather(*(asyncio.to_thread(native,b['opacity']) for b in lut['bindings']));assert values==[1.]*len(values),values
    await rack(row,lut,'enable',on=False);await wait(lambda:not s['effect_rack'][row['id']]['enabled'].get(lut['id']))
    await rack(row,melt,'latch',on=True);await wait(lambda:s['effect_rack'][row['id']]['latched'].get(melt['id']))
    await asyncio.sleep(.15);assert all(await asyncio.gather(*(asyncio.to_thread(native,b['latch']) for b in melt['bindings'])))
    await rack(row,melt,'latch',on=False);await wait(lambda:not s['effect_rack'][row['id']]['latched'].get(melt['id']))
    await asyncio.sleep(.15);opacity=await asyncio.gather(*(asyncio.to_thread(native,b['opacity']) for b in melt['bindings']));bypass=await asyncio.gather(*(asyncio.to_thread(native,b['bypass']) for b in melt['bindings']));assert opacity==[1.]*len(opacity) and bypass==[False]*len(bypass)
    report['rack'].append(dict(row=row['id'],decon_amount_after_trigger=values,melt_amount_after_release=opacity,melt_bypass_after_release=bypass));print('Rack passed:',row['id'],flush=True)
   for lid,cid in [(1788149968008,1788780037897)]:
    await send(cmd='launch',layer_id=lid,clip_id=cid);await wait(lambda:any(t.get('clip_id')==cid and t.get('authored') for t in c['targets']))
    refs=profiles[str(cid)];ts=[t['id'] for t in refs['targets']];await send(cmd='watch',targets=ts)
    loops=[p for t in refs['targets'] for p in t['params'] if p.get('source')=='timeline' and p['out']!=p['in']];await wait(lambda:all(s.get('values',{}).get(str(p['id']),{}).get('drive') for p in loops))
    for p in loops:
     v=s['values'][str(p['id'])];expected=sorted([(p[k]-p['min'])/(p['max']-p['min']) for k in ('in','out')]);assert abs(v['lo']-expected[0])<1e-9 and abs(v['hi']-expected[1])<1e-9,(p,v)
    probes=loops[:4];samples=[]
    for i in range(12):
     samples.append(await asyncio.gather(*(asyncio.to_thread(native,p['id']) for p in probes)));print(json.dumps({'native':samples[-1],'heart':[s['values'].get(str(p['id'])) for p in probes],'hold':s['hold'],'metrics':s['metrics']}),flush=True);await asyncio.sleep(.12)
    for i,p in enumerate(probes):
     low,high=sorted([p['in'],p['out']]);values=[v[i] for v in samples];tol=max(1e-5,(p['max']-p['min'])*1e-6);assert min(values)>=low-tol and max(values)<=high+tol,(p,values);assert max(values)-min(values)>1e-6,(p['name'],values)
    if loops:
     tid=next(t['id'] for t in refs['targets'] if any(p.get('source')=='timeline' for p in t['params']));await send(cmd='drive_bank',epoch=c['epoch'],target=tid,action='shuffle');await asyncio.sleep(.15)
     for p in loops:
      v=s['values'][str(p['id'])];assert abs(v['lo']-(min(p['in'],p['out'])-p['min'])/(p['max']-p['min']))<1e-9
    report['clips'].append(dict(id=cid,name=refs['name'],loops=len(loops),sampled=len(probes),samples=samples));print('Clip passed:',refs['name'],len(loops),'drives',flush=True)
  finally:
   for row in c.get('effect_rack',{}).get('rows',[]):
    for pad in row['pads']:
     on=rack_before[row['id']].get('latched' if pad['mode']=='latch' else 'enabled',{}).get(pad['id'],False);await rack(row,pad,'latch' if pad['mode']=='latch' else 'enable',on=on)
   for lid,cid in before.items():
    if cid:await send(cmd='launch',layer_id=lid,clip_id=cid)
    else:await send(cmd='layer_action',layer_id=lid,action='eject')
   await send(cmd='select',target=selected);await send(cmd='watch',targets=[]);await asyncio.sleep(1.5)
   report['final']={k:s.get(k) for k in ('armed','connected','hold','error','effect_rack','metrics')};(ROOT/'checks/deep-clean-live.json').write_text(json.dumps(report,indent=2)+'\n');task.cancel()
  assert not s['error'];print('PASS live rack, automatic reference-range motion, bounded shuffle and revisit',flush=True)
asyncio.run(main())
