# 任务2 前后对比截图：python3 tools/p21_shots.py <root> <port> <out_prefix> [js...]
import sys,subprocess,time
from playwright.sync_api import sync_playwright
INIT="""try{localStorage.setItem("tutorialDone","true")}catch(e){};window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"""
pre=sys.argv[3];steps=sys.argv[4:]
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');srv=subprocess.Popen(['python3','-m','http.server',''+sys.argv[2]+''],cwd=sys.argv[1],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.add_init_script(INIT);pg.goto('http://localhost:'+sys.argv[2]+'/index.html');time.sleep(3);pg.evaluate("window.G=GAME;__run(500)")
  for i,js in enumerate(['0']+steps):
    pg.evaluate(js);pg.evaluate("__run(200)");time.sleep(0.5);pg.evaluate("__run(50)");pg.screenshot(path='%s_%d.png'%(pre,i))
  print('errs',errs);srv.kill();br.close()
