from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; SP=OUT.parents[2];sys.path.insert(0,str(SP))
import sp_header as smart
name='Heart Fraser Spiral Field'
inputs=smart.ROOT+smart.slot('twist','Twist',1,drive=False)+smart.slot('trace','Trace',0,drive=False)
body='''
float frBox(float x,float y,float hx,float hy,float aa){
 return smoothstep(-hx-aa,-hx+aa,x)*(1.0-smoothstep(hx-aa,hx+aa,x))*smoothstep(-hy-aa,-hy+aa,y)*(1.0-smoothstep(hy-aa,hy+aa,y));
}
void main(){
 float H=TIME*heartRate;
 float tilt=TWIST*.7853981633974483;
 float proof=TRACE;
 float units=620.0/min(RENDERSIZE.x,RENDERSIZE.y);
 float x=(gl_FragCoord.x-.5*RENDERSIZE.x)*units;
 float y=(.5*RENDERSIZE.y-gl_FragCoord.y)*units;
 float aa=.5*units;
 float parity=mod(floor((x+310.0)/42.0)+floor((y+310.0)/42.0),2.0);
 vec3 rgb=mix(vec3(188,182,168),vec3(156,150,138),parity)/255.0;
 float theta=atan(y,x);
 // Five independent closed circles. Only bars tilt; centers never spiral.
 for(int ring=0;ring<5;ring++){
  float r=70.0+50.0*float(ring);
  float count=floor(6.283185307179586*r/34.0+.5);
  float nearest=floor(theta*count/6.283185307179586+.5);
  // Neighboring bar centers suffice: spacing~34, half-diagonal<14.
  for(int j=-1;j<=1;j++){
   float angle=(nearest+float(j))*6.283185307179586/count;
   float dx=x-r*cos(angle),dy=y-r*sin(angle);
   float orientation=angle+1.5707963267948966+tilt;
   float ca=cos(orientation),sa=sin(orientation);
   float lx=ca*dx+sa*dy,ly=-sa*dx+ca*dy;
   float coverage=frBox(lx,ly,13.0,4.5,aa);
   float light=smoothstep(-aa,aa,lx);
   vec3 bar=mix(vec3(29,28,25),vec3(244,241,232),light)/255.0;
   rgb=mix(rgb,bar,coverage);
  }
 }
 float rd=abs(sqrt(x*x+y*y)-220.0);
 float circle=1.0-smoothstep(1.25-aa,1.25+aa,rd);
 float dash=1.0-smoothstep(8.0-aa,8.0+aa,mod((theta+3.141592653589793)*220.0,15.0));
 rgb=mix(rgb,vec3(184,96,58)/255.0,proof*circle*dash);
 gl_FragColor=vec4(rgb,1);
}
'''.replace('TWIST',smart.call('twist',0)).replace('TRACE',smart.call('trace',1))
h={'ISFVSN':'2','CATEGORIES':['Generator','Field'],'DESCRIPTION':'Corpus Fraser false spiral. Five closed circular rings of tilted two-tone bars over checkerboard; Twist0 removes tilt, Trace reveals true circle.','CREDIT':'Donovan corpus fraser-spiral.html; existing Smart Params.','INPUTS':inputs}
(OUT/(name+'.fs')).write_text('/*'+json.dumps(h,indent=2)+'*/\n'+smart.block()+body)
(OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([('twist','Twist'),('trace','Trace')]),indent=2))
p=Path('/Users/donovan/work/toys/fraser-spiral.html');(OUT/'fraser-provenance.json').write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'slots':{'twist':1,'trace':0},'open':'Twist driven; Trace remains0 unless deliberate proof.'},indent=2))
