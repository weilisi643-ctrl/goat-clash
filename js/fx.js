// 画面特效（只读物理事件，绝不写回物理状态；自带 RNG，不消耗 Math.random，保证回归一致）
var N=240,P=[],seed=9,now=0,shake=0,shakeT=0,flash=0,freezeT=0,frozen=null,rings=[],lines=[],sq={};
for(var i=0;i<N;i++)P.push({a:0});
function r(){seed=(seed*16807)%2147483647;return seed/2147483647;}
var K={dust:['#d8c9a8',3,0.6,-30],grass:['#5fae3c',2.5,0.9,120],spark:['#fff3a0',2,0.35,0],wool:['#ffffff',4,1.2,40],conf:[null,4,2.2,60]};
var CONF=['#ff5a5a','#ffd23f','#4cc9f0','#7bd36b','#c77dff'];
function emit(type,x,y,n,sp,dir,spread,col){for(var j=0;j<P.length&&n>0;j++){var p=P[j];if(p.a>0)continue;n--;
 var k=K[type],a=(dir==null?r()*6.283:dir+(r()-.5)*(spread||1)),v=sp*(0.4+r()*0.8);
 p.a=p.l=k[2]*(0.6+r()*0.6);p.x=x;p.y=y;p.vx=Math.cos(a)*v;p.vy=Math.sin(a)*v;p.g=k[3];p.s=k[1]*(0.6+r()*0.8);
 p.c=col||k[0]||CONF[(r()*5)|0];p.t=type;p.rot=r()*6;}}
function ev(name,o){o=o||{};
 if(name==='jump'){emit('dust',o.x,o.y,8,60,Math.PI,2.4);sq[o.id]={k:'stretch',t:now};}
 else if(name==='land'){emit('dust',o.x,o.y,10,80,-Math.PI/2,2.8);emit('grass',o.x,o.y,5,90,-Math.PI/2,1.6);sq[o.id]={k:'squash',t:now};}
 else if(name==='clash'){var pw=Math.min(1,(o.d||0)/30);freezeT=now+60+40*pw;frozen=o.snap;shake=4+6*pw;shakeT=now;flash=0.55+0.35*pw;
  rings.push({x:o.x,y:o.y,t:now});for(var i=0;i<10;i++)lines.push({x:o.x,y:o.y,a:r()*6.283,t:now});
  emit('spark',o.x,o.y,14+(pw*10|0),260);emit('wool',o.x,o.y,8,120,null,0,o.wool);emit('dust',o.x,o.y+40,8,90,-Math.PI/2,2.5);}
 else if(name==='ddl'){var t=o.k;if(t==='wall')emit('dust',o.x,o.y,5,60);else if(t==='break'){emit('spark',o.x,o.y,10,200);emit('dust',o.x,o.y,12,120);shake=4;shakeT=now;}
  else if(t==='hay'){emit('grass',o.x,o.y,14,110,-Math.PI/2,3);rings.push({x:o.x,y:o.y,t:now});}else if(t==='rock'){emit('spark',o.x,o.y,6,150);}}
 else if(name==='win'){for(var c=0;c<3;c++)emit('conf',o.x+(c-1)*80,o.y,25,220,-Math.PI/2,1.6);}}
function step(ms){var dt=Math.min(0.05,Math.max(0,(ms-now)/1000));now=ms;
 for(var i=0;i<N;i++){var p=P[i];if(p.a<=0)continue;p.a-=dt;p.vy+=p.g*dt;p.vx*=1-1.5*dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.rot+=dt*8;}
 rings=rings.filter(function(g){return now-g.t<350;});lines=lines.filter(function(l){return now-l.t<220;});flash=Math.max(0,flash-dt*5);}
function frozenView(){return now<freezeT?frozen:null;}
function shakeOff(){var e=now-shakeT,a=e<220?shake*(1-e/220):0;return a?[(r()-.5)*2*a,(r()-.5)*2*a]:[0,0];}
function squash(id,vy){var s=sq[id],e=s?now-s.t:1e9;
 if(s&&s.k==='squash'&&e<160){var k=Math.sin(e/160*Math.PI)*0.18;return [1+k,1-k];}
 if(s&&s.k==='stretch'&&e<140){var k2=Math.sin(e/140*Math.PI)*0.14;return [1-k2,1+k2];}
 var v=Math.min(0.08,Math.abs(vy||0)*0.012);return [1-v/2,1+v];}
function draw(ctx,W,H){
 rings.forEach(function(g){var e=(now-g.t)/350;ctx.strokeStyle='rgba(255,255,255,'+(1-e)+')';ctx.lineWidth=4*(1-e)+1;ctx.beginPath();ctx.arc(g.x,g.y,10+70*e,0,7);ctx.stroke();});
 lines.forEach(function(l){var e=(now-l.t)/220,r0=20+60*e,r1=r0+24*(1-e);ctx.strokeStyle='rgba(255,255,255,'+(0.9*(1-e))+')';ctx.lineWidth=2;ctx.beginPath();
  ctx.moveTo(l.x+Math.cos(l.a)*r0,l.y+Math.sin(l.a)*r0);ctx.lineTo(l.x+Math.cos(l.a)*r1,l.y+Math.sin(l.a)*r1);ctx.stroke();});
 for(var i=0;i<N;i++){var p=P[i];if(p.a<=0)continue;ctx.globalAlpha=Math.min(1,p.a/p.l*1.5);ctx.fillStyle=p.c;
  if(p.t==='conf'||p.t==='grass'){ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot);ctx.fillRect(-p.s,-p.s/3,p.s*2,p.s*0.7);ctx.restore();}
  else{ctx.beginPath();ctx.arc(p.x,p.y,p.s,0,7);ctx.fill();}}
 ctx.globalAlpha=1;
 if(flash>0){ctx.fillStyle='rgba(255,255,255,'+Math.min(1,flash)+')';ctx.fillRect(-20,-20,W+40,H+40);}}
function alive(){var c=0;for(var i=0;i<N;i++)if(P[i].a>0)c++;return c;}
module.exports={ev:ev,step:step,draw:draw,frozenView:frozenView,shakeOff:shakeOff,squash:squash,alive:alive,enabled:true};
