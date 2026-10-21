from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path(__file__).resolve().parent;metrics=[]
for col in [20,25,38]:
 fs=sorted(p.glob(f'{col}-*.png'));out=Image.new('RGB',(1000,160*((len(fs)+3)//4)),(22,22,22));d=ImageDraw.Draw(out)
 for i,f in enumerate(fs):
  im=Image.open(f).convert('RGB');a=np.asarray(im);mask=a.max(axis=2)>20;y,x=np.where(mask);edge=bool(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any());metrics.append(dict(file=f.name,edge=edge,lit_pixels=int(mask.sum()),bounds=[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None));im.thumbnail((250,135));xx=i%4*250;yy=i//4*160;out.paste(im,(xx,yy+22));d.text((xx+3,yy+2),f.stem,fill='white')
 if fs:out.save(p/f'contact-{col}.jpg')
(p/'frame-metrics.json').write_text(json.dumps(metrics,indent=2));print('Edge contact:',[x['file'] for x in metrics if x['edge']]);print('Black:',[x['file'] for x in metrics if not x['lit_pixels']])
