"""Temporary bounded diagnostic; forwards existing sends/reads unchanged."""
import asyncio,gc,json,time
from pathlib import Path
OUT=Path('/Users/donovan/work/0000000/shadertoy shaders/sp/heart-v2/checks/motion-jitter')
async def capture_motion_delivery():
 from phase_frames import PhaseFrames
 frames=next(o for o in gc.get_objects() if isinstance(o,PhaseFrames))
 original_emit,original_read=frames.emit,frames.read
 packets=[];reads=[];reports=[];original_report=frames.report
 def emit(packet):
  original_emit(packet)
  if len(packets)<20000:packets.append((time.perf_counter(),frames.frame[0],frames.frame[1],packet.hex()))
 async def read(path):
  started=time.perf_counter();native=await original_read(path);finished=time.perf_counter();values=[]
  for row in (frames.frame[2] if frames.frame else []):
   route=row[2]
   if route.get('read')!=path:continue
   p=native
   for k in route.get('path',[]):p=p.get(k,{}) if isinstance(p,dict) else {}
   values.append((row[0],p.get('value'),p.get('in'),p.get('out')))
  if len(reads)<10000:reads.append((started,finished,path,values))
  return native
 def report(**m):
  original_report(**m)
  if len(reports)<1000:reports.append(m)
 frames.emit,frames.read,frames.report=emit,read,report
 try:await asyncio.sleep(15)
 finally:
  if frames.emit is emit:frames.emit=original_emit
  if frames.read is read:frames.read=original_read
  if frames.report is report:frames.report=original_report
  result=dict(packets=packets,reads=reads,reports=reports)
  await asyncio.to_thread((OUT/'delivery-trace.json').write_text,json.dumps(result))
asyncio.get_running_loop().create_task(capture_motion_delivery())
