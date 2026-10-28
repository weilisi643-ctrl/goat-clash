// v2 过关率复测：σA=2° σP=0.03；主指标=自适应+力度吸附；对照=盲目复读（同上次）
const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..');
const P=require(path.join(root,'js/ddl_physics.js'));
const DATA=JSON.parse(fs.readFileSync(path.join(root,'design/data/levels.v2.json'),'utf8'));
const TARGETS={1:0.70,2:0.35,3:0.35,4:0.35,5:0.35,6:0.40,7:0.20,8:0.35,9:0.20,10:0.20};
function gauss(r,sd){const u=1-r(),v=r();return Math.sqrt(-2*Math.log(Math.max(u,1e-12)))*Math.cos(2*Math.PI*v)*sd;}
function powerNotch(p,snap=0.05){const ns=[0.5,0.6,0.7,0.8,0.9,1.0];let best=p,bd=1;for(const n of ns){const d=Math.abs(p-n);if(d<=snap&&d<bd){bd=d;best=n;}}return best;}
function angleMagnet(lv,st,aim){
  if(lv.assist&&lv.assist.angleMagnet===false) return aim;
  const sx=lv.start.x,sy=lv.start.y; let bestA=null,bestD=4;
  const consider=(x,y)=>{let a=Math.atan2(sy-y,x-sx)*180/Math.PI; if(a<0)a+=360; const d=Math.abs(((aim-a+180)%360)-180); if(d<=3&&d<bestD){bestD=d;bestA=a;}};
  for(const b of st){ if(!b.alive||b.inHay||b.static||b.type==='rock') continue; consider(b.x,b.y); }
  for(const h of lv.hays) consider(h.x,h.y);
  return bestA!=null?bestA:aim;
}
function rng(seed){let s=seed>>>0; return ()=>{s=(s*1664525+1013904223)>>>0; return s/4294967296;};}
function clear(st){return P.solved(st)&&P.targetsAlive(st);}
function blind(lv,N,opts){
  let c=0;
  for(let i=0;i<N;i++){
    const r=rng(i*997+lv.id*13); let st=P.init(lv);
    for(const s of lv.solution){
      let a=s.angle+gauss(r,2), p=Math.max(0.05,Math.min(1,s.power+gauss(r,0.03)));
      if(opts.powerSnap) p=powerNotch(p);
      if(opts.angleMagnet) a=angleMagnet(lv,st,a);
      st=P.shoot(lv,st,a,p,lv.horn||'curl').state;
    }
    if(clear(st)) c++;
  }
  return c/N;
}
function adapt(lv,N,opts){
  // 文档主指标：按参考解意图顶，每步噪声；力度吸附；未过关且有次数则继续后续参考步（或朝剩余目标）
  let c=0; const sol=lv.solution;
  for(let i=0;i<N;i++){
    const r=rng(i*991+lv.id*17); let st=P.init(lv), si=0, shots=0;
    while(!clear(st)&&shots<lv.maxShots){
      let ba,bp;
      if(si<sol.length){ba=sol[si].angle; bp=sol[si].power;}
      else {
        const tgt=st.find(b=>b.target&&!b.inHay&&b.alive); if(!tgt) break;
        const sx=lv.start.x,sy=lv.start.y; ba=((Math.atan2(-(tgt.y-sy),tgt.x-sx)*180/Math.PI)+360)%360; bp=0.85;
      }
      let a=ba+gauss(r,2), p=Math.max(0.05,Math.min(1,bp+gauss(r,0.03)));
      if(opts.powerSnap) p=powerNotch(p);
      if(opts.angleMagnet) a=angleMagnet(lv,st,a);
      st=P.shoot(lv,st,a,p,lv.horn||'curl').state;
      shots++; si++;
    }
    if(clear(st)) c++;
  }
  return c/N;
}
const N=400;
console.log('lv | target | adapt+pSnap | OK? | blind+pSnap | blind(no assist) | angleMagnet');
const rows=[];
for(const lv of DATA.levels){
  const t=TARGETS[lv.id];
  const a=adapt(lv,N,{powerSnap:true,angleMagnet:false}); // 文档 4.1 主指标：自适应+力度吸附
  const aM=adapt(lv,N,{powerSnap:true,angleMagnet:true}); // 对照：再开物件磁吸
  const b=blind(lv,N,{powerSnap:true,angleMagnet:false});
  const b0=blind(lv,N,{powerSnap:false,angleMagnet:false});
  const ok=a>=t-0.001;
  console.log(`L${lv.id} ${lv.name} | ${t.toFixed(2)} | ${a.toFixed(3)} | ${ok?'OK':'MISS'} | ${b.toFixed(3)} | ${b0.toFixed(3)} | adapt+magnet=${aM.toFixed(3)} assist=${JSON.stringify(lv.assist)}`);
  rows.push({id:lv.id,name:lv.name,target:t,adapt_powerSnap:a,ok,blind_powerSnap:b,blind:b0,adapt_both:aM});
}
fs.writeFileSync('/tmp/ddl_v2_rates.json',JSON.stringify(rows,null,2));
console.log('miss',rows.filter(r=>!r.ok).map(r=>r.id));
