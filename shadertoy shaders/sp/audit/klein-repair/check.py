import subprocess,json
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
p=Path(__file__).resolve().parent;rows=[]
for w,h in [(640,360),(360,640),(512,512)]:
 for n,extra in enumerate([['refractIdx=0','quatW=0'],['refractIdx=1','quatW=-1','quatX=1','quatY=-1','quatZ=1','wallThickness=.08']]):
  out=p/f'case-{w}-{h}-{n}.png';cmd=['sp/qa/.venv/bin/python','sp/render_isf_fb.py','sp/Heart Klein Bottle.fs','-o',str(out),'-w',str(w),'-H',str(h),'--frames','1','--rgba']
  for a in extra:cmd+=['--set',a]
  subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL);im=Image.open(out);a=im.getchannel('A');edge=max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]);rows.append(dict(size=[w,h],case=n,bounds=a.getbbox(),edge=edge))
(p/'bounds.json').write_text(json.dumps(rows,indent=2));assert all(r['bounds'] and r['edge']==0 for r in rows)
for n in [0,1]:subprocess.run(['sp/qa/.venv/bin/python','sp/render_isf_fb.py','sp/Heart Klein Bottle.fs','-o',str(p/f'refract-{n}.png'),'-w','640','-H','360','--frames','1','--rgba','--set',f'refractIdx={n}'],check=True,stdout=subprocess.DEVNULL)
a,b=[Image.open(p/f'refract-{n}.png') for n in [0,1]];print('bounds passed',len(rows),'refraction difference',sum(ImageStat.Stat(ImageChops.difference(a,b)).mean))
