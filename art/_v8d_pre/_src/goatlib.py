import numpy as np
from PIL import Image
ART='/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(p).convert('RGBA')).astype(float)
def tint(a,c,div=255):
    c=np.array([int(c[i:i+2],16) for i in (1,3,5)],float); o=a.copy(); o[...,:3]=np.clip(a[...,:3]/div*c,0,255); return o
def over(d,s): sa=s[...,3:]/255; d[...,:3]=s[...,:3]*sa+d[...,:3]*(1-sa); d[...,3:]=np.maximum(d[...,3:],s[...,3:]); return d
def goat(root,pose,w,h,wc,hc,beard_tint=True):
    d=np.zeros((1024,1152,4)); b=L(f'{root}/beard/beard_{pose}.png')
    seq=[tint(L(f'{root}/wool/{w}_{pose}.png'),wc)]+([tint(L(f'{root}/wool/spots_mask_{pose}.png'),'#8b5a2b')] if w=='spots' else [])
    seq+=[tint(L(f'{root}/wool/knee_{pose}.png'),'#a8774a'),L(f'{root}/body/body_{pose}.png'),tint(b,wc) if beard_tint else b,L(f'{root}/face/face_{pose}.png'),tint(L(f'{root}/horn/{h}_{pose}.png'),hc,128)]
    for s in seq: d=over(d,s)
    return d
def onbg(d,bg=(150,185,140)):
    a=d[...,3:]/255; return (d[...,:3]*a+np.array(bg,float)*(1-a)).astype(np.uint8)
