"""Prepare an isolated Wire package with explicit Image -> ISF texture binding.
Preserves staged identity and controls; does not write installed or live resources.
"""
from pathlib import Path
import json,copy,shutil,hashlib
ROOT=Path(__file__).resolve().parent
NAME='SP Toy Quasicrystal Figure 01'
SRC=ROOT/'staged'/NAME
DST=ROOT/'packaging-fixed'/NAME
DST.mkdir(parents=True,exist_ok=True)
shutil.copytree(SRC/'Resource',DST/'Resource',dirs_exist_ok=True)
wire=json.loads((SRC/(NAME+'.wire')).read_text()); before=copy.deepcopy(wire)
fs=DST/'Resource'/(NAME+'.fs'); text=fs.read_text(); end=text.index('*/')+2
hdr=json.loads(text[2:end-2]); assert hdr['IMPORTED']=={'toyPoints':{'PATH':'quasicrystal-points.png'}}
del hdr['IMPORTED']; hdr['INPUTS'].append({'NAME':'toyPoints','TYPE':'image','LABEL':'Toy Points (internal)'})
fs.write_text('/*'+json.dumps(hdr,indent=2)+'*/'+text[end:])
# Use the exact node class/version/resource serialization from shipped Wire docs.
template=next(Path('/Applications/Resolume Wire/Documentation/Nodes').glob('* - Image/*.wire'))
doc=json.loads(template.read_text())
node=copy.deepcopy(next(n for n in doc['patch']['nodes'].values() if n['class']['id'].lower()=='77697265-3683-409b-8c89-43afaea9a2b0'))
resource=node['attributes']['image']['value']; resource['path']={'main':'Resource/quasicrystal-points.png','sub':''}
resource['value']['resolution']={'width':800,'height':800}
node['name']='Toy Points Image';node['bounds'].update(x=-300,y=-550)
node['constants']['straight']['value']=True
patch=wire['patch']; nid=patch['nextNodeId']; assert str(nid) not in patch['nodes']
patch['nodes'][str(nid)]=node; patch['nextNodeId']=nid+1
patch['connections'].append({'from':[nid,'output'],'to':[0,'toyPoints']})
isf=patch['nodes']['0'];isf['constants']['toyPoints']={'type':'texture2d','value':None}
isf['attributes']['fragment-shader']['value']['value']['inputs'].append({'name':'toyPoints','type':'image','label':'Toy Points (internal)'})
(DST/(NAME+'.wire')).write_text(json.dumps(wire,indent=2)+'\n')
# Structural contract: no changes to old connections, controls, ordering, identity or point asset.
old=before['patch']
assert patch['connections'][:-1]==old['connections']
assert patch['meta']==old['meta'] and patch['inputOrder']==old['inputOrder']
for k,n in old['nodes'].items():
 if k!='0': assert patch['nodes'][k]==n
assert (DST/'Resource'/'quasicrystal-points.png').read_bytes()==(SRC/'Resource'/'quasicrystal-points.png').read_bytes()
assert fs.read_text().split('*/',1)[1]==(SRC/'Resource'/(NAME+'.fs')).read_text().split('*/',1)[1]
report={'diagnosis':'Original staged wrapper has no toyPoints cached input, constant, connection or image resource node; original shader declared it only via IMPORTED.', 'image_node_template':str(template),'image_node_id':nid,'connection':patch['connections'][-1],'patch_identifier_preserved':patch['meta']['identifier'],'source_body_unchanged':True,'point_png_sha256':hashlib.sha256((DST/'Resource'/'quasicrystal-points.png').read_bytes()).hexdigest(),'controls_and_input_order_unchanged':True,'live_validation':'Not performed by this task; main task owns integration.'}
(ROOT/'evidence'/'packaging-fix.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
