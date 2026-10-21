"""Read existing engine timing history; no controls are changed."""
import asyncio,gc,json,time
from pathlib import Path
OUT=Path('/Users/donovan/work/0000000/shadertoy shaders/sp/heart-v2/checks/motion-jitter')
async def capture_engine_timing():
 import __main__
 e=next(o for o in gc.get_objects() if type(o) is __main__.Engine)
 rows=[]
 for n in range(16):
  rows.append(dict(now=time.perf_counter(),gaps=list(e.gaps),work=list(e.work),epoch=e.epoch,owned=list(e.owned),selected=e.selected))
  await asyncio.sleep(1)
 await asyncio.to_thread((OUT/'engine-trace.json').write_text,json.dumps(rows))
asyncio.get_running_loop().create_task(capture_engine_timing())
