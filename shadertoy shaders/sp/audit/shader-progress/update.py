"""Publish audited progress; no access to Resolume and no invented completion."""
import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'engine/progress.json'
def publish(message=None,phase=None,record=None):
 try:old=json.loads(OUT.read_text())
 except (OSError,ValueError):old={}
 ledger=json.loads((ROOT/'audit/shader-coverage-batch1/coverage.json').read_text())
 overrides=old.get('overrides',{})
 if record:overrides[record['id']]=record
 rows=[]
 for r in ledger['clips']:
  key=f"D{r['deck']} L{r['layer']}C{r['col']}";status=r['rendered_status'];sampled=status.startswith('batch')
  row=dict(id=key,source=r['source'],layer=r['layer'],controls=len(r['controls']),enrolled=bool(r['heart_registered'] or r.get('enrolled_now')),sampled=sampled,status='Sampled' if sampled else 'Untested',note=status if sampled else 'No rendered check in this coverage run')
  row.update(overrides.get(key,{}));rows.append(row)
 now=datetime.now(timezone.utc).isoformat();events=old.get('events',[])
 if message:events.insert(0,dict(at=now,text=message))
 data=dict(updated=now,phase=phase or old.get('phase','Working'),current=message or old.get('current','Preparing checks'),events=events[:30],overrides=overrides,rows=rows,issues=['Routine-rescan queue loss repaired: 149/156 before, 156/156 after. Narrow-range drive startup repaired: 40/40 live samples in range; 220 tests pass.','Enrollment exposes controls; it does not certify shader behavior or Figure containment.','Source boolean, trigger and color exposure is incomplete.'],scope=f'{len(rows)} populated clips across all three decks. Includes routers and repeated sources. Rendered samples include flagged candidates; sampling is not exhaustive acceptance.')
 board=ROOT/'show-day/roadmap.json'
 if board.exists():data['roadmap']=json.loads(board.read_text())
 tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));os.replace(tmp,OUT)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('message');a.add_argument('--phase');a.add_argument('--record');p=a.parse_args();publish(p.message,p.phase,json.loads(p.record) if p.record else None)
