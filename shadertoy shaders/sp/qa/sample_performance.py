"""Read-only native acquisition and engine sample; no composition mutations."""
import asyncio,json,time,statistics,sys
from pathlib import Path
import websockets
ROOT=Path(__file__).resolve().parents[1]
async def main():
 name=sys.argv[1];duration=float(sys.argv[2]) if len(sys.argv)>2 else 60
 rows=[];seen=set();latest={};start=time.monotonic()
 async with websockets.connect('ws://127.0.0.1:8766') as ws:
  while time.monotonic()-start<duration:
   latest=json.loads(await asyncio.wait_for(ws.recv(),3))
   try:t=json.loads((ROOT/'monitor/telemetry.json').read_text())
   except (OSError,ValueError):continue
   stamp=t.get('timestamp')
   if stamp in seen:continue
   seen.add(stamp)
   rows.append({'monitor':t,'engine':{k:latest.get(k) for k in ('fps','worst','queue','delivery','arena_connected','hold','bars')},'clips':[(c['layer'],c['col'],c['name']) for c in latest.get('clips',[])],'age_seconds':time.time()-stamp})
 fps=[r['monitor']['fps'] for r in rows];intervals=sorted(v for r in rows for v in r['monitor'].get('intervals_ms',[]))
 summary={'sample':name,'seconds':time.monotonic()-start,'samples':len(rows),'median_fps':statistics.median(fps) if fps else None,'p95_frame_ms':intervals[min(len(intervals)-1,int(len(intervals)*.95))] if intervals else None,'intervals_over_100ms':sum(x>100 for x in intervals),'all_visible':all(r['monitor'].get('visible') for r in rows),'all_1080p':all((r['monitor'].get('width'),r['monitor'].get('height'))==(1920,1080) for r in rows),'stale_samples':sum(r['age_seconds']>3 for r in rows),'method':'Heart Syphon acquisition, not Arena presentation; GPU percentage is system-wide'}
 path=ROOT/'design/heart-performance-plan/performance';path.mkdir(exist_ok=True);(path/(name+'.json')).write_text(json.dumps({'summary':summary,'rows':rows},indent=2));print(json.dumps(summary),flush=True)
asyncio.run(main())
