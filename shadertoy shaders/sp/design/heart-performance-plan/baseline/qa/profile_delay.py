import asyncio,json,time,statistics,urllib.request
from pathlib import Path
import websockets
from profile_composition import gpu,get
B='http://127.0.0.1:8080/api/v1'
def connect(col):urllib.request.urlopen(urllib.request.Request(B+f'/composition/layers/4/clips/{col}/connect',data=b'',method='POST'),timeout=3).read()
async def main():
 comp=get('/composition');playing=[i+1 for i,c in enumerate(comp['layers'][3]['clips']) if 'Connected' in str(c['connected']['value'])]
 if playing!=[1]:raise RuntimeError('Delay layer changed; comparison skipped to preserve current work')
 rows=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  initial=json.loads(await ws.recv());old_hold=initial.get('hold',False)
  await ws.send(json.dumps({'cmd':'hold','on':True}))
  try:
   for col,label in [(1,'original'),(12,'half-resolution-history')]:
    connect(col);await asyncio.sleep(10)
    samples=[]
    for _ in range(8):samples.append(gpu());await asyncio.sleep(.5)
    row={'case':label,'samples':samples,'median_gpu_percent':statistics.median(s['Device Utilization %'] for s in samples),'median_system_memory':statistics.median(s['In use system memory'] for s in samples)};rows.append(row);print(label,row['median_gpu_percent'],row['median_system_memory'],flush=True)
  finally:
   connect(1);await ws.send(json.dumps({'cmd':'hold','on':old_hold}))
   Path(__file__).resolve().parents[1].joinpath('audit/20260907-070411/delay-comparison.json').write_text(json.dumps(rows,indent=2));print('Original delay restored',flush=True)
asyncio.run(main())
