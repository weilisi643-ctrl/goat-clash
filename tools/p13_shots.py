# v2.3 美术修复前后对比：pre=bae2bca / post=当前。①idle/jump/clash 整羊绿底/洋红底合成（放大头部、下巴）②对战、擂主截图 ③绿边/针孔像素检测
from playwright.sync_api import sync_playwright
from PIL import Image,ImageFilter,ImageChops,ImageDraw
import subprocess,time,os,json,base64,io
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
ROOTS=json.loads(os.environ['ROOTS']) if os.environ.get('ROOTS') else [('pre','/tmp/wt_pre'),('post',R)]
INIT="""try{localStorage.setItem("tutorialDone","true")}catch(e){};window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
POSES=['idle','jump','clash'];WOOLS=['fluffy','short','spots','cloud'];COLS=['#ffffff','#333333']
REND2_SUFFIX=1
REND="""(a)=>{var G=null;for(var k in cache){if(k.indexOf('/js/goat.js')>=0)G=cache[k].exports}
var c=document.createElement('canvas');c.width=900;c.height=900;var x=c.getContext('2d');if(a.bg)x.fillStyle=a.bg,x.fillRect(0,0,900,900);
G.drawGoatArt(x,450,560,a.s,{wool:a.wool,woolColor:a.col,horn:'curl'},1,0,a.pose);return c.toDataURL('image/png')}"""
REND2=REND.replace("a.pose)","a.pose,{head:1e-6,tail:1e-6})")
def img(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
COORD=[];COORDS={}
PARTS_ORDER=None
def detect(tr,gr):
  """tr: 透明底渲染；gr: 绿底(#3cc83c)渲染。返回
  fringe=羊内部(距任一透明像素>7px)合成后呈绿色的像素（半透明渗边/针孔）；
  holes=轮廓内 alpha=0 的小封闭孔(<400px，排除角圈等大镂空)像素；tint=图层自身偏绿像素"""
  a=tr.split()[3];m=a.point(lambda v:255 if v>0 else 0)
  f=m.copy();ImageDraw.floodfill(f,(0,0),128)
  inner=m.filter(ImageFilter.MinFilter(15))  # 距任何透明像素 >7px（s=7 时约为 _320 源图 1px）的羊内部：排除外缘/镂空处正常的半透明抗锯齿带
  gp=gr.convert('RGB').load();tp=tr.load();ip=inner.load();w,h=tr.size;fr=t=0;COORD.clear()
  for y in range(h):
    for x in range(w):
      r,G,b,al=tp[x,y]
      if al>8 and G>r+12 and G>b+12: t+=1
      if ip[x,y]:
        r2,G2,b2=gp[x,y]
        if G2>r2+30 and G2>b2+30: fr+=1;COORD.append(('green',x,y))
  # 小孔：内部 alpha=0 连通块
  hp=f.load();seen=set();holes=0
  for y in range(h):
    for x in range(w):
      if hp[x,y]==0 and (x,y) not in seen:
        st=[(x,y)];seen.add((x,y));n=0;comp=[]
        while st:
          cx,cy=st.pop();n+=1;comp.append((cx,cy))
          for nx,ny in((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
            if 0<=nx<w and 0<=ny<h and hp[nx,ny]==0 and (nx,ny) not in seen: seen.add((nx,ny));st.append((nx,ny))
        if n<400: holes+=n;COORD.extend(('hole',px,py) for (px,py) in comp)
  return fr,holes,t
res={};HB={};BEARD={}
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for i,(tag,root) in enumerate(ROOTS):
    port=8850+i;srv=subprocess.Popen(['python3','-m','http.server',str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
    pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%port);time.sleep(3)
    pg.evaluate(SEED+"window.G=GAME;G.setNow(Date.UTC(2026,10,3,4,0));__run(500)")
    for pose in POSES:
      for wool in WOOLS:
        for col in COLS:
          A={'pose':pose,'wool':wool,'col':col,'s':7}
          tr=img(pg.evaluate(REND,dict(A,bg=None)));gr=img(pg.evaluate(REND,dict(A,bg='#3cc83c')))
          res.setdefault(tag,{})['%s_%s_%s'%(pose,wool,col)]=detect(tr,gr)
          if tag=='post' and COORD:
            order=pg.evaluate("(function(){for(var k in cache){if(k.indexOf('/js/goat.js')>=0)return cache[k].exports.ART.parts.part_draw_order}})()")
            masks=[]
            for part in order:
              pg.evaluate("(n)=>{for(var k in cache){if(k.indexOf('/js/goat.js')>=0)cache[k].exports.ART.onlyPart=n}}",part)
              for _ in range(30):
                im=img(pg.evaluate(REND2,dict(A,bg=None)))
                if pg.evaluate("(function(){for(var k in cache){if(k.indexOf('/js/goat.js')>=0){var L=cache[k].exports.ART.loadingP;return !L||!Object.keys(L).length}}})()"): im=img(pg.evaluate(REND2,dict(A,bg=None)));break
                pg.wait_for_timeout(50)
              masks.append((part,im.split()[3].load()))
            pg.evaluate("(function(){for(var k in cache){if(k.indexOf('/js/goat.js')>=0)cache[k].exports.ART.onlyPart=null}})()")
            sc=7*0.1*1024/320*320/1024  # 画布px→art px：size=cw*0.1*s
            for (kind,x,y) in COORD:
              own='none'
              for part,ml in masks:
                if ml[x,y]>0: own=part
              ax_=round(511+(x-450)/(0.1*7),1);ay_=round(995+(y-(560+40*7))/(0.1*7),1)
              COORDS.setdefault(wool,{}).setdefault(own,{}).setdefault(pose,[]).append({'type':kind,'bg_wool':col,'canvas':[x,y],'art_px':[ax_,ay_]})
          if wool=='fluffy' and pose not in HB:
            bx=tr.getbbox();HB[pose]=(bx[2]-330,bx[1]+20,bx[2],bx[1]+350)  # 头部+下巴胡子
          if wool=='fluffy': tr.save('/tmp/p13tr_%s_%s_%s.png'%(pose,col[1:],tag))
          if wool=='fluffy': gr.save('/tmp/p13_%s_%s_%s.png'%(pose,col[1:],tag))
    # 胡子随羊毛换色：data.woolColors 各色 idle/clash 头部
    WC=pg.evaluate("(function(){for(var k in cache){if(k.indexOf('/js/data.js')>=0)return cache[k].exports.woolColors}})()")
    for pose in ['idle','clash']:
      for j,col in enumerate(WC):
        im=img(pg.evaluate(REND,{'pose':pose,'wool':'fluffy','col':col,'s':7,'bg':'#8fb8de'}));BEARD.setdefault(tag,{})[(pose,j)]=im
    # 对战（撞击瞬间）与擂主
    pg.evaluate("G.startMatch&&G.startMatch();__run(800);G.B.meter=0.8;G.jump()")
    for _ in range(200):
      if pg.evaluate("G.B.phase==='result'||G.B.clashT>0"): break
      pg.evaluate("__run(1000/60)")
    pg.screenshot(path=d+'p13_battle_%s.png'%tag)
    pg.evaluate("G.openArena();G.st.scene='faction';__run(300);G.chooseFaction('east');__run(800)");pg.screenshot(path=d+'p13_arena_%s.png'%tag)
    print(tag,errs);pg.close();srv.kill()
  br.close()
# 放大对比：整羊 + 头部/下巴 3x
for pose in POSES:
  for col in ['ffffff','333333']:
    rows=[]
    for tag,_ in ROOTS:
      im=Image.open('/tmp/p13_%s_%s_%s.png'%(pose,col,tag)).convert('RGB')
      bb=HB[pose]
      head=im.crop(bb).resize((600,600),Image.NEAREST)  # 头部(耳/眼/下巴胡子) 放大
      row=Image.new('RGB',(900+600,900),'white');row.paste(im,(0,0));row.paste(head,(900,150));rows.append(row)
    c=Image.new('RGB',(1500,1810),'white');c.paste(rows[0],(0,0));c.paste(rows[1],(0,910))
    c.save(d+'p13_%s_%s_compare.png'%(pose,col))
# 胡子换色对比：上=pre 下=post，每行 woolColors 各色头部放大
for pose in ['idle','clash']:
  n=len(BEARD['post'])//2;c=Image.new('RGB',(300*n,610),'white')
  for r,(tag,_) in enumerate(ROOTS):
    for j in range(n): c.paste(BEARD[tag][(pose,j)].convert('RGB').crop(HB[pose]).resize((300,300)),(j*300,r*310))
  c.save(d+'p13_beard_colors_%s_compare.png'%pose)
for n in ['battle','arena']:
  c=Image.new('RGB',(760,667),'white')
  for i,(t,_) in enumerate(ROOTS): c.paste(Image.open(d+'p13_%s_%s.png'%(n,t)),(i*385,0))
  c.save(d+'p13_%s_compare.png'%n)
summ={t:{'fringe_green':sum(v[0] for v in r.values()),'pinholes':sum(v[1] for v in r.values()),'green_tint':sum(v[2] for v in r.values())} for t,r in res.items()}
json.dump({'summary':summ,'detail':res},open(R+'/docs/p13_green_fringe.json','w'),indent=1)
json.dump({'note':'post 渲染中透绿(green)/小孔(hole)像素：wool(皮肤)→part(部件，按 parts.json part_draw_order 取最上层覆盖该像素的部件；none=无部件覆盖)→pose；canvas=900×900 渲染坐标(s=7,x=450,footY=840)；art_px=1152×1024 原图坐标；bg_wool=当次羊毛色','counts':{w:{p:{po:len(v) for po,v in d.items()} for p,d in pp.items()} for w,pp in COORDS.items()},'coords':COORDS},open(R+'/docs/p13_green_coords.json','w'),ensure_ascii=False);print(json.dumps(summ))
