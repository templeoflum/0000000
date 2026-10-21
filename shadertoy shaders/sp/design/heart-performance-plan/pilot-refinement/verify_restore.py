import json,sys
from pathlib import Path
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
before=json.loads((p/'before.json').read_text());after=json.loads((p/'restored.json').read_text())
keys=('drive','ratio','mult','offset','shape','lo','hi','lock','cyc')
def targets(s):
 out={}
 for c in s['clips']:
  out[f"source/{c['layer']}/{c['col']}"]=c
 for e in s['fx']:
  if e.get('motion') and any(x['drive'] for x in e['motion']['slots']):out[e['key']]=e['motion']
 return {k:{'g':v.get('g'), 'slots':{x['name']:{n:x.get(n) for n in keys} for x in v['slots']}} for k,v in out.items()}
b,a=targets(before),targets(after)
errors=[k for k in b if b[k]!=a.get(k)]
result={'relationships_match':not errors,'mismatched_targets':errors,'source_targets':len(before['clips']),'driven_effect_targets':len(b)-len(before['clips']),'tempo_before':before['bpm'],'tempo_after':after['bpm'],'hold_match':before['hold']==after['hold']}
(p/'restore-comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
