const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..');
const C=JSON.parse(fs.readFileSync(path.join(root,'design/data/champions.v2.json')));
const D=require(path.join(root,'js/data.js'));
const ANG=['low','mid','high'];
const STANCE={low_charge:'low',low_sweep:'low',mid_ram:'mid',mid_feint:'mid',high_leap:'high',high_rear:'high'};
function st(look){const w=D.wools.find(x=>x.id===look.wool),h=D.horns.find(x=>x.id===look.horn);return{hp:100+w.hp,spd:w.spd,pow:h.pow,win:h.win};}
function clashOnce(ps,es,ai,pAng,eAng,timing,r){
  let pp=20+ps.pow+timing*30+ps.spd*0.3;
  const eT=r()<ai.timingHit?1:r()*0.7;
  let ep=20+es.pow+ai.powBonus+eT*30+es.spd*0.3;
  if(ps.win===eAng)pp*=1.3; if(es.win===pAng)ep*=1.3;
  const d=Math.round(Math.abs(pp-ep))+8;
  return pp>=ep?{who:0,d}:{who:1,d};
}
function gauss(r,sd){const u=1-r(),v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)*sd;}
function stageWin(cfg,stage,look,perfect,N){
  const sc=cfg.stages[stage-1],ai=sc.ai; const es0=st(cfg.look); const eMax=es0.hp+(ai.hpBonus||0);
  const ps=st(look); let wins=0;
  for(let i=0;i<N;i++){
    const r=Math.random; let bw=[0,0];
    while(Math.max(bw[0],bw[1])<2){
      let php=ps.hp,ehp=eMax;
      while(php>0&&ehp>0){
        const eang=STANCE[cfg.stancePref[Math.floor(r()*cfg.stancePref.length)]];
        let pang=perfect?(ANG.find(a=>a!==es0.win)||'mid'):(r()<0.7?(ANG.find(a=>a!==es0.win)||'mid'):ANG[Math.floor(r()*3)]);
        let timing=perfect?1:Math.max(0,1-Math.abs((0.8+gauss(r,0.15))-0.8)/0.8);
        const c=clashOnce(ps,es0,ai,pang,eang,timing,r);
        if(c.who===0)ehp-=c.d; else php-=c.d;
      }
      if(php>0)bw[0]++; else bw[1]++;
    }
    if(bw[0]===2)wins++;
  }
  return wins/N;
}
const N=2500;
console.log('day name | s1N s2N clearN | s2P | docClear');
for(const d of C.days){
  const horns=d.stages[1].allowedHorns||['curl'];
  let s1=0,s2=0,s2p=0;
  for(const h of horns){
    s1+=stageWin(d,1,{wool:'fluffy',horn:'curl'},false,N);
    s2+=stageWin(d,2,{wool:'fluffy',horn:h},false,N);
    s2p+=stageWin(d,2,{wool:'short',horn:h},true,N);
  }
  s1/=horns.length; s2/=horns.length; s2p/=horns.length;
  console.log(d.day,d.name, s1.toFixed(3), s2.toFixed(3), (s1*s2).toFixed(3), '|', s2p.toFixed(3), '| doc', d.sim.clearNormal);
}
