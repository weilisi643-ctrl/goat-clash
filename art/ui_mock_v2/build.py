# 重建: python3 build.py  (需要 playwright + /usr/bin/google-chrome; 羊图由 ../ui_mock/_work/goat.py 从 v7 图层合成)
import random,os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__));U='file://'+D+'/'
F='file:///workspace/goat-game/art/_fonts/ZCOOLKuaiLe-Regular.ttf'
random.seed(7)
tufts=''.join(f"<svg class=ab style='left:{random.randint(20,690)}px;top:{random.randint(20,1290)}px' width=40 height=24><path d='M6 22 L2 8 M14 22 L16 2 M22 22 L30 10' stroke='#B1D198' stroke-width=3 fill=none stroke-linecap=round/></svg>" for _ in range(16))
CSS=f"""<meta charset=utf-8><style>@font-face{{font-family:K;src:url({F})}}*{{margin:0;box-sizing:border-box}}
body{{width:750px;height:1334px;background:#CFFC98;font-family:K,'Noto Sans CJK SC';color:#2F3727;position:relative;overflow:hidden}}
.ab{{position:absolute}}.c{{text-align:center;width:750px;left:0}}
.ttl{{font-size:110px;color:#fff;-webkit-text-stroke:14px #2F3727;paint-order:stroke fill;text-shadow:6px 8px 0 #2F3727;transform:rotate(-3deg);letter-spacing:4px}}
.b{{background:#fff;border:4px solid #2F3727;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:40px}}
.main{{box-shadow:0 12px 0 #8CCB4E,0 12px 0 4px #2F3727}}
.sm{{box-shadow:0 7px 0 #2F3727}}
.pill{{background:#2F3727;color:#fff;border-radius:999px;padding:6px 26px;font-size:28px}}
.hp{{height:30px;border:4px solid #2F3727;border-radius:15px;background:#fff;overflow:hidden}}
</style>{tufts}"""
def home(): 
    rows=[('羊毛','蓬松卷毛'),('毛色','白 <span style=\"display:inline-block;width:30px;height:30px;border-radius:50%;background:#fff;border:3px solid #2F3727;vertical-align:middle\"></span>'),('角形','卷角'),('角色','金 <span style=\"display:inline-block;width:30px;height:30px;border-radius:50%;background:#D6B678;border:3px solid #2F3727;vertical-align:middle\"></span>')]
    r=''.join(f"<div style='display:flex;align-items:center;gap:18px;margin:14px 0'><div class='b sm' style='width:70px;height:70px;background:#FCD800;font-size:34px'>◀</div><div class=b style='flex:1;height:70px;font-size:32px;border-radius:999px'><span style='opacity:.5'>{a}</span>&nbsp;&nbsp;{b}</div><div class='b sm' style='width:70px;height:70px;background:#FCD800;font-size:34px'>▶</div></div>" for a,b in rows)
    return CSS+f"""<div class='ab c' style='top:150px'><span class=ttl>咩咩顶角王</span></div>
<div class='ab c' style='top:310px'><span class=pill>打造你的山羊</span></div>
<img class=ab src='{U}g_home.png' style='left:235px;top:380px;height:300px'>
<div class='ab c' style='top:700px;font-size:28px'>体力 110 · 速度 +0 · 力量 +0</div>
<div class=ab style='left:95px;top:750px;width:560px'>{r}</div>
<div class='ab b main' style='left:175px;top:1110px;width:400px;height:110px;font-size:52px'>开始对战</div>
<div class='ab b sm' style='left:40px;top:1140px;width:110px;height:84px;background:#2E6FD8;color:#fff;font-size:26px;flex-direction:column;line-height:1.1'>每日<br>擂主</div>
<div class='ab b sm' style='left:600px;top:1140px;width:110px;height:84px;background:#FF9E3D;color:#fff;font-size:26px;flex-direction:column;line-height:1.1'>顶<br>顶乐</div>"""
def hud():
    ang=''.join(f"<div class='b {'main' if s else 'sm'}' style='width:170px;height:96px;font-size:44px;{'' if s else 'background:#fff'}'>{n}</div>" for n,s in [('低',0),('中',1),('高',0)])
    return CSS+f"""<div class='b sm ab' style='left:30px;top:40px;width:64px;height:64px;font-size:34px'>Ⅱ</div>
<div class='ab c' style='top:50px'><span class=pill>第 1 回合 · 三局两胜</span></div>
<div class='ab c' style='top:110px;font-size:96px;color:#fff;-webkit-text-stroke:10px #2F3727;paint-order:stroke fill'>0 : 0</div>
<div class=ab style='left:40px;top:250px;width:310px'><div style='font-size:30px'>你 · 110</div><div class=hp style='margin-top:8px'><div style='width:100%;height:100%;background:#8CCB4E'></div></div></div>
<div class=ab style='left:400px;top:250px;width:310px;text-align:right'><div style='font-size:30px'>100 · 电脑</div><div class=hp style='margin-top:8px'><div style='width:91%;height:100%;background:#FF7A6B;margin-left:9%'></div></div></div>
<img class=ab src='{U}g_me.png' style='left:30px;top:540px;height:280px'>
<img class=ab src='{U}g_op.png' style='left:460px;top:540px;height:280px'>
<div class='ab c' style='top:880px'><div class=b style='display:inline-flex;font-size:30px;padding:10px 30px;border-radius:999px'>对手架势：低角度 · 选你的角度</div></div>
<div class=ab style='left:75px;top:980px;width:600px;display:flex;justify-content:space-between'>{ang}</div>
<div class='ab hp' style='left:105px;top:1115px;width:540px;height:34px'><div style='margin-left:62%;width:14%;height:100%;background:#8CCB4E'></div></div>
<div class=ab style='left:490px;top:1103px;width:12px;height:58px;background:#FF4D4D;border:3px solid #2F3727;border-radius:6px'></div>
<div class='ab b main' style='left:175px;top:1185px;width:400px;height:104px;font-size:50px'>起跳顶角！</div>"""
def result(lose=False):
    return hud().replace('</style>','.dim{}</style>')+f"""<div class=ab style='inset:0;background:rgba(47,55,39,.55)'></div>
<div class='ab' style='left:85px;top:300px;width:580px;height:800px;background:#fff;border:5px solid #2F3727;border-radius:36px;box-shadow:0 12px 0 #2F3727'></div>
<div class='ab c' style='top:250px'>{"<span class=ttl style='font-size:96px;display:inline-block;color:#C9CCC4'>再接再厉</span>" if lose else "<span class=ttl style='font-size:96px;display:inline-block;color:#FCD800'>胜 利 !</span>"}</div>
<img class=ab src='{U}g_home.png' style='left:270px;top:420px;height:220px'>
<div class='ab c' style='top:660px;font-size:34px'>{'1 : 2 · 惜败' if lose else '2 : 1 · 赢下本场'}</div>
<div class='ab c' style='top:715px;font-size:30px;opacity:.6'>本局得分</div>
<div class='ab c' style='top:755px;font-size:88px;color:#fff;-webkit-text-stroke:10px #2F3727;paint-order:stroke fill'>{'860' if lose else '1260'}</div>
<div class='ab b main' style='left:195px;top:860px;width:360px;height:100px;font-size:46px'>再来一局</div>
<div class='ab b sm' style='left:265px;top:990px;width:220px;height:80px;font-size:34px;background:#2E6FD8;color:#fff'>回主页</div>
"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':750,'height':1334})
    for n,f in [('home',home),('hud',hud),('result',result),('result_lose',lambda:result(True))]:
        open(D+'/_t.html','w').write(f());pg.goto(U+'_t.html');pg.wait_for_timeout(500);pg.screenshot(path=f'{D}/{n}.png')
    b.close()
from PIL import Image
o=Image.new('RGB',(4*375+100,707),'#2F3727')
for i,n in enumerate(['home','hud','result','result_lose']): o.paste(Image.open(f'{D}/{n}.png').convert('RGB').resize((375,667)),(20+i*395,20))
o.save(D+'/overview.png')
