#!/usr/bin/env python3
"""build_wrapper.py <patch name> — build/refresh <Patches>/<name>/<name>.wire from
<Patches>/<name>/Resource/<name>.fs. One In node per ISF input (float/bool/long),
wired to the ISF node; Transport Time -> time; Texture Out. Fresh identifier per patch."""
import json,re,sys,os,uuid,copy
P=os.path.expanduser("~/Documents/Resolume Wire/Patches")
TEMPLATE=f"{P}/Gentle Rings/Gentle Rings.wire"
CLS={"float":("77697265-D235-4A6A-B661-02ABE55C72FF",4),
     "bool": ("77697265-999C-4F8B-8B9D-3646DC68AA69",0),
     "long": ("77697265-2649-4abb-b38f-4e1005183415",0)}
def build(name,cat="source"):
    fs=f"{P}/{name}/Resource/{name}.fs"
    s=open(fs).read(); hdr=json.loads(re.search(r'/\*(\{.*?\})\*/',s,re.S).group(1))
    t=json.load(open(TEMPLATE)); patch=t['patch']
    isf=copy.deepcopy(patch['nodes']['0']); tex=copy.deepcopy(patch['nodes']['1']); clk=copy.deepcopy(patch['nodes']['2'])
    tmpl_float=copy.deepcopy(patch['nodes']['25'])
    isf['attributes']['fragment-shader']['value']['path']['main']=f"Resource/{name}.fs"
    cached=[]; consts={"bypass":{"type":"bool","value":False},"time":{"type":"float","value":0}}
    nodes={"0":isf,"1":tex,"2":clk}; conns=[{"from":[2,"seconds"],"to":[0,"time"]},{"from":[0,"output"],"to":[1,"input"]}]
    roots=[]; nid=10; y=-300
    for inp in hdr["INPUTS"]:
        ty=inp["TYPE"]; n=inp["NAME"]; lab=inp.get("LABEL",n)
        if ty=="image":   # Texture In → ISF image input (mirrored from QuarternionLens effect patch)
            tin={"attributes":{"flow":{"type":"flow","value":"signal"},"instances":{"type":"integer","value":1}},"bounds":{"height":82,"width":130,"x":-420,"y":y},
                 "class":{"id":"77697265-B2A2-4C1C-8C4C-2915D78CC8E9","version":1},"clock":"video","color":"ffff6a00",
                 "constants":{"input":{"type":"texture2d","value":None}},"hidden":["flow","instances"],"name":lab,"thumbnail_visible":True}
            y+=95; nodes[str(nid)]=tin; conns.append({"from":[nid,"output"],"to":[0,n]})
            cached.append({"name":n,"type":"image"}); consts[n]={"type":"texture2d","value":None}
            roots.append({"node":nid}); nid+=1; continue
        if ty not in CLS: continue
        if n.startswith("shuf"):   # shuffle button: Trigger In → Counter(step 1) → ISF float input
            trig={"attributes":{"flow":{"type":"flow","value":"event"},"instances":{"type":"integer","value":1}},"bounds":{"height":82,"width":150,"x":-420,"y":y},
                  "class":{"id":"77697265-e61f-42c0-862a-0dca04e14569","version":1},"clock":"video","color":"ffff6a00",
                  "constants":{"input":{"type":"trigger","value":None}},"hidden":["instances","flow"],"name":lab,"thumbnail_visible":True}
            cnt={"attributes":{"instances":{"type":"integer","value":1},"output0-flow":{"type":"flow","value":"event"},"reset-flow":{"type":"flow","value":"event"},
                  "start-flow":{"type":"flow","value":"signal"},"step-flow":{"type":"flow","value":"signal"},"trigger-flow":{"type":"flow","value":"event"}},
                 "bounds":{"height":82,"width":150,"x":-240,"y":y},"class":{"id":"77697265-CD8C-4E66-8603-3011D462906C","version":2},"clock":"video","color":"ff6a6a6a",
                 "constants":{"reset":{"type":"trigger","value":None},"start":{"type":"float","value":0},"step":{"type":"float","value":1},"trigger":{"type":"trigger","value":None}},
                 "hidden":["trigger-flow","reset-flow","start-flow","step-flow","output0-flow","instances"],"name":lab+" Counter","thumbnail_visible":True}
            y+=95
            nodes[str(nid)]=trig; nodes[str(nid+1)]=cnt
            conns.append({"from":[nid,"output"],"to":[nid+1,"trigger"]}); conns.append({"from":[nid+1,"output0"],"to":[0,n]})
            cached.append({"defaultValue":0,"label":lab,"max":9999,"min":0,"name":n,"type":"float"}); consts[n]={"type":"float","value":0}
            roots.append({"node":nid}); nid+=2; continue
        node=copy.deepcopy(tmpl_float); cid,ver=CLS[ty]; node['class']={"id":cid,"version":ver}
        node['name']=lab; node['bounds']={"height":82,"width":150,"x":-420,"y":y}; y+=95
        a=node['attributes']
        if ty=="float":
            a['min']['value']=inp.get("MIN",0); a['max']['value']=inp.get("MAX",1)
            node['constants']={"input":{"type":"float","value":inp.get("DEFAULT",0)}}
            cached.append({"defaultValue":inp.get("DEFAULT",0),"label":lab,"max":inp.get("MAX",1),"min":inp.get("MIN",0),"name":n,"type":"float"})
            consts[n]={"type":"float","value":inp.get("DEFAULT",0)}
        elif ty=="bool":
            node['attributes']={"flow":a['flow'],"instances":a['instances']}; node['hidden']=["flow","input","instances"]
            node['constants']={"input":{"type":"bool","value":bool(inp.get("DEFAULT",False))}}
            cached.append({"defaultValue":bool(inp.get("DEFAULT",False)),"label":lab,"name":n,"type":"bool"})
            consts[n]={"type":"bool","value":bool(inp.get("DEFAULT",False))}
        else:  # long → Int In, mirrored exactly from Wire's own Acos "Function" node (signal-flow dropdown)
            vals=inp.get("VALUES",[0,1]); labs=inp.get("LABELS")
            node['class']={"id":cid,"version":2}
            a={"flow":{"type":"flow","value":"signal"},"has-max":{"type":"bool","value":True},"has-min":{"type":"bool","value":True},
               "instances":{"type":"integer","value":1},"max":{"type":"integer","value":int(max(vals))},"min":{"type":"integer","value":int(min(vals))},
               "options-count":{"type":"integer","value":0},"unit":{"type":"integer","value":0},"widget":{"type":"integer","value":0}}
            hidden=["input","instances","flow","has-min","min","has-max","max","options-count","widget"]
            if labs and len(labs)==len(vals):
                a["options-count"]["value"]=len(vals)
                for j,(v,l) in enumerate(zip(vals,labs)):
                    a[f"option{j}-label"]={"type":"string","value":str(l)}; a[f"option{j}-value"]={"type":"integer","value":int(v)}
                    hidden+=[f"option{j}-label",f"option{j}-value"]
            node['attributes']=a; node['hidden']=hidden
            node['constants']={"input":{"type":"integer","value":int(inp.get("DEFAULT",0))}}
            cached.append({"defaultValue":int(inp.get("DEFAULT",0)),"label":lab,"max":max(vals),"min":min(vals),"name":n,"type":"long","values":vals,"labels":inp.get("LABELS",[str(v) for v in vals])})
            consts[n]={"type":"integer","value":int(inp.get("DEFAULT",0))}
        nodes[str(nid)]=node; conns.append({"from":[nid,"output"],"to":[0,n]}); roots.append({"node":nid}); nid+=1
    isf['attributes']['fragment-shader']['value']['value']['inputs']=cached; isf['constants']=consts
    # ── groups (collapsed) from the sidecar <name>.sp.json: {group name: [input names]} ──
    byname={c['name']:nodes_id for c,nodes_id in zip(cached,[r['node'] for r in roots])}
    groups={}; gsp=f"{P}/{name}/Resource/{name}.sp.json"; order=[]
    spec=json.load(open(gsp)) if os.path.exists(gsp) else {}
    grouped=set(); gid=1700000000000
    for gname,members in spec.items():
        ids=[byname[m] for m in members if m in byname]
        if not ids: continue
        gid+=1; groups[str(gid)]={"children":ids,"collapsed":True,"name":gname}; grouped.update(ids)
        spec[gname]=gid
    for r in roots:
        if r['node'] in grouped: continue
        order.append(r)
        # place a slot's group right after its Drive toggle
        nm=[c['name'] for c in cached if byname[c['name']]==r['node']][0]
        for gname,g in spec.items():
            if isinstance(g,int) and nm.endswith("Lock") and gname.lower().startswith(cached[[c["name"] for c in cached].index(nm)]["label"].replace(" Lock","").lower()):
                order.append({"group":g})
    patch['nodes']=nodes; patch['connections']=conns; patch['nextNodeId']=nid; patch['inputOrder']={"groups":groups,"roots":order}
    m=patch['meta']; m['displayName']=name; m['identifier']=str(uuid.uuid4()); m['category']=cat; m['description']=hdr.get("DESCRIPTION","")
    out=f"{P}/{name}/{name}.wire"
    if os.path.exists(out):   # keep an existing identifier so Arena clips don't orphan
        try: m['identifier']=json.load(open(out))['patch']['meta']['identifier']
        except Exception: pass
    json.dump(t,open(out,"w"),indent=2); print("wrote",out,len(roots),"inputs, id",m['identifier'])
if __name__=="__main__": build(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "source")
