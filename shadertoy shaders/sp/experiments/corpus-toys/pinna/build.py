"""Build isolated corpus Pinna Figure with existing Smart Params only."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;SP=OUT.parents[2]
sys.path.insert(0,str(SP))
import sp_header as smart
NAME='Heart Pinna Brelstaff Figure'
SOURCE=Path('/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/pinna-brelstaff.html')
slots=[('tilt','Tilt',24/45),('contrast','Contrast',1.0)]
inputs=list(smart.ROOT)
for n,label,default in slots:inputs+=smart.slot(n,label,default,drive=False,shape=1,cyclic=False)
body='''
// Scalar coverage avoids Wire's observed vec2 rectangle-helper width problem.
float pbSquare(float x,float y,float h,float aa){
 float left=smoothstep(-h-aa,-h+aa,x);
 float right=1.0-smoothstep(h-aa,h+aa,x);
 float top=smoothstep(-h-aa,-h+aa,y);
 float bottom=1.0-smoothstep(h-aa,h+aa,y);
 return left*right*top*bottom;
}
void main(){
 float H=TIME*heartRate;
 float tiltAngle=TILT*0.7853981633974483;
 float contrastAmount=0.55+0.45*CONTRAST;
 float shortSide=min(RENDERSIZE.x,RENDERSIZE.y);
 float px=(gl_FragCoord.x-.5*RENDERSIZE.x)/shortSide;
 float py=(.5*RENDERSIZE.y-gl_FragCoord.y)/shortSide;
 float aa=.5/shortSide;
 // Original short-side geometry reduced uniformly by .8 to reserve breathing room.
 float tileHalf=.028*.8;
 float strokeHalf=(1.5/800.0)*.8*.5;
 vec3 field=vec3(207,202,189)/255.0;
 vec3 ink=vec3(43,42,38)/255.0;
 vec3 paper=vec3(246,242,232)/255.0;
 vec3 rgb=field;
 float distanceFromCenter=sqrt(px*px+py*py);
 float alpha=1.0-smoothstep(.36-aa,.36+aa,distanceFromCenter);
 if(alpha<=0.0){gl_FragColor=vec4(0);return;}
 // Angular centers are invariant. No TIME-driven spin, zoom or independent ring phase.
 for(int ring=0;ring<2;ring++){
  int count=ring==0?21:30;
  float radius=ring==0?.22*.8:.37*.8;
  float direction=ring==0?1.0:-1.0;
  for(int i=0;i<30;i++){
   if(i>=count)break;
   float angle=6.283185307179586*float(i)/float(count);
   float cx=cos(angle)*radius;
   float cy=sin(angle)*radius;
   float orientation=angle+1.5707963267948966+direction*tiltAngle;
   float ca=cos(orientation),sa=sin(orientation);
   float dx=px-cx,dy=py-cy;
   float localX=ca*dx+sa*dy;
   float localY=-sa*dx+ca*dy;
   float fill=pbSquare(localX,localY,tileHalf,aa);
   float outer=pbSquare(localX,localY,tileHalf+strokeHalf,aa);
   float inner=pbSquare(localX,localY,tileHalf-strokeHalf,aa);
   float stroke=clamp(outer-inner,0.0,1.0);
   bool dark=(i-2*(i/2))==0;
   vec3 fillColor=mix(field,dark?ink:paper,contrastAmount);
   vec3 strokeColor=mix(field,dark?paper:ink,contrastAmount);
   rgb=mix(rgb,fillColor,fill);
   rgb=mix(rgb,strokeColor,stroke);
  }
 }
 // Original 16px-wide fixation cross scaled with the contained stimulus.
 float horizontal=pbSquare(px,py,.008,aa);
 float thinHorizontal=1.0-smoothstep(.001-aa,.001+aa,abs(py));
 float thinVertical=1.0-smoothstep(.001-aa,.001+aa,abs(px));
 float crossMask=horizontal*max(thinHorizontal,thinVertical);
 rgb=mix(rgb,vec3(184,96,58)/255.0,crossMask);
 gl_FragColor=vec4(rgb,alpha);
}
'''
for i,(n,label,default) in enumerate(slots):body=body.replace(n.upper(),smart.call(n,i))
hdr={'ISFVSN':'2','CATEGORIES':['Generator','Figure'],'DESCRIPTION':'Corpus Pinna–Brelstaff Figure. Fixed ring centers, opposing tile tilt, neutral circular plate. External Figure Transform supplies shared breathing; no real spin. Contrast retains at least55% source contrast.','CREDIT':'Adapted from Donovan’s corpus pinna-brelstaff.html; existing Heart Smart Params.','INPUTS':inputs}
fs=OUT/(NAME+'.fs');fs.write_text('/*'+json.dumps(hdr,indent=2)+'*/\n'+smart.block()+body)
(OUT/(NAME+'.sp.json')).write_text(json.dumps(smart.groups([(n,label) for n,label,_ in slots]),indent=2)+'\n')
(OUT/'manifest.json').write_text(json.dumps({'name':NAME,'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'shader_sha256':hashlib.sha256(fs.read_bytes()).hexdigest(),'smart_params_sha256':hashlib.sha256((SP/'sp.glsl').read_bytes()).hexdigest(),'slots':[{'name':n,'label':l,'default':v,'drive':False,'cyclic':False,'shape':1} for n,l,v in slots],'source_radius_pixels':'0.36 * min(width,height) + 1','ring_counts':[21,30],'geometry_scale_from_source':.8,'installed':False},indent=2)+'\n')
print(NAME,'Tilt Home',24/45,'Contrast Home1; Drive off')
