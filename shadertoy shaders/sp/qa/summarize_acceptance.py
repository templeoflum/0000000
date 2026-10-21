"""Keep overall acquisition results and intentional patch-transition windows separate."""
import json,statistics
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'design/heart-performance-plan/performance'
j=json.loads((p/'feedback-checked-sustained.json').read_text());actions=json.loads((p/'action-exercise.json').read_text());rows=j['rows']
transitions=[];begin=None
for a in actions:
 c=a.get('command',{})
 if c.get('cmd')=='patch_recall':begin=a['time']
 elif a.get('operation')=='patch_recall' and begin is not None:
  transitions.append((begin,a['time']+2));begin=None
stable=[r for r in rows if not any(a<=r['monitor']['timestamp']<=b for a,b in transitions)]
def stats(rs):
 iv=sorted(v for r in rs for v in r['monitor'].get('intervals_ms',[]));fps=[r['monitor']['fps'] for r in rs]
 return {'seconds_sampled':len(rs),'median_acquisition_fps':statistics.median(fps) if fps else None,'minimum_one_second_fps':min(fps) if fps else None,'samples_under_55_fps':sum(f<55 for f in fps),'p95_interval_ms':iv[min(len(iv)-1,int(len(iv)*.95))] if iv else None,'intervals_over_100ms':sum(v>100 for v in iv),'not_visible':sum(not r['monitor'].get('visible') for r in rs),'stale_telemetry':sum(r['age_seconds']>3 for r in rs),'dimensions':sorted({(r['monitor'].get('width'),r['monitor'].get('height')) for r in rs}),'max_delivery_age_ms':max((r['engine'].get('delivery') or {}).get('max_pending_age_ms',0) for r in rs) if rs else None,'max_pending_targets':max((r['engine'].get('delivery') or {}).get('pending',0) for r in rs) if rs else None}
summary={'overall':stats(rows),'outside_documented_recalls_plus_two_seconds':stats(stable),'recall_windows':transitions,'exercise_results':[a for a in actions if 'result' in a],'method':'Syphon acquisition, not presentation. Recall exclusion is disclosed; overall results retained. This is a scripted action-path exercise, not GUI/trackpad/focus acceptance.'}
(p/'acceptance-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
