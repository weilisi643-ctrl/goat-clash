// 用法: node tools/battle_check.js <项目根> [局数]  —— 对战统计（胜率/帧数/穿模/卡死）+ 顶顶乐 410 例与鲁棒采样的重叠/超时检测
const path=require('path'),fs=require('fs');
const root=path.resolve(process.argv[2]||'.'), N=+process.argv[3]||300; process.chdir(root);
let seed=777; Math.random=function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
let now=1793000000000; Date.now=()=>now;
const noop=()=>{}; const ctx=new Proxy({},{get:(o,k)=>k==='createLinearGradient'?()=>({addColorStop:noop}):k==='measureText'?()=>({width:10}):k in o?o[k]:noop,set:(o,k,v)=>(o[k]=v,true)});
let raf=null,touch=null; const mem={};
global.wx={getFileSystemManager:()=>({readFileSync:(p,e)=>fs.readFileSync(p,e)}),createCanvas:()=>({getContext:()=>ctx,width:0,height:0}),getSystemInfoSync:()=>({windowWidth:375,windowHeight:667}),onTouchStart:f=>touch=f,getStorageSync:k=>mem[k],setStorageSync:(k,v)=>{mem[k]=JSON.parse(JSON.stringify(v));}};
global.requestAnimationFrame=f=>raf=f;
const M=require(path.join(root,'js/main.js'));
let BP=null; try{BP=require(path.join(root,'js/battle_physics.js'));}catch(e){}
function click(l){const b=M.st.buttons.filter(x=>x.label.indexOf(l)>=0).pop();if(!b)return false;touch({touches:[{clientX:b.x+1,clientY:b.y+1}]});return true;}
const R={};
function run(tag,setup,skill){ // skill: 玩家目标蓄力点的标准差（0.8 为完美）
  let wins=0,maxF=0,stuck=0,pen=0,maxPen=0,exch=0,airF=[],dmg=[],order=0;
  for(let g=0;g<N;g++){ setup(g); let f=0,tgt=null,af=0;
    while(M.st.scene==='battle'&&f<20000){ raf(); f++; const B=M.B;
      if(B.p.x>=B.e.x) order++;
      if(BP&&B.phase==='air'){af++; const hp=BP.hornPoint(B.p,1,'jump'),he=BP.hornPoint(B.e,-1,'jump'),d=2*BP.HIT.hornR-(he[0]-hp[0]); if(d>0.5){pen++;maxPen=Math.max(maxPen,d);}}
      if(B.phase==='charge'){ if(tgt==null){let u=0;for(let i=0;i<6;i++)u+=Math.random();tgt=Math.max(0.02,Math.min(0.99,0.8+(u-3)*skill));}
        if(Math.abs(B.meter-tgt)<0.01){M.jump();tgt=null;} }
      if(B.phase==='result'&&B.t===1){exch++;airF.push(af);af=0;if(B.lastClash)dmg.push(B.lastClash.dmg);}
      if(B.phase==='result'&&B.t>30){click('下一回合')||click('继续');}
    }
    if(f>=20000) stuck++; maxF=Math.max(maxF,f);
    const w=M.B.wins; if(w[0]===2) wins++;
  }
  const avg=a=>a.length?+(a.reduce((x,y)=>x+y,0)/a.length).toFixed(2):null;
  R[tag]={games:N,winRate:+(wins/N).toFixed(3),maxFrames:maxF,stuck,exchPerGame:+(exch/N).toFixed(2),airFramesAvg:avg(airF),dmgAvg:avg(dmg),hornPenFrames:pen,maxHornPen:+maxPen.toFixed(2),crossFrames:order};
}
for(const [nm,sk] of [['free_good',0.05],['free_avg',0.15],['free_bad',0.35]]) run(nm,g=>{M.st.idx={wool:g%4,wc:g%5,horn:g%4,hc:g%5};M.startMatch();},sk);
for(const stg of [1,2]) for(const [nm,sk] of [['good',0.05],['avg',0.15]]) run('arena'+stg+'_'+nm,g=>{ for(const k in mem) delete mem[k]; now=1793000000000+g*864e5; M.setNow(now); M.openArena(); if(M.st.scene==='faction')M.chooseFaction(null);
  const sc=M.AR.champ.cfg.stages[stg-1]; if(sc.allowedHorns){const D=require(path.join(root,'js/data.js'));M.st.idx.horn=D.horns.map(h=>h.id).indexOf(sc.allowedHorns[g%sc.allowedHorns.length]);M.st.look.horn=sc.allowedHorns[g%sc.allowedHorns.length];}
  if(stg===2){M.AR.p.inChallenge=true;M.AR.p.stage1Won=true;} M.st.scene='arena'; M.startArenaStage(stg); if(M.st.scene!=='battle') throw new Error('arena start failed '+M.AR.msg); },sk);
// 顶顶乐：410 例 + 每关 200 次扰动，检测重叠深度与超时
const P=require(path.join(root,'js/ddl_physics.js'));
const L1={};JSON.parse(fs.readFileSync('design/data/levels.json')).levels.forEach(l=>L1[l.id]=l);
const L2=JSON.parse(fs.readFileSync('design/data/levels.v2.json')).levels;
let dd={shots:0,timeouts:0,maxOverlap:0,overlapFrames:0,maxSteps:0,solved410:0,nan:0};
function shot(lv,st,a,p,h){let steps=0;const r=P.shoot(lv,st,a,p,h,B=>{steps++;for(let i=0;i<B.length;i++)for(let j=i+1;j<B.length;j++){const x=B[i],y=B[j];if(!x.alive||!y.alive||x.inHay||y.inHay)continue;const o=x.r+y.r-Math.hypot(x.x-y.x,x.y-y.y);if(o>dd.maxOverlap)dd.maxOverlap=o;if(o>2)dd.overlapFrames++;}
  B.forEach(b=>{if(!isFinite(b.x)||!isFinite(b.y))dd.nan++;});});dd.shots++;dd.maxSteps=Math.max(dd.maxSteps,steps);if(steps>=480)dd.timeouts++;return r.state;}
const cases=JSON.parse(fs.readFileSync(path.join(__dirname,'ddl_cases.json')));
cases.forEach(c=>{const lv=L1[c.lv];let s=P.init(lv);c.shots.forEach(([a,p])=>s=shot(lv,s,a,p,c.horn));if(P.solved(s))dd.solved410++;});
let rs=12345;const rnd=()=>(rs=(rs*1664525+1013904223)>>>0)/4294967296;
L2.forEach(lv=>{for(let i=0;i<200;i++){let s=P.init(lv);lv.solution.forEach(h=>s=shot(lv,s,h.angle+(rnd()-.5)*20,Math.max(.05,Math.min(1,h.power+(rnd()-.5)*.4)),lv.horn||'curl'));}});
dd.maxOverlap=+dd.maxOverlap.toFixed(3); R.ddl=dd;
console.log(JSON.stringify(R,null,1));
