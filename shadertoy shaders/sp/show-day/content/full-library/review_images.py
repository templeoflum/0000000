from PIL import Image,ImageOps,ImageDraw,ImageStat,ImageChops
from pathlib import Path
import json
P=Path(__file__).resolve().parent
results=json.loads((P/'results.json').read_text());stats=[];pages=[]
for i,r in enumerate(results):
 key=f"L{r['layer']}C{r['col']}";row=dict(key=key,source=r['source']);pair=[]
 for phase in ['home','shuffle']:
  f=P/f'{key}-{phase}.png'
  if not f.exists():pair.append(None);continue
  im=Image.open(f).convert('RGBA');bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);im=bg.convert('RGB');gray=im.convert('L');st=ImageStat.Stat(gray)
  hist=gray.histogram();row[phase]=dict(size=im.size,mean=round(st.mean[0],2),stddev=round(st.stddev[0],2),near_black=round(sum(hist[:5])/(im.width*im.height),4),near_white=round(sum(hist[251:])/(im.width*im.height),4))
  pair.append(im)
 if all(x is not None for x in pair):row['pixel_difference']=round(ImageStat.Stat(ImageChops.difference(*pair)).mean[0],3)
 stats.append(row)
 if i%5==0:
  page=Image.new('RGB',(1200,1125),'#19232d');draw=ImageDraw.Draw(page);pages.append(page)
 y=(i%5)*225
 for j,im in enumerate(pair):
  draw.text((j*600+5,y+3),f"{key} {r['source'][:53]} / {['Home','Shuffle'][j]}",fill='white')
  if im is not None:page.paste(ImageOps.contain(im,(595,200)),(j*600,y+23))
for i,im in enumerate(pages):im.save(P/f'review-{i+1:02}.jpg',quality=88)
(P/'image-statistics.json').write_text(json.dumps(stats,indent=2))
print(len(stats),'pairs;',len(pages),'review sheets')
print('DARK/FLAT',[(r['key'],r['source']) for r in stats if any(r.get(p,{}).get('near_black',0)>.98 or r.get(p,{}).get('stddev',100)<2 for p in ['home','shuffle'])])
