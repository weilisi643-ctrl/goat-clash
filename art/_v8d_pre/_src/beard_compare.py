import numpy as np
from PIL import Image, ImageDraw, ImageFont
ART='/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(p).convert('RGBA')).astype(float)
def tint(a,c,div=255):
    c=np.array([int(c[i:i+2],16) for i in (1,3,5)],float); o=a.copy(); o[...,:3]=np.clip(a[...,:3]/div*c,0,255); return o
def over(d,s): sa=s[...,3:]/255; d[...,:3]=s[...,:3]*sa+d[...,:3]*(1-sa); d[...,3:]=np.maximum(d[...,3:],s[...,3:]); return d
def goat(root,pose,w,h,wc,hc,new):
    d=np.zeros((1024,1152,4)); b=L(f'{root}/beard/beard_{pose}.png')
    for lay in [tint(L(f'{root}/wool/{w}_{pose}.png'),wc),tint(L(f'{root}/wool/knee_{pose}.png'),'#a8774a'),L(f'{root}/body/body_{pose}.png'),tint(b,wc) if new else b,L(f'{root}/face/face_{pose}.png'),tint(L(f'{root}/horn/{h}_{pose}.png'),hc,128)]: d=over(d,lay)
    return d
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
WC=['#ffffff','#333333','#f6d6e6','#cfe8ff','#ffe9a8','#8b5a2b','#c9f2c7','#5a4a7a']; HC=['#d9b77a','#c0c0c0','#ff7aa8','#7ad0ff']
cell=(300,260); o=Image.new('RGB',(4*2*cell[0],4*cell[1]+30),(236,240,232)); dr=ImageDraw.Draw(o)
dr.text((10,6),'胡子换色对比：每组 左=修改前（固定白色胡子） 右=修改后（胡子 = 灰度/255 × 羊毛色）；头部特写',fill=(0,0,0),font=F)
pose='idle'; box=(600,250,1000,700)
for i,w in enumerate(['fluffy','short','spots','cloud']):
    for k,h in enumerate(['curl','straight','spiral','branch']):
        wc=WC[(i*4+k)%8]; hc=HC[(i+k)%4]
        for j,(root,new) in enumerate([(ART+'/_v8c_pre',False),(ART,True)]):
            d=goat(root,pose,w,h,wc,hc,new); bg=np.zeros(d.shape[:2]+(3,)); bg[:]=[150,185,140]; a=d[...,3:]/255; c=d[...,:3]*a+bg*(1-a)
            im=Image.fromarray(c[box[1]:box[3],box[0]:box[2]].astype(np.uint8)).resize((cell[0]-6,cell[1]-24),Image.LANCZOS)
            x=(k*2+j)*cell[0]; y=30+i*cell[1]; o.paste(im,(x+3,y+20))
            dr.text((x+4,y+2),f"{w}/{h} {wc} {'前' if j==0 else '后'}",fill=(0,0,0),font=F)
o.save(ART+'/beard_color_compare.png',optimize=True)
