# 顶顶乐轨迹线显示规则测试（只显示层）：第 2 关/第 5 关 失败 1 次、2 次；换关清零
import sys,subprocess,time,json,os
from playwright.sync_api import sync_playwright
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
INIT=open('/workspace/regress_tools/quickshot.py').read().split('INIT="""')[1].split('"""')[0]
INIT+="localStorage.setItem('goat_ddl_progress_v1',JSON.stringify({stars:{1:3,2:3,3:3,4:3,5:3},grass:0,daily:{}}));"
FAIL="G.DG.aimAngle=G.DG.lv.solution[0].angle+25;G.DG.meter=G.DG.aimPower=0.75;G.fireDdl();__run(8000);"  # 偏 25° 的顶撞：不过关
res={};ok=True
def chk(name,cond):
  global ok;ok&=cond;print(('OK  ' if cond else 'FAIL'),name)
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');srv=subprocess.Popen(['python3','-m','http.server','8911'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.add_init_script(INIT);pg.goto('http://localhost:8911/index.html');time.sleep(3);pg.evaluate("window.G=GAME;__run(500);G.openDdl()")
  def step(tag,js):
    pg.evaluate(js);pg.evaluate("__run(100)");time.sleep(0.3);pg.screenshot(path=R+'/screenshots/p25_%s.png'%tag)
    s=pg.evaluate("(function(){var t=G.trailState();return {lv:G.DG.lv.id,phase:G.DG.phase,fails:t.TF.fails,mode:t.mode,show:t.show}})()");res[tag]=s;print(tag,s);return s
  s=step('lv2_fail1',"G.enterDdl(2);"+FAIL);chk('第2关失败1次：山羊+球',s['phase']!='result' and s['mode']=={'goat':True,'balls':True} and s['show'])
  s=step('lv2_fail2',FAIL);chk('第2关失败2次：山羊+球',s['mode']=={'goat':True,'balls':True})
  s=step('lv5_fail1',"G.enterDdl(5);"+FAIL);chk('第5关失败1次：不显示（换关清零）',s['lv']==5 and s['fails']==1 and s['mode'] is None)
  s=step('lv5_fail2',FAIL);chk('第5关连续失败2次：只画山羊',s['fails']==2 and s['mode']=={'goat':True,'balls':False})
  s=step('lv5_restart',"G.enterDdl(5);"+FAIL);chk('第5关重开后仍连续计数（3次）：只画山羊',s['fails']==3 and s['mode']=={'goat':True,'balls':False})
  s=step('lv4_switch',"G.enterDdl(4);"+FAIL);chk('换到第4关失败1次：清零后不显示',s['fails']==1 and s['mode'] is None)
  s=step('lv5_clear',"G.enterDdl(5);"+FAIL+"G.enterDdl(5);var sol=G.DG.lv.solution;for(var i=0;i<sol.length&&G.DG.phase==='aim';i++){G.DG.aimAngle=sol[i].angle;G.DG.meter=G.DG.aimPower=sol[i].power;G.fireDdl();__run(8000)}window.__ph=G.DG.phase;G.enterDdl(5);")
  print('clear phase',pg.evaluate('__ph'))
  chk('第5关过关后重进：计数清零、不显示',s['fails']==0 and s['mode'] is None)
  chk('页面无 JS 错误',not errs)
  srv.kill();br.close()
json.dump({'pass':ok,'cases':res},open(R+'/docs/p25_trail.json','w'),ensure_ascii=False,indent=1);print('TRAIL','PASS' if ok else 'FAIL')
