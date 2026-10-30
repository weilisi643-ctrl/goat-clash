import numpy as np, json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,'/workspace/goat-game/art/_src'); from verify_parts import stack, over, J, ART
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
def part_img(pose,part,w='fluffy',h='curl',wc='#ffffff',hc='#d9b77a'):
    d=np.zeros((1024,1152,4))
    for l in stack(f'parts/{pose}/{part}',pose,w,h,wc,hc,''): d=over(d,l)
    return Image.fromarray(d.astype(np.uint8),'RGBA')
COL={'horn':(200,120,0),'head':(220,40,40),'body':(60,60,60),'tail':(40,40,220),'leg_back_near':(0,150,0),'leg_back_far':(0,90,0),'leg_front_near':(220,150,0),'leg_front_far':(140,80,0)}
SC=0.5; cw,ch=int(1152*SC),int(1024*SC)
pv=Image.new('RGB',(cw*3+40,ch*2+380),(236,240,232)); dr=ImageDraw.Draw(pv)
dr.text((20,8),'部件拆分（上：合成+轴心；中：部件错开显示）—— idle / jump / clash',fill=(30,30,30),font=F)
for i,(pose,P) in enumerate(J['poses'].items()):
    x0=10+i*(cw+10)
    full=Image.new('RGBA',(1152,1024)); expl=Image.new('RGBA',(1152,1024))
    off={'head':(60,-40),'tail':(-50,0),'leg_back_near':(-20,50),'leg_back_far':(10,50),'leg_front_near':(10,50),'leg_front_far':(40,50),'body':(0,0),'horn':(60,-40)}
    for part in J['part_draw_order']:
        im=part_img(pose,part); full.alpha_composite(im); expl.alpha_composite(im,dest=off[part]) if False else expl.paste(im,off[part],im)
    for img,y0,shift in [(full,40,False),(expl,40+ch+10,True)]:
        g=img.resize((cw,ch),Image.LANCZOS); pv.paste(g,(x0,y0),g); d=ImageDraw.Draw(pv)
        for k,(px,py) in P['pivots'].items():
            if k in ('body_alt_foot_anchor','horn'): continue
            o=off[k] if shift else (0,0); X,Y=x0+(px+o[0])*SC,y0+(py+o[1])*SC
            d.ellipse([X-5,Y-5,X+5,Y+5],fill=COL[k],outline=(255,255,255)); d.text((X+6,Y-10),k.replace('leg_',''),fill=COL[k],font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',13))
        ax,ay=x0+511*SC,y0+995*SC; d.line([(ax-8,ay),(ax+8,ay)],fill=(255,0,255),width=2); d.line([(ax,ay-8),(ax,ay+8)],fill=(255,0,255),width=2)
    dr.text((x0+5,42),pose,fill=(30,30,30),font=F)
y=40+2*ch+30; dr.text((20,y),'特效贴图（灰度类示例换色：尘土 #c8b08a，羊毛碎片 #ffffff/#f6d6e6/#3a3a3a，冲击波 #fff2c0）',fill=(30,30,30),font=F)
fx=json.load(open(ART+'/fx/fx.json'))['files']; tints={'dust':'#c8b08a','wool_fluff_0':'#ffffff','wool_fluff_1':'#f6d6e6','wool_fluff_2':'#3a3a3a','shockwave':'#fff2c0'}
x=20; bg=(90,110,80)
dr.rectangle([10,y+30,pv.width-10,y+320],fill=bg)
for m in fx:
    a=np.asarray(Image.open(f"{ART}/{m['file']}").convert('RGBA')).astype(float)
    for k,c in tints.items():
        if os.path.basename(m['file']).startswith(k):
            cc=np.array([int(c[i:i+2],16) for i in (1,3,5)]); a[...,:3]=a[...,:3]/255*cc
    im=Image.fromarray(a.astype(np.uint8),'RGBA'); s=min(1,240/im.width) if im.width>128 else (2 if im.width<=64 else 1)
    im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    if x+im.width>pv.width-20: break
    pv.paste(im,(x,y+50),im); dr.text((x,y+295),os.path.basename(m['file'])[:-4],fill=(255,255,255),font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)); x+=im.width+12
pv.save(ART+'/parts_preview.png',optimize=True)
