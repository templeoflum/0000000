const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
class Element extends EventTarget {}
class InputEvent extends Event { constructor(type, {bubbles, ...fields}={}) { super(type,{bubbles}); Object.assign(this, fields); } }
const document = new EventTarget(), messages=[];
const window = {webkit:{messageHandlers:{heartPointer:{postMessage:m=>messages.push(m)}}}};
vm.runInNewContext(fs.readFileSync(__dirname+'/pointer.js','utf8'), {
  document, window, Element, Event, MouseEvent:InputEvent, KeyboardEvent:InputEvent
});
const a=new Element(), b=new Element(); let clicks=0, movement=0, escapes=0;
a.addEventListener('click',()=>clicks++);
a.addEventListener('mousemove',e=>movement+=e.movementY);
document.addEventListener('keydown',e=>{if(e.key==='Escape')escapes++;});
a.requestPointerLock();
assert.equal(document.pointerLockElement,null, 'Do not claim capture until native acknowledgement');
window.heartPointer.acquired();
assert.equal(document.pointerLockElement,a);
b.requestPointerLock();
assert.equal(messages.length,1,'Another target cannot steal a capture');
window.heartPointer.move(1,12,false,false,false,false);
window.heartPointer.click();
assert.equal(movement,12); assert.equal(clicks,1);
window.heartPointer.released();
window.heartPointer.click();
assert.equal(document.pointerLockElement,null); assert.equal(clicks,1); assert.equal(escapes,1);
b.requestPointerLock(); document.exitPointerLock(); window.heartPointer.acquired();
assert.equal(document.pointerLockElement,null,'Cancelled request cannot become a late capture');
assert.equal(messages.at(-1),'unlock');
b.requestPointerLock(); window.heartPointer.failed();
assert.equal(document.pointerLockElement,null); assert.equal(escapes,2);
console.log('Pointer adapter: acknowledgement, routing, release, cancellation, failure passed');
