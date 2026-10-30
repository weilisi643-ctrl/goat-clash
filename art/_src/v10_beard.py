# v10: _320 beard longer (x1.45 downwards, anchored at top/chin row), stays grayscale mask (recolored gray/255 x wool), + soft gray highlight strip.
import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
A='/workspace/goat-game/art/beard'; R={}
for p in ['idle','jump','clash']:
    f=f'{A}/beard_{p}_320.png'; a=np.asarray(Image.open(f).convert('RGBA')).astype(float)
    before=[int((a[...,3]>0).sum()),int((a[...,3]>200).sum())]
    ys,xs=np.nonzero(a[...,3]>0); y0,y1=ys.min(),ys.max()+1; x0,x1=xs.min(),xs.max()+1
    crop=a[y0:y1,x0:x1]; h=y1-y0; nh=int(round(h*1.45))
    pm=crop.copy(); pm[...,:3]*=crop[...,3:]/255
    im=Image.fromarray(np.clip(pm,0,255).astype(np.uint8),'RGBA').resize((x1-x0,nh),Image.LANCZOS)
    r=np.asarray(im).astype(float); al=r[...,3]
    # taper the added tail a little so it ends in a point, keep crisp
    t=np.clip((np.arange(nh)-h)/(nh-h+1e-6),0,1)[:,None]; cx=(np.arange(x1-x0)-(x1-x0-1)/2)/((x1-x0)/2+1e-6)
    al=al*np.clip(1-np.abs(cx)[None,:]*t*0.9,0,1); al=np.clip((al-25)*1.6,0,255)
    g=np.where(r[...,3]>0,r[...,0]/np.maximum(r[...,3],1)*255,0)
    good=al>60; _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True); g=g[iy,ix]
    # highlight: centre column +18 gray, fading to edges and tip
    hl=np.clip(1-np.abs(cx)*1.6,0,1)[None,:]*np.clip(1-np.arange(nh)/nh,0.3,1)[:,None]*18
    g=np.clip(g+hl,0,250)
    out=np.zeros_like(a); out[y0:y0+nh,x0:x1]=np.dstack([g,g,g,al])
    o=out.astype(np.uint8); assert (o[...,0]==o[...,1]).all() and (o[...,1]==o[...,2]).all()
    Image.fromarray(o,'RGBA').save(f)
    R[p]=dict(before_a0=before[0],before_a200=before[1],after_a0=int((o[...,3]>0).sum()),after_a200=int((o[...,3]>200).sum()),len_px=[int(h),nh])
print(json.dumps(R))
