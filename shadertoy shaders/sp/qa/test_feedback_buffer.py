"""GPU state tests using the same multipass host as the existing shader renderer."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
shader=ROOT/'patches/SP Heart Feedback/Resource/SP Heart Feedback.fs'
sys.argv=['render_isf_fb.py',str(shader),'-o','/tmp/unused-feedback.png','-w','320','-H','180']
# Reuse the existing ISF compiler/buffer allocation; own the frame sequence below.
host=(ROOT/'render_isf_fb.py').read_text().split('strip = []; keep =',1)[0]
exec(compile(host,str(ROOT/'render_isf_fb.py'),'exec'),globals())
reset_serial=0
def frame(image,**values):
 global reset_serial
 if values.pop('clearHistory',False):
  reset_serial+=1;values['shufReset']=float(reset_serial)
 for k,v in values.items():
  if k in prog:prog[k].value=v
 in_tex.write(image.tobytes())
 for pi,p in enumerate(passes):
  target=p.get('TARGET')
  for unit,s in enumerate(samplers):
   tx=in_tex if s in images else bufs[s]['read'];tx.use(unit)
   if s in prog:prog[s].value=unit
   if f'_{s}_size' in prog:prog[f'_{s}_size'].value=tx.size
  fbo=fbos[target]['write'] if target else out_fbo
  fbo.use();size=bufs[target]['size'] if target else (320,180);ctx.viewport=(0,0,*size);prog['PASSINDEX'].value=pi;prog['RENDERSIZE'].value=size
  vao.render(moderngl.TRIANGLE_STRIP)
  if target:
   bufs[target]['read'],bufs[target]['write']=bufs[target]['write'],bufs[target]['read']
   fbos[target]['read'],fbos[target]['write']=fbos[target]['write'],fbos[target]['read']
 return np.frombuffer(out_fbo.read(components=4),dtype=np.uint8).reshape(180,320,4)[:,:,:3].copy()
blank=np.zeros((180,320,4),dtype=np.uint8);seed=blank.copy();seed[60:100,120:180]=[180,60,20,255]
results=[]
for name,fx in [('neutral',{}),('loop effects',dict(hueStep=7.,invertMix=.4,foldMix=.6,detail=.3))]:
 frame(blank,clearHistory=True,**fx)
 seeded=frame(seed,clearHistory=False,gainv=1.,zoomv=1.,rotz=0.,floorv=0.)
 trail=frame(blank)
 assert trail.max()>0,'Fixture must contain actual stored history'
 cleared=frame(seed,clearHistory=True)
 assert not cleared.any(),'Clear must empty output even with a live seed'
 assert not np.frombuffer(bufs['acc']['read'].read(),dtype=np.uint8).any(),'Persistent acc must be zero'
 for _ in range(6):assert not frame(blank,clearHistory=False).any(),'Old history must not return'
 fresh=frame(seed)
 assert np.array_equal(fresh,seed[:,:,:3]),'Live signal must return cleanly after reset'
 results.append(dict(case=name,seed_max=int(seeded.max()),history_max=int(trail.max()),reset_zero=True,release_stays_zero=True,fresh_input_exact=True))
# Demonstrate that hue modifies stored history, while current input remains exact.
frame(blank,clearHistory=True,hueStep=0.,invertMix=0.,foldMix=0.,detail=0.)
frame(seed,clearHistory=False);plain=frame(blank)
frame(blank,clearHistory=True);frame(seed,clearHistory=False);tinted=frame(blank,hueStep=10.)
assert np.abs(plain.astype(int)-tinted.astype(int)).sum()>0
results.append(dict(case='hue changes stored history',passed=True))
path=ROOT/'design/heart-performance-plan/feedback-buffer-tests.json';path.write_text(json.dumps(results,indent=2));print(json.dumps(results))
