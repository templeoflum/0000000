"""Probe configured Hermes providers. Never serialize credentials or raw errors."""
from pathlib import Path
import sys,os,json,time,contextlib,logging
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path.home()/'.hermes'
sys.path.insert(0,str(ROOT/'hermes-agent'))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env',override=False)
import yaml,requests
logging.disable(logging.CRITICAL)
from hermes_cli.runtime_provider import resolve_runtime_provider
cfg=yaml.safe_load((ROOT/'config.yaml').read_text())
items=[]
for alias,spec in cfg['model'].get('aliases',{}).items():
 if isinstance(spec,dict):items.append((alias,spec['provider'],spec['model']))
 elif spec.startswith('nous/'):items.append((alias,'nous',spec.removeprefix('nous/')))
for p in ['nvidia','deepinfra','copilot']:items.append((p,p,None))
if len(sys.argv)>1:items=[x for x in items if x[0] in sys.argv[1:]]
# Resolve serially: Hermes may refresh stored OAuth credentials.
resolved=[];results=[]
for alias,provider,model in items:
 try:
  with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
   r=resolve_runtime_provider(requested=provider,target_model=model)
  if not r.get('api_key'):raise ValueError('missing credential')
  resolved.append((alias,provider,model,r))
 except Exception as e:results.append({'alias':alias,'provider':provider,'model':model,'status':'credential resolution failed','error_type':type(e).__name__})

def probe(item):
 alias,provider,model,r=item;t=time.monotonic();out={'alias':alias,'provider':provider,'model':model}
 headers={'Authorization':'Bearer '+r['api_key'],'Content-Type':'application/json'}
 base=r['base_url'].rstrip('/')
 mode=r.get('api_mode','chat_completions')
 from urllib.parse import urlsplit
 out['host']=urlsplit(base).hostname;out['api_mode']=mode
 try:
  if model is None:
   response=requests.get(base+'/models',headers=headers,timeout=(5,12))
   if response.status_code!=200:out.update(status='model discovery failed',http=response.status_code);return out
   entries=response.json().get('data',[])
   candidates=[m['id'] for m in entries if m.get('id') and not any(x in m['id'].lower() for x in ['embed','rerank','whisper','tts','vision','image','guard'])]
   if not candidates:out['status']='no text models discovered';return out
   preferred=[m for m in candidates if any(x in m.lower() for x in ['llama-3.3-70b-instruct','qwen3-coder','gpt-4o-mini','gpt-4.1-mini'])]
   model=(preferred or candidates)[0];out['model']=model
  prompt='Reply with exactly HEART_OK. No explanation.'
  if mode=='anthropic_messages':
   path='/messages';headers['x-api-key']=r['api_key'];headers['anthropic-version']='2023-06-01';payload={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':256}
  elif mode in ['codex_responses','responses']:
   path='/responses';payload={'model':model,'input':prompt,'max_output_tokens':256,'store':False}
  else:
   path='/chat/completions';payload={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':256,'stream':False}
  response=requests.post(base+path,headers=headers,json=payload,timeout=(5,18));out['http']=response.status_code
  if response.status_code!=200:
   out['status']={401:'authentication rejected',403:'access denied',402:'credit/payment required',404:'model or route unavailable',429:'quota/rate limited',400:'request rejected',503:'provider unavailable'}.get(response.status_code,'HTTP error');return out
  data=response.json()
  if path=='/messages':text=''.join(b.get('text','') for b in data.get('content',[]))
  elif path=='/responses':text=''.join(b.get('text','') for a in data.get('output',[]) for b in a.get('content',[]))
  else:text=(data.get('choices') or [{}])[0].get('message',{}).get('content') or ''
  out['status']='PASS' if text.strip()=='HEART_OK' else 'responded; unexpected/empty text'
  out['reply_chars']=len(text)
 except requests.Timeout:out['status']='timeout'
 except Exception as e:out.update(status='request failed',error_type=type(e).__name__)
 finally:out['seconds']=round(time.monotonic()-t,2)
 return out
with ThreadPoolExecutor(max_workers=6) as pool:
 for result in pool.map(probe,resolved):results.append(result);print(json.dumps(result),flush=True)
p=Path(__file__).parent/('smoke-retry.json' if len(sys.argv)>1 else 'smoke-results.json');p.write_text(json.dumps(results,indent=2)+'\n')
for r in results:
 if r['status']=='credential resolution failed':print(json.dumps(r),flush=True)
