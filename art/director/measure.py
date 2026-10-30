# 只读测量脚本：不修改任何素材
import json,glob,os,collections
from PIL import Image
import numpy as np
from scipy import ndimage
A='/workspace/goat-game/art'; R='/workspace/gc_repo/art'
out={}
def top(path,n=8,q=8,mask_alpha=True):
    im=np.array(Image.open(path).convert('RGBA'));a=im[...,3]
    px=im[a>200][:,:3] if mask_alpha else im[...,:3].reshape(-1,3)
    qq=(px//q)*q+q//2
    c=collections.Counter(map(tuple,qq));tot=len(px)
    return [('#%02X%02X%02X'%k,v,round(v/tot*100,1)) for k,v in c.most_common(n)]
ui={}
for f in ['home','hud','result','g_home']:
    im=np.array(Image.open(f'{A}/ui_mock_v2/{f}.png').convert('RGB')).reshape(-1,3)
    c=collections.Counter(map(tuple,im));ui[f]=[('#%02X%02X%02X'%k,v) for k,v in c.most_common(10)]
out['ui_exact']=ui
out['body_idle']=top(f'{A}/body/body_idle.png',10)
out['face_idle']=top(f'{A}/face/face_idle.png',6)
for nm in ['ref_realistic']:
    out[nm]=top(f'{A}/base_side_realistic.png',10)
# 灰度 mask 统计
g={}
for p in sorted(glob.glob(f'{A}/wool/*.png')+glob.glob(f'{A}/beard/*.png')+glob.glob(f'{A}/horn/*.png')):
    im=np.array(Image.open(p).convert('RGBA'));a=im[...,3];L=im[...,:3].mean(-1)
    op=a>200;semi=(a>0)&(a<=200)
    r,gg,b=[im[...,i].astype(int) for i in range(3)]
    green=((gg-np.maximum(r,b))>25)&(a>0)
    lab,n=ndimage.label(~(a>0));sizes=ndimage.sum(np.ones_like(a),lab,range(1,n+1))
    edge=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))
    holes=[int(s) for i,s in enumerate(sizes,1) if i not in edge]
    g[os.path.relpath(p,A)]=dict(size=im.shape[1::-1][::-1] and [im.shape[1],im.shape[0]],opaque=int(op.sum()),semi=int(semi.sum()),
      Lmean=round(float(L[op].mean()),1) if op.any() else None,Lmax=int(L[op].max()) if op.any() else None,
      Lp5=int(np.percentile(L[op],5)) if op.any() else None,green=int(green.sum()),
      sat=int((np.ptp(im[...,:3].astype(int),-1)>12)[op].sum()),holes=len(holes),hole_px=sum(holes),hole_px_ge4=sum(h for h in holes if h>=4))
out['masks']=g
# 尺寸普查
sz=collections.Counter();bad=[]
for p in glob.glob(f'{A}/*/*.png'):
    if '/_' in p or 'ui_mock' in p or '/director/' in p: continue
    w,h=Image.open(p).size;sz[(w,h)]+=1
    if (w,h) not in [(1152,1024),(360,320)] and '/ui/' not in p and '/fx/' not in p: bad.append((os.path.relpath(p,A),w,h))
out['sizes']={f'{k[0]}x{k[1]}':v for k,v in sz.items()};out['size_outliers']=bad
# knee 覆盖腿部
kc={}
for pose in ['idle','jump','clash']:
    b=np.array(Image.open(f'{A}/body/body_{pose}.png').convert('RGBA'))[...,3]>0
    k=np.array(Image.open(f'{A}/wool/knee_{pose}.png').convert('RGBA'))[...,3]>0
    w=np.array(Image.open(f'{A}/wool/fluffy_{pose}.png').convert('RGBA'))[...,3]>0
    kc[pose]=dict(body_px=int(b.sum()),knee_px=int(k.sum()),body_not_wool=int((b&~w).sum()),knee_on_body_not_wool=int((k&b&~w).sum()))
out['knee']=kc
# repo 与 art 是否一致
import hashlib
diff=[]
for p in glob.glob(f'{R}/*/*.png'):
    q=p.replace(R,A)
    if os.path.exists(q) and hashlib.md5(open(p,'rb').read()).hexdigest()!=hashlib.md5(open(q,'rb').read()).hexdigest(): diff.append(os.path.relpath(p,R))
    if not os.path.exists(q): diff.append('仅repo:'+os.path.relpath(p,R))
out['repo_vs_art_diff']=diff
json.dump(out,open('measurements.json','w'),ensure_ascii=False,indent=1)
