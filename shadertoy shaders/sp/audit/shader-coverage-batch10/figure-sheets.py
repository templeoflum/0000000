from pathlib import Path
from PIL import Image,ImageDraw
import json
p=Path(__file__).resolve().parent;rows=json.loads((p/'figure-no-controls.json').read_text())
for start in range(0,len(rows),4):
 group=rows[start:start+4];out=Image.new('RGB',(1100,335*len(group)),'#222');d=ImageDraw.Draw(out)
 for j,r in enumerate(group):
  for i in (0,1):
   im=Image.open(p/f"no-controls-L5C{r['col']}-{i}.png").convert('RGB');im.thumbnail((550,310));out.paste(im,(i*550,j*335+25));d.text((i*550+8,j*335+5),f"L5C{r['col']} {r['source']} / {i}",fill='white')
 out.save(p/f'figure-output-sheet-{start//4}.jpg')
