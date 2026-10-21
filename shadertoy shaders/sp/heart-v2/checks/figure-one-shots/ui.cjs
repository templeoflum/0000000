const {chromium}=require('/Users/donovan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const fixture=read('checks/session-surface-fixture.json');
fixture.catalog=read('checks/figure-one-shots/catalog-before.json');fixture.catalog.effect_rack=read('effect-rack.json');
const c=fixture.catalog,params=new Map(c.targets.flatMap(t=>t.params.map(p=>[p.id,p]))),s=fixture.state;
s.values=Object.fromEntries([...params].map(([id,p])=>[id,{value:p.value,drive:false,owned:false,lo:0,hi:1,locked:false}]));
s.selected=c.targets.find(t=>t.kind==='source')?.id||c.targets[0].id;s.groups=Object.fromEntries(c.targets.map(t=>[t.id,{pattern:0,speed:1,depth:1,spread:1,seed:0,fm:0}]));
s.authored={};s.drive_bank={};s.armed=s.connected=true;s.session={busy:false,recovery:{base:false,safe:false},loops:{}};s.effect_rack={};
for(const r of c.effect_rack.rows){
 s.session.loops[r.id]={running:false,pattern:'kick',kick:'twitch',snare:'stack',strength:.65,length:.25,beat:1};
 const live={ready:true,color:0,mixed:false,controls:{},levels:{},enabled:{},latched:{},active:{}};
 for(const ctl of r.controls||[])live.controls[ctl.id]={value:params.get(ctl.bindings[0].parameter).value,mixed:false};
 for(const pad of r.pads){live.levels[pad.id]={value:params.get(pad.bindings[0].opacity).value,mixed:false};live.enabled[pad.id]=true;live.active[pad.id]=false;}
 s.effect_rack[r.id]=live;
}
(async()=>{
 const browser=await chromium.launch(),page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://heart.test/**',r=>{const p=new URL(r.request().url()).pathname;return r.fulfill({contentType:p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'text/html',body:fs.readFileSync(path.join(root,p==='/'?'index.html':p.slice(1)),'utf8')});});
 await page.addInitScript(f=>{window.fixture=f;window.commands=[];window.WebSocket=class{constructor(){this.readyState=1;window.socket=this;setTimeout(()=>{this.onopen?.();this.emit(f.catalog);this.publish();},20);}emit(m){this.onmessage?.({data:JSON.stringify(m)});}publish(){this.emit(f.state);}send(raw){const d=JSON.parse(raw);commands.push(d);if(d.cmd==='select')f.state.selected=d.target;if(d.cmd==='rack_sequence')Object.assign(f.state.session.loops[d.row],d);if(!['watch','refresh'].includes(d.cmd))this.publish();}};},fixture);
 try{
  for(const [width,height] of [[639,734],[1440,900]]){
   await page.setViewportSize({width,height});await page.goto('http://heart.test');await page.waitForFunction(()=>window.heartPlaying);await page.getByRole('button',{name:'Perform',exact:true}).click();
   const row=page.locator('[data-rack-row="figure"]');await row.scrollIntoViewIfNeeded();
   assert.equal(await row.locator('input[type=range]:visible').count(),0);
   for(const [label,key] of [['Infinite Zoom','infinite_zoom'],['Low Rez','low_rez']]){
    const b=page.getByRole('button',{name:'Figure '+label,exact:true});await b.click();let d=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_fire').at(-1));assert.equal(d.row,'figure');assert.equal(d.pad,key);assert.equal(d.amount,.65);assert.equal(d.beats,.25);
    await b.focus();await page.keyboard.press('Enter');d=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_fire').at(-1));assert.equal(d.pad,key);
   }
   assert(await row.evaluate(e=>e.scrollWidth<=e.clientWidth));assert(await row.locator('.rack-native-control').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect(),p=e.closest('section').getBoundingClientRect();return r.bottom<=p.bottom&&r.right<=p.right;})));
   await page.screenshot({path:path.join(__dirname,'rack-'+width+'.png')});
   await page.getByRole('button',{name:'Figure color and loop controls',exact:true}).click();
   for(const [voice,key] of [['kick','infinite_zoom'],['snare','low_rez']]){await page.getByRole('combobox',{name:'Figure '+voice+' effect',exact:true}).selectOption(key);assert.equal(await page.evaluate(v=>commands.filter(c=>c.cmd==='rack_sequence').at(-1)[v],voice),key);}
   await page.evaluate(()=>{fixture.state.armed=false;socket.publish();});assert(await page.getByRole('button',{name:'Figure Infinite Zoom',exact:true}).isDisabled());assert(await page.getByRole('button',{name:'Figure Low Rez',exact:true}).isDisabled());
  }
  assert.deepEqual(errors,[]);console.log('PASS compact/wide Figure one-shot clicks, keyboard, kick/snare choices, collapsed sliders, bounds and disabled state.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
