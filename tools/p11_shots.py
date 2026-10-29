# 画面升级第二步前后对比：before = 提交 2286c4b（worktree），after = 当前工作区；虚拟 rAF 时钟 + 固定种子，同一时刻截图
from playwright.sync_api import sync_playwright
import subprocess,time,sys
BEFORE=sys.argv[1] if len(sys.argv)>1 else '/tmp/wt_before'
d=(sys.argv[2] if len(sys.argv)>2 else '/workspace/goat-game')+'/screenshots/'
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for tag,root,port in [('before',BEFORE,8781),('after',(sys.argv[2] if len(sys.argv)>2 else '/workspace/goat-game'),8782)]:
    srv=subprocess.Popen(['python3','-m','http.server',str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
    pg=b.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT);pg.goto('http://localhost:%d/index.html'%port);time.sleep(2)
    def shot(n): pg.screenshot(path=d+'p11_%s_%s.png'%(n,tag))
    pg.evaluate(SEED+"G=GAME;__run(800)");shot('01_home')
    pg.evaluate("G.startMatch();__run(800)");shot('02_battle')
    pg.evaluate("G.B.meter=0.8;G.jump()")
    for _ in range(200):
      if pg.evaluate("G.B.phase==='result'"): break
      pg.evaluate("__run(1000/60)")
    pg.evaluate("__run(50)");shot('03_clash')
    pg.evaluate("G.setNow(Date.UTC(2026,10,3,4,0));G.openArena();if(G.st.scene==='faction')G.chooseFaction('east');__run(800)");shot('04_arena_faction')
    pg.evaluate("G.st.scene='faction';__run(800)");shot('06_buttons_panels')
    pg.evaluate("G.openDdl();G.enterDdl(1);var g=G.DG;g.aimAngle=g.lv.solution[0].angle;g.meter=g.lv.solution[0].power;g.aimPower=g.meter;G.fireDdl();__run(420)");shot('05_ddl')
    print(tag,errs);pg.close();srv.kill()
  b.close()
