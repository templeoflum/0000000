# builds toys/21.html from 02.html: same head/CSS, same BN mask block,
# same rail boilerplate + tail (name swapped to S21), new machine section.
import re

SRC = r"C:\Users\User\Documents\0000000\dither-deck\toys\02.html"
DST = r"C:\Users\User\Documents\0000000\dither-deck\toys\21.html"

html = open(SRC, encoding="utf8").read()

# head: everything up to and including "<script>\n"
head_end = html.index("<script>") + len("<script>")
head = html[:head_end]

# BN mask block: from "const BN_N=128;" through the line ending "return t;})();"
bn_start = html.index("const BN_N=128;")
bn_end = html.index("return t;})();") + len("return t;})();")
bn_block = html[bn_start:bn_end]

# rail boilerplate + tail: from the FIRST "const rail=document.getElementById" to EOF
rail_start = html.index('const rail=document.getElementById("rail");')
tail = html[rail_start:]
assert 'window.atom={name:"S02"' in tail
tail = tail.replace('window.atom={name:"S02"', 'window.atom={name:"S21"')

machine = '''
/* ── THE TOY: the tank.
   two needles, one water surface — the ripple-tank photograph of every
   physics text, computed, not drawn. two coherent point sources, in phase,
   equal strength, radiating circular waves on a 2-D surface:
     ψ(x,y) = a(r₁)·cos(2π r₁/λ) + a(r₂)·cos(2π r₂/λ),
     a(r) = √(λ/(r+r₀))   — cylindrical spreading: energy flux through a
     circle of radius r is constant, so amplitude falls as exactly 1/√r
     (r₀ = λ softens the source singularity; the needle has finite size).
   the superposition principle does the rest: nodal hyperbolas where the
   path difference r₁−r₂ is a half-integer number of wavelengths, antinodal
   fans where it is whole. nothing is drawn; the fringes are the equation.
   the knob is the source separation d, measured in wavelengths — the lab
   dial. at d=0 the needles coincide and the tank is one bullseye; as d
   grows the centre pinches into an eye, the eye splits into two eyes, the
   nodal fan opens between them, and by d=10λ the middle of the tank is a
   standing lattice flanked by two ring systems. (an unasked-for gift:
   from d≈3λ on, the field is unmistakably a face — two eyes and a spine
   of dashes. pareidolia out of two cosines; we did not put it there.)
   what is shown is the signed instantaneous amplitude — a strobe frame,
   crests and troughs frozen — thresholded at its own exact 45th
   percentile (02's law): ink = the deep troughs, 0.45 at every state,
   pinned while the pattern reorganizes.
   d is quantized to eight stops — 0, 0.6, 1.2, 2, 3, 4.5, 6.5, 10
   wavelengths — because moving a source rephases the whole field (S12's
   reason: a continuous dial pours instead of stepping); between stops the
   field dissolves pixel-by-pixel in blue-noise order (08's law of regime
   change), so mid-travel reads as a textured reaction front. measured:
   ink 0.4500 at every stop; worst flip 2.35% per 1/200 k-step (mean
   1.75%, p95 2.34%) — inside the 2.5% law. λ = 24px, so ~14 rings span
   the half-field; stops are non-half-integer below 2λ because d = (n+½)λ
   puts the entire outer source axis in a node — a wide dead band that
   reads as a bug, though it is honest physics.
   static states; the knob alone moves anything. ── */
'''
machine += bn_block + "\n"
machine += '''const scene=document.getElementById("scene");
const DPR=2;               /* fixed internal resolution — layout-independent */
let S=680;
scene.width=S;scene.height=S;
const ctx=scene.getContext("2d");
const img=ctx.createImageData(S,S);
let k=0;
const N=S*S;
const CC=(S-1)/2;          /* 339.5: the pixel grid mirrors exactly about it */
const LAM=12*DPR;          /* wavelength: 24px — ~14 rings across the half-field */
const R0=12*DPR;           /* source softening = λ (the needle has finite size) */
const TAU=2*Math.PI;
const hist=new Uint32Array(513);

/* one stop: the tank at separation d = dl·λ, thresholded at the exact 45th
   percentile of its own amplitude field (02's conservation law).
   the field is mirror-symmetric about both axes through the sources'
   midpoint, so only a quarter is evaluated; the rest is reflection —
   identical values, no approximation. */
function stopField(dl){
  const d=dl*LAM, x1=CC-d/2, x2=CC+d/2, M=S-1;
  const F=new Float32Array(N);
  for(let y=0;y<=M/2;y++){
    const dy=y-CC, dy2=dy*dy, o=y*S, om=(M-y)*S;
    for(let x=0;x<=M/2;x++){
      const dx1=x-x1, dx2=x-x2;
      const r1=Math.sqrt(dx1*dx1+dy2), r2=Math.sqrt(dx2*dx2+dy2);
      const v=Math.sqrt(LAM/(r1+R0))*Math.cos(TAU*r1/LAM)
             +Math.sqrt(LAM/(r2+R0))*Math.cos(TAU*r2/LAM);
      F[o+x]=v; F[o+M-x]=v; F[om+x]=v; F[om+M-x]=v;
    }
  }
  hist.fill(0);
  for(let i=0;i<N;i++){let q=(F[i]*102+256)|0;if(q<0)q=0;if(q>512)q=512;hist[q]++;}
  const target=N*0.45;let acc=0,thr=0;
  for(let q=0;q<=512;q++){acc+=hist[q];if(acc>=target){thr=(q-256)/102;break;}}
  const B=new Uint8Array(N);
  for(let i=0;i<N;i++) B[i]=F[i]<thr?1:0;
  return B;
}

/* the separation ladder, in wavelengths: bullseye → pinch → eye → two eyes →
   the fan opens → wide fan → the lattice. eight stops; the blue-noise tweens
   between them stay a legible textured morph. */
const DL=[0,0.6,1.2,2,3,4.5,6.5,10];
const STAGE=DL.map(stopField);
const NS=STAGE.length;

function apply(){
  const p=k*(NS-1);
  let D=Math.floor(p); if(D>NS-2)D=NS-2;
  let f=p-D; if(f<0)f=0;
  const A=STAGE[D], B=STAGE[D+1], d=img.data;
  for(let y=0;y<S;y++){
    const br=(y&(BN_N-1))*BN_N, o=y*S;
    for(let x=0;x<S;x++){
      const i=o+x, a=A[i];
      const on=a===B[i]?a:(BN[br+(x&(BN_N-1))]<f?B[i]:a);   /* 08's dissolve */
      const v=on?0:255, j=i*4;
      d[j]=v;d[j+1]=v;d[j+2]=v;d[j+3]=255;
    }
  }
  ctx.putImageData(img,0,0);
}
apply();
 
'''

out = head + "\n" + machine.lstrip("\n") + tail
open(DST, "w", encoding="utf8", newline="\n").write(out)
print("wrote", DST, len(out), "bytes")
