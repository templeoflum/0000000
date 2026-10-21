// Resume must bridge only an explicit, connected resume command.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../engine/status.html','utf8');
const fn=html.slice(html.indexOf('function cmd(o){'),html.indexOf('function paintLiveState(s){'));
const posts=[],sent=[];
const context={ws:{readyState:1,send:s=>sent.push(JSON.parse(s))},window:{webkit:{messageHandlers:{heartPointer:{postMessage:s=>posts.push(s)}}}},document:{getElementById:()=>({classList:{add(){}}})},Date};
vm.createContext(context);vm.runInContext(fn,context);
context.cmd({cmd:'hold',on:true});assert.equal(posts.length,0);
context.cmd({cmd:'hold',on:false});assert.deepEqual(posts,['resume']);
context.ws.readyState=3;context.cmd({cmd:'hold',on:false});assert.equal(posts.length,1);
context.ws.readyState=1;context.window={};context.cmd({cmd:'hold',on:false});
console.log('Resume bridge checks passed: explicit resume only, disconnected guard, browser fallback.');
