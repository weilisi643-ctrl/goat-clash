# v8c pipeline step (after fix_edges.py): beard becomes a gray mask recolored like wool (gray/255 x woolColor).
import numpy as np, json, os, imagequant
from PIL import Image
ART='/workspace/goat-game/art'
for pose in ['idle','jump','clash']:
    rel=f'beard/beard_{pose}.png'; a=np.asarray(Image.open(f'{ART}/{rel}').convert('RGBA')).astype(float)
    m=a[...,3]>128; L=a[...,:3]@[0.299,0.587,0.114]
    hi=np.percentile(L[m],98); L=np.clip(L/hi*250,0,255)   # brightest strands ~250, keeps dark/light strand shading
    o=np.dstack([L,L,L,a[...,3]]); o=np.round(o).astype(np.uint8); o[o[...,3]<3]=0
    im=Image.fromarray(o,'RGBA'); im.save(f'{ART}/{rel}',optimize=True,compress_level=9)
    sm=im.resize((360,320),Image.LANCZOS); sa=np.asarray(sm).copy(); sa[sa[...,3]<3]=0
    imagequant.quantize_pil_image(Image.fromarray(sa,'RGBA'),dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90).save(f'{ART}/'+rel.replace('.png','_320.png'),optimize=True)
m=json.load(open(ART+'/manifest.json'))
for f in m['files']:
    if f['file'].startswith('beard/'): f['kind']='gray_mask'
    f['bytes']=os.path.getsize(f"{ART}/{f['file']}"); f['small_bytes']=os.path.getsize(f"{ART}/{f['small']}")
m['recolor']['color']='彩色原样绘制，不换色（body 含蹄子、耳内粉色；face 含眼鼻嘴）'
m['recolor']['beard']='v8c 起胡子为灰度 mask，与羊毛同色：RGB = 灰度/255 × woolColor（同 data.woolColors），保留明暗层次；最亮约 250'
m['beard_recolor']='gray_mask × woolColor'
json.dump(m,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1); print('ok')
