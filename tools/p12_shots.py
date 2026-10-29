# v2.1 对比：orig=2286c4b（纯色按钮）/ v2=5b84a85 / v21=当前；按钮、emoji 标签、擂主色调、撞击光晕；并测按钮平均亮度
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
import subprocess,time,sys,os,json
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
ROOTS=[('orig','/tmp/wt_2286c4b'),('v2','/tmp/wt_5b84a85'),('v21',R)]
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
N=['01_buttons','02_emoji_labels','03_arena_tint','04_clash_glow']
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for i,(tag,root) in enumerate(ROOTS):
    port=8820+i;srv=subprocess.Popen(['python3','-m','http.server',str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
    pg=b.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%port);time.sleep(2)
    sh=lambda n:pg.screenshot(path=d+'p12_%s_%s.png'%(n,tag))
    pg.evaluate(SEED+"G=GAME;G.setNow(Date.UTC(2026,10,3,4,0));G.openArena();G.st.scene='faction';__run(800)");sh(N[0])
    pg.evaluate("G.st.scene='custom';__run(800)");sh(N[1])
    pg.evaluate("G.chooseFaction('east');__run(800)");sh(N[2])
    pg.evaluate("G.startMatch();__run(800);G.B.meter=0.8;G.jump()")
    for _ in range(200):
      if pg.evaluate("G.B.phase==='result'"): break
      pg.evaluate("__run(1000/60)")
    pg.evaluate("__run(50)");sh(N[3]);print(tag,errs);pg.close();srv.kill()
  b.close()
for n in N:
  ims=[Image.open(d+'p12_%s_%s.png'%(n,t)) for t,_ in ROOTS];c=Image.new('RGB',(375*3+20,667),'white')
  for i,im in enumerate(ims): c.paste(im,(i*385,0))
  c.save(d+'p12_%s_compare.png'%n)
# 按钮内部平均亮度（L），排除文字：取按钮左右两侧无字区域
BOX={'01_buttons':[(26,136,60,172),(205,136,240,172),(26,322,60,358),(114,582,150,616)],'02_emoji_labels':[(20,600,40,640),(130,600,145,640),(255,600,270,640)]}
res={}
for n,bs in BOX.items():
  for t,_ in ROOTS:
    im=Image.open(d+'p12_%s_%s.png'%(n,t)).convert('L');res.setdefault(n,{})[t]=round(sum(ImageStat.Stat(im.crop(x)).mean[0] for x in bs)/len(bs),1)
print(json.dumps(res));json.dump(res,open(R+'/docs/p12_button_luma.json','w'),indent=1)
