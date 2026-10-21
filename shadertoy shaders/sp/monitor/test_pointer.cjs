const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
class Element extends EventTarget {}
class InputEvent extends Event { constructor(type, {bubbles, cancelable, ...fields}={}) { super(type,{bubbles,cancelable}); Object.assign(this, fields); } }
const document = new EventTarget(), messages=[];
const window = {webkit:{messageHandlers:{heartPointer:{postMessage:m=>messages.push(m)}}}};
vm.runInNewContext(fs.readFileSync(__dirname+'/pointer.js','utf8'), {
  document, window, Element, Event, MouseEvent:InputEvent, KeyboardEvent:InputEvent, WheelEvent:InputEvent
});
const a=new Element(), b=new Element(); let clicks=0, movement=0, escapes=0, ups=0, downs=0, wheel=0;
a.addEventListener('click',()=>clicks++);
a.addEventListener('mousemove',e=>movement+=e.movementY);
a.addEventListener('mousedown',()=>downs++);
a.addEventListener('mouseup',()=>ups++);
a.addEventListener('wheel',e=>{wheel+=e.deltaY;assert.equal(e.deltaMode,1);});
document.addEventListener('keydown',e=>{if(e.key==='Escape')escapes++;});
a.requestPointerLock();
assert.equal(document.pointerLockElement,null, 'Do not claim capture until native acknowledgement');
window.heartPointer.acquired(messages.at(-1).id);
assert.equal(document.pointerLockElement,a);
b.requestPointerLock();
assert.equal(messages.length,1,'Another target cannot steal a capture');
window.heartPointer.move(1,12,false,false,false,false);
window.heartPointer.button(true);window.heartPointer.button(false);
window.heartPointer.wheel(0,-3,1,false,false,false,false);
assert.equal(movement,12); assert.equal(clicks,1);assert.equal(ups,1);assert.equal(downs,1);assert.equal(wheel,-3);
window.heartPointer.released();
window.heartPointer.click();
assert.equal(document.pointerLockElement,null); assert.equal(clicks,1); assert.equal(escapes,1);
b.requestPointerLock(); const cancelled=messages.at(-1).id;document.exitPointerLock(); window.heartPointer.acquired(cancelled);
assert.equal(document.pointerLockElement,null,'Cancelled request cannot become a late capture');
assert.equal(messages.at(-1).action,'unlock');
b.requestPointerLock(); window.heartPointer.failed(messages.at(-1).id);
assert.equal(document.pointerLockElement,null); assert.equal(escapes,2);
a.requestPointerLock();const stale=messages.at(-1).id;document.exitPointerLock();
b.requestPointerLock();const current=messages.at(-1).id;
window.heartPointer.acquired(stale);
assert.equal(document.pointerLockElement,null,'Old acknowledgement cannot acquire the new target');
window.heartPointer.released(stale);window.heartPointer.failed(stale);
assert.equal(window.heartPointer.pendingTarget,b,'Old native callbacks cannot cancel the new request');
window.heartPointer.acquired(current);assert.equal(document.pointerLockElement,b);
let bUps=0;b.addEventListener('mouseup',()=>{bUps++;document.exitPointerLock();});
let bClicks=0;b.addEventListener('click',()=>bClicks++);
window.heartPointer.button(false,stale);assert.equal(bUps,0,'Stale release does not end a new hold');
window.heartPointer.button(false,current);assert.equal(bUps,1);assert.equal(bClicks,0,'Ending a hold must not create a follow-on click');
assert.equal(document.pointerLockElement,null);
console.log('Pointer adapter: acknowledgement, button/wheel routing, click compatibility, cancellation, stale callbacks and failure passed');
