# 同一时刻 before(FX 关)/after(FX 开) 对比截图 + 对撞录屏（Playwright + 系统 chrome，虚拟 rAF 时钟保证同一时刻）
from playwright.sync_api import sync_playwright
import subprocess,time,glob,os,shutil
srv=subprocess.Popen(['python3','-m','http.server','8768'],cwd='/workspace/goat-game',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
d='/workspace/goat-game/screenshots/'
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
shots=[('clash_hitstop',"G.B.phase==='result'",30),('clash_spark',"G.B.phase==='result'",160),('land',"G.B.phase==='result'",520)]
import sys
ONLY_VIDEO='--video' in sys.argv
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for tag,on in ([] if ONLY_VIDEO else [('before',False),('after',True)]):
    pg=b.new_page(viewport={'width':375,'height':667});pg.add_init_script(INIT);pg.goto('http://localhost:8768/index.html');time.sleep(1.5)
    pg.evaluate(SEED+"G=GAME;G.FX.enabled=%s;__run(100);G.startMatch();__run(600);G.B.meter=0.8;G.jump();"%('true' if on else 'false'))
    pg.evaluate("__run(1000/60*2)");pg.screenshot(path=d+'p10_01_jump_%s.png'%tag)
    for _ in range(200):
      if pg.evaluate("G.B.phase==='result'"): break
      pg.evaluate("__run(1000/60)")
    t0=0
    for i,(nm,_,ms) in enumerate(shots):
      pg.evaluate("__run(%f)"%(ms-t0));t0=ms;pg.screenshot(path=d+'p10_%02d_%s_%s.png'%(i+2,nm,tag))
    pg.evaluate("G.openDdl();G.enterDdl(1);var g=G.DG;g.aimAngle=g.lv.solution[0].angle;g.meter=g.lv.solution[0].power;g.aimPower=g.meter;G.fireDdl();__run(700)")
    pg.screenshot(path=d+'p10_05_ddl_hay_%s.png'%tag)
    for _ in range(300):
      if pg.evaluate("G.st.scene==='ddlResult'"): break
      pg.evaluate("__run(1000/60)")
    pg.evaluate("__run(250)");pg.screenshot(path=d+'p10_06_ddl_confetti_%s.png'%tag)
    print(tag,pg.evaluate("G.FX.alive()"));pg.close()
  # 录屏（真实时间，FX 开）
  ctxv=b.new_context(viewport={'width':375,'height':667},record_video_dir='/tmp/vid',record_video_size={'width':375,'height':667})
  pg=ctxv.new_page();pg.goto('http://localhost:8768/index.html');time.sleep(1)
  for k in range(3):
    pg.evaluate("GAME.startMatch()") if k==0 else None
    for _ in range(400):
      if pg.evaluate("GAME.B.phase==='charge'&&Math.abs(GAME.B.meter-0.8)<0.02"): break
      if pg.evaluate("GAME.B.phase==='result'&&GAME.B.t>30"): pg.evaluate("GAME.st.buttons.filter(b=>/下一回合|继续/.test(b.label)).pop().cb()")
      time.sleep(0.01)
    pg.evaluate("GAME.jump()");time.sleep(1.4)
  pg.close();ctxv.close()
  v=sorted(glob.glob('/tmp/vid/*.webm'),key=os.path.getmtime)[-1];shutil.copy(v,d+'p10_clash_fx.webm')
  b.close()
srv.kill()
