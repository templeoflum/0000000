from pathlib import Path
import sys,re,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'engine'));import clip_navigation
path=ROOT/'engine/sweetspots.json';data=json.loads(path.read_text());(P/'sweetspots-before.json').write_text(path.read_text());rows=[]
for name in sorted(n for n in clip_navigation.COPIES if n.startswith('Heart ')):
 src=ROOT/(name+'.fs');s=src.read_text();h=json.loads(re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S).group(1));static={}
 for i in h['INPUTS']:
  if i['TYPE']!='float':continue
  lo,hi=i.get('MIN',0),i.get('MAX',1);v=i.get('DEFAULT',lo);static[i.get('LABEL',i['NAME'])]=(v-lo)/(hi-lo)
 if name=='Heart Quaternion Field':static.update({'Field Scale':.55,'Sample Distance':.55,'Brightness':.75,'Mean Radius':.5})
 if name in data:rows.append(dict(source=name,status='existing profile preserved'));continue
 data[name]={'bindings':{},'static':static};rows.append(dict(source=name,status='added',static=static))
path.write_text(json.dumps(data,indent=2)+'\n');(P/'profiles.json').write_text(json.dumps(rows,indent=2));print('added',sum(r['status']=='added' for r in rows))
