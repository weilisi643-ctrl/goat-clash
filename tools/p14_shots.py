# v3 UI（参考国内版羊了个羊）：①样稿与实现并排（home/hud/result/result_lose）②延伸屏 ③真实鼠标点击走通主流程（按钮中心点击，校验场景跳转）
from playwright.sync_api import sync_playwright
from PIL import Image
import subprocess,time,os,json,sys
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
MOCK=os.environ.get('MOCK','/workspace/goat-game/art/ui_mock_v2')
INIT="""try{localStorage.setItem("tutorialDone","true")}catch(e){};window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
log=[];ok=True
def chk(c,m):
  global ok; log.append(('OK  ' if c else 'FAIL')+' '+m); ok=ok and c
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  srv=subprocess.Popen(['python3','-m','http.server','8860'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.add_init_script(INIT);pg.goto('http://localhost:8860/index.html')
  pg.evaluate("document.fonts.ready");time.sleep(1.5)
  pg.evaluate(SEED+"window.G=GAME;G.setNow(Date.UTC(2026,10,3,4,0));localStorage.clear&&localStorage.clear();__run(600)")
  chk(pg.evaluate("document.fonts.check('16px KuaiLe')"),'站酷快乐体已加载')
  run=lambda ms=600:pg.evaluate("__run(%d)"%ms)
  sc=lambda:pg.evaluate("G.st.scene")
  def click(lab,expect=None):
    b=pg.evaluate("(l)=>{var b=G.st.buttons.filter(function(x){return l[0]==='^'?x.label.split(String.fromCharCode(10)).join('').indexOf(l.slice(1))===0:x.label.split(String.fromCharCode(10)).join('').indexOf(l)>=0}).pop();return b&&{x:b.x+b.w/2,y:b.y+b.h/2,lab:b.label}}",lab)
    if not b: chk(False,'找不到按钮 %s（场景 %s）'%(lab,sc()));return False
    # 命中区校验：按钮中心的最上层按钮必须是它自己
    top=pg.evaluate("([x,y])=>{for(var i=G.st.buttons.length-1;i>=0;i--){var b=G.st.buttons[i];if(x>=b.x&&x<=b.x+b.w&&y>=b.y&&y<=b.y+b.h)return b.label}return null}",[b['x'],b['y']])
    pg.mouse.click(b['x'],b['y']);run(400)
    s=sc();chk(top==b['lab'] and (expect is None or s==expect),'点击「%s」→ %s'%(b['lab'].replace('\n',''),s));return True
  shot=lambda n:pg.screenshot(path=d+'p14_%s.png'%n)
  def battle_to(end):
    for _ in range(300):
      s=sc()
      if s!='battle': break
      ph=pg.evaluate("G.B.phase")
      if ph=='charge': pg.evaluate("G.B.meter=0.8");click('起跳')
      elif ph=='result' and pg.evaluate("G.B.t>30"): click('下一回合' if pg.evaluate("G.st.buttons.some(function(b){return b.label.indexOf('下一回合')>=0})") else '继续')
      else: run(300)
    chk(sc()==end,'对战结束 → %s'%sc())
  try:
    # 主页
    run(800);shot('home');shot('impl_home')
    # 自由对战：换装 → 开始 → 蓄力截图 → 打完 → 结果
    click('▶');click('◀')
    click('开始对战','battle');run(600);shot('impl_hud')
    battle_to('over');run(800);shot('impl_result' if pg.evaluate("G.B.wins[0]===2") else 'impl_result_lose')
    click('再来一局','battle');battle_to('over');run(800)
    shot('impl_result' if pg.evaluate("G.B.wins[0]===2") else 'impl_result_lose')
    # 补拍另一种结果（直接设比分，仅截图用）
    for k,w in [('impl_result','[2,1]'),('impl_result_lose','[1,2]')]:
      if not os.path.exists(d+'p14_%s.png'%k) or True: pg.evaluate("G.B.wins=%s;G.st.scene='over';__run(800)"%w);shot(k)
    click('回主页','custom')
    # 每日擂主
    click('擂主','faction');run(800);shot('ext_faction');click('东','arena');run(800);shot('ext_arena')
    click('挑战第 1 场','battle');run(600);shot('ext_arena_battle');battle_to('arenaResult');run(800);shot('ext_arena_result')
    click('返回擂台','arena');click('选择牧场','faction');click('稍后再选','arena');click('返回','custom')
    # 顶顶乐
    click('顶顶乐','ddlSelect');run(800);shot('ext_ddl_select');click('^1. ','ddl');run(600)
    pg.evaluate("var g=G.DG;g.aimAngle=g.lv.solution[0].angle;g.dir=0;g.meter=g.lv.solution[0].power;g.aimPower=g.meter");run(50);shot('ext_ddl_aim')
    click('瞄准线','ddl');run(200);shot('ext_ddl_hint')
    pg.evaluate("var g=G.DG;g.aimAngle=g.lv.solution[0].angle;g.meter=g.lv.solution[0].power;g.dir=0");click('顶！');run(2500)
    chk(sc()=='ddlResult','顶顶乐过关 → %s'%sc());run(800);shot('ext_ddl_result')
    click('下一关','ddl');click('选关','ddlSelect');click('返回','custom')
  except Exception as e:
    chk(False,'异常 %s'%str(e)[:200]);print('\n'.join(log));raise
  chk(not errs,'页面无 JS 错误 %s'%errs)
  pg.close();srv.kill();br.close()
# 样稿 | 实现 并排
for n in ['home','hud','result','result_lose']:
  m=Image.open(MOCK+'/%s.png'%n).convert('RGB').resize((375,667),Image.LANCZOS);i=Image.open(d+'p14_impl_%s.png'%n).convert('RGB')
  c=Image.new('RGB',(375*2+30,667+0),'#2F3727');c.paste(m,(0,0));c.paste(i,(405,0));c.save(d+'p14_mock_vs_impl_%s.png'%n)
ext=['ext_faction','ext_arena','ext_arena_battle','ext_arena_result','ext_ddl_select','ext_ddl_aim','ext_ddl_hint','ext_ddl_result']
c=Image.new('RGB',(4*395+20,2*687+20),'#2F3727')
for k,n in enumerate(ext): c.paste(Image.open(d+'p14_%s.png'%n).convert('RGB'),(20+(k%4)*395,20+(k//4)*687))
c.save(d+'p14_extended_overview.png')
print('\n'.join(log));print('FLOW', 'PASS' if ok else 'FAIL')
json.dump({'pass':ok,'log':log},open(R+'/docs/p14_flow.json','w'),ensure_ascii=False,indent=1)
