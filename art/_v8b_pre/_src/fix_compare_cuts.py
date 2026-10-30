import numpy as np, os, glob
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',24)
COL={'body':(200,200,200),'head':(230,80,80),'tail':(80,80,230),'leg_back_near':(60,180,60),'leg_back_far':(20,90,20),'leg_front_near':(230,180,40),'leg_front_far':(140,90,0)}
def labmap(root,pose):
    lab=np.full((1024,1152),'',object)
    for p in COL:
        for f in [f'{root}/parts/{pose}/{p}/fluffy_{pose}.png',f'{root}/parts/{pose}/{p}/body_{pose}.png',f'{root}/parts/{pose}/{p}/face_{pose}.png']:
            if os.path.exists(f):
                a=np.asarray(Image.open(f))[...,3]
                if p=='body' or root==ART: a=a*(1)  # v2 files contain underlap: use own-region only
                lab[(a==255)&(lab=='')]=p if True else lab
    return lab
def own_v2(pose):
    return np.load(f'/tmp/lab_{pose}.npy').astype(object)
rows=[]
for pose in ['jump','clash']:
    g=Image.open(f'{ART}/_v8_pre/parts/{pose}/body/fluffy_{pose}.png')  # placeholder size
    base=np.zeros((1024,1152,3)); base[:]=255
    for f in [f'wool/fluffy_{pose}',f'body/body_{pose}',f'beard/beard_{pose}',f'face/face_{pose}']:
        a=np.asarray(Image.open(f'{ART}/{f}.png').convert('RGBA')).astype(float); al=a[...,3:]/255; base=a[...,:3]*al+base*(1-al)
    vis=np.asarray(Image.open(f'{ART}/wool/fluffy_{pose}.png'))[...,3]>0
    panels=[]
    for name,lab in [('修复前 v1',labmap(ART+'/_v8_pre',pose)),('修复后 v2',own_v2(pose))]:
        im=base.copy()*0.75+64
        for k,c in COL.items(): m=(lab==k)&vis; im[m]=im[m]*0.55+np.array(c)*0.45
        edge=np.zeros(vis.shape,bool)
        for k in COL: m=lab==k; edge|=m^nd.binary_erosion(m)
        edge&=vis&nd.binary_erosion(vis,iterations=2); edge=nd.binary_dilation(edge)
        im[edge]=[255,0,0]
        p=Image.fromarray(im.astype(np.uint8)); ImageDraw.Draw(p).text((20,20),f'{pose} {name}（红线=切线）',fill=(0,0,0),font=F); panels.append(p)
    rows.append(panels)
o=Image.new('RGB',(1152*2,1024*2),(255,255,255))
for r,ps in enumerate(rows):
    for c,p in enumerate(ps): o.paste(p,(c*1152,r*1024))
o.resize((1728,1536),Image.LANCZOS).save(ART+'/fix_compare_cuts.png',optimize=True)
