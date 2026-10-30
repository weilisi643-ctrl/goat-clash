# v9 (director report 2026-10-29) post-process after fix_edges/beard_gray, before parts.py/neck_patch.py.
# P1/P2 short wool holes (short follows fluffy silhouette inside), P3 cloud edge tightening + hole fill,
# P4 handled in neck_patch.py (leg patches), P5 beard _320 thicker, P6 spots_mask de-speckle. Idempotent.
import numpy as np, imagequant, sys
from PIL import Image
from scipy import ndimage as nd
sys.path.insert(0,'/workspace/goat-game/art/_src'); import woolfill
ART='/workspace/goat-game/art'
def L(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA')).astype(float)
def q(sm,path): imagequant.quantize_pil_image(sm,dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90).save(path,optimize=True)
def save(a,rel,small=None):
    a=np.clip(np.round(a),0,255).astype(np.uint8); a[a[...,3]<3]=0; im=Image.fromarray(a,'RGBA'); im.save(f'{ART}/{rel}',optimize=True,compress_level=9)
    sa=np.asarray(im.resize((360,320),Image.LANCZOS)).copy()
    if small: sa=small(sa)
    sa[sa[...,3]<3]=0; q(Image.fromarray(sa,'RGBA'),f'{ART}/'+rel.replace('.png','_320.png'))
def wool_small(sa):  # same steepening as fix_edges + close interior pinholes
    aa=sa[...,3].astype(float); st=np.clip((aa-24)*1.45,0,255)
    sa[...,3]=np.where(nd.binary_erosion(aa>0,iterations=1)&(aa>=90),255,st).astype(np.uint8)
    m=sa[...,3]>0; h=nd.binary_fill_holes(m)&~m; lab,n=nd.label(h)
    if n:
        sz=nd.sum(h,lab,range(1,n+1)); small_h=np.isin(lab,np.nonzero(sz<=40)[0]+1)
        good=sa[...,3]>200; _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True)
        sa[small_h]=sa[iy[small_h],ix[small_h]]; sa[small_h,3]=255
    return sa
def semi(a): return int(((a[...,3]>0)&(a[...,3]<=200)).sum())
def fill_holes(W,w,maxpx=2500,ref=None):
    m=W[...,3]>0; h=nd.binary_fill_holes(m)&~m; lab,n=nd.label(h); tgt=np.zeros_like(m)
    for i in range(1,n+1):
        c=lab==i
        if c.sum()<=maxpx and (ref is None or (ref[c]>0).mean()>0.5): tgt|=c
    lo=nd.binary_fill_holes(m)&(W[...,3]<250)&(nd.distance_transform_edt(nd.binary_fill_holes(m))>=3)
    tgt|=lo&(True if ref is None else ref>200)
    good=W[...,3]>200; W=woolfill.fill(W,good,tgt&~good,w); W[tgt,3]=255; return W,int(tgt.sum())
def seam(W,F,pose,w):  # near colour layers (beard/face/body) never thinner than fluffy -> no crack under the jaw/ear
    oa=np.maximum.reduce([L(f'{k}/{k}_{pose}.png')[...,3] for k in ['body','face','beard']])
    z=nd.binary_dilation(oa>0,iterations=12)&(F[...,3]>W[...,3]); good=W[...,3]>200
    W=woolfill.fill(W,good,z&~good,w); W[z,3]=F[z,3]; return W
S={}
for pose in ['idle','jump','clash']:
    F=L(f'wool/fluffy_{pose}.png'); fa=F[...,3]
    # --- short: inside the fluffy silhouette (eroded 4px) short must be solid -> removes belly/leg gaps (P2) and head/horn-root pockets (P1 #4)
    W=L(f'wool/short_{pose}.png'); inner=nd.binary_erosion(fa>200,iterations=4)
    tgt=inner&(W[...,3]<250); good=W[...,3]>200
    W=woolfill.fill(W,good,tgt&~good,'short'); W[tgt,3]=255
    HN=np.maximum.reduce([L(f'horn/{h}_{pose}.png')[...,3] for h in ['curl','straight','spiral','branch']])>128
    z=nd.binary_dilation(HN,iterations=30)&nd.binary_erosion(fa>200,iterations=1)&(W[...,3]<fa); good=W[...,3]>200
    W=woolfill.fill(W,good,z&~good,'short'); W[z,3]=fa[z]   # P1#4 horn-root/head pocket: match fluffy there
    W,n2=fill_holes(W,'short',ref=fa); W=seam(W,F,pose,'short'); S[f'short_{pose}']=int(tgt.sum())+n2
    save(W,f'wool/short_{pose}.png',wool_small)
    # --- cloud: crisp edges (P3). steepen alpha ramp until semi px <= fluffy, then fill holes
    C=L(f'wool/cloud_{pose}.png'); a0=C[...,3].copy(); target=semi(F)
    for lo_,hi_ in [(60,190),(80,180),(100,170),(110,160),(120,150)]:
        a=np.clip((a0-lo_)/(hi_-lo_),0,1)*255
        a=np.where(a0>=hi_,255,a); C2=C.copy(); C2[...,3]=a
        # drop isolated fog specks
        lab,n=nd.label(a>0); sz=nd.sum(a>0,lab,range(1,n+1)); C2[np.isin(lab,np.nonzero(sz<30)[0]+1),3]=0
        if semi(C2)<=target: break
    C2,nh=fill_holes(C2,'cloud')
    C2=seam(C2,F,pose,'cloud')
    S[f'cloud_{pose}']=dict(semi_before=semi(C),semi_after=semi(C2),fluffy=target,ramp=(lo_,hi_),holes_filled=nh)
    save(C2,f'wool/cloud_{pose}.png',wool_small)
    # --- spots_mask: de-speckle (P6): close small holes inside spots, harden soft fringe
    M=L(f'wool/spots_mask_{pose}.png'); a=M[...,3].copy()
    on=a>100; h=nd.binary_fill_holes(on)&~on   # keep the original soft spot shapes; only close small pits inside spots + drop specks
    lab,n=nd.label(h); hs=np.isin(lab,np.nonzero(nd.sum(h,lab,range(1,n+1))<=400)[0]+1) if n else h
    sp_=a>40; lab,n=nd.label(sp_); spk=np.isin(lab,np.nonzero(nd.sum(sp_,lab,range(1,n+1))<25)[0]+1) if n else sp_
    good=a>100; _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True); M[hs,:3]=M[iy[hs],ix[hs],:3]
    na=a.copy(); na[hs]=np.maximum(a[hs],nd.gaussian_filter(np.where(good,a,0),1.5)[hs]*0+255); na[spk]=0
    na=np.minimum(na,nd.grey_closing(na,size=(5,5)))*0+np.maximum(na,np.minimum(nd.grey_closing(na,size=(5,5)),255))
    M[...,3]=np.minimum(na,L(f'wool/spots_{pose}.png')[...,3]); S[f'spots_mask_{pose}']=dict(semi_before=int(((a>0)&(a<=200)).sum()),semi_after=semi(M),opaque_before=int((a>200).sum()),opaque_after=int((M[...,3]>200).sum()))
    sp=np.asarray(Image.open(f'{ART}/wool/spots_{pose}_320.png').convert('RGBA'))[...,3]
    def msmall(sa): sa[...,3]=np.minimum(sa[...,3],sp); return sa
    save(M,f'wool/spots_mask_{pose}.png',msmall)
    # --- beard _320 thicker (P5): >=60 opaque px, keeps gray shading
    B=L(f'beard/beard_{pose}.png')
    def bsmall(sa):
        aa=sa[...,3].astype(float); g=sa[...,0].astype(float)
        a1=np.maximum(aa,nd.grey_dilation(aa,size=(3,2))*0.9)
        for th in (45,35,25,15,5):
            aa=np.clip((a1-th)*2.6,0,255)  # thicker + crisp (no wispy semi strands), >=60 opaque px at 360x320
            if (aa>200).sum()>=60: break
        good=sa[...,3]>60
        if good.any(): _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True); g=g[iy,ix]
        return np.dstack([g,g,g,aa]).astype(np.uint8)
    save(B,f'beard/beard_{pose}.png',bsmall)
print(S)
