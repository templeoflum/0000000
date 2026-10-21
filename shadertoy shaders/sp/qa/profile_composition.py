"""Temporary bypass comparison, restoring every changed value in finally."""
import asyncio,json,subprocess,re,time,urllib.request,statistics
from pathlib import Path
import websockets
B='http://127.0.0.1:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(B+path,timeout=3))
def put(pid,v):
 r=urllib.request.Request(B+f'/parameter/by-id/{pid}',data=json.dumps({'value':v}).encode(),method='PUT',headers={'Content-Type':'application/json'})
 urllib.request.urlopen(r,timeout=3).read()
def gpu():
 s=subprocess.check_output(['ioreg','-r','-c','AGXAccelerator','-l'],text=True)
 return {k:int(v) for k,v in re.findall(r'"(Device Utilization %|Renderer Utilization %|In use system memory)"=(\d+)',s)}
async def main():
 out=Path(__file__).resolve().parents[1]/'audit/20260907-070411'
 comp=get('/composition');conditions=[]
 for l in comp['layers']:
  for c in l['clips']:
   if 'Connected' not in str(c['connected']['value']):continue
   for e in (c.get('video') or {}).get('effects',[]):
    if e['name'] in ['SPDelayChain','Blur','Sharpen'] and 'id' in e.get('bypassed',{}):conditions.append((e['name'],e['bypassed']['id'],e['bypassed']['value']))
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  state=json.loads(await ws.recv());old_hold=state.get('hold',False);await ws.send(json.dumps({'cmd':'hold','on':True}))
  results=[]
  try:
   for name,pid,old in [('baseline',None,None)]+conditions+[('baseline-repeat',None,None)]:
    if pid:put(pid,True)
    await asyncio.sleep(1)
    samples=[]
    for _ in range(6):samples.append(gpu());await asyncio.sleep(.5)
    results.append({'condition':name,'samples':samples,'median_gpu_percent':statistics.median(x.get('Device Utilization %',0) for x in samples)})
    print(name,results[-1]['median_gpu_percent'],flush=True)
    if pid:put(pid,old)
  finally:
   for _,pid,old in conditions:put(pid,old)
   await ws.send(json.dumps({'cmd':'hold','on':old_hold}))
   (out/'composition-gpu.json').write_text(json.dumps({'note':'System-wide GPU utilization, not per-shader GPU time or Arena FPS; motion held across comparison','results':results},indent=2))
   for _,pid,old in conditions:assert get(f'/parameter/by-id/{pid}')['value']==old
   print('Bypass values restored and verified',flush=True)
if __name__=='__main__':asyncio.run(main())
