// extract machine code from 23.html, run it headless, verify laws
const fs = require("fs");
const html = fs.readFileSync("C:/Users/User/Documents/0000000/dither-deck/toys/23.html", "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
let code = m[1];
code = code.slice(0, code.indexOf('const rail=document.getElementById("rail");'));

// DOM stubs
const W = new Uint8ClampedArray(680 * 680 * 4);
global.document = {
  getElementById: () => ({
    width: 0, height: 0,
    getContext: () => ({
      createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
      putImageData: () => {},
    }),
  }),
};
code += ";globalThis.__m={apply,F,hist,N,setK:function(v){k=v;}};";
const t0 = Date.now();
eval(code);
console.log("load+precompute ms:", Date.now() - t0);
const M = globalThis.__m;

// re-implement a black-count reader by re-running apply with k sweep:
// apply() writes into img; count blacks via the same F/thr logic — instead,
// instrument: eval exposes k, apply, F, hist, N in this scope.
function measure(kval) {
  M.setK(kval);
  const t1 = Date.now();
  M.apply();
  const ms = Date.now() - t1;
  // recount threshold to get ink
  const hist = M.hist, F = M.F, N = M.N;
  hist.fill(0);
  for (let i = 0; i < N; i++) { let q = (F[i] * 512) | 0; if (q < 0) q = 0; if (q > 512) q = 512; hist[q]++; }
  const target = N * 0.45; let acc = 0, thr = 0.5;
  for (let q = 0; q <= 512; q++) { acc += hist[q]; if (acc >= target) { thr = (q + 0.5) / 512; break; } }
  const B = new Uint8Array(N);
  let black = 0;
  for (let i = 0; i < N; i++) { B[i] = F[i] < thr ? 1 : 0; black += B[i]; }
  return { ink: black / N, B, ms };
}

let worst = 0, wi = -1, prev = null;
const states = {};
for (let i = 0; i <= 200; i++) {
  const kv = i / 200;
  const { ink, B, ms } = measure(kv);
  if ([0, 50, 100, 150, 200].includes(i)) states[kv] = ink;
  if (prev) {
    let fl = 0;
    for (let j = 0; j < M.N; j++) if (B[j] !== prev[j]) fl++;
    fl /= M.N;
    if (fl > worst) { worst = fl; wi = i; }
  }
  prev = B;
}
console.log("ink @ 0,.25,.5,.75,1:", Object.entries(states).map(([k, v]) => `${k}:${v.toFixed(4)}`).join(" "));
console.log("worst flip per 1/200 step:", (worst * 100).toFixed(2) + "%", "at step", wi);
console.log("apply() ms:", measure(0.37).ms);
