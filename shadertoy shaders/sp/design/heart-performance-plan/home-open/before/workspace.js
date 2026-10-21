/* The performance workspace only changes presentation and targeting. */
(() => {
  const $=id=>document.getElementById(id);
  const modules={mix:'Layer faders',monitor:'Heart Monitor',rack:'Effects rack',actions:'Play',parameters:'Parameters A + B',clips:'Clip library'};
  const defaults=()=>({version:2,columns:[25,44,31],row:40,order:['mix','monitor','rack','actions','parameters','clips'],a:{kind:'follow'},b:{kind:'follow-effect'},rack:'follow',selectedEffect:null});
  let cfg=defaults(),initialized=false,arranging=false,detached=false,state=null,selectedEffect=null,layoutFrame=0;
  const panes={},views={};
  function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
  function button(text,fn,cls,title){const b=node('button',cls,text);b.type='button';b.onclick=fn;if(title)b.title=title;return b;}
  function option(s,value,text){const o=node('option','',text);o.value=value;s.append(o);}
  function save(){cmd({cmd:'surface_cfg',value:{workspace:cfg}});}
  function safeConfig(value){
    const out=defaults();if(!value||![1,2].includes(value.version))return out;
    if(Array.isArray(value.columns)&&value.columns.length===3&&value.columns.every(x=>Number.isFinite(x)&&x>=15&&x<=65))out.columns=[...value.columns];
    if(Number.isFinite(value.row))out.row=Math.max(25,Math.min(70,value.row));
    // The old A and B cells become one parameter module and a separate library.
    const order=Array.isArray(value.order)?value.order.map(x=>value.version===1?(x==='a'?'parameters':x==='b'?'clips':x):x):null;
    if(Array.isArray(order)&&order.length===6&&new Set(order).size===6&&order.every(x=>modules[x]))out.order=order;
    for(const k of ['a','b'])if(['follow','follow-effect','source','effect'].includes(value[k]?.kind))out[k]={...value[k]};
    if(typeof value.rack==='string')out.rack=value.rack;
    if(typeof value.selectedEffect==='string')out.selectedEffect=value.selectedEffect;
    return out;
  }
  function layerRole(c){return state?.layers.find(l=>l.i===c.layer)?.name;}
  function sourceRef(c){return {kind:'source',role:layerRole(c),name:c.name,col:c.col,instrument:c.instrument?.id||null};}
  function resolve(ref){
    if(!state)return null;
    if(ref.kind==='follow')return state.clips.find(c=>c.layer===focusLayer)||null;
    if(ref.kind==='follow-effect')ref={kind:'effect',key:selectedEffect};
    if(ref.kind==='source'){
      const found=state.clips.filter(c=>layerRole(c)===ref.role&&c.name===ref.name&&(!ref.col||c.col===ref.col)&&(!ref.instrument||c.instrument?.id===ref.instrument));
      return found.length===1?found[0]:null;
    }
    const found=(state.fx||[]).filter(e=>e.key===ref.key);return found.length===1?found[0]:null;
  }
  const isEffect=c=>typeof c?.key==='string';
  function label(c){return !c?'Unavailable':isEffect(c)?`${c.lname||'Composition'} / ${c.name}`:`${layerRole(c)} / ${c.instrument?.label||c.name}`;}
  function target(c){return isEffect(c)?{effect:c.key,instance:c.instance}:{layer:c.layer,col:c.col,instance:c.instance};}
  function current(c){const matches=isEffect(c)?(state?.fx||[]).filter(e=>e.key===c.key):(state?.clips||[]).filter(x=>x.layer===c.layer&&x.col===c.col);return matches.length===1&&matches[0].instance===c.instance?matches[0]:null;}
  function send(c,o){if(c&&state?.arena_connected&&current(c))cmd({...o,...target(c)});}
  function effectSend(e,o){if(e&&state?.arena_connected&&current(e))cmd({...o,key:e.key,instance:e.instance});}
  const motion=c=>isEffect(c)?c?.motion:c;
  function followLayer(i){if(document.pointerLockElement)return;focusLayer=i;HeartSurface.focus();}
  function bankLabel(l){return l?.bank==='forms'?'Forms':'All sources';}
  function bankClips(l){return (l?.bank==='forms'?l.forms:l?.clips)||[];}

  document.body.classList.add('workspace');
  const arrange=button('Arrange',()=>{if(document.pointerLockElement)return;arranging=!arranging;document.body.classList.toggle('arranging',arranging);arrange.setAttribute('aria-pressed',String(arranging));arrange.textContent=arranging?'Lock layout':'Arrange';layout();},'', 'Resize or exchange modules. Lock the arrangement before playing.');arrange.id='arrange';arrange.setAttribute('aria-pressed','false');document.querySelector('h1').append(arrange);
  const dockBack=button('Dock monitor',()=>window.webkit?.messageHandlers?.heartPointer?.postMessage('dock-monitor'));dockBack.hidden=true;document.querySelector('h1').append(dockBack);
  const reset=button('Reset layout',()=>{const old=cfg;cfg={...defaults(),a:old.a,b:old.b,selectedEffect:old.selectedEffect};layout();save();});reset.id='reset-layout';arrange.after(reset);
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
  // Play always shows the same eight layer launchers. Bank editing lives in the library.
  const act=panes.actions.body,transport=node('div','transport'),tempoRow=node('div','tempo-row');
  const bpm=node('input','tempo-input');bpm.type='number';bpm.min=20;bpm.max=500;bpm.step=.1;bpm.setAttribute('aria-label','BPM');
  bpm.onchange=()=>{const value=Number(bpm.value);if(Number.isFinite(value)&&value>=20&&value<=500)cmd({cmd:'tempo',value});};
  const bpmLabel=node('label','','BPM');bpmLabel.append(bpm);
  const tap=button('Tap BPM',()=>cmd({cmd:'tap_tempo'})),downbeat=button('Downbeat',()=>cmd({cmd:'downbeat'}),'','Set beat one and the phrase origin');
  const beatState=node('div','beat-state');beatState.setAttribute('aria-label','Beat, bar and phrase');
  tempoRow.append(tap,bpmLabel,downbeat);transport.append(tempoRow,beatState);act.append(transport);
  const playLayers=node('div','play-layers');act.append(playLayers);
  const selectedTools=node('div','selected-tools'),actName=node('div','target-line'),sourceActions=node('div','action-row');selectedTools.append(actName,sourceActions);act.append(selectedTools);
  const hold=button('Hold',()=>cmd({cmd:'hold',on:!state?.hold}),'','Hold all Heart motion');sourceActions.append(hold);
  for(const [action,text,cls] of [['undo','Undo',''],['home','Home','home'],['fire','Shuffle','shuffle']])sourceActions.append(button(text,()=>{const c=resolve({kind:'follow'});if(c)send(c,{cmd:action});},cls));
  const playDetails=node('details','play-details'),detailsToggle=node('summary','','⋯'),detailsContent=node('div','play-details-content');detailsToggle.setAttribute('aria-label','Selected source details and Beatpad');playDetails.append(detailsToggle,detailsContent);selectedTools.append(playDetails);
  const detailsName=node('div','target-line'),actNote=node('div','pane-note');detailsContent.append(detailsName,actNote);
  const beatpad=node('div','beatpad-placeholder','Beatpad · later');beatpad.setAttribute('aria-disabled','true');detailsContent.append(beatpad);

  const library=panes.clips.body,libraryTools=node('div','library-tools'),libraryLayer=node('select'),bankSelect=node('select');
  libraryLayer.setAttribute('aria-label','Clip library layer');libraryLayer.onchange=()=>followLayer(+libraryLayer.value);
  bankSelect.setAttribute('aria-label','Clip bank');option(bankSelect,'forms','Forms');option(bankSelect,'all','All sources');
  bankSelect.onchange=()=>{const l=state.layers.find(l=>l.i===focusLayer);if(l)cmd({cmd:'surface_cfg',value:{banks:{...state.surface?.banks,[l.name]:bankSelect.value}}});};
  libraryTools.append(libraryLayer,bankSelect);library.append(libraryTools);
  const search=node('input','source-search');search.type='search';search.placeholder='Find a clip…';search.setAttribute('aria-label','Find a clip in this bank');search.oninput=()=>paintLibrary();library.append(search);
  const libraryNote=node('div','pane-note'),sources=node('div','source-list');library.append(libraryNote,sources);
  library.append(button('Clear selected layer',()=>cmd({cmd:'clear',layer:focusLayer}),'clear-layer'));
  function paintActions(){
    if(document.activeElement!==bpm)bpm.value=Number.isFinite(state.bpm)?Math.round(state.bpm*10)/10:'';
    tap.disabled=downbeat.disabled=bpm.disabled=!state.arena_connected;
    const t=state.transport;
    beatState.textContent=t?`Beat ${t.beat} · Bar ${t.bar} / ${t.phrase_bars} · Phrase ${Math.floor((t.beats||0)/(4*(t.phrase_bars||1)))+1}`:'Beat / bar / phrase waiting';
    beatState.style.setProperty('--beat-phase',Math.max(0,Math.min(1,t?.phase||0)));
    tap.title=t?.taps?`${t.taps} taps in this tempo estimate`:'Tap to set the tempo';
    const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));
    if(playLayers.dataset.sig!==sig){playLayers.dataset.sig=sig;playLayers.replaceChildren();for(const l of state.layers){
      const row=node('div','play-layer');row.dataset.layer=l.i;
      const choose=button('',()=>followLayer(l.i),'play-layer-name');choose.append(node('strong','',`${l.i} · ${l.name}`),node('span','play-clip'));
      const nav=node('div','play-nav');for(const [dir,text,title] of [['prev','‹','Previous'],['rand','↝','Random'],['next','›','Next']])nav.append(button(text,()=>cmd({cmd:'clip_nav',layer:l.i,dir}),'',`${title} clip in ${l.name}’s current bank`));
      row.append(choose,nav,node('span','play-bank'));playLayers.append(row);
    }}
    for(const l of state.layers){const row=[...playLayers.children].find(x=>+x.dataset.layer===l.i);row.classList.toggle('selected',l.i===focusLayer);row.querySelector('.play-clip').textContent=l.clip||'empty';row.querySelector('.play-layer-name').title=`${l.i} · ${l.name} / ${l.clip||'empty'}`;row.querySelector('.play-bank').textContent=bankLabel(l);row.querySelectorAll('.play-nav button').forEach(b=>b.disabled=!state.arena_connected||!bankClips(l).length);}
    const l=state.layers.find(l=>l.i===focusLayer),c=resolve({kind:'follow'});actName.textContent=l?.name||'Source';actName.title=detailsName.textContent=`Selected source · ${l?.name||'Layer '+focusLayer} / ${l?.clip||'empty'}`;sourceActions.setAttribute('aria-label',actName.title);
    sourceActions.querySelectorAll('button').forEach(b=>{b.disabled=!state.arena_connected||(b!==hold&&!c);if(b!==hold)b.title=`${b.textContent} selected source · ${l?.name||'Layer '+focusLayer}`;});hold.setAttribute('aria-pressed',String(!!state.hold));hold.textContent=state.hold?'Resume':'Hold';
    actNote.textContent=c?`${c.slots.filter(x=>x.drive).length} active drives · ${c.home_kind||'Home'}`:'Select an adapted source to use Home and Shuffle.';
  }
  function paintLibrary(){
    const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));if(libraryLayer.dataset.sig!==sig){libraryLayer.dataset.sig=sig;libraryLayer.replaceChildren();for(const l of state.layers)option(libraryLayer,l.i,`${l.i} · ${l.name}`);}
    if(document.activeElement!==libraryLayer)libraryLayer.value=focusLayer;
    const l=state.layers.find(l=>l.i===focusLayer);bankSelect.disabled=!l?.forms?.length||!state.arena_connected;if(document.activeElement!==bankSelect)bankSelect.value=l?.bank||'all';
    const list=bankClips(l),q=search.value.trim().toLowerCase(),filtered=list.filter(x=>x.name.toLowerCase().includes(q));libraryNote.textContent=`${bankLabel(l)} · ${filtered.length} of ${list.length} clips · Play arrows use this bank`;
    const listSig=JSON.stringify([focusLayer,l?.ccol,filtered,state.arena_connected]);if(sources.dataset.sig!==listSig){sources.dataset.sig=listSig;sources.replaceChildren();for(const x of filtered){const b=button(x.name,()=>cmd({cmd:'launch',layer:l.i,col:x.col}));b.classList.toggle('active',x.col===l.ccol);b.disabled=!state.arena_connected;sources.append(b);}if(!filtered.length)sources.append(node('p','pane-note',q?'No matching clips.':'This bank is empty.'));}
    library.querySelector('.clear-layer').disabled=!state.arena_connected||!l?.ccol;
  }
  // Rack selection changes the follow target; an explicitly pinned A or B stays pinned.
  const scope=node('select');scope.setAttribute('aria-label','Effect rack scope');panes.rack.body.append(scope);const rackList=node('div','fx-list');panes.rack.body.append(rackList);
  scope.onchange=()=>{cfg.rack=scope.value;save();paintRack();};
  function rackOptions(){const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));if(scope.dataset.sig===sig)return;scope.dataset.sig=sig;scope.replaceChildren();option(scope,'follow','Selected layer');option(scope,'all','All effects');option(scope,'composition','Composition');for(const l of state.layers)option(scope,'layer:'+l.name,l.i+' · '+l.name);scope.value=cfg.rack;}
  function openEffect(e){if(!current(e)||document.pointerLockElement)return;selectedEffect=e.key;cfg.selectedEffect=e.key;save();paintParameters('a');paintParameters('b');paintRack();}
  function envelope(e,anchor){
    const live=current(e);if(!live)return;fxPop(live,anchor);const pop=document.querySelector('.pop');if(!pop)return;
    const pulse=node('fieldset','pulse-settings');pulse.append(node('legend','','Pulse envelope · seconds'));
    for(const [key,text,fallback,min] of [['pulse_attack','In',.04,.01],['pulse_hold','Hold',.08,.016],['pulse_return','Return',.25,.01]]){
      const line=node('label','',text),input=node('input');input.type='number';input.min=min;input.max=10;input.step=.01;input.value=live.cfg[key]??fallback;input.setAttribute('aria-label','Pulse '+text.toLowerCase()+' seconds');
      input.onchange=()=>{const value=Number(input.value);if(Number.isFinite(value)&&value>=min&&value<=10)effectSend(live,{cmd:'fx_cfg',cfg:{[key]:value}});};line.append(input);pulse.append(line);
    }
    pulse.append(button('Pulse',()=>effectSend(live,{cmd:'fx_pulse'}),'fx-pulse'));pop.lastElementChild.before(pulse);
  }
  function paintRack(){
    rackOptions();const list=(state.fx||[]).filter(e=>cfg.rack==='all'||cfg.rack==='composition'?cfg.rack==='all'||e.scope==='C':cfg.rack==='follow'?e.layer===focusLayer:e.lname===cfg.rack.slice(6));
    const sig=JSON.stringify(list.map(e=>[e.key,e.instance,e.name]));if(rackList.dataset.sig!==sig){rackList.dataset.sig=sig;rackList.replaceChildren();for(const e of list){
      const row=node('div','fx-row');row.dataset.key=e.key;const toggle=button('',null,'fx-switch');let pressed=false;
      toggle.onpointerdown=ev=>{if(!current(e))return;ev.preventDefault();toggle.setPointerCapture(ev.pointerId);pressed=true;effectSend(e,{cmd:'fx_press'});};
      const release=()=>{if(!pressed)return;pressed=false;cmd({cmd:'fx_release',key:e.key,instance:e.instance});};toggle.onpointerup=release;toggle.onpointercancel=release;toggle.onlostpointercapture=release;
      const open=button('',()=>openEffect(e),'fx-open');open.append(node('span','fx-name',e.name),node('span','fx-info'));
      const pulse=button('Pulse',()=>effectSend(e,{cmd:'fx_pulse'}),'fx-pulse','Pulse the envelope and return to its previous level');
      const settings=button('⚙',()=>envelope(e,row),'fx-envelope','Envelope and trigger settings');row.append(toggle,open,pulse,settings);rackList.append(row);
    }}
    for(const e of list){const row=[...rackList.children].find(x=>x.dataset.key===e.key);if(!row)continue;row.classList.toggle('chosen',selectedEffect===e.key);row.classList.toggle('pinned',cfg.a.key===e.key||cfg.b.key===e.key);row.classList.toggle('pulsing',!!e.pulsing);const t=row.querySelector('.fx-switch');t.disabled=row.querySelector('.fx-pulse').disabled=e.has_amount===false||!state.arena_connected;t.textContent=e.env>.001?'On':'Off';t.setAttribute('aria-pressed',String(e.env>.001));row.querySelector('.fx-info').textContent=`${e.scope==='C'?'Composition':e.lname} · ${e.pulsing?'pulse '+(e.pulse_stage||'active'):e.pending?'waiting for beat':Math.abs(e.target-e.env)>.015?'fading':e.bypassed?'bypassed':Math.round(e.env*100)+'%'} · ${e.cfg.mode}${e.cfg.key?' · key '+e.cfg.key:''}`;}
  }
  // Target and motion controls stay above the two independently scrolling grids.
  const parameterTop=node('div','parameter-top'),parameterColumns=node('div','parameter-columns');panes.parameters.body.append(parameterTop,parameterColumns);
  for(const id of ['a','b']){
    const header=node('section','parameter-header'),tools=node('div','target-tools'),pick=node('select');header.dataset.side=id;tools.append(node('strong','parameter-letter',id.toUpperCase()));pick.setAttribute('aria-label','Target for Parameters '+id.toUpperCase());tools.append(pick);header.append(tools);
    const pin=button('Pin',()=>{const ref=cfg[id],c=resolve(ref);if(ref.kind==='source')cfg[id]={kind:'follow'};else if(ref.kind==='effect')cfg[id]={kind:'follow-effect'};else if(c)cfg[id]=isEffect(c)?{kind:'effect',key:c.key}:sourceRef(c);else return;save();paintParameters(id);paintRack();},'','Follow the selection, or keep this exact target in place');tools.append(pin);
    const name=node('div','target-line'),controls=node('div','parameter-controls'),summary=node('div','drive-state');header.append(name,controls,summary);parameterTop.append(header);
    const content=node('section','parameter-scroll');content.dataset.side=id;content.setAttribute('aria-label','Parameters '+id.toUpperCase());parameterColumns.append(content);
    views[id]={pick,pin,name,controls,summary,content,sig:'',widgets:{},c:null};
    pick.onchange=()=>{if(document.pointerLockElement)return;cfg[id]=JSON.parse(pick.value);save();paintParameters(id);paintRack();};
  }
  function targetOptions(id){const v=views[id],sig=JSON.stringify([state.clips.map(c=>sourceRef(c)),(state.fx||[]).map(e=>[e.key,e.name,e.lname]),cfg[id]]);if(v.pick.dataset.sig===sig)return;v.pick.dataset.sig=sig;v.pick.replaceChildren();option(v.pick,JSON.stringify({kind:'follow'}),'Follow selected source');option(v.pick,JSON.stringify({kind:'follow-effect'}),'Follow selected effect');for(const c of state.clips)option(v.pick,JSON.stringify(sourceRef(c)),'Source · '+label(c));for(const e of state.fx||[])option(v.pick,JSON.stringify({kind:'effect',key:e.key}),'Effect · '+label(e)+' · '+e.key.split('~').at(-1));const key=JSON.stringify(cfg[id]);if(![...v.pick.options].some(o=>o.value===key))option(v.pick,key,'Pinned target unavailable');v.pick.value=key;}
  function disposeView(view){for(const w of Object.values(view.widgets))w.chip?.dispose();view.widgets={};view.content.replaceChildren();view.controls.replaceChildren();view.speed=view.pattern=view.amount=view.morph=view.moreToggle=null;view.timing=[];}
  function paintParameters(id){
    const view=views[id],locked=!!document.pointerLockElement;view.pick.disabled=view.pin.disabled=locked;
    if(locked&&view.content.contains(document.pointerLockElement)){if(resolve(cfg[id])?.instance!==view.c?.instance)view.summary.textContent='Target changed · release the pointer to reconnect this pane';return;}
    targetOptions(id);const c=resolve(cfg[id]);view.c=c;const follows=cfg[id].kind.startsWith('follow');view.pin.textContent=follows?'Pin':cfg[id].kind==='effect'?'Follow effect':'Follow source';view.pin.disabled=locked||(follows&&!c);view.pin.setAttribute('aria-pressed',String(!follows));view.pin.title=follows?'Keep this exact target in place':`Pinned target · click to follow the selected ${cfg[id].kind==='effect'?'effect':'source'}`;
    view.name.textContent=c?`${follows?'':'Pinned · '}${label(c)}`:follows?(cfg[id].kind==='follow-effect'?'Select an effect in the rack':'No adapted source selected'):'Pinned target unavailable';
    const m=motion(c),sig=JSON.stringify([cfg[id],c?.instance,c?.col,(m?.slots||[]).map(s=>[s.name,s.choices,s.min,s.max,s.integer]),isEffect(c)?Object.entries(c.params||{}).map(([n,p])=>[n,p.id,p.valuetype,p.options,p.min,p.max]):null]);
    if(view.sig!==sig){view.sig=sig;disposeView(view);if(!c){view.summary.textContent='';view.content.append(node('p','pane-placeholder',follows?(cfg[id].kind==='follow-effect'?'Choose an effect name in the rack to inspect its motion.':'Choose a layer with an adapted Heart source to inspect its motion.'):'This exact target is not present. Choose another target above; these controls have not been redirected.'));return;}buildParameters(view,c);}
    if(!c)return;
    for(const input of view.controls.querySelectorAll('button,select,input'))input.disabled=!state.arena_connected;
    if(m){const slots=m.slots||[],moving=slots.filter(x=>x.morphing),remaining=Math.max(0,...moving.map(x=>x.morph_remaining||0));view.summary.textContent=!slots.length?'No motion parameters on this target':`${state.hold?'Motion held · ':''}${slots.filter(x=>x.drive).length}/${slots.length} drives · ${m.home_kind||'Home'}${moving.length?' · morphing '+remaining.toFixed(1)+'s':''}`;
      if(view.speed&&document.activeElement!==view.speed)view.speed.value=m.g?.speed??1;
      if(view.pattern&&document.activeElement!==view.pattern)view.pattern.value=m.pattern||(state.families||FAMILIES)[m.g?.pattern??0];
      if(view.moreToggle){const family=m.pattern||(state.families||FAMILIES)[m.g?.pattern??0];view.moreToggle.textContent='More · '+family;view.moreToggle.title='Relationship: '+family+' · all relationships, morph and Home settings';}
      if(view.morph&&document.activeElement!==view.morph)view.morph.value=m.morph??0;
      for(const b of view.timing)b.setAttribute('aria-pressed',String(m.g?.timing_mode===b.dataset.mode));
      for(const sl of slots){const w=view.widgets[sl.name];if(!w)continue;w.sl=sl;if(w.picker){if(document.activeElement!==w.picker)w.picker.value=sl.choices[Math.round(sl.v*(sl.choices.length-1))];continue;}if(!w.chip)continue;if(!w.chip.locked)w.chip.set(sl.v,true);if(w.chip.driven!==sl.drive)w.chip.setDriven(sl.drive,true);w.lock.classList.toggle('on',!!sl.lock);w.lock.setAttribute('aria-pressed',String(!!sl.lock));if(!w.chip.menusOpen())w.chip.syncConfig({ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,min:sl.lo,max:sl.hi});}
    }else view.summary.textContent='Effect motion unavailable · manual controls';
    view.summary.title=view.summary.textContent;
    if(isEffect(c)){for(const [name,w] of Object.entries(view.widgets)){const p=c.params[name];if(!p||w.sl)continue;if(w.chip){if(!w.chip.locked)w.chip.set((p.value-(p.min??0))/((p.max??1)-(p.min??0)||1),true);}else if(w.input&&document.activeElement!==w.input){if(w.input.type==='checkbox')w.input.checked=!!p.value;else if(w.input.type!=='button')w.input.value=w.input.type==='color'?String(p.value).slice(0,7):p.value;}}
      if(view.amount&&document.activeElement!==view.amount)view.amount.value=c.target;
    }
  }
  function buildMotionTools(view,c,m){
    const toolbar=node('div','param-actions');view.controls.append(toolbar);toolbar.append(button('Home',()=>send(c,{cmd:'home'}),'home'),button('Shuffle',()=>send(c,{cmd:'fire'}),'shuffle'),button('Undo',()=>send(c,{cmd:'undo'})));
    view.speed=node('select');view.speed.setAttribute('aria-label',label(c)+' speed');for(const x of [.0625,.125,.25,.5,1,2,4,8,16])option(view.speed,x,x+'×');view.speed.onchange=()=>send(c,{cmd:'speed',value:+view.speed.value});toolbar.append(view.speed);
    const timing=node('div','param-actions timing-actions');view.controls.append(timing);for(const [mode,text] of [['unison','Stable'],['harmonic','Musical'],['irrational','Irrational']]){const b=button(text,()=>send(c,{cmd:'timing',mode}),'',mode+' timing');b.dataset.mode=mode;view.timing.push(b);timing.append(b);}
    const more=node('details','motion-more'),extra=node('div','motion-more-content');view.moreToggle=node('summary','','More');view.moreToggle.setAttribute('aria-label',label(c)+' more motion settings');more.append(view.moreToggle,extra);timing.append(more);
    view.pattern=node('select','relationship-choice');view.pattern.setAttribute('aria-label',label(c)+' relationship');for(const family of state.families||FAMILIES)option(view.pattern,family,family);view.pattern.onchange=()=>send(c,{cmd:'global_cfg',key:'Pattern',value:view.pattern.value});const familyLabel=node('label','motion-family-label','Relationship');familyLabel.append(view.pattern);extra.append(familyLabel);
    const morphLabel=node('label','morph-control','Morph s');view.morph=node('input');view.morph.type='number';view.morph.min=0;view.morph.max=60;view.morph.step=.25;view.morph.setAttribute('aria-label',label(c)+' morph seconds');view.morph.onchange=()=>send(c,{cmd:'morph',seconds:+view.morph.value});morphLabel.append(view.morph);extra.append(morphLabel);
    extra.append(button('Set Home',()=>send(c,{cmd:'home_set'}),'set-motion-home','Save current drives, relationships and ranges as this target’s Home'));
    if(c.feedback_behaviors?.length){const fb=node('div','param-actions');for(const name of c.feedback_behaviors)fb.append(button(name,()=>send(c,{cmd:'feedback_behavior',name})));fb.append(button('Reset trails',()=>send(c,{cmd:'feedback_reset'})));extra.append(fb);}
  }
  function buildMotionSlot(view,c,sl,grid){
    const row=node('div','slot2');grid.append(row);if(sl.choices?.length){row.append(node('label','',sl.name));const picker=node('select');picker.setAttribute('aria-label',sl.name);for(const s of sl.choices)option(picker,s,s);picker.onchange=()=>send(c,{cmd:'choice',slot:sl.name,option:picker.value});row.append(picker);view.widgets[sl.name]={picker,sl};return;}
    const mini=node('div','ax'),w={sl};const good=button('★',()=>send(c,{cmd:'good_go',slot:sl.name}),'axb','Return to this axis’s good value');const lock=button('Lock',()=>send(c,{cmd:'slot_cfg',slot:sl.name,key:'Lock',value:!w.sl.lock}),'axb','Exclude this axis from shuffles');const fire=button('⚡',()=>send(c,{cmd:'fire_slot',slot:sl.name}),'axb','Shuffle this axis');mini.append(good,lock,fire);row.append(mini);
    const native=isEffect(c),lo=sl.min??0,span=(sl.max??1)-lo||1,integer=!!sl.integer;
    const chip=createSmartParam({label:sl.name,value:sl.v,driven:sl.drive,wrap:!!sl.cyc,min:sl.lo,max:sl.hi,ratioLabels:RATIOS,ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,
      ...(native?{step:integer?1/span:.01,format:v=>kitFormat(integer?Math.round(lo+v*span):lo+v*span),parse:v=>(v-lo)/span}:{}),
      onInput:value=>send(c,{cmd:'manual',slot:sl.name,value}),onDrive:on=>send(c,{cmd:'drive',slot:sl.name,on}),onReset:()=>send(c,{cmd:'good_go',slot:sl.name}),onHomeSet:()=>send(c,{cmd:'good_set',slot:sl.name}),
      onConfig:cf=>{const entries=[['Ratio',RATIOS[cf.ratio],w.sl.ratio],['Mult',cf.multiplier,w.sl.mult],['Offset',cf.offset,w.sl.offset??0],['Lo',cf.min,w.sl.lo],['Hi',cf.max,w.sl.hi]];for(const [key,value,old] of entries)if(value!==old)send(c,{cmd:'slot_cfg',slot:sl.name,key,value});}});
    row.append(chip.el);if(native)row.append(node('div','native-value',integer?'whole steps':c.params[sl.name]?.view?.suffix?.trim()||'native units'));Object.assign(w,{chip,lock});view.widgets[sl.name]=w;
  }
  function buildParameters(view,c){
    const m=motion(c);if(m?.slots?.length)buildMotionTools(view,c,m);
    if(isEffect(c)){const actions=node('div','param-actions effect-envelope');actions.append(button('Envelope',()=>envelope(c,view.name)));view.controls.append(actions);
      if(c.has_amount!==false){actions.append(button('Pulse',()=>effectSend(c,{cmd:'fx_pulse'}),'fx-pulse'));const line=node('label','effect-level','Opacity');const amount=node('input');amount.type='range';amount.min=0;amount.max=1;amount.step=.001;amount.setAttribute('aria-label',label(c)+' envelope opacity');amount.oninput=()=>effectSend(c,{cmd:'fx_amount',value:+amount.value});line.append(amount);actions.append(line);view.amount=amount;}
    }
    const grid=node('div','parameter-grid');view.content.append(grid);
    for(const sl of m?.slots||[])if(!(isEffect(c)&&sl.name==='Opacity'&&c.has_amount!==false))buildMotionSlot(view,c,sl,grid);
    if(!isEffect(c))return;
    for(const [name,p] of Object.entries(c.params||{})){if(view.widgets[name]||(name==='Opacity'&&c.has_amount!==false))continue;const row=node('div','slot2');grid.append(row);
      if(['ParamRange','ParamFloat','ParamInt','ParamNumber'].includes(p.valuetype)){
        const lo=p.min??0,span=(p.max??1)-lo||1,integer=['ParamInt','ParamNumber'].includes(p.valuetype)||p.view?.display_units==='integer';
        const chip=createSmartParam({label:name,value:(p.value-lo)/span,min:0,max:1,step:integer?1/span:.01,format:v=>kitFormat(integer?Math.round(lo+v*span):lo+v*span),parse:v=>(v-lo)/span,onInput:v=>effectSend(c,{cmd:'fx_param',name,value:integer?Math.round(lo+v*span):lo+v*span})});
        const old=chip.el.querySelector('.sp-name'),title=node('div','sp-name',name);old.replaceWith(title);row.append(chip.el,node('div','native-value',integer?'whole steps':p.view?.suffix?.trim()||'native units'));view.widgets[name]={chip};
      }else{
        row.append(node('label','',name));const line=node('div','effect-manual');let input;
        if(p.valuetype==='ParamChoice'){input=node('select');for(const x of p.options||[])option(input,x,x);}
        else{input=node('input');input.type=['ParamBool','ParamBoolean'].includes(p.valuetype)?'checkbox':p.valuetype==='ParamColor'?'color':'button';if(input.type==='button')input.value='Trigger';}
        input.setAttribute('aria-label',name);const change=()=>effectSend(c,{cmd:'fx_param',name,value:input.type==='checkbox'?input.checked:input.type==='button'?true:input.value});if(input.type==='button')input.onclick=change;else input.onchange=change;line.append(input);row.append(line);view.widgets[name]={input};
      }
    }
  }
  window.HeartSurface={render(s){state=s;FXR.keys=Object.fromEntries((s.fx||[]).filter(e=>e.cfg.key).map(e=>[e.cfg.key,e.key]));if(!initialized){cfg=safeConfig(s.surface?.workspace);selectedEffect=cfg.selectedEffect||(cfg.b.kind==='effect'?cfg.b.key:null)||s.fx?.[0]?.key||null;initialized=true;layout();}paintActions();paintLibrary();paintRack();paintParameters('a');paintParameters('b');for(const [i,d] of Object.entries(fad))d.classList.toggle('selected',+i===focusLayer);$('target-name').textContent='♥ Heart';},focus(){if(state)this.render(state);}};
  document.addEventListener('pointerlockchange',()=>{if(state)HeartSurface.render(state);});
  window.addEventListener('pagehide',()=>{for(const view of Object.values(views)){disposeView(view);view.sig='';}});
  layout();reportMonitor();if(!ws)connect();
})();
