"""Isolated corpus-toy ISF builds using the project's existing Smart Params."""
import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; SP=OUT.parents[2]
sys.path.insert(0,str(SP))
import sp_header as smart
SOURCE=Path('/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys')
common='''
float boxCoverage(vec2 p,vec2 center,vec2 halfSize,float aa){
 vec2 d=abs(p-center)-halfSize;
 return 1.0-smoothstep(-aa,aa,max(d.x,d.y));
}
'''
barber='''
// Scalar rectangle edges avoid the confirmed Wire vector-helper width error.
float scalarBox(float x,float y,float cx,float cy,float hx,float hy,float aa){
 float left=smoothstep(cx-hx-aa,cx-hx+aa,x);
 float right=1.0-smoothstep(cx+hx-aa,cx+hx+aa,x);
 float top=smoothstep(cy-hy-aa,cy-hy+aa,y);
 float bottom=1.0-smoothstep(cy+hy-aa,cy+hy+aa,y);
 return left*right*top*bottom;
}
void main(){
 float H=TIME*heartRate;
 float phaseValue=PHASE;
 float apertureValue=APERTURE;
 float contrastValue=CONTRAST;
 float units=520.0/min(RENDERSIZE.x,RENDERSIZE.y);
 // Original canvas coordinates, y downward; preserve diagonal in physical pixels.
 vec2 p=vec2(gl_FragCoord.x-.5*RENDERSIZE.x,.5*RENDERSIZE.y-gl_FragCoord.y)*units+vec2(310,260);
 float aa=.5*units;
 vec3 paper=vec3(246,242,232)/255.0;
 vec3 stripe=vec3(74,85,96)/255.0;
 vec3 ink=vec3(43,42,38)/255.0;
 // A single phase translates along (1,1)/sqrt(2); aperture never changes it.
 float d=abs(mod(dot(p,vec2(.7071067811865475))-48.0*phaseValue+24.0,48.0)-24.0);
 float stripeMask=1.0-smoothstep(12.0-aa,12.0+aa,d);
 float halfWidth=60.0+150.0*apertureValue;
 float halfHeight=200.0-150.0*apertureValue;
 float opening=scalarBox(p.x,p.y,310.0,250.0,halfWidth,halfHeight,aa);
 float outer=scalarBox(p.x,p.y,310.0,250.0,halfWidth+1.5,halfHeight+1.5,aa);
 float inner=scalarBox(p.x,p.y,310.0,250.0,halfWidth-1.5,halfHeight-1.5,aa);
 vec3 rgb=mix(paper,stripe,opening*stripeMask*contrastValue);
 rgb=mix(rgb,ink,clamp(outer-inner,0.0,1.0));
 gl_FragColor=vec4(rgb,1);
}
'''
feet='''
void main(){
 float H=TIME*heartRate;
 float phaseValue=PHASE;
 float stripesValue=STRIPES;
 float units=340.0/min(RENDERSIZE.x,RENDERSIZE.y);
 float sceneWidth=RENDERSIZE.x*units;
 vec2 p=vec2(gl_FragCoord.x*units,170.0+(.5*RENDERSIZE.y-gl_FragCoord.y)*units);
 float aa=.5*units;
 // Dark first half of each 72-unit stripe; original grayscale endpoints.
 float edge=abs(mod(p.x-18.0+36.0,72.0)-36.0);
 float darkMask=1.0-smoothstep(18.0-aa,18.0+aa,edge);
 float dk=floor(mix(150.0,26.0,stripesValue)+.5)/255.0;
 float lt=floor(mix(150.0,238.0,stripesValue)+.5)/255.0;
 float lum=mix(lt,dk,darkMask);
 // Exactly one position drives BOTH bars. Full-frame travel adapts to aspect.
 // At cyclic endpoints both bars are wholly outside the frame.
 float pos=phaseValue*(sceneWidth+96.0)-96.0;
 float pale=boxCoverage(p,vec2(pos+48.0,119.0),vec2(48,23),aa);
 float dark=boxCoverage(p,vec2(pos+48.0,221.0),vec2(48,23),aa);
 lum=mix(lum,232.0/255.0,pale);
 lum=mix(lum,34.0/255.0,dark);
 gl_FragColor=vec4(vec3(lum),1);
}
'''
def emit(name,source,desc,slots,body):
 inputs=list(smart.ROOT)
 for i,(n,label,default,cyc) in enumerate(slots):
  inputs+=smart.slot(n,label,default,drive=False,mult=16.0 if name=="Heart Barberpole Field" and n=="phase" else 1.0,shape=0 if cyc else 1,cyclic=cyc)
  body=body.replace(n.upper(),smart.call(n,i))
 hdr={'ISFVSN':'2','CATEGORIES':['Generator','Field'],'DESCRIPTION':desc,'CREDIT':'Adapted from Donovan’s corpus toy factory: '+source+'.html; existing Heart Smart Params.','INPUTS':inputs}
 (OUT/(name+'.fs')).write_text('/*'+json.dumps(hdr,indent=2)+'*/\n'+smart.block()+(common if source != 'barberpole' else '')+body)
 (OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([(n,label) for n,label,_,_ in slots]),indent=2)+'\n')
 return {'name':name,'source':str(SOURCE/(source+'.html')),'source_sha256':hashlib.sha256((SOURCE/(source+'.html')).read_bytes()).hexdigest(),'slots':[{'name':n,'label':label,'default':v,'cyclic':c,'drive':False,'shape':0 if c else 1} for n,label,v,c in slots]}
reports=[emit('Heart Barberpole Field','barberpole','Field: fixed diagonal grating drift seen through tall-to-wide aperture. Opaque paper background. Still Home; phase uses cyclic linear Smart Params.', [('phase','Phase',.5,True),('aperture','Aperture',0,False),('contrast','Contrast',1,False)],barber),emit('Heart Stepping Feet Field','stepping-feet','Field: opposite-luminance bars share exactly one position and speed against vertical stripes. Opaque background. Still central Home; cyclic linear Phase.', [('phase','Phase',.5,True),('stripes','Stripes',1,False)],feet)]
(OUT/'manifest.json').write_text(json.dumps({'pilots':reports,'shared_sp_sha256':hashlib.sha256((SP/'sp.glsl').read_bytes()).hexdigest(),'installed':False,'canonical_shader_sha256':{r['name']+'.fs':hashlib.sha256((OUT/(r['name']+'.fs')).read_bytes()).hexdigest() for r in reports},'barberpole_rectangle_fix':'Scalar edge coverage promoted following main-task live confirmation.'},indent=2)+'\n')
print(json.dumps(reports,indent=2))
