/* Device decoding only. Layout targets, musical state and release curves belong to the engine. */
(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.HeartControllers=api;})(globalThis,()=>{
 'use strict';
 const clamp=(v,lo=0,hi=1)=>Math.max(lo,Math.min(hi,v));
 const key=(device,control)=>JSON.stringify([device,control]);
 function relativeCC(value,encoding){
  if(encoding==='twos-complement')return value<64?value:value-128;
  if(encoding==='binary-offset')return value-64;
  if(encoding==='sign-magnitude')return value<64?value:-(value-64);
  return 0;
 }
 class Router {
  constructor({emit,learn=()=>false,navigate=()=>{},contacts=()=>{}}){
   Object.assign(this,{emit,learn,navigate,contacts});this.layout=null;this.enabled=false;this.revision=null;
   this.raw=new Map();this.active=new Map();this.blocked=new Set();this.devices=new Set();this.padDevices=new Set();this.touchFrames=new Map();this.fingers=new Map();this.touchBlocked=new Set();this.touchLocked=false;this.touchMode='faders';this.nav=false;
  }
  configure(layout,enabled,revision){
   if(layout!==this.layout || revision!==this.revision || !!enabled!==this.enabled){this.reset();this.layout=layout;this.enabled=!!enabled;this.revision=revision;}
  }
  reset(){
   for(const [k,a] of this.active)this.emit({cmd:'input',device:a.device,control:a.control,phase:'end'});
   this.active.clear();this.blocked=new Set([...this.raw].filter(([,r])=>r.pressed||r.type==='axis'&&Math.abs(r.value)>.12).map(([k])=>k));
   this.touchGrab(false);this.fingers.clear();
  }
  disconnect(device){
   for(const [k,a] of this.active)if(a.device===device){this.emit({cmd:'input',device,control:a.control,phase:'end'});this.active.delete(k);}
   for(const [k,r] of this.raw)if(r.device===device){this.raw.delete(k);this.blocked.delete(k);}
   this.devices.delete(device);
  }
  bindings(device,control){return this.layout?.inputs?.find(b=>b.device===device&&b.control===control);}
  mapped(device,control){return !!this.bindings(device,control);}
  slot(binding){return this.layout?.controls.find(c=>c.id===binding?.slot);}
  send(binding,phase,value,delta){
   const {device,control}=binding,k=key(device,control);
   if(phase==='end'){if(this.active.has(k))this.emit({cmd:'input',device,control,phase});this.active.delete(k);return;}
   if(!this.enabled)return;
   if(!this.active.has(k))phase='begin';this.active.set(k,{device,control,time:this.now||0});
   this.emit({cmd:'input',device,control,phase,...(value===undefined?{}:{value}),...(delta===undefined?{}:{delta})});
  }
  sample(device,control,value,type,name,seed=false){
   if(!Number.isFinite(value))return;const k=key(device,control),prev=this.raw.get(k),binding=this.nav&&device.startsWith('gc:')?null:this.bindings(device,control),slot=this.slot(binding);
   const pressed=type==='axis'?Math.abs(value)>.12:value>0;
   const raw={device,control,value,type,pressed,name};this.raw.set(k,raw);this.devices.add(device);
   const changed=!prev||prev.value!==value;
   if(!seed&&changed&&((type==='axis'&&Math.abs(value)>.35)||type==='cc'||pressed)&&this.learn({...raw})){this.blocked.add(k);return;}
   if(type==='cc'&&(!slot||slot.kind!=='button')){
    if(!binding||!changed&&(binding.encoding||'absolute')==='absolute')return;
    if(seed||!this.enabled)return;
    // A learned encoder event is consumed; its next physical movement is intentional.
    this.blocked.delete(k);
    const encoding=binding.encoding||'absolute';
    if(encoding==='absolute')this.send(binding,'move',binding.invert?1-value/127:value/127);
    else {const delta=relativeCC(value,encoding)*(binding.sensitivity??.5)/32*(binding.invert?-1:1);if(delta)this.send(binding,'move',undefined,clamp(delta,-1,1));}
    return;
   }
   if(type==='axis'&&slot?.kind!=='button'){
    const dead=binding?.deadzone??.12,neutral=Math.abs(value)<=dead;
    if(seed||!prev){if(!neutral)this.blocked.add(k);return;}
    if(neutral){this.blocked.delete(k);if(binding)this.send(binding,'end');return;}
    if(this.blocked.has(k)||!this.enabled||!binding)return;
    if(binding.behavior==='absolute'&&changed)this.send(binding,'move',binding.invert?(1-value)/2:(value+1)/2);
    return;
   }
   if(type==='trigger'&&slot?.kind!=='button'){
    const neutral=value<.02;
    if(seed||!prev){if(!neutral)this.blocked.add(k);return;}
    if(neutral){this.blocked.delete(k);if(binding)this.send(binding,'end');return;}
    if(!this.blocked.has(k)&&binding&&changed)this.send(binding,'move',binding.invert?1-value:value);
    return;
   }
   const analog=type==='trigger'||type==='axis',v=type==='cc'?value/127:type==='axis'?Math.abs(value):value;
   const threshold=analog?(binding?.threshold??.6):type==='cc'?1/127:0.5,hysteresis=analog?(binding?.hysteresis??.1):0;
   const was=prev?.down??false,down=v>=(was?threshold-hysteresis:threshold);raw.down=down;
   if(seed||!prev){if(down)this.blocked.add(k);return;}
   if(!down){this.blocked.delete(k);if(binding)this.send(binding,'end');return;}
   if(this.blocked.has(k)||!this.enabled)return;
   if(this.nav&&device.startsWith('gc:')&&['up','down','left','right'].includes(control)){if(!was)this.navigate(control);return;}
   if(!binding)return;
   if(slot?.kind==='button'){if(!was)this.send(binding,'begin',1);}
   else if(type==='trigger'&&changed)this.send(binding,'move',binding.invert?1-value:value);
  }
  midi(message){
   const [status,n,value]=message.data||[],kind=status&240;
   if(![176,144,128].includes(kind)||!Number.isFinite(value))return false;
   const control=(kind===176?'cc:':'note:')+(status&15)+':'+n;
   const used=this.mapped(message.id,control);
   this.sample(message.id,control,kind===128?0:value,kind===176?'cc':'button',message.name);
   return used;
  }
  gamepads(pads,now){
   this.now=now;const present=new Set();
   for(const pad of pads){present.add(pad.id);if(pad.ambiguous){this.disconnect(pad.id);continue;}
    const seed=!this.padDevices.has(pad.id);
    for(const [c,v] of Object.entries(pad.axes||{}))this.sample(pad.id,c,v,'axis',pad.name,seed);
    for(const [c,v] of Object.entries(pad.buttons||{}))this.sample(pad.id,c,v,['l2','r2'].includes(c)?'trigger':'button',pad.name,seed);
   }
   for(const id of this.padDevices)if(!present.has(id))this.disconnect(id);
   this.padDevices=present;
  }
  tick(now,dt){
   this.now=now;if(!this.enabled)return;
   for(const [k,r] of this.raw){
    if(r.type!=='axis'||this.blocked.has(k)||this.nav&&r.device.startsWith('gc:'))continue;
    const b=this.bindings(r.device,r.control),slot=this.slot(b);if(!b||slot?.kind==='button'||b.behavior==='absolute')continue;
    const dead=b.deadzone??.12;if(Math.abs(r.value)<=dead)continue;
    const delta=(Math.abs(r.value)-dead)/(1-dead)*Math.sign(r.value)*(b.invert?-1:1)*(b.sensitivity??.5)*Math.min(.05,dt);
    this.send(b,'move',undefined,clamp(delta,-1,1));
   }
   for(const [k,a] of this.active)if(a.control.startsWith('cc:')&&this.slot(this.bindings(a.device,a.control))?.kind!=='button'&&now-a.time>.25)this.send(a,'end');
  }
  touchGrab(on,mode=this.touchMode){
   for(const [id,f] of this.fingers)if(f.binding)this.send(f.binding,'end');
   this.fingers.clear();this.touchLocked=!!on;this.touchMode=mode;
   this.touchBlocked=new Set([...this.touchFrames.values()].flatMap(frame=>frame.map(f=>String(f.id))));this.contacts([]);
  }
  touch(frame){
   if(frame.overflow){this.touchGrab(false);return false;}
   this.touchFrames.set(frame.device||'trackpad',frame.fingers||[]);
   const fingers=[...this.touchFrames.values()].flat(),present=new Set(fingers.map(f=>String(f.id)));
   for(const id of this.touchBlocked)if(!present.has(id))this.touchBlocked.delete(id);
   if(!this.touchLocked||!this.enabled)return true;
   for(const [id,f] of this.fingers)if(!present.has(id)){if(f.binding)this.send(f.binding,'end');this.fingers.delete(id);}
   for(const raw of fingers){
    const id=String(raw.id);if(this.touchBlocked.has(id))continue;
    let f=this.fingers.get(id);
    if(!f){
     const region=Math.min(3,Math.floor(clamp(raw.x)*4))+(this.touchMode==='pads'&&raw.y<.5?4:0);
     if([...this.fingers.values()].some(f=>f.region===region)){this.touchBlocked.add(id);continue;}
     const control=(this.touchMode==='pads'?'pad:':'fader:')+region,binding=this.bindings('trackpad',control);
     f={id,region,binding,x:raw.x,y:raw.y};this.fingers.set(id,f);
     if(binding)this.send(binding,'begin',this.touchMode==='pads'?1:clamp(raw.y));
    }else if(f.binding&&this.touchMode==='faders'&&f.y!==raw.y)this.send(f.binding,'move',clamp(raw.y));
    f.x=raw.x;f.y=raw.y;
   }
   this.contacts([...this.fingers.values()].map(({id,region,x,y})=>({id,region,x,y})));return true;
  }
 }
 return {Router,relativeCC};
});
