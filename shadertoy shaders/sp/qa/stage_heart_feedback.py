"""Preserve current live composition, stage an unplayed clone with a new feedback effect."""
from pathlib import Path
import urllib.request,json,time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/heart-performance-plan/feedback-instrument';OUT.mkdir(exist_ok=True)
B='http://127.0.0.1:8080/api/v1'
def req(path,method='GET',value=None,kind='text/plain'):
 data=None if value is None else (json.dumps(value) if kind=='application/json' else str(value)).encode()
 with urllib.request.urlopen(urllib.request.Request(B+path,data=data,method=method,headers={'Content-Type':kind}),timeout=8) as r:
  raw=r.read();return json.loads(raw) if raw else None
c=req('/composition');row=c['layers'][0]['clips'];col=next(i+1 for i,x in enumerate(row) if not x.get('video'))
backup=OUT/('before-'+time.strftime('%Y%m%d-%H%M%S')+'.avc');req('/composition/save','POST',backup.as_uri())
(OUT/'before-live.json').write_text(json.dumps(c,indent=2))
req('/composition/save','POST',(OUT/'Feedback instrument.avc').as_uri())
p=f'/composition/layers/1/clips/{col}'
req(p+'/insert','POST',['composition:///composition/layers/1/clips/1?operation=copy'],'application/json')
clone=req(p)
# Remove effects only from the verified, unplayed new copy. Preserve the original map clip.
assert not clone['connected']['value'].startswith('Connected')
for i in range(len(clone['video']['effects'])-1,-1,-1):
 if clone['video']['effects'][i]['name']!='Transform':req(p+f'/effects/video/{i}','DELETE')
req(p+'/effects/video/add','POST','effect:///video/SP%20Heart%20Feedback')
clone=req(p);req('/parameter/by-id/'+str(clone['name']['id']),'PUT',{'value':'heart feedback'},'application/json')
req('/composition/save','POST',(OUT/'Feedback instrument.avc').as_uri())
(OUT/'staged.json').write_text(json.dumps({'layer':1,'col':col,'backup':str(backup),'effect':clone['video']['effects']},indent=2))
print('Staged unplayed Heart Feedback at L1C'+str(col));print([(e['name'],list(e['params'])) for e in clone['video']['effects']])
