"""Bounded source-only GPU checks; no Arena mutations and no downstream FX masks."""
import sys,runpy,json,math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/heart-performance-plan/figure-milestone'
catalog=json.loads((ROOT/'engine/instruments.json').read_text())['instruments'];results=[];pictures=[]
for d in catalog:
 path=ROOT/d['source']['file'] if d['source']['file'] else Path.home()/'Documents/Resolume Wire/Patches/z33d+/Resource/z33d+.isf'
 hdr=json.loads(path.read_text().split('/*',1)[1].split('*/',1)[0]);inputs=hdr['INPUTS'];labels={p.get('LABEL',p['NAME']):p for p in inputs}
 if d['id']=='figure.seed':labels.update({a:next(p for p in inputs if p['NAME']==b) for a,b in {'mx':'mX','my':'mY','axis x':'axisX','axis y':'axisY','rot angle':'rotAngle','axis drift':'axisDrift'}.items()})
 sys.argv=['render_isf_fb.py',str(path),'-o',str(OUT/'qa-scratch.png'),'-w','640','-H','360','--frames','1','--rgba']
 ns=runpy.run_path(str(ROOT/'render_isf_fb.py'));prog=ns['prog'];ctx=ns['ctx'];vao=ns['vao'];out=ns['out_fbo'];base=dict(ns['vals'])
 if d['id']=='figure.seed':base.update(zoom=.169697,rate=0)
 def native(label,v):
  p=labels[label];return p['MIN']+(p['MAX']-p['MIN'])*v if p['TYPE']=='float' else v
 def home(phase):
  v=dict(base);pr=d['home']
  for label,x in pr.get('static',{}).items():v[labels[label]['NAME']]=native(label,x)
  for label,choice in pr.get('choices',{}).items():p=labels[label];v[p['NAME']]=p.get('VALUES',range(len(p['LABELS'])))[p['LABELS'].index(choice)]
  for i,(label,b) in enumerate(pr['bindings'].items()):
   lo,hi=b['range'];t=(phase+i/len(pr['bindings']))%1
   value=t if b.get('cyclic') and b.get('shape')==0 else lo+(hi-lo)*(.5-.5*math.cos(t*2*math.pi))
   v[labels[label]['NAME']]=native(label,value)
  return v
 def render(v,program=prog,vertex=vao):
  for k,x in v.items():
   if k in program:program[k].value=x
  if 'TIME' in program:program['TIME'].value=0
  for pi,p in enumerate(ns['passes']):
   for unit,s in enumerate(ns['samplers']):
    tex=ns['in_tex'] if s in ns['images'] else ns['bufs'][s]['read'];tex.use(unit)
    if s in program:program[s].value=unit
    if '_'+s+'_size' in program:program['_'+s+'_size'].value=tuple(map(float,tex.size))
   t=p.get('TARGET');fbo=ns['fbos'][t]['write'] if t else out;size=ns['bufs'][t]['size'] if t else (640,360)
   fbo.use();ctx.viewport=(0,0,*size);program['RENDERSIZE'].value=tuple(map(float,size))
   if 'PASSINDEX' in program:program['PASSINDEX'].value=pi
   ctx.clear(0,0,0,0);vertex.render(ns['moderngl'].TRIANGLE_STRIP)
   if t:
    ns['bufs'][t]['read'],ns['bufs'][t]['write']=ns['bufs'][t]['write'],ns['bufs'][t]['read']
    ns['fbos'][t]['read'],ns['fbos'][t]['write']=ns['fbos'][t]['write'],ns['fbos'][t]['read']
  return np.frombuffer(out.read(components=4),dtype=np.uint8).reshape(360,640,4)[::-1].copy()
 cases=[(f'home-{i}',home(i/8)) for i in range(8)]
 if d['id']=='figure.solid':
  cases += [(f'corner-{i}',{**home(.3),'sizev':1.,'px':x,'py':y,'shadow':.1,'tumble':.17*i}) for i,(x,y) in enumerate([(0,0),(0,1),(1,0),(1,1)])]
 if d['id']=='figure.shell':
  cases += [(f'sphere-perspective-{v}',{**home(.3),'figA':1,'figB':1,'morph':0.,'sizev':1.,'persp':v,'thick':1.,'layers':32.,'spread':0.,'drift':0.,'wpos':0.,'edgesv':0.,'verts':0.}) for v in [0.,1.]]
  cases += [(f'bars-corner-{i}',{**home(.3),'sizev':1.,'posx':x,'posy':y,'edgesv':1.,'verts':1.,'focus':1.,'persp':float(i%2)}) for i,(x,y) in enumerate([(-1,-1),(-1,1),(1,-1),(1,1)])]
 for label,v in cases:
  im=render(v);ys,xs=np.where(im[:,:,3]>1);edge=max(im[0,:,3].max(),im[-1,:,3].max(),im[:,0,3].max(),im[:,-1,3].max())
  row={'instrument':d['id'],'case':label,'nonempty':bool(len(xs)),'edge_alpha':int(edge),'bounds':list(map(int,[xs.min(),ys.min(),xs.max(),ys.max()])) if len(xs) else None}
  if label=='home-0':Image.fromarray(im).save(OUT/(d['id']+'-source.png'));pictures.append(Image.fromarray(im))
  if d['id']=='figure.shell' and label in ['sphere-perspective-1.0','bars-corner-3']:
   frag=ns['frag'].replace('if (length(uv) > Rc) { gl_FragColor = vec4(0.0); return; }','')
   p2=ctx.program(vertex_shader=ns['vert'],fragment_shader=frag);v2=ctx.simple_vertex_array(p2,ns['vbo'],'p');other=render(v,p2,v2)
   row['unculled_max_difference']=int(np.abs(im.astype(int)-other.astype(int)).max());v2.release();p2.release()
  results.append(row)
 print(d['id'],len(cases),'cases',flush=True)
(OUT/'source-checks.json').write_text(json.dumps({'resolution':[640,360],'method':'raw source alpha at phase and boundary samples; shell compares culling disabled on two stress cases','cases':results},indent=2)+'\n')
sheet=Image.new('RGBA',(640*3,360),(0,0,0,255))
for i,p in enumerate(pictures):sheet.alpha_composite(p,(i*640,0))
sheet.convert('RGB').save(OUT/'source-lineup.png')
fail=[r for r in results if r['edge_alpha'] or not r['nonempty'] or r.get('unculled_max_difference',0)>2]
print('FAILURES',json.dumps(fail))
if fail:sys.exit(1)
