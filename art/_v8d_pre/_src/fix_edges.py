# v8 pipeline step after build.py: despill green, remove beard "throat box", fill alpha pinholes between layers.
# Idempotent. Rewrites full-size + _320 for wool/body/face/beard layers.
import numpy as np, json, os, imagequant
from PIL import Image
from scipy import ndimage as nd
import sys; sys.path.insert(0,'/workspace/goat-game/art/_src'); import woolfill
ART='/workspace/goat-game/art'; WOOLS=['fluffy','short','spots','cloud']
def L(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA')).astype(float)
def save(a,rel):
    a=np.clip(np.round(a),0,255).astype(np.uint8); a[a[...,3]<3]=0; im=Image.fromarray(a,'RGBA'); im.save(f'{ART}/{rel}',optimize=True,compress_level=9)
    sm=im.resize((360,320),Image.LANCZOS); sa=np.asarray(sm).copy()
    if rel.startswith('wool/'):  # v8b: steepen the downsampled wool edge (cloud/short fuzz -> 1-2px of alpha~150-200 let the game background show through)
        aa=sa[...,3].astype(float); st=np.clip((aa-24)*1.45,0,255); sa[...,3]=np.where(nd.binary_erosion(aa>0,iterations=1)&(aa>=90),255,st).astype(np.uint8)
    sa[sa[...,3]<3]=0; sm=Image.fromarray(sa,'RGBA')
    imagequant.quantize_pil_image(sm,dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90).save(f'{ART}/'+rel.replace('.png','_320.png'),optimize=True)
def nearest_fill(arr,src_mask,dst_mask):
    if not dst_mask.any() or not src_mask.any(): return arr
    _,(iy,ix)=nd.distance_transform_edt(~src_mask,return_indices=True); arr[dst_mask]=arr[iy[dst_mask],ix[dst_mask]]; return arr
stats={}
for pose in ['idle','jump','clash']:
    body,face,beard,knee=[L(f'{k}/{k}_{pose}.png') if k!='knee' else L(f'wool/knee_{pose}.png') for k in ['body','face','beard','knee']]
    wool={w:L(f'wool/{w}_{pose}.png') for w in WOOLS}; sm=L(f'wool/spots_mask_{pose}.png')
    # 1 despill
    for c in (body,face,beard):
        m=c[...,1]>np.maximum(c[...,0],c[...,2]); c[...,1]=np.where(m,np.maximum(c[...,0],c[...,2]),c[...,1])
    # 1b un-matte: translucent edge px (alpha<160) of colour layers carry the light source-background colour -> light halo on dark wool
    for c in (body,face,beard):
        core=c[...,3]>=230; edge=(c[...,3]>0)&(c[...,3]<160)
        if core.any(): _,(iy,ix)=nd.distance_transform_edt(~core,return_indices=True); c[edge,:3]=c[iy[edge],ix[edge],:3]
    # 2 beard "box": rows (or columns) of the beard bbox that are nearly full width are chin fur clipped by the
    #   beard box in build.py -> move them to the wool layers (keep silhouette alpha, nearest wool texture)
    oth=np.maximum.reduce([body[...,3],face[...,3],wool['fluffy'][...,3]])>128
    bm=beard[...,3]>0
    chin=bm&(nd.distance_transform_edt(~oth)<=12)
    chin=nd.binary_opening(chin,iterations=1)
    chin=nd.binary_dilation(chin,iterations=2)&(beard[...,3]>0)
    chin_a=beard[...,3].copy(); throat=chin
    beard[chin]=0
    fe=np.clip(nd.distance_transform_edt(~chin)/5,0,1); beard[...,3]*=np.where(nd.binary_dilation(chin,iterations=6),fe,1)
    chin_soft=nd.binary_dilation(chin,iterations=5)&(beard[...,3]<250)&(chin_a>0)
    # 3 pinholes: per wool style, interior pixels where union alpha <250 get opaque wool (nearest texture)
    nfill=0
    for w in WOOLS:
        W=wool[w]; U=np.maximum.reduce([W[...,3],body[...,3],face[...,3],beard[...,3],knee[...,3]])
        inside=nd.binary_fill_holes(U>128); deep=nd.distance_transform_edt(inside)>=3
        holes=deep&(U<250); good=W[...,3]>200
        tgt=holes|chin; W=nearest_fill(W,good,tgt&~good); W[holes,3]=255; W[chin,3]=np.maximum(W[chin,3],chin_a[chin]); W=nearest_fill(W,good&~chin_soft,chin_soft&~good); W[chin_soft,3]=np.maximum(W[chin_soft,3],chin_a[chin_soft]); W=woolfill.fill(W,good&~chin_soft&~chin,(chin|chin_soft)&~good,w)
        # v8b: round the boxy chin outline (opening of the silhouette in the chin zone)
        Z=nd.binary_dilation(chin,iterations=14)
        other=np.maximum.reduce([body[...,3],face[...,3],beard[...,3]])
        U2=np.maximum(W[...,3],other)>128
        S=nd.gaussian_filter(U2.astype(float),6)>0.5
        S=(S|(other>128))&Z | (U2&~Z)
        add=S&~U2&Z
        W=woolfill.fill(W,(W[...,3]>200)&~add,add,w)
        cap=nd.gaussian_filter(S.astype(float),1.0)*255
        W[...,3]=np.where(Z,np.where(add,np.maximum(W[...,3],cap),np.minimum(W[...,3],cap)),W[...,3])
        W[...,3]=np.where(Z&nd.binary_erosion(S,iterations=2),255,W[...,3])
        # seam under colour-layer AA edges: wool alpha >= colour alpha where they touch (union alpha unchanged, no background bleed)
        oa=np.maximum.reduce([body[...,3],face[...,3]]); seam=(oa>0)&(oa>W[...,3])&nd.binary_dilation(W[...,3]>128,iterations=4)
        good2=W[...,3]>200; _,(iy,ix)=nd.distance_transform_edt(~good2,return_indices=True); W[seam,:3]=W[iy[seam],ix[seam],:3]; W[seam,3]=oa[seam]
        if w!='fluffy':  # short/cloud/spots leave wider gaps around ears/mouth/hooves: match the clean fluffy silhouette next to colour features
            Fa=wool['fluffy'][...,3]; nearc=nd.binary_dilation(oa>0,iterations=8); fx_=nearc&(Fa>W[...,3])
            good2=W[...,3]>200; _,(iy,ix)=nd.distance_transform_edt(~good2,return_indices=True); W[fx_,:3]=W[iy[fx_],ix[fx_],:3]; W[fx_,3]=Fa[fx_]  # no translucent seam inside rounded chin
        wool[w]=W; nfill+=int(holes.sum())
        if w=='spots':
            smm=sm[...,3]>0; sm=nearest_fill(sm,smm|(~(holes|chin)&inside),(holes|chin)&~smm)
    stats[pose]=dict(throat_px=int(throat.sum()),pinhole_px_all_styles=nfill)
    for k,a in [('body',body),('face',face),('beard',beard)]: save(a,f'{k}/{k}_{pose}.png')
    for w in WOOLS: save(wool[w],f'wool/{w}_{pose}.png')
    save(sm,f'wool/spots_mask_{pose}.png')
# refresh byte counts in manifest (only field that changes)
m=json.load(open(ART+'/manifest.json'))
for f in m['files']:
    f['bytes']=os.path.getsize(f"{ART}/{f['file']}"); f['small_bytes']=os.path.getsize(f"{ART}/{f['small']}")
m['edge_fix']='v8b: fix_edges.py 去绿边/胡子喉部方块（并入羊毛、下巴轮廓圆角、纹理自然填充）/图层间针孔（build.py 之后运行）'
json.dump(m,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1); print(stats)
