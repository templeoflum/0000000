#!/usr/bin/env python3
"""make_atoms.py — learn every SP clip from the LIVE composition and give it a card: each numeric knob a slot, each picker
a picker slot, drive off; phase-type knobs cyclic. Keyed by Arena's own names (source description / effect name), so
the heart matches by what Arena reports. Existing entries keep their tuned config; only new knobs are added."""
import json, os, urllib.request
B="http://localhost:8080/api/v1"; H=os.path.dirname(os.path.abspath(__file__)); F=os.path.join(H,"atoms.json")
CYCLIC={"Turn","Spin","Double","Sweep","Travel","Hue","Sun","Tilt","Yaw","Angle","Phase","Rotate","Flow","Drift X"}
A=json.load(open(F)) if os.path.exists(F) else {}
comp=json.load(urllib.request.urlopen(B+"/composition"))
def slots_from(params):
    out={}
    for k,v in (params or {}).items():
        if not (isinstance(v,dict) and 'valuetype' in v): continue
        t=v['valuetype']
        if t=='ParamChoice': out[k]={"cyclic":False,"ratio":"1:4","mult":1,"offset":0.0,"shape":0,"lo":0.0,"hi":1.0,"drive":False,"choice":True}
        elif t in ('ParamRange','ParamFloat','ParamInt'): out[k]={"cyclic":k in CYCLIC,"ratio":"1:4","mult":1,"offset":0.0,"shape":0 if k in CYCLIC else 1,"lo":0.0,"hi":1.0,"drive":False}
    return out
added={}
for l in comp['layers']:
    for c in l['clips']:
        v=c.get('video') or {}
        if not c['name']['value'] or not v: continue
        desc=v.get('description') or ''
        if desc.startswith('SP '): 
            sec=A.setdefault(desc,{"_global":{"pattern":0,"seed":0,"spread":1,"depth":1.0,"fm":0.0}})
            for k,s in slots_from(v.get('sourceparams')).items():
                if k not in sec: sec[k]=s; added.setdefault(desc,[]).append(k)
        for e in v.get('effects') or []:
            if e['name'].startswith('SP') and e['name']!='Transform':
                sec=A.setdefault(e['name'],{"_global":{"pattern":0,"seed":0,"spread":1,"depth":1.0,"fm":0.0}})
                for k,s in slots_from(e.get('params')).items():
                    if k=='Opacity' or k not in sec and k in sec: continue
                    if k not in sec: sec[k]=s; added.setdefault(e['name'],[]).append(k)
json.dump(A,open(F,"w"),indent=1)
for k,v in added.items(): print(f"{k}: +{len(v)}  {v}")
print("sections:", len(A))
