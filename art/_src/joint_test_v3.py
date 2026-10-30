import numpy as np, json, sys, os
USE_PATCH=int(sys.argv[1]) if len(sys.argv)>1 else 1
OUT=sys.argv[2] if len(sys.argv)>2 else 'parts_joint_test_v3.png'
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
sys.path.insert(0,'/workspace/goat-game/art/_src'); from verify_parts import stack, over, J, ART
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
def part_img(pose,part,w,wc):
    d=np.zeros((1024,1152,4))
    for l in stack(f'parts/{pose}/{part}',pose,w,'curl',wc,'#d9b77a',''): d=over(d,l)
    return Image.fromarray(d.astype(np.uint8),'RGBA')
panels=[]; stats={}
for pose in ['idle','jump','clash']:
    P=J['poses'][pose]['pivots']
    for w,wc in [('fluffy','#ffffff'),('short','#333333')]:
        parts={p:part_img(pose,p,w,wc) for p in J['part_draw_order']}
        for sg in [1,-1]:
            rot={'head':15*sg,'tail':15*sg,'leg_front_near':12*sg,'leg_back_near':12*sg,'leg_front_far':-12*sg,'leg_back_far':-12*sg,'body':0,'horn':15*sg}
            c=Image.new('RGBA',(1152,1024))
            for jp in ['head','tail']:
                for k,cc in [(w,wc)]+([('spots_mask','#8b5a2b')] if w=='spots' else []):
                    fp=f'{ART}/parts/{pose}/{jp}_patch/{k}_{pose}_a{rot[jp]:+d}.png'
                    if os.path.exists(fp) and USE_PATCH:
                        pa=np.asarray(Image.open(fp).convert('RGBA')).astype(float); col=np.array([int(cc[i:i+2],16) for i in (1,3,5)]); pa[...,:3]=pa[...,:3]/255*col
                        c.alpha_composite(Image.fromarray(pa.astype(np.uint8),'RGBA'))
            for p in J['part_draw_order']:
                im=parts[p]
                if rot[p]: im=im.convert('RGBa').rotate(rot[p],resample=Image.BICUBIC,center=tuple(P[p])).convert('RGBA')  # premultiplied, like canvas
                c.alpha_composite(im)
            a=np.asarray(c)[...,3]; inside=nd.binary_erosion(nd.binary_fill_holes(a>128),iterations=3)
            stats[f'{pose}/{w}/{"+" if sg>0 else "-"}']=int((inside&(a<250)).sum())
            b=Image.new('RGB',c.size,(110,170,110)); b.paste(c,(0,0),c); d=ImageDraw.Draw(b)
            d.text((20,20),f'{pose} {w} {wc}  头{15*sg:+d}° 补片{"开" if USE_PATCH else "关"} 近腿{12*sg:+d}° 远腿{-12*sg:+d}° 尾{15*sg:+d}°',fill=(0,0,0),font=F)
            panels.append(b.resize((768,683),Image.LANCZOS))
o=Image.new('RGB',(768*4,683*3))
for i,p in enumerate(panels): o.paste(p,((i%4)*768,(i//4)*683))
o.save(ART+'/'+OUT,optimize=True); print('interior pixels with alpha<250 after rotation:',stats)
