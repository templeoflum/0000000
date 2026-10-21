# build_rough.py — rough-cut S12v2 slider toy from the EXISTING 340^2 frames.
# No new compute: bitpack g00..g11, emit toys/12v2_rough.html.
# Preview only: final build will re-render at 680^2 with LAM=14.
import base64, io, os
from PIL import Image

LAB = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(LAB, "..", ".."))
OUT = os.path.join(DECK, "12v2_rough.html")

frames = []
for i in range(12):
    p = os.path.join(LAB, f"g{i:02d}.png")
    im = Image.open(p).convert("L")
    frames.append(im)
S = frames[0].size[0]
assert all(f.size == (S, S) for f in frames), "frame size mismatch"

payloads, inks = [], []
for im in frames:
    px = im.load()
    bits = bytearray()
    cur, n = 0, 0
    dark = 0
    for y in range(S):
        for x in range(S):
            b = 1 if px[x, y] < 128 else 0   # dark ridge = 1
            dark += b
            cur = (cur << 1) | b
            n += 1
            if n == 8:
                bits.append(cur); cur, n = 0, 0
    if n:
        bits.append(cur << (8 - n))
    payloads.append(base64.b64encode(bytes(bits)).decode("ascii"))
    inks.append(dark / (S * S))

for i, f in enumerate(inks):
    print(f"g{i:02d} ink={f:.3f}")

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>◐</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden;overscroll-behavior:none;background:#0e0d12}
#app{height:100vh;height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}
#scene{width:min(80vw,340px);aspect-ratio:1;background:#fff;border-radius:3px}
#rail{width:min(86vw,420px);height:auto;touch-action:none;cursor:pointer}
</style>
</head>
<body>
<div id="app">
  <canvas id="scene"></canvas>
  <svg id="rail" viewBox="0 0 420 56" aria-label="the knob">
    <line x1="30" y1="28" x2="390" y2="28" stroke="#26242f" stroke-width="2" stroke-linecap="round"/>
    <circle id="knob" cx="30" cy="28" r="13" fill="#0e0d12" stroke="#93a4c2" stroke-width="2"/>
    <circle id="knobcore" cx="30" cy="28" r="4" fill="#93a4c2"/>
  </svg>
</div>
<script>
/* ── ROUGH CUT — S12·v2, preview only.
   anisotropic Swift–Hohenberg stripes buckling on a Sherlock–Monro
   zero-pole director field (cores = +1/2 zeros, deltas = -1/2 poles).
   the knob moves the CHARGES: arch -> tented -> loop -> whorl, and the
   stripe field re-anneals around them; minutiae are dislocations.
   these are the 340^2 prototype frames (10k-step warm-start anneals,
   12 stops, nearest-frame, no dissolve). final build re-renders at
   680^2 at the reference pitch. mechanics are the substrate; noise was
   only the seed. */
const S=__S__, NF=12;
const F=[__PAYLOADS__];
function bits(b64){
  const bin=atob(b64), n=bin.length, out=new Uint8Array(n*8);
  for(let i=0;i<n;i++){const c=bin.charCodeAt(i);for(let j=0;j<8;j++)out[i*8+j]=(c>>(7-j))&1;}
  return out;
}
const FR=F.map(bits);
const cv=document.getElementById("scene");
cv.width=S; cv.height=S;
const ctx=cv.getContext("2d");
const img=ctx.createImageData(S,S);
let k=0, last=-1;
function apply(){
  const fi=Math.min(NF-1,Math.round(k*(NF-1)));
  if(fi===last)return; last=fi;
  const b=FR[fi], d=img.data;
  for(let i=0;i<S*S;i++){
    const v=b[i]?0:255, o=i*4;
    d[o]=v; d[o+1]=v; d[o+2]=v; d[o+3]=255;
  }
  ctx.putImageData(img,0,0);
}
apply();

const rail=document.getElementById("rail");
const knob=document.getElementById("knob");
const knobcore=document.getElementById("knobcore");
let dragging=false;
function set(clientX){
  const r=rail.getBoundingClientRect();
  k=Math.min(1,Math.max(0,(clientX-r.left-r.width*30/420)/(r.width*360/420)));
  apply();
  const x=30+360*k;
  knob.setAttribute("cx",x); knobcore.setAttribute("cx",x);
}
function start(e){dragging=true;move(e);}
function move(e){
  if(!dragging)return;
  set(e.touches?e.touches[0].clientX:e.clientX);
  if(e.cancelable)e.preventDefault();
}
rail.addEventListener("mousedown",start);
rail.addEventListener("touchstart",start,{passive:false});
window.addEventListener("mousemove",move);
window.addEventListener("touchmove",move,{passive:false});
window.addEventListener("mouseup",()=>dragging=false);
window.addEventListener("touchend",()=>dragging=false);
document.addEventListener("touchmove",e=>{if(dragging)e.preventDefault();},{passive:false});

(function(){
  const rail=document.getElementById("rail");
  function n2c(t){const r=rail.getBoundingClientRect();return r.left+r.width*(30+360*Math.min(1,Math.max(0,t)))/420;}
  window.atom={name:"S12v2-rough",
    set:function(t){set(n2c(t));},
    get:function(){const x=parseFloat(document.getElementById("knob").getAttribute("cx"));return (x-30)/360;}};
  const q=new URLSearchParams(location.search).get("k");
  if(q!==null) setTimeout(function(){window.atom.set(parseFloat(q));},80);
})();
</script>
</body>
</html>
""".replace("__S__", str(S)).replace("__PAYLOADS__", ",".join('"%s"' % p for p in payloads))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
