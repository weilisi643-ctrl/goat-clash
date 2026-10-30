import json,os
from PIL import Image,ImageDraw,ImageFont
D=os.path.dirname(os.path.abspath(__file__)); F=D+'/../_fonts/ZCOOLKuaiLe-Regular.ttf'; T=json.load(open(D+'/theme_tokens.json')); C=T['colors']
f=lambda s: ImageFont.truetype(F,s); I=lambda p: Image.open(p).convert('RGBA')
# spec sheet (2x of 375-wide logic)
W,H=1500,1640; im=Image.new('RGB',(W,H),C['bg']); d=ImageDraw.Draw(im); ink=C['stroke']
d.text((40,30),'山羊对撞 UI 规范 v3（逻辑宽 375，图中为 @2x）',font=f(44),fill=ink)
y=110; d.text((40,y),'色值',font=f(30),fill=ink); y+=45
keys=['bg','bgResult','primaryGreen','resultDeepGreen','accentYellow','accentBlue','accentOrange','accentRed','cardWhite','stroke','text','textSub','lockedGray','disabledFill']
for i,k in enumerate(keys):
    x=40+(i%7)*205; yy=y+(i//7)*130
    d.rounded_rectangle([x,yy,x+180,yy+70],14,fill=C[k],outline=ink,width=4); d.text((x,yy+76),k,font=f(20),fill=ink); d.text((x,yy+100),C[k],font=f(18),fill=ink)
y+=280; d.text((40,y),'字号（逻辑 px）',font=f(30),fill=ink); y+=45; x=40
for k,v in T['fontSize'].items():
    if k=='min': continue
    d.text((x,y+(112-v*2)),f'{k} {v}',font=f(v*2 if v*2<=96 else 96),fill=ink); x+=max(160,int(f(min(v*2,96)).getlength(f'{k} {v}'))+30)
    if x>1100: x=40; y+=120
y+=140; d.text((40,y),'按钮 5 态 + 按下态',font=f(30),fill=ink); y+=45
row=[('btn_primary','主要'),('btn_primary_pressed','主要·按下'),('btn_secondary','次要'),('btn_secondary_pressed','次要·按下')]
row2=[('btn_selected','选中'),('btn_unselected','未选'),('btn_disabled','禁用'),('btn_locked','锁定'),('btn_arrow','箭头')]
for r in (row,row2):
    x=40
    for n,l in r:
        p=I(f'{D}/slices/{n}@2x.png'); im.paste(p,(x,y),p); d.text((x,y+p.height+4),l,font=f(20),fill=ink); x+=p.width+40
    y+=150
d.text((40,y),'关卡卡 3 态 / 胶囊',font=f(30),fill=ink); y+=45; x=40
for n,l in [('card_level_open','可玩'),('card_level_current','当前'),('card_level_locked','锁定'),('pill_hint','对手提示胶囊'),('pill_round','回合胶囊')]:
    p=I(f'{D}/slices/{n}@2x.png'); im.paste(p,(x,y),p); d.text((x,y+p.height+4),l,font=f(20),fill=ink); x+=p.width+50
y+=290
for t in ['描边 #2F3727：按钮/胶囊 2，面板 2.5，比分字 5，标题字 6（逻辑 px）；角色不描边',
          '圆角：按钮 11，小按钮 9，胶囊全圆，面板 18，关卡卡 14；投影 = 实心硬投影无模糊，下移 3.5/6',
          '主按钮：白底 + 绿厚底 6（#8CCB4E）；按下整体下移 6、厚底消失，60ms；禁用不响应、锁定可点提示',
          '草叶装饰：只在背景层，距屏幕边/按钮/卡片/羊 不小于 16，不进入安全区与刘海区，不压文字']:
    d.text((40,y),t,font=f(24),fill=ink); y+=40
im.save(D+'/spec_sheet.png')
# preview
A=['title_perfect','title_win','title_lose','deco_star','deco_star_small','deco_dash','deco_burst','pedestal','contact_shadow']
pv=Image.new('RGB',(1500,760),C['bg']); pv.paste(C['bgResult'],(750,0,1500,760)); d=ImageDraw.Draw(pv)
for half,bx in [(0,0),(1,750)]:
    x=bx+30; y=30
    for n in A[:3]:
        p=I(f'{D}/assets/{n}@2x.png'); pv.paste(p,(x,y),p); y+=p.height+20
    x=bx+30
    for n in A[3:7]:
        p=I(f'{D}/assets/{n}@2x.png'); pv.paste(p,(x+(450 if n!='deco_burst' else 450),0),p) if False else pv.paste(p,(x+430,30+A[3:7].index(n)*80),p)
    p=I(f'{D}/assets/pedestal@2x.png'); pv.paste(p,(bx+40,600),p); s=I(f'{D}/assets/contact_shadow@2x.png'); pv.paste(s,(bx+420,620),s)
    d.text((bx+40,560),'展示台底座',font=f(22),fill=C['stroke'] if not half else '#FFFFFF'); d.text((bx+420,580),'软接触阴影',font=f(22),fill=C['stroke'] if not half else '#FFFFFF')
pv.save(D+'/preview.png'); print('ok')
