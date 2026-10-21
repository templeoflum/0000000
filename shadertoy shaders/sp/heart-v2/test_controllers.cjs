const assert=require('node:assert/strict');
const {Router,relativeCC}=require('./controllers');
const layout={id:'test',controls:[...Array.from({length:4},(_,i)=>({id:'f'+i,kind:'continuous'})),...Array.from({length:8},(_,i)=>({id:'p'+i,kind:'button'}))],inputs:[...Array.from({length:4},(_,i)=>({device:'trackpad',control:'fader:'+i,slot:'f'+i})),...Array.from({length:8},(_,i)=>({device:'trackpad',control:'pad:'+i,slot:'p'+i})),{device:'midi',control:'cc:0:1',slot:'f0',encoding:'absolute'},{device:'midi',control:'cc:0:2',slot:'f1',encoding:'twos-complement',sensitivity:1},{device:'midi',control:'note:0:60',slot:'p0'},{device:'gc:ps4',control:'cross',slot:'p1'},{device:'gc:ps4',control:'lx',slot:'f2',behavior:'relative',sensitivity:1},{device:'gc:ps4',control:'l2',slot:'f3'},{device:'gc:ps4',control:'r2',slot:'p2',threshold:.6,hysteresis:.1}]};
function setup(){const events=[],nav=[],r=new Router({emit:e=>events.push(e),navigate:k=>nav.push(k)});r.configure(layout,true,1);return {r,events,nav};}
function touch(r,fs){r.touch({device:'pad',fingers:fs});}
const finger=(id,x,y)=>({id,x,y});
{
 const {r,events}=setup();touch(r,[finger(99,.1,.5)]);r.touchGrab(true);touch(r,[finger(99,.2,.8)]);assert.equal(events.length,0,'opening contact must be seeded');touch(r,[]);
 const fs=[0,1,2,3].map(i=>finger(i,(i+.5)/4,.2+i*.1));touch(r,fs);assert.equal(events.length,4);assert(events.every(e=>e.phase==='begin'));
 touch(r,[...fs.slice(1),finger(0,.9,.9),finger(4,.1,.6)]);assert.equal(events.filter(e=>e.control==='fader:0'&&e.value===.9).length,1,'crossing keeps original lane');assert.equal(events.filter(e=>e.phase==='begin').length,4,'a second contact cannot steal the lane');
 touch(r,[...fs.slice(1),finger(4,.1,.6)]);assert.equal(events.at(-1).phase,'end');touch(r,[...fs.slice(1),finger(4,.1,.7)]);assert.equal(events.filter(e=>e.phase==='begin').length,4,'blocked contact must lift before takeover');
 touch(r,[]);assert.equal(events.filter(e=>e.phase==='end').length,4);
 r.touchGrab(true,'pads');touch(r,Array.from({length:8},(_,i)=>finger(i,(i%4+.5)/4,i<4?.75:.25)));assert.equal(events.filter(e=>e.control.startsWith('pad:')&&e.phase==='begin').length,8);
 r.touchGrab(false);assert.equal(events.filter(e=>e.control.startsWith('pad:')&&e.phase==='end').length,8);
}
{
 const {r,events}=setup();const midi=data=>r.midi({id:'midi',name:'Test',data});
 midi([176,1,64]);assert.equal(events.at(-1).value,64/127);midi([176,1,64]);assert.equal(events.length,1);
 midi([176,2,1]);midi([176,2,1]);midi([176,2,127]);assert.deepEqual(events.slice(1).map(e=>e.delta),[1/32,1/32,-1/32]);
 midi([144,60,100]);assert(!events.some(e=>e.control==='note:0:60'),'first held note after attach is seeded');midi([128,60,0]);midi([144,60,100]);midi([144,60,100]);midi([128,60,0]);assert.deepEqual(events.filter(e=>e.control==='note:0:60').map(e=>e.phase),['begin','end']);
 r.tick(1,.016);assert(events.some(e=>e.control==='cc:0:1'&&e.phase==='end'));r.disconnect('midi');assert.equal(r.raw.size,0);
 assert.equal(relativeCC(65,'binary-offset'),1);assert.equal(relativeCC(63,'binary-offset'),-1);assert.equal(relativeCC(65,'sign-magnitude'),-1);assert.equal(relativeCC(1,'sign-magnitude'),1);
}
{
 const {r,events,nav}=setup();const pad=(axes={},buttons={},ambiguous=false)=>r.gamepads([{id:'gc:ps4',name:'PS4',axes:{lx:0,...axes},buttons:{cross:0,l2:0,r2:0,up:0,...buttons},ambiguous}],0);
 pad({lx:1},{cross:1});r.tick(.01,.01);assert.equal(events.length,0,'held reconnect input must not fire');pad();pad({lx:.8},{cross:1,l2:.2,r2:.61});r.tick(.1,.02);
 assert(events.some(e=>e.control==='cross'&&e.phase==='begin'));assert(events.some(e=>e.control==='lx'&&e.delta>0));assert(events.some(e=>e.control==='l2'&&e.value===.2),'triggers retain continuous values below button threshold');
 pad({lx:.8},{cross:1,r2:.55});assert.equal(events.filter(e=>e.control==='r2'&&e.phase==='end').length,0,'trigger hysteresis');pad({},{});assert(events.some(e=>e.control==='r2'&&e.phase==='end'));
 const start=events.length;r.reset();r.nav=true;pad({lx:.8},{cross:1,up:1});r.tick(.2,.02);assert.deepEqual(nav,['up']);assert.equal(events.length,start,'navigation mode does not also perform mapped actions');
 r.nav=false;pad();pad({}, {cross:1});r.gamepads([],1);assert.equal(events.at(-1).phase,'end');pad({}, {cross:1});assert.equal(events.at(-1).phase,'end','reconnect held remains blocked');
 pad({}, {},true);assert(!r.devices.has('gc:ps4'));
}
{
 const {r,events}=setup();const next=structuredClone(layout);next.inputs[0].slot='f3';r.configure(next,true,1);r.touchGrab(true);touch(r,[finger(1,.1,.5)]);assert.equal(r.layout,next,'same-id refreshed layout must update bindings');
 let learned=0;r.learn=()=>{learned++;return true;};r.midi({id:'new',data:[176,7,99]});assert.equal(learned,1);assert.equal(events.filter(e=>e.device==='new').length,0,'learn never writes');
}
console.log('PASS controller adapters: 4 contacts, 8 pads, identity/collision/seed/release, MIDI encodings and edges, sticks/triggers, navigation isolation, reconnect and layout refresh');
