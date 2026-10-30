# before(_v9_pre) / after comparison for the director report fixes -> art/director_fix_compare.png
import numpy as np, sys, os
from PIL import Image, ImageDraw, ImageFont
ART='/workspace/goat-game/art'; BG=np.array([0x3c,0xc8,0x3c],float)
FONT=ImageFont.truetype(next(f'{ART}/_fonts/'+f for f in os.listdir(ART+'/_fonts') if f.endswith(('ttf','otf'))),26)
def L(p): return np.asarray(Image.open(p).convert('RGBA')).astype(float)
def hexc(c): return np.array([int(c[i:i+2],16) for i in (1,3,5)],float)
def comp(root,pose,w,wc,sfx='',horn='curl',up=None):
    seq=[(f'wool/{w}_{pose}',wc,255)]+([(f'wool/spots_mask_{pose}','#8b5a2b',255)] if w=='spots' else [])+[(f'wool/knee_{pose}','#a8774a',255),(f'body/body_{pose}',None,0),(f'beard/beard_{pose}',wc,255),(f'face/face_{pose}',None,0),(f'horn/{horn}_{pose}','#d9b77a',128)]
    out=None
    for f,c,dv in seq:
        a=L(f'{root}/{f}{sfx}.png')
        if c: a[...,:3]=np.clip(a[...,:3]/dv*hexc(c),0,255)
        if up: a=np.asarray(Image.fromarray(a.astype(np.uint8),'RGBA').resize(up,Image.BILINEAR)).astype(float)
        if out is None: out=np.zeros(a.shape[:2]+(3,))+BG
        s=a[...,3:]/255; out=a[...,:3]*s+out*(1-s)
    return out.astype(np.uint8)
def rotparts(root,pose,w,leg,th,patch):
    import json; J=json.load(open(f'{ART}/parts.json')); piv=J['poses'][pose]['pivots'][leg]
    out=np.zeros((1024,1152,3))+BG; wc=hexc('#333333')
    def over(a):
        nonlocal out; s=a[...,3:]/255; out=a[...,:3]*s+out*(1-s)
    if patch:
        p=f'{root}/parts/{pose}/{leg}_patch/{w}_{pose}_a{th:+d}.png'
        if os.path.exists(p): a=L(p); a[...,:3]=a[...,:3]/255*wc; over(a)
    for part in J['part_draw_order']:
        for k,c,dv in [(w,wc,255),('knee',hexc('#a8774a'),255),('body',None,0),('beard',wc,255),('face',None,0),('curl',hexc('#d9b77a'),128)]:
            p=f'{root}/parts/{pose}/{part}/{k}_{pose}.png'
            if not os.path.exists(p): continue
            a=L(p)
            if c is not None: a[...,:3]=np.clip(a[...,:3]/dv*c,0,255)
            if part==leg: a=np.asarray(Image.fromarray(a.astype(np.uint8),'RGBA').convert('RGBa').rotate(th,resample=Image.BICUBIC,center=tuple(piv)).convert('RGBA')).astype(float)
            over(a)
    return out.astype(np.uint8)
B=ART+'/_v9_pre'; rows=[]
def crop(a,box,sz=(420,360)): return Image.fromarray(a).crop(box).resize(sz,Image.NEAREST if box[2]-box[0]<200 else Image.LANCZOS)
G=(717*1152//1024,717)
rows.append(('1 short_jump 羊毛补洞（游戏缩放 _320→717px）',[crop(comp(r,'jump','short','#333333','_320',up=G),(150,150,700,620)) for r in (B,ART)]))
rows.append(('2 cloud_idle 边缘收紧/碎孔（大图）',[crop(comp(r,'idle','cloud','#333333'),(100,300,700,820)) for r in (B,ART)]))
rows.append(('3 腿补丁：jump leg_front_near 转 -15°（左无补丁/右有补丁，均为新图）',[crop(rotparts(ART,'jump','short','leg_front_near',-15,p),(600,470,960,780)) for p in (False,True)]))
rows.append(('4 short_idle 角根/头部空隙（游戏缩放）',[crop(comp(r,'idle','short','#333333','_320',up=G),(480,120,760,360)) for r in (B,ART)]))
rows.append(('5 胡子小图 _320（放大 8 倍）',[crop(comp(r,'jump','fluffy','#333333','_320'),(228,112,278,155)) for r in (B,ART)]))
rows.append(('6 spots_mask 去麻点（大图）',[crop(comp(r,'idle','spots','#ffffff'),(150,330,650,760)) for r in (B,ART)]))
W=2*420+60; H=sum(360+50 for _ in rows)+60; can=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(can)
d.text((20,15),'修复前 (_v9_pre)                         修复后',fill='black',font=FONT); y=60
for t,(a,b) in rows:
    d.text((20,y),t,fill='black',font=FONT); can.paste(a,(20,y+40)); can.paste(b,(40+420,y+40)); y+=410
can.save(ART+'/director_fix_compare.png'); print(can.size)
