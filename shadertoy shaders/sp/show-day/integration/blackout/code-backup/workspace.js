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
    if(typeof value.rack==='string')out.rack=value.rack==='transform'?'follow':value.rack;
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
  const isTransform=e=>e?.target_kind==='transform';
  const isFigureTransform=e=>e?.scope==='L'&&e.has_amount===true&&/^layer\/figure~1\/effect\/Transform~1$/i.test(e.key||'');
  function figureTransform(){const found=(state?.fx||[]).filter(isFigureTransform);return found.length===1?found[0]:null;}
  function transformScope(e){const parts=(e.key||'').split('/'),clip=parts.indexOf('clip');return e.scope==='K'?`Clip · ${e.lname} / ${decodeURIComponent(parts[clip+1]||'').replace(/~\d+$/,'')}`:e.scope==='L'?`Layer · ${e.lname}`:e.scope==='G'?`Group · ${decodeURIComponent(parts[1]||'').replace(/~\d+$/,'')}`:'Composition';}
  function label(c){return !c?'Unavailable':isTransform(c)?`${transformScope(c)} / Transform`:isEffect(c)?`${c.lname||'Composition'} / ${c.name}`:`${layerRole(c)} / ${c.instrument?.label||c.name}`;}
  function target(c){return isEffect(c)?{effect:c.key,instance:c.instance}:{layer:c.layer,col:c.col,instance:c.instance};}
  function current(c){const matches=isEffect(c)?(state?.fx||[]).filter(e=>e.key===c.key):(state?.clips||[]).filter(x=>x.layer===c.layer&&x.col===c.col);return matches.length===1&&matches[0].instance===c.instance?matches[0]:null;}
  function send(c,o){if(c&&state?.arena_connected&&current(c))cmd({...o,...target(c)});}
  function effectSend(e,o){if(e&&state?.arena_connected&&current(e))cmd({...o,key:e.key,instance:e.instance});}
  const motion=c=>isEffect(c)?c?.motion:c;
  function followLayer(i){if(document.pointerLockElement)return;focusLayer=i;HeartSurface.focus();}
  function bankLabel(l){return {heart:'Heart copies',explore:'Explore figures',forms:'Forms'}[l?.bank]||'All sources';}
  function bankClips(l){return (l?.bank==='heart'?l.heart_copies:l?.bank==='explore'?l.explore:l?.bank==='forms'?l.forms:l?.clips)||[];}
  function clipLabel(x){return (x.heart_copy?x.source:x.name)||x.source||'Untitled';}

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
  const playTabs=node('div','play-tabs'),padPanel=node('div','trackpad-panel');
  let playTab='clips';const tabButtons={};
  for(const [id,label] of [['clips','Clips'],['trackpad','Trackpad']]){const b=button(label,()=>{playTab=id;paintPad();});b.setAttribute('role','tab');tabButtons[id]=b;playTabs.append(b);}
  playTabs.setAttribute('role','tablist');act.append(playTabs);
  const playLayers=node('div','play-layers');act.append(playLayers,padPanel);
  padPanel.append(node('div','pane-note','Four faders · drag a region onto a layer fader, or choose its target below.'));
  const padDiagram=node('div','trackpad-diagram'),padRegions=[];padPanel.append(padDiagram);
  const padAPI=()=>typeof PAD==='undefined'?null:PAD;
  for(let lane=1;lane<=4;lane++){
    const region=node('div','trackpad-region'),label=node('strong','',String(lane)),target=node('select'),behavior=node('select');
    region.draggable=true;region.ondragstart=e=>{if(padAPI()?.isLocked()){e.preventDefault();return;}e.dataTransfer.setData('application/x-heart-lane',String(lane));e.dataTransfer.effectAllowed='link';};
    target.setAttribute('aria-label',`Trackpad region ${lane} layer`);behavior.setAttribute('aria-label',`Trackpad region ${lane} behavior`);
    for(const [v,t] of [['absolute','Absolute'],['relative','Relative'],['spring','Spring → 0']])option(behavior,v,t);
    target.onchange=()=>{const p=padAPI();if(!p)return;const old=state.layers.find(l=>p.laneOf(l.i)===lane);if(old)p.assign(old.i,0);if(+target.value)p.assign(+target.value,lane);paintPad();};
    behavior.onchange=()=>{if(+target.value)padAPI()?.configure(+target.value,behavior.value);};
    region.append(label,target,behavior);padDiagram.append(region);padRegions.push({lane,region,label,target,behavior});
  }
  const grabPad=button('Grab trackpad',()=>{if(window.heartPointer)return;const p=padAPI();if(p?.isLocked())p.release();else p?.grab();paintPad();},'grab-trackpad');
  grabPad.addEventListener('heartphysicalpress',e=>{if(e.detail.stage>=1&&!grabPad.disabled&&!padAPI()?.isLocked()){padAPI()?.grab();paintPad();}});
  const padStatus=node('div','pane-note');padStatus.setAttribute('role','status');padPanel.append(grabPad,padStatus);
  function paintPad(){
    playLayers.hidden=playTab!=='clips';padPanel.hidden=playTab!=='trackpad';
    for(const id of Object.keys(tabButtons))tabButtons[id].setAttribute('aria-selected',String(playTab===id));
    const p=padAPI(),locked=!!p?.isLocked(),sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));let assigned=0;
    for(const r of padRegions){
      if(r.target.dataset.sig!==sig){r.target.replaceChildren();option(r.target,0,'Unassigned');for(const l of state.layers)option(r.target,l.i,l.name);r.target.dataset.sig=sig;}
      const l=state.layers.find(l=>p?.laneOf(l.i)===r.lane),valid=l&&p.available(l.i);if(valid)assigned++;
      if(document.activeElement!==r.target)r.target.value=l?String(l.i):'0';
      r.label.textContent=String(r.lane)+(l&&!valid?' · unavailable':'');
      r.target.disabled=locked;r.behavior.disabled=locked||!valid;r.region.draggable=!locked;
      if(l&&document.activeElement!==r.behavior){const c=p.config(l.i);r.behavior.value=c.rel==='zero'?'spring':c.touch==='rel'?'relative':'absolute';}
    }
    grabPad.disabled=!p||(!locked&&(!state.arena_connected||!window.heartTouchLive||!assigned));grabPad.textContent=locked?'Release trackpad':'Grab trackpad';grabPad.setAttribute('aria-pressed',String(locked));
    padStatus.textContent=locked?'Playing · physical click or Escape releases':!window.heartTouchLive?'Trackpad probe unavailable':`${assigned}/4 assigned · Grab to play · physical click or Escape releases`;
    for(const l of state.layers){const f=typeof fad==='undefined'?null:fad[l.i];if(!f)continue;
      f.ondragover=e=>{if(e.dataTransfer.types.includes('application/x-heart-lane')){e.preventDefault();e.dataTransfer.dropEffect='link';}};
      f.ondrop=e=>{const lane=Number(e.dataTransfer.getData('application/x-heart-lane'));if(!Number.isInteger(lane)||lane<1||lane>4||p?.isLocked())return;e.preventDefault();p?.assign(l.i,lane);paintPad();};
    }
  }

  const selectedTools=node('div','selected-tools'),actName=node('div','target-line'),sourceActions=node('div','action-row');selectedTools.append(actName,sourceActions);act.append(selectedTools);
  let blackoutPending=false,blackoutError='';
  const blackout=button('Blackout',async()=>{
    const b=state?.blackout;if(blackoutPending||!state?.arena_connected||!b?.available)return;
    blackoutPending=true;blackoutError='';paintActions();
    try{
      const response=await fetch('/blackout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({on:!b.on,parameter_id:b.parameter_id})});
      const observed=await response.json();state.blackout=observed;
      if(!response.ok)throw Error(observed.error||'Output change not confirmed');
    }catch(e){blackoutError=e.message||'Output change not confirmed';}
    finally{blackoutPending=false;paintActions();}
  },'blackout-control','Immediate native output cut; motion and layer levels keep running');
  blackout.setAttribute('aria-label','Blackout');sourceActions.append(blackout);
  const blackoutStatus=node('span','blackout-status');blackoutStatus.setAttribute('role','status');selectedTools.append(blackoutStatus);
  const hold=button('Hold',()=>cmd({cmd:'hold',on:!state?.hold}),'','Hold all Heart motion');sourceActions.append(hold);
  for(const [action,text,cls] of [['settle','Settle all','home'],['open','Open all','open-motion'],['shuffle','Shuffle all','shuffle']])sourceActions.append(button(text,()=>cmd({cmd:'play_all',action,value:shuffleMode.value}),cls));
  const globalOptions=node('div','global-options'),shuffleMode=node('select'),motionSpeed=node('select');
  shuffleMode.setAttribute('aria-label','Global shuffle relationship');for(const [v,t] of [['harmonic','Musical'],['irrational','Irrational'],['unison','Stable']])option(shuffleMode,v,t);
  motionSpeed.setAttribute('aria-label','Global motion speed');for(const v of [.125,.25,.5,1,2,4])option(motionSpeed,v,v+'×');option(motionSpeed,'mixed','Mixed');motionSpeed.value='mixed';motionSpeed.onchange=()=>{if(motionSpeed.value!=='mixed')cmd({cmd:'play_all',action:'speed',value:Number(motionSpeed.value)});};
  globalOptions.append(node('span','','Shuffle'),shuffleMode,node('span','','Speed'),motionSpeed);selectedTools.append(globalOptions);
  const globalFeedback=node('div','global-feedback');globalFeedback.setAttribute('role','status');selectedTools.append(globalFeedback);
  const playDetails=node('details','play-details'),detailsToggle=node('summary','','⋯'),detailsContent=node('div','play-details-content');detailsToggle.setAttribute('aria-label','Global performance details and Beatpad');playDetails.append(detailsToggle,detailsContent);selectedTools.append(playDetails);
  const detailsName=node('div','target-line'),actNote=node('div','pane-note');detailsContent.append(detailsName,actNote);
  const beatpad=node('div','beatpad-placeholder','Beatpad · later');beatpad.setAttribute('aria-disabled','true');detailsContent.append(beatpad);

  const library=panes.clips.body,libraryTools=node('div','library-tools'),libraryLayer=node('select'),bankSelect=node('select');
  libraryLayer.setAttribute('aria-label','Clip library layer');libraryLayer.onchange=()=>followLayer(+libraryLayer.value);
  bankSelect.setAttribute('aria-label','Clip bank');
  bankSelect.onchange=()=>{const l=state.layers.find(l=>l.i===focusLayer);if(l)cmd({cmd:'surface_cfg',value:{banks:{...state.surface?.banks,[l.name]:bankSelect.value}}});};
  libraryTools.append(libraryLayer,bankSelect);library.append(libraryTools);
  const search=node('input','source-search');search.type='search';search.placeholder='Find a clip…';search.setAttribute('aria-label','Find a clip in this bank');search.oninput=()=>paintLibrary();library.append(search);
  const libraryNote=node('div','pane-note'),sources=node('div','source-list');library.append(libraryNote,sources);
  library.append(button('Clear selected layer',()=>cmd({cmd:'clear',layer:focusLayer}),'clear-layer'));
  function paintActions(){
    paintPad();
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
    actName.textContent='Whole composition';sourceActions.setAttribute('aria-label','Whole composition');
    const busy=!!state.play_action?.busy||!!state.patch_operation?.busy;
    sourceActions.querySelectorAll('button').forEach(b=>{b.disabled=!state.arena_connected||(b!==hold&&busy);});
    const output=state.blackout;blackout.disabled=!state.arena_connected||!output?.available||blackoutPending;
    blackout.textContent=output?.on===true?'Restore output':'Blackout';blackout.setAttribute('aria-label',blackout.textContent);
    blackout.setAttribute('aria-pressed',output?.available?String(output.on):'false');blackout.setAttribute('aria-busy',String(blackoutPending));
    blackoutStatus.textContent=blackoutError||output?.error||(blackoutPending?'Confirming native output…':!state.arena_connected?'Output disconnected':!output?.available?'Output state unavailable':output.on?'Output blacked out':'Output active');
    shuffleMode.disabled=motionSpeed.disabled=!state.arena_connected||busy;
    hold.setAttribute('aria-pressed',String(!!state.hold));hold.textContent=state.hold?'Resume':'Hold';
    const motions=[...(state.clips||[]),...(state.fx||[]).map(f=>f.motion).filter(Boolean)];
    const speeds=[...new Set(motions.filter(c=>(c.slots||[]).some(s=>s.drive)).map(c=>Number(c.g?.speed??1)))];
    if(document.activeElement!==motionSpeed)motionSpeed.value=speeds.length===1&&[.125,.25,.5,1,2,4].includes(speeds[0])?String(speeds[0]):'mixed';
    const slots=motions.flatMap(c=>c.slots||[]),moving=slots.filter(s=>s.morphing).length;
    globalFeedback.textContent=(state.hold?'Held · ':'')+slots.filter(s=>s.drive).length+' drives · '+(moving?moving+' changing · ':'')+(state.play_action?.label||'Ready');
    detailsName.textContent='Whole composition';actNote.textContent='Settle fades effects out and rests motion. Open starts drives and preserves effect on/off levels. Shuffle changes active, unlocked timing relationships. Hold freezes motion.';

  }
  function paintLibrary(){
    const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));if(libraryLayer.dataset.sig!==sig){libraryLayer.dataset.sig=sig;libraryLayer.replaceChildren();for(const l of state.layers)option(libraryLayer,l.i,`${l.i} · ${l.name}`);}
    if(document.activeElement!==libraryLayer)libraryLayer.value=focusLayer;
    const l=state.layers.find(l=>l.i===focusLayer);
    const banks=[['heart','Heart copies',l?.heart_copies],['explore','Explore figures',l?.explore],['forms','Forms',l?.forms],['all','All sources',l?.clips]].filter(([key,,clips])=>key==='all'||clips?.length||key===l?.bank);
    const bankSig=JSON.stringify(banks.map(([key,label])=>[key,label]));if(bankSelect.dataset.sig!==bankSig){bankSelect.dataset.sig=bankSig;bankSelect.replaceChildren();for(const [key,label] of banks)option(bankSelect,key,label);}
    bankSelect.disabled=!l||!state.arena_connected;if(document.activeElement!==bankSelect)bankSelect.value=l?.bank||'all';
    const list=bankClips(l),q=search.value.trim().toLowerCase(),filtered=list.filter(x=>[x.name,x.source,x.note].some(v=>String(v||'').toLowerCase().includes(q)));libraryNote.textContent=`${bankLabel(l)} · ${filtered.length} of ${list.length} clips · Play arrows use this bank${l?.bank==='explore'?' · Full-range containment unchecked':''}`;
    const listSig=JSON.stringify([focusLayer,l?.ccol,filtered,state.arena_connected]);if(sources.dataset.sig!==listSig){sources.dataset.sig=listSig;sources.replaceChildren();for(const x of filtered){const b=button((x.note?'⚠ ':'')+clipLabel(x),()=>cmd({cmd:'launch',layer:l.i,col:x.col}));b.title=`${x.col} · ${x.source||x.name}${x.note?' — '+x.note:''}`;b.classList.toggle('active',x.col===l.ccol);b.disabled=!state.arena_connected;sources.append(b);}if(!filtered.length)sources.append(node('p','pane-note',q?'No matching clips.':'This bank is empty.'));}
    library.querySelector('.clear-layer').disabled=!state.arena_connected||!l?.ccol;
  }
  // Rack selection changes the follow target; an explicitly pinned A or B stays pinned.
  const rackModes=node('div','rack-modes'),scope=node('select');scope.setAttribute('aria-label','Effect rack scope');
  const rackMode=(value)=>{cfg.rack=value;scope.value=value;save();paintRack();};
  const compositionMode=button('Composition',()=>rackMode('composition')),layerMode=button('Selected layer',()=>rackMode('follow'));
  const transformMode=button('Figure Transform',()=>{const e=figureTransform();if(!e||!state.arena_connected||document.pointerLockElement)return;cfg.b={kind:'effect',key:e.key};openEffect(e);},'figure-transform','Open the Figure layer’s position, size and rotation in Parameters B');
  rackModes.append(compositionMode,layerMode,transformMode,scope);panes.rack.body.append(rackModes);const rackList=node('div','fx-list');panes.rack.body.append(rackList);
  scope.onchange=()=>{cfg.rack=scope.value;save();paintRack();};
  function rackOptions(){const sig=JSON.stringify(state.layers.map(l=>[l.i,l.name]));if(scope.dataset.sig===sig)return;scope.dataset.sig=sig;scope.replaceChildren();option(scope,'follow','Selected layer');option(scope,'all','All effects');option(scope,'composition','Composition');for(const l of state.layers)option(scope,'layer:'+l.name,l.i+' · '+l.name);scope.value=cfg.rack;}
  function openEffect(e){if(!current(e)||document.pointerLockElement)return;selectedEffect=e.key;cfg.selectedEffect=e.key;save();paintParameters('a');paintParameters('b');paintRack();}
  function envelope(e,anchor){const live=current(e);if(live)fxPop(live,anchor,true);}
  const isStrobe=e=>/\/effect\/Strobe~\d+$/.test(e?.key||'');
  const heldStrobes=new Set();
  function strobeButton(e){
    let held=false;
    const b=button('Hold',ev=>ev?.preventDefault(),'fx-hold','Hold to strobe; release to stop');
    b.setAttribute('aria-label',e.name+' hold to activate');
    const press=()=>{if(held||!current(e)||!state.arena_connected)return;held=true;heldStrobes.add(release);effectSend(e,{cmd:'fx_press'});};
    const release=()=>{if(!held)return;held=false;heldStrobes.delete(release);cmd({cmd:'fx_release',key:e.key,instance:e.instance});};
    b._release=release;
    b.onpointerdown=ev=>{if(ev.button!==undefined&&ev.button!==0)return;ev.preventDefault();b.setPointerCapture(ev.pointerId);press();};
    b.onpointerup=b.onpointercancel=b.onlostpointercapture=b.onblur=release;
    b.onkeydown=ev=>{if([' ','Enter'].includes(ev.key)){ev.preventDefault();if(!ev.repeat)press();}};
    b.onkeyup=ev=>{if([' ','Enter'].includes(ev.key)){ev.preventDefault();release();}};
    return b;
  }
  window.addEventListener('blur',()=>{for(const release of [...heldStrobes])release();});
  window.addEventListener('pagehide',()=>{for(const release of [...heldStrobes])release();});
  const hasMeltLock=e=>['ParamBool','ParamBoolean'].includes(e?.params?.MELT_LOCK?.valuetype);
  function meltHoldButton(effect){
    const e={...effect};let held=false;
    const b=button('Hold melt',ev=>ev?.preventDefault(),'fx-bool-hold','Hold MELT_LOCK; release to stop holding');
    b.setAttribute('aria-label',e.name+' · Hold melt');
    const press=()=>{const live=current(e);if(held||!state.arena_connected||!live||!hasMeltLock(live))return;held=true;heldStrobes.add(release);effectSend(e,{cmd:'fx_bool_press',name:'MELT_LOCK'});};
    const release=()=>{if(!held)return;held=false;heldStrobes.delete(release);cmd({cmd:'fx_bool_release',key:e.key,instance:e.instance,name:'MELT_LOCK'});};
    b._release=release;
    b.onpointerdown=ev=>{if(ev.button!==undefined&&ev.button!==0)return;ev.preventDefault();b.setPointerCapture(ev.pointerId);press();};
    b.onpointerup=b.onpointercancel=b.onlostpointercapture=b.onblur=release;
    b.onkeydown=ev=>{if([' ','Enter'].includes(ev.key)){ev.preventDefault();if(!ev.repeat)press();}};
    b.onkeyup=ev=>{if([' ','Enter'].includes(ev.key)){ev.preventDefault();release();}};
    return b;
  }
  function meltLatchButton(effect){
    const e={...effect};
    const fire=()=>{const live=current(e);if(!state.arena_connected||!live||!hasMeltLock(live))return;effectSend(e,{cmd:'fx_param',name:'MELT_LOCK',value:!live.params.MELT_LOCK.value});};
    const b=button('Latch melt',ev=>{if(!ev||ev.detail===0)fire();},'fx-bool-latch','Toggle MELT_LOCK');
    b.setAttribute('aria-label',e.name+' · Latch melt');
    b.onpointerdown=ev=>{if(ev.button!==undefined&&ev.button!==0)return;ev.preventDefault();fire();};
    return b;
  }
  function directionButton(e,value){
    const fire=()=>effectSend(e,{cmd:'fx_direction',value});
    const b=button(value?'In':'Out',ev=>{if(!ev||ev.detail===0)fire();},value?'fx-in':'fx-out',value?'Play opacity forward to full, then hold':'Play opacity backward to zero, then hold');
    b.setAttribute('aria-label',e.name+(value?' fade in and hold':' fade out and hold'));
    b.onpointerdown=ev=>{if(ev.button!==undefined&&ev.button!==0)return;ev.preventDefault();fire();};
    return b;
  }
  const eventNames=e=>Object.entries(e.params||{}).filter(([name,p])=>name!=='MELT_TRIGGER'&&['ParamEvent','ParamTrigger'].includes(p?.valuetype)).map(([name])=>name);
  function eventButton(effect,name){
    // Capture identity independently of mutable readback objects.
    const e={...effect},label=name.replace(/_/g,' ').trim()||name;
    const fire=()=>{
      const live=current(e);
      if(!state.arena_connected||!live||!eventNames(live).includes(name))return;
      effectSend(e,{cmd:'fx_param',name,value:true});
      b.classList.remove('sent');void b.offsetWidth;b.classList.add('sent');
    };
    const b=button(label,ev=>{if(!ev||ev.detail===0)fire();},'fx-event',name+' · send native event');
    b.setAttribute('aria-label',effect.name+' · '+name);b.dataset.name=name;
    b.onpointerdown=ev=>{if(ev.button!==undefined&&ev.button!==0)return;ev.preventDefault();fire();};
    b.onanimationend=()=>b.classList.remove('sent');
    return b;
  }
  function paintRack(){
    compositionMode.setAttribute('aria-pressed',String(cfg.rack==='composition'));layerMode.setAttribute('aria-pressed',String(cfg.rack==='follow'));scope.value=cfg.rack;transformMode.disabled=!figureTransform()||!state.arena_connected;
    rackOptions();const list=(state.fx||[]).filter(e=>!isTransform(e)&&(cfg.rack==='all'||cfg.rack==='composition'?cfg.rack==='all'||e.scope==='C':cfg.rack==='follow'?e.layer===focusLayer:e.lname===cfg.rack.slice(6)));
    const sig=JSON.stringify(list.map(e=>[e.key,e.instance,e.name,e.target_kind,eventNames(e),hasMeltLock(e)]));if(rackList.dataset.sig!==sig){rackList.dataset.sig=sig;for(const cls of ['.fx-hold','.fx-bool-hold'])for(const b of rackList.querySelectorAll(cls))b._release();rackList.replaceChildren();for(const e of list){
      const row=node('div','fx-row');row.dataset.key=e.key;
      const open=button('',()=>openEffect(e),'fx-open');open.append(node('span','fx-name',e.name),node('span','fx-info'));
      const settings=button('⚙',()=>envelope(e,row),'fx-envelope','Fade in and fade out times');if(isTransform(e)){row.classList.add('fx-transform');settings.onclick=()=>openEffect(e);settings.title='Transform controls';row.append(open,settings);}else if(isStrobe(e)){settings.onclick=()=>openEffect(e);settings.title='Strobe controls';row.append(open,strobeButton(e),settings);}else row.append(open,directionButton(e,0),directionButton(e,1),settings);
      const names=eventNames(e);if(names.length||hasMeltLock(e)){const events=node('div','fx-events');if(hasMeltLock(e))events.append(meltHoldButton(e),meltLatchButton(e));for(const name of names)events.append(eventButton(e,name));row.append(events);}rackList.append(row);
    }}
    for(const e of list){const row=[...rackList.children].find(x=>x.dataset.key===e.key);if(!row)continue;row.classList.toggle('chosen',selectedEffect===e.key);row.classList.toggle('pinned',cfg.a.key===e.key||cfg.b.key===e.key);row.classList.toggle('pulsing',!!e.pulsing);const out=row.querySelector('.fx-out'),into=row.querySelector('.fx-in');const hold=row.querySelector('.fx-hold');for(const b of [out,into,hold].filter(Boolean))b.disabled=e.has_amount===false||!state.arena_connected;for(const b of row.querySelectorAll('.fx-event'))b.disabled=!state.arena_connected;const meltHold=row.querySelector('.fx-bool-hold'),meltLatch=row.querySelector('.fx-bool-latch');if(meltHold){meltHold.disabled=!state.arena_connected;if(!state.arena_connected)meltHold._release();}if(meltLatch){meltLatch.disabled=!state.arena_connected;meltLatch.setAttribute('aria-pressed',String(!!e.params.MELT_LOCK.value));}const parent=(state.layers||[]).find(l=>l.i===e.layer),context=e.scope==='C'?'Composition':e.lname,layerNote=parent?(parent.bypass?' · layer bypassed':parent.opacity<=.001?' · layer at 0%':!parent.ccol?' · no clip':''):'';const amount=e.observed_amount??e.env,bypassed=e.observed_bypassed??e.bypassed,on=!bypassed&&amount>.001;if(hold)hold.setAttribute('aria-pressed',String(on));else if(out&&into){out.setAttribute('aria-pressed',String(!on));into.setAttribute('aria-pressed',String(on));}row.querySelector('.fx-info').textContent=isTransform(e)?transformScope(e):`${context}${layerNote} · ${e.pulsing?'pulse '+(e.pulse_stage||'active'):e.pending?'waiting':Math.abs(e.target-e.env)>.015?(e.target>e.env?'fading in':'fading out')+' · '+Math.round(amount*100)+'%':bypassed?'Off':Math.round(amount*100)+'%'}${e.cfg.key?' · key '+e.cfg.key:''}`;}
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
  function targetOptions(id){const v=views[id],sig=JSON.stringify([state.clips.map(c=>sourceRef(c)),(state.fx||[]).map(e=>[e.key,e.name,e.lname]),cfg[id]]);if(v.pick.dataset.sig===sig)return;v.pick.dataset.sig=sig;v.pick.replaceChildren();option(v.pick,JSON.stringify({kind:'follow'}),'Follow selected source');option(v.pick,JSON.stringify({kind:'follow-effect'}),'Follow selected effect');for(const c of state.clips)option(v.pick,JSON.stringify(sourceRef(c)),'Source · '+label(c));for(const e of (state.fx||[]).filter(e=>!isTransform(e)||isFigureTransform(e)))option(v.pick,JSON.stringify({kind:'effect',key:e.key}),(isTransform(e)?'Transform · ':'Effect · ')+label(e)+' · '+e.key.split('~').at(-1));const key=JSON.stringify(cfg[id]);if(![...v.pick.options].some(o=>o.value===key))option(v.pick,key,'Pinned target unavailable');v.pick.value=key;}
  function disposeView(view){for(const b of view.controls.querySelectorAll('.fx-hold'))b._release();for(const w of Object.values(view.widgets))w.chip?.dispose();view.widgets={};view.content.replaceChildren();view.controls.replaceChildren();view.speed=view.pattern=view.amount=view.morph=view.moreToggle=null;view.timing=[];}
  function paintParameters(id){
    const view=views[id],locked=!!document.pointerLockElement;view.pick.disabled=view.pin.disabled=locked;
    if(locked&&view.content.contains(document.pointerLockElement)){if(resolve(cfg[id])?.instance!==view.c?.instance)view.summary.textContent='Target changed · release the pointer to reconnect this pane';return;}
    targetOptions(id);const c=resolve(cfg[id]);view.c=c;const follows=cfg[id].kind.startsWith('follow');view.pin.textContent=follows?'Pin':cfg[id].kind==='effect'?'Follow effect':'Follow source';view.pin.disabled=locked||(follows&&!c);view.pin.setAttribute('aria-pressed',String(!follows));view.pin.title=follows?'Keep this exact target in place':`Pinned target · click to follow the selected ${cfg[id].kind==='effect'?'effect':'source'}`;
    view.name.textContent=c?`${follows?'':'Pinned · '}${label(c)}`:follows?(cfg[id].kind==='follow-effect'?'Select an effect in the rack':'No adapted source selected'):'Pinned target unavailable';
    const m=motion(c),sig=JSON.stringify([cfg[id],c?.instance,c?.col,c?.target_kind,c?.name,delayEffect(c)?.instance,relatedDelays().map(x=>[x.effect.key,x.effect.instance]),(m?.slots||[]).map(s=>[s.name,s.choices,s.min,s.max,s.integer]),isEffect(c)?Object.entries(c.params||{}).map(([n,p])=>[n,p.id,p.valuetype,p.options,p.min,p.max]):null]);
    if(view.sig!==sig){view.sig=sig;disposeView(view);if(!c){view.summary.textContent='';view.content.append(node('p','pane-placeholder',follows?(cfg[id].kind==='follow-effect'?'Choose an effect name in the rack to inspect its motion.':'Choose a layer with an adapted Heart source to inspect its motion.'):'This exact target is not present. Choose another target above; these controls have not been redirected.'));return;}buildParameters(view,c);}
    if(!c)return;
    for(const input of view.controls.querySelectorAll('button,select,input'))input.disabled=!state.arena_connected||(input._available&&!input._available());
    if(m){const slots=m.slots||[],moving=slots.filter(x=>x.morphing),remaining=Math.max(0,...moving.map(x=>x.morph_remaining||0));view.summary.textContent=!slots.length?'No motion parameters on this target':`${state.hold?'Motion held · ':''}${slots.filter(x=>x.drive).length}/${slots.length} drives · ${m.guard||m.home_kind||'Home'}${moving.length?' · morphing '+remaining.toFixed(1)+'s':''}`;
      if(view.speed&&document.activeElement!==view.speed)view.speed.value=m.g?.speed??1;
      if(view.pattern&&document.activeElement!==view.pattern)view.pattern.value=m.pattern||(state.families||FAMILIES)[m.g?.pattern??0];
      if(view.moreToggle){const family=m.pattern||(state.families||FAMILIES)[m.g?.pattern??0];view.moreToggle.textContent='More · '+family;view.moreToggle.title='Relationship: '+family+' · all relationships, morph and Home settings';}
      if(view.morph&&document.activeElement!==view.morph)view.morph.value=m.morph??0;
      for(const b of view.timing)b.setAttribute('aria-pressed',String(m.g?.timing_mode===b.dataset.mode));
      for(const sl of slots){const w=view.widgets[sl.name];if(!w)continue;w.sl=sl;if(w.valueInput&&document.activeElement!==w.valueInput)w.valueInput.value=w.display();if(w.ratioPick&&document.activeElement!==w.ratioPick)w.ratioPick.value=sl.ratio;if(w.rate)w.rate.textContent=(motion(c)?.g?.pattern?'base · ':'')+sl.mult+'×';if(w.picker){if(document.activeElement!==w.picker)w.picker.value=sl.choices[Math.round(sl.v*(sl.choices.length-1))];continue;}if(!w.chip)continue;if(!w.chip.locked)w.chip.set(sl.v,true);if(w.chip.driven!==sl.drive)w.chip.setDriven(sl.drive,true);w.lock.classList.toggle('on',!!sl.lock);w.lock.setAttribute('aria-pressed',String(!!sl.lock));if(!w.chip.menusOpen())w.chip.syncConfig({ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,min:sl.lo,max:sl.hi});}
    }else view.summary.textContent='Effect motion unavailable · manual controls';
    view.summary.title=view.summary.textContent;
    if(isEffect(c)){for(const [name,w] of Object.entries(view.widgets)){const p=c.params[name];if(!p||w.sl)continue;if(w.chip){if(!w.chip.locked)w.chip.set((p.value-(p.min??0))/((p.max??1)-(p.min??0)||1),true);}else if(w.input&&document.activeElement!==w.input){if(w.input.type==='checkbox')w.input.checked=!!p.value;else if(w.input.type!=='button')w.input.value=w.input.type==='color'?String(p.value).slice(0,7):p.value;}}
      if(view.amount&&document.activeElement!==view.amount)view.amount.value=c.target;
    }
  }
  function buildMotionTools(view,c,m){
    const toolbar=node('div','param-actions');view.controls.append(toolbar);toolbar.append(button('Home',()=>send(c,{cmd:'home'}),'home',isTransform(c)?'Settle this transform to its saved still pose':isEffect(c)?'Settle to a still pose and fade this effect out':'Settle this source to a still Home pose'),button('Open',()=>send(c,{cmd:'open'}),'open-motion',"Start motion using this target’s operating ranges"),button('Shuffle',()=>send(c,{cmd:'fire'}),'shuffle'),button('Undo',()=>send(c,{cmd:'undo'})));
    view.speed=node('select');view.speed.setAttribute('aria-label',label(c)+' speed');for(const x of [.0625,.125,.25,.5,1,2,4,8,16])option(view.speed,x,x+'×');view.speed.onchange=()=>send(c,{cmd:'speed',value:+view.speed.value});toolbar.append(view.speed);
    const timing=node('div','param-actions timing-actions');view.controls.append(timing);for(const [mode,text] of [['unison','Stable'],['harmonic','Musical'],['irrational','Irrational']]){const b=button(text,()=>send(c,{cmd:'timing',mode}),'',mode+' timing');b.dataset.mode=mode;view.timing.push(b);timing.append(b);}
    const more=node('details','motion-more'),extra=node('div','motion-more-content');view.moreToggle=node('summary','','More');view.moreToggle.setAttribute('aria-label',label(c)+' more motion settings');more.append(view.moreToggle,extra);timing.append(more);
    view.pattern=node('select','relationship-choice');view.pattern.setAttribute('aria-label',label(c)+' relationship');for(const family of state.families||FAMILIES)option(view.pattern,family,family);view.pattern.onchange=()=>send(c,{cmd:'global_cfg',key:'Pattern',value:view.pattern.value});const familyLabel=node('label','motion-family-label','Relationship');familyLabel.append(view.pattern);extra.append(familyLabel);
    const morphLabel=node('label','morph-control','Morph s');view.morph=node('input');view.morph.type='number';view.morph.min=0;view.morph.max=60;view.morph.step=.25;view.morph.setAttribute('aria-label',label(c)+' morph seconds');view.morph.onchange=()=>send(c,{cmd:'morph',seconds:+view.morph.value});morphLabel.append(view.morph);extra.append(morphLabel);
    extra.append(button('Set Home',()=>send(c,{cmd:'home_set'}),'set-motion-home','Save the current visible pose as the still Home for this target'));
    if(c.feedback_behaviors?.length){const fb=node('div','param-actions');for(const name of c.feedback_behaviors)fb.append(button(name,()=>send(c,{cmd:'feedback_behavior',name})));fb.append(button('Reset trails',()=>send(c,{cmd:'feedback_reset'})));extra.append(fb);}
  }
  function buildMotionSlot(view,c,sl,grid){
    const row=node('div','slot2');grid.append(row);if(sl.choices?.length){row.append(node('label','',sl.name));const picker=node('select');picker.setAttribute('aria-label',sl.name);for(const s of sl.choices)option(picker,s,s);picker.onchange=()=>send(c,{cmd:'choice',slot:sl.name,option:picker.value});row.append(picker);view.widgets[sl.name]={picker,sl};return;}
    const mini=node('div','ax'),w={sl};const good=button('Reset',()=>send(c,{cmd:'good_go',slot:sl.name}),'axb','Return to saved Home, authored Home, or the value when this control connected');const lock=button('Lock',()=>send(c,{cmd:'slot_cfg',slot:sl.name,key:'Lock',value:!w.sl.lock}),'axb','Exclude this axis from shuffles');const fire=button('⚡',()=>send(c,{cmd:'fire_slot',slot:sl.name}),'axb','Shuffle this axis');mini.append(good,lock,fire);row.append(mini);
    const native=isEffect(c),lo=sl.min??0,span=(sl.max??1)-lo||1,integer=!!sl.integer;
    const chip=createSmartParam({label:sl.name,value:sl.v,driven:sl.drive,wrap:!!sl.cyc,min:sl.lo,max:sl.hi,ratioLabels:RATIOS,ratio:Math.max(0,RATIOS.indexOf(sl.ratio)),multiplier:sl.mult,offset:sl.offset??0,
      ...(native?{step:integer?1/span:.01,format:v=>kitFormat(integer?Math.round(lo+v*span):lo+v*span),parse:v=>(v-lo)/span}:{}),
      onInput:value=>send(c,{cmd:'manual',slot:sl.name,value}),onDrive:on=>send(c,{cmd:'drive',slot:sl.name,on}),onReset:()=>send(c,{cmd:'good_go',slot:sl.name}),onHomeSet:()=>send(c,{cmd:'good_set',slot:sl.name}),
      onConfig:cf=>{const entries=[['Ratio',RATIOS[cf.ratio],w.sl.ratio],['Mult',cf.multiplier,w.sl.mult],['Offset',cf.offset,w.sl.offset??0],['Lo',cf.min,w.sl.lo],['Hi',cf.max,w.sl.hi]];for(const [key,value,old] of entries)if(value!==old)send(c,{cmd:'slot_cfg',slot:sl.name,key,value});}});
    row.append(chip.el);
    const quick=node('div','param-quick'),valueInput=node('input'),ratioPick=node('select'),rate=node('span','param-rate');
    valueInput.type='number';valueInput.step=integer?'1':'any';valueInput.min=native?lo:0;valueInput.max=native?lo+span:1;valueInput.setAttribute('aria-label',sl.name+' exact value');valueInput.title='Type a value · Enter applies · Escape cancels; applying stops this drive';
    const display=()=>String(native?(integer?Math.round(lo+w.sl.v*span):Number((lo+w.sl.v*span).toFixed(5))):Number(w.sl.v.toFixed(5)));
    valueInput.value=display();let cancelled=false;
    valueInput.onfocus=()=>{cancelled=false;};
    valueInput.onchange=()=>{if(cancelled)return;const v=Number(valueInput.value);if(valueInput.value.trim()===''||!Number.isFinite(v)){valueInput.value=display();return;}const normalized=Math.max(0,Math.min(1,native?((integer?Math.round(v):v)-lo)/span:v));send(c,{cmd:'manual',slot:sl.name,value:normalized});};
    valueInput.onkeydown=ev=>{ev.stopPropagation();if(ev.key==='Escape'){cancelled=true;valueInput.value=display();valueInput.blur();}else if(ev.key==='Enter')valueInput.blur();};
    ratioPick.setAttribute('aria-label',sl.name+' ratio');for(const r of RATIOS)option(ratioPick,r,r);ratioPick.value=sl.ratio;ratioPick.title='Per-parameter ratio; a selected relationship family can override this base ratio';ratioPick.onchange=()=>send(c,{cmd:'slot_cfg',slot:sl.name,key:'Ratio',value:ratioPick.value});
    quick.append(valueInput,ratioPick,rate);row.append(quick);Object.assign(w,{valueInput,ratioPick,rate,display});
    if(native)row.append(node('div','native-value',integer?'whole steps':c.params[sl.name]?.view?.suffix?.trim()||'native units'));Object.assign(w,{chip,lock});view.widgets[sl.name]=w;
  }
  function delayEffect(c){
    if(!c)return null;
    const candidates=isEffect(c)?[c]:(state.fx||[]).filter(e=>e.scope==='K'&&e.layer===c.layer);
    const found=candidates.filter(e=>e.name==='SP Delay Chain'&&['⚡ Shuffle','⌂ Home','φ'].every(n=>e.params?.[n]?.valuetype==='ParamEvent'));
    return found.length===1?found[0]:null;
  }
  function relatedDelays(){
    return [['DelayRGB','L','sculpt','RGB delay · Sculpt'],['ColourLoop','C',null,'Colour loop · Composition']].flatMap(([name,scope,layer,text])=>{
      const found=(state.fx||[]).filter(e=>e.name===name&&e.scope===scope&&(!layer||e.lname?.toLowerCase()===layer));
      return found.length===1?[{effect:found[0],text}]:[];
    });
  }
  function delayLink(c,e,text,resolveTarget){
    const instance=e.instance,key=e.key,sourceInstance=c.instance;
    const available=()=>{const target=resolveTarget();return current(c)?.instance===sourceInstance&&target?.key===key&&target.instance===instance&&!!current(target);};
    const b=button(text,()=>{if(!state.arena_connected||document.pointerLockElement||!available())return;cfg.b={kind:'effect',key};openEffect(resolveTarget());},'delay-control-link','Open and pin existing effect in Parameters B');
    b._available=available;return b;
  }
  function buildParameters(view,c){
    const m=motion(c);if(m?.slots?.length)buildMotionTools(view,c,m);
    if(/\/effect\/(LinearCloner|RadialCloner|Iterate)~\d+$/.test(c.key||''))view.controls.append(node('p','pane-note effect-range-note','Open protects scale / holds structural controls; manual edits remain available'));
    const delay=delayEffect(c);
    if(delay){const delayInstance=delay.instance;const actions=node('div','param-actions delay-actions');actions.append(node('span','',isEffect(c)?'Delay pattern':'Delay motion here · direct effect controls in B'));
      if(!isEffect(c))actions.append(delayLink(c,delay,'Delay controls',()=>delayEffect(current(c))));
      for(const {effect,text} of relatedDelays())actions.append(delayLink(c,effect,text,()=>relatedDelays().find(x=>x.text===text)?.effect));
      for(const [name,text] of [['⚡ Shuffle','Shuffle taps'],['⌂ Home','Reset taps'],['φ','Golden taps']])actions.append(button(text,()=>{if(current(c)&&delayEffect(current(c))?.instance===delayInstance)effectSend(delay,{cmd:'fx_param',name,value:true});},'',text+' in the native delay line; separate from Heart motion Home and Shuffle'));
      view.controls.append(actions);
    }
    if(isStrobe(c)){const actions=node('div','param-actions effect-envelope');actions.append(strobeButton(c));view.controls.append(actions);}else if(isEffect(c)&&!isTransform(c)){const actions=node('div','param-actions effect-envelope');actions.append(button('Envelope',()=>envelope(c,view.name)));view.controls.append(actions);
      if(c.has_amount!==false){actions.append(directionButton(c,0),directionButton(c,1));const line=node('label','effect-level','Opacity');const amount=node('input');amount.type='range';amount.min=0;amount.max=1;amount.step=.001;amount.setAttribute('aria-label',label(c)+' envelope opacity');amount.oninput=()=>effectSend(c,{cmd:'fx_amount',value:+amount.value});line.append(amount);actions.append(line);view.amount=amount;}
    }
    const grid=node('div','parameter-grid');view.content.append(grid);
    for(const sl of m?.slots||[])if(!(isEffect(c)&&sl.name==='Opacity'&&c.has_amount!==false))buildMotionSlot(view,c,sl,grid);
    if(!isEffect(c))return;
    for(const [name,p] of Object.entries(c.params||{})){if(name==='MELT_TRIGGER'||view.widgets[name]||(name==='Opacity'&&c.has_amount!==false))continue;const row=node('div','slot2');grid.append(row);
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
  window.addEventListener('pagehide',()=>{for(const release of [...heldStrobes])release();for(const view of Object.values(views)){disposeView(view);view.sig='';}});
  layout();reportMonitor();if(!ws)connect();
})();
