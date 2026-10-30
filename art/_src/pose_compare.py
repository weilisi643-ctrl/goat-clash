import sys; sys.path.insert(0,'/workspace/goat-game/art/_src'); from goatlib import *
from PIL import ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19)
o=Image.new('RGB',(1728,552),(240,240,235)); d=ImageDraw.Draw(o)
for i,p in enumerate(['idle','jump','clash']):
    g=goat(ART,p,'fluffy','curl','#ffffff','#9a9a9a'); a=g[...,3]
    foot=int(np.nonzero(a.max(1)>128)[0].max()); im=Image.fromarray(onbg(g,(255,255,255))).resize((576,512),Image.LANCZOS)
    x0=i*576; o.paste(im,(x0,40)); s=0.5
    d.line((x0,40+995*s,x0+575,40+995*s),fill=(230,0,0),width=2); d.ellipse((x0+511*s-6,40+995*s-6,x0+511*s+6,40+995*s+6),outline=(0,0,230),width=2)
    d.text((x0+8,2),f'{p} 脚底 y={foot}，红线 y=995，蓝圈=锚点(511,995)',fill=(0,0,0),font=F); d.line((x0,40,x0,552),fill=(0,0,0),width=2)
o.save(ART+'/pose_compare.png',optimize=True)
