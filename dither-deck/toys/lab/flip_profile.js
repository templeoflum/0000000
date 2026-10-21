/* flip-rate profile for a toy: flip fraction per 1/200 step, printed per step */
const fs = require('fs');
const file = process.argv[2];
const NSTEPS = parseInt(process.argv[3] || '200', 10);
const src = fs.readFileSync(file, 'utf8');
const js = src.match(/<script>([\s\S]*)<\/script>/)[1];
let lastFrame = null;
function makeCtx() {
  return {
    createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
    putImageData: (i) => { lastFrame = i; },
    fillRect() {}, clearRect() {}, drawImage() {},
  };
}
function makeEl(id) {
  const el = {
    id, attrs: {},
    getContext: makeCtx,
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k] !== undefined ? this.attrs[k] : '30'; },
    addEventListener() {},
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 420, height: 56 }),
    style: {},
  };
  return el;
}
const els = {};
global.document = {
  getElementById: (id) => (els[id] = els[id] || makeEl(id)),
  createElement: () => makeEl('o'),
  addEventListener() {},
};
global.window = { addEventListener() {}, atom: null, location: { search: '' } };
global.location = window.location;
global.parent = window;
global.setInterval = () => 0;
global.setTimeout = () => 0;
eval(js);
let prev = null;
const rates = [];
for (let s = 0; s <= NSTEPS; s++) {
  window.atom.set(s / NSTEPS);
  const d = lastFrame.data, n = d.length / 4;
  const b = new Uint8Array(n);
  for (let i = 0; i < n; i++) b[i] = d[i * 4] ? 0 : 1;
  if (prev) {
    let fl = 0;
    for (let i = 0; i < n; i++) fl += b[i] !== prev[i] ? 1 : 0;
    rates.push([s / NSTEPS, fl / n]);
  }
  prev = b;
}
for (const [k, r] of rates) console.log(k.toFixed(3), (r * 100).toFixed(2));
