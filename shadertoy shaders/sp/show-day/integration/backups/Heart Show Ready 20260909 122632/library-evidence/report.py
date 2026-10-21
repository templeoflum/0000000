"""Join control evidence and actual-render review without claiming full certification."""
import json,collections
from pathlib import Path
P=Path(__file__).resolve().parent
inventory=json.loads((P/'inventory.json').read_text());results=json.loads((P/'results.json').read_text());visual=json.loads((P/'visual-review.json').read_text()) if (P/'visual-review.json').exists() else {}
repairs={f"L{r['layer']}C{r['col']}":r for r in json.loads((P/'repairs.json').read_text())}
counts=dict(collections.Counter(r['status'] for r in results));rows=[]
for r in results:
 key=f"L{r['layer']}C{r['col']}";v=visual.get(key)
 repair=repairs.get(key)
 rows.append(dict(r,source=repair.get('source',r['source']) if repair else r['source'],repair=repair,visual=v or {'status':'awaiting review'}))
summary=dict(run_entries=len(results),planned_entries=sum('status' not in r for r in inventory['rows']),remaining_entries=max(0,sum('status' not in r for r in inventory['rows'])-len(results)),previously_checked=sum(r.get('status')=='previously checked' for r in inventory['rows']),duplicate_schemas=sum(r.get('status')=='duplicate schema' for r in inventory['rows']),routing_entries=len(inventory['routing']),glyph='deferred per user',control_results=counts,actual_render_reviews=sum(f"L{r['layer']}C{r['col']}" in visual for r in results),limits='Brief sampled output and accelerated control/recovery checks. No sustained smoothness, full-range, or Figure pre-effect containment certification.')
(P/'summary.json').write_text(json.dumps(summary,indent=2));(P/'combined-results.json').write_text(json.dumps(rows,indent=2))
lines=['# Existing library — continuous pass','',f"{len(results)} current-run entries, {summary['actual_render_reviews']} rendered pairs reviewed. {summary['previously_checked']} previously checked representatives and {summary['duplicate_schemas']} duplicate schemas listed separately. Routing stays under its separate rehearsal; Glyph deferred.",'', 'Control results: '+', '.join(f'{v} {k}' for k,v in counts.items())+'.','',summary['limits'],'','| Layer / clip | Source | Controls | Render review |','|---|---|---|---|']
for r in rows:
 v=r['visual'];review=' / '.join(v.get(p,'pending') for p in ('home','shuffle'))
 lines.append(f"| L{r['layer']} C{r['col']} | {r['source'].replace('|','/')} | {r['status']} | {review} |")
(P/'README.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))
