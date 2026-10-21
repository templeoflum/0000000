const assert=require('node:assert/strict');
const {midiMessages,pickedUp}=require('../hardware_mapping.js');
assert.deepEqual(midiMessages([0xB2,7,127]),[{type:176,channel:2,number:7,value:1}]);
assert.deepEqual(midiMessages([0x92,40,127,0x82,40,64]),[{type:144,channel:2,number:40,value:1},{type:144,channel:2,number:40,value:0}]);
assert.equal(midiMessages([0xB0,7,12,0xF8,8,127]).length,2,'running status and realtime bytes');
assert.equal(midiMessages([0xF0,1,2,0xF7]).length,0,'ignore sysex');
assert.equal(pickedUp(null,.1,.8),false);assert.equal(pickedUp(.1,.9,.8),true);assert.equal(pickedUp(null,.79,.8),true);assert.equal(pickedUp(.2,.3,undefined),false);
// Exercise actual mapping lifecycle with a small DOM stub, not an alternate implementation.
const fs=require('node:fs'),vm=require('node:vm');
class Element{constructor(tag){this.tag=tag;this.children=[];this.style={};this.value='';}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}setAttribute(){}get options(){return this.children;} }
const midi=new Element('div'),pad=new Element('div');let id='instance-A',now=2000,dispatches=[],released=0;
const binding={kind:'hold',ref:{kind:'effect',key:'test'}};
const axis={kind:'axis',ref:{kind:'effect',key:'test'},slot:'Amount'};
const stored={midi:{f1:{binding:axis,source:{device:'Intech',type:176,channel:0,number:1}},b1:{binding,source:{device:'Intech',type:144,channel:0,number:4}}},ps4:{triangle:{binding}}};
const win={document:{createElement:t=>new Element(t)},localStorage:{getItem:()=>JSON.stringify(stored),setItem(){}},HeartMapping:{choices:k=>[{label:'Unassigned',binding:null},{label:'Test',binding:k==='axis'?axis:binding}],identity:()=>id,state:()=>({arena_connected:true}),read:()=>.5,dispatch:(b,v)=>{dispatches.push([b,v]);return b.kind==='hold'?()=>released++:null;}},addEventListener(){}};
win.window=win;win.globalThis=win;win.performance={now:()=>now};win.Date=Date;win.setInterval=()=>{};vm.runInNewContext(fs.readFileSync(require.resolve('../hardware_mapping.js'),'utf8'),win);
win.HeartHardwareMapping.mount(midi,pad);
function find(n,text){if(n.textContent===text)return n;for(const x of n.children||[]){const f=find(x,text);if(f)return f;}}
find(pad,'Grab controller').onclick();win.HeartHardwareMapping.frame({connected:true,enabled:true,buttons:{}});now+=16;win.HeartHardwareMapping.frame({connected:true,enabled:true,buttons:{triangle:true}});assert.equal(dispatches.length,1,'triangle mapped');id='instance-B';win.HeartHardwareMapping.frame({connected:true,enabled:true,buttons:{triangle:true}});assert.equal(released,1,'target replacement releases captured hold');
find(midi,'Arm MIDI').onclick();win.HeartHardwareMapping.hardware({events:[],midi:['Intech']});
win.HeartHardwareMapping.hardware({events:[{seq:1,kind:'midi',device:'Intech',bytes:[176,1,0]}],midi:['Intech']});assert.equal(dispatches.length,1,'no jump before pickup');
win.HeartHardwareMapping.hardware({events:[{seq:2,kind:'midi',device:'Intech',bytes:[176,1,100]}],midi:['Intech']});assert.equal(dispatches.length,2,'crossing value picks up');
win.HeartHardwareMapping.hardware({events:[{seq:3,kind:'midi',device:'Intech',bytes:[144,4,127]}],midi:['Intech']});assert.equal(dispatches.length,3);win.HeartHardwareMapping.hardware({events:[],midi:[]});assert.equal(released,2,'disconnect releases MIDI hold');
console.log('Hardware mapping: MIDI parsing, pickup, PS4 dispatch, target replacement and disconnect release passed');
