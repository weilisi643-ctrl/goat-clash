import numpy as np
from PIL import Image, ImageDraw, ImageFont
ART='/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(p).convert('RGBA')).astype(float)
def comp(root,pose,wc):
    d=np.zeros((1024,1152,3)); d[:]=[60,200,60]
    c=np.array([int(wc[i:i+2],16) for i in (1,3,5)])
    for p in [f'wool/fluffy_{pose}',f'wool/knee_{pose}',f'body/body_{pose}',f'beard/beard_{pose}',f'face/face_{pose}']:
        a=L(f'{root}/{p}.png')
        if 'wool' in p: a[...,:3]=a[...,:3]/255*(c if 'fluffy' in p else np.array([168,119,74]))
        al=a[...,3:]/255; d=a[...,:3]*al+d*(1-al)
    return d
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
J={'idle':[(690,250,790,350),(770,280,870,380),(790,400,890,500)],'clash':[(800,640,900,740),(820,700,920,800),(730,780,830,880)]}
rows=[]
for pose,boxes in J.items():
  for wc in ['#ffffff','#333333']:
    b0,b1=comp(ART+'/_v8_pre',pose,wc),comp(ART,pose,wc)
    row=Image.new('RGB',(6*300+10,320),(240,240,240)); d=ImageDraw.Draw(row)
    for i,b in enumerate(boxes):
        for j,src in enumerate([b0,b1]):
            im=Image.fromarray(src[b[1]:b[3],b[0]:b[2]].astype(np.uint8)).resize((290,290),Image.NEAREST); row.paste(im,(i*600+j*295,28))
        d.text((i*600,2),f"{pose} {['耳','眼','胡子'][i]} {wc}  左=修复前 右=修复后",fill=(0,0,0),font=F)
    rows.append(row)
o=Image.new('RGB',(rows[0].width,320*len(rows)),(255,255,255))
for i,r in enumerate(rows): o.paste(r,(0,i*320))
o.save(ART+'/fix_compare_green.png',optimize=True)
