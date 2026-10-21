from pathlib import Path
import re,json,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
src=Path.home()/'Documents/Resolume Wire/Patches/Color Wheel/Resource/Color Wheel.isf';s=src.read_text();m=re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S);h=json.loads(m.group(1));inputs=[]
settings={'rotate':('Hue Rotation',0.,1.),'multiply':('Color Repeats',1.,24.),'sharpenLines':('Saturation Contrast',1.,8.),'invert':('Center Brightness',.1,1.),'warp':('Gain',.1,2.),'mRadius':('Saturation Spread',.25,3.)}
for i in h['INPUTS']:
 if i['NAME']=='pos':continue
 label,lo,hi=settings[i['NAME']];i.update(LABEL=label,MIN=lo,MAX=hi);inputs.append(i)
h['INPUTS']=inputs;h['DESCRIPTION']='Heart Color Wheel: usable gain and saturation ranges. Original source preserved.'
body=s[m.end():].replace('c.y)*warp','clamp(c.y,0.0,1.0))*warp');body='\nconst vec2 pos=vec2(0.0);\n'+body
name='Heart Color Wheel';out=ROOT/(name+'.fs');out.write_text(s[:m.start()]+'/*'+json.dumps(h,indent=2)+'*/'+body)
res=P/'patches'/name/'Resource';res.mkdir(parents=True,exist_ok=True);shutil.copy2(out,res/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(name)
