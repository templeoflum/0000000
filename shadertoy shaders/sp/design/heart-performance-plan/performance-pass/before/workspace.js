/* The performance workspace only changes presentation and targeting. */
(() => {
  const $=id=>document.getElementById(id);
  const modules={mix:'Layer faders',monitor:'Heart Monitor',rack:'Effects rack',actions:'Play',a:'Parameters A',b:'Parameters B'};
  const defaults=()=>({version:1,columns:[25,44,31],row:46,order:['mix','monitor','rack','actions','a','b'],a:{kind:'follow'},b:{kind:'effect',key:'layer/figure~1/effect/LinearCloner~1'},rack:'follow'});
  let cfg=defaults(),initialized=false,arranging=false,detached=false,state=null,selectedEffect=null,layoutFrame=0;
  const panes={},views={};
  function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
  function button(text,fn,cls,title){const b=node('button',cls,text);b.type='button';b.onclick=fn;if(title)b.title=title;return b;}
  function option(s,value,text){const o=node('option','',text);o.value=value;s.append(o);}
  function save(){cmd({cmd:'surface_cfg',value:{workspace:cfg}});}
  function safeConfig(value){
    const out=defaults();if(!value||value.version!==1)return out;
    if(Array.isArray(value.columns)&&value.columns.length===3&&value.columns.every(x=>Number.isFinite(x)&&x>=15&&x<=65))out.columns=value.columns;
    if(Number.isFinite(value.row))out.row=Math.max(25,Math.min(70,value.row));
    if(Array.isArray(value.order)&&value.order.length===6&&new Set(value.order).size===6&&value.order.every(x=>modules[x]))out.order=value.order;
    for(const k of ['a','b'])if(['follow','source','effect'].includes(value[k]?.kind))out[k]=value[k];
    if(typeof value.rack==='string')out.rack=value.rack;
    return out;
  }
  function layerRole(c){return state?.layers.find(l=>l.i===c.layer)?.name;}
  function sourceRef(c){return {kind:'source',role:layerRole(c),name:c.name,col:c.col,instrument:c.instrument?.id||null};}
  function resolve(ref){
    if(!state)return null;
    if(ref.kind==='follow')return state.clips.find(c=>c.layer===focusLayer)||null;
    if(ref.kind==='source'){
      const found=state.clips.filter(c=>layerRole(c)===ref.role&&c.name===ref.name&&(!ref.col||c.col===ref.col)&&(!ref.instrument||c.instrument?.id===ref.instrument));
      return found.length===1?found[0]:null;
    }
    const found=(state.fx||[]).filter(e=>e.key===ref.key);return found.length===1?found[0]:null;
  }
  const isEffect=c=>typeof c?.key==='string';
  function label(c){return !c?'Unavailable':isEffect(c)?`${c.lname||'Composition'} / ${c.name}`:`${layerRole(c)} / ${c.instrument?.label||c.name}`;}
  function target(c){return {layer:c.layer,col:c.col,instance:c.instance};}
  function send(c,o){cmd({...o,...target(c)});}
  document.body.classList.add('workspace');
  const arrange=button('Arrange',()=>{if(document.pointerLockElement)return;arranging=!arranging;document.body.classList.toggle('arranging',arranging);arrange.setAttribute('aria-pressed',String(arranging));arrange.textContent=arranging?'Lock layout':'Arrange';layout();},'', 'Resize or exchange modules. Lock the arrangement before playing.');arrange.id='arrange';arrange.setAttribute('aria-pressed','false');document.querySelector('h1').append(arrange);
  const dockBack=button('Dock monitor',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('dock-monitor'));dockBack.hidden=true;document.querySelector('h1').append(dockBack);
  const reset=button('Reset layout',()=>{const old=cfg;cfg={...defaults(),a:old.a,b:old.b};layout();save();});reset.id='reset-layout';arrange.after(reset);
  const work=node('main');work.id='workbench';document.body.append(work);
  for(const [id,title] of Object.entries(modules)){
    const pane=node('section','pane'),head=node('header','pane-head'),body=node('div','pane-body');pane.dataset.module=id;head.append(node('strong','',title));pane.append(head,body);work.append(pane);panes[id]={pane,head,body};
    const chooser=node('select','module-choice');chooser.setAttribute('aria-label','Move '+title+' to another area');for(const [k,v] of Object.entries(modules))option(chooser,k,v);chooser.value=id;
    chooser.onchange=()=>{const a=cfg.order.indexOf(id),b=cfg.order.indexOf(chooser.value);[cfg.order[a],cfg.order[b]]=[cfg.order[b],cfg.order[a]];chooser.value=id;layout();save();};head.append(chooser);
  }
  panes.mix.body.append($('strip'));
  const slot=panes.monitor.body;slot.id='monitor-slot';slot.append(node('p','', 'Live output uses the native Heart Monitor.'),button('Dock monitor',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('dock-monitor')));
  panes.monitor.head.append(button('Detach',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('toggle-monitor')));
  panes.monitor.head.append(button('Fit / 1:1',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('fit-monitor')));
  const resumeMonitor=button('Resume monitor',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('resume'));resumeMonitor.hidden=true;panes.monitor.head.append(resumeMonitor);
  window.heartMonitorState=info=>{const changed=detached!==!!info.detached;resumeMonitor.hidden=!info.suspended;detached=!!info.detached;dockBack.hidden=!detached;if(changed)layout();slot.classList.toggle('native-docked',!detached&&!!window.webkit?.messageHandlers?.heartPointer);slot.querySelector('p').textContent=detached?'Heart Monitor is floating. Dock it here, or use Arrange to give this area to another module.':'Open the Heart app for the live GPU monitor.';panes.monitor.head.querySelector('button').textContent=detached?'Dock':'Detach';};
  function reportMonitor(){cancelAnimationFrame(layoutFrame);layoutFrame=requestAnimationFrame(()=>{const r=slot.getBoundingClientRect();window.webkit?.messageHandlers?.heartPointer?.postMessage({action:'monitor-layout',x:r.x,y:r.y,width:r.width,height:r.height,viewportWidth:innerWidth,viewportHeight:innerHeight});});}
  const dividers=[node('div','divider vertical'),node('div','divider vertical'),node('div','divider horizontal')];dividers.forEach(d=>work.append(d));
  function layout(){
    for(const [i,k] of cfg.order.entries()){panes[k].pane.style.gridArea=`${i<3?1:2} / ${i%3+1}`;panes[k].pane.hidden=k==='monitor'&&detached;}
    if(detached){const i=cfg.order.indexOf('monitor'),partner=i<3?i+3:i-3;panes[cfg.order[partner]].pane.style.gridArea=`1 / ${i%3+1} / 3 / ${i%3+2}`;}
    work.style.setProperty('--left',cfg.columns[0]+'fr');work.style.setProperty('--middle',cfg.columns[1]+'fr');work.style.setProperty('--right',cfg.columns[2]+'fr');work.style.setProperty('--top',cfg.row+'fr');work.style.setProperty('--bottom',(100-cfg.row)+'fr');
    requestAnimationFrame(()=>{const r=work.getBoundingClientRect();for(let i=0;i<2;i++){const id=cfg.order[i]==='monitor'&&detached?cfg.order[i+3]:cfg.order[i];const p=panes[id].pane.getBoundingClientRect();dividers[i].style.left=(p.right-r.left+4)+'px';}const top=cfg.order.slice(0,3).find(id=>id!=='monitor'&&(!detached||cfg.order[cfg.order.indexOf(id)+3]!=='monitor'));const p=panes[top].pane.getBoundingClientRect();dividers[2].style.top=(p.bottom-r.top+4)+'px';reportMonitor();});
  }
  dividers.forEach((d,i)=>{d.onpointerdown=e=>{if(!arranging||document.pointerLockElement)return;e.preventDefault();d.setPointerCapture(e.pointerId);const r=work.getBoundingClientRect(),start=[...cfg.columns],total=start.reduce((a,b)=>a+b,0);const move=ev=>{if(i===2)cfg.row=Math.max(25,Math.min(70,(ev.clientY-r.top)/r.height*100));else{const left=i===0?0:start[0]/total*100;const right=i===0?(start[0]+start[1])/total*100:100;const pos=Math.max(left+18,Math.min(right-18,(ev.clientX-r.left)/r.width*100));cfg.columns=start.map(x=>x/total*100);cfg.columns[i]=pos-left;cfg.columns[i+1]=right-pos;}layout();};const end=()=>{d.removeEventListener('pointermove',move);d.removeEventListener('pointerup',end);d.removeEventListener('pointercancel',end);save();};d.addEventListener('pointermove',move);d.addEventListener('pointerup',end);d.addEventListener('pointercancel',end);};});
  new ResizeObserver(()=>layout()).observe(work);new ResizeObserver(reportMonitor).observe(slot);window.addEventListener('resize',reportMonitor);
  // Performance actions target the selected layer; parameter panes retain their own targets.
  const act=panes.actions.body,actName=node('div','target-line'),nav=node('div','action-row');act.append(actName,nav);
  for(const [dir,text] of [['prev','‹ Previous'],['rand','Random'],['next','Next ›']])nav.append(button(text,()=>cmd({cmd:'clip_nav',layer:focusLayer,dir})));
  const sourceActions=node('div','action-row');act.append(sourceActions);
  for(const [action,text,cls] of [['home','Home','home'],['fire','Shuffle','shuffle'],['undo','Undo','']])sourceActions.append(button(text,()=>{const c=resolve({kind:'follow'});if(c)send(c,{cmd:action});},cls));
  const speed=node('select');speed.setAttribute('aria-label','Selected source speed');for(const v of [.0625,.125,.25,.5,1,2,4,8,16])option(speed,v,v+'×');speed.onchange=()=>{const c=resolve({kind:'follow'});if(c)send(c,{cmd:'speed',value:+speed.value});};sourceActions.append(speed);
  act.append(node('div','section-label','Source bank'));const bankSelect=node('select');option(bankSelect,'forms','Forms');option(bankSelect,'all','All sources');bankSelect.onchange=()=>{const l=state.layers.find(l=>l.i===focusLayer);if(l)cmd({cmd:'surface_cfg',value:{banks:{...state.surface?.banks,[l.name]:bankSelect.value}}});};act.append(bankSelect);
  const search=node('input','source-search');search.type='search';search.placeholder='Find a source…';search.setAttribute('aria-label','Find a source');search.oninput=()=>paintActions();act.append(search);
  const sources=node('div','source-list');act.append(sources);const actNote=node('div','pane-note');act.append(actNote);
  act.append(node('div','section-label','Trackpad'));const trackpad=button('Capture faders · L',()=>$('padlock').click());act.append(trackpad,node('p','pane-note','Click a fader to capture the pointer. Click again or press Esc to release.'));
  const lanes=node('div','pad-assignments');act.append(lanes);
  const selectedActions=node('div','action-row');act.append(selectedActions);
  selectedActions.append(button('Clear selected layer',()=>cmd({cmd:'clear',layer:focusLayer})));
  function paintActions(){
    const l=state.layers.find(l=>l.i===focusLayer),c=resolve({kind:'follow'});actName.textContent=`${l?.name||'Layer '+focusLayer} / ${l?.clip||'empty'}`;sourceActions.querySelectorAll('button,select').forEach(x=>x.disabled=!c||!state.arena_connected);if(c&&document.activeElement!==speed)speed.value=c.g.speed??1;
    bankSelect.hidden=!l?.forms?.length;if(document.activeElement!==bankSelect)bankSelect.value=l?.bank||'all';
    const list=(l?.bank==='forms'?l.forms:l?.clips)||[],q=search.value.toLowerCase();const sig=JSON.stringify([focusLayer,l?.ccol,list,q]);
    if(sources.dataset.sig!==sig){sources.dataset.sig=sig;sources.replaceChildren();for(const x of list.filter(x=>x.name.toLowerCase().includes(q))){const b=button(x.name,()=>cmd({cmd:'launch',layer:l.i,col:x.col}));b.classList.toggle('active',x.col===l.ccol);sources.append(b);}}
    actNote.textContent=c?`${c.slots.filter(x=>x.drive).length} active drives · ${c.home_kind||'Home not yet refined'}`:'No Heart source controls on this layer. Effects are still accessible.';
    trackpad.textContent=document.pointerLockElement?'Release · Esc':'Capture faders · L';
    const laneSig=JSON.stringify([state.layers.map(l=>[l.i,l.name]),state.surface?.pad?.assign]);if(lanes.dataset.sig!==laneSig){lanes.dataset.sig=laneSig;lanes.replaceChildren();for(let n=1;n<=4;n++){const label=node('label','',n+' '),select=node('select');select.setAttribute('aria-label','Trackpad lane '+n);option(select,0,'Unassigned');for(const l of state.layers)option(select,l.i,l.name);select.value=state.layers.find(l=>PAD.laneOf(l.i)===n)?.i||0;select.onchange=()=>{for(const l of state.layers)if(PAD.laneOf(l.i)===n)PAD.assign(l.i,0);if(+select.value)PAD.assign(+select.value,n);};label.append(select);lanes.append(label);}}
  }
  // Rack selection opens B without toggling the effect. On/Off remains a separate gesture.
  const scope=node('select');scope.setAttribute('aria-label','Effect rack scope');panes.rack.body.append(scope);const rackList=node('div','fx-list');panes.rack.body.append(rackList);
  scope.onchange=()=>{cfg.rack=scope.value;save();paintRack();};
  function rackOptions(){const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));if(scope.dataset.sig===sig)return;scope.dataset.sig=sig;scope.replaceChildren();option(scope,'follow','Selected layer');option(scope,'all','All effects');option(scope,'composition','Composition');for(const l of state.layers)option(scope,'layer:'+l.name,l.i+' · '+l.name);scope.value=cfg.rack;}
  function openEffect(e,which='b'){cfg[which]={kind:'effect',key:e.key};selectedEffect=e.key;views[which].sig='';save();paintParameters(which);paintRack();}
  function paintRack(){
    rackOptions();const list=(state.fx||[]).filter(e=>cfg.rack==='all'||cfg.rack==='composition'?cfg.rack==='all'||e.scope==='C':cfg.rack==='follow'?e.layer===focusLayer:e.lname===cfg.rack.slice(6));
    const sig=list.map(e=>e.key).join('|');if(rackList.dataset.sig!==sig){rackList.dataset.sig=sig;rackList.replaceChildren();for(const e of list){const row=node('div','fx-row');row.dataset.key=e.key;const toggle=button('',null,'fx-switch');toggle.onpointerdown=ev=>{ev.preventDefault();toggle.setPointerCapture(ev.pointerId);cmd({cmd:'fx_press',key:e.key,instance:e.instance});};const release=()=>cmd({cmd:'fx_release',key:e.key});toggle.onpointerup=release;toggle.onpointercancel=release;toggle.onlostpointercapture=release;const open=button('',()=>openEffect(e),'fx-open');open.append(node('span','fx-name',e.name),node('span','fx-info'));const settings=button('⚙',()=>fxPop(state.fx.find(x=>x.key===e.key)||e,row),'fx-envelope','Envelope and trigger settings');row.append(toggle,open,settings);rackList.append(row);}}
    for(const e of list){const row=[...rackList.children].find(x=>x.dataset.key===e.key);if(!row)continue;row.classList.toggle('chosen',cfg.a.key===e.key||cfg.b.key===e.key);const t=row.querySelector('.fx-switch');t.disabled=e.has_amount===false;t.textContent=e.env>.001?'On':'Off';t.setAttribute('aria-pressed',String(e.env>.001));row.querySelector('.fx-info').textContent=`${e.scope==='C'?'Composition':e.lname} · ${e.pending?'waiting for beat':Math.abs(e.target-e.env)>.015?'fading':e.bypassed?'bypassed':Math.round(e.env*100)+'%'} · ${e.cfg.mode}${e.cfg.key?' · key '+e.cfg.key:''}`;}
  }
  for(const id of ['a','b']){
    const body=panes[id].body,tools=node('div','target-tools'),pick=node('select');pick.setAttribute('aria-label','Target for Parameters '+id.toUpperCase());tools.append(pick);body.append(tools);
    const pin=button('Pin',()=>{const c=resolve(cfg[id]);if(c&&!isEffect(c)){cfg[id]=cfg[id].kind==='follow'?sourceRef(c):{kind:'follow'};views[id].sig='';save();paintParameters(id);}},'','Follow the selected source, or keep this exact instrument in place');tools.append(pin);
    const name=node('div','target-line'),content=node('div');body.append(name,content);views[id]={pick,pin,name,content,sig:'',widgets:{},c:null};
    pick.onchange=()=>{if(document.pointerLockElement)return;cfg[id]=JSON.parse(pick.value);views[id].sig='';save();paintParameters(id);};
  }
  function targetOptions(id){const v=views[id],sig=JSON.stringify([state.clips.map(c=>sourceRef(c)),(state.fx||[]).map(e=>[e.key,e.name,e.lname]),cfg[id]]);if(v.pick.dataset.sig===sig)return;v.pick.dataset.sig=sig;v.pick.replaceChildren();option(v.pick,JSON.stringify({kind:'follow'}),'Follow selected source');for(const c of state.clips)option(v.pick,JSON.stringify(sourceRef(c)),'Source · '+label(c));for(const e of state.fx||[])option(v.pick,JSON.stringify({kind:'effect',key:e.key}),'Effect · '+label(e)+' · '+e.key.split('~').at(-1));const key=JSON.stringify(cfg[id]);if(![...v.pick.options].some(o=>o.value===key))option(v.pick,key,'Pinned target unavailable');v.pick.value=key;}
  function paintParameters(id){
    const view=views[id];view.pick.disabled=!!document.pointerLockElement;if(document.pointerLockElement&&view.content.contains(document.pointerLockElement)){if(resolve(cfg[id])?.instance!==view.c?.instance&&view.summary)view.summary.textContent='Target changed · release the pointer to reconnect this pane';return;}
    targetOptions(id);const c=resolve(cfg[id]);view.c=c;view.pin.hidden=isEffect(c)||cfg[id].kind==='effect';view.pin.textContent=cfg[id].kind==='follow'?'Pin':'Follow';view.name.textContent=c?label(c):cfg[id].kind==='follow'?(state.layers.find(l=>l.i===focusLayer)?.ccol?'Source not yet adapted':'No active source'):'Pinned target unavailable';view.pick.disabled=!!document.pointerLockElement;
    const sig=JSON.stringify([cfg[id],c?.instance,c?.col,isEffect(c)?Object.entries(c.params||{}).map(([n,p])=>[n,p.id,p.valuetype,p.options,p.min,p.max]):c?.slots.map(s=>[s.name,s.choices])]);
    if(view.sig!==sig){view.sig=sig;for(const w of Object.values(view.widgets))w.chip?.dispose();view.widgets={};view.content.replaceChildren();if(!c){view.content.append(node('p','pane-placeholder',cfg[id].kind==='follow'?(state.layers.find(l=>l.i===focusLayer)?.ccol?'This source does not have a Heart instrument adapter yet. Open its Source entry in the effects rack for manual controls. The three Forms pilots already have animated Homes.':'Select a layer with an active source to see its parameters.'):'This exact target is not present. Choose another target above; no controls have been redirected.'));return;}if(isEffect(c))buildEffect(view,c);else buildSource(view,c);}
    if(!c)return;
    if(isEffect(c)){for(const [name,w] of Object.entries(view.widgets)){const p=c.params[name];if(!p)continue;if(w.chip){if(!w.chip.locked)w.chip.set((p.value-(p.min||0))/((p.max??1)-(p.min||0)||1),true);w.readout.textContent=p.view?.display_units==='integer'?'whole steps':p.view?.suffix?.trim()||'native units';}else if(document.activeElement!==w.input){if(w.input.type==='checkbox')w.input.checked=!!p.value;else if(w.input.type!=='button')w.input.value=p.value;}}if(view.amount&&document.activeElement!==view.amount)view.amount.value=c.target;view.summary.textContent=`${c.bypassed?'Bypassed':Math.round(c.env*100)+'% active'} · ${Object.keys(c.params).length} controls · manual effect controls`;}
    else{const moving=c.slots.filter(x=>x.morphing),remaining=Math.max(0,...moving.map(x=>x.morph_remaining||0));view.summary.textContent=`${state.hold?'Motion held · ':''}${c.slots.filter(x=>x.drive).length}/${c.slots.length} drives · ${c.home_kind||'Home'}${moving.length?' · morphing '+remaining.toFixed(1)+'s':''}`;if(document.activeElement!==view.speed)view.speed.value=c.g.speed??1;for(const sl of c.slots){const w=view.widgets[sl.name];if(!w)continue;if(w.picker){if(document.activeElement!==w.picker)w.picker.value=sl.choices[Math.round(sl.v*(sl.choices.length-1))];continue;}w.sl=sl;if(!w.chip.locked)w.chip.set(sl.v,true);if(w.chip.driven!==sl.drive)w.chip.setDriven(sl.drive,true);w.lock.classList.toggle('on',!!sl.lock);if(!w.chip.menusOpen())w.chip.syncConfig({ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,min:sl.lo,max:sl.hi});}}
  }
  function buildSource(view,c){
    const toolbar=node('div','param-actions');view.content.append(toolbar);toolbar.append(button('Home',()=>send(c,{cmd:'home'}),'home'),button('Shuffle',()=>send(c,{cmd:'fire'}),'shuffle'),button('Undo',()=>send(c,{cmd:'undo'})));
    view.speed=node('select');view.speed.setAttribute('aria-label',label(c)+' speed');for(const x of [.0625,.125,.25,.5,1,2,4,8,16])option(view.speed,x,x+'×');view.speed.onchange=()=>send(c,{cmd:'speed',value:+view.speed.value});toolbar.append(view.speed);
    for(const [mode,text] of [['unison','⊙'],['harmonic','♩'],['irrational','∞']])toolbar.append(button(text,()=>send(c,{cmd:'timing',mode}),'',mode+' timing'));
    toolbar.append(button('Set Home',()=>send(c,{cmd:'home_set'}),'set-motion-home','Save current relationships and ranges as this source’s Home'));
    view.summary=node('div','drive-state');view.content.append(view.summary);
    if(c.feedback_behaviors?.length){const fb=node('div','param-actions');for(const name of c.feedback_behaviors)fb.append(button(name,()=>send(c,{cmd:'feedback_behavior',name})));fb.append(button('Reset trails',()=>send(c,{cmd:'feedback_reset'})));view.content.append(fb);}
    const grid=node('div','parameter-grid');view.content.append(grid);
    for(const sl of c.slots){const row=node('div','slot2');grid.append(row);if(sl.choices?.length){row.append(node('label','',sl.name));const picker=node('select');picker.setAttribute('aria-label',sl.name);for(const s of sl.choices)option(picker,s,s);picker.onchange=()=>send(c,{cmd:'choice',slot:sl.name,option:picker.value});row.append(picker);view.widgets[sl.name]={picker};continue;}
      const mini=node('div','ax'),w={sl};const good=button('★',()=>send(c,{cmd:'good_go',slot:sl.name}),'axb','Return to this axis’s good value');const lock=button('Lock',()=>send(c,{cmd:'slot_cfg',slot:sl.name,key:'Lock',value:!w.sl.lock}),'axb','Exclude this axis from shuffles');const fire=button('⚡',()=>send(c,{cmd:'fire_slot',slot:sl.name}),'axb','Shuffle this axis');mini.append(good,lock,fire);row.append(mini);
      const chip=createSmartParam({label:sl.name,value:sl.v,driven:sl.drive,wrap:!!sl.cyc,min:sl.lo,max:sl.hi,ratioLabels:RATIOS,ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,
        onInput:value=>send(c,{cmd:'manual',slot:sl.name,value}),onDrive:on=>send(c,{cmd:'drive',slot:sl.name,on}),onReset:()=>send(c,{cmd:'good_go',slot:sl.name}),onHomeSet:()=>send(c,{cmd:'good_set',slot:sl.name}),
        onConfig:cf=>{const entries=[['Ratio',RATIOS[cf.ratio],w.sl.ratio],['Mult',cf.multiplier,w.sl.mult],['Offset',cf.offset,w.sl.offset??0],['Lo',cf.min,w.sl.lo],['Hi',cf.max,w.sl.hi]];for(const [key,value,old] of entries)if(value!==old)send(c,{cmd:'slot_cfg',slot:sl.name,key,value});}});
      row.append(chip.el);Object.assign(w,{chip,lock});view.widgets[sl.name]=w;
    }
  }
  function buildEffect(view,e){
    view.summary=node('div','drive-state');view.content.append(view.summary);
    const actions=node('div','param-actions');actions.append(button('Envelope settings',()=>fxPop(e,view.name)));view.content.append(actions);
    view.amount=null;if(e.has_amount){const line=node('label','effect-level','Effect amount');const amount=node('input');amount.type='range';amount.min=0;amount.max=1;amount.step=.001;amount.oninput=()=>cmd({cmd:'fx_amount',key:e.key,instance:e.instance,value:+amount.value});line.append(amount);view.content.append(line);view.amount=amount;}
    const grid=node('div','parameter-grid');view.content.append(grid);
    for(const [name,p] of Object.entries(e.params||{})){if(name==='Opacity'&&e.has_amount)continue;const row=node('div','slot2');grid.append(row);
      if(['ParamRange','ParamFloat','ParamInt','ParamNumber'].includes(p.valuetype)){
        const lo=p.min??0,span=(p.max??1)-lo||1,integer=['ParamInt','ParamNumber'].includes(p.valuetype)||p.view?.display_units==='integer';
        const chip=createSmartParam({label:name,value:(p.value-lo)/span,min:0,max:1,step:integer?1/span:.01,format:v=>kitFormat(integer?Math.round(lo+v*span):lo+v*span),parse:v=>(v-lo)/span,onInput:v=>cmd({cmd:'fx_param',key:e.key,instance:e.instance,name,value:integer?Math.round(lo+v*span):lo+v*span})});
        // Until effect motion is connected, a parameter name is a label, not a false Drive switch.
        const old=chip.el.querySelector('.sp-name'),title=node('div','sp-name',name);old.replaceWith(title);const readout=node('div','native-value');row.append(chip.el,readout);view.widgets[name]={chip,readout};
      }else{
        row.append(node('label','',name));const line=node('div','effect-manual');let input;
        if(p.valuetype==='ParamChoice'){input=node('select');for(const x of p.options||[])option(input,x,x);}
        else{input=node('input');input.type=['ParamBool','ParamBoolean'].includes(p.valuetype)?'checkbox':p.valuetype==='ParamColor'?'color':'button';if(input.type==='button')input.value='Trigger';}
        input.setAttribute('aria-label',name);const change=()=>cmd({cmd:'fx_param',key:e.key,instance:e.instance,name,value:input.type==='checkbox'?input.checked:input.type==='button'?true:input.value});if(input.type==='button')input.onclick=change;else input.onchange=change;line.append(input);row.append(line);view.widgets[name]={input};
      }
    }
  }
  window.HeartSurface={render(s){state=s;FXR.keys=Object.fromEntries((s.fx||[]).filter(e=>e.cfg.key).map(e=>[e.cfg.key,e.key]));if(!initialized){cfg=safeConfig(s.surface?.workspace);initialized=true;layout();}paintActions();paintRack();paintParameters('a');paintParameters('b');for(const [i,d] of Object.entries(fad))d.classList.toggle('selected',+i===focusLayer);$('target-name').textContent='♥ Heart';},focus(){if(state)this.render(state);}};
  document.addEventListener('pointerlockchange',()=>{if(state)HeartSurface.render(state);});
  layout();reportMonitor();if(!ws)connect();
})();
