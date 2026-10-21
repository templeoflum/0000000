"""Create a fresh local recovery snapshot only after verified departure save."""
import json,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3];E=ROOT/'sp/engine'
r=json.loads((P/'departure-verified.json').read_text());dest=P.parent/'backups'/r['name'];dest.mkdir(parents=True,exist_ok=False)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,rel):
 target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
 for _ in range(3):
  before=digest(p);shutil.copy2(p,target)
  if digest(p)==before==digest(target):return
 raise RuntimeError('Changed during copy: '+str(p))
for f in [Path(r['avc']),Path(r['avc']).with_suffix('.json')]:copy(f,Path('setup')/f.name)
for p in E.glob('*.json'):
 if p.name=='progress.json':continue
 copy(p,Path('engine-config')/p.name)
for p in E.glob('*'):
 if p.is_file() and p.suffix in ['.py','.html','.js','.css']:copy(p,Path('engine-code')/p.name)
for p in (E/'performance-presets').glob('*.json'):copy(p,Path('performance-presets')/p.name)
for name in ['start.sh','launch.py']:copy(ROOT/'sp'/name,Path('launcher')/name)
# Preserve the installed fresh Heart wrappers and their embedded resources.
patches=Path.home()/'Documents/Resolume Wire/Patches'
for folder in patches.glob('Heart *'):
 if folder.is_dir():
  for p in folder.rglob('*'):
   if p.is_file():copy(p,Path('wire-patches')/p.relative_to(patches))
copy(P/'REPORT.md',Path('REHEARSAL.md'));copy(P/'departure-verified.json',Path('PAIR-CHECK.json'))
(dest/'READ-ME.txt').write_text('Local recovery snapshot; not a standalone portable app. Keep the working workspace, sp/engine/.venv, sp/monitor/Heart.app and its Syphon framework at their existing paths. Original installed Wire patches and media remain in place. This copy does not protect against loss of this laptop. Live routed samples and navigation/recovery checked; latest paired-setup reopen and complete remaining representative-source pass verified separately in the included evidence. Full application/OS cold start and exhaustive visual-range/smoothness certification remain untested.\n')
manifest={str(p.relative_to(dest)):digest(p) for p in dest.rglob('*') if p.is_file()};(dest/'SHA256.json').write_text(json.dumps(manifest,indent=2));print(dest);print(len(manifest),'files verified')
