from pathlib import Path
import json,time,statistics,random,re
import numpy as np, moderngl
import argparse
ap=argparse.ArgumentParser()
ap.add_argument('--original',default=str(Path(__file__).with_name('session-performance-script-original.fs')))
ap.add_argument('--candidate',default=str(Path(__file__).with_name('session-performance-script-optimized.fs')))
ap.add_argument('--report',default=str(Path(__file__).with_name('session-performance-script-recheck.json')))
a=ap.parse_args()
original=Path(a.original)
optimized=Path(a.candidate)
# Every complete path must be contained before applying its expanded bounds.
source=original.read_text()
tables={n:[float(x) for x in re.search(r'const (?:float|int) '+n+r'\[\d+\] = (?:float|int)\[\d+\]\(([^)]+)\)',source)[1].split(',')] for n in ['PX','PY','SS','GS','BB']}
for g in range(len(tables['GS'])-1):
    lo=int(tables['SS'][int(tables['GS'][g])]); hi=int(tables['SS'][int(tables['GS'][g+1])]); b=tables['BB'][g*4:g*4+4]
    assert all(b[0]<=tables['PX'][i]<=b[2] and b[1]<=tables['PY'][i]<=b[3] for i in range(lo,hi)), g
ctx=moderngl.create_standalone_context()
vert='#version 410\nin vec2 p;void main(){gl_Position=vec4(p,0,1);}'
vbo=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],dtype='f4').tobytes())
programs=[]; defaults={}
for f in [original,optimized]:
 s=f.read_text();h=json.loads(s[s.index('/*')+2:s.index('*/')]);decl=[]
 for i in h['INPUTS']:
  typ='int' if i['TYPE']=='long' else 'float'
  decl.append(f'uniform {typ} {i["NAME"]};');defaults[i['NAME']]=i['DEFAULT']
 frag='#version 410\nout vec4 fragColor;\n#define gl_FragColor fragColor\nuniform vec2 RENDERSIZE;\n'+'\n'.join(decl)+'\n'+s[s.index('*/')+2:]
 p=ctx.program(vertex_shader=vert,fragment_shader=frag);programs.append((p,ctx.simple_vertex_array(p,vbo,'p')))

def render(index,settings,size,fbo):
 p,vao=programs[index]
 for k,v in {**defaults,**settings}.items():
  if k in p:p[k].value=int(v) if isinstance(defaults[k],int) else float(v)
 p['RENDERSIZE'].value=tuple(float(x) for x in size)
 fbo.use();ctx.viewport=(0,0,*size);ctx.clear(0,0,0,0);vao.render(moderngl.TRIANGLE_STRIP)

def targets(size):return [ctx.simple_framebuffer(size,components=4) for _ in range(2)]

checks=[]; rng=random.Random(739)
size=(640,240);fbos=targets(size)
counts=[63,52,24,20]
for sy,n in enumerate(counts):
 for gi in range(n):
  for morph in [0,.47]:
   settings={'script':sy,'glyph':min(1,(gi+morph)/(n-1)), 'sizev':rng.choice([0,.4,1]),'weight':rng.choice([0,.3,1]),'slant':rng.choice([-1,0,1]),'soft':rng.choice([0,1]),'ends':rng.choice([0,1]),'write':rng.choice([0,.17,.5,1]),'posx':rng.choice([-1,0,1]),'posy':rng.choice([-1,0,1])}
   outputs=[]
   for i in [0,1]:render(i,settings,size,fbos[i]);outputs.append(fbos[i].read(components=4))
   equal=outputs[0]==outputs[1];checks.append({'settings':settings,'resolution':size,'rgba_byte_exact':equal})
   if not equal:raise AssertionError(settings)
for f in fbos:f.release()
for size in [(1920,1080),(3840,1440)]:
 fbos=targets(size)
 for settings in [{},{'script':1,'glyph':.237,'sizev':1,'weight':1,'ends':1,'slant':-1,'soft':1,'write':.53,'posx':1,'posy':-1},{'script':3,'glyph':.613,'sizev':0,'weight':0,'slant':1,'soft':1,'posx':-1,'posy':1}]:
  outputs=[]
  for i in [0,1]:render(i,settings,size,fbos[i]);outputs.append(fbos[i].read(components=4))
  equal=outputs[0]==outputs[1];checks.append({'settings':settings,'resolution':size,'rgba_byte_exact':equal})
  if not equal:raise AssertionError(settings)
 for f in fbos:f.release()
bench=[]
for size in [(1920,1080),(3840,1440)]:
 fbos=targets(size)
 for settings in [{},{'sizev':1,'glyph':.237,'script':1}]:
  for warm in range(12):
   for i in [0,1]:render(i,settings,size,fbos[i]);ctx.finish()
  timings=[[],[]]
  for n in range(80):
   for i in ([0,1] if n%2==0 else [1,0]):
    ctx.finish();start=time.perf_counter();render(i,settings,size,fbos[i]);ctx.finish();timings[i].append((time.perf_counter()-start)*1000)
  bench.append({'resolution':size,'settings':settings,'original_median_ms':statistics.median(timings[0]),'candidate_median_ms':statistics.median(timings[1]),'original_p95_ms':float(np.percentile(timings[0],95)),'candidate_p95_ms':float(np.percentile(timings[1],95)), 'original_samples_ms':timings[0],'candidate_samples_ms':timings[1]})
 for f in fbos:f.release()
result={'method':'Offscreen OpenGL synchronized CPU submission + GPU completion, paired alternating order; excludes readback; not Arena frame time','renderer':ctx.info['GL_RENDERER'],'checks':checks,'benchmark':bench,'original':str(original),'candidate':str(optimized),'glyph_bounds_check':'All 159 complete glyph boxes contain every vertex. Expanded by stroke radius + full smoothstep antialias radius, after shear.'}
Path(a.report).write_text(json.dumps(result,indent=2))
print(json.dumps({'exact_checks':len(checks),'benchmark':[{k:v for k,v in b.items() if not k.endswith('samples_ms')} for b in bench]},indent=2))
