# build_final_toy.py — bitpack the 13 finished 680^2 stops into toys/12v2.html.
import base64, os
from PIL import Image

LAB = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(LAB, "..", "..", "12v2.html")

S, NF = 680, 13
payloads = []
for f in range(NF):
    im = Image.open(os.path.join(LAB, f"h{f:02d}.png")).convert("L")
    assert im.size == (S, S), f"h{f:02d} wrong size {im.size}"
    px = im.load()
    bits = bytearray(); cur = n = 0
    for y in range(S):
        for x in range(S):
            cur = (cur << 1) | (1 if px[x, y] < 128 else 0)
            n += 1
            if n == 8:
                bits.append(cur); cur = n = 0
    if n:
        bits.append(cur << (8 - n))
    payloads.append(base64.b64encode(bytes(bits)).decode("ascii"))

HEADER = """/* ── THE TOY: the print, grown.
   anisotropic Swift-Hohenberg stripe formation riding a Sherlock-Monro
   zero-pole director field:
     dp/dt = eps*p - B(B(p)) - p^3,   B(p) = div(A grad p) + q0^2 p,
     A = R diag(1, alpha) R^T   (ridges grow ALONG the director),
     d = H/|H|,  H = prod(z - cores) / prod(z - deltas),
   cores are +1/2 winding zeros, deltas -1/2 winding poles — the two
   singularity species every fingerprint is classified by. the field p is
   not drawn, it is ANNEALED: stripes nucleate, buckle, and heal around the
   charges, and the minutiae — ridge endings, bifurcations — appear by
   themselves as dislocations in the stripe crystal. nothing is placed.

   the knob slides the CHARGES along the classification homotopy:
   arch -> tented -> loop -> whorl. at the four named states (stops 0, 4,
   8, 12) the field was annealed 15k steps from its own seed (arch family
   from 0.25cos+0.08 noise — stripe-leaning seeds relax clean; loop from
   pure noise); between them, warm bridges carry one material causally —
   8k steps per stop, charges gliding, no dissolves anywhere.

   the whorl is honest about its origins: a single +1/2 core can only make
   a recurve — a target whorl needs winding +1, so a second core rides in
   EXACTLY on the loop's exiting delta (zero over pole cancels — it is not
   there until it is), and the whorl state itself was GROWN from the crisp
   loop, the way volar pads actually develop one. it is the one stop whose
   seed is the journey.

   notes, not laws: the machine has a minimum honest dwell per state — rush
   the anneal and it shows you its history. noise is a seed here, never the
   substrate. ink is the global 45th percentile of the whole square field
   (02's law); the pattern does not know about fingers, so there is no pad,
   no oval, no imprint — the square fills edge to edge, periodic on all
   four sides. pitch lambda = 14px, matched to the reference print.
   eps=0.3 alpha=0.25 dt=0.02 seed=7, 680^2, 13 stops. */
"""

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
__HEADER__
const S=__S__, NF=__NF__;
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
  window.atom={name:"S12v2",
    set:function(t){set(n2c(t));},
    get:function(){const x=parseFloat(document.getElementById("knob").getAttribute("cx"));return (x-30)/360;}};
  const q=new URLSearchParams(location.search).get("k");
  if(q!==null) setTimeout(function(){window.atom.set(parseFloat(q));},80);
})();
</script>
</body>
</html>
"""

html = (html
        .replace("__HEADER__", HEADER.strip())
        .replace("__S__", str(S))
        .replace("__NF__", str(NF))
        .replace("__PAYLOADS__", ",".join('"%s"' % p for p in payloads)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", os.path.abspath(OUT), os.path.getsize(OUT), "bytes")
