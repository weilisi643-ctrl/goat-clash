# p18：宽屏草地留边 / 320 宽血条 / 腿补丁 ±15° / 对战画面。TAG 环境变量区分 before/after
from playwright.sync_api import sync_playwright
import subprocess,time,os,json,sys
R=os.environ.get('ROOT') or os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))+'/screenshots/'
TAG=os.environ.get('TAG','after');PORT=int(os.environ.get('PORT','8880'))
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
out={}
srv=subprocess.Popen(['python3','-m','http.server',str(PORT)],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for W in [320,375,1024]:
    pg=br.new_page(viewport={'width':W,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('**/index.html',lambda rt,rq,W=W:rt.fulfill(status=200,content_type='text/html',body=rt.fetch().text().replace('var W=375,H=667','var W=%d,H=667'%W)))
    pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%PORT);time.sleep(2.5)
    pg.evaluate(SEED+"window.G=GAME;G.setNow(Date.UTC(2026,10,3,4,0));__run(600)")
    pg.evaluate("G.startMatch();__run(600)");pg.screenshot(path=d+'p18_battle_%d_%s.png'%(W,TAG))
    # 血条矩形（布局令牌推算）
    out['W%d'%W]={'errors':errs}
    pg.evaluate("G.openDdl?G.openDdl():0;__run(300)")
    pg.close()
  br.close()
srv.kill();print(json.dumps(out))
