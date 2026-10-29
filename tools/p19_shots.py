# p19：对战页层级/首页展示台 改前后（320/375/414/1024）+ 碰撞帧角点叠加与偏差。TAG=before|after, ROOT 可指向 worktree
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
import subprocess,time,os,json,sys,io,base64
R=os.environ.get('ROOT') or os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))+'/screenshots/'
TAG=os.environ.get('TAG','after');PORT=int(os.environ.get('PORT','8883'))
INIT="""try{localStorage.setItem("tutorialDone","true")}catch(e){};window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
out={}
CAP="""(()=>{var GG=G.G;if(!GG.__orig)GG.__orig=GG.drawGoatArt;window.__cap=[];GG.drawGoatArt=function(c,x,y,s,look,face,t,pose,rot){var m=c.getTransform();window.__cap.push({m:[m.a,m.b,m.c,m.d,m.e,m.f],x:x,y:y,s:s,face:face,pose:pose||'idle'});return GG.__orig.apply(this,arguments)}})()"""
MEAS="""(()=>{var A=G.G.ART,BP=null;for(var k in cache)if(k.indexOf('battle_physics.js')>=0)BP=cache[k].exports;var dpr=1,out=[];
var cap=window.__cap.filter(function(c){return c.s===1.1});var X=G.sceneXf(G.FX.enabled?G.FX.shakeOff():[0,0]);
function ap(m,x,y){return [m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]]}
cap.slice(-2).forEach(function(c){var pm=A.poseMan[c.pose]||A.man,P=pm.poses[c.pose],ref=A.imgs['body/body_'+c.pose],cw=ref&&ref.height?pm.canvas[1]*ref.width/ref.height:pm.canvas[0],chh=pm.canvas[1];
 var sz=chh*0.1*c.s,size=cw*0.1*c.s,ax=P.anchor[0]/cw,ay=P.anchor[1]/chh,hr=P.horn_root||(A.man.poses[c.pose]||{}).horn_root;
 var lx=(hr[0]/cw-ax)*size,ly=(hr[1]/chh-ay)*sz,art=ap(c.m,c.x+c.face*lx,c.y+40*c.s+ly);
 var o=BP.hornOffset(c.pose,c.s),phys=ap(c.m,c.x+c.face*o[0],c.y+o[1]),q=[(c.x+c.face*o[0])*X.k+X.tx,(c.y+o[1])*X.k+X.ty];
 out.push({pose:c.pose,face:c.face,art:art,phys:phys,xf:q,hitR:BP.HIT.hornR*X.k,dArt:Math.hypot(art[0]-phys[0],art[1]-phys[1]),dXf:Math.hypot(q[0]-phys[0],q[1]-phys[1]),k:X.k,matK:c.m[3]})});
return {xf:X,goats:out}})()"""
srv=subprocess.Popen(['python3','-m','http.server',str(PORT)],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for W,H in [(320,568),(375,667),(414,896),(1024,768)]:
    pg=br.new_page(viewport={'width':W,'height':H});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%PORT);time.sleep(2.5)
    pg.evaluate(SEED+"window.G=GAME;G.setNow&&G.setNow(Date.UTC(2026,10,3,4,0));try{localStorage.setItem('tutorialDone','1')}catch(e){};__run(800)")
    pg.screenshot(path=d+'p19_home_%d_%s.png'%(W,TAG))
    pg.evaluate("G.startMatch();__run(600)");pg.screenshot(path=d+'p19_battle_%d_%s.png'%(W,TAG))
    # 打到碰撞帧：起跳后推进到 result 首帧
    pg.evaluate("G.B.meter=0.8;G.st.buttons.filter(function(b){return b.label.indexOf('起跳')>=0}).pop().fn&&0")
    b=pg.evaluate("(()=>{var b=G.st.buttons.filter(function(b){return b.label.indexOf('起跳')>=0}).pop();return {x:b.x+b.w/2,y:b.y+b.h/2}})()")
    pg.mouse.click(b['x'],b['y'])
    for i in range(400):
      if pg.evaluate("G.B.phase")=='result': break
      pg.evaluate("__run(1000/60)")
    pg.evaluate(CAP);pg.evaluate("__run(1000/60)")
    pg.screenshot(path=d+'p19_clash_%d_%s.png'%(W,TAG))
    info=pg.evaluate(MEAS)
    if info and TAG=='after':
      im=Image.open(d+'p19_clash_%d_%s.png'%(W,TAG)).convert('RGB');dr=ImageDraw.Draw(im)
      for g in info['goats']:
        (ax,ay),(px,py),(qx,qy)=g['art'],g['phys'],g['xf']
        dr.ellipse((ax-5,ay-5,ax+5,ay+5),outline=(0,90,255),width=2)   # 蓝圈：角贴图 horn_root（实际画布矩阵）
        dr.line((px-6,py,px+6,py),fill=(255,0,0),width=2);dr.line((px,py-6,px,py+6),fill=(255,0,0),width=2) # 红十字：物理角点经实际矩阵
        dr.rectangle((qx-3,qy-3,qx+3,qy+3),outline=(255,0,255))       # 品红方：物理角点经 G.sceneXf()
        r=g['hitR'];dr.ellipse((qx-r,qy-r,qx+r,qy+r),outline=(255,120,0))  # 橙圈：角判定半径 HIT.hornR×k
      im.save(d+'p19_clash_overlay_%d.png'%W)
    more=[]
    for n in [4,5,10]:
      pg.evaluate(CAP);pg.evaluate("__run(%f)"%(n*1000/60));m=pg.evaluate(MEAS);more+=[(g['pose'],round(g['dArt'],3),round(g['dXf'],3)) for g in m['goats']]
    out['W%d'%W]={'errors':errs,'clash':info,'more_frames':more};pg.close()
  br.close()
srv.kill();print(json.dumps(out))
