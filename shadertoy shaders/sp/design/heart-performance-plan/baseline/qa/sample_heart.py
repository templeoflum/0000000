import asyncio,json,sys,statistics
from pathlib import Path
import websockets
async def main():
 rows=[]
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  for _ in range(150):rows.append(json.loads(await ws.recv()))
 out=Path(sys.argv[1]);out.write_text(json.dumps(rows,indent=1))
 for k in ('fps','worst','queue'):
  vals=[r[k] for r in rows];print(k,min(vals),statistics.median(vals),max(vals))
 print('delivery',rows[-1].get('delivery'));out.with_suffix('.last.json').write_text(json.dumps(rows[-1],indent=2))
asyncio.run(main())
