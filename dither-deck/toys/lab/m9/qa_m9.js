// headless QA for m9.html: run the real machine code with a mocked DOM,
// then measure ink per state and 200-step flip fractions on the real output.
const fs = require("fs");
const html = fs.readFileSync("C:/Users/User/Documents/0000000/dither-deck/toys/m9.html", "utf8");
const m = html.match(/<script>([\s\S]*?)const rail=document\.getElementById\("rail"\);/);
if (!m) { console.error("FAIL: rail cut not found"); process.exit(1); }
let code = m[1];
if (!/let k=0/.test(code)) { console.error("FAIL: let k=0 missing"); process.exit(1); }
if (!/function apply\(/.test(code)) { console.error("FAIL: function apply( missing"); process.exit(1); }
if (!/document\.getElementById\("scene"\)/.test(code)) { console.error("FAIL: scene ref missing"); process.exit(1); }

// mock DOM
const S = 680;
const px = new Uint8ClampedArray(S * S * 4);
const ctx = {
  createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
  putImageData: (im) => { px.set(im.data); },
};
const scene = { width: 0, height: 0, getContext: () => ctx };
const document = { getElementById: (id) => (id === "scene" ? scene : null) };
const window = {};

// expose internals: append probes before the rail cut
code += "\n;globalThis.__probe={get k(){return k},set k(v){k=v},apply,U,N,UAM,UBY,remap,img,ctx};\n";
const fn = new Function("document", "window", "parent", "location", "URLSearchParams", code);
fn(document, window, window, { search: "" }, URLSearchParams);

const P = globalThis.__probe;
if (!P) { console.error("FAIL: probe missing"); process.exit(1); }
console.log("N =", P.N, " remap(0)=", P.remap(0), " remap(1)=", P.remap(1));

function fieldAt(kval) {
  P.k = kval; P.apply();
  const d = px;
  const on = new Uint8Array(P.N);
  let black = 0;
  for (let gy = 0, i = 0; gy < 340; gy++) {
    const row = gy * 2 * S;
    for (let gx = 0; gx < 340; gx++, i++) {
      const v = d[(row + gx * 2) * 4] === 0 ? 1 : 0;
      on[i] = v; black += v;
    }
  }
  return { on, ink: black / P.N };
}

// ink at named states
for (const kval of [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1]) {
  const { ink } = fieldAt(kval);
  console.log("k=" + kval.toFixed(3), "ink=" + ink.toFixed(4));
}
// 200-step sweep
let prev = null, worst = 0, wa = -1, tot = 0, zero = 0;
for (let i = 0; i <= 200; i++) {
  const kv = i / 200;
  const { on } = fieldAt(kv);
  if (prev) {
    let f = 0;
    for (let j = 0; j < on.length; j++) if (on[j] !== prev[j]) f++;
    const frac = f / on.length;
    tot += frac; if (frac === 0) zero++;
    if (frac > worst) { worst = frac; wa = kv; }
  }
  prev = on;
}
console.log("worst flip per 1/200 step:", worst.toFixed(4), "at k=", wa.toFixed(3),
  " mean:", (tot / 200).toFixed(4), " dead steps:", zero);
// timing
const t0 = Date.now();
for (let i = 0; i <= 200; i++) { P.k = i / 200; P.apply(); }
console.log("201 applies:", (Date.now() - t0) + "ms");
