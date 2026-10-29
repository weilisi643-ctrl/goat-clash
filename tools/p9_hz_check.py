# Playwright + 系统 chrome：用虚拟 rAF 时钟模拟 30/60/120/144Hz（及 45Hz 抖动、5Hz 卡顿），比较同一真实时间内的游戏进度
from playwright.sync_api import sync_playwright
import subprocess,time,json,random
srv=subprocess.Popen(['python3','-m','http.server','8767'],cwd='/workspace/goat-game',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
INIT="""window.__q=[];window.__t=0;var __js=7;function __jr(){__js=(__js*48271)%2147483647;return __js/2147483647}window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms,hz,jit){var end=__t+ms;while(__t<end-1e-9){var dt=1000/hz;if(jit)dt*=(0.5+__jr());__t=Math.min(end,__t+dt);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
res={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for hz,jit in [(30,0),(60,0),(120,0),(144,0),(45,1),(5,0)]:
    pg=b.new_page(viewport={'width':375,'height':667});pg.add_init_script(INIT);errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8767/index.html');time.sleep(1.5)
    r=pg.evaluate("""([hz,jit])=>{Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();
      var G=GAME;G.__run=__run;__run(100,hz,0);G.startMatch();var s0=G.clock.steps;__run(1000,hz,jit);var o={meter:+G.B.meter.toFixed(4),stepsCharge:G.clock.steps-s0};
      G.B.meter=0.8;G.jump();s0=G.clock.steps;__run(500,hz,jit);o.stepsAfterJump=G.clock.steps-s0;o.phase=G.B.phase;o.t=G.B.t;o.px=+G.B.p.x.toFixed(3);o.ex=+G.B.e.x.toFixed(3);o.py=+G.B.p.y.toFixed(3);o.hpE=G.B.e.hp;o.hpP=G.B.p.hp;
      G.openDdl();G.enterDdl(1);var g=G.DG;g.aimAngle=g.lv.solution[0].angle;g.meter=g.lv.solution[0].power;g.aimPower=g.meter;G.fireDdl();s0=G.clock.steps;__run(1500,hz,jit);o.ddlSteps=G.clock.steps-s0;o.ddlScene=G.st.scene;o.dropped=G.clock.dropped;o.renders=G.clock.frames;return o;}""",[hz,jit])
    r['errors']=errs;res[('%dHz'%hz)+('_jitter' if jit else '')]=r;pg.close()
  b.close()
srv.kill();print(json.dumps(res,indent=1))
json.dump(res,open('/workspace/goat-game/docs/fixed_step_hz_check.json','w'),indent=1)
