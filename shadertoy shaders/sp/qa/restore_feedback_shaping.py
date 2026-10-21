"""Restore native output shaping on candidate; keep originals and initialize bypassed."""
import json,urllib.request
from pathlib import Path
BASE='http://127.0.0.1:8080/api/v1'
def req(path,method='GET',body=None):
 data=body.encode() if isinstance(body,str) else json.dumps(body).encode() if body is not None else None
 r=urllib.request.Request(BASE+path,data=data,method=method,headers={'Content-Type':'text/plain' if isinstance(body,str) else 'application/json'})
 with urllib.request.urlopen(r,timeout=5) as f:
  raw=f.read();return json.loads(raw) if raw else None
path='/composition/layers/1/clips/6'
source={e['name']:e for e in req('/composition/layers/1/clips/1')['video']['effects']}
assert req(path)['name']['value']=='heart feedback'
report=[]
for name in ['InvertRGB','Blur','Sharpen']:
 effects=req(path)['video']['effects']
 assert not any(e['name']==name for e in effects),f'{name} already present; stop to avoid duplicate'
 req(path+'/effects/video/add','POST','effect:///video/'+{'InvertRGB':'Invert%20RGB','Blur':'Blur','Sharpen':'Sharpen'}[name])
 target=next(e for e in req(path)['video']['effects'] if e['name']==name)
 req('/parameter/by-id/'+str(target['bypassed']['id']),'PUT',{'value':True})
 for group in ['params','mixer']:
  for key,old in (source[name].get(group) or {}).items():
   new=(target.get(group) or {}).get(key)
   if not new or new['valuetype'] not in ('ParamRange','ParamChoice','ParamBoolean'):continue
   val=0.0 if key=='Opacity' else old.get('index') if new['valuetype']=='ParamChoice' else old['value']
   req('/parameter/by-id/'+str(new['id']),'PUT',{'value':val})
 final=next(e for e in req(path)['video']['effects'] if e['name']==name)
 assert final['bypassed']['value'] and final['params']['Opacity']['value']==0,final
 report.append(final);print(name,'restored, bypassed, zero opacity',flush=True)
Path('sp/design/heart-performance-plan/feedback-instrument/restored-native-shaping.json').write_text(json.dumps(report,indent=2))
