# v10.1 验证：用游戏绘制代码测全部组合透绿/小孔（p19 游戏尺寸 s=1.342 与 p13 参考尺寸 s=7），并输出透绿坐标
# 用法：python3 tools/p22_v101_fringe.py <root> <port> <out.json>
import json,os,sys,io,base64,subprocess,time
from PIL import Image,ImageFilter,ImageDraw
from playwright.sync_api import sync_playwright
R,PORT,OUT=sys.argv[1],sys.argv[2],sys.argv[3]
INIT="try{localStorage.setItem('tutorialDone','true')}catch(e){};"
REND="""(a)=>{var G=null;for(var k in cache){if(k.indexOf('/js/goat.js')>=0)G=cache[k].exports}
var c=document.createElement('canvas');c.width=a.W;c.height=a.W;var x=c.getContext('2d');if(a.bg)x.fillStyle=a.bg,x.fillRect(0,0,a.W,a.W);
G.drawGoatArt(x,a.W/2,a.W*0.45,a.s,{wool:a.wool,woolColor:a.col,horn:'curl'},1,0,a.pose);return c.toDataURL('image/png')}"""
def img(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
def detect(tr,gr,ip_):
  a=tr.split()[3];m=a.point(lambda v:255 if v>0 else 0);f=m.copy();ImageDraw.floodfill(f,(0,0),128)
  inner=m.filter(ImageFilter.MinFilter(2*ip_+1)) if ip_>0 else m
  gp=gr.convert('RGB').load();ipx=inner.load();w,h=tr.size;pts=[]
  for y in range(h):
    for x in range(w):
      if ipx[x,y]:
        r,g,b=gp[x,y]
        if g>r+30 and g>b+30: pts.append([x,y])
  hp=f.load();seen=set();holes=0;hpts=[]
  for y in range(h):
    for x in range(w):
      if hp[x,y]==0 and (x,y) not in seen:
        st=[(x,y)];seen.add((x,y));n=0
        while st:
          cx,cy=st.pop();n+=1
          for q in((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
            if 0<=q[0]<w and 0<=q[1]<h and hp[q]==0 and q not in seen: seen.add(q);st.append(q)
        if n<400: holes+=n;hpts.append([x,y,n])
  return pts,holes,hpts
CHK=[(685,345),(437,445),(698,717)]
out={'sizes':{}}
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');srv=subprocess.Popen(['python3','-m','http.server',PORT],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});pg.add_init_script(INIT);pg.goto('http://localhost:%s/index.html'%PORT);time.sleep(3)
  for name,s in {'p19_s1.342':1.1*1.22,'p13_s7':7}.items():
    W=int(130*s)+40;ip_=max(0,round(s));tot=[0,0];combos={}
    for pose in ['idle','jump','clash']:
      for wool in ['fluffy','short','spots','cloud']:
        for col in ['#ffffff','#333333']:
          for _ in range(2):
            A={'pose':pose,'wool':wool,'col':col,'s':s,'W':W};tr=img(pg.evaluate(REND,dict(A,bg=None)));gr=img(pg.evaluate(REND,dict(A,bg='#3cc83c')))
          pts,holes,hp=detect(tr,gr,ip_);tot[0]+=len(pts);tot[1]+=holes
          near={'%d,%d'%c:sum(1 for x,y in pts if abs(x-c[0])<=12 and abs(y-c[1])<=12) for c in CHK} if s==7 else None
          combos['%s/%s/%s'%(pose,wool,col)]={'fringe':len(pts),'pinholes':holes,'near':near,'coords':pts[:400],'hole_coords':hp[:100]}
    out['sizes'][name]={'W':W,'fringe_green':tot[0],'pinholes':tot[1],'combos':combos};print(name,tot,flush=True)
  srv.kill();br.close()
json.dump(out,open(OUT,'w'))
