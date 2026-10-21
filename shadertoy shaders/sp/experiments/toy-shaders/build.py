"""Isolated content build. Uses existing Smart Params; never calls installing emit()."""
import sys, json, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent
SP=OUT.parent.parent
sys.path.insert(0,str(SP))
import sp_header as smart
name='SP Toy Transit Figure 01'
inputs=smart.ROOT+smart.slot('phase','Phase',0.5,drive=False)+smart.slot('impact','Impact',0.0,drive=False)
body='''
// Scene-only adaptation of met3or/instruments/transit.html, drawScene/Ox/Oy.
// Original star radius 46, planet ratio .30, x=-250+500*phase relative to star.
// All placement belongs to external Figure Transform. No local scale/position.
float disc(float d,float r,float aa){return 1.0-smoothstep(r-aa,r+aa,d);}
vec3 starPalette(float r){
    if(r<0.35)return mix(vec3(255,243,223),vec3(246,192,122),r/0.35)/255.0;
    if(r<0.75)return mix(vec3(246,192,122),vec3(224,145,47),(r-0.35)/0.40)/255.0;
    return mix(vec3(224,145,47),vec3(58,38,15),clamp((r-0.75)/0.25,0.0,1.0))/255.0;
}
void main(){
    float H=TIME*heartRate;
    float ph=PHASE_CALL;
    float b=1.05*IMPACT_CALL;
    vec2 p=(gl_FragCoord.xy-0.5*RENDERSIZE)*650.0/min(RENDERSIZE.x,RENDERSIZE.y);
    // Canvas y is downward; preserve source impact direction in GLSL.
    vec2 planet=vec2(-250.0+500.0*ph,-b*46.0);
    float aa=650.0/min(RENDERSIZE.x,RENDERSIZE.y);
    float s=disc(length(p),46.0,aa);
    float pd=length(p-planet);
    float occ=disc(pd,13.8,aa);
    float rim=(1.0-smoothstep(0.55-aa,0.55+aa,abs(pd-13.8)))*0.8;
    // Opaque dark occultor, matching the source; straight alpha output.
    vec3 rgb=starPalette(length(p)/46.0);
    float alpha=s+occ*(1.0-s);
    vec3 prem=rgb*s*(1.0-occ)+vec3(5,8,12)/255.0*occ;
    prem=mix(prem,vec3(90,167,232)/255.0,rim);
    alpha=alpha+rim*(1.0-alpha);
    gl_FragColor=vec4(alpha>0.0?prem/alpha:vec3(0),alpha);
}
'''.replace('PHASE_CALL',smart.call('phase',0)).replace('IMPACT_CALL',smart.call('impact',1))
hdr={'ISFVSN':'2','CATEGORIES':['Generator','Experimental','Figure'],'DESCRIPTION':'Scene-only MET3OR Transit adaptation. Centered contained Figure. Use external Transform. Still Home; existing Smart Params drive Phase and Impact.','CREDIT':'Derived from Donovan’s local MET3OR Transit rev 1.2.1; scene adaptation by Codex.','INPUTS':inputs}
(OUT/(name+'.fs')).write_text('/*'+json.dumps(hdr,indent=2)+'*/\n'+smart.block()+body)
(OUT/(name+'.sp.json')).write_text(json.dumps(smart.groups([('phase','Phase'),('impact','Impact')]),indent=2)+'\n')
sources=[Path('/Users/donovan/work/met3or/instruments/transit.html'),Path('/Users/donovan/work/met3or/lore/recovered/met3or_quasicrystal.html'),SP/'sp.glsl',SP/'sp_header.py']
(OUT/'provenance.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
print(name)
