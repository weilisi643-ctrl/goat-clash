# 主题切换演示：运行时把按钮/面板改为 solid + 描边 + 阴影、关位图字体，验证所有按钮/面板/标题都走主题（不改文件）
from playwright.sync_api import sync_playwright
import subprocess,time,os
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
srv=subprocess.Popen(['python3','-m','http.server','8840'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto('http://localhost:8840/index.html');time.sleep(2)
  pg.evaluate("""var T=GAME.UI.TH;T.button.style='solid';T.button.radius=22;T.button.stroke={width:2,color:'#ffffff'};T.button.shadow={color:'rgba(0,0,0,0.18)',blur:8,offsetY:3};
   T.panel.style='solid';T.panel.fill='rgba(255,255,255,0.9)';T.panel.radius=18;T.font.bitmap.titleMinSize=999;T.font.bitmap.bodyMinSize=999;T.colors.skyTop='#d8f0ff';T.colors.ground='#a8dd8c';""")
  time.sleep(0.6);pg.screenshot(path=R+'/screenshots/p12_05_theme_solid_demo.png');print(errs);b.close()
srv.kill()
