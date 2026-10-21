#!/usr/bin/env python3
"""Build the unified deck: one stage, one slider, every toy a module.
Canonical toys live as standalone files; this wraps each toy's machine
(everything before its rail boilerplate) in a closure module and mounts
them all on one persistent canvas + one persistent rail."""
import re, shutil, os

HERE = os.path.dirname(os.path.abspath(__file__))
TOYS = HERE + "/"
OUT  = os.path.join(HERE, "deck_slim.html")
APP  = os.path.join(HERE, "..", "app", "index.html")   # preview copy; skipped if no app/ dir

MANIFEST_ATOMS = ["01","02","03","04","05","06","07","08","09","10","11","12","13",
                  "16","20","21","22","23"]
MANIFEST_MOLS  = [("m1","M1"),("m2","M2"),("m3v4b","M3"),
                  ("M4", [("m4v4","v4"),("m4v5","v5")]),
                  ("M5", [("m5v7","v7"),("m5v6","v6")]),
                  ("m6","M6"),("m7","M7"),("m8","M8"),("m9","M9")]

old = open(OUT, encoding="utf-8").read()
MASK_OLD = re.search(r'MASK_OLD="([^"]+)"', old).group(1)
MASK_NEW = re.search(r'MASK_NEW="([^"]+)"', old).group(1)

def module(fname, name):
    s = open(TOYS + fname + ".html", encoding="utf-8").read()
    body = s[s.find("<script>")+8 : s.find("</script>")]
    cut = body.find('const rail=document.getElementById("rail");')
    assert cut > 0, fname
    m = body[:cut]
    m = m.replace('document.getElementById("scene")', 'document.createElement("canvas")')
    m = m.replace('"'+MASK_OLD+'"', 'MASK_OLD').replace('"'+MASK_NEW+'"', 'MASK_NEW')
    assert 'function apply(' in m and re.search(r'let k=0', m), fname
    return ('REG.push((function(){\n' + m +
            '\n;return {name:"'+name+'",canvas:scene,'
            'set:function(v){k=Math.min(1,Math.max(0,v));apply();}};\n})());\n')

mods = []
for f in MANIFEST_ATOMS:
    mods.append((f, "S"+f, module(f, "S"+f)))
molmods = []
for entry in MANIFEST_MOLS:
    if isinstance(entry[1], str):
        f, label = entry
        molmods.append((f, label, module(f, label)))
    else:
        label, vers = entry
        for f, v in vers:
            molmods.append((f, label+" · "+v, module(f, label+" · "+v)))

CSS = """
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden;overscroll-behavior:none;background:#0e0d12}
#bar{position:fixed;top:0;left:0;right:0;z-index:2;display:flex;flex-direction:column;align-items:center;gap:9px;padding-top:16px}
.row{display:flex;gap:13px;height:14px;align-items:center}
.dot{width:13px;height:13px;border-radius:50%;background:#26242f;cursor:pointer;transition:background .15s}
.dot:hover{background:#4a4658}
.row.mol .dot{border-radius:3px}
.dot.on{background:#93a4c2}
#versrow{gap:7px;height:9px}
#versrow .dot{width:8px;height:8px;border-radius:2px;background:#3a3745}
#versrow .dot.on{background:#c2a493}
#stage{height:100vh;height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}
#view{width:min(80vw,340px);aspect-ratio:1;background:#fff;border-radius:3px}
#rail{width:min(86vw,420px);height:auto;touch-action:none;cursor:pointer}
#tag{position:fixed;right:16px;bottom:12px;color:#565064;font:11px/1 ui-monospace,Menlo,monospace;letter-spacing:2px}
"""

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>the deck</title>
<style>""" + CSS + """</style>
</head>
<body>
<div id="bar"></div>
<div id="stage">
  <canvas id="view"></canvas>
  <svg id="rail" viewBox="0 0 420 56" aria-label="the knob">
    <line x1="30" y1="28" x2="390" y2="28" stroke="#26242f" stroke-width="2" stroke-linecap="round"/>
    <circle id="knob" cx="30" cy="28" r="13" fill="#0e0d12" stroke="#93a4c2" stroke-width="2"/>
    <circle id="knobcore" cx="30" cy="28" r="4" fill="#93a4c2"/>
  </svg>
</div>
<div id="tag"></div>
<script>
/* one stage, one slider: the dots only choose which machine is rendering.
   k is deck-global; switching view never reloads, never resets, never blanks. */
const MASK_OLD=\"""" + MASK_OLD + "\",MASK_NEW=\"" + MASK_NEW + "\";\n"
html += "const REG=[];\n"
for f, label, code in mods + molmods:
    html += "/* ── " + label + " (" + f + ") ── */\n" + code

html += """
const view=document.getElementById("view");
view.width=680;view.height=680;
const vctx=view.getContext("2d");
vctx.imageSmoothingEnabled=false;
let k=0, cur=null;
function blit(){
  vctx.fillStyle="#fff";vctx.fillRect(0,0,680,680);
  const c=cur.canvas;
  if(c.width===680){ vctx.drawImage(c,0,0); }
  else { vctx.drawImage(c,0,0,c.width,c.height,0,0,680,680); }
}
const tag=document.getElementById("tag");
const rail=document.getElementById("rail");
const knob=document.getElementById("knob");
const knobcore=document.getElementById("knobcore");
function activate(m,label){
  cur=m; m.set(k); blit();
  tag.textContent=label;
}
function setK(clientX){
  const r=rail.getBoundingClientRect();
  k=Math.min(1,Math.max(0,(clientX-r.left-r.width*30/420)/(r.width*360/420)));
  cur.set(k); blit();
  const x=30+360*k;
  knob.setAttribute("cx",x); knobcore.setAttribute("cx",x);
}
let dragging=false;
function start(e){dragging=true;move(e);}
function move(e){
  if(!dragging)return;
  setK(e.touches?e.touches[0].clientX:e.clientX);
  if(e.cancelable)e.preventDefault();
}
rail.addEventListener("mousedown",start);
rail.addEventListener("touchstart",start,{passive:false});
window.addEventListener("mousemove",move);
window.addEventListener("touchmove",move,{passive:false});
window.addEventListener("mouseup",()=>dragging=false);
window.addEventListener("touchend",()=>dragging=false);
document.addEventListener("touchmove",e=>{if(dragging)e.preventDefault();},{passive:false});

const bar=document.getElementById("bar");
function mkdot(fn){
  const d=document.createElement("div");
  d.className="dot";
  d.addEventListener("click",fn);
  return d;
}
const r1=document.createElement("div");r1.className="row";bar.appendChild(r1);
const r2=document.createElement("div");r2.className="row mol";bar.appendChild(r2);
const rv=document.createElement("div");rv.id="versrow";rv.className="row";bar.appendChild(rv);
let litAtom=null, litMol=null, litVers=[];
function light(row,i){ if(row===1){litAtom=i;} else {litMol=i;}
  [...r1.children].forEach((d,j)=>d.classList.toggle("on",j===litAtom));
  [...r2.children].forEach((d,j)=>d.classList.toggle("on",j===litMol));
}
"""

# atom dots
html += "const ATOMS=[\n"
for f, label, code in mods:
    html += "{label:\"" + label + "\",m:REG[" + str(len([1 for x in (mods+molmods) if x[1]==label and x[0]==f]) - 1) + "},\n"
html = html.rstrip(",\n") + "\n];\n"

REGIDX = {}
for i, (f, label, code) in enumerate(mods + molmods):
    REGIDX[(f, label)] = i

# rebuild ATOMS cleanly with correct indices
html = html[:html.find("const ATOMS=[")]
html += "const ATOMS=[" + ",".join(
    "{label:\""+label+"\",m:REG["+str(REGIDX[(f,label)])+"]}" for f,label,_ in mods) + "];\n"

html += "const MOLS=[" 
first = True
for entry in MANIFEST_MOLS:
    if isinstance(entry[1], str):
        f, label = entry
        idx = REGIDX[(f, label)]
        html += ("{label:\""+label+"\",vers:[{m:REG["+str(idx)+"],vt:\""+label+"\"}]}")
    else:
        label, vers = entry
        parts = []
        for f, v in vers:
            idx = REGIDX[(f, label+" · "+v)]
            parts.append("{m:REG["+str(idx)+"],vt:\""+v+"\"}")
        html += "{label:\""+label+"\",vers:["+",".join(parts)+"]}"
    html += ","
html = html.rstrip(",") + "];\n"

html += """
let curMol=-1, curVers=-1;
ATOMS.forEach((a,i)=>{
  const d=mkdot(()=>{ curMol=-1; light(1,i); rv.innerHTML=""; activate(a.m,a.label); });
  r1.appendChild(d);
});
MOLS.forEach((mo,i)=>{
  const d=mkdot(()=>{
    light(2,i);
    if(i!==curMol){ curMol=i; curVers=0; }
    rv.innerHTML=""; litVers=[];
    if(mo.vers.length>1){
      mo.vers.forEach((v,j)=>{
        const vd=mkdot(()=>{ curVers=j; activate(v.m, mo.label+" · "+v.vt);
          [...rv.children].forEach((x,q)=>x.classList.toggle("on",q===j)); });
        if(j===curVers) vd.classList.add("on");
        rv.appendChild(vd);
      });
    }
    const v=mo.vers[curVers];
    activate(v.m, mo.vers.length>1 ? mo.label+" · "+v.vt : mo.label);
  });
  r2.appendChild(d);
});
light(1,0);
activate(ATOMS[0].m, ATOMS[0].label);
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf-8").write(html)
if os.path.isdir(os.path.dirname(APP)):
    shutil.copy(OUT, APP)
print("unified deck built:", len(html)//1024, "KB,", html.count("REG.push"), "modules")
