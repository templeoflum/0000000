(()=>{
 'use strict';
 const el=(tag,text,attrs={})=>{const e=document.createElement(tag);if(text!==null)e.textContent=text;for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e;};
 const clone=v=>JSON.parse(JSON.stringify(v));const uid=()=>crypto.randomUUID?.()||Array.from(crypto.getRandomValues(new Uint32Array(4)),n=>n.toString(16).padStart(8,'0')).join('');
 let preferred='';try{preferred=localStorage.getItem('heart-performance-layout')||'';}catch{}
 let saved=null,draft=null,active=null,activeRevision=-1,editId='',regionEdit=null,learningSlot=null,editingBinding=null,mode='faders',locked=false,touchDevices=0,native=false,lastFrame=0,lastTouch=0,prevTime=0,savePending=false,grabPending=false,refreshActive=null,suspended=false,actionDirty=false;
 const inputReady=()=>writable()&&!suspended&&!document.hidden&&document.hasFocus();
 const midiPorts=new Map();let pads=[];const cells=[];const pointerSlots=new Map();
 const panel=el('dialog',null,{id:'performance','aria-label':'Performance layout'});
 panel.innerHTML='<div class="perf-row"><strong>Performance</strong><button id="perf-close">Close</button></div><div class="perf-row"><select id="perf-layout" class="grow" aria-label="Performance layout"></select><button id="perf-grab">Grab layout</button><button id="perf-new">New</button><button id="perf-edit">Setup</button></div><div class="perf-row"><select id="perf-mode" aria-label="Trackpad regions"><option value="faders">4 faders</option><option value="pads">8 pads</option></select><button id="perf-touch">Grab trackpad</button><select id="perf-nav" aria-label="Controller mode"><option value="perform">PS4 · Perform</option><option value="navigate">PS4 · Navigate</option></select><button id="perf-arm">Arm control</button></div><div id="perf-grid"></div><div id="perf-state" role="status"></div><div id="perf-devices"></div>';
 const editor=el('dialog',null,{id:'perf-editor','aria-label':'Layout setup'});
 editor.innerHTML='<div class="perf-row"><strong>Layout setup</strong><button id="perf-save">Save</button><button id="perf-edit-close">Close</button></div><div class="perf-edit-body"><div class="perf-edit-list"><input id="perf-name" aria-label="Layout name"><select id="perf-control-list" size="8" aria-label="Layout controls"></select><button id="perf-add-control">Add control</button><button id="perf-remove-control">Remove control</button></div><div class="perf-form"><div class="perf-row"><label>Label<input id="perf-label"></label><label>Control<select id="perf-kind"><option value="continuous">Fader</option><option value="button">Action</option><option value="rate">Rate</option><option value="intensity">Intensity</option></select></label></div><fieldset><legend>Destination</legend><div class="perf-row"><label>Find<input id="perf-find" type="search"></label><label>Target<select id="perf-target"></select></label></div><div class="perf-row"><label>Parameter<select id="perf-param"></select></label><label class="inline-check"><input id="perf-follow" type="checkbox">Follow selection</label><button id="perf-member-add">Add</button></div><div id="perf-members" class="perf-members"></div><div id="perf-action-row" class="perf-row"><label>Action<select id="perf-action"><option value="toggle">Toggle</option><option value="on">On</option><option value="off">Off</option><option value="in">IN</option><option value="out">OUT</option><option value="drive-on">Drive on</option><option value="drive-off">Drive off</option><option value="trigger">Trigger</option><option value="hold">Hold</option><option value="downbeat">Downbeat</option><option value="open">Open</option><option value="settle">Settle</option><option value="shuffle">Shuffle</option><option value="return_home">Return Home</option><option value="set_home">Set Home</option><option value="launch">Launch clip</option><option value="select">Select target</option></select></label><label class="inline-check"><input id="perf-momentary" type="checkbox">Momentary</label></div><div id="perf-launch-row" class="perf-row"><label>Layer<select id="perf-launch-layer"></select></label><label>Clip<select id="perf-launch-clip"></select></label></div></fieldset><fieldset id="perf-motion"><legend>Gesture</legend><div class="perf-row"><label>Entry<select id="perf-entry"><option value="absolute">Absolute</option><option value="relative">Relative</option><option value="pickup">Pickup</option></select></label><label>Release<select id="perf-release"><option value="hold">Hold value</option><option value="zero">Return to zero</option><option value="home">Return to reference</option></select></label><label>Seconds<input id="perf-seconds" type="number" min="0" max="120" step="0.05"></label><label>Reference %<input id="perf-reference" type="number" min="0" max="100" step="1"></label></div></fieldset><fieldset><legend>Inputs</legend><div class="perf-row"><button id="perf-learn">Learn input</button><label>Trackpad<select id="perf-region"><option value="">Unassigned</option></select></label></div><div id="perf-bindings" class="perf-bindings"></div><div class="perf-row"><label>Knob encoding<select id="perf-encoding"><option value="absolute">Absolute</option><option value="twos-complement">Two’s complement</option><option value="binary-offset">Binary offset</option><option value="sign-magnitude">Sign / magnitude</option></select></label><label>Stick<select id="perf-axis"><option value="relative">Relative rate</option><option value="absolute">Absolute position</option></select></label></div><div class="perf-row"><label>Sensitivity<input id="perf-sensitivity" type="number" min="0.001" max="16" step="0.05"></label><label>Dead zone %<input id="perf-deadzone" type="number" min="0" max="95"></label><label>Trigger %<input id="perf-threshold" type="number" min="0" max="100"></label><label class="inline-check"><input id="perf-invert" type="checkbox">Reverse</label></div></fieldset></div></div><div id="perf-edit-feedback" class="perf-feedback" role="status"></div>';
 document.body.append(panel,editor);const open=el('button','Performance',{id:'performance-open'});$('arm').before(open);
 const router=new HeartControllers.Router({emit:d=>send(d),learn:learnInput,contacts:drawContacts,navigate:direction=>{
  if(editor.open||document.activeElement?.matches('input,select,textarea'))return;
  if(['up','down'].includes(direction)){
   const list=catalog.layers.filter(l=>!l.stage),i=list.findIndex(l=>l.i===navLayer),n=list[(i+(direction==='down'?1:-1)+list.length)%list.length];if(n)navigate(navScope==='stage'?'clip':navScope,n.i);
  }else{const list=scopeTargets(),i=list.findIndex(t=>t.id===selected),n=list[(i+(direction==='right'?1:-1)+list.length)%list.length];if(n)chooseTarget(n.id);}
 }});
 const current=()=>draft?.controls.find(c=>c.id===editId);
 const findParam=id=>catalog.targets.flatMap(t=>t.params).find(p=>p.id===id);
 const targetOf=id=>catalog.targets.find(t=>t.params.some(p=>p.id===id));
 const labelOf=m=>m.follow==='selection'?'Selection · '+m.name:((targetOf(m.id)?.label||'Unavailable')+' · '+(findParam(m.id)?.name||'Control'));
 const displayed=()=>active||saved;
 const controlFor=i=>{const l=displayed(),id=l?.surface?.[mode]?.[i];return l?.controls.find(c=>c.id===id);};
 function inform(s){$('perf-edit-feedback').textContent=s;}
 function request(id){if(id)send({cmd:'layout_get',id},false);}
 function updateList(){const list=state.performance?.layouts||[],select=$('perf-layout'),old=saved?.id||preferred||select.value;const sig=JSON.stringify(list);if(select.dataset.sig!==sig){select.replaceChildren(...list.map(l=>option(l.id,l.name)));select.dataset.sig=sig;}if(list.some(l=>l.id===old))select.value=old;if(!saved&&select.value)request(select.value);}
 function renderGrid(){
  cells.length=0;$('perf-grid').replaceChildren();
  for(let i=0;i<(mode==='faders'?4:8);i++){
   const c=controlFor(i),box=el('div',null,{class:'perf-cell'}),name=el('strong',c?.label||((mode==='faders'?'Fader ':'Pad ')+(i+1))),dest=el('div',null,{class:'perf-destination'});
   const destination=c?.members?.map(labelOf).join(' + ')|| (c?.press?.binding?labelOf(c.press.binding):catalog.targets.find(t=>t.id===c?.press?.target)?.label||c?.press?.cmd||'Unassigned');dest.textContent=destination;dest.title=destination;box.append(name,dest);
   let play,output;if(mode==='faders'){
    output=el('output','—');play=el('input',null,{type:'range',min:0,max:1,step:'any','aria-label':(c?.label||'Fader '+(i+1))+' performance'});box.append(output,play);
    play.oninput=()=>{if(!c)return;pointerSlots.set(c.id,play);send({cmd:'control',slot:c.id,phase:'move',value:+play.value});};
    const end=()=>{if(c&&pointerSlots.has(c.id)){send({cmd:'control',slot:c.id,phase:'end'});pointerSlots.delete(c.id);}};
    play.onpointerup=play.onpointercancel=play.onchange=play.onblur=end;
   }else{
    play=el('button',c?.label||'Unassigned',{class:'perf-play','aria-label':(c?.label||'Pad '+(i+1))+' performance'});box.append(play);
    const begin=()=>{if(!c||pointerSlots.has(c.id))return;pointerSlots.set(c.id,play);send({cmd:'control',slot:c.id,phase:'begin',value:1});};
    const end=()=>{if(c&&pointerSlots.has(c.id)){send({cmd:'control',slot:c.id,phase:'end'});pointerSlots.delete(c.id);}};
    play.onpointerdown=e=>{e.preventDefault();play.setPointerCapture(e.pointerId);begin();};play.onpointerup=play.onpointercancel=play.onlostpointercapture=end;
    play.onkeydown=e=>{if([' ','Enter'].includes(e.key)){e.preventDefault();if(!e.repeat)begin();}};play.onkeyup=end;play.onblur=end;
   }
   const setup=el('button','Setup',{class:'perf-setup','aria-label':(c?.label||'Region '+(i+1))+' setup'});setup.onclick=()=>openEditor(c?.id,{group:mode,index:i});box.append(setup);$('perf-grid').append(box);cells.push({box,play,output,c});
  }
  paint();
 }
 function paint(){
  const running=state.performance?.active===active?.id&&!!active,ready=writable()&&running;
  $('perf-grab').textContent=running?'Release layout':'Grab layout';$('perf-grab').disabled=!state.connected||(!saved&&!running)||grabPending;
  $('perf-arm').textContent=state.armed?'Disarm':'Arm control';$('perf-arm').disabled=!state.connected;
  $('perf-touch').disabled=!ready||!touchDevices||!native;$('perf-touch').textContent=locked?'Release trackpad · Esc':'Grab trackpad';$('perf-touch').classList.toggle('on',locked);
  $('perf-mode').disabled=locked;$('perf-layout').disabled=!!active;$('perf-edit').disabled=!saved||locked;
  $('perf-new').disabled=!!active||locked;$('pad-grab').disabled=!writable()||!!active;
  $('perf-state').textContent=state.error||(active?.name||saved?.name||'No layout')+' · '+(running?(state.armed?'Grabbed':'Grabbed · disarmed'):'Released');
  for(const {box,play,output,c} of cells){const s=state.performance?.controls.find(s=>s.id===c?.id);play.disabled=!ready||!s?.ready;box.classList.toggle('unavailable',!!c&&running&&!s?.ready);box.classList.toggle('active',!!s?.held);
   if(output&&c){const value=s?.value;output.textContent=!running?'—':!s?.ready?'Unavailable':value==null?'—':c.kind==='rate'?['⅛','¼','½','1','2','4','8'][Math.round(value*6)]+'×':Math.round(value*100)+'%';if(value!=null&&!pointerSlots.has(c.id))play.value=value;}
  }
  $('perf-devices').textContent=[touchDevices?'Trackpad connected':'Trackpad unavailable',pads.length?pads.map(p=>p.name+(p.ambiguous?' · ambiguous':'')).join(', '):'PS4 disconnected',midiPorts.size?[...midiPorts.values()].join(', '):'MIDI disconnected'].join(' · ');
 }
 function drawContacts(fingers){for(const c of cells)c.box.querySelectorAll('.perf-dot').forEach(d=>d.remove());for(const f of fingers){const cell=cells[f.region];if(!cell)continue;const dot=el('span',null,{class:'perf-dot'});dot.style.left=(Math.max(.04,Math.min(.96,f.x*4-f.region%4))*100)+'%';dot.style.top=(mode==='pads'?(1-f.y)*2-Math.floor(f.region/4):1-f.y)*100+'%';cell.box.append(dot);}}
 function releaseTouch(){if(locked||router.touchLocked)window.webkit?.messageHandlers?.heartInputs?.postMessage({action:'release'});locked=false;router.touchGrab(false);document.documentElement.classList.remove('perf-captured');paint();}
 function suspend(){releaseTouch();router.reset();router.enabled=false;for(const id of pointerSlots.keys())send({cmd:'control',slot:id,phase:'end'});pointerSlots.clear();send({cmd:'input_release'});}
 function cancelLearn(){learningSlot=null;$('perf-learn').textContent='Learn input';}
 function learnInput(raw){
  if(!learningSlot||!draft)return false;const slot=current();if(!slot)return false;
  if(slot.kind!=='button'&&raw.type==='button')return true;
  draft.inputs=draft.inputs.filter(b=>!(b.device===raw.device&&b.control===raw.control));
  draft.inputs.push({device:raw.device,control:raw.control,slot:learningSlot,name:raw.name,encoding:$('perf-encoding').value,behavior:$('perf-axis').value,sensitivity:+$('perf-sensitivity').value,deadzone:+$('perf-deadzone').value/100,threshold:+$('perf-threshold').value/100,invert:$('perf-invert').checked});editingBinding=draft.inputs.at(-1);
  inform((raw.name||'Controller')+' · '+raw.control+' → '+slot.label);cancelLearn();renderBindings();return true;
 }
 function configureRegion(c,region){
  if(!region)return;draft.surface||={faders:[],pads:[]};const control=(region.group==='pads'?'pad:':'fader:')+region.index;
  draft.surface[region.group][region.index]=c.id;draft.inputs=draft.inputs.filter(b=>!(b.device==='trackpad'&&b.control===control));draft.inputs.push({device:'trackpad',control,slot:c.id});
 }
 function newControl(kind='continuous'){return {id:uid(),label:kind==='button'?'Action':'Control',kind,members:[],entry:'absolute',release:'hold',release_time:.15,home:0};}
 function openEditor(id,region=null){
  releaseTouch();cancelLearn();draft=clone(saved||active||{id:uid(),name:'Performance',controls:[],inputs:[],surface:{faders:[],pads:[]}});regionEdit=region;
  let c=draft.controls.find(c=>c.id===id)||draft.controls[0];if(region&&!id){c=newControl(region.group==='pads'?'button':'continuous');draft.controls.push(c);configureRegion(c,region);}
  if(!c){c=newControl();draft.controls.push(c);}editId=c.id;$('perf-name').value=draft.name;inform('');renderControlList();loadControl();editor.showModal();
 }
 function renderControlList(){$('perf-control-list').replaceChildren(...draft.controls.map(c=>option(c.id,c.label)));$('perf-control-list').value=editId;}
 function fillTargets(){const chosen=$('perf-target').value||selected,q=$('perf-find').value.toLowerCase(),list=catalog.targets.filter(t=>!q||t.label.toLowerCase().includes(q));$('perf-target').replaceChildren(...list.map(t=>option(t.id,t.label)));if(list.some(t=>t.id===chosen))$('perf-target').value=chosen;fillParams();}
 function fillParams(){const chosen=$('perf-param').value,t=catalog.targets.find(t=>t.id===$('perf-target').value),c=current(),list=t?.params.filter(p=>c?.kind==='button'||num(p))||[];$('perf-param').replaceChildren(...list.map(p=>option(p.id,p.name)));if(list.some(p=>String(p.id)===chosen))$('perf-param').value=chosen;}
 function actionName(a){if(!a)return'toggle';if(a.cmd==='manual')return a.value===true?'on':a.value===false?'off':'trigger';if(a.cmd==='envelope')return a.direction;if(a.cmd==='drive')return a.on?'drive-on':'drive-off';if(a.cmd==='gesture')return a.action;return a.cmd;}
 function loadControl(){
  cancelLearn();const c=current();if(!c)return;
  $('perf-label').value=c.label;$('perf-kind').value=c.kind;$('perf-kind').disabled=draft.inputs.some(b=>b.slot===c.id&&b.device==='trackpad');
  $('perf-entry').value=c.entry||'absolute';$('perf-release').value=c.release||'hold';$('perf-seconds').value=c.release_time??.15;$('perf-reference').value=(c.home||0)*100;
  $('perf-action').value=actionName(c.press);$('perf-momentary').checked=typeof c.release==='object'&&c.kind==='button';actionDirty=!c.press;
  $('perf-follow').checked=c.press?.binding?.follow==='selection';$('perf-find').value='';fillTargets();
  const binding=c.press?.binding||c.members?.[0];const t=c.press?.target||targetOf(binding?.id)?.id;if(t){$('perf-target').value=t;fillParams();}if(binding?.id)$('perf-param').value=binding.id;
  $('perf-launch-layer').replaceChildren(...catalog.layers.map(l=>option(l.i,l.name)));if(c.press?.layer)$('perf-launch-layer').value=c.press.layer;fillClips();if(c.press?.col)$('perf-launch-clip').value=c.press.col;
  loadBinding(draft.inputs.find(b=>b.slot===c.id&&b.device!=='trackpad'));
  $('perf-region').replaceChildren(option('','Unassigned'),...Array.from({length:c.kind==='button'?8:4},(_,i)=>option(i,(c.kind==='button'?'Pad ':'Fader ')+(i+1))));
  const region=draft.inputs.find(b=>b.device==='trackpad'&&b.slot===c.id);$('perf-region').value=region?region.control.split(':')[1]:'';
  renderMembers();renderBindings();showKinds();
 }
 function showKinds(){const button=$('perf-kind').value==='button',a=$('perf-action').value;$('perf-action-row').hidden=!button;$('perf-motion').hidden=button;$('perf-members').hidden=button;$('perf-member-add').hidden=button;$('perf-launch-row').hidden=!button||a!=='launch';$('perf-momentary').disabled=!['on','off','in','out','drive-on','drive-off','hold'].includes(a);if($('perf-momentary').disabled)$('perf-momentary').checked=false;}
 function fillClips(){const l=catalog.layers.find(l=>l.i===+$('perf-launch-layer').value);$('perf-launch-clip').replaceChildren(...(l?.clips||[]).map(c=>option(c.col,c.name)));}
 function renderMembers(){const c=current();$('perf-members').replaceChildren();for(const [i,m] of (c.members||[]).entries()){
  const row=el('div',null,{class:'perf-member'}),label=el('strong',labelOf(m),{title:labelOf(m)});row.append(label);
  for(const [key,name,fallback] of [['weight','Weight',1],['low','Low',0],['high','High',1]]){const input=el('input',null,{type:'number',step:'any','aria-label':labelOf(m)+' '+name,title:name});input.value=m[key]??fallback;input.onchange=()=>m[key]=+input.value;row.append(input);}
  const remove=el('button','×',{'aria-label':'Remove '+labelOf(m)});remove.onclick=()=>{c.members.splice(i,1);renderMembers();};row.append(remove);$('perf-members').append(row);
 }}
 function renderBindings(){const c=current();$('perf-bindings').replaceChildren();for(const b of draft.inputs.filter(b=>b.slot===c.id)){
  const row=el('div',null,{class:'perf-binding'}),label=el('span',(b.name||b.device)+' · '+b.control),remove=el('button','Clear');row.append(label);if(b.device!=='trackpad'){const edit=el('button',editingBinding===b?'Editing':'Edit');edit.onclick=()=>{storeBinding();loadBinding(b);renderBindings();};row.append(edit);}row.append(remove);remove.onclick=()=>{draft.inputs=draft.inputs.filter(x=>x!==b);if(editingBinding===b)loadBinding();if(b.device==='trackpad'){const group=b.control.startsWith('pad:')?'pads':'faders';draft.surface[group][+b.control.split(':')[1]]=null;$('perf-region').value='';}renderBindings();};$('perf-bindings').append(row);
 }}
 function loadBinding(b){editingBinding=b||null;b||={};$('perf-encoding').value=b.encoding||'absolute';$('perf-axis').value=b.behavior||'relative';$('perf-sensitivity').value=b.sensitivity??.5;$('perf-deadzone').value=(b.deadzone??.12)*100;$('perf-threshold').value=(b.threshold??.6)*100;$('perf-invert').checked=!!b.invert;}
 function storeBinding(){if(editingBinding&&draft.inputs.includes(editingBinding))Object.assign(editingBinding,{encoding:$('perf-encoding').value,behavior:$('perf-axis').value,sensitivity:+$('perf-sensitivity').value,deadzone:+$('perf-deadzone').value/100,threshold:+$('perf-threshold').value/100,invert:$('perf-invert').checked});}
 function storeControl(){
  const c=current();if(!c)return;c.label=$('perf-label').value.trim()||'Control';c.kind=$('perf-kind').value;
  if(c.kind==='button'&&actionDirty){
   const a=$('perf-action').value,p=findParam(+$('perf-param').value),target=$('perf-target').value,b=$('perf-follow').checked?{follow:'selection',name:p?.name}:{id:p?.id};
   let press,release;if(['on','off','toggle','trigger','in','out','drive-on','drive-off'].includes(a)&&!p)throw Error('Choose a parameter');
   if(a==='in'||a==='out'){press={cmd:'envelope',binding:b,direction:a};release={...press,direction:a==='in'?'out':'in'};}
   else if(a.startsWith('drive-')){press={cmd:'drive',binding:b,on:a==='drive-on'};release={...press,on:!press.on};}
   else if(a==='on'||a==='off'){press={cmd:'manual',binding:b,value:num(p)?a==='on'?p.max:p.min:a==='on'};release={...press,value:num(p)?a==='on'?p.min:p.max:a!=='on'};}
   else if(a==='toggle')press={cmd:'toggle',binding:b};
   else if(a==='trigger')press={cmd:'manual',binding:b,value:true};
   else if(a==='hold'){press={cmd:'hold',...($('perf-momentary').checked?{on:true}:{})};release={cmd:'hold',on:false};}
   else if(['open','settle','shuffle'].includes(a))press={cmd:'gesture',target,action:a};
   else if(a==='launch')press={cmd:'launch',layer:+$('perf-launch-layer').value,col:+$('perf-launch-clip').value};
   else press={cmd:a,...(['return_home','set_home','select'].includes(a)?{target}:{})};
   c.press=press;delete c.release;if($('perf-momentary').checked&&release)c.release=release;delete c.members;
  }else if(c.kind!=='button'){delete c.press;c.members||=[];c.entry=$('perf-entry').value;c.release=$('perf-release').value;c.release_time=+$('perf-seconds').value;c.home=+$('perf-reference').value/100;}
  storeBinding();
  draft.name=$('perf-name').value.trim()||'Performance';
 }
 open.onclick=()=>{if(panel.open)panel.close();else{panel.show();updateList();renderGrid();}};
 $('perf-close').onclick=()=>{releaseTouch();panel.close();};$('perf-arm').onclick=()=>$('arm').click();
 $('perf-layout').onchange=()=>request($('perf-layout').value);
 $('perf-grab').onclick=()=>{suspend();releasePad();grabPending=true;send({cmd:active?'layout_release':'layout_grab',...(active?{}:{id:saved.id})},false);paint();};
 $('perf-new').onclick=()=>{
  if(active){inform('Release the layout first');return;}
  const layers=catalog.layers.filter(l=>!l.stage).slice().reverse().slice(mixerBank*8,mixerBank*8+4),controls=[];
  for(const l of layers){const p=catalog.targets.find(t=>t.kind==='layer'&&t.layer===l.i)?.params.find(p=>p.name==='Level'&&num(p));if(p)controls.push({id:uid(),label:l.name,kind:'continuous',members:[{id:p.id,weight:1}],entry:'absolute',release:'hold'});}
  saved={id:uid(),name:'Layer bank',controls,inputs:controls.map((c,i)=>({device:'trackpad',control:'fader:'+i,slot:c.id})),surface:{faders:controls.map(c=>c.id),pads:[]}};openEditor(controls[0]?.id);
 };
 $('perf-edit').onclick=()=>openEditor();$('perf-mode').onchange=()=>{releaseTouch();mode=$('perf-mode').value;renderGrid();};
 $('perf-nav').onchange=()=>{router.reset();router.nav=$('perf-nav').value==='navigate';router.enabled=writable()&&!!active;};
 $('perf-touch').onclick=()=>{if(locked)releaseTouch();else if(writable()&&active){releasePad();window.webkit?.messageHandlers?.heartInputs?.postMessage({action:'grab'});}};
 $('perf-edit-close').onclick=()=>editor.close();editor.addEventListener('close',()=>{cancelLearn();draft=null;});
 $('perf-control-list').onchange=()=>{try{storeControl();editId=$('perf-control-list').value;regionEdit=null;loadControl();}catch(e){inform(e.message);}};
 $('perf-add-control').onclick=()=>{try{storeControl();const c=newControl();draft.controls.push(c);editId=c.id;regionEdit=null;renderControlList();loadControl();}catch(e){inform(e.message);}};
 $('perf-remove-control').onclick=()=>{draft.controls=draft.controls.filter(c=>c.id!==editId);draft.inputs=draft.inputs.filter(b=>b.slot!==editId);for(const group of ['faders','pads'])draft.surface[group]=draft.surface[group].map(id=>id===editId?null:id);if(!draft.controls.length)draft.controls.push(newControl());editId=draft.controls[0].id;renderControlList();loadControl();};
 $('perf-label').onchange=()=>{current().label=$('perf-label').value;renderControlList();};$('perf-find').oninput=fillTargets;$('perf-target').onchange=fillParams;$('perf-launch-layer').onchange=fillClips;$('perf-action').onchange=showKinds;
 $('perf-kind').onchange=()=>{const c=current();c.kind=$('perf-kind').value;c.members||=[];if(c.kind==='button'){delete c.release;actionDirty=true;}$('perf-region').replaceChildren(option('','Unassigned'),...Array.from({length:c.kind==='button'?8:4},(_,i)=>option(i,(c.kind==='button'?'Pad ':'Fader ')+(i+1))));showKinds();fillParams();};
 $('perf-member-add').onclick=()=>{const p=findParam(+$('perf-param').value);if(!p||!num(p)){inform('Choose a numeric parameter');return;}const m=$('perf-follow').checked?{follow:'selection',name:p.name,low:p.min,high:p.max,weight:1}:{id:p.id,low:p.min,high:p.max,weight:1};current().members||=[];if(!current().members.some(x=>x.id&&x.id===m.id||x.follow&&x.name===m.name))current().members.push(m);renderMembers();};
 $('perf-region').onchange=()=>{const c=current(),group=c.kind==='button'?'pads':'faders';for(const g of ['faders','pads'])draft.surface[g]=draft.surface[g].map(id=>id===c.id?null:id);draft.inputs=draft.inputs.filter(b=>!(b.slot===c.id&&b.device==='trackpad'));if($('perf-region').value!=='')configureRegion(c,{group,index:+$('perf-region').value});renderBindings();};
 $('perf-learn').onclick=()=>{if(learningSlot)cancelLearn();else{storeBinding();setMidiLearn(false);learningSlot=editId;$('perf-learn').textContent='Listening…';inform('');}};
 $('perf-save').onclick=()=>{try{storeControl();cancelLearn();savePending=true;send({cmd:'layout_save',layout:draft},false);inform('Saving…');}catch(e){inform(e.message);}};
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){releaseTouch();cancelLearn();}},true);
 const suppress=e=>{if(locked){e.preventDefault();e.stopImmediatePropagation();}};for(const name of ['wheel','touchmove','gesturestart','gesturechange','gestureend','contextmenu'])document.addEventListener(name,suppress,{capture:true,passive:false});
 for(const id of ['perf-target','perf-param','perf-follow','perf-action','perf-momentary','perf-launch-layer','perf-launch-clip'])$(id).addEventListener('change',()=>actionDirty=true);
 window.addEventListener('blur',()=>{suspended=true;suspend();});window.addEventListener('focus',()=>{suspended=false;router.padDevices.clear();});window.addEventListener('pagehide',suspend);document.addEventListener('visibilitychange',()=>{if(document.hidden){suspended=true;suspend();}else suspended=false;});
 function message(m){
  if(m.type==='layout'&&m.layout){saved=m.layout;preferred=saved.id;try{localStorage.setItem('heart-performance-layout',preferred);}catch{}if(savePending){const before=editingBinding;savePending=false;draft=clone(saved);renderControlList();loadControl();if(before)loadBinding(draft.inputs.find(b=>b.device===before.device&&b.control===before.control));renderBindings();inform(active?.id===saved.id?'Saved · release and grab to apply':'Saved');}updateList();if(!active)renderGrid();}
  if(m.type==='layout_active'){
   active=m.layout;refreshActive=null;activeRevision=state.performance?.revision??-1;router.configure(active,inputReady()&&!!active,activeRevision);grabPending=false;if(active){saved=clone(active);$('perf-layout').value=active.id;}releaseTouch();renderGrid();
  }
  if(m.type==='state'){
   const p=m.performance;if(p&&p.revision!==activeRevision&&refreshActive!==p.revision){refreshActive=p.revision;send({cmd:'layout_get',active:true},false);}
   if(!writable()||!p?.active){if(locked)releaseTouch();}
   if(p?.controls.some(c=>c.held&&!c.ready))releaseTouch();
   router.configure(active,inputReady()&&p?.active===active?.id,p?.revision);updateList();paint();
   if(m.error&&savePending){savePending=false;inform(m.error);}if(m.error)grabPending=false;
  }
  if(m.type==='catalog'&&active)paint();
 }
 window.heartNativeInputs=m=>{
  native=true;lastFrame=performance.now();
  if(m.type==='suspend'){suspended=true;suspend();return;}
  if(m.type==='resume'){suspended=false;router.padDevices.clear();return;}
  if(m.type==='capture'){locked=!!m.locked;router.touchGrab(locked,mode);document.documentElement.classList.toggle('perf-captured',locked);if(m.error)error(m.error);paint();return;}
  touchDevices=m.touchDevices||0;pads=m.gamepads||[];router.gamepads(pads,performance.now()/1000);
  for(const frame of m.touch||[]){lastTouch=performance.now();if(!router.touch(frame))releaseTouch();}paint();
 };
 const browserPad=p=>({id:'gc:web:'+p.id,name:p.id,axes:Object.fromEntries(['lx','ly','rx','ry'].map((n,i)=>[n,p.axes[i]||0])),buttons:Object.fromEntries(['cross','circle','square','triangle','l1','r1','l2','r2','share','options','l3','r3','up','down','left','right'].map((n,i)=>[n,p.buttons[i]?.value||0]))});
 function tick(t){const dt=Math.min(.05,(t-prevTime)/1000);prevTime=t;
  if(!native){const ps=Array.from(navigator.getGamepads?.()||[]).filter(Boolean).map(browserPad);const counts=new Map();ps.forEach(p=>counts.set(p.id,(counts.get(p.id)||0)+1));ps.forEach(p=>p.ambiguous=counts.get(p.id)>1);pads=ps;router.gamepads(ps,t/1000);}
  if(native&&t-lastFrame>1500&&router.enabled)suspend();if(locked&&router.fingers.size&&t-lastTouch>500)releaseTouch();router.tick(t/1000,dt);requestAnimationFrame(tick);
 }
 setInterval(()=>{if(locked)window.webkit?.messageHandlers?.heartInputs?.postMessage({action:'heartbeat'});},500);
 window.heartPerformance={message,suspend,busy:()=>locked||!!learningSlot||editor.open,midi:m=>{const learning=!!learningSlot,used=router.midi(m);return learning||used;},ports:inputs=>{const current=new Set(inputs.map(i=>i.id));for(const id of midiPorts.keys())if(!current.has(id)){midiPorts.delete(id);router.disconnect(id);}for(const p of inputs)midiPorts.set(p.id,p.name);paint();},router};
 requestAnimationFrame(tick);updateList();renderGrid();window.webkit?.messageHandlers?.heartMidi?.postMessage('scan');
})();
