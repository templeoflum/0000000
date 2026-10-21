// Isolated DOM/event and timer checks; never connects to the running instrument.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/status.html','utf8');
for(const m of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(m[1]);
const gestureSource=html.split('// FADER GESTURES —')[1].split('// END FADER GESTURES')[0];
const springSource=html.slice(html.indexOf('  function released(i,d,options={})'),html.indexOf('  return {assign,laneOf,popover'));
class InputEvent{
  constructor(type,fields={}){Object.assign(this,{type,bubbles:true,button:0,buttons:0,deltaMode:0,deltaX:0,deltaY:0},fields);}
  preventDefault(){this.defaultPrevented=true;}
  stopImmediatePropagation(){this.stopped=true;}
  stopPropagation(){this.stopped=true;}
}
class Element{
  constructor(){this.listeners={};this.style={};this.dataset={};this.children=[];}
  addEventListener(type,fn,options={}){
    if(options.signal?.aborted)return;
    const entry={fn,capture:!!options.capture};(this.listeners[type]??=[]).push(entry);
    options.signal?.addEventListener('abort',()=>this.listeners[type].splice(this.listeners[type].indexOf(entry),1),{once:true});
  }
  dispatchEvent(e){
    e.target=this;const path=[];for(let p=this;p;p=p.parent)path.push(p);
    for(const capture of [true,false])for(const p of capture?[...path].reverse():path){
      for(const entry of [...(p.listeners[e.type]||[])]){
        if(entry.capture!==capture)continue;entry.fn(e);if(e.stopped)return !e.defaultPrevented;
      }
      if(!capture&&!e.bubbles)break;
    }
    return !e.defaultPrevented;
  }
  appendChild(child){child.parent=this;this.children.push(child);return child;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);this.parent=null;}
  setAttribute(){}
  getBoundingClientRect(){return {top:100,height:200};}
}
function setup(capture='native'){
  const document=new Element(),window=new Element();document.body=document.appendChild(new Element());document.createElement=()=>new Element();
  const messages=[],sent=[],states=[],releases=[],timers=new Map();let time=0,nextTimer=0,value=.3;
  // Each fixture gets its own prototype because the native adapter installs a browser API.
  class Track extends Element{}
  const context=vm.createContext({document,window,Element:Track,Event:InputEvent,MouseEvent:InputEvent,WheelEvent:InputEvent,KeyboardEvent:InputEvent,CustomEvent:InputEvent,
    AbortController,performance:{now:()=>time},Date,Math,
    setTimeout:(fn,delay)=>{const id=++nextTimer;timers.set(id,{fn,at:time+delay});return id;},clearTimeout:id=>timers.delete(id),
    requestAnimationFrame:fn=>{const id=++nextTimer;timers.set(id,{fn,at:time+16});return id;},
    cfgOf:()=>({rel:'hold',spring:.4}),homeOf:()=>.7,cmd:o=>sent.push(o)});
  if(capture==='native'){
    window.webkit={messageHandlers:{heartPointer:{postMessage:m=>messages.push(m)}}};
    vm.runInContext(fs.readFileSync(__dirname+'/../monitor/pointer.js','utf8'),context);
  }else{
    document.pointerLockElement=null;
    document.exitPointerLock=()=>{document.pointerLockElement=null;document.dispatchEvent(new InputEvent('pointerlockchange'));};
  }
  vm.runInContext('//'+gestureSource+'\n'+springSource,context);
  const trk=document.body.appendChild(new Track()),d=new Element();
  if(capture==='denied')trk.requestPointerLock=()=>{throw Error('User activation required');};
  if(capture==='pending')trk.requestPointerLock=()=>{};
  d.getVal=()=>value;d.setVal=v=>{value=v;};
  const gesture=context.bindFaderGesture(d,trk,{getValue:d.getVal,setValue:v=>{value=v;sent.push({value:v});},
    onState:(mode,status)=>states.push({mode,status}),onRelease:(mode,reason)=>{releases.push({mode,reason});if(mode==='hold')context.released(1,d,{rel:'zero',immediate:reason!=='release'});}});
  d.isLocked=gesture.active;
  const fire=(node,type,fields={})=>{const e=new InputEvent(type,fields);node.dispatchEvent(e);return e;};
  const advance=ms=>{const end=time+ms;let count=0;while(true){const due=[...timers].filter(([,t])=>t.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!due)break;
    if(count++>1000)throw Error('Timer loop');const [id,t]=due;timers.delete(id);time=t.at;t.fn();}time=end;};
  const acquire=()=>window.heartPointer.acquired(messages.findLast(m=>m.action==='lock').id);
  return {document,window,trk,d,gesture,messages,sent,states,releases,fire,advance,acquire,get value(){return value;}};
}
{
  const f=setup();f.fire(f.trk,'mousedown',{clientY:150,buttons:1});assert.equal(f.value,.75,'Hold jumps to the absolute track position');
  assert.equal(f.document.pointerLockElement,null,'Capture waits for the native acknowledgement');f.acquire();
  f.window.heartPointer.move(0,-50,false,false,false,false);assert.equal(f.value,1);
  f.window.heartPointer.pressure(2);assert(f.gesture.active(),'Opening press must not immediately unlock');f.window.heartPointer.button(false);assert(f.gesture.active(),'Releasing the initial click stays locked');f.window.heartPointer.move(0,20,false,false,false,false);assert.equal(f.value,.9,'Light movement works without holding a button');f.window.heartPointer.pressure(0);assert(f.gesture.active());f.window.heartPointer.pressure(1);assert.equal(f.gesture.active(),false);f.fire(f.document,'mouseup');assert.equal(f.document.pointerLockElement,null);
  f.advance(1800);assert.equal(f.value,0,'Normal release completes its spring exactly at zero');
  assert.equal(f.releases.length,1,'Native mouseup must not create another click gesture');
}
{
  const f=setup();f.fire(f.trk,'wheel',{deltaY:-26,clientY:170});assert.equal(f.value,.4);
  assert.equal(f.messages.length,0,'Hover scroll never requests native capture');assert(!f.gesture.active());
  f.fire(f.trk,'wheel',{deltaY:-26});assert.equal(f.value,.5);
  const other=f.document.body.appendChild(new Element());let clicks=0;other.addEventListener('click',()=>clicks++);
  f.fire(other,'click');assert.equal(clicks,1,'Hover scroll leaves other controls available');
  f.advance(1000);assert.equal(f.value,.5,'Scrolled level stays put');
}
{
  const f=setup();f.window.heartTouchLive=true;
  const touch=(fingers)=>f.fire(f.document,'hearttouch',{detail:{fingers}});
  f.fire(f.trk,'mousedown',{clientY:150,buttons:1});f.acquire();
  assert.equal(f.value,.3,'Latching does not perform a touch');
  touch([{id:1,state:'touch',y:.8}]);f.window.heartPointer.button(false);
  assert.equal(f.value,.3,'Opening finger is ignored until lifted');
  f.window.heartPointer.pressure(1);assert(f.gesture.active(),'Opening physical press cannot unlatch before first lift');
  touch([]);touch([{id:2,state:'touch',y:.8}]);assert.equal(f.value,.8);
  f.window.heartPointer.move(0,-50,false,false,false,false);assert.equal(f.value,.8,'Mouse deltas cannot fight raw contact position');
  touch([{id:2,state:'break',y:.8}]);f.advance(200);assert(f.value>0&&f.value<.8);assert(f.gesture.active(),'Lift springs without releasing latch');
  f.window.heartPointer.button(true);f.window.heartPointer.button(false);assert(f.gesture.active(),'Tap-to-click after lift must not unlatch');
  touch([{id:3,state:'touch',y:.2}]);assert.equal(f.value,.2,'Retouch interrupts spring immediately');
  touch([]);f.advance(500);assert.equal(f.value,0);assert(f.gesture.active());
  touch([{id:4,state:'touch',y:.6}]);f.window.heartPointer.button(true);f.window.heartPointer.button(false);assert(f.gesture.active(),'Tap-to-click with stale or present raw contact must not unlatch');
  f.window.heartPointer.pressure(0);assert(f.gesture.active(),'Sub-click pressure does not unlatch');
  f.window.heartPointer.pressure(1);assert(!f.gesture.active(),'First physical pressure click unlatches without requiring Force Click');
  f.fire(f.document,'mouseup');f.advance(1800);assert.equal(f.value,0);
}
for(const capture of ['denied','absent']){
  const f=setup(capture);f.fire(f.trk,'mousedown',{clientY:200,buttons:1});assert.equal(f.value,.5);
  assert.equal(f.states.at(-1).status,'in-page','Ordinary browsers expose the in-page fallback');
  f.fire(f.document,'mousemove',{clientY:120,buttons:1});assert.equal(f.value,.9);
  f.fire(f.document,'mouseup',{button:0});assert(f.gesture.active());f.fire(f.document,'mousemove',{clientY:130,buttons:0});assert.equal(f.value,.85);f.fire(f.document,'mousedown',{button:0});assert(!f.gesture.active());f.fire(f.document,'mouseup',{button:0});f.advance(1800);assert.equal(f.value,0);
  f.fire(f.trk,'wheel',{deltaY:-1,deltaMode:1});assert(Math.abs(f.value-16/260)<1e-9);f.advance(180);assert(!f.gesture.active());
}
{
  const f=setup();f.fire(f.trk,'mousedown',{clientY:120,buttons:1});const cancelled=f.messages.at(-1).id;
  f.fire(f.document,'keydown',{key:'Escape'});assert(!f.gesture.active());assert.equal(f.value,0);
  f.window.heartPointer.acquired(cancelled);assert.equal(f.document.pointerLockElement,null,'Esc cancels a pending native capture');
  f.advance(0);f.fire(f.trk,'mousedown',{clientY:160,buttons:1});f.acquire();
  f.window.heartPointer.released(cancelled);assert(f.gesture.active(),'A cancelled request cannot release a later hold');
  f.fire(f.window,'blur');assert(!f.gesture.active());assert.equal(f.value,0,'Blur cannot leave a throttled spring above zero');
}
for(const reason of ['visibility','pagehide','pointercancel','native-release']){
  const f=setup();f.fire(f.trk,'mousedown',{clientY:140,buttons:1});f.acquire();
  if(reason==='visibility'){f.document.hidden=true;f.fire(f.document,'visibilitychange');}
  else if(reason==='native-release')f.window.heartPointer.released(f.messages.at(-1).id);
  else f.fire(reason==='pagehide'?f.window:f.document,reason);
  assert(!f.gesture.active(),reason+' must release capture');assert.equal(f.value,0,reason+' must release the held level');
}
{
  const f=setup('pending');f.fire(f.trk,'wheel',{deltaY:-26});f.advance(180);
  assert.equal(f.messages.length,0,'Scroll cannot leave a pending capture');
}
{
  const f=setup('absent');f.fire(f.trk,'mousedown',{clientY:140,buttons:1});f.fire(f.document,'mouseup');f.fire(f.document,'mousedown');f.fire(f.document,'mouseup');f.advance(32);
  f.fire(f.trk,'wheel',{deltaY:-26});const held=f.value;f.advance(2000);assert.equal(f.value,held,'A new scroll cancels the prior spring without an extra stale write');
  f.fire(f.trk,'mousedown',{clientY:140,buttons:1});f.fire(f.document,'mouseup');f.fire(f.document,'mousedown');f.fire(f.document,'mouseup');f.advance(16);
  f.gesture.dispose();const count=f.sent.length;f.advance(2000);assert.equal(f.sent.length,count,'Removed faders cannot continue writing spring levels');
}
{
  const f=setup('absent');f.fire(f.trk,'mousedown',{clientY:140,buttons:1});f.fire(f.document,'mouseup');f.fire(f.document,'mousedown');f.fire(f.document,'mouseup');f.advance(32);
  assert(f.value>0);f.fire(f.window,'blur');assert.equal(f.value,0,'A spring already in flight also settles before the page can suspend');
  const count=f.sent.length;f.advance(2000);assert.equal(f.sent.length,count);
}
{
  const f=setup();f.document.exitPointerLock();const other=f.document.body.appendChild(new f.trk.constructor());other.requestPointerLock();f.acquire();
  f.fire(f.trk,'mousedown',{clientY:100,buttons:1});assert(!f.gesture.active());assert.equal(f.value,.3,'Another widget owns the pointer until it releases');
}
{
  const p=new Element(),d=new Element(),release={dataset:{k:'rel'},type:'select-one'};let saved=0,stopped=false;
  p.querySelectorAll=()=>[release];p.lastElementChild={};
  const st={cfg:{}};
  const context=vm.createContext({document:{querySelectorAll:()=>[],createElement:()=>p},st,cfgOf:()=>({rel:'hold'}),save:()=>saved++,paintLanes:()=>{}});
  const start=html.indexOf('  function popover(i,d,ev)');vm.runInContext(html.slice(start,html.indexOf('  // ── lock ──',start)),context);
  context.popover(1,d,{stopPropagation:()=>{stopped=true;}});assert(stopped);assert.equal(d.children[0],p,'PAD settings open without the stray effect editor reference');
  release.value='home';release.oninput();assert.equal(st.cfg[1].rel,'home');assert.equal(saved,1,'Saved PAD release settings remain independent of mouse hold');
  p.lastElementChild.onclick();assert.equal(d.children.length,0);
}
console.log('Fader gestures passed: native hold/wheel, absolute movement, spring/lasting levels, click isolation, browser fallback, pending cancellation, release safety and disposal.');
