import json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent
c=json.load(open('sp/audit/shader-coverage-batch1/deck-1.json'))
schemas=[]
for i in [20,25,38]:
 v=c['layers'][4]['clips'][i-1]['video'];schemas.append({'source':v['description'],'controls':{k:{x:p.get(x) for x in ('valuetype','min','max','options')} for k,p in v['sourceparams'].items()}})
prompt='Return JSON with records, one per source. For each give source, continuous_controls (exact names of ParamRange/Float/Number numeric controls), unsupported_controls (exact names of other types), and note. Do not invent rendered behavior or suitability. Note must say live testing required. Data: '+json.dumps(schemas)
def post(path,data):return json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11434/api/'+path,json.dumps(data).encode(),{'Content-Type':'application/json'}),timeout=150))
try:
 r=post('chat',{'model':'qwen3:8b','messages':[{'role':'user','content':prompt}],'format':'json','stream':False,'think':False,'keep_alive':'2m','options':{'num_ctx':8192,'num_predict':1800,'temperature':0}})
 answer=json.loads(r['message']['content']);checks=[]
 for s in schemas:
  matches=[x for x in answer.get('records',[]) if x.get('source')==s['source']];a=matches[0] if len(matches)==1 else {}
  expected=[k for k,p in s['controls'].items() if p['valuetype'] in ('ParamRange','ParamFloat','ParamNumber')]
  checks.append({'source':s['source'],'exact_continuous_match':a.get('continuous_controls')==expected,'exact_other_match':a.get('unsupported_controls')==[k for k in s['controls'] if k not in expected]})
 (P/'local-review.json').write_text(json.dumps({'answer':answer,'checks':checks},indent=2));print(checks)
finally:post('generate',{'model':'qwen3:8b','keep_alive':0})
