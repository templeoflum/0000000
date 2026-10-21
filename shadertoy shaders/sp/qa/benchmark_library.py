"""Sequential 1080p smoke/performance catalog; never modifies Arena or shader sources."""
from pathlib import Path
import subprocess,json,hashlib,time
root=Path(__file__).resolve().parents[1]
out=root/'audit/20260907-070411/library';out.mkdir(parents=True,exist_ok=True)
patches=Path.home()/'Documents/Resolume Wire/Patches'
rows=[]
for shader in sorted(root.glob('*.fs')):
 name=shader.stem; report=out/(name+'.json'); png=out/(name+'.png')
 cmd=[str(root/'qa/.venv/bin/python'),str(root/'render_isf_fb.py'),str(shader),'-o',str(png),'--frames','42','--benchmark',str(report),'--scale','4']
 try:
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
  row=json.loads(report.read_text()) if r.returncode==0 else {'shader':str(shader),'error':r.stdout[-1500:]+r.stderr[-500:]}
 except subprocess.TimeoutExpired: row={'shader':str(shader),'error':'45s timeout'}
 installed=patches/name/'Resource'/(name+'.fs')
 row['installed_match']=hashlib.sha256(installed.read_bytes()).digest()==hashlib.sha256(shader.read_bytes()).digest() if installed.exists() else None
 rows.append(row);(out/'catalog.json').write_text(json.dumps(rows,indent=2))
 print(name, round(row.get('median_ms',0),3), 'ERROR' if 'error' in row else '',flush=True)
print('Catalog:',out/'catalog.json')
