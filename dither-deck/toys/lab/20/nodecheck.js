// headless harness: stub the DOM, run 20.html's script, measure ink + flips + timing
const fs = require("fs");
const html = fs.readFileSync("C:/Users/User/Documents/0000000/dither-deck/toys/20.html", "utf8");
const m = html.match(/<script>([\s\S]*)<\/script>/);
let src = m[1];
// cut everything from the rail boilerplate on (DOM interaction); keep machine code
const cut = src.indexOf('const rail=document.getElementById("rail");');
src = src.slice(0, cut);
src += "\nglobalThis.__setk = function(v){ k = v; };\nglobalThis.__apply = apply;\n";

const W = 680;
const store = {};
function makeCanvas() {
  return {
    width: 0, height: 0,
    getContext: () => ({
      createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
      putImageData: (im) => { store.img = im; }
    })
  };
}
const canvas = makeCanvas();
global.document = { getElementById: (id) => id === "scene" ? canvas : null };
global.window = {};

const t0 = Date.now();
eval(src);   // defines k, apply, runs precompute + first apply
const t1 = Date.now();
console.log("load(precompute+first apply):", t1 - t0, "ms");

function ink() {
  const d = store.img.data; let b = 0;
  for (let i = 0; i < W * W; i++) if (d[i * 4] === 0) b++;
  return b / (W * W);
}
function snap() { return store.img.data.slice(); }

// ink at milestone states
for (const kk of [0, 0.1, 0.2, 0.3, 0.4, 0.65, 0.9, 0.95, 1.0]) {
  __setk(kk); __apply();
  console.log("k=" + kk.toFixed(2), "ink=" + ink().toFixed(4));
}
// 200-step granularity + apply timing
let prev = null, worst = 0, worstk = 0, tot = 0;
const t2 = Date.now();
for (let s = 0; s <= 200; s++) {
  __setk(s / 200); __apply();
  const cur = snap();
  if (prev) {
    let f = 0;
    for (let i = 0; i < W * W; i++) if (cur[i * 4] !== prev[i * 4]) f++;
    const fr = f / (W * W);
    tot += fr;
    if (fr > worst) { worst = fr; worstk = s / 200; }
  }
  prev = cur;
}
const t3 = Date.now();
console.log("worst flip/step =", (worst * 100).toFixed(2) + "%", "at k=" + worstk.toFixed(3),
            "mean =", (tot / 200 * 100).toFixed(2) + "%");
console.log("201 applies:", t3 - t2, "ms  =>", ((t3 - t2) / 201).toFixed(1), "ms/apply");
