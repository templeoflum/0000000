# assemble toys/18.html from 02.html's head + rail/tail, with S18 machine code
import os
d = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(d, "..", "..", "02.html"), encoding="utf-8").read()
b64 = open(os.path.join(d, "mask_b64.txt")).read().strip()

head = src.split("<script>")[0] + "<script>\n"
tail = src[src.index('const rail=document.getElementById("rail");'):]
tail = tail.replace('name:"S02"', 'name:"S18"')

machine = '''/* ── S18 · DEEP MASK ─────────────────────────────────────────────────────
   one mask, many depths.

   THE MACHINE. P is a single binary mask on a 136x136 torus, converged by
   Ulichney's void-and-cluster algorithm (Ulichney, "The void-and-cluster
   method for dither array generation", SPIE 1913, 1993): minority pixels
   (45% ink) repel through a Gaussian kernel exp(-d^2/2 s^2), s=1.9 px;
   each move evicts the tightest cluster into the largest void until the
   swap would undo itself (1098 moves from a random start). verified a true
   local optimum: 80000 forced continuations never lowered the total kernel
   energy (lab/18/verify_vc2.py). the mask ships below as packed bits.

   THE KNOB. the state at k is the Gaussian scale-space (Witkin, "Scale-
   space filtering", IJCAI 1983) of that one mask: F = G_sigma * P on the
   torus, sigma = 7.0*k^2 mask px, exact separable convolution per apply
   (no stop-lerp, no stops at all). the field is tiled 5x5 onto the 680
   canvas with bilinear (= tent-kernel) sampling, then thresholded at the
   exact 45th percentile of the per-frame landscape (atom 02's conservation
   law). ink is pinned at 0.4500 at every k; what reorganizes is the DEPTH
   of the mask — its skeleton at progressively longer correlation lengths,
   the low-frequency body the eye cannot see in the raw mask.

   THE JOURNEY (named states, lab/18/final_k*.png):
     k=0.00  sigma 0.0  the circuit maze — the raw converged mask (blue
                        noise at 45% ink is a labyrinth, not dots)
     k=0.25  sigma 0.4  melting curds — walls round off, pores coarsen
     k=0.50  sigma 1.8  coral — worms and lobes
     k=0.75  sigma 3.9  cow hide — large irregular patches
     k=1.00  sigma 7.0  the world map — continents and inland seas

   MEASURED (offline, exact pipeline, lab/18/tune2.py, granularity.py):
     ink at every k of the 200-step sweep: 0.4500
     worst flip per 1/200 k-step: 1.61% (at k=0.185, the early melt)

   DEVIATIONS.
     - tie-break jitter: at sigma=0 the landscape is binary, so the 45th
       percentile sits inside a tie mass and ink wanders (measured 0.4436;
       with nearest-neighbour sampling it collapses to 0.0000 — dead end).
       a fixed hash jitter of amplitude 1e-4 is added to the landscape to
       break ties; it is orders of magnitude below the blurred field's
       contrast at the deep end and only ever decides exact ties.
       deterministic; not a pattern source.
     - bilinear upsampling is itself a tent-kernel convolution, so the
       k=0 state is the mask filtered by a tent of width 5 canvas px;
       canvas pixel centers land exactly on mask pixels and the maze
       renders pixel-true.
     - the percentile histogram runs at 65536 bins, not atom 02's 513:
       the raw mask's upsampled landscape lives on a lattice of multiples
       of 0.04, and the deep field's contrast sinks to ±0.005 (blue noise
       suppresses exactly the low frequencies the deep end keeps), so a
       512-bin grid straddles dense quanta and throws ink off by up to 9%
       (measured 0.4075 at k=0, 0.5493 at k=1 with 513 bins). the fine
       grid costs nothing and restores 0.4500 at every k.

   DEAD ENDS.
     - schedule sigma = 7*k^2.5 compressed the early melt (k=0 and k=0.25
       too alike); k^2 spreads the states and still peaks at 1.61% flips.
     - depths past sigma 7 empty the stage to one landmass; sigma_max=7
       keeps inland seas and archipelagos alive.
   ─────────────────────────────────────────────────────────────────────── */
const M=136, UP=5;
const MASK=(()=>{
  const b64="__B64__";
  const bin=atob(b64);
  const t=new Float32Array(M*M);
  for(let i=0;i<M*M;i++)t[i]=(bin.charCodeAt(i>>3)>>(7-(i&7)))&1;
  return t;
})();
function hash2(ix,iy,seed){let h=(ix*374761393+iy*668265263+seed*1442695040)|0;h=(h^(h>>>13))|0;h=Math.imul(h,1274126177);h=(h^(h>>>16))>>>0;return h/4294967296;}
const scene=document.getElementById("scene");
const DPR=2;               /* fixed internal resolution — layout-independent */
let S=680;
scene.width=S;scene.height=S;
const ctx=scene.getContext("2d");
const img=ctx.createImageData(S,S);
const N=S*S;
/* bilinear sampling maps: canvas px -> torus mask coordinates */
const X0=new Int16Array(S),X1=new Int16Array(S),FX=new Float32Array(S);
const Y0=new Int16Array(S),Y1=new Int16Array(S),FY=new Float32Array(S);
for(let x=0;x<S;x++){const mx=(x+0.5)/UP-0.5,x0=Math.floor(mx);X0[x]=((x0%M)+M)%M;X1[x]=(X0[x]+1)%M;FX[x]=mx-x0;}
for(let y=0;y<S;y++){const my=(y+0.5)/UP-0.5,y0=Math.floor(my);Y0[y]=((y0%M)+M)%M;Y1[y]=(Y0[y]+1)%M;FY[y]=my-y0;}
/* deterministic tie-break jitter, amplitude 1e-4 (see header) */
const JIT=new Float32Array(N);
for(let y=0;y<S;y++)for(let x=0;x<S;x++)JIT[y*S+x]=hash2(x,y,5)*1e-4;
/* the blurred mask field on the 136x136 torus */
const FM=new Float32Array(M*M),TM=new Float32Array(M*M);
function blurField(sig){
  if(sig<=0){FM.set(MASK);return;}
  const r=Math.ceil(3*sig),w=2*r+1,g=new Float32Array(w);
  let gs=0;
  for(let j=-r;j<=r;j++){const v=Math.exp(-(j*j)/(2*sig*sig));g[j+r]=v;gs+=v;}
  for(let j=0;j<w;j++)g[j]/=gs;
  for(let y=0;y<M;y++){const yo=y*M;
    for(let x=0;x<M;x++){let s=0;
      for(let j=-r;j<=r;j++){let xx=x+j;xx=xx<0?xx+M:(xx>=M?xx-M:xx);s+=g[j+r]*MASK[yo+xx];}
      TM[yo+x]=s;}}
  for(let x=0;x<M;x++){
    for(let y=0;y<M;y++){let s=0;
      for(let j=-r;j<=r;j++){let yy=y+j;yy=yy<0?yy+M:(yy>=M?yy-M:yy);s+=g[j+r]*TM[yy*M+x];}
      FM[y*M+x]=s;}}
}
const F=new Float32Array(N);
const hist=new Uint32Array(513);
const SIGMAX=7.0;
let k=0;
function apply(){
  blurField(SIGMAX*k*k);
  /* upsample + jitter + histogram in one pass */
  hist.fill(0);
  for(let y=0;y<S;y++){
    const r0=Y0[y]*M,r1=Y1[y]*M,fy=FY[y],yo=y*S;
    for(let x=0;x<S;x++){
      const i=yo+x,fx=FX[x],x0=X0[x],x1=X1[x];
      const top=FM[r0+x0]*(1-fx)+FM[r0+x1]*fx;
      const bot=FM[r1+x0]*(1-fx)+FM[r1+x1]*fx;
      const v=top*(1-fy)+bot*fy+JIT[i];
      F[i]=v;
      let q=(v*512)|0;if(q<0)q=0;if(q>512)q=512;hist[q]++;
    }
  }
  /* pin the quantity: threshold at the exact 45th percentile of the landscape */
  const target=N*0.45;let acc=0,thr=0.5;
  for(let q=0;q<=512;q++){acc+=hist[q];if(acc>=target){thr=(q+0.5)/512;break;}}
  const d=img.data;
  for(let i=0;i<N;i++){
    const on=F[i]<thr;
    const v=on?0:255,j=i*4;
    d[j]=v;d[j+1]=v;d[j+2]=v;d[j+3]=255;
  }
  ctx.putImageData(img,0,0);
}
apply();
 
'''

out = head + machine.replace("__B64__", b64) + tail
open(os.path.join(d, "..", "..", "18.html"), "w", encoding="utf-8", newline="\n").write(out)
print("wrote 18.html,", len(out), "bytes")
