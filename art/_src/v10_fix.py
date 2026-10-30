# v10: residual green/holes from gc_repo docs/p13_green_coords.json (game renderer @7234191).
#  a) cloud: detached crescent fragments of the scalloped edge (green inside the crescent) -> removed; small enclosed holes filled
#  b) short idle ear/horn-root wedge: short alpha >= fluffy within 40px of the horn
#  c) all styles: tiny enclosed gaps between touching legs/hooves (<=150 px of union silhouette) filled with wool
#  curl-horn centre pocket (idle ~742,242 / jump ~728,285) is design -> untouched. Idempotent-ish; run from _v10_pre copies.
import numpy as np, sys
from scipy import ndimage as nd
sys.argv=['x']; src=open('/workspace/goat-game/art/_src/director_fix.py').read().split('S={}')[0]; exec(src)
HORNS=['curl','straight','spiral','branch']; ST={}
for pose in ['idle','jump','clash']:
    F=L(f'wool/fluffy_{pose}.png'); oth=np.maximum.reduce([L(f'{k}/{k}_{pose}.png')[...,3] for k in ['body','face','beard']]+[L(f'wool/knee_{pose}.png')[...,3]])
    HN=np.maximum.reduce([L(f'horn/{h}_{pose}.png')[...,3] for h in HORNS])>128
    for w in ['fluffy','short','spots','cloud']:
        W=L(f'wool/{w}_{pose}.png'); n0=0
        if w=='cloud':
            m=W[...,3]>0; lab,n=nd.label(m,structure=np.ones((3,3)))
            sz=nd.sum(m,lab,range(1,n+1)); main=1+int(np.argmax(sz)); det=m&(lab!=main)&~nd.binary_dilation(oth>0,iterations=2)
            W[det,3]=0; n0+=int(det.sum())
        if w=='short':
            z=nd.binary_dilation(HN,iterations=40)&(F[...,3]>W[...,3]); good=W[...,3]>200
            W=woolfill.fill(W,good,z&~good,'short'); W[z,3]=F[z,3]; n0+=int(z.sum())
        U=np.maximum(W[...,3],oth)>128; enc=nd.binary_fill_holes(U|HN)&~U&~HN; lab,n=nd.label(enc)
        hornpk=nd.binary_dilation(HN,iterations=6)
        tgt=np.zeros_like(U)
        for i in range(1,n+1):
            c=lab==i
            if c.sum()<=150 and not (c&hornpk).any(): tgt|=c
        good=W[...,3]>200; W=woolfill.fill(W,good,tgt&~good,w); W[tgt,3]=255; n0+=int(tgt.sum())
        ST[f'{w}_{pose}']=n0
        if w=='spots':
            M=L(f'wool/spots_mask_{pose}.png'); M[...,3]=np.minimum(M[...,3],W[...,3]); 
        save(W,f'wool/{w}_{pose}.png',wool_small)
        if w=='spots':
            sp=np.asarray(Image.open(f'{ART}/wool/spots_{pose}_320.png').convert('RGBA'))[...,3]
            def msmall(sa,sp=sp): sa[...,3]=np.minimum(sa[...,3],sp); return sa
            save(M,f'wool/spots_mask_{pose}.png',msmall)
print(ST)
