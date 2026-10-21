from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
import json
p=Path(__file__).resolve().parent;rows=json.loads((p/'live-results.json').read_text());metrics=[]
for start in range(0,len(rows),4):
 group=rows[start:start+4];out=Image.new('RGB',(1100,335*len(group)),'#222');d=ImageDraw.Draw(out)
 for j,r in enumerate(group):
  ims=[]
  for i,n in enumerate((0,3)):
   f=p/f"L5C{r['col']}-motion-{n}.png";rgba=Image.open(f).convert('RGBA');bg=Image.new('RGBA',rgba.size,'black');bg.alpha_composite(rgba);im=bg.convert('RGB');ims.append(im.copy());im.thumbnail((550,310));out.paste(im,(i*550,j*335+25));d.text((i*550+8,j*335+5),f"L5C{r['col']} {r['source']} / {n}",fill='white')
  metrics.append(dict(col=r['col'],frame_difference=sum(ImageStat.Stat(ImageChops.difference(*ims)).mean)/3,mean_brightness=sum(ImageStat.Stat(ims[0]).mean)/3))
 out.save(p/f'output-sheet-{start//4}.jpg')
(p/'image-metrics.json').write_text(json.dumps(metrics,indent=2))
