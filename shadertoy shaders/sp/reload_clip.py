#!/usr/bin/env python3
"""reload_clip.py snapshot <layer> <column>   — save every dial + playing state of a clip
   reload_clip.py restore  <layer> <column>   — after the source/effect was re-opened: put the dials back, reconnect
Keeps his settings across a reload (Arena resets a clip's params when its source is re-opened)."""
import json, sys, os, urllib.request
BASE = "http://localhost:8080/api/v1"
STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".reload_snap.json")
def get(u): return json.load(urllib.request.urlopen(BASE + u, timeout=3))
def put(pid, val):
    r = urllib.request.Request(f"{BASE}/parameter/by-id/{pid}", data=json.dumps({"value": val}).encode(), method="PUT", headers={"Content-Type": "application/json"})
    urllib.request.urlopen(r, timeout=3).read()
def post(u):
    r = urllib.request.Request(BASE + u, data=b"", method="POST"); urllib.request.urlopen(r, timeout=5).read()
def params_of(block):
    out = {}
    for k, v in (block or {}).items():
        if isinstance(v, dict) and "valuetype" in v:
            if v["valuetype"] == "ParamChoice": out[k] = v["index"]
            elif "value" in v: out[k] = v["value"]                 # triggers (ParamTrigger) carry no value: skip
    return out
def snapshot(L, C):
    c = get(f"/composition/layers/{L}/clips/{C}"); v = c["video"]
    snap = {"desc": v.get("description"), "connected": "Connected" in str(c["connected"]["value"]),
            "source": params_of(v.get("sourceparams")),
            "effects": [(e["name"], params_of(e.get("params"))) for e in v.get("effects", [])],
            "bypass": {e["name"]: (e.get("bypassed") or {}).get("value") for e in v.get("effects", []) if isinstance(e.get("bypassed"), dict)},
            "opacity": v["opacity"]["value"], "blend": v["mixer"]["Blend Mode"]["index"]}
    db = json.load(open(STORE)) if os.path.exists(STORE) else {}
    db[f"{L}:{C}"] = snap; json.dump(db, open(STORE, "w"))
    print(f"snapshot L{L}C{C} {snap['desc']!r}: {len(snap['source'])} source params, {sum(len(p) for _, p in snap['effects'])} effect params, {'playing' if snap['connected'] else 'idle'}")
def restore(L, C):
    db = json.load(open(STORE)); snap = db[f"{L}:{C}"]
    c = get(f"/composition/layers/{L}/clips/{C}"); v = c["video"]; n = 0; skipped = []
    sp = v.get("sourceparams") or {}
    effs = v.get("effects", [])
    for k, val in snap["source"].items():
        p = sp.get(k)
        if isinstance(p, dict) and "id" in p: put(p["id"], val); n += 1; continue
        hit = False                                   # a source dial may now live on an effect (source → router+effect)
        for e in effs:
            q = (e.get("params") or {}).get(k)
            if isinstance(q, dict) and "id" in q: put(q["id"], val); n += 1; hit = True; break
        if not hit: skipped.append(k)
    for (name, ps) in snap["effects"]:
        for e in effs:
            if e["name"] == name:
                for k, val in ps.items():
                    p = (e.get("params") or {}).get(k)
                    if isinstance(p, dict) and "id" in p: put(p["id"], val); n += 1
                    else: skipped.append(f"{name}/{k}")
                break
    for e in effs:                                                # bypass state, too
        b = snap.get("bypass", {}).get(e["name"])
        if b is not None and isinstance(e.get("bypassed"), dict) and "id" in e["bypassed"]: put(e["bypassed"]["id"], b)
    put(v["opacity"]["id"], snap["opacity"]); put(v["mixer"]["Blend Mode"]["id"], snap["blend"])
    if snap["connected"] and "Connected" not in str(c["connected"]["value"]): post(f"/composition/layers/{L}/clips/{C}/connect")
    print(f"restored L{L}C{C}: {n} params" + (f", gone: {skipped}" if skipped else "") + (", reconnected" if snap["connected"] else ""))
if __name__ == "__main__":
    {"snapshot": snapshot, "restore": restore}[sys.argv[1]](int(sys.argv[2]), int(sys.argv[3]))
