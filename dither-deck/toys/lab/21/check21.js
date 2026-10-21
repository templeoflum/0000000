// headless QA for 21.html: extract script, stub DOM, measure ink + granularity
const fs = require("fs");
const html = fs.readFileSync("C:/Users/User/Documents/0000000/dither-deck/toys/21.html", "utf8");
const script = html.slice(html.indexOf("<script>") + 8, html.indexOf("</script>", html.indexOf("<script>")));
// cut the rail boilerplate + tail (needs real DOM events); keep the machine up to first apply();
const machine = script.slice(0, script.indexOf("const rail=document.getElementById"));

// --- DOM stubs ---
const W = 680;
const pixels = new Uint8ClampedArray(W * W * 4);
const imgStub = { data: pixels };
const ctxStub = {
  createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
  putImageData: function (im) { imgStub.data = im.data; },
};
const sceneStub = {
  width: 0, height: 0, style: {},
  getContext: () => ctxStub,
  getBoundingClientRect: () => ({ width: 340, left: 0 }),
};
global.document = {
  getElementById: (id) => (id === "scene" ? sceneStub : null),
};
global.window = { devicePixelRatio: 2 };

const t0 = Date.now();
eval(machine);
const loadMs = Date.now() - t0;

function ink() {
  let black = 0;
  for (let i = 0; i < W * W; i++) if (imgStub.data[i * 4] === 0) black++;
  return black / (W * W);
}
function snap() { return imgStub.data.slice(); }
function diff(a, b) {
  let n = 0;
  for (let i = 0; i < a.length; i += 4) if (a[i] !== b[i]) n++;
  return n / (W * W);
}

// stops: k exactly on stops
console.log("load+precompute time (ms):", loadMs);
const stopK = [0, 1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7, 6 / 7, 1];
for (const kk of stopK) { k = kk; apply(); console.log(`k=${kk.toFixed(3)} ink=${ink().toFixed(4)}`); }

// 200-step sweep
let prev = null, worst = 0, worstK = -1, sum = 0;
for (let s = 0; s <= 200; s++) {
  k = s / 200; apply();
  const cur = snap();
  if (prev) { const f = diff(prev, cur); sum += f; if (f > worst) { worst = f; worstK = k; } }
  prev = cur;
}
console.log(`worst flip per 1/200 step: ${worst.toFixed(4)} at k=${worstK.toFixed(3)}, mean=${(sum / 200).toFixed(4)}`);

// timing of apply
const t1 = Date.now();
for (let s = 0; s <= 50; s++) { k = s / 50; apply(); }
console.log("apply() avg ms:", ((Date.now() - t1) / 51).toFixed(2));
