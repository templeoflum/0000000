from pathlib import Path
import subprocess,json
from PIL import Image
P=Path(__file__).resolve().parent;rows=[]
for name,extra in [('Heart HypnoWorm',['amp1=.25','amp2=.25','freq1=10','freq2=-10']),('Heart Torus',['torusSize=1','animationSpeed=1'])]:
 for w,h in [(640,360),(360,640),(512,512)]:
  out=P/f'{name}-{w}-{h}.png';args=['sp/qa/.venv/bin/python','sp/render_isf_fb.py',f'sp/{name}.fs','-o',str(out),'-w',str(w),'-H',str(h),'--frames','121','--rgba']
  for v in extra:args+=['--set',v]
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL);a=Image.open(out).getchannel('A');edge=max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
  rows.append(dict(source=name,size=[w,h],bounds=a.getbbox(),edge_alpha=edge))
print(rows);(P/'bounds.json').write_text(json.dumps(rows,indent=2));assert all(r['bounds'] and not r['edge_alpha'] for r in rows)
