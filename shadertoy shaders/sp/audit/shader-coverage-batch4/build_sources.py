from pathlib import Path
import re,json,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
for old,new,cam,fov in [('Spikeball_v2','SP Figure Spike Source',4.0,2.5),('Crystal Drops','SP Figure Crystal Source',4.8,1.8)]:
 src=Path.home()/'Documents/Resolume Wire/Patches'/old/'Resource'/(old+'.fs');s=src.read_text();h=json.loads(re.search(r'/\*(\{.*?\})\*/',s,re.S).group(1));h['DESCRIPTION']='Heart bounded Figure source. Shared Figure Transform owns size and placement. '+h.get('DESCRIPTION','');h['INPUTS']=[i for i in h['INPUTS'] if i['NAME'] not in ('camDist','fov')];s=re.sub(r'/\*\{.*?\}\*/','/*'+json.dumps(h,indent=2)+'*/',s,count=1,flags=re.S)
 s=s.replace('q = normalize(q);','float q2 = dot(q,q);\n    q = q2 > 1e-10 ? q * inversesqrt(q2) : vec4(0.0,0.0,0.0,1.0);')
 s=s.replace('vec4(quatW, quatX, quatY, quatZ)', 'vec4(quatX, quatY, quatZ, quatW)')
 s=s.replace('camDist',str(cam)).replace('-fov','-'+str(fov));s=s.replace('/ RENDERSIZE.y','/ min(RENDERSIZE.x, RENDERSIZE.y)')
 if old=='Crystal Drops':
  s=s.replace('if (t >= 25.0)', 'if (t >= 25.0 || d >= 0.01)')
  s=s.replace('vec3 offset = mix( 0.1*rndPos, 15.0*rndPos, phase);','// Keep satellite centers in a radius-1.15 neighborhood.\n        vec3 direction = normalize(rndPos + vec3(0.00001));\n        vec3 offset = direction * mix(0.1, 1.15, phase);')
  s=s.replace('s = smin_v(s, s0, 0.4);','// Fade each droplet before its wrap, instead of teleporting a visible satellite.\n        float envelope = smoothstep(0.0,0.12,phase) * (1.0-smoothstep(0.82,1.0,phase));\n        s0 += (1.0-envelope)*0.3;\n        s = smin_v(s, s0, 0.16);')
  # Tighten smoothing; 12 unions can expand the outer bound by at most 12*.04.
  # Radius <=1.15+.25+.48+.007 = 1.887; camera4.8/fov1.8 => screen radius < .39 short side.
 out=ROOT/(new+'.fs');out.write_text(s);resource=P/'patches'/new/'Resource';resource.mkdir(parents=True,exist_ok=True);shutil.copy2(out,resource/(new+'.fs'));build_wrapper.P=str((P/'patches').resolve());build_wrapper.build(new)
