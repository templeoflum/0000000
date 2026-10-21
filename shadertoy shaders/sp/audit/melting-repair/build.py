from pathlib import Path
import json,re,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
src=Path.home()/'Documents/Resolume Wire/Patches/Melting Fractal/Resource/Melting Fractal.isf';s=src.read_text();m=re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S);h=json.loads(m.group(1));h['INPUTS']=[i for i in h['INPUTS'] if i['NAME']!='camDist']
for i in h['INPUTS']:
 if i['NAME']=='animSpeed':i['LABEL']='Fold Phase'
 if i['NAME']=='orbitSpeed':i['LABEL']='Orbit Phase'
 if i['NAME']=='rotMix':i['LABEL']='Twist Amount'
h['DESCRIPTION']='Heart Melting Fractal: phase-driven folds, orthogonal rotations and fixed source camera. Original preserved.'
b=s[m.end():];b=b.replace('float s = sin(angle);','angle *= 1.0 + rMix;\n    float s = sin(angle);').replace('float r = 1.0 + rMix - c;','float r = 1.0 - c;')
b=b.replace('mix(-1.0, 0.18, foldOffset)','mix(-0.4, -0.2, foldOffset)')
b=b.replace('float cDist     = mix(0.5, 10.0, camDist);','float cDist     = 3.0;').replace('/ RENDERSIZE.y;', '/ min(RENDERSIZE.x, RENDERSIZE.y);')
b=b.replace('if(res.x < precis || t > MAX_DIST) break;\n        t += res.x;\n        m = res.y;', 'if(res.x < precis){m=res.y;break;}\n        if(t > MAX_DIST)break;\n        t += max(res.x * 0.8, MIN_DIST);')
b=b.replace('gl_FragColor = vec4(color, glowAlpha);','gl_FragColor = vec4(0.0);')
b=b.replace('color = effect(color);','color += glow * (0.25 + 2.0*glowStrength) * vec3(242,223,126)/255.;\n    color=pow(clamp(color,0.0,1.0),vec3(1.0/2.2));')
name='Heart Melting Fractal';out=ROOT/(name+'.fs');out.write_text('/*'+json.dumps(h,indent=2)+'*/'+b);res=P/'patches'/name/'Resource';res.mkdir(parents=True,exist_ok=True);shutil.copy2(out,res/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(name)
