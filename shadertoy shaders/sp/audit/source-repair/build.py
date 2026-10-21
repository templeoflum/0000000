from pathlib import Path
import json,re,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
for old,new,fn in [('HypnoWorm','Heart HypnoWorm','HypnoWorm.isf'),('Torus thingy','Heart Torus','torus thingy.isf')]:
 src=Path.home()/'Documents/Resolume Wire/Patches'/old/'Resource'/fn;s=src.read_text();h=json.loads(re.search(r'/\*(\{.*?\})\*/',s,re.S).group(1));body=s[s.index('*/')+2:];inputs=[]
 for i in h['INPUTS']:
  n=i['NAME']
  if n=='center':body='const vec2 center=vec2(1.0);\n'+body;continue
  if n=='size':continue
  if n=='edge':continue # declared but unused in source
  if n in ('camX','camY','camZ','vignette'):
   body=f'const float {n}={(1.857142857 if n=='camZ' else i["DEFAULT"])};\n'+body;continue
  if i['TYPE']=='color':
   for k,ch in enumerate('RGB'):inputs.append(dict(NAME=n+ch,TYPE='float',DEFAULT=i['DEFAULT'][k],MIN=0.,MAX=1.))
   body=re.sub(r'\b'+n+r'\b',f'vec4({n}R,{n}G,{n}B,1.0)',body)
  else:inputs.append(i)
 if old=='HypnoWorm':body=body.replace('11.0 - size','12.0').replace('gl_FragCoord.xy / RENDERSIZE.xy','(gl_FragCoord.xy - 0.5*RENDERSIZE.xy) / min(RENDERSIZE.x,RENDERSIZE.y) + 0.5').replace('uv.x *= RENDERSIZE.x / RENDERSIZE.y;','').replace('col = pow(col, vec4(1.0 / gamma));','col = pow(max(col, vec4(0.0)), vec4(1.0 / gamma));')
 else:
  body=body.replace('#define FAR   80.','#define FAR   140.').replace('/ R.y;', '/ min(R.x,R.y);').replace('TIME','t').replace('t = abs(t * _animSpeed);','t = abs(TIME * _animSpeed);').replace('h *= 0.;','h = vec3(0.0);')
 h['INPUTS']=inputs;h['DESCRIPTION']='Heart control-ready copy; original preserved. '+h.get('DESCRIPTION','')
 out=ROOT/(new+'.fs');out.write_text('/*'+json.dumps(h,indent=2)+'*/\n'+body)
 resource=P/'patches'/new/'Resource';resource.mkdir(parents=True,exist_ok=True);shutil.copy2(out,resource/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(new)
