from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; SP=OUT.parents[2];sys.path.insert(0,str(SP))
import sp_header as smart
name='Heart Cafe Wall Field'
inputs=smart.ROOT+smart.slot('offset','Offset',1,drive=False)+smart.slot('mortar','Mortar',.5,drive=False)
body='''
void main(){
 float H=TIME*heartRate;
 float shift=0.5*OFFSET;
 float mortarWidth=14.0*MORTAR;
 float units=680.0/min(RENDERSIZE.x,RENDERSIZE.y);
 float x=gl_FragCoord.x*units;
 float y=(RENDERSIZE.y-gl_FragCoord.y)*units;
 float aa=.5*units;
 float pitch=60.0+mortarWidth;
 float row=floor(y/pitch);
 float localY=mod(y,pitch);
 float rowShift=mod(row,2.0)*shift*88.0;
 float tileX=mod(x-rowShift,176.0);
 float black=1.0-smoothstep(44.0-aa,44.0+aa,abs(tileX-44.0));
 float tile=mix(235.0,20.0,black)/255.0;
 float coverage=1.0-smoothstep(60.0-aa,60.0+aa,localY);
 if(mortarWidth<.001)coverage=1.0;
 gl_FragColor=vec4(vec3(mix(128.0/255.0,tile,coverage)),1);
}
'''.replace('OFFSET',smart.call('offset',0)).replace('MORTAR',smart.call('mortar',1))
h={'ISFVSN':'2','CATEGORIES':['Generator','Field'],'DESCRIPTION':'Corpus Cafe Wall. Horizontal mortar remains straight; offset shifts alternate rows. Offset0 and Mortar0 are proof states. Opaque Field.','CREDIT':'Donovan corpus cafe-wall.html; existing Smart Params.','INPUTS':inputs}
(OUT/(name+'.fs')).write_text('/*'+json.dumps(h,indent=2)+'*/\n'+smart.block()+body)
(OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([('offset','Offset'),('mortar','Mortar')]),indent=2))
p=Path('/Users/donovan/work/toys/cafe-wall.html');(OUT/'cafe-provenance.json').write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'slots':{'offset':1,'mortar':.5},'open':'Offset driven within0–1; Mortar stable.5 retains visible mortar.'},indent=2))
