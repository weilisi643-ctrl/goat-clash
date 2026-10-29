# Playwright + 系统 google-chrome：physics v2 截图 screenshots/p8_*
from playwright.sync_api import sync_playwright
import subprocess,time
srv=subprocess.Popen(['python3','-m','http.server','8766'],cwd='/workspace/goat-game',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
d='/workspace/goat-game/screenshots/'
def wait(pg,js,t=6):
  e=time.time()+t
  while time.time()<e:
    if pg.evaluate(js): return True
    time.sleep(0.005)
  return False
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':375,'height':667});errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
  pg.goto('http://localhost:8766/index.html');time.sleep(2)
  for i,dbg in enumerate([False,True]):
    pg.evaluate('GAME.G.ART.debug=%s;GAME.startMatch()'%('true' if dbg else 'false'))
    wait(pg,"GAME.B.phase==='charge'&&Math.abs(GAME.B.meter-0.8)<0.02");pg.evaluate('GAME.jump()')
    wait(pg,"GAME.B.phase==='air'&&GAME.B.p.ta>0.12");pg.screenshot(path=d+'p8_%02d_jump%s.png'%(1+i*2,'_debug' if dbg else ''))
    wait(pg,"GAME.B.phase==='result'&&GAME.B.t>=2");pg.screenshot(path=d+'p8_%02d_clash%s.png'%(2+i*2,'_debug' if dbg else ''))
    print('clash',pg.evaluate('JSON.stringify(GAME.B.lastClash)'),pg.evaluate('JSON.stringify(GAME.G.ART.lastDebug||null)'))
  pg.evaluate('GAME.G.ART.debug=false')
  wait(pg,"GAME.B.phase==='result'&&GAME.B.t>=18");pg.screenshot(path=d+'p8_05_knockback.png')
  pg.evaluate('GAME.openDdl&&GAME.openDdl()');time.sleep(.5);pg.evaluate('GAME.enterDdl(1)');time.sleep(.5);pg.screenshot(path=d+'p8_06_ddl_aim.png')
  pg.evaluate('var g=GAME.DG,s=g.lv.solution[0];g.aimAngle=s.angle;g.aimPower=s.power;GAME.fireDdl()');time.sleep(.35);pg.screenshot(path=d+'p8_07_ddl_push.png')
  time.sleep(2.5);pg.screenshot(path=d+'p8_08_ddl_after.png')
  print('errors',errs);b.close()
srv.kill()
