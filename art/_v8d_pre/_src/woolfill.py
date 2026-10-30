# natural-looking wool fill for new pixels: blurred nearest base shade x style texture detail
import numpy as np
from PIL import Image
from scipy import ndimage as nd
SRC='/workspace/goat-game/art/_src'; AMP=dict(fluffy=0.45,short=0.25,spots=0.3,cloud=0.5); _T={}
def tex(w,shape):
    if w not in _T:
        t=np.asarray(Image.open(f'{SRC}/tex_{w}.jpg').convert('L')).astype(float); _T[w]=t/t.mean()
    t=_T[w]; n=t.shape[0]; yy,xx=np.mgrid[:shape[0],:shape[1]]
    return t[(yy*2)%n,(xx*2)%n]
def fill(W,good,tgt,w,sigma=5):
    """W: HxWx4 float gray wool layer; fills RGB at tgt from nearby good pixels with texture."""
    if not tgt.any() or not good.any(): return W
    _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True)
    base=W[...,0].copy(); base[~good]=W[iy,ix,0][~good]
    base=nd.gaussian_filter(base,sigma); det=tex(w,base.shape)
    g=base*(1-AMP[w]+AMP[w]*det)
    for c in range(3): W[...,c]=np.where(tgt,np.clip(g,0,255),W[...,c])
    return W
