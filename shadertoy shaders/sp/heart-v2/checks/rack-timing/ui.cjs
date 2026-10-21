const {chromium}=require('/Users/donovan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fixture.json'),'utf8'));
(async()=>{
 const browser=await chromium.launch(),page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://heart.test/**',r=>{const p=new URL(r.request().url()).pathname;return r.fulfill({contentType:p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'text/html',body:fs.readFileSync(path.join(root,p==='/'?'index.html':p.slice(1)),'utf8')});});
 await page.addInitScript(f=>{window.fixture=f;window.commands=[];window.WebSocket=class{
  constructor(){this.readyState=1;window.socket=this;setTimeout(()=>{this.onopen?.();this.emit(f.catalog);this.publish();},20);}
  emit(m){this.onmessage?.({data:JSON.stringify(m)});}publish(){this.emit(f.state);}
  send(raw){const d=JSON.parse(raw);commands.push(d);
   if(d.cmd==='select')f.state.selected=d.target;
   if(d.cmd==='rack_timing')f.state.session.loops[d.row].timings[d.pad]=d.length;
   if(d.cmd==='rack_sequence')Object.assign(f.state.session.loops[d.row],d);
   if(d.cmd==='effect_color')for(const row of f.catalog.effect_rack.rows)for(const key of ['lut','color'])if(row[key]?.[0]?.opacity===d.bindings[0]?.opacity)f.state.effect_rack[row.id][key]=d.amount;
   if(d.cmd==='rack_parameter')f.state.effect_rack[d.row].controls[d.control].value=d.value;
   if(d.cmd==='rack_control'&&d.action==='enable')f.state.effect_rack[d.row].enabled[d.pad]=d.on;
   if(!['watch','refresh'].includes(d.cmd))this.publish();
  }
 };},fixture);
 try{
  for(const [width,height] of [[639,734],[1440,900],[480,800]]){
   await page.setViewportSize({width,height});await page.goto('http://heart.test');await page.waitForFunction(()=>window.heartPlaying);await page.getByRole('button',{name:'Perform',exact:true}).click();
   const rack=page.locator('#performance-rack'),figure=page.locator('[data-rack-row="figure"]'),feedback=page.locator('[data-rack-row="feedback"]');
   assert.equal(await rack.locator('input[type=range]').count(),9);assert.equal(await rack.locator('.rack-pad-alpha').count(),0);
   for(const row of fixture.catalog.effect_rack.rows){
    const box=page.locator('[data-rack-row="'+row.id+'"]');await box.scrollIntoViewIfNeeded();
    if(row.id!=='feedback')for(const label of ['LUT','Color Loop'])assert(await page.getByRole('slider',{name:row.label+' '+label+' amount',exact:true}).isVisible());
    assert(await box.locator('.rack-native-control').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect(),p=e.closest('section').getBoundingClientRect();return r.bottom<=p.bottom+1&&r.right<=p.right+1;})));
   }
   const invert=page.getByRole('slider',{name:'Feedback Invert A',exact:true});await invert.fill('0.42');await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_parameter').at(-1).value),.42);
   assert.equal(await feedback.getByRole('button',{name:/Run\/Stop/}).count(),0);assert.equal(await page.locator('[data-rack-row="output"]').getByRole('button',{name:/Run\/Stop/}).count(),0);
   const mirror=page.getByRole('button',{name:'Feedback Mirror X',exact:true});await mirror.click();assert.equal(await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_control').at(-1).action),'enable');await page.getByRole('combobox',{name:'Feedback Mirror X fade time',exact:true}).selectOption('2');assert.equal(await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_timing').at(-1).length),2);
   await page.screenshot({path:path.join(__dirname,'feedback-'+width+'.png')});
   await figure.scrollIntoViewIfNeeded();
   for(const [label,key] of [['Linear Cloner','linear_cloner'],['Mirror X','mirror_x'],['Mirror Y','mirror_y'],['Mirror XY','mirror_xy']]){
    const toggle=page.getByRole('button',{name:'Figure '+label,exact:true});await toggle.click();const d=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_control').at(-1));assert.equal(d.pad,key);assert.equal(d.action,'enable');
    await page.getByRole('combobox',{name:'Figure '+label+' fade time',exact:true}).selectOption('2');assert.equal(await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_timing').at(-1).pad),key);
    assert.equal(await figure.getByRole('combobox',{name:'Figure kick effect',exact:true}).locator('option[value="'+key+'"]').count(),0);
   }
   const zoom=page.getByRole('combobox',{name:'Figure Infinite Zoom hit length',exact:true}),twitch=page.getByRole('combobox',{name:'Figure Twitch hit length',exact:true});await zoom.selectOption('4');await twitch.selectOption('0.125');assert.equal(await zoom.inputValue(),'4');assert.equal(await twitch.inputValue(),'0.125');
   await page.getByRole('button',{name:'Figure Infinite Zoom',exact:true}).click();let cmd=await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_fire').at(-1));assert.deepEqual(cmd,{cmd:'rack_fire',epoch:fixture.catalog.epoch,row:'figure',pad:'infinite_zoom'});
   await page.getByRole('button',{name:'Figure Low Rez',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>commands.filter(c=>c.cmd==='rack_fire').at(-1).pad),'low_rez');
   const lut=page.getByRole('slider',{name:'Figure LUT amount',exact:true});await lut.fill('0.56');await page.waitForTimeout(100);cmd=await page.evaluate(()=>commands.filter(c=>c.cmd==='effect_color').at(-1));assert.equal(cmd.amount,.56);assert.deepEqual(cmd.bindings,fixture.catalog.effect_rack.rows.find(r=>r.id==='figure').lut);
   await page.getByRole('button',{name:'Figure pattern controls',exact:true}).click();for(const [voice,key] of [['kick','twitch'],['snare','infinite_zoom']])await page.getByRole('combobox',{name:'Figure '+voice+' effect',exact:true}).selectOption(key);
   assert.equal(await page.getByRole('combobox',{name:'Stage kick effect',exact:true}).locator('option[value="distort"]').count(),0);
   await page.getByRole('button',{name:'Figure pattern controls',exact:true}).click();await page.screenshot({path:path.join(__dirname,'figure-'+width+'.png')});
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight));assert(await rack.evaluate(e=>e.scrollWidth<=e.clientWidth));
   await page.evaluate(()=>{fixture.state.armed=false;socket.publish();});assert(await lut.isDisabled());assert(await zoom.isDisabled());assert(await mirror.isDisabled());
  }
  assert.deepEqual(errors,[]);console.log('PASS 639/1440/480 px: nine quick sliders only, independent hit/fade times, saved UI values, separate trigger/toggle behavior, typed commands, loop choices, keyboard, disabled states and no overflow.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
