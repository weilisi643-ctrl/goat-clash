# green-fringe check (mirrors gc_repo tools/p13_shots.py detect): canvas source-over composite on #3cc83c,
# fringe = goat interior (>7px full / >1px _320 from any transparent px) that reads green; tint = layer px alpha>8 with g>r+12 & g>b+12.
import numpy as np, glob, os, sys, json
from PIL import Image
from scipy import ndimage as nd
ROOT=sys.argv[1] if len(sys.argv)>1 else '/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(p).convert('RGBA')).astype(float)
def hexc(c): return np.array([int(c[i:i+2],16) for i in (1,3,5)],float)
def comp(pose,w,wc,sfx):
    seq=[(f'wool/{w}_{pose}',wc,255)]+([(f'wool/spots_mask_{pose}','#8b5a2b',255)] if w=='spots' else [])+[(f'wool/knee_{pose}','#a8774a',255),(f'body/body_{pose}',None,0),(f'beard/beard_{pose}',wc if 'v8c' not in ROOT or True else None,255),(f'face/face_{pose}',None,0),(f'horn/curl_{pose}','#d9b77a',128)]
    rgb=None; al=None
    for f,c,dv in seq:
        a=L(f'{ROOT}/{f}{sfx}.png')
        if c and not (f.startswith('beard') and BEARD_RAW): a[...,:3]=np.clip(a[...,:3]/dv*hexc(c),0,255)
        sa=a[...,3:]/255
        if rgb is None: rgb=np.zeros(a.shape[:2]+(3,)); al=np.zeros(a.shape[:2]+(1,))
        rgb=a[...,:3]*sa+rgb*(1-sa); al=sa+al*(1-sa)   # premultiplied over
    return rgb,al[...,0]
BEARD_RAW='_v8c_pre' in ROOT or '_v8b_pre' in ROOT
tint=0
files=[f for f in glob.glob(ROOT+'/**/*.png',recursive=True) if '/_v' not in f[len(ROOT):] and '/fx/' not in f and os.path.basename(os.path.dirname(f)) not in ('',)]
files=[f for f in files if any(s in f for s in ['/wool/','/body/','/face/','/beard/','/horn/','/parts/'])]
for f in files:
    a=L(f); m=(a[...,3]>8)&(a[...,1]>a[...,0]+12)&(a[...,1]>a[...,2]+12); tint+=int(m.sum())
fr={}; BG=hexc('#3cc83c')
for pose in ['idle','jump','clash']:
    for w in ['fluffy','short','spots','cloud']:
        for wc in ['#ffffff','#333333']:
            for sfx,er in [('',7),('_320',1)]:
                rgb,al=comp(pose,w,wc,sfx); g=rgb+BG*(1-al[...,None])
                inner=nd.binary_erosion(al>0,structure=np.ones((3,3),bool),iterations=er,border_value=0)  # square, like PIL MinFilter
                fr[f'{pose}_{w}_{wc}{sfx}']=int((inner&(g[...,1]>g[...,0]+30)&(g[...,1]>g[...,2]+30)).sum())
print(json.dumps(dict(root=ROOT,layer_files=len(files),tint_px=tint,fringe_total=sum(fr.values()),fringe_full=sum(v for k,v in fr.items() if not k.endswith('_320')),fringe_320=sum(v for k,v in fr.items() if k.endswith('_320')),worst=sorted(fr.items(),key=lambda x:-x[1])[:6])))
