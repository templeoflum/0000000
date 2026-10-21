from pathlib import Path
import json,re,sys,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT));import build_wrapper
name='Heart Capsule';s=(ROOT/'SP Figure.fs').read_text();h=json.loads(re.search(r'/\*\s*(\{.*?\})\s*\*/',s,re.S).group(1))
h['DESCRIPTION']='Centered capsule with bounded internal tilt. Placement and size belong to the shared Figure Transform. Original SP Figure preserved.'
h['INPUTS']=[dict(NAME=n,LABEL=label,TYPE='float',DEFAULT=v,MIN=0.,MAX=1.) for n,label,v in [('turn','Turn',0.),('outline','Outline',0.),('material','Material',.65),('altitude','Float',.15),('tiltPhase','Tilt',.5)]]
body='#define SP_PI 3.141592653589793\n'+s[s.index('float sdCapsule2'):]
start=body.index('    float H =');end=body.index('    // ── the folds:',start)
body=body[:start]+'    float TN=turn, OL=outline, MT=material, FLT=altitude;\n'+body[end:]
start=body.index('    vec2 uv =');end=body.index('    float a =',start)
body=body[:start]+'''    vec2 uv = (gl_FragCoord.xy - .5*RENDERSIZE.xy) / min(RENDERSIZE.x, RENDERSIZE.y);
    // Fixed source-space radius includes shadows; all final alpha stays inside it.
    float rad=.30;
    vec2 c=vec2(0.0);

'''+body[end:]
body=re.sub(r'float axr = SPN[^\n]*', 'float axr = (tiltPhase-.5) * (2.0*SP_PI/3.0); // bounded -60 to +60 degrees',body)
body=re.sub(r'float ayr = SPN[^\n]*', 'float ayr = axr;',body)
out=ROOT/(name+'.fs');out.write_text('/*'+json.dumps(h,indent=2)+'*/\n'+body)
r=P/'patches'/name/'Resource';r.mkdir(parents=True,exist_ok=True);shutil.copy2(out,r/out.name);build_wrapper.P=str(P/'patches');build_wrapper.build(name)
