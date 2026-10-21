"""Small verified tool-use benchmark; no live VJ tools or arbitrary file access."""
from pathlib import Path
import sys,os,json,time,re,logging,contextlib,threading,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
OUT=Path(__file__).resolve().parent
SOURCE=(OUT.parent/'ollama/pilot/Ground.fs').read_text()
HEADER=json.loads(SOURCE.split('/*',1)[1].split('*/',1)[0])
EXPECTED={x['NAME']:x['TYPE'] for x in HEADER['INPUTS']}
TOOLS=[{'type':'function','function':{'name':'read_shader','description':'Read the complete Ground shader being audited. Only this fixture is available.','parameters':{'type':'object','properties':{}}}},
{'type':'function','function':{'name':'submit_audit','description':'Submit facts grounded in the shader source.','parameters':{'type':'object','properties':{
'inputs':{'type':'array','items':{'type':'object','properties':{'name':{'type':'string'},'type':{'type':'string'}},'required':['name','type']}},
'uses_TIME':{'type':'boolean'},'scale_type':{'type':'string'},'scale_continuous':{'type':'boolean'},
'camZ_expression':{'type':'string','description':'Exact RHS of the camZ assignment, without semicolon.'},
'f_expression':{'type':'string','description':'Exact RHS of the f_ assignment, without semicolon.'},
'haze_less_instructions':{'type':'boolean','description':'Does simply reducing haze reduce executed GLSL instructions on the ground path?'}},
'required':['inputs','uses_TIME','scale_type','scale_continuous','camZ_expression','f_expression','haze_less_instructions']}}}]
PROMPT='Use read_shader to inspect Ground.fs. Then use submit_audit to report its inputs and facts. Scale means the input labeled Scale. Do not guess performance benefits from visual simplicity. No other tools or external data are available.'
MODELS=['qwen3-coder:30b','gemma4:12b','qwen3:8b']

def grade(a):
 norm=lambda x:re.sub(r'\s+','',str(x)).rstrip(';')
 inv={x.get('name'):x.get('type') for x in a.get('inputs',[]) if isinstance(x,dict)}
 return {'inputs':inv==EXPECTED and len(a.get('inputs',[]))==len(EXPECTED),'TIME':a.get('uses_TIME') is False,
 'scale_type':a.get('scale_type')=='float','continuous':a.get('scale_continuous') is True,
 'travel':norm(a.get('camZ_expression'))==norm('travel * 4.0 + D'),'scale_expression':norm(a.get('f_expression'))==norm('2.0 + scalev * 18.0'),
 'performance':a.get('haze_less_instructions') is False}

def run(label,model,config,local=False):
 start=time.monotonic();deadline=start+150;msgs=[{'role':'user','content':PROMPT}];events=[];answer=None;tokens=0
 result={'label':label,'model':model,'local':local}
 try:
  for turn in range(4):
   remaining=deadline-time.monotonic()
   if remaining<=0:raise TimeoutError()
   if local:
    url='http://127.0.0.1:11434/api/chat';headers={};body={'model':model,'messages':msgs,'tools':TOOLS,'stream':False,'think':False,'keep_alive':'5m','options':{'num_ctx':8192,'num_predict':1400,'temperature':0}}
   else:
    url=config['base_url'].rstrip('/')+'/chat/completions';headers={'Authorization':'Bearer '+config['api_key']};body={'model':model,'messages':msgs,'tools':TOOLS,'max_tokens':1800,'stream':False}
   response=requests.post(url,headers=headers,json=body,timeout=(8,max(1,min(100,remaining))))
   if response.status_code!=200:result.update(status='HTTP error',http=response.status_code);break
   data=response.json();msg=data['message'] if local else data['choices'][0]['message'];tokens+=data.get('eval_count',0) if local else data.get('usage',{}).get('completion_tokens',0)
   calls=msg.get('tool_calls') or [];msgs.append(msg)
   if not calls:
    result['status']='no tool call';result['text_excerpt']=(msg.get('content') or '')[:300];break
   for idx,call in enumerate(calls):
    fn=call.get('function',{});name=fn.get('name');args=fn.get('arguments',{})
    if isinstance(args,str):args=json.loads(args)
    events.append(name)
    if name=='submit_audit':answer=args;break
    value=SOURCE if name=='read_shader' else 'Unknown tool; only read_shader and submit_audit exist.'
    toolmsg={'role':'tool','content':value}
    if local:toolmsg['tool_name']=name
    else:toolmsg['tool_call_id']=call['id']
    msgs.append(toolmsg)
   if answer is not None:
    checks=grade(answer);result.update(status='complete',checks=checks,score=sum(checks.values()),max_score=len(checks),tool_pass=events==['read_shader','submit_audit'],answer=answer);break
  else:result['status']='turn limit'
 except (requests.Timeout,TimeoutError):result['status']='timeout'
 except Exception as e:result.update(status='error',error_type=type(e).__name__)
 result.update(seconds=round(time.monotonic()-start,2),tool_calls=events,output_tokens=tokens)
 return result

def local():
 results=[];snapshots=[];stop=threading.Event()
 def monitor():
  while not stop.is_set():
   try:
    d=requests.get('http://127.0.0.1:11434/api/ps',timeout=2).json()
    snapshots.append({'t':round(time.monotonic(),3),'models':[{'name':m['name'],'size_vram':m.get('size_vram'),'context_length':m.get('context_length')} for m in d.get('models',[])]})
   except Exception:pass
   stop.wait(1)
 thread=threading.Thread(target=monitor,daemon=True);thread.start()
 def unload(model):
  try:requests.post('http://127.0.0.1:11434/api/generate',json={'model':model,'keep_alive':0},timeout=15)
  except Exception:pass
 try:
  # Sequential cold runs and concurrent cold runs; unload between conditions.
  groups=[('solo-coder',[MODELS[0]]),('solo-gemma',[MODELS[1]]),('solo-qwen8',[MODELS[2]]),('pair',MODELS[:2]),('trio',MODELS)]
  for name,models in groups:
   start=time.monotonic();print('Starting '+name,flush=True)
   with ThreadPoolExecutor(max_workers=len(models)) as pool:
    group=list(pool.map(lambda m:run(name,m,{},True),models))
   elapsed=round(time.monotonic()-start,2)
   for r in group:r['group_seconds']=elapsed;results.append(r);print(json.dumps({k:v for k,v in r.items() if k not in ['answer','text_excerpt']}),flush=True)
   (OUT/'local.json').write_text(json.dumps(results,indent=2));(OUT/'residency.json').write_text(json.dumps(snapshots,indent=2))
   for model in models:unload(model)
 finally:
  stop.set();thread.join(timeout=3)
  for model in MODELS:unload(model)
if __name__=='__main__': local()
