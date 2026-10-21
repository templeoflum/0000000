"""Bounded comparison of current XML against existing recorded paths only."""
from pathlib import Path
from collections import Counter
import json, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]/'restored-compositions'
report=json.loads((BASE/'video-relink-report.json').read_text())
rows=json.loads((BASE/'portal-video-candidates.json').read_text())['rows']
def norm(s):return s.replace('\\','/').lstrip('/').casefold()
lookup={norm(p):r for r in rows for p in r['original_paths']}
refs=[]
for n in ET.parse(BASE/'portal.avc').getroot().iter():
    for k,v in n.attrib.items():
        if (k=='fileName' or (n.tag=='VideoFile' and k=='value')) and Path(v).suffix.lower() in ('.mov','.mp4','.avi','.mkv','.m4v'):
            refs.append({'tag':n.tag,'attribute':k,'path':v,'exists':Path(v).exists()})
missing={r['path'] for r in refs if not r['exists']}
items=[]
for p in sorted(missing):
    row=lookup.get(norm(p));target=report['changes'].get(p)
    candidates=row.get('candidates',[]) if row else []
    suffix=p.replace('\\','/').split('/Videos/',1)[-1]
    mirrors=[Path('/Users/donovan/work/Visuals')/suffix]
    if suffix.lower().startswith('visuals/'):
        mirrors.append(Path('/Users/donovan/work/Visuals')/suffix.split('/',1)[1])
    items.append({'path':p,'historical_status':row['status'] if row else 'unmatched','filename':row.get('filename') if row else None,'recorded_relink_target':target,'recorded_target_exists':Path(target).exists() if target else None,'candidates':[{'path':c,'exists':Path(c).exists()} for c in candidates], 'bounded_mirror_checks':[{'path':str(c),'exists':c.exists()} for c in mirrors]})
actual={r['path'] for r in refs}
linked_targets=set(report['changes'].values())
data={'scope':'Only current Portal VideoFile/value and fileName video references, recorded relink destinations and recorded candidate paths. No disk scan or playback.','occurrences':len(refs),'missing_occurrences':sum(not r['exists'] for r in refs),'unique_literal_missing_paths':len(missing),'unique_normalized_missing_paths':len({norm(p) for p in missing}),'missing_by_historical_status':dict(Counter(i['historical_status'] for i in items)),'missing_video_identities_by_status':dict(Counter({i['filename']:i['historical_status'] for i in items}.values())),'recorded_linked_target_count':len(linked_targets),'recorded_linked_targets_missing':[p for p in sorted(linked_targets) if not Path(p).exists()],'recorded_linked_targets_absent_from_xml':sorted(linked_targets-actual),'missing_references_with_recorded_relink':[i for i in items if i['recorded_relink_target']],'missing':items}
(HERE/'PORTAL-RECONCILIATION.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k!='missing'},indent=2))
