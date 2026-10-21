from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1];out=root/'audit/20260907-070411/active';out.mkdir(exist_ok=True)
comp=json.loads((out.parent/'composition-before.json').read_text())
rows=[]
for layer in comp['layers']:
 for clip in layer['clips']:
  if 'Connected' not in str(clip['connected']['value']):continue
  v=clip.get('video') or {}
  sections=[(v.get('description',''),v.get('sourceparams',{}))]+[(e['name'],e.get('params',{})) for e in v.get('effects',[])]
  for name,params in sections:
   fs=next((f for f in root.glob('*.fs') if f.stem.replace(' ','')==name.replace(' ','')),None)
   if not fs:continue
   text=fs.read_text();hdr=json.loads(text[text.index('/*')+2:text.index('*/')]);settings={}
   for inp in hdr['INPUTS']:
    par=params.get(inp.get('LABEL',inp['NAME']))
    if not par or inp['TYPE']=='image':continue
    value=par.get('index') if inp['TYPE']=='long' else par.get('value')
    if isinstance(value,(int,float,bool)):settings[inp['NAME']]=int(value) if isinstance(value,bool) else value
   scenarios={'live':settings}
   if name=='SP Atom 4D Field':
    for size in [.36,.7,1.]:scenarios['large-'+str(size)]={**settings,'size':size,'layers':32,'drift':0,'edgesv':1,'verts':1,'halo':1}
   for tag,ss in scenarios.items():
    dest=out/(name+'-'+tag)
    cmd=[str(root/'qa/.venv/bin/python'),str(root/'render_isf_fb.py'),str(fs),'-o',str(dest)+'.png','--frames','72','--scale','3','--benchmark',str(dest)+'.json']
    for k,v in ss.items():cmd.extend(['--set',f'{k}={v}'])
    try:
     r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
     row=json.loads(Path(str(dest)+'.json').read_text()) if not r.returncode else {'error':r.stdout+r.stderr}
    except subprocess.TimeoutExpired:row={'error':'timeout'}
    row['scenario']=tag;rows.append(row);print(name,tag,row.get('median_ms',row.get('error')),flush=True)
(out/'catalog.json').write_text(json.dumps(rows,indent=2))
