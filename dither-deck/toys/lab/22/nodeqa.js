const fs = require("fs");
const html = fs.readFileSync("C:/Users/User/Documents/0000000/dither-deck/toys/22.html","utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
let src = m[1];
src = src.slice(0, src.indexOf('const rail=document.getElementById("rail");'));
// DOM stubs
const S=680;
const px = new Uint8ClampedArray(S*S*4);
const ctx = { createImageData:(w,h)=>({data:px,width:w,height:h}), putImageData(){} };
const scene = { width:0, height:0, getContext:()=>ctx };
const documentStub = { getElementById:(id)=> id==="scene"?scene:null };
const window = {};
eval("(function(){" + src.replace(/document\.getElementById/g,"documentStub.getElementById") + "; globalThis.__setK=(t)=>{k=t;apply();}; globalThis.__img=img; globalThis.__N=N; })()");
const N = globalThis.__N, img = globalThis.__img;
function bw(){ const d=img.data; const a=new Uint8Array(N); let c=0;
  for(let i=0;i<N;i++){ if(d[i*4]===0){a[i]=1;c++;} } return {a,cov:c/N}; }
let prev=null, worst=0, worstk=0, inks=[];
let times=[];
for(let i=0;i<=200;i++){
  const t0=process.hrtime.bigint();
  globalThis.__setK(i/200);
  times.push(Number(process.hrtime.bigint()-t0)/1e6);
  const {a,cov}=bw(); inks.push(cov);
  if(prev){ let f=0; for(let j=0;j<N;j++) if(a[j]!==prev[j]) f++;
    if(f/N>worst){worst=f/N;worstk=i/200;} }
  prev=a;
}
console.log("ink  min/max:", Math.min(...inks).toFixed(4), Math.max(...inks).toFixed(4));
console.log("worst flip/step:", (worst*100).toFixed(2)+"%", "at k="+worstk);
console.log("apply() ms avg/max:", (times.reduce((a,b)=>a+b)/times.length).toFixed(1), Math.max(...times).toFixed(1));
