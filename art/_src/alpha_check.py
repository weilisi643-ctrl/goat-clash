# every asset PNG under art/ must carry alpha and must not have a solid background:
#  - mode RGBA/LA, or P/L/RGB with a tRNS transparency entry
#  - the 4 corners transparent (alpha 0) and >=20% of pixels transparent
# exempt: backups (_v*/), review images (top-level art/*.png, ui_mock*/, fx previews) which are opaque by design.
import os, sys, json, numpy as np
from PIL import Image
ART=sys.argv[1] if len(sys.argv)>1 else '/workspace/goat-game/art'
ASSET=('wool','body','face','beard','horn','parts','fx')
bad=[]; n=0; ex=0
for d,_,fs in os.walk(ART):
    rel=os.path.relpath(d,ART)
    for f in fs:
        if not f.endswith('.png'): continue
        top=rel.split(os.sep)[0]
        if top.startswith('_v') or top not in ASSET: ex+=1; continue
        p=os.path.join(d,f); im=Image.open(p); n+=1
        has=im.mode in ('RGBA','LA','PA') or 'transparency' in im.info
        a=np.asarray(im.convert('RGBA'))[...,3]
        corners=[a[0,0],a[0,-1],a[-1,0],a[-1,-1]]
        if not has or max(corners)>0 or (a==0).mean()<0.2: bad.append(dict(file=os.path.relpath(p,ART),mode=im.mode,alpha_channel=has,corners=[int(c) for c in corners],transparent_frac=round(float((a==0).mean()),3)))
print(json.dumps(dict(checked=n,exempt=ex,bad=len(bad),examples=bad[:8]),ensure_ascii=False))
sys.exit(1 if bad else 0)
