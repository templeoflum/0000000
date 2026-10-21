const fs = require('fs');
const file = process.argv[2];
const ks = (process.argv[3] || '0,0.25,0.5,0.68,0.75,1').split(',').map(Number);
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
for (const k of ks) {
  window.atom.set(k);
  const d = lastFrame.data;
  let ink = 0;
  const n = d.length / 4;
  for (let i = 0; i < n; i++) if (!d[i * 4]) ink++;
  console.log('k=' + k, 'ink=' + (ink / n).toFixed(4));
}
