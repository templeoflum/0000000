"""Stage bypassed feedback controls in the approved working composition only."""
from pathlib import Path
import urllib.request,urllib.parse,json
BASE='http://127.0.0.1:8080/api/v1'
def get(path):return json.load(urllib.request.urlopen(BASE+path,timeout=4))
def put(pid,value):
 urllib.request.urlopen(urllib.request.Request(BASE+f'/parameter/by-id/{pid}',data=json.dumps({'value':value}).encode(),method='PUT',headers={'Content-Type':'application/json'}),timeout=4).read()
def post(path,value):
 urllib.request.urlopen(urllib.request.Request(BASE+path,data=value.encode(),method='POST',headers={'Content-Type':'text/plain'}),timeout=8).read()
comp=get('/composition');name=comp['name']['value']
if name!='Heart Performance':raise RuntimeError('Open the Heart Performance working composition first: '+name)
installed=get('/effects')['video']
for display in ['Hue Rotate','Delay RGB','Auto Mask','Mirror']:
 layer=get('/composition/layers/1');current=layer['video']['effects']
 if any(e.get('display_name')==display for e in current):continue
 match=next(e for e in installed if e['name']==display)
 post('/composition/layers/1/effects/video/add','effect:///video/'+urllib.parse.quote(match['name'],safe=''))
 new=get('/composition/layers/1')['video']['effects'][-1]
 put(new['bypassed']['id'],True)
 if 'Opacity' in new['params']:put(new['params']['Opacity']['id'],0)
 print('Staged bypassed',new['name'])
post('/composition/save',(Path(__file__).parent/'Heart Performance.avc').resolve().as_uri())
