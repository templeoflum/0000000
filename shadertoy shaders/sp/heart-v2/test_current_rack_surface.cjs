const {chromium}=require('/Users/donovan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const read=name=>JSON.parse(fs.readFileSync(__dirname+'/'+name,'utf8'));
const fixture=read('checks/session-surface-fixture.json');
fixture.catalog=read('checks/session-composition-goo-catalog.json');
fixture.catalog.effect_rack=read('effect-rack.json');
const catalog=fixture.catalog,rack=catalog.effect_rack,params=new Map(catalog.targets.flatMap(t=>t.params.map(p=>[p.id,p])));
fixture.state.values=Object.fromEntries([...params].map(([id,p])=>[id,{value:p.value,drive:false,owned:false,lo:0,hi:1,locked:false}]));
fixture.state.selected=catalog.targets.find(t=>t.kind==='source')?.id||catalog.targets[0].id;
fixture.state.groups=Object.fromEntries(catalog.targets.map(t=>[t.id,{pattern:0,speed:1,depth:1,spread:1,seed:0,fm:0}]));
fixture.state.authored={};fixture.state.drive_bank={};fixture.state.armed=fixture.state.connected=true;
fixture.state.session={busy:false,recovery:{base:false,safe:false},loops:{}};fixture.state.effect_rack={};
for(const row of rack.rows){
 const voices=row.pads.filter(p=>['toggle','pulse','trigger'].includes(p.mode));
 fixture.state.session.loops[row.id]={running:false,pattern:'kick',kick:voices[0]?.id||'',snare:voices.at(-1)?.id||'',strength:.65,length:.25,beat:1};
 const live={ready:true,color:row.color.length?params.get(row.color[0].opacity).value:0,mixed:false,controls:{},levels:{},enabled:{},latched:{},active:{}};
 for(const c of row.controls)live.controls[c.id]={value:params.get(c.bindings[0].parameter).value,mixed:false};
 for(const p of row.pads){live.levels[p.id]={value:params.get(p.bindings[0].opacity).value,mixed:false};live.enabled[p.id]=p.bindings.every(b=>!params.get(b.bypass).value&&params.get(b.opacity).value>0);live.latched[p.id]=p.mode==='latch'&&p.bindings.every(b=>params.get(b.latch).value);live.active[p.id]=false;}
 fixture.state.effect_rack[row.id]=live;
}
(async()=>{
 const browser=await chromium.launch(),page=await browser.newPage({viewport:{width:639,height:734}}),errors=[];page.setDefaultTimeout(6000);page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://heart.test/**',r=>{const p=new URL(r.request().url()).pathname;return r.fulfill({contentType:p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'text/html',body:fs.readFileSync(__dirname+(p==='/'?'/index.html':p),'utf8')});});
 await page.addInitScript(f=>{window.fixture=f;window.commands=[];window.WebSocket=class{constructor(){this.readyState=1;window.socket=this;setTimeout(()=>{this.onopen?.();this.emit(f.catalog);this.publish();},20);}emit(m){this.onmessage?.({data:JSON.stringify(m)});}publish(){this.emit(f.state);}send(raw){const d=JSON.parse(raw);commands.push(d);if(d.cmd==='select')f.state.selected=d.target;if(d.cmd==='rack_parameter'){const row=f.catalog.effect_rack.rows.find(r=>r.id===d.row),c=row.controls.find(c=>c.id===d.control);f.state.effect_rack[d.row].controls[c.id]={value:d.value,mixed:false};for(const b of c.bindings)f.state.values[b.parameter].value=d.value;}if(d.cmd==='rack_sequence')Object.assign(f.state.session.loops[d.row],d);if(!['watch','refresh'].includes(d.cmd))this.publish();}};},fixture);
 try{
  await page.goto('http://heart.test');await page.waitForFunction(()=>window.heartPlaying);await page.getByRole('button',{name:'Perform',exact:true}).click();
  assert.deepEqual(await page.locator('.hit-rack-row').evaluateAll(es=>es.map(e=>e.dataset.rackRow)),['output','stage','field','feedback']);
  assert.equal(await page.locator('.rack-advanced[hidden]').count(),0);assert.equal(await page.locator('.hit-row-pads button').filter({hasText:/Melt hit/i}).count(),0);
  assert.equal(await page.locator('.loop-assignments option[value="melt_hit"]').count(),0);
  for(const row of rack.rows){
   const box=page.locator('[data-rack-row="'+row.id+'"]');assert(await box.locator('.rack-color-tools').isVisible());assert(await box.locator('.rack-sequence').isVisible());
   assert.equal(await box.locator('.rack-color-tools input,.rack-color-tools select').count(),row.controls.length);
   for(const c of row.controls){const control=page.getByLabel(row.label+' '+c.label,{exact:true});await control.scrollIntoViewIfNeeded();assert(await control.isVisible());assert(!(await control.isDisabled()));const r=await control.boundingBox(),panel=await page.locator('#perform-panel').boundingBox();assert(r.x>=panel.x&&r.x+r.width<=panel.x+panel.width+1);assert(r.y>=panel.y-1&&r.y+r.height<=panel.y+panel.height+1);}
  }
  const output=rack.rows.find(r=>r.id==='output'),bool=output.controls.find(c=>(c.type||c.bindings[0].type)==='ParamBoolean'),choice=output.controls.find(c=>(c.type||c.bindings[0].type)==='ParamChoice');assert(bool&&choice);
  const checkbox=page.getByRole('checkbox',{name:output.label+' '+bool.label,exact:true}),before=await checkbox.isChecked();await checkbox.setChecked(!before);await page.waitForTimeout(100);let command=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_parameter').at(-1));assert.equal(command.control,bool.id);assert.equal(command.value,!before);assert.equal(typeof command.value,'boolean');
  const select=page.getByRole('combobox',{name:output.label+' '+choice.label,exact:true}),current=await select.inputValue(),next=choice.options.find(v=>v!==current);await select.selectOption(next);await page.waitForTimeout(100);command=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_parameter').at(-1));assert.equal(command.control,choice.id);assert.equal(command.value,next);assert.equal(typeof command.value,'string');assert.equal(await select.inputValue(),next);
  await page.locator('#perform-panel').evaluate(e=>e.scrollTop=0);await page.screenshot({path:'/tmp/heart-current-output-compact.png'});
  const feedback=rack.rows.find(r=>r.id==='feedback'),invertA=feedback.controls.find(c=>c.label==='Invert A');assert(invertA);const alpha=page.getByRole('slider',{name:feedback.label+' '+invertA.label,exact:true});await alpha.fill('0.43');await page.waitForTimeout(100);command=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_parameter').at(-1));assert.equal(command.control,invertA.id);assert.equal(command.value,.43);assert.equal(typeof command.value,'number');await alpha.scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/heart-current-feedback-compact.png'});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight));
  assert(await page.locator('#perform-panel,.hit-rack-row,.rack-color-tools').evaluateAll(es=>es.every(e=>e.scrollWidth<=e.clientWidth+1)));
  assert(await page.locator('.hit-rack-row').evaluateAll(es=>es.every((e,i)=>!i||es[i-1].getBoundingClientRect().bottom<=e.getBoundingClientRect().top)));
  assert.equal(await page.locator('#fx-rows').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length),2);assert.deepEqual(errors,[]);
  console.log('PASS current 639x734 rack: Composition Goo seven controls, boolean/choice/numeric commands, Invert A, all four rows expanded and reachable, no Melt hit, no overlap/overflow or JS errors, two-column effects.');
 }catch(error){await page.screenshot({path:'/tmp/heart-current-rack-failure.png'});throw error;}finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
