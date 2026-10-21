import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent.parent
rows=json.loads((p/'results.json').read_text())
review=json.loads((p/'visual-review.json').read_text())
new=[r for r in rows if "--all" in sys.argv or f"L{r['layer']}C{r['col']}" not in review or ("--flags" in sys.argv and any(review.get(f"L{r['layer']}C{r['col']}",{}).get(s) in {"blank","flat","sparse"} for s in ["home","shuffle"]))]
print('total',len(rows),'unreviewed',len(new),'finished',(p/'finished.json').exists())
for batch in range(0,len(new),6):
 rs=new[batch:batch+6]; out=Image.new('RGB',(960, len(rs)*294),(35,35,35));d=ImageDraw.Draw(out)
 for i,r in enumerate(rs):
  k=f"L{r['layer']}C{r['col']}"
  for j,s in enumerate(['home','shuffle']):
   f=p/f'{k}-{s}.png'
   if f.exists():
    rgba=Image.open(f).convert('RGBA');im=Image.alpha_composite(Image.new('RGBA',rgba.size,(0,0,0,255)),rgba).convert('RGB');im.thumbnail((480,270));out.paste(im,(480*j,294*i+24))
   d.text((480*j+4,294*i+5),f'{k} {r["source"]} {s}',fill='white')
 dest=p/'review-assets'/f'pending-{batch//6}.jpg';out.save(dest);print(dest)
