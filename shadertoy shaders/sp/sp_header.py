"""sp_header.py — build ISF INPUTS for smart-param slots + emit the shared GLSL block."""
import json,os
HERE=os.path.dirname(os.path.abspath(__file__))
CYC={}
RATIO_LABELS=["1:1","1:2","1:4","2:3","3:4","4:5","5:6","3:5","1/phi","1/sqrt2","1/pi","1:3","2:5","5:8","8:13","3:2"]
def slot(n,label,default=0.5,drive=False,ratio=0,mult=1.0,shape=1,cyclic=False):
    CYC[n]=cyclic
    return [
     {"NAME":n,          "LABEL":label,            "TYPE":"float","DEFAULT":default,"MIN":0.0,"MAX":1.0},
     {"NAME":n+"Drive",  "LABEL":label+" Drive",   "TYPE":"bool", "DEFAULT":drive},
     {"NAME":n+"Lock",   "LABEL":label+" Lock",    "TYPE":"bool", "DEFAULT":False},
     {"NAME":n+"Ratio",  "LABEL":label+" Ratio",   "TYPE":"long", "DEFAULT":ratio,"VALUES":list(range(16)),"LABELS":RATIO_LABELS},
     {"NAME":n+"Mult",   "LABEL":label+" Mult",    "TYPE":"float","DEFAULT":mult,"MIN":-16.0,"MAX":16.0},
     {"NAME":n+"Offset", "LABEL":label+" Offset",  "TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":1.0},
     {"NAME":n+"Shape",  "LABEL":label+" Shape",   "TYPE":"long", "DEFAULT":shape,"VALUES":[0,1],"LABELS":(["rotate","sway"] if cyclic else ["triangle","cosine"])},
     {"NAME":n+"Lo",     "LABEL":label+" Lo",      "TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":1.0},
     {"NAME":n+"Hi",     "LABEL":label+" Hi",      "TYPE":"float","DEFAULT":1.0,"MIN":0.0,"MAX":1.0},
    ]
PATTERN_LABELS=["per-slot","unison","near-unison","harmonic","just intonation","septimal","undecimal","powers of 2","powers of 3","cross-base 2v3","pendulum wave","fibonacci","lucas","coprime primes","prime stacks","CF approximants","metallic","near-phi","irrationals"]
ROOT=[{"NAME":"heartRate","LABEL":"Heart Rate (turns/s)","TYPE":"float","DEFAULT":0.1,"MIN":0.0,"MAX":2.0},
      {"NAME":"pattern","LABEL":"Pattern","TYPE":"long","DEFAULT":11,"VALUES":list(range(19)),"LABELS":PATTERN_LABELS},
      {"NAME":"seed","LABEL":"Seed","TYPE":"long","DEFAULT":0,"VALUES":list(range(32)),"LABELS":[str(i) for i in range(32)]},
      {"NAME":"spread","LABEL":"Spread","TYPE":"long","DEFAULT":1,"VALUES":list(range(1,9)),"LABELS":[str(i) for i in range(1,9)]},
      {"NAME":"depth","LABEL":"Depth","TYPE":"float","DEFAULT":1.0,"MIN":0.0,"MAX":1.0},
      {"NAME":"fm","LABEL":"FM","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":1.0},
      {"NAME":"shufTiming","LABEL":"Shuffle Timing","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufPattern","LABEL":"Shuffle Pattern","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufMotion","LABEL":"Shuffle Motion","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufRange","LABEL":"Shuffle Range","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufDrives","LABEL":"Shuffle Drives","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufLook","LABEL":"Shuffle Look","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0},
      {"NAME":"shufAll","LABEL":"Shuffle All","TYPE":"float","DEFAULT":0.0,"MIN":0.0,"MAX":9999.0}]
def call(n,i): return f"sp({n}, {n}Drive, {n}Lock, {'true' if CYC.get(n) else 'false'}, H, {i}, {n}Ratio, {n}Mult, {n}Offset, {n}Shape, {n}Lo, {n}Hi)"
def groups(slots):
    """sidecar spec: {group name: [input names]} — build_wrapper collapses these"""
    return {f"{lab} drive": [n+s for s in ("Ratio","Mult","Offset","Shape","Lo","Hi")] for n,lab in slots}
HEART_OLD=[{"NAME":"heartRate","LABEL":"Heart Rate (turns/s)","TYPE":"float","DEFAULT":0.1,"MIN":0.0,"MAX":2.0},
       {"NAME":"speed","LABEL":"Speed","TYPE":"float","DEFAULT":1.0,"MIN":0.0,"MAX":3.0}]
def block(): return open(os.path.join(HERE,"sp.glsl")).read()
def emit(desc,credit,inputs,body,name,grp=None):
    hdr={"DESCRIPTION":desc,"CREDIT":credit,"ISFVSN":"2","CATEGORIES":["Generator"],"INPUTS":inputs}
    out="/*"+json.dumps(hdr,indent=2)+"*/\n"+block()+body
    D=os.path.expanduser(f"~/Documents/Resolume Wire/Patches/{name}/Resource"); os.makedirs(D,exist_ok=True)
    open(f"{D}/{name}.fs","w").write(out); open(os.path.join(HERE,f"{name}.fs"),"w").write(out)
    json.dump(grp or {},open(f"{D}/{name}.sp.json","w"),indent=1)
    return f"{D}/{name}.fs"
