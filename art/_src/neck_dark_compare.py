import sys; sys.path.insert(0,'/workspace/goat-game/art/_src'); from goatlib import *
from PIL import ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
B={'idle':(640,200,940,520),'jump':(620,230,920,550),'clash':(700,600,1000,920)}
C=[('#111111','黑'),('#333333','#333'),('#8b5a2b','棕'),('#ffffff','白')]
cw,ch=300,320; o=Image.new('RGB',(len(C)*2*cw,3*(ch+24)+34),(238,240,232)); d=ImageDraw.Draw(o)
d.text((8,8),'脖子/喉部浅色毛：每组 左=修改前(v8d_pre，浅毛在 face 层不换色) 右=修改后(并入羊毛灰度 mask，跟羊毛色)',fill=(0,0,0),font=F)
for r,p in enumerate(['idle','jump','clash']):
    b=B[p]
    for i,(wc,n) in enumerate(C):
        for j,root in enumerate([ART+'/_v8d_pre',ART]):
            im=onbg(goat(root,p,'fluffy','curl',wc,'#d9b77a'))[b[1]:b[3],b[0]:b[2]]
            x=(i*2+j)*cw; y=34+r*(ch+24); o.paste(Image.fromarray(im),(x,y+24)); d.text((x+4,y+2),f"{p} {n} {'前' if j==0 else '后'}",fill=(0,0,0),font=F)
o.save(ART+'/neck_dark_compare.png',optimize=True)
