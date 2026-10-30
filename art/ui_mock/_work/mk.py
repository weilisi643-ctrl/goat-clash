from playwright.sync_api import sync_playwright
T={
'A_cream_meadow':dict(bg='linear-gradient(#FFFBF2 70%,#EEF4E4)',ink='#4A5A3A',sub='#9AA58A',pri='#8DB86B',priT='#fff',sec='#F3EDDF',card='#FFFFFF',acc='#E8B96A',my='#8DB86B',op='#E8A88A',bord='none',font='Noto Sans CJK SC',filt='',rad='28px',ground='#DCE8CB'),
'B_light_airy':dict(bg='linear-gradient(#F4F7FA,#EAF0F5)',ink='#2F3B48',sub='#9AA7B4',pri='#6E8FB0',priT='#fff',sec='#FFFFFF',card='rgba(255,255,255,.75)',acc='#A9C3DA',my='#7FA6C9',op='#C9B3D9',bord='none',font='Noto Sans CJK SC',filt='',rad='999px',ground='#E1E8EF'),
'C_pastel_crayon':dict(bg='#FFF6EE',ink='#5B4A5E',sub='#A895A6',pri='#F6B6C1',priT='#5B4A5E',sec='#CDE7F0',card='#FFFDF9',acc='#FFE3A3',my='#B8E0C2',op='#F6B6C1',bord='3px solid #5B4A5E',font='Noto Serif CJK SC',filt='filter:url(#wob);',rad='22px',ground='#E4F2D9'),
}
def css(t):return f"""<style>*{{margin:0;box-sizing:border-box}}body{{width:750px;height:1334px;background:{t['bg']};font-family:'{t['font']}';color:{t['ink']};position:relative;overflow:hidden}}
.c{{text-align:center}}.btn{{border-radius:{t['rad']};border:{t['bord']};{t['filt']}display:flex;align-items:center;justify-content:center;font-weight:700}}
.card{{background:{t['card']};border-radius:28px;border:{t['bord']};{t['filt']}}}
.ab{{position:absolute}}.arrow{{width:72px;height:72px;background:{t['sec']};border-radius:50%;border:{t['bord']};{t['filt']}display:flex;align-items:center;justify-content:center;font-size:28px;color:{t['sub']}}}
.row{{display:flex;align-items:center;justify-content:space-between;height:80px}}
.bar{{height:18px;border-radius:9px;background:rgba(0,0,0,.06);overflow:hidden;border:{t['bord'].replace('3px','2px')};{t['filt']}}}
</style><svg width=0 height=0><filter id=wob><feTurbulence type=fractalNoise baseFrequency=.04 numOctaves=2 seed=3 result=n /><feDisplacementMap in=SourceGraphic in2=n scale=6 xChannelSelector=R yChannelSelector=G /></filter></svg>"""
W='file:///workspace/goat-game/art/ui_mock/_work/'
def home(t):
    rows=[('羊毛','蓬松卷毛',None),('毛色','',"#FAF8F2"),('角形','卷角',None),('角色','',"#D6B678")]
    r=''.join(f"<div class=row><div class=arrow>‹</div><div style='font-size:30px'><span style='color:{t['sub']}'>{a}</span>&nbsp;&nbsp;{b}"+(f"<span style='display:inline-block;width:34px;height:34px;border-radius:50%;background:{c};vertical-align:middle;border:2px solid rgba(0,0,0,.12)'></span>" if c else '')+"</div><div class=arrow>›</div></div>" for a,b,c in rows)
    return css(t)+f"""
<div class='ab c' style='top:110px;width:750px'><div style='font-size:64px;font-weight:700;letter-spacing:6px'>咩咩顶角王</div><div style='font-size:26px;color:{t['sub']};margin-top:10px;letter-spacing:8px'>打造你的山羊</div></div>
<div class=ab style='left:175px;top:270px;width:420px;height:40px;bottom:auto'></div>
<div class=ab style='left:200px;top:585px;width:350px;height:36px;border-radius:50%;background:{t['ground']}'></div>
<img class=ab src='{W}g_home.png' style='left:205px;top:250px;height:360px'>
<div class='ab c' style='top:640px;width:750px;font-size:26px;color:{t['sub']}'>体力 <b style='color:{t['ink']}'>110</b> · 速度 <b style='color:{t['ink']}'>+0</b> · 力量 <b style='color:{t['ink']}'>+0</b><div style='margin-top:8px;font-size:24px;color:{t['acc'] if t['acc']!='#FFE3A3' else '#D79A5A'}'>卷角 · 低角度克制</div></div>
<div class='ab card' style='left:60px;top:740px;width:630px;padding:8px 28px'>{r}</div>
<div class='ab btn' style='left:60px;top:1112px;width:630px;height:100px;background:{t['pri']};color:{t['priT']};font-size:38px;letter-spacing:8px'>开始对战</div>
<div class='ab btn' style='left:60px;top:1232px;width:305px;height:76px;background:{t['sec']};font-size:28px'>每日擂主</div>
<div class='ab btn' style='left:385px;top:1232px;width:305px;height:76px;background:{t['sec']};font-size:28px'>顶顶乐</div>"""
def hud(t):
    return css(t)+f"""
<div class='ab c' style='top:80px;width:750px'><div style='font-size:24px;color:{t['sub']};letter-spacing:4px'>第 1 回合 · 三局两胜</div><div style='font-size:72px;font-weight:700;margin-top:4px'>0 <span style='color:{t['sub']};font-weight:400'>:</span> 0</div></div>
<div class=ab style='left:50px;top:250px;width:300px'><div style='display:flex;justify-content:space-between;font-size:24px'><b>你</b><span style='color:{t['sub']}'>110</span></div><div class=bar style='margin-top:10px'><div style='width:100%;height:100%;background:{t['my']}'></div></div></div>
<div class=ab style='left:400px;top:250px;width:300px'><div style='display:flex;justify-content:space-between;font-size:24px'><span style='color:{t['sub']}'>100</span><b>电脑</b></div><div class=bar style='margin-top:10px'><div style='width:91%;height:100%;background:{t['op']};margin-left:9%'></div></div></div>
<div class=ab style='left:0;top:820px;width:750px;height:514px;background:{t['ground']};border-radius:50% 50% 0 0/40px 40px 0 0'></div>
<img class=ab src='{W}g_me.png' style='left:40px;top:560px;height:270px'>
<img class=ab src='{W}g_op.png' style='left:460px;top:560px;height:270px'>
<div class='ab c' style='top:880px;width:750px;font-size:26px;color:{t['sub']}'>对手架势 <b style='color:{t['ink']}'>低角度</b> · 选择你的角度</div>
<div class=ab style='left:60px;top:950px;width:630px;display:flex;gap:20px'>{''.join(f"<div class=btn style='flex:1;height:84px;font-size:30px;background:{t['pri'] if s else t['sec']};color:{t['priT'] if s else t['ink']}'>{s and '✓ ' or ''}{n}</div>" for n,s in [('低',0),('中',1),('高',0)])}</div>
<div class=ab style='left:90px;top:1080px;width:570px'><div class=bar style='height:16px;position:relative'><div style='position:absolute;left:62%;width:14%;height:100%;background:{t['my']}'></div></div><div style='position:absolute;left:72%;top:-10px;width:8px;height:36px;border-radius:4px;background:{t['ink']}'></div></div>
<div class='ab btn' style='left:155px;top:1160px;width:440px;height:112px;background:{t['pri']};color:{t['priT']};font-size:38px;letter-spacing:6px'>起跳顶角</div>"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':750,'height':1334})
    for k,t in T.items():
        for n,f in [('home',home),('hud',hud)]:
            open('t.html','w').write('<meta charset=utf-8>'+f(t));pg.goto(W+'t.html');pg.wait_for_timeout(300);pg.screenshot(path=f'../{k}_{n}.png')
    b.close()
from PIL import Image
ks=list(T);o=Image.new('RGB',(3*375+4*20,2*667+3*20),'#ddd')
for i,k in enumerate(ks):
    for j,n in enumerate(['home','hud']):
        o.paste(Image.open(f'../{k}_{n}.png').convert('RGB').resize((375,667)),(20+i*395,20+j*687))
o.save('../overview.png')
