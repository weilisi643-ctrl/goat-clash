# v10 pass 2: cloud scallop crescents -> solid puffs (closing r=8 of cloud alpha, filled with cloud texture);
# clash 641,861 wedge between front legs (all styles) -> local closing r=8 within 30px.
import numpy as np, sys
from scipy import ndimage as nd
sys.argv=['x']; exec(open('/workspace/goat-game/art/_src/director_fix.py').read().split('S={}')[0])
def disk(r): y,x=np.ogrid[-r:r+1,-r:r+1]; return x*x+y*y<=r*r
ST={}
for pose in ['idle','jump','clash']:
    for w in ['fluffy','short','spots','cloud']:
        W=L(f'wool/{w}_{pose}.png'); m=W[...,3]>128; tgt=np.zeros_like(m)
        if w=='cloud': tgt|=nd.binary_closing(np.pad(m,20),disk(8))[20:-20,20:-20]&~m
        if pose=='clash':
            win=np.zeros_like(m); win[831:892,611:672]=True
            tgt|=nd.binary_closing(m,disk(8))&~m&win
        if not tgt.any(): continue
        good=W[...,3]>200; W=woolfill.fill(W,good,tgt,w); W[tgt,3]=255; ST[f'{w}_{pose}']=int(tgt.sum())
        save(W,f'wool/{w}_{pose}.png',wool_small)
        if w=='spots':
            M=L(f'wool/spots_mask_{pose}.png'); sp=np.asarray(Image.open(f'{ART}/wool/spots_{pose}_320.png').convert('RGBA'))[...,3]
            def msmall(sa,sp=sp): sa[...,3]=np.minimum(sa[...,3],sp); return sa
            save(M,f'wool/spots_mask_{pose}.png',msmall)
print(ST)
