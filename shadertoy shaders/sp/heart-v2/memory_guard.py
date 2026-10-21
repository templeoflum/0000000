"""Read Arena's macOS physical footprint without querying its API."""
import argparse,ctypes,datetime,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GIB=1024**3
class Usage(ctypes.Structure):
 _fields_=[('uuid',ctypes.c_uint8*16)]+[(name,ctypes.c_uint64) for name in ('user','system','wakeups','interrupts','pageins','wired','resident','footprint','start','exit')]
def footprint(pid):
 lib=ctypes.CDLL('/usr/lib/libproc.dylib',use_errno=True)
 lib.proc_pid_rusage.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p]
 lib.proc_pid_rusage.restype=ctypes.c_int
 usage=Usage()
 if lib.proc_pid_rusage(pid,0,ctypes.byref(usage)):
  raise OSError(ctypes.get_errno(),'Cannot read process memory')
 return usage.footprint
def severity(size,warn=40,pause=64):return 'pause' if size>=pause*GIB else 'warning' if size>=warn*GIB else 'normal'
def atomic(path,value):
 temporary=path.with_name(path.name+'.tmp');temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(path)
def notify(message):
 subprocess.run(['osascript','-e','on run argv\ndisplay notification (item 1 of argv) with title "Resolume memory" sound name "Glass"\nend run',message],capture_output=True,timeout=5)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');parser.add_argument('--warn-gib',type=float,default=40);parser.add_argument('--pause-gib',type=float,default=64);args=parser.parse_args()
 if not 0<args.warn_gib<args.pause_gib:parser.error('Require 0 < warning < pause threshold')
 import fcntl
 lock=(ROOT/'memory-guard.lock').open('w')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise SystemExit('Memory guard is already running')
 last=None
 while True:
  try:
   result=subprocess.run(['pgrep','-x','Arena'],capture_output=True,text=True,timeout=3)
   pids=[int(x) for x in result.stdout.split()]
   if not pids:row={'status':'not_running'}
   else:
    pid,size=max(((pid,footprint(pid)) for pid in pids),key=lambda x:x[1]);level=severity(size,args.warn_gib,args.pause_gib)
    row={'status':level,'pid':pid,'footprint_bytes':size,'footprint_gib':round(size/GIB,2),'warn_gib':args.warn_gib,'pause_gib':args.pause_gib}
    key=(pid,level)
    if level=='pause' and not (ROOT/'api-paused.json').exists():
     atomic(ROOT/'api-paused.json',{'reason':f'Resolume physical memory reached {size/GIB:.1f} GiB; Heart traffic paused by memory guard.','at':datetime.datetime.now().astimezone().isoformat()})
    if key!=last and level in ('warning','pause'):
     message=f'Resolume memory: {size/GIB:.1f} GB. '+('Heart traffic paused. Resolume remains running.' if level=='pause' else 'Memory is high. Save your work and check the running content.')
     try:notify(message)
     except (OSError,subprocess.SubprocessError):pass
    last=key
  except (OSError,ValueError,subprocess.SubprocessError) as ex:row={'status':'unavailable','error':str(ex)}
  row['at']=datetime.datetime.now().astimezone().isoformat();atomic(ROOT/'arena-memory.json',row)
  print(json.dumps(row),flush=True)
  if args.once:return
  time.sleep(5)
if __name__=='__main__':main()
