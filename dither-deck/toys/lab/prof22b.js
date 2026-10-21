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

function time(k) {
  const a = Date.now();
  window.atom.set(k);
  return Date.now() - a;
}

// fixed k, 10 reps
let ts = [];
for (let r = 0; r < 10; r++) ts.push(time(0.05));
console.log('fixed 0.05 x10:', ts.join(' '));

// alternating two nearby k
ts = [];
for (let r = 0; r < 10; r++) ts.push(time(r % 2 ? 0.05 : 0.06));
console.log('alternating 0.05/0.06 x10:', ts.join(' '));

// fixed again after alternation
ts = [];
for (let r = 0; r < 10; r++) ts.push(time(0.05));
console.log('fixed 0.05 again x10:', ts.join(' '));

// the exact sweep values: is a specific k slow?
for (const k of [0, 0.005, 0.01, 0.1, 0.5, 0.995, 1]) {
  ts = [];
  for (let r = 0; r < 3; r++) ts.push(time(k));
  console.log('k=' + k + ':', ts.join(' '));
}
