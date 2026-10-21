import subprocess,json
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;rows=[r for r in json.loads((P/'containment.json').read_text()) if r['source']=='SP Figure Spike Source']
for name,control in [('SP Figure Crystal Source','ior')]:
 for w,h in [(640,360),(360,640),(512,512)]:
  for n,extra in enumerate([[],[control+'=0','quatW=0','quatX=0','quatY=0','quatZ=0'],[control+'=1' if control=='spikeSharp' else 'ior=.5','quatW=-1','quatX=1','quatY=-1','quatZ=1','speed=3']]):
   out=P/f"{name.split()[2]}-{w}-{h}-{n}.png";args=['sp/qa/.venv/bin/python','sp/render_isf_fb.py','sp/'+name+'.fs','-o',str(out),'-w',str(w),'-H',str(h),'--frames','121','--rgba']
   for v in extra:args+=['--set',v]
   subprocess.run(args,check=True,stdout=subprocess.DEVNULL);im=Image.open(out);a=im.getchannel('A');edge=max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]);r=dict(source=name,size=[w,h],case=extra,edge_alpha=edge,bounds=a.getbbox());rows.append(r);print(name,w,h,n,'edge',edge,'bounds',r['bounds'],flush=True)
   (P/'containment.json').write_text(json.dumps(rows,indent=2))
assert all(r['bounds'] and r['edge_alpha']==0 for r in rows)
