"""Relink unambiguous image paths only; preserve original compositions and all other XML."""
import re,html,json,hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'restored-compositions'
files=[Path(x) for x in Path('/tmp/heart-restoration-images.txt').read_text().splitlines()]
index={}
for p in files:
 parts=p.as_posix().lower().split('/')
 for n in range(2,len(parts)+1):index.setdefault('/'.join(parts[-n:]),set()).add(str(p))
report={}
for name in ('portal','treehouse'):
 src=Path.home()/'Documents/Resolume Arena/Compositions'/f'{name}.avc';original=src.read_text();changes={};missing=set()
 def sub(m):
  raw=m[2];old=html.unescape(raw);norm=re.sub('/+', '/', old.replace('\\','/'));parts=norm.lower().split('/')
  if not re.search(r'\.(png|jpe?g|tiff?|bmp|gif)$',norm,re.I) or '/' not in norm:return m[0]
  if Path(old).is_file():return m[0]
  candidates=set()
  for n in range(len(parts),1,-1):
   candidates=index.get('/'.join(parts[-n:]),set())
   if candidates:break
  if len(candidates)!=1:missing.add(old);return m[0]
  new=next(iter(candidates));assert Path(new).is_file();changes[old]=new
  return m[1]+html.escape(new,quote=True)+m[3]
 restored=re.sub(r'(\b[\w:.-]+\s*=\s*")([^"]*)(")',sub,original)
 ET.fromstring(restored)
 dest=OUT/f'{name}.avc';dest.write_text(restored)
 assert src.read_text()==original
 report[name]={'original':str(src),'restored':str(dest),'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'relinked_unique_images':len(changes),'unresolved_unique_images':len(missing),'changes':changes,'unresolved':sorted(missing),'note':'Image references only. Original XML otherwise preserved; video-library relinking and native playback not performed.'}
 print(name,'relinked',len(changes),'unresolved',len(missing));print('Unresolved examples:',sorted(missing)[:5])
(OUT/'image-relink-report.json').write_text(json.dumps(report,indent=2))
