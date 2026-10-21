# Assemble toys/m8.html from S13's plumbing + 02.html's rail/tail + M8 frames.
import json, re, os

LAB = os.path.dirname(os.path.abspath(__file__))
TOYS = os.path.dirname(os.path.dirname(LAB))

s13 = open(os.path.join(TOYS, "13.html"), encoding="utf-8").read()
s02 = open(os.path.join(TOYS, "02.html"), encoding="utf-8").read()
frames = json.load(open(os.path.join(LAB, "frames.json")))

# the NEW blue-noise mask literal, lifted from S13 (identical in 12/13/m7)
bn = re.search(r'const BN=\(\(\)=>\{const b64="([^"]+)"', s13).group(1)

# 02.html's rail boilerplate + tail, verbatim from the cut point onward
cut = 'const rail=document.getElementById("rail");'
tail = s02[s02.index(cut):]
tail = tail.replace('name:"S02"', 'name:"M8"')
tail = tail.rstrip()
if tail.endswith("</html>"):
    tail = tail[: tail.rindex("</html>")].rstrip()

header = '''/* \u2500\u2500 M8: bond of studies 12 and 13 \u2014 the reaction in the river.
   the Gray\u2013Scott pair (S13's certified machine: Du=0.21, Dv=0.105,
   F=0.0545, k=0.062 \u2014 Pearson's 1993 spot regime, nine-point Laplacian,
   dt=1, explicit Euler, periodic edges, 224\u00b2 lattice, 8% static seed)
   now runs in a moving medium: S12's potential flow past a cylinder with
   circulation (U=1, R=110 device px \u2248 36.2 cells, \u0393\u0303=0.6, stream vertical).
   the BOND: the activator alone is advected \u2014
     \u2202v = Dv\u2207\u00b2v + u\u00b7v\u00b2 \u2212 (F+k)\u00b7v \u2212 c\u00b7(w\u00b7\u2207v)      w = S12's velocity field
   while the substrate stays gel-immobilized (\u2202u has no advection term:
   the CIMA gel-reactor arrangement \u2014 one species bound to the matrix,
   one species free to flow). advection is first-order upwind; the
   cylinder is solid (no reaction inside r<R). the knob is the coupling c
   \u2208 [0, 0.45]: at c=0 the certified coat; as c grows the spots connect
   downstream into worms bowing around the core, the worms lock into
   reaction-wave ridges combed along the streamlines, and the ridges wind
   into a typhoon around the eye \u2014 the deltas of the fingerprint showing
   as fine-grain stagnation patches where the flow stalls. neither parent
   shows these states: S12's streamlines are smooth constructions, these
   ridges are born of the reaction; S13's coat is isotropic, this one is
   combed by the river.
   ink law: S13's, inherited \u2014 each frame is cut at the 74th percentile
   of the activator field, cover 0.26, the rosette cover-fraction. it
   holds exactly at every stop (measured 0.2600 \u00b1 0.0000).
   granularity: c is quantized to thirteen stops (the integration cannot
   run inside an instant switch \u2014 S13's precedent), with 08's blue-noise
   dissolve between them; worst flip 2.36% per 1/200 k-step (measured).
   deviations, honestly: (1) |w| is capped at 2.2 cells/step \u2014 the flow
   peaks at 3.17 on the core's skin, and the cap keeps the upwind CFL
   \u2264 1 at the strongest coupling; only the thin fast layer near the
   surface is touched. (2) frames are precomputed offline (seed 42,
   t=520 for c=0 \u2014 S13's mature coat exactly \u2014 t=700 otherwise) and
   bitpacked; the equations were integrated, the deck ships the result.
   (3) grain is 224\u2192680, \u2248 3 device px per cell. dead end, documented:
   advecting BOTH species washes the pattern downstream and leaves the
   upstream half barren \u2014 the substrate must stay put for the coat to
   survive the river. static states; the knob alone moves anything. \u2500\u2500 */'''

fr_js = "const FRAMES=[\n" + ",\n".join('"%s"' % f for f in frames["frames"]) + "\n];"

machine = f'''{header}
const BN_N=128;
const BN=(()=>{{const b64="{bn}";
  const bin=atob(b64),n=BN_N*BN_N,t=new Float32Array(n);
  for(let i=0;i<n;i++){{const v=bin.charCodeAt(2*i)|(bin.charCodeAt(2*i+1)<<8);t[i]=(v+0.5)/n;}}return t;}})();
/* the coupling ladder, c = {", ".join(str(c) for c in frames["stops"])} \u2014 1-bit at 224\u00b2, MSB-first */
{fr_js}
function unpack(s){{
  const bin=atob(s),n=224*224,out=new Uint8Array(n);
  for(let i=0;i<n;i++) out[i]=(bin.charCodeAt(i>>3)>>(7-(i&7)))&1;
  return out;
}}
const FR=FRAMES.map(unpack);
const NS=FR.length;

const scene=document.getElementById("scene");
const DPR=2;               /* fixed internal resolution \u2014 layout-independent */
let S=680;
scene.width=S;scene.height=S;
const ctx=scene.getContext("2d");
ctx.imageSmoothingEnabled=false;
const G2=224;
const cv=document.createElement("canvas"); cv.width=G2;cv.height=G2;
const cx2=cv.getContext("2d");
const img=cx2.createImageData(G2,G2);
let k=0;

function apply(){{
  const p=k*(NS-1);
  let D=Math.floor(p); if(D>NS-2)D=NS-2;
  let f=p-D; if(f<0)f=0;
  const A=FR[D], B=FR[D+1], d=img.data;
  for(let y=0;y<G2;y++){{
    const br=(y&(BN_N-1))*BN_N, o=y*G2;
    for(let x=0;x<G2;x++){{
      const i=o+x, a=A[i];
      const on=a===B[i]?a:(BN[br+(x&(BN_N-1))]<f?B[i]:a);   /* 08's dissolve */
      const v=on?0:255, j=i*4;
      d[j]=v;d[j+1]=v;d[j+2]=v;d[j+3]=255;
    }}
  }}
  cx2.putImageData(img,0,0);
  ctx.drawImage(cv,0,0,G2,G2,0,0,S,S);   /* \u2248 3px grains \u2014 the deck's weave */
}}
apply();

'''

head = s13[: s13.index("<script>") + len("<script>")]

html = head + "\n" + machine + tail + "\n</html>\n"
open(os.path.join(TOYS, "m8.html"), "w", encoding="utf-8", newline="\n").write(html)
print("m8.html written, KB:", len(html) // 1024)
