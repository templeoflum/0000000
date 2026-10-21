from pathlib import Path
import json,re,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
base=Path.home()/'Documents/Resolume Wire/Patches';rows=[]
def inp(n,d,lo,hi):return dict(NAME=n,TYPE='float',DEFAULT=d,MIN=lo,MAX=hi)
for old,new,col in [('Concentrip','Heart Concentrip',9),('TwoFiftySixBiatch','Heart Puls Lattice',10),('kali - ancient temple','Heart Ancient Temple',11),('kali liberation of the true self','Heart Kali Liberation',12)]:
 j=json.loads(next((base/old).glob('*.wire')).read_text());nodes=[n for n in j['patch']['nodes'].values() if 'fragment-shader' in n.get('attributes',{})];assert len(nodes)==1
 src=base/old/nodes[0]['attributes']['fragment-shader']['value']['path']['main'];s=src.read_text();m=re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S);h=json.loads(m.group(1));body=s[m.end():]
 if old=='Concentrip':
  h['INPUTS']=[inp('radialDensity',25.,3.,45.),inp('angularDensity',16.,2.,28.),inp('blendThreshold',.5,.1,.9),inp('blendWidth',.5,.05,.8),inp('phase',0.,0.,6.283185),inp('hue',0.,0.,1.)]
  body=body.replace('#define threshold 0.5','#define threshold blendThreshold').replace('#define overlap 0.5','#define overlap blendWidth').replace('l*25.0','l*radialDensity').replace('n/a*16.0','n/max(a,0.00001)*angularDensity').replace('TIME','(TIME+phase)')
  body=body.replace('G = V; B = V;', 'R = V; G = V; B = V;').replace('float R; float G; float B;', 'H = fract(H + hue);\n float R; float G; float B;')
  body=body.replace('mod(p,(TIME+phase))','safeMod(p,(TIME+phase))').replace('mod(n/max(a,0.00001)*angularDensity','safeMod(n/max(a,0.00001)*angularDensity')
  body='\nfloat safeMod(float x,float y){float d=abs(y)<0.00001?(y<0.0?-0.00001:0.00001):y;return mod(x,d);}\n'+body
 elif old=='TwoFiftySixBiatch':
  h['INPUTS']=[inp('cellSpacing',4.5,3.5,6.),inp('barWidth',.14,.06,.25),inp('boltWidth',.28,.16,.4),inp('greenExpansion',0.,0.,.4),inp('orangeExpansion',0.,0.,.4),inp('pulsePhase',0.,0.,6.283185),inp('travelPhase',0.,0.,6.283185)]
  body=re.sub(r'uniform float bin[012];','',body).replace('#define CELL_SIZE 4.5','#define CELL_SIZE cellSpacing').replace('sin(TIME*2.0)','sin(TIME*2.0+pulsePhase)').replace('max(bin0-0.55, 0.0)*2.0','greenExpansion').replace('max(bin1-0.4, 0.0)*2.0','orangeExpansion').replace('bars_d(q, 0.14)','bars_d(q, barWidth)').replace('bars_d(q, 0.28)','bars_d(q, boltWidth)').replace('TIME *0.05','TIME *0.05+travelPhase').replace('sqrt(1.0 - x*x - y*y)','sqrt(max(0.00001,1.0 - x*x - y*y))')
 h['DESCRIPTION']='Heart control-ready Field copy; original preserved. '+h.get('DESCRIPTION','')
 out=ROOT/(new+'.fs');out.write_text('/*'+json.dumps(h,indent=2)+'*/'+body);resource=P/'patches'/new/'Resource';resource.mkdir(parents=True,exist_ok=True);shutil.copy2(out,resource/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(new)
 rows.append(dict(old=old,name=new,col=col,source=str(src),controls=[i.get('LABEL',i['NAME']) for i in h['INPUTS']]))
(P/'sources.json').write_text(json.dumps(rows,indent=2))
