import numpy as np
from PIL import Image, ImageDraw, ImageFont
ART='/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA')).astype(float)
def tint(a,hexc):
    c=np.array([int(hexc[i:i+2],16) for i in (1,3,5)],float); o=a.copy(); o[...,:3]=a[...,:3]/255*c; return o
def over(dst,src):
    sa=src[...,3:]/255; dst[...,:3]=src[...,:3]*sa+dst[...,:3]*(1-sa); dst[...,3:]=np.maximum(dst[...,3:],src[...,3:]); return dst
def goat(pose,wool,horn,wc,hc):
    d=np.zeros((1024,1024,4))
    for lay in [tint(L(f'wool/{wool}_{pose}.png'),wc),tint(L(f'wool/knee_{pose}.png'),'#a8774a'),L(f'body/body_{pose}.png'),L(f'face/face_{pose}.png'),tint(L(f'horn/{horn}_{pose}.png'),hc)]:
        d=over(d,lay)
    return Image.fromarray(d.astype(np.uint8),'RGBA')
try: F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
except: F=ImageFont.load_default()
T=230; W=4*T+60; Hh=60+T+40+4*T+40
pv=Image.new('RGB',(W,Hh),(236,240,232)); dr=ImageDraw.Draw(pv)
dr.text((20,15),'姿态：待机 / 起跳 / 对撞（fluffy 白毛 + curl 米色角）',fill=(40,40,40),font=F)
for i,p in enumerate(['idle','jump','clash']):
    g=goat(p,'fluffy','curl','#ffffff','#d9b77a').resize((T+40,T+40),Image.LANCZOS); pv.paste(g,(20+i*(T+60),50),g)
wools=['fluffy','short','spots','cloud']; horns=['curl','straight','spiral','branch']
wc=['#ffffff','#f6d6e6','#cfe8ff','#3a3a3a','#ffe9a8','#c9f2c7']; hc=['#d9b77a','#ffd700','#c0c0c0','#ff7aa8','#7ad0ff','#8b5a2b']
y0=60+T+40; dr.text((20,y0-30),'4 羊毛（行）× 4 角形（列），随机换色示例',fill=(40,40,40),font=F)
for r,w in enumerate(wools):
    for c,h in enumerate(horns):
        g=goat('idle',w,h,wc[(r+c)%6],hc[(r*2+c)%6]).resize((T,T),Image.LANCZOS)
        x,y=30+c*T,y0+r*T; pv.paste(g,(x,y),g); dr.text((x+6,y+4),f'{w}/{h}',fill=(90,90,90),font=F)
pv.save(f'{ART}/preview.png',optimize=True); print(pv.size)
