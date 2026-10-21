/* Shared, explicit hardware assignments. Loading this file never arms controls. */
(function(root){
  'use strict';
  const clamp=v=>Math.max(0,Math.min(1,v));
  function midiMessages(bytes){
    const out=[];let status=0,data=[];
    for(const byte of bytes||[]){const b=Number(byte);if(b>=248)continue;if(b&128){status=b;data=[];continue;}if(status<128||status>=240)continue;data.push(b);const type=status&240,needed=type===192||type===208?1:2;if(data.length<needed)continue;if([128,144,176].includes(type))out.push({type:type===128?144:type,channel:status&15,number:data[0],value:type===128?0:data[1]/127});data=[];}
    return out;
  }
  function pickedUp(previous,value,target){return Number.isFinite(target)&&(Math.abs(value-target)<=.025||(Number.isFinite(previous)&&(previous-target)*(value-target)<=0));}
  if(typeof module!=='undefined')module.exports={midiMessages,pickedUp};
  if(!root.document)return;
  const key='heart-hardware-mapping-v1';let cfg={midi:{},ps4:{}};
  try{const x=JSON.parse(localStorage.getItem(key));if(x&&typeof x==='object')cfg={midi:x.midi||{},ps4:x.ps4||{}};}catch(_){}
  const B=()=>root.HeartMapping;
  const rows={midi:[],ps4:[]};let learning=null,midiArmed=false,padArmed=false,seq=null,lastMidi=0,lastPad=0,prior=null,padTime=0;
  const active=new Map();let midiStatus,padStatus,midiButton,padButton;
  const save=()=>{try{localStorage.setItem(key,JSON.stringify(cfg));}catch(_){}};
  function el(tag,text){const n=document.createElement(tag);if(text)n.textContent=text;return n;}
  function btn(text,fn){const n=el('button',text);n.type='button';n.onclick=fn;return n;}
  function status(kind,text){const n=kind==='midi'?midiStatus:padStatus;if(n)n.textContent=text;const b=kind==='midi'?midiButton:padButton;if(b)b.setAttribute('aria-pressed',String(kind==='midi'?midiArmed:padArmed));}
  function release(kind,reason){for(const [id,a] of active)if(id.startsWith(kind+':')){a.release?.();active.delete(id);}if(kind==='midi')midiArmed=false;else{padArmed=false;prior=null;}status(kind,reason||'Assignments saved · not armed');if(midiButton)midiButton.textContent=midiArmed?'Release MIDI':'Arm MIDI';if(padButton)padButton.textContent=padArmed?'Release controller':'Grab controller';}
  function identity(binding){return B()?.identity?.(binding)??null;}
  function arm(kind){release(kind);const assigned=rows[kind].filter(r=>cfg[kind][r.id]?.binding&&(kind!=='midi'||cfg.midi[r.id].source));if(!assigned.length){status(kind,'Assign a target'+(kind==='midi'?' and Learn a physical control':'')+' first');return;}
    if(!B()?.state()?.arena_connected){status(kind,'Connect Resolume first');return;}
    for(const r of assigned){const binding=cfg[kind][r.id].binding,id=identity(binding);if(id===null){release(kind,'A target is unavailable · choose its current target');return;}active.set(kind+':'+r.id,{binding,identity:id,release:null,held:false,picked:false,previous:null});}
    if(kind==='midi'){midiArmed=true;midiButton.textContent='Release MIDI';status(kind,'ARMED · move each fader/knob through its current value to pick up');}else{padArmed=true;prior=null;padTime=0;padButton.textContent='Release controller';status(kind,'GRABBED · Circle + Options or Escape releases');}}
  function valid(kind){if(!B()?.state()?.arena_connected){release(kind,'Released · Resolume disconnected');return false;}for(const [id,a] of active)if(id.startsWith(kind+':')&&identity(a.binding)!==a.identity){release(kind,'Released · target changed; rearm to use its current instance');return false;}return true;}
  function press(a,down){if(down&&!a.held){a.release=B().dispatch(a.binding,1);a.held=true;}else if(!down&&a.held){if(typeof a.release==='function')a.release();a.release=null;a.held=false;}}
  function paint(){const lists={axis:B()?.choices('axis')||[],button:B()?.choices('button')||[]},signatures={axis:JSON.stringify(lists.axis),button:JSON.stringify(lists.button)};for(const kind of ['midi','ps4'])for(const r of rows[kind]){const c=cfg[kind][r.id]||{},choices=lists[r.axis?'axis':'button'],signature=signatures[r.axis?'axis':'button'];if(r.signature!==signature){r.select.replaceChildren();for(const choice of choices){const o=el('option',choice.label);o.value=JSON.stringify(choice.binding);r.select.append(o);}r.signature=signature;}const wanted=JSON.stringify(c.binding||null);if(![...r.select.options].some(o=>o.value===wanted)){const o=el('option','Unavailable saved target');o.value=wanted;r.select.append(o);}if(document.activeElement!==r.select)r.select.value=wanted;const choice=choices.find(x=>JSON.stringify(x.binding)===wanted);r.targetLabel.textContent=c.binding?(choice?.label||'Saved target unavailable — choose a current target'):'Unassigned · drag this handle onto a target';r.targetLabel.className='hardware-assigned-target'+(c.binding?' is-assigned':'');if(r.learn)r.learn.textContent=learning===r.id?'Move / press now…':c.source?`${c.source.device} · ${c.source.type===176?'CC':'Note'} ${c.source.number} · Learn`:'Learn';}}
  function row(kind,id,title,axis,container){const n=el('div'),handle=el('span','⠿ '+title),select=el('select'),targetLabel=el('div');n.className='hardware-assignment-row';handle.className='hardware-drag-handle';targetLabel.className='hardware-assigned-target';n.style.cssText='display:grid;grid-template-columns:minmax(82px,auto) minmax(0,1fr);gap:6px;align-items:center;margin:5px 0';handle.draggable=true;handle.title='Drag this control onto a parameter, effect action, or layer fader';select.style.cssText='min-width:0;width:100%';select.setAttribute('aria-label',title+' assignment');const r={id,axis,select,handle,targetLabel};rows[kind].push(r);
    const assign=binding=>{if(binding&&!((B()?.choices(axis?'axis':'button')||[]).some(x=>JSON.stringify(x.binding)===JSON.stringify(binding)))){status(kind,'That target does not fit this '+(axis?'continuous control':'button'));return;}release(kind,'Assignment changed · rearm to play');cfg[kind][id]={...cfg[kind][id],binding};save();paint();};
    select.onchange=()=>assign(JSON.parse(select.value));handle.ondragstart=e=>{release(kind);B().assignSource=assign;e.dataTransfer.setData('application/x-heart-control',JSON.stringify({device:kind,input:id,kind:axis?'axis':'button'}));e.dataTransfer.effectAllowed='link';};handle.ondragend=()=>{if(B())B().assignSource=null;};n.append(handle,select,targetLabel);
    if(kind==='midi'){const learn=btn('Learn',()=>{release('midi');learning=learning===id?null:id;status('midi',learning?'Move only the physical control to learn':'Learn cancelled');paint();});learn.style.cssText='grid-column:1/-1;white-space:normal';r.learn=learn;n.append(learn);}container.append(n);}
  function mount(midiContainer,padContainer){
    const midiBody=el("div"),padBody=el("div");midiBody.className=padBody.className="hardware-mapping-body";midiContainer.append(midiBody);padContainer.append(padBody);midiContainer=midiBody;padContainer=padBody;
    midiButton=btn('Arm MIDI',()=>midiArmed?release('midi'):arm('midi'));midiStatus=el('p','Assignments saved locally · not armed');midiStatus.className='hardware-state';midiStatus.setAttribute('role','status');const midiBar=el('div');midiBar.className='hardware-control-bar';midiBar.append(midiButton,midiStatus);midiContainer.append(midiBar);
    padButton=btn('Grab controller',()=>padArmed?release('ps4'):arm('ps4'));padStatus=el('p','Navigate · grab to use assignments · Escape releases');padStatus.className='hardware-state';padStatus.setAttribute('role','status');const padBar=el('div');padBar.className='hardware-control-bar';padBar.append(padButton,padStatus);padContainer.append(padBar);
    const note=el('p','Learn each physical input, then drag its handle onto the thing to control. Faders and knobs use pickup to avoid jumps.');note.className='pane-note';midiContainer.append(note);
    for(const [prefix,label,axis] of [['f','Fader',true],['k','Knob',true],['b','Button',false]])for(let i=1;i<=4;i++)row('midi',prefix+i,label+' '+i,axis,midiContainer);
    const pn=el('p','Navigate normally, or Grab to play these assignments. Drag a control onto its target. Circle + Options or Escape always releases.');pn.className='pane-note';padContainer.append(pn);
    for(const [id,title] of [['cross','✕ Cross'],['circle','○ Circle'],['square','□ Square'],['triangle','△ Triangle'],['l1','L1'],['r1','R1'],['l2','L2 press'],['r2','R2 press'],['l3','L3'],['r3','R3'],['up','D-pad ↑'],['down','D-pad ↓'],['left','D-pad ←'],['right','D-pad →'],['share','Share'],['options','Options'],['touchpad','Touchpad click'],['ps','PS / Home']])row('ps4',id,title,false,padContainer);
    for(const [id,title] of [['lx','Left stick ↔'],['ly','Left stick ↕'],['rx','Right stick ↔'],['ry','Right stick ↕'],['l2-axis','L2 amount'],['r2-axis','R2 amount']])row('ps4',id,title,true,padContainer);
    const support=el('p','PS / Share availability depends on macOS controller support');support.className='pane-note';padContainer.append(support);paint();
  }
  function hardware(info){lastMidi=Date.now();const events=info.events||[];
    if(seq===null){seq=Math.max(0,...events.map(e=>e.seq||0));return;}
    if(info.enabled===false){release('midi','Released · Heart inactive');seq=Math.max(seq,...events.map(e=>e.seq||0));return;}
    if(midiArmed&&!valid('midi'))return;
    for(const e of events){if(e.seq<=seq)continue;seq=e.seq;if(e.kind!=='midi')continue;
      for(const m of midiMessages(e.bytes)){
        const source={device:e.device,type:m.type,channel:m.channel,number:m.number};
        if(learning){const r=rows.midi.find(r=>r.id===learning);if((r.axis&&m.type!==176)||(!r.axis&&m.value===0))continue;for(const [id,c] of Object.entries(cfg.midi))if(id!==learning&&JSON.stringify(c.source)===JSON.stringify(source))delete c.source;cfg.midi[learning]={...cfg.midi[learning],source};learning=null;save();paint();status('midi','Learned · drag this input onto a target, then Arm MIDI');continue;}
        if(!midiArmed)continue;
        for(const r of rows.midi){if(JSON.stringify(cfg.midi[r.id]?.source)!==JSON.stringify(source))continue;const a=active.get('midi:'+r.id);if(!a)continue;if(r.axis){if(!a.picked)a.picked=pickedUp(a.previous,m.value,B().read(a.binding));a.previous=m.value;if(a.picked)B().dispatch(a.binding,m.value);else status('midi',r.id+' · move through '+Math.round(100*B().read(a.binding))+'% to pick up');}else press(a,m.value>0);}
      }
    }
    if(midiArmed&&Array.isArray(info.midi))for(const r of rows.midi)if(active.has('midi:'+r.id)&&!info.midi.includes(cfg.midi[r.id]?.source?.device)){release('midi','Released · MIDI device disconnected');break;}
  }
  function frame(f){lastPad=Date.now();if(!padArmed)return false;if(!f.connected||!f.enabled||!valid('ps4')){release('ps4','Released · controller or target unavailable');return true;}const buttons=f.buttons||{};if(buttons.circle&&buttons.options){release('ps4');return true;}const now=performance.now(),dt=padTime?Math.min(.05,(now-padTime)/1000):0;padTime=now;if(!prior){prior={...buttons};return true;}
    for(const r of rows.ps4){const a=active.get('ps4:'+r.id);if(!a)continue;if(r.axis){const trigger=r.id.endsWith('-axis'),v=f.axes?.[trigger?r.id.slice(0,-5):r.id]||0;if(trigger){if(!a.picked)a.picked=pickedUp(a.previous,v,B().read(a.binding));a.previous=v;if(a.picked)B().dispatch(a.binding,v);}else if(Math.abs(v)>.2){const current=B().read(a.binding);if(Number.isFinite(current))B().dispatch(a.binding,clamp(current+Math.sign(v)*(Math.abs(v)-.2)/.8*.45*dt));}}else{const down=!!buttons[r.id];if(down!==!!prior[r.id])press(a,down);}}
    prior={...buttons};return true;
  }
  root.HeartHardwareMapping={mount,paint,hardware,frame,releaseAll:()=>{release('midi');release('ps4');}};
  root.heartMidiEvents=hardware;
  root.addEventListener('blur',()=>root.HeartHardwareMapping.releaseAll());root.addEventListener('pagehide',()=>root.HeartHardwareMapping.releaseAll());root.addEventListener('keydown',e=>{if(e.key==='Escape')root.HeartHardwareMapping.releaseAll();});
  setInterval(()=>{if(midiArmed&&Date.now()-lastMidi>1500)release('midi','Released · MIDI input heartbeat lost');if(padArmed&&Date.now()-lastPad>1000)release('ps4','Released · controller heartbeat lost');},300);
})(typeof window==='undefined'?globalThis:window);
