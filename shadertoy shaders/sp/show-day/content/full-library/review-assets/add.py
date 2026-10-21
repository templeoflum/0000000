import json,sys
from pathlib import Path
p=Path(__file__).resolve().parent.parent
r=json.loads((p/'visual-review.json').read_text()); rows={f"L{x['layer']}C{x['col']}":x for x in json.loads((p/'results.json').read_text())}
for line in sys.stdin:
 k,h,s,n=line.rstrip().split('|',3)
 r[k]={'source':rows[k]['source'],'home':h,'shuffle':s,'notes':n,'figure_pre_effect_containment':'not certified from composite renders'}
(p/'visual-review.json').write_text(json.dumps(r,indent=2)+'\n')
