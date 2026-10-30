const fs=require('fs'),P=require('../js/ddl_physics.js');
const L={};JSON.parse(fs.readFileSync(__dirname+'/../design/data/levels.json')).levels.forEach(l=>L[l.id]=l);
const out=JSON.parse(fs.readFileSync(process.argv[2])).map(c=>{const lv=L[c.lv];let st=P.init(lv);const res=[];
 for(const [a,p] of c.shots){const tr=[];const r=P.shoot(lv,st,a,p,c.horn,B=>tr.push(B.map(b=>[b.id,b.x,b.y,b.vx,b.vy])));st=r.state;
  res.push({trace:tr,ev:r.ev,state:st.map(b=>[b.id,b.x,b.y,b.alive,b.inHay])});}
 return {res,solved:P.solved(st)};});
fs.writeFileSync(process.argv[3],JSON.stringify(out));
