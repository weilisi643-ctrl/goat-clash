# v8b green-fringe: horn layers had a 1-3px half-transparent rim (alpha 60-190) inside the goat outline -> background showed through.
# Harden it (alpha>=90 not on the outermost px -> 255; rest steepened). Runs once (manifest flag), full + _320.
import numpy as np, json, glob
from PIL import Image
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; m=json.load(open(ART+'/manifest.json'))
if m.get('horn_edge_fix'): raise SystemExit('already applied')
for f in glob.glob(ART+'/horn/*.png'):
    im=Image.open(f); pal=im.mode=='P'; a=np.asarray(im.convert('RGBA')).copy(); aa=a[...,3].astype(float)
    st=np.clip((aa-24)*1.45,0,255); a[...,3]=np.where(nd.binary_erosion(aa>0,iterations=1)&(aa>=90),255,st).astype(np.uint8)
    o=Image.fromarray(a,'RGBA')
    if f.endswith('_320.png'):
        import imagequant; o=imagequant.quantize_pil_image(o,dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90)
    o.save(f,optimize=True)
m['horn_edge_fix']='v8b: 角的半透明内沿收紧（alpha≥90 且不在最外 1px → 255），去除游戏里透出背景的绿边'
json.dump(m,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1); print('ok')
