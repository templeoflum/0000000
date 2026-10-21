from pathlib import Path
import subprocess,json
from PIL import Image
p=Path('sp/audit/figure-transform-pilot');rows=[]
for w,h in [(640,360),(360,640),(512,512)]:
 for n,extra in enumerate([[],['shadow=1','emboss=1','tumble=.75'],['morph=1','tumble=.5','axisv=1','micro=1']]):
  out=p/f'check-{w}-{h}-{n}.png';args=['sp/qa/.venv/bin/python','sp/render_isf_fb.py','sp/SP Figure Solid Source.fs','-o',str(out),'-w',str(w),'-H',str(h),'--frames','1','--rgba']
  for value in extra:args+=['--set',value]
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL);im=Image.open(out);a=im.getchannel('A');edge=max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]);row={'size':[w,h],'case':extra,'edge_alpha':edge,'bounds':a.getbbox()};rows.append(row)
(p/'containment.json').write_text(json.dumps(rows,indent=2));print(rows);assert all(r['bounds'] and r['edge_alpha']==0 for r in rows)
