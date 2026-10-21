const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const html=fs.readFileSync(__dirname+'/status.html','utf8');
const section=html.slice(html.indexOf('  // ── lock ──'),html.indexOf('  btn.onclick=()=>locked?'));
const listeners={};const ctx={locked:true,pressureReady:false,unlocks:0,document:{addEventListener:(k,f)=>listeners[k]=f},eat(){},unlock(){ctx.locked=false;ctx.unlocks++;}};
const pressure=section.slice(section.indexOf("  document.addEventListener('heartpressure'"));vm.runInNewContext(pressure,ctx);
const fire=stage=>listeners.heartpressure({detail:{stage}});
fire(1);assert.equal(ctx.unlocks,0,'initial latch press cannot release');fire(0);assert.equal(ctx.unlocks,0,'lifting cannot release');fire(0);assert.equal(ctx.unlocks,0);fire(1);assert.equal(ctx.unlocks,1,'next physical press releases');
const eat=section.slice(section.indexOf('  const eat='),section.indexOf('  const eatKey='));assert(!eat.includes('unlock()'),'tap-to-click mouse events cannot release');
console.log('PAD pressure: latch press, lift, and next physical press passed.');
