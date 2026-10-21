from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; SP=OUT.parents[2];sys.path.insert(0,str(SP))
import sp_header as smart
name='Heart Hering Field'
inputs=smart.ROOT+smart.slot('lines','Lines',108/168,drive=False)+smart.slot('fan','Fan',1,drive=False)
body='''
void main(){
 float H=TIME*heartRate;
 float count=floor(12.0+168.0*LINES+.5);
 float amount=FAN;
 float units=640.0/min(RENDERSIZE.x,RENDERSIZE.y);
 float x=(gl_FragCoord.x-.5*RENDERSIZE.x)*units;
 float y=(.5*RENDERSIZE.y-gl_FragCoord.y)*units;
 float aa=.5*units;
 vec3 paper=vec3(246,242,232)/255.0;
 vec3 fanColor=vec3(124,117,101)/255.0;
 vec3 mark=vec3(184,96,58)/255.0;
 float r=sqrt(x*x+y*y);
 float angle=atan(y,x);
 float stepAngle=6.283185307179586/count;
 float nearest=floor(angle/stepAngle+.5)*stepAngle;
 float distanceToRay=abs(sin(angle-nearest))*r;
 float ray=1.0-smoothstep(.7-aa,.7+aa,distanceToRay);
 ray*=1.0-smoothstep(900.0-aa,900.0+aa,r);
 vec3 rgb=mix(paper,fanColor,ray*amount);
 // Exactly straight parallel lines at x=+-150; rounded ends y=+-230.
 float verticalExcess=max(abs(y)-230.0,0.0);
 float leftDx=x+150.0,rightDx=x-150.0;
 float leftDistance=sqrt(leftDx*leftDx+verticalExcess*verticalExcess);
 float rightDistance=sqrt(rightDx*rightDx+verticalExcess*verticalExcess);
 float left=1.0-smoothstep(2.5-aa,2.5+aa,leftDistance);
 float right=1.0-smoothstep(2.5-aa,2.5+aa,rightDistance);
 rgb=mix(rgb,mark,max(left,right));
 gl_FragColor=vec4(rgb,1);
}
'''.replace('LINES',smart.call('lines',0)).replace('FAN',smart.call('fan',1))
h={'ISFVSN':'2','CATEGORIES':['Generator','Field'],'DESCRIPTION':'Corpus Hering. Test lines stay straight and parallel; radial fan varies. Fan0 is proof. Lines rounds12–180; keep density manual in Open.','CREDIT':'Donovan corpus hering.html; existing Smart Params.','INPUTS':inputs}
(OUT/(name+'.fs')).write_text('/*'+json.dumps(h,indent=2)+'*/\n'+smart.block()+body)
(OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([('lines','Lines'),('fan','Fan')]),indent=2))
p=Path('/Users/donovan/work/toys/hering.html');(OUT/'hering-provenance.json').write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'slots':{'lines':108/168,'fan':1},'open':'Fan driven; Lines stable108/168 (=120spokes), avoid density popping.'},indent=2))
