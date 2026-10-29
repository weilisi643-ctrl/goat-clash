# p16：部件头/尾展示性旋转 + 关节补片。①rot≈0 部件合成 vs 整图逐像素 ②头/尾 -15,-3,0,+3,+15 网格（各姿态）③游戏内对战截图（ART.rot 覆盖）④补片帧/透明度表
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops,ImageDraw
import subprocess,time,os,json,base64,io
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
GM="(function(){for(var k in cache){if(k.indexOf('/js/goat.js')>=0)return cache[k].exports}})()"
REND="""(a)=>{var G="""+GM+""";var c=document.createElement('canvas');c.width=a.w||900;c.height=a.h||900;var x=c.getContext('2d');if(a.bg)x.fillStyle=a.bg,x.fillRect(0,0,c.width,c.height);
G.drawGoatArt(x,a.x||450,a.y||560,a.s,{wool:a.wool,woolColor:a.col,horn:a.horn||'curl'},1,0,a.pose,a.rot);return c.toDataURL('image/png')}"""
def img(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
POSES=['idle','jump','clash'];ANG=[-15,-3,0,3,15];out={'equiv':{},'patch_rule':{}}
port=8870;srv=subprocess.Popen(['python3','-m','http.server',str(port)],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%port);time.sleep(3);pg.evaluate(SEED+"window.G=GAME;G.setNow(Date.UTC(2026,10,3,4,0));__run(500)")
  def R_(**a):
    for _ in range(40):  # 部件惰性加载：渲染两次直到就绪
      im=img(pg.evaluate(REND,a));pg.wait_for_timeout(50)
      if not a.get('rot') or pg.evaluate("(function(){var G="+GM+";return !G.ART.loadingP||!Object.keys(G.ART.loadingP).length})()"): im=img(pg.evaluate(REND,a));break
    return im
  for pose in POSES:
    for wool in ['fluffy','short','spots','cloud']:
      A=dict(pose=pose,wool=wool,col='#ffffff',s=7,bg='#3cc83c')
      w=R_(**A);pr=R_(**A,rot={'head':1e-6,'tail':1e-6})
      diff=ImageChops.difference(w.convert('RGB'),pr.convert('RGB')).convert('L');n=sum(1 for v in diff.getdata() if v>8)
      out['equiv']['%s_%s'%(pose,wool)]=n
  # 补片规则表
  out['patch_rule']=pg.evaluate("(function(){var G="+GM+";var r={};[-15,-12.6,-10,-7.6,-5,-3,-1,-0.5,0,0.5,1,2,3,5,7.5,10,12.5,15].forEach(function(cd){var a=-cd;var aa=Math.abs(a);r[cd]=aa<1?null:{frame:(a>0?'+':'-')+(aa<=7.5?5:aa<=12.5?10:15),alpha:Math.max(0,Math.min(1,(aa-1)/4))}});return r})()")
  for which in ['head','tail']:
    for pose in POSES:
      tiles=[]
      for a in ANG:
        im=R_(pose=pose,wool='fluffy',col='#ffffff',s=5,bg='#8fb8de',w=700,h=600,x=350,y=380,rot={which:a})
        dr=ImageDraw.Draw(im);dr.text((10,10),'%s %+d deg (canvas)'%(which,a),fill='black');tiles.append(im)
      g=Image.new('RGB',(700*len(tiles),600),'white')
      for i,t in enumerate(tiles): g.paste(t,(700*i,0))
      g.save(d+'p16_%s_%s.png'%(which,pose))
  # 开发对照：全尺寸补片帧（_320 帧无 alpha 被跳过）验证补片规则
  pg.evaluate("(function(){var G="+GM+";G.ART.patchFull=true;Object.keys(G.ART.imgs).forEach(function(k){if(k.indexOf('_patch/')>=0)delete G.ART.imgs[k]})})()")
  for which in ['head','tail']:
    tiles=[]
    for a in ANG:
      im=R_(pose='idle',wool='fluffy',col='#ffffff',s=5,bg='#8fb8de',w=700,h=600,x=350,y=380,rot={which:a});ImageDraw.Draw(im).text((10,10),'%s %+d (full-size patch)'%(which,a),fill='black');tiles.append(im)
    g=Image.new('RGB',(700*len(tiles),600),'white')
    for i,t_ in enumerate(tiles): g.paste(t_,(700*i,0))
    g.save(d+'p16_%s_idle_fullpatch.png'%which)
  pg.evaluate("(function(){var G="+GM+";G.ART.patchFull=false;Object.keys(G.ART.imgs).forEach(function(k){if(k.indexOf('_patch/')>=0)delete G.ART.imgs[k]})})()")
  # 游戏内：对战屏，ART.rot 覆盖（只渲染）
  for tag,rot in [('0',None),('head+15',{'head':15}),('head-15',{'head':-15}),('head+3',{'head':3}),('head-3',{'head':-3}),('tail+15',{'tail':15}),('tail-15',{'tail':-15}),('tail+3',{'tail':3}),('tail-3',{'tail':-3})]:
    pg.evaluate("(r)=>{var G="+GM+";G.ART.rot=r;G2=window.G;G2.st.scene='custom';__run(100);G2.startMatch&&G2.startMatch();__run(400)}",rot)
    pg.wait_for_timeout(300);pg.evaluate("__run(50)");pg.wait_for_timeout(200);pg.evaluate("__run(50)")
    pg.screenshot(path=d+'p16_battle_%s.png'%tag)
  pg.evaluate("(function(){var G="+GM+";G.ART.rot=null})()")
  out['errors']=errs;out['art_errors']=pg.evaluate("(function(){var G="+GM+";return G.ART.errors})()")
  br.close()
srv.kill()
ims=[Image.open(d+'p16_battle_%s.png'%t) for t in ['0','head+15','head-15','tail+15','tail-15']]
o=Image.new('RGB',(375*5+40,667),'#2F3727')
for i,t in enumerate(ims): o.paste(t,(i*385,0))
o.save(d+'p16_battle_overview.png')
json.dump(out,open(R+'/docs/p16_parts.json','w'),ensure_ascii=False,indent=1);print(json.dumps(out,ensure_ascii=False)[:1500])
