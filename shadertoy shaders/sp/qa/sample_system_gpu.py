"""Read AGX counters independently of Heart, for controlled UI comparisons."""
import json,plistlib,statistics,subprocess,sys,time
from pathlib import Path
name=sys.argv[1];duration=float(sys.argv[2]) if len(sys.argv)>2 else 30
rows=[];start=time.monotonic()
while time.monotonic()-start<duration:
 data=plistlib.loads(subprocess.check_output(['ioreg','-a','-r','-c','AGXAccelerator']))
 stats=[d['PerformanceStatistics'] for d in data if 'PerformanceStatistics' in d]
 rows.append({'elapsed':time.monotonic()-start,'accelerators':stats})
 time.sleep(1)
values=[s['Device Utilization %'] for r in rows for s in r['accelerators'] if 'Device Utilization %' in s]
summary={'name':name,'seconds':time.monotonic()-start,'samples':len(rows),'median_gpu':statistics.median(values),'min_gpu':min(values),'max_gpu':max(values)}
out=Path(__file__).resolve().parents[1]/'design/heart-performance-plan/performance'
(out/(name+'.json')).write_text(json.dumps({'summary':summary,'rows':rows},indent=2));print(json.dumps(summary))
