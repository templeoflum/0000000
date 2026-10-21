"""Review saved Resolume RGBA snapshots on black without discarding alpha."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
import json
P=Path(__file__).resolve().parent
cases=[(10,8,1),(11,3,8),(8,5,28),(10,5,40),(9,5,50),(9,5,52),(11,3,94),(10,5,9)]
rows=[]
for batch,l,c in cases:
 ims=[]
 for n in (0,3):
  path=P.parent/f'shader-coverage-batch{batch}'/f'L{l}C{c}-motion-{n}.png'
  if not path.exists():continue
  im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);im=bg.convert('RGB');ims.append(im)
  im.save(P/f'original-L{l}C{c}-{n}.jpg')
 if len(ims)!=2:continue
 rows.append(dict(layer=l,col=c,brightness=[sum(ImageStat.Stat(im).mean)/3 for im in ims],difference=sum(ImageStat.Stat(ImageChops.difference(*ims)).mean)/3))
 sheet=Image.new('RGB',(960,295),'#222');d=ImageDraw.Draw(sheet)
 for i,im in enumerate(ims):
  im.thumbnail((480,270));sheet.paste(im,(i*480,25));d.text((i*480+8,5),f'L{l}C{c} frame {i}',fill='white')
 sheet.save(P/f'review-L{l}C{c}.jpg')
(P/'corrected-metrics.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
