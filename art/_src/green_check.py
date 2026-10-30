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
# --- game-like: _320 layers upscaled to s=7 (1024*0.1*7 = 717 px tall) one by one with bilinear (premultiplied), then source-over; MinFilter(15) interior.
def up(a,W,H):
    pm=a.copy(); pm[...,:3]*=a[...,3:]/255
    r=np.asarray(Image.fromarray(np.clip(pm,0,255).astype(np.uint8),'RGBA').resize((W,H),Image.BILINEAR)).astype(float)  # premultiplied resize
    o=r.copy(); s=np.maximum(r[...,3:],1e-6); o[...,:3]=np.where(r[...,3:]>0,r[...,:3]/s*255,0); return np.clip(o,0,255)
def game(pose,w,wc):
    H=717; W=int(round(H*1152/1024))
    seq=[(f'wool/{w}_{pose}',wc,255)]+([(f'wool/spots_mask_{pose}','#8b5a2b',255)] if w=='spots' else [])+[(f'wool/knee_{pose}','#a8774a',255),(f'body/body_{pose}',None,0),(f'beard/beard_{pose}',wc,255),(f'face/face_{pose}',None,0),(f'horn/curl_{pose}','#d9b77a',128)]
    rgb=np.zeros((H,W,3)); al=np.zeros((H,W,1))
    for f,c,dv in seq:
        a=L(f'{ROOT}/{f}_320.png')
        if c and not (f.startswith('beard') and BEARD_RAW): a[...,:3]=np.clip(a[...,:3]/dv*hexc(c),0,255)
        a=up(a,W,H); sa=a[...,3:]/255; rgb=a[...,:3]*sa+rgb*(1-sa); al=sa+al*(1-sa)
    al=al[...,0]; g=rgb+BG*(1-al[...,None]); inner=nd.binary_erosion(al>0,structure=np.ones((15,15),bool),border_value=0)
    fr_=int((inner&(g[...,1]>g[...,0]+30)&(g[...,1]>g[...,2]+30)).sum())
    out=~nd.binary_fill_holes(al>0); hl,n=nd.label((al==0)&~out); sz=nd.sum(np.ones_like(al),hl,range(1,n+1)) if n else []
    holes=int(sum(s for s in sz if s<400)); return fr_,holes,(inner&(g[...,1]>g[...,0]+30)&(g[...,1]>g[...,2]+30))
GM={}
for pose in ['idle','jump','clash']:
    for w in ['fluffy','short','spots','cloud']:
        f_,h_,_=game(pose,w,'#ffffff'); GM[f'{pose}_{w}']=(f_,h_)
print(json.dumps(dict(game_like_x2colors=dict(fringe=2*sum(v[0] for v in GM.values()),pinholes=2*sum(v[1] for v in GM.values())),per=GM)))
