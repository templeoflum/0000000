// diagnose: dump F stats + threshold region for several k
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
let captured = null;
function mkEl(id){return {id,width:0,height:0,style:{},getContext(){return{
  createImageData(w,h){return {width:w,height:h,data:new Uint8ClampedArray(w*h*4)};},
  putImageData(im){captured=im;}};},
  setAttribute(k,v){this[k]=v;},getAttribute(k){return this[k];},
  addEventListener(){},getBoundingClientRect(){return {left:0,width:420};}};}
const els={scene:mkEl("scene"),rail:mkEl("rail"),knob:mkEl("knob"),knobcore:mkEl("knobcore")};
global.document={getElementById:id=>els[id],addEventListener(){}};
global.window={addEventListener(){},devicePixelRatio:1};
global.location={search:""}; global.parent=global.window;
global.setInterval=()=>{}; global.setTimeout=()=>{};
global.URLSearchParams=class{constructor(){} get(){return null;}};
eval(script);

// reach into internals? not possible; re-derive by instrumenting: instead,
// monkey-patch via a second eval that exposes F through a global hook.
const instrumented = script.replace("ctx.putImageData(img,0,0);\n}",
  "ctx.putImageData(img,0,0);globalThis.__F=F;globalThis.__thr=thr;globalThis.__FM=FM;}");
eval(instrumented);
for (const kk of [0, 0.5, 1]) {
  window.atom.set(kk);
  const F = globalThis.__F;
  let mn = 1e9, mx = -1e9;
  for (let i = 0; i < F.length; i++) { if (F[i] < mn) mn = F[i]; if (F[i] > mx) mx = F[i]; }
  // count below exact quantile: sort sample
  const s = Float32Array.from(F).sort();
  const q = s[Math.floor(F.length * 0.45)];
  let below = 0; for (let i = 0; i < F.length; i++) if (F[i] < q) below++;
  console.log("k=" + kk, "Fmin=" + mn.toFixed(5), "Fmax=" + mx.toFixed(5),
    "q45=" + q.toFixed(5), "below=" + (below / F.length).toFixed(4),
    "thrUsed=" + globalThis.__thr.toFixed(5));
}
