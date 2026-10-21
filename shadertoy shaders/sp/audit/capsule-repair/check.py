from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];rows=[];sheet=Image.new('RGB',(960,180*7))
for j,(w,h) in enumerate([(640,360),(360,640),(512,512)]):
 for i,t in enumerate([0,.15,.25,.5,.75,.85,1]):
  f=P/f'check-{w}-{h}-{i}.png';args=[str(R/'sp/qa/.venv/bin/python'),str(R/'sp/render_isf_fb.py'),str(R/'sp/Heart Capsule.fs'),'-o',str(f),'-w',str(w),'-H',str(h),'--frames','1','--rgba','--set',f'tiltPhase={t}','--set',f'outline={i%2}','--set',f'material={i/6}','--set','altitude=.8','--set',f'turn={i/6}'];subprocess.run(args,check=True,capture_output=True)
  im=Image.open(f).convert('RGBA');a=im.getchannel('A');box=a.point(lambda x:255 if x>8 else 0).getbbox();edge=max(a.crop(b).getextrema()[1] for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]);assert box and edge==0,(w,h,t,box,edge)
  rows.append(dict(width=w,height=h,tilt=t,bbox=box,edge_alpha=edge));bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);bg.thumbnail((310,150));sheet.paste(bg.convert('RGB'),(j*320,i*180));ImageDraw.Draw(sheet).text((j*320+5,i*180+153),f'{w}x{h} tilt {t}',fill='white')
(P/'bounds.json').write_text(json.dumps(rows,indent=2));sheet.save(P/'sheet.png');print(len(rows),'nonempty, zero edge alpha')
