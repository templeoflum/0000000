/* smoke test for the unified deck: stub DOM, activate every module,
   set a few k values, verify a frame renders each time (instant switching). */
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const js = src.match(/<script>([\s\S]*)<\/script>/)[1];

let lastFrame = null;
const CTX_METHODS = ['beginPath', 'closePath', 'arc', 'arcTo', 'ellipse', 'fill', 'stroke',
  'moveTo', 'lineTo', 'rect', 'fillRect', 'strokeRect', 'clearRect', 'save', 'restore',
  'translate', 'rotate', 'scale', 'transform', 'setTransform', 'resetTransform',
  'quadraticCurveTo', 'bezierCurveTo', 'setLineDash', 'clip', 'fillText', 'strokeText'];
function makeCtx(onPut) {
  const ctx = {
    createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
    getImageData: (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4), width: w, height: h }),
    measureText: () => ({ width: 0 }),
  };
  for (const m of CTX_METHODS) ctx[m] = () => {};
  ctx.putImageData = (i) => { lastFrame = i; if (onPut) onPut(i); };
  ctx.drawImage = () => {};
  return ctx;
}
function makeEl(id) {
  const el = {
    id, width: 0, height: 0, attrs: {}, children: [], _cls: new Set(),
    getContext: () => makeCtx(),
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k] !== undefined ? this.attrs[k] : '30'; },
    addEventListener() {},
    appendChild(c) { this.children.push(c); return c; },
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 420, height: 56 }),
    style: {},
    classList: {
      add: (c) => el._cls.add(c),
      toggle: (c, on) => { on ? el._cls.add(c) : el._cls.delete(c); },
    },
    set innerHTML(v) { el.children = []; },
    set textContent(v) { el._text = v; },
    get textContent() { return el._text || ''; },
  };
  return el;
}
const els = {};
global.document = {
  getElementById: (id) => (els[id] = els[id] || makeEl(id)),
  createElement: (tag) => makeEl(tag),
  addEventListener() {},
};
global.window = { addEventListener() {}, location: { search: '' } };
global.location = window.location;
global.parent = window;
global.setInterval = () => 0;
global.setTimeout = () => 0;

/* canvases keep their last putImageData so the view blit can see a frame */
const origMake = makeEl;
global.document.createElement = (tag) => {
  const el = origMake(tag);
  if (tag === 'canvas') {
    const ctx = makeCtx((i) => { el.__lastData = i.data; });
    el.getContext = () => ctx;
  }
  return el;
};

eval(js + '\n;global.__REG=REG;global.__ATOMS=ATOMS;global.__MOLS=MOLS;');

const REG = global.__REG;
const ATOMS = global.__ATOMS;
const MOLS = global.__MOLS;

console.log('modules:', REG.length, '| atoms:', ATOMS.length, '| mols:', MOLS.length);
let fail = 0;
const labels = ATOMS.map(a => a.label);
for (const mo of MOLS) for (const v of mo.vers) labels.push(mo.label + (mo.vers.length > 1 ? '·' + v.vt : ''));
let li = 0;
for (const m of REG) {
  const label = labels[li++] || m.name;
  try {
    for (const k of [0, 0.37, 0.63, 1]) {
      m.set(k);
      if (!lastFrame || !lastFrame.data || !lastFrame.data.length) throw new Error('no frame at k=' + k);
    }
    console.log('  ok   ', label);
  } catch (e) {
    fail++;
    console.log('  FAIL ', label, '-', e.message);
  }
}
console.log(fail ? fail + ' FAILURES' : 'all modules render at every k probed');
