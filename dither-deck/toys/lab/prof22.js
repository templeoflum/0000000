const fs = require('fs');
const js = fs.readFileSync(process.argv[2], 'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
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

let t = 0;
for (let s = 0; s <= 200; s++) {
  const a = Date.now();
  window.atom.set(s / 200);
  t += Date.now() - a;
}
console.log('varying k, no analysis:', (t / 201).toFixed(1) + 'ms avg');

t = 0;
for (let s = 0; s <= 200; s++) {
  const a = Date.now();
  window.atom.set(s / 200);
  t += Date.now() - a;
  const b = new Uint8Array(462400);
  for (let i = 0; i < 462400; i++) b[i] = lastFrame.data[i * 4] ? 0 : 1;
}
console.log('varying k + bitcopy:', (t / 201).toFixed(1) + 'ms avg');
