"""Bake original SVG point construction to a transparent asset; no live installation."""
import math, itertools, json, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent.parent))
import sp_header as smart
S=4
im=Image.new('RGBA',(400*S,400*S))
def circle(x,y,r,col,opacity):
    layer=Image.new('RGBA',im.size)
    ImageDraw.Draw(layer).ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=(*col,round(255*opacity)))
    im.alpha_composite(layer)
points=[]
e=[(math.cos(k*math.tau/5),math.sin(k*math.tau/5)) for k in range(5)]
ep=[(math.cos(k*2*math.tau/5),math.sin(k*2*math.tau/5)) for k in range(5)]
for n in itertools.product(range(-2,3),repeat=5):
    px,py=[sum(n[k]*e[k][j] for k in range(5)) for j in range(2)]
    qx,qy=[sum(n[k]*ep[k][j] for k in range(5)) for j in range(2)]
    I=math.exp(-.30*(qx*qx+qy*qy)); r=math.hypot(px,py)
    if I>=.12 and r*21<=176: points.append((I,200+px*21,200+py*21,r))
points.sort(key=lambda p:p[0]); seen=set(); kept=[]
for I,x,y,r in points:
    key=(math.floor(x/3+.5),math.floor(y/3+.5))
    if key in seen: continue
    seen.add(key); kept.append([x,y,I,r])
    col=(230,237,243) if r<.6 else [(74,222,128),(90,167,232),(240,169,74)][math.floor(math.log(r/2)/math.log(1.618)+.5)%3]
    core=.7+4.6*math.sqrt(I)
    circle(x,y,core+2.4,col,.13*I); circle(x,y,core,col,min(1,.35+.65*I))
circle(200,200,9,(230,237,243),.16); circle(200,200,4.5,(230,237,243),1)
im.resize((800,800),Image.Resampling.LANCZOS).save(OUT/'quasicrystal-points.png')
(OUT/'quasicrystal-points.json').write_text(json.dumps(kept,separators=(',',':')))
name='SP Toy Quasicrystal Figure 01'
inputs=smart.ROOT+smart.slot('turn','Turn',0,drive=False,cyclic=True)+smart.slot('reveal','Reveal',1,drive=False)
body='''
void main(){
 float H=TIME*heartRate;
 float angle=6.28318530718*TURN_CALL;
 float amount=REVEAL_CALL;
 vec2 p=(gl_FragCoord.xy-.5*RENDERSIZE)/min(RENDERSIZE.x,RENDERSIZE.y);
 p=mat2(cos(angle),-sin(angle),sin(angle),cos(angle))*p;
 vec2 uv=p/.88+.5;
 if(any(lessThan(uv,vec2(0)))||any(greaterThan(uv,vec2(1)))){gl_FragColor=vec4(0);return;}
 vec4 ink=IMG_NORM_PIXEL(toyPoints,uv);
 // Optional performative erosion of faint halos/points; Home retains full plate.
 ink.a*=smoothstep((1.0-amount)*.85,(1.0-amount)*.85+.03,ink.a);
 gl_FragColor=ink;
}
'''.replace('TURN_CALL',smart.call('turn',0)).replace('REVEAL_CALL',smart.call('reveal',1))
h={'ISFVSN':'2','CATEGORIES':['Generator','Experimental','Figure'],'CREDIT':'Adapted from Donovan’s MET3OR phi-quasicrystal, original projected point construction.','DESCRIPTION':'Contained quasicrystal Figure. Existing Smart Params turn and reveal; external Transform owns placement. Bundled imported PNG required.','IMPORTED':{'toyPoints':{'PATH':'quasicrystal-points.png'}},'INPUTS':inputs}
(OUT/(name+'.fs')).write_text('/*'+json.dumps(h,indent=2)+'*/\n'+smart.block()+body)
(OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([('turn','Turn'),('reveal','Reveal')]),indent=2))
print('accepted tuples',len(points),'deduplicated points',len(kept))
