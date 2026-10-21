/* generic headless harness for dither-deck toys.
   usage: node verify_toy.js <toyfile.html> [nsteps]
   stubs DOM/canvas, drives window.atom.set(k) over k=0..1,
   measures ink coverage per state and flip fraction per 1/nsteps step. */
const fs = require('fs');
const file = process.argv[2];
const NSTEPS = parseInt(process.argv[3] || '200', 10);

const src = fs.readFileSync(file, 'utf8');
const m = src.match(/<script>([\s\S]*)<\/script>/);
if (!m) { console.error('no script block'); process.exit(1); }
const js = m[1];

/* ── stubs ── */
let lastFrame = null;          // {data, width, height}
function makeCtx(canvas) {
  return {
    createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
    getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
    putImageData: (img) => { lastFrame = img; },
    fillRect(){}, clearRect(){}, drawImage(){}, save(){}, restore(){},
    beginPath(){}, arc(){}, fill(){}, stroke(){}, moveTo(){}, lineTo(){},
    set fillStyle(v){}, set strokeStyle(v){},
  };
}
function makeEl(id) {
  const el = {
    id, width: 0, height: 0, attrs: {},
    getContext: () => makeCtx(el),
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
  createElement: () => makeEl('offscreen'),
  addEventListener() {},
};
global.window = {
  addEventListener() {},
  atom: null,
  location: { search: '' },
};
global.location = global.window.location;
global.parent = global.window;
global.URLSearchParams = URLSearchParams;
global.setInterval = () => 0;
global.setTimeout = (fn) => 0;

/* ── run the toy ── */
const t0 = Date.now();
eval(js);
const loadMs = Date.now() - t0;
if (!global.window.atom) { console.error('no window.atom'); process.exit(1); }

function frame() {
  if (!lastFrame) throw new Error('no frame rendered');
  return lastFrame;
}
function bitsOf(img) {
  const n = img.width * img.height;
  const b = new Uint8Array(n);
  for (let i = 0; i < n; i++) b[i] = img.data[i * 4] ? 0 : 1;   // black=1
  return b;
}

const inks = [];
let prev = null, worstFlip = 0, worstAt = 0, applyMs = 0;
for (let s = 0; s <= NSTEPS; s++) {
  const k = s / NSTEPS;
  const ta = Date.now();
  global.window.atom.set(k);
  applyMs += Date.now() - ta;
  const b = bitsOf(frame());
  let ink = 0; for (let i = 0; i < b.length; i++) ink += b[i];
  inks.push(ink / b.length);
  if (prev) {
    let fl = 0; for (let i = 0; i < b.length; i++) fl += b[i] !== prev[i] ? 1 : 0;
    const f = fl / b.length;
    if (f > worstFlip) { worstFlip = f; worstAt = k; }
  }
  prev = b;
}
const mn = Math.min(...inks), mx = Math.max(...inks);
console.log(JSON.stringify({
  toy: file, atom: global.window.atom.name,
  loadMs, avgApplyMs: +(applyMs / (NSTEPS + 1)).toFixed(2),
  inkMin: +mn.toFixed(4), inkMax: +mx.toFixed(4),
  worstFlipPer200: +worstFlip.toFixed(4), worstFlipAtK: +worstAt.toFixed(3),
}, null, 1));
