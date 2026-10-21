from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
P=Path(__file__).resolve().parent;cols=[35,38,39,45,46,51];out=Image.new('RGB',(900,185*len(cols)),'#182029');d=ImageDraw.Draw(out)
for i,col in enumerate(cols):
 for j,phase in enumerate(['home','open']):
  p=P/f'{col}-{phase}.png'
  if not p.exists():continue
  im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);im=ImageOps.contain(bg.convert('RGB'),(440,160));out.paste(im,(j*450,i*185+22));d.text((j*450+5,i*185+4),f'{col} {phase}',fill='white')
out.save(P/'contact.jpg')
