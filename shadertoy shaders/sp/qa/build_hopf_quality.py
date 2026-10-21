"""Build a separate Wire patch exposing the shader's tested quality modes."""
from pathlib import Path
import json,copy,uuid,shutil
root=Path(__file__).resolve().parents[1];dest=root/'patches/Hopf fibers Performance';(dest/'Resource').mkdir(parents=True,exist_ok=True)
src=Path.home()/'Documents/Resolume Wire/Patches/Hopf fibers SP/Hopf fibers SP.wire'
d=json.loads(src.read_text());p=d['patch'];n=copy.deepcopy(p['nodes']['11']);nid=p['nextNodeId'];p['nextNodeId']=nid+1
n['name']='Render Quality';n['bounds']['y']-=100;n['attributes']={k:v for k,v in n['attributes'].items() if not k.startswith('option')}
n['attributes']['options-count']={'type':'integer','value':3};n['attributes']['max']['value']=2
for i,label in enumerate(['Performance','Balanced','Full']):
 n['attributes'][f'option{i}-label']={'type':'string','value':label};n['attributes'][f'option{i}-value']={'type':'integer','value':i}
n['constants']['input']['value']=2;p['nodes'][str(nid)]=n;p['inputOrder']['roots'].insert(0,{'node':nid})
p['connections'].append({'from':[nid,'output'],'to':[0,'renderQuality']})
isf=p['nodes']['0'];isf['constants']['renderQuality']={'type':'integer','value':2}
isf['attributes']['fragment-shader']['value']['value']['inputs'].append({'name':'renderQuality','label':'Render Quality','type':'long','min':0,'max':2,'defaultValue':2,'values':[0,1,2],'labels':['Performance','Balanced','Full']})
p['meta']['displayName']='Hopf fibers Performance';p['meta']['identifier']='39a883ed-26bf-4c10-a5b3-d8f7595bce9f';p['meta']['description']='Hopf fibers with explicit Full, Balanced and Performance sample density. Full preserves the original rendering.'
(dest/'Hopf fibers Performance.wire').write_text(json.dumps(d,indent=1));shutil.copy2(root/'Hopf fibers SP.fs',dest/'Resource/Hopf fibers SP.fs')
print(dest/'Hopf fibers Performance.wire')
