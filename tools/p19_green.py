# 任务3：放大后的战场尺寸下重测透绿/小孔。战斗羊 s=1.1（goat 世界尺度）× sceneZoom → 屏幕尺度；另测 dpr=2/3 实际像素
import json,os,sys,io,base64,subprocess,time
sys.argv=[sys.argv[0]];os.environ.setdefault('ROOTS','[]')
from PIL import Image,ImageFilter,ImageDraw
from playwright.sync_api import sync_playwright
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
INIT="try{localStorage.setItem('tutorialDone','true')}catch(e){};"
REND="""(a)=>{var G=null;for(var k in cache){if(k.indexOf('/js/goat.js')>=0)G=cache[k].exports}
var c=document.createElement('canvas');c.width=a.W;c.height=a.W;var x=c.getContext('2d');if(a.bg)x.fillStyle=a.bg,x.fillRect(0,0,a.W,a.W);
G.drawGoatArt(x,a.W/2,a.W*0.45,a.s,{wool:a.wool,woolColor:a.col,horn:'curl'},1,0,a.pose);return c.toDataURL('image/png')}"""
def img(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
def detect(tr,gr,inner_px):
  a=tr.split()[3];m=a.point(lambda v:255 if v>0 else 0);f=m.copy();ImageDraw.floodfill(f,(0,0),128)
  inner=m.filter(ImageFilter.MinFilter(2*inner_px+1)) if inner_px>0 else m
  gp=gr.convert('RGB').load();ip=inner.load();w,h=tr.size;fr=0
  for y in range(h):
    for x in range(w):
      if ip[x,y]:
        r2,G2,b2=gp[x,y]
        if G2>r2+30 and G2>b2+30: fr+=1
  hp=f.load();seen=set();holes=0
  for y in range(h):
    for x in range(w):
      if hp[x,y]==0 and (x,y) not in seen:
        st=[(x,y)];seen.add((x,y));n=0
        while st:
          cx,cy=st.pop();n+=1
          for q in((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
            if 0<=q[0]<w and 0<=q[1]<h and hp[q]==0 and q not in seen: seen.add(q);st.append(q)
        if n<400*(1 if True else 0): holes+=n
  return fr,holes
ZOOM=1.22;CASES={'before_s1.1':1.1,'after_s%.3f'%(1.1*ZOOM):1.1*ZOOM,'after_dpr2':1.1*ZOOM*2,'after_dpr3':1.1*ZOOM*3,'ref_s7':7}
out={}
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');srv=subprocess.Popen(['python3','-m','http.server','8861'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});pg.add_init_script(INIT);pg.goto('http://localhost:8861/index.html');time.sleep(3)
  for name,s in CASES.items():
    W=int(130*s)+40;ip=max(0,round(s))  # 内部判定：距透明 >~源图1px（s=7 时 7px，与 p13 一致）
    tot=[0,0]
    for pose in ['idle','jump','clash']:
      for wool in ['fluffy','short','spots','cloud']:
        for col in ['#ffffff','#333333']:
          for _ in range(2):
            A={'pose':pose,'wool':wool,'col':col,'s':s,'W':W};tr=img(pg.evaluate(REND,dict(A,bg=None)));gr=img(pg.evaluate(REND,dict(A,bg='#3cc83c')))
          r=detect(tr,gr,ip);tot[0]+=r[0];tot[1]+=r[1]
    out[name]={'scale':round(s,3),'fringe_green':tot[0],'pinholes':tot[1]};print(name,out[name],flush=True)
  srv.kill();br.close()
json.dump(out,open(R+'/docs/p19_green_fringe.json','w'),indent=1)
