// 用法: node tools/p6_regress.js <项目根>  —— 固定种子跑自由对战/擂主，逐帧哈希物理状态；顶顶乐参考解三星
const path=require('path'),crypto=require('crypto'),fs=require('fs');
const root=path.resolve(process.argv[2]||'.'); process.chdir(root);
let seed=12345; Math.random=function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
Date.now=()=>1793000000000;
const noop=()=>{}; const ctx=new Proxy({},{get:(o,k)=>k==='createLinearGradient'?()=>({addColorStop:noop}):k==='measureText'?()=>({width:10}):k in o?o[k]:noop,set:(o,k,v)=>(o[k]=v,true)});
let raf=null, touch=null; const mem={};
global.wx={getFileSystemManager:()=>({readFileSync:(p,e)=>fs.readFileSync(p,e)}),createCanvas:()=>({getContext:()=>ctx,width:0,height:0}),getSystemInfoSync:()=>({windowWidth:375,windowHeight:667}),onTouchStart:f=>touch=f,
 getStorageSync:k=>mem[k],setStorageSync:(k,v)=>{mem[k]=JSON.parse(JSON.stringify(v));}};
global.requestAnimationFrame=f=>raf=f;
const M=require(path.join(root,'js/main.js'));
const H=crypto.createHash('sha256'); const per=[]; let frames=0;
function snap(tag){const B=M.B;const s=JSON.stringify({tag,sc:M.st.scene,B:B&&{p:B.p,e:B.e,ph:B.phase,t:B.t,m:B.meter,w:B.wins,r:B.round,msg:B.msg,re:B.roundEnd,rv:B.reveal,ts:B.timingSum,ai:B.ai},AR:M.AR&&M.AR.last});H.update(s);frames++;return s;}
function click(label){const b=M.st.buttons.filter(x=>x.label.indexOf(label)>=0).pop(); if(!b) return false; touch({touches:[{clientX:b.x+1,clientY:b.y+1}]}); return true;}
function battle(tag,targets){let i=0,guard=0;
 while(M.st.scene==='battle'&&guard++<20000){ raf(); const B=M.B; snap(tag);
  if(B.phase==='charge'&&B.meter>=targets[i%targets.length]){M.jump();i++;}
  if(B.phase==='result'&&B.t>30){click('下一回合')||click('继续');}
 }
 return {scene:M.st.scene,wins:M.B.wins};}
const out={};
// 1) 自由对战 3 局
for(let g=0;g<3;g++){M.st.idx={wool:g%4,wc:g,horn:(g+1)%4,hc:g};M.startMatch(); const h0=frames; out['free'+g]=battle('free'+g,[0.8,0.6,0.95,0.3]); out['free'+g].frames=frames-h0;}
// 2) 擂主 第1/2场
M.setNow(Date.UTC(2026,10,3,4,0)); M.openArena(); if(M.st.scene==='faction') M.chooseFaction(null);
M.startArenaStage(1); out.arena1=battle('arena1',[0.8,0.78,0.82]); out.arena1.last=M.AR.last&&{win:M.AR.last.win,info:M.AR.last.info};
M.st.scene='arena'; M.startArenaStage(2); out.arena2=M.st.scene==='battle'?battle('arena2',[0.8]):{skipped:M.AR.msg}; out.arena2.last=M.AR.last&&{win:M.AR.last.win,info:M.AR.last.info};
out.frames=frames; out.battleHash=H.digest('hex');
// 3) 顶顶乐参考解
const DDL=M.DDL,P=DDL.P; out.ddl=DDL.DATA.levels.map(lv=>{let s=P.init(lv),ev=[];lv.solution.forEach(sh=>{const r=P.shoot(lv,s,sh.angle,sh.power,lv.horn);s=r.state;ev.push(r.ev);});
 const shots=lv.solution.length; const star=shots<=lv.stars['3']?3:shots<=lv.stars['2']?2:1; return {id:lv.id,solved:P.solved(s),shots,stars:P.solved(s)?star:0,evHash:crypto.createHash('sha256').update(JSON.stringify([ev,s])).digest('hex').slice(0,16)};});
console.log(JSON.stringify(out));
