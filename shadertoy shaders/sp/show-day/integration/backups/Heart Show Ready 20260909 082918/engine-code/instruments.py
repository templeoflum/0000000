"""Shared, declarative instrument definitions over Heart's existing parameter engine.

Definitions use durable native source IDs for preflight/provenance. Arena's live
source descriptions select the adapter; the source ID must be verified from native
readback before promoting a new definition. Runtime parameter IDs are never saved.
"""
import copy
import json
from pathlib import Path

PATH=Path(__file__).with_name('instruments.json')

def load(path=PATH):
    with Path(path).open() as f:data=json.load(f)
    if data.get('version')!=1:raise ValueError('Unsupported instrument catalog')
    seen=set()
    for d in data['instruments']:
        key=(d['role'],d['source']['description'])
        if key in seen or not d['source'].get('native_id'):raise ValueError('Ambiguous instrument identity')
        seen.add(key)
        if d.get('framing',{}).get('scope')!='source':raise ValueError('Figure framing must be source-only')
        for b in d['home']['bindings'].values():
            lo,hi=b['range']
            if not 0<=lo<=hi<=1 or not 0<=b['center']<=1:raise ValueError('Home uses normalized parameter values')
    return data['instruments']

CATALOG=load()

def get(role,description):
    return next((d for d in CATALOG if d['role']==role and d['source']['description']==description),None)

def atom_defaults():
    out={}
    for d in CATALOG:
        params={'_global':{'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.}}
        for n,b in d['home']['bindings'].items():
            params[n]={'cyclic':b.get('cyclic',False),'drive':False,'ratio':'1:4','mult':1.,'offset':0.,'shape':b.get('shape',1),'lo':b['range'][0],'hi':b['range'][1],'lock':False}
        out[d['source']['description']]=params
    return out

def home(role,description):
    d=get(role,description)
    return copy.deepcopy(d['home']) if d else None

def summary(role,description):
    d=get(role,description)
    return {k:copy.deepcopy(d[k]) for k in ('id','label','family','framing','primary_controls','status')} if d else None

def bank(role,clips):
    descriptions={d['source']['description']:d for d in CATALOG if d['role']==role}
    return [{**c,'name':descriptions[c.get('source')]['label']} for c in clips if c.get('source') in descriptions]
