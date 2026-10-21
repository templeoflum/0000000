from pathlib import Path
import json,re,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
installed=Path.home()/'Documents/Resolume Wire/Patches';rows=[]
for old,new,col in [('QField2','Heart Quaternion Field',4),('quarternionSwell','Heart Quaternion Swell',5),('Paper Fractal','Heart Paper Fractal',6),('VectorFromHell','Heart Vector Lattice',7)]:
 j=json.loads((installed/old/(old+'.wire')).read_text());nodes=[n for n in j['patch']['nodes'].values() if 'fragment-shader' in n.get('attributes',{})];assert len(nodes)==1
 source=installed/old/nodes[0]['attributes']['fragment-shader']['value']['path']['main'];s=source.read_text();m=re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S);h=json.loads(m.group(1));assert all(i['TYPE']=='float' for i in h['INPUTS'])
 h['DESCRIPTION']='Heart control-ready Field copy; original shader body preserved. '+h.get('DESCRIPTION','');s='/*'+json.dumps(h,indent=2)+'*/'+s[m.end():]
 out=ROOT/(new+'.fs');out.write_text(s);resource=P/'patches'/new/'Resource';resource.mkdir(parents=True,exist_ok=True);shutil.copy2(out,resource/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(new)
 rows.append(dict(old=old,name=new,col=col,source=str(source),controls=[i.get('LABEL',i['NAME']) for i in h['INPUTS']]))
(P/'sources.json').write_text(json.dumps(rows,indent=2))
