/* Device regions bind through the same identity-checked action interface as MIDI. */
(()=>{
 const M=window.HeartMapping;if(!M)return;
 const host=document.querySelector('.trackpad-panel');if(!host)return;
 const original=[...host.children];for(const e of original)if(!e.classList.contains('grab-trackpad'))e.hidden=true;
 const box=document.createElement('div');box.className='mapped-trackpad';host.prepend(box);
 let config;try{config=JSON.parse(localStorage.getItem('heart-trackpad-map-v1'))||{};}catch{config={};}
 config.mode=config.mode==='pads'?'pads':'faders';config.faders||=[];config.pads||=[];config.behaviors||={};
 if(!config.faders.some(Boolean)&&typeof PAD!=='undefined')for(const l of M.state()?.layers||[]){const lane=PAD.laneOf(l.i);if(lane)config.faders[lane-1]={kind:'layer',role:l.name};}
 const save=()=>localStorage.setItem('heart-trackpad-map-v1',JSON.stringify(config));
 const mode=document.createElement('select');mode.setAttribute('aria-label','Trackpad layout');mode.innerHTML='<option value="faders">4 faders</option><option value="pads">8 pads</option>';mode.value=config.mode;
 const note=document.createElement('p');note.className='pane-note';note.textContent='Drag a region onto a parameter, layer level or action. Physical click grabs; click again or Escape releases.';
 const grid=document.createElement('div');grid.className='mapping-pad-grid';box.append(mode,note,grid);
 let active={},capture=null,wasLocked=false;const tails=new Map();
 function stopTail(i,finish=false){const t=tails.get(i);if(t){cancelAnimationFrame(t.frame);if(finish&&M.identity(t.binding)===t.id)M.dispatch(t.binding,0);tails.delete(i);}}
 function spring(i,t){stopTail(i);const start=performance.now(),from=M.read(t.binding)||0,item={...t,frame:0};tails.set(i,item);const step=()=>{if(tails.get(i)!==item)return;if(M.identity(t.binding)!==t.id){tails.delete(i);return;}const progress=Math.min(1,(performance.now()-start)/150);M.dispatch(t.binding,from*(1-progress)*(1-progress));if(progress<1)item.frame=requestAnimationFrame(step);else tails.delete(i);};step();}
 const clamp=v=>Math.max(0,Math.min(1,v));
 function release(){for(const x of Object.values(active))x.release?.();for(const i of [...tails.keys()])stopTail(i,true);active={};capture=null;wasLocked=false;}
 window.heartEightPadRelease=release;
 mode.onchange=()=>{if(PAD.isLocked()){mode.value=config.mode;return;}release();config.mode=mode.value;save();paint();};
 function paint(){
  box.dataset.mode=config.mode;window.heartPadMode='mapped';const list=config[config.mode],n=config.mode==='pads'?8:4;window.heartEightPadReady=list.some(Boolean);grid.style.gridTemplateColumns='repeat(4,minmax(0,1fr))';grid.replaceChildren();
  for(let i=0;i<n;i++){
   const cell=document.createElement('div');cell.className='mapping-pad-cell';cell.draggable=true;cell.dataset.region=i;
   const title=document.createElement('strong');title.textContent=(config.mode==='pads'?'Pad ':'Fader ')+(i+1);
   const select=document.createElement('select');select.setAttribute('aria-label',title.textContent+' target');const empty=document.createElement('option');empty.value='';empty.textContent='Unassigned';select.append(empty);
   const options=M.choices(config.mode==='pads'?'button':'axis');for(const x of options){const o=document.createElement('option');o.value=JSON.stringify(x.binding);o.textContent=x.label;select.append(o);}
   if(list[i]&&!options.some(x=>JSON.stringify(x.binding)===JSON.stringify(list[i]))){const o=document.createElement('option');o.value=JSON.stringify(list[i]);o.textContent='Unavailable assignment';select.append(o);}
   select.value=list[i]?JSON.stringify(list[i]):'';
   select.onchange=()=>{if(PAD.isLocked())return;list[i]=select.value?JSON.parse(select.value):null;save();window.heartEightPadReady=list.some(Boolean);};
   cell.ondragstart=e=>{if(PAD.isLocked()){e.preventDefault();return;}M.assignSource=b=>{const axis=b.kind==='axis'||b.kind==='layer';if((config.mode==='faders')!==axis){note.textContent=config.mode==='faders'?'Faders need a continuous parameter or layer level.':'Pads need an action button.';return;}list[i]=b;save();paint();};e.dataTransfer.setData('application/x-heart-control',JSON.stringify({device:'trackpad',region:i}));};cell.ondragend=()=>{M.assignSource=null;};
   cell.append(title,select);if(config.mode==='faders'){const behavior=document.createElement('select');behavior.setAttribute('aria-label',title.textContent+' behavior');behavior.innerHTML='<option value=absolute>Absolute</option><option value=relative>Relative</option><option value=spring>Spring → 0</option>';behavior.value=config.behaviors[i]||'absolute';behavior.onchange=()=>{if(PAD.isLocked())return;config.behaviors[i]=behavior.value;save();};cell.append(behavior);}grid.append(cell);
  }
 }
 window.heartEightPadFrame=s=>{
  if(!PAD.isLocked())return false;
  if(!wasLocked){capture=config[config.mode].map(b=>b?{binding:b,id:M.identity(b)}:null);wasLocked=true;}
  if(s.offline||!M.state()?.arena_connected||capture.some(x=>x&&(!x.id||M.identity(x.binding)!==x.id))){release();PAD.release();return true;}
  const touched={};for(const g of s.fingers||[])if(g.state!=='leave'&&g.state!=='hover'){
   const i=Math.min(3,Math.max(0,Math.floor(g.x*4)))+(config.mode==='pads'?(g.y<.5?4:0):0);touched[i]=g;
  }
  for(const [i,g] of Object.entries(touched)){
   const t=capture[i];if(!t)continue;
   if(config.mode==='pads'){if(!active[i])active[i]={release:M.dispatch(t.binding,1)};}
   else {stopTail(i);const mode=config.behaviors[i]||'absolute',previous=active[i];const v=mode==='relative'?clamp((previous?.value??M.read(t.binding)??0)+(previous?g.y-previous.y:0)):clamp(g.y);M.dispatch(t.binding,v);active[i]={value:v,y:g.y,release:mode==='spring'?()=>spring(i,t):null};}
  }
  for(const i of Object.keys(active))if(!touched[i]){active[i].release?.();delete active[i];}
  for(const cell of grid.children)cell.classList.toggle('active',!!touched[cell.dataset.region]);return true;
 };
 window.addEventListener('blur',release);window.addEventListener('pagehide',release);
 let sig='';window.heartTrackpadMappingPaint=()=>{const next=M.choices('axis').map(x=>x.label).join('|')+M.choices('button').map(x=>x.label).join('|');if(!PAD.isLocked()&&sig!==next){sig=next;paint();}mode.disabled=PAD.isLocked();};paint();
})();
