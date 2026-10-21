"""Read-only Portal video candidate inventory. Never moves files or edits compositions."""
from pathlib import Path
import collections,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'restored-compositions'
comp=out/'portal.avc';root=ET.parse(comp).getroot()
exts={'.mov','.mp4','.m4v','.avi','.mkv','.webm','.mpg','.mpeg'}
refs=collections.defaultdict(list)
def norm(s):return re.sub('/+','/',s.replace('\\','/')).lstrip('/').lower()
for e in root.iter():
 for k,v in e.attrib.items():
  if Path(v.replace('\\','/')).suffix.lower() in exts and ('/' in v or '\\' in v):
   key=norm(v)
   if v not in refs[key]:refs[key].append(v)
files=sorted({str(Path(x).resolve()) for x in Path('/tmp/portal-local-videos.txt').read_text().splitlines() if Path(x).is_file()})
byname=collections.defaultdict(list);bystem=collections.defaultdict(list)
for f in files:byname[Path(f).name.lower()].append(f);bystem[Path(f).stem.lower()].append(f)
rows=[]
for key,original in sorted(refs.items()):
 name=key.split('/')[-1];candidates=byname[name];scored=[]
 for f in candidates:
  a=key.split('/')[::-1];b=norm(f).split('/')[::-1];n=0
  for x,y in zip(a,b):
   if x!=y:break
   n+=1
  scored.append((n,f))
 top=max((s for s,f in scored),default=0);best=[f for s,f in scored if s==top]
 if top>=3 and len(best)==1:status='folder_match'
 elif top>=2 and len(best)==1:status='parent_folder_candidate'
 elif len(best)==1:status='filename_only_candidate'
 elif best:status='ambiguous'
 else:
  best=bystem[Path(name).stem.lower()];status='different_extension_candidate' if best else 'not_found'
 category=key.split('/videos/',1)[-1].split('/')[0]
 rows.append({'original_paths':original,'category':category,'filename':name,'status':status,'matching_suffix_components':top,'candidates':best,'candidate_sizes':{f:Path(f).stat().st_size for f in best}})
report={'composition':str(comp),'searched_roots':['Movies','work','Documents','Downloads','Desktop'],'mounted_volumes':['Macintosh HD'],'local_videos_scanned':len(files),'unique_referenced_videos':len(rows),'counts':dict(collections.Counter(r['status'] for r in rows)),'rows':rows,'limits':'Path/name candidates only; source originals were on Windows. No checksum or playback identity proof, no files moved, no composition edits. Unmounted drives and other computers were not searchable.'}
(out/'portal-video-candidates.json').write_text(json.dumps(report,indent=2))
lines=['# Portal video search','',f"Found {len(rows)} distinct video references; searched {len(files)} local video files.",'','No video files moved or composition paths changed. Folder matches preserve at least two enclosing folder names plus filename. Other matches require review. Only Macintosh HD was mounted.','', '| Result | Count |','|---|---:|']
lines += [f'| {k} | {v} |' for k,v in report['counts'].items()]
lines += ['', '## Original library folders', '', '| Folder | References | Folder matches | Other candidates | Not found |','|---|---:|---:|---:|---:|']
for cat in sorted({r['category'] for r in rows}):
 rr=[r for r in rows if r['category']==cat];lines.append(f"| {cat} | {len(rr)} | {sum(r['status']=='folder_match' for r in rr)} | {sum(r['status'] not in ['folder_match','not_found'] for r in rr)} | {sum(r['status']=='not_found' for r in rr)} |")
lines += ['', '## Located files and candidates', '']
for r in rows:
 if r['status']=='not_found':continue
 lines += [f"- **{r['filename']}** — {r['status']}; original: `{r['original_paths'][0]}`"]
 lines += [f'  - `{f}`' for f in r['candidates']]
lines += ['', 'Full unresolved list and candidate details: portal-video-candidates.json.']
(out/'Portal video search.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:report[k] for k in ['local_videos_scanned','unique_referenced_videos','counts']}))
for r in [r for r in rows if r['status']=='folder_match'][:8]:print(r['original_paths'][0],'=>',r['candidates'][0])
