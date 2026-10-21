from pathlib import Path
import subprocess,json
from PIL import Image
P=Path(__file__).resolve().parent;rows=[]
for i,(fold,phase,twist) in enumerate([(f,p,t) for f in [0.,1.] for p in [0.,.25,.5,.75] for t in [0.,.5,1.]]):
 out=P/f'case-{i}.png';cmd=['sp/qa/.venv/bin/python','sp/render_isf_fb.py','sp/Heart Melting Fractal.fs','-o',str(out),'-w','480','-H','270','--frames','1','--rgba','--set',f'foldOffset={fold}','--set',f'animSpeed={phase}','--set',f'rotMix={twist}'];subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL);im=Image.open(out);a=im.getchannel('A');rows.append(dict(fold=fold,phase=phase,twist=twist,bounds=a.getbbox()))
(P/'cases.json').write_text(json.dumps(rows,indent=2));print(rows)
