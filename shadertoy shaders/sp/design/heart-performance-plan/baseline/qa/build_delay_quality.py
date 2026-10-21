"""Preserve delay timing and taps, halve only the 480-frame history texture dimensions."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];src=Path.home()/'Documents/Resolume Wire/Patches/SP Delay Chain/SP Delay Chain.wire'
d=json.loads(src.read_text());p=d['patch'];nid=p['nextNodeId'];p['nextNodeId']=nid+1
attr=lambda t,v:{'type':t,'value':v}
p['nodes'][str(nid)]={'attributes':{'input0-type':attr('type','texture2d'),'instances':attr('integer',1),'resolution-mode':attr('integer',0),'resolution-relative':attr('float2',[.5,.5]),'resolution-absolute':attr('float2',[960,540]),'bitdepth':attr('integer',0),'sampling':attr('integer',1)},'bounds':{'height':82,'width':180,'x':-300,'y':-120},'class':{'id':'77697265-A4AE-41FA-8316-8C0D54BC55B7','version':1},'clock':'video','color':'ffff6a00','constants':{'input0':attr('texture2d',None)},'hidden':['input0-type','instances','resolution-mode','resolution-relative','resolution-absolute','bitdepth','sampling'],'name':'To Texture','thumbnail_visible':True}
edge=next(e for e in p['connections'] if e['from']==[0,'output'] and e['to']==[1,'input0']);edge['from']=[nid,'output0'];p['connections'].append({'from':[0,'output'],'to':[nid,'input0']})
p['meta']['displayName']='SP Delay Performance';p['meta']['identifier']='99858897-b5a1-418d-aafe-335bb5d605a7';p['meta']['description']='SP Delay Chain with half-width/half-height history textures. Same tap timing, span and color delays. Softer echoes; current frame and final mix retain full resolution.'
dest=root/'patches/SP Delay Performance';dest.mkdir(parents=True,exist_ok=True);(dest/'SP Delay Performance.wire').write_text(json.dumps(d,indent=1));print(dest)
