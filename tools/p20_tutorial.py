# 任务1 新手教学战验证：首次自动进入→6 步截图→埋点/奖励/tutorialDone；跳过路径；设置页重玩；共享配置前后一致
from playwright.sync_api import sync_playwright
import subprocess,time,os,json,hashlib
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
INIT="""window.__q=[];window.__t=0;window.requestAnimationFrame=function(f){window.__q.push(f)};
window.__run=function(ms){var end=__t+ms;while(__t<end-1e-9){__t=Math.min(end,__t+1000/60);var q=__q;__q=[];q.forEach(function(f){f(__t)});}};"""
SEED="Math.random=(function(){var s=42;return function(){s=(s*1664525+1013904223)>>>0;return s/4294967296}})();"
CFG="""(function(){var o={};for(var k in cache){if(/js\\/(data|arena|ddl|battle_physics)\\.js/.test(k)){var e=cache[k].exports,c={};for(var n in e)if(typeof e[n]!=='function')c[n]=e[n];o[k.replace(/.*js\\//,'')]=c}}return JSON.stringify(o)})()"""
out={'checks':[]}
def ok(n,c,info=''): out['checks'].append([n,bool(c),info]);print('OK  ' if c else 'FAIL',n,info)
def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');srv=subprocess.Popen(['python3','-m','http.server','8863'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
  pg=br.new_page(viewport={'width':375,'height':667});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.add_init_script(INIT+SEED);pg.goto('http://localhost:8863/index.html');time.sleep(3)
  pg.evaluate("window.G=GAME;__run(300)")
  c0=pg.evaluate(CFG);out['cfg_before']=sha(c0)
  ok('首次启动自动进入教学',pg.evaluate("G.T.active&&G.st.scene==='battle'&&G.B.arena.tutorial"))
  st=lambda:pg.evaluate("G.T.step")
  def shot(n):pg.evaluate("__run(50)");pg.screenshot(path=d+'p20_tut_step%s.png'%n)
  shot(1);ok('step1',st()==1)
  pg.mouse.click(180,330);pg.evaluate("__run(50)");shot(2);ok('点击继续→step2',st()==2)
  L=pg.evaluate("G.UI.TH.layout.battle")
  pg.mouse.click(375/2-1.5*L['angleW']-15+L['angleW']/2,667-L['angleBottom']+L['angleH']/2);shot(3);ok('选角度→step3',st()==3)
  ok('完美区描边读现有常量',pg.evaluate("JSON.stringify(G.PERFECT_ZONE)")=='[0.72,0.88]')
  for _ in range(400):
    if abs(pg.evaluate("G.B.meter")-0.8)<0.01: break
    pg.evaluate("__run(1000/60)")
  pg.mouse.click(375/2,667-L['jumpBottom']+L['jumpH']/2);ok('起跳→step4',st()==4)
  for _ in range(300):
    if pg.evaluate("G.B.phase==='result'"): break
    pg.evaluate("__run(1000/60)")
  pg.evaluate("__run(600)");shot(4)
  pg.evaluate("__run(1600)");ok('自动 2 秒→step5',st()==5);shot(5)
  for _ in range(60):
    if pg.evaluate("G.st.scene!=='battle'"): break
    ph=pg.evaluate("G.B.phase")
    if ph=='charge': pg.evaluate("G.B.meter=0.8;G.jump()")
    elif ph=='result': pg.evaluate("__run(700)");pg.evaluate("(function(){var b=G.st.buttons.filter(function(b){return b.label==='下一回合'||b.label==='继续'})[0];if(b)b.cb()})()")
    pg.evaluate("__run(300)")
  shot(6);ok('结算页 tutResult',pg.evaluate("G.st.scene")=='tutResult')
  ok('tutorialDone 写入',pg.evaluate("JSON.parse(localStorage.getItem('tutorialDone'))")==True)
  ok('奖励羊毛色 樱花粉',pg.evaluate("G.woolColorList().indexOf('#F4B6C2')>=0&&JSON.parse(localStorage.getItem('woolUnlocked')).length===1"))
  ev=pg.evaluate("JSON.parse(localStorage.getItem('tutorialEvents'))");out['events']=ev
  ok('埋点 start/step1-6/end',[e['e'] for e in ev]==['tutorial_start']+['tutorial_step']*6+['tutorial_end'],json.dumps([e.get('n',e['e']) for e in ev]))
  ok('end 含 win/perfectCount','perfectCount' in ev[-1] and 'win' in ev[-1],json.dumps(ev[-1]))
  c1=pg.evaluate(CFG);out['cfg_after']=sha(c1);ok('共享配置教学前后一致',c0==c1,out['cfg_before']+' / '+out['cfg_after'])
  # 设置页 → 重玩 → 跳过
  pg.evaluate("G.st.scene='custom';__run(100)");pg.mouse.click(375-38,27);pg.evaluate("__run(100)");pg.screenshot(path=d+'p20_settings.png');ok('设置页',pg.evaluate("G.st.scene")=='settings')
  pg.mouse.click(375/2,166);pg.evaluate("__run(100)");ok('重玩教学',pg.evaluate("G.T.active&&G.T.step===1"))
  pg.mouse.click(375-38,27);pg.evaluate("__run(100)");pg.screenshot(path=d+'p20_after_skip.png')
  ev=pg.evaluate("JSON.parse(localStorage.getItem('tutorialEvents'))")
  ok('跳过→回主页且记录 skip{step}',pg.evaluate("!G.T.active&&G.st.scene==='custom'") and ev[-1]['e']=='tutorial_skip' and ev[-1]['step']==1,json.dumps(ev[-1]))
  # 中途退出不算完成：新存储
  pg.evaluate("localStorage.clear()");pg.reload();time.sleep(3);pg.evaluate("window.G=GAME;__run(300);G.st.scene='custom';G.startMatch();__run(100)")
  ok('中途退出不写 tutorialDone',pg.evaluate("!G.T.active&&localStorage.getItem('tutorialDone')===null"))
  pg.evaluate("localStorage.setItem('tutorialDone','true')");pg.reload();time.sleep(3);pg.evaluate("window.G=GAME;__run(300)")
  ok('已完成不再自动进入',pg.evaluate("!G.T.active&&G.st.scene==='custom'"))
  ok('无 JS 错误',not errs,str(errs));srv.kill();br.close()
json.dump(out,open(R+'/docs/p20_tutorial.json','w'),ensure_ascii=False,indent=1)
print('TUT PASS' if all(c[1] for c in out['checks']) else 'TUT FAIL')
