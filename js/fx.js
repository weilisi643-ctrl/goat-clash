var UI = require('./ui.js'); // 贴图加载/乘色（art/fx，按 fx.json；未就绪或失败时回退程序化绘制）
// 画面特效（只读物理事件，绝不写回物理状态；自带 RNG，不消耗 Math.random，保证回归一致）
var perf=null,BLEND=100,sk=[0,0],drawn=false,N=240,P=[],seed=9,now=0,shake=0,shakeT=0,flash=0,freezeT=0,frozen=null,rings=[],lines=[],glows=[],sq={};
for(var i=0;i<N;i++)P.push({a:0});
function r(){seed=(seed*16807)%2147483647;return seed/2147483647;}
var K={dust:['#d8c9a8',3,0.6,-30],grass:['#5fae3c',2.5,0.9,120],spark:['#fff3a0',2,0.35,0],wool:['#ffffff',4,1.2,40],conf:[null,4,2.2,60]};
var CONF=['#ff5a5a','#ffd23f','#4cc9f0','#7bd36b','#c77dff'];
function emit(type,x,y,n,sp,dir,spread,col){for(var j=0;j<P.length&&n>0;j++){var p=P[j];if(p.a>0)continue;n--;
 var k=K[type],a=(dir==null?r()*6.283:dir+(r()-.5)*(spread||1)),v=sp*(0.4+r()*0.8);
 p.a=p.l=k[2]*(0.6+r()*0.6);p.x=x;p.y=y;p.vx=Math.cos(a)*v;p.vy=Math.sin(a)*v;p.g=k[3];p.s=k[1]*(0.6+r()*0.8);
 p.c=col||k[0]||CONF[(r()*5)|0];p.t=type;p.rot=r()*6;p.v=j%3;}}
function ev(name,o){o=o||{};
 if(name==='jump'){emit('dust',o.x,o.y,8,60,Math.PI,2.4);sq[o.id]={k:'stretch',t:now};}
 else if(name==='land'){emit('dust',o.x,o.y,10,80,-Math.PI/2,2.8);emit('grass',o.x,o.y,5,90,-Math.PI/2,1.6);sq[o.id]={k:'squash',t:now};}
 else if(name==='clash'){var pw=Math.min(1,(o.d||0)/30);freezeT=now+60+40*pw;frozen=o.snap;shake=4+6*pw;shakeT=now;flash=0.55+0.35*pw;if(o.perfect){var PF=UI.TH.feedback.perfect;freezeT=now+PF.hitstopMs;shake=Math.max(PF.shake,Math.min(shake,PF.shakeMax));perf={x:o.x,y:o.y,t:freezeT};}
  rings.push({x:o.x,y:o.y,t:now});glows.push({x:o.x,y:o.y,t:now,p:pw});for(var i=0;i<10;i++)lines.push({x:o.x,y:o.y,a:r()*6.283,t:now});
  emit('spark',o.x,o.y,14+(pw*10|0),260);emit('wool',o.x,o.y,8,120,null,0,o.wool);emit('dust',o.x,o.gy,8,90,-Math.PI/2,2.5);}
 else if(name==='ddl'){var t=o.k;if(t==='wall')emit('dust',o.x,o.y,5,60);else if(t==='break'){emit('spark',o.x,o.y,10,200);emit('dust',o.x,o.y,12,120);shake=4;shakeT=now;}
  else if(t==='hay'){emit('grass',o.x,o.y,14,110,-Math.PI/2,3);rings.push({x:o.x,y:o.y,t:now});}else if(t==='rock'){emit('spark',o.x,o.y,6,150);}}
 else if(name==='win'){for(var c=0;c<3;c++)emit('conf',o.x+(c-1)*80,o.y,25,220,-Math.PI/2,1.6);}}
function step(ms){var dt=Math.min(0.05,Math.max(0,(ms-now)/1000));now=ms;
 for(var i=0;i<N;i++){var p=P[i];if(p.a<=0)continue;p.a-=dt;p.vy+=p.g*dt;p.vx*=1-1.5*dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.rot+=dt*8;}
 glows=glows.filter(function(g){return now-g.t<UI.VC.impactGlow.ms;});rings=rings.filter(function(g){return now-g.t<350;});lines=lines.filter(function(l){return now-l.t<220;});flash=Math.max(0,flash-dt*5);var e=now-shakeT,a=e<220?shake*(1-e/220):0;sk=a?[(r()-.5)*2*a,(r()-.5)*2*a]:[0,0];drawn=false;}
function lerpG(a,b,k){return{x:a.x+(b.x-a.x)*k,y:a.y+(b.y-a.y)*k,vy:b.vy};}
function view(B){ // 顿帧定格 → BLEND ms 平滑追上物理（只影响显示）
 if(!frozen)return null;if(now<freezeT)return frozen;var e=(now-freezeT)/BLEND;if(e>=1){frozen=null;return null;}
 var k=1-Math.pow(1-e,3);return{p:lerpG(frozen.p,B.p,k),e:lerpG(frozen.e,B.e,k),t:B.t,phase:B.phase};}
function perfectAnim(){ // 「完美！」：顿帧后 0.6→1.1→1.0（popMs）→ 停留 holdMs → 上浮 floatPx 并淡出 fadeMs（只显示）
 if(!perf)return null;var P=UI.TH.feedback.perfect,e=now-perf.t;if(e<0)return null;var tot=P.popMs+P.holdMs+P.fadeMs;if(e>=tot){perf=null;return null;}
 var s,a=1,dy=0;if(e<P.popMs){var k=e/P.popMs;s=k<0.6?P.from+(P.peak-P.from)*(k/0.6):P.peak+(1-P.peak)*((k-0.6)/0.4);}else s=1;
 if(e>P.popMs+P.holdMs){var f=(e-P.popMs-P.holdMs)/P.fadeMs;a=1-f;dy=-P.floatPx*f;}return{x:perf.x,y:perf.y,s:s,a:a,dy:dy};}
function frozenView(){return now<freezeT?frozen:null;}
function shakeOff(){return sk;}
function squash(id,vy){var s=sq[id],e=s?now-s.t:1e9;
 if(s&&s.k==='squash'&&e<160){var k=Math.sin(e/160*Math.PI)*0.18;return [1+k,1-k];}
 if(s&&s.k==='stretch'&&e<140){var k2=Math.sin(e/140*Math.PI)*0.14;return [1-k2,1+k2];}
 var v=Math.min(0.08,Math.abs(vy||0)*0.012);return [1-v/2,1+v];}
var T='art/fx/';['dust_0','dust_1','dust_2','grass_blade_0','grass_blade_1','grass_blade_2','spark_streak','spark_burst','wool_fluff_0','wool_fluff_1','wool_fluff_2','shockwave_ring'].forEach(function(n){UI.img(T+n+'.png');});
function dimg(ctx,im,x,y,sz,rot){ctx.save();ctx.translate(x,y);if(rot)ctx.rotate(rot);ctx.drawImage(im,-sz/2,-sz/2,sz,sz);ctx.restore();}
function drawScene(ctx){drawn=true;var ring=UI.tinted(T+'shockwave_ring.png','#fff6d0'),burst=UI.img(T+'spark_burst.png');
 var IG=UI.VC.impactGlow;if(IG.enabled)glows.forEach(function(g){var e=(now-g.t)/IG.ms;if(e>=1)return;var R=IG.radius+IG.grow*e+IG.powerRadius*g.p,A=IG.alpha*(1-e),gr=UI.grad(ctx.createRadialGradient&&ctx.createRadialGradient(g.x,g.y,0,g.x,g.y,R),[[0,'rgba(255,240,180,'+A+')'],[0.5,'rgba(255,190,80,'+(A*0.45)+')'],[1,'rgba(255,160,40,0)']]);
  ctx.save();ctx.globalCompositeOperation='lighter';if(gr){ctx.fillStyle=gr;ctx.beginPath();ctx.arc(g.x,g.y,R,0,7);ctx.fill();}
  if(burst&&e<0.6){ctx.globalAlpha=IG.burstAlpha*(1-e/0.6);dimg(ctx,burst,g.x,g.y,IG.burstSize*(1+e),g.t%6);}ctx.restore();});
 rings.forEach(function(g){var e=(now-g.t)/350;if(ring){ctx.globalAlpha=1-e;dimg(ctx,ring,g.x,g.y,256*(0.2+1.0*e)*0.6);ctx.globalAlpha=1;return;}
  ctx.strokeStyle='rgba(255,255,255,'+(1-e)+')';ctx.lineWidth=4*(1-e)+1;ctx.beginPath();ctx.arc(g.x,g.y,10+70*e,0,7);ctx.stroke();});
 lines.forEach(function(l){var e=(now-l.t)/220,r0=20+60*e,r1=r0+24*(1-e);ctx.strokeStyle='rgba(255,255,255,'+(0.9*(1-e))+')';ctx.lineWidth=2;ctx.beginPath();
  ctx.moveTo(l.x+Math.cos(l.a)*r0,l.y+Math.sin(l.a)*r0);ctx.lineTo(l.x+Math.cos(l.a)*r1,l.y+Math.sin(l.a)*r1);ctx.stroke();});
 for(var i=0;i<N;i++){var p=P[i];if(p.a<=0||(module.exports.low&&p.v))continue;var al=Math.min(1,p.a/p.l*1.5),life=1-p.a/p.l,im=null;ctx.globalAlpha=al;
  if(p.t==='dust')im=UI.tinted(T+'dust_'+Math.min(2,(life*3)|0)+'.png',p.c);
  else if(p.t==='grass')im=UI.img(T+'grass_blade_'+p.v+'.png');else if(p.t==='wool')im=UI.tinted(T+'wool_fluff_'+p.v+'.png',p.c);
  else if(p.t==='spark')im=UI.img(T+'spark_streak.png');
  if(im){if(p.t==='spark'){ctx.save();ctx.globalCompositeOperation='lighter';dimg(ctx,im,p.x,p.y,p.s*9,Math.atan2(p.vy,p.vx)+Math.PI/2);ctx.restore();}
   else dimg(ctx,im,p.x,p.y,p.t==='dust'?p.s*(6+6*life):p.t==='wool'?p.s*4:p.s*5,p.t==='dust'?0:p.rot);continue;}
  ctx.fillStyle=p.c;
  if(p.t==='conf'||p.t==='grass'){ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot);ctx.fillRect(-p.s,-p.s/3,p.s*2,p.s*0.7);ctx.restore();}
  else{ctx.beginPath();ctx.arc(p.x,p.y,p.s,0,7);ctx.fill();}}
 ctx.globalAlpha=1;}
function drawFlash(ctx,W,H){if(!drawn)drawScene(ctx);
 if(flash>0){ctx.fillStyle='rgba(255,255,255,'+Math.min(1,flash)+')';ctx.fillRect(-20,-20,W+40,H+40);}}
function alive(){var c=0;for(var i=0;i<N;i++)if(P[i].a>0)c++;return c;}
module.exports={perfectAnim:perfectAnim,ev:ev,step:step,drawScene:drawScene,drawFlash:drawFlash,view:view,frozenView:frozenView,shakeOff:shakeOff,squash:squash,alive:alive,enabled:true,low:false};
