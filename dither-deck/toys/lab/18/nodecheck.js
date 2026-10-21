// node DOM-stub harness: runs the real 18.html script, measures ink + flips
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const script = html.split("<script>")[1].split("</script>")[0];

let captured = null; // last putImageData payload
const S = 680;
const listeners = {};
function mkEl(id) {
  return {
    id, width: 0, height: 0, style: {},
    getContext() {
      return {
        createImageData(w, h) { return { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }; },
        putImageData(im) { captured = im; }
      };
    },
    setAttribute(k, v) { this[k] = v; },
    getAttribute(k) { return this[k]; },
    addEventListener() {},
    getBoundingClientRect() { return { left: 0, width: 420 }; }
  };
}
const els = { scene: mkEl("scene"), rail: mkEl("rail"), knob: mkEl("knob"), knobcore: mkEl("knobcore") };
global.document = {
  getElementById: id => els[id],
  addEventListener() {}
};
global.window = {
  addEventListener() {}, devicePixelRatio: 1,
};
global.location = { search: "" };
global.parent = global.window;
global.setInterval = () => {};
global.setTimeout = fn => {};
global.URLSearchParams = class { constructor() {} get() { return null; } };

eval(script);

function inkOf() {
  const d = captured.data; let b = 0;
  for (let i = 0; i < S * S; i++) if (d[i * 4] === 0) b++;
  return b / (S * S);
}
function snap() { return captured.data.slice(); }
function flips(a, b) {
  let f = 0;
  for (let i = 0; i < S * S; i++) if ((a[i * 4] === 0) !== (b[i * 4] === 0)) f++;
  return f / (S * S);
}

// ink at named states
for (const kk of [0, 0.25, 0.5, 0.75, 1]) {
  window.atom.set(kk);
  console.log("k=" + kk, "ink=" + inkOf().toFixed(4), "get=" + window.atom.get().toFixed(3));
}
// 200-step sweep
window.atom.set(0);
let prev = snap(), worst = 0, wk = 0, t0 = Date.now(), maxMs = 0;
for (let i = 1; i <= 200; i++) {
  const kk = i / 200;
  const ta = Date.now();
  window.atom.set(kk);
  const ms = Date.now() - ta; if (ms > maxMs) maxMs = ms;
  const cur = snap();
  const f = flips(prev, cur);
  if (f > worst) { worst = f; wk = kk; }
  prev = cur;
}
console.log("worst flip per 1/200 step:", worst.toFixed(4), "at k=" + wk);
console.log("total sweep ms:", Date.now() - t0, "max single apply ms:", maxMs);
// determinism: same k twice -> identical field
window.atom.set(0.37); const s1 = snap();
window.atom.set(0.5); window.atom.set(0.37); const s2 = snap();
console.log("deterministic re-set:", flips(s1, s2) === 0);
