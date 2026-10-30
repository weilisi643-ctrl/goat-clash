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
stats={}; stats_neck={}
for pose in ['idle','jump','clash']:
    body,face,beard,knee=[L(f'{k}/{k}_{pose}.png') if k!='knee' else L(f'wool/knee_{pose}.png') for k in ['body','face','beard','knee']]
    wool={w:L(f'wool/{w}_{pose}.png') for w in WOOLS}; sm=L(f'wool/spots_mask_{pose}.png')
    # 0 v8d: light fur bits painted into the FACE layer (throat/neck patch under the jaw, small neck/forehead tufts) never got the wool tint
    #   -> move them into every wool layer as gray mask (keeps their light/dark shading), keep only eyes + mouth in face.
    KEEP={'idle':[(811,330),(898,408)],'jump':[(790,370),(857,438)],'clash':[(831,760),(821,845)]}[pose]
    fm=face[...,3]>0; lab,n=nd.label(nd.binary_dilation(fm,iterations=2)); lab=lab*fm
    keep_ids={lab[y,x] for x,y in KEEP} | {lab[yy,xx] for x,y in KEEP for yy in range(y-6,y+7) for xx in range(x-6,x+7) if lab[yy,xx]}
    mv=fm&~np.isin(lab,list(keep_ids)); fa=face[...,3]/255; flum=face[...,:3]@[0.299,0.587,0.114]
    neck_moved=face.copy(); neck_moved[~mv]=0; face[mv]=0
    # same for small detached light fur flecks in the BODY layer around the ear/neck (keep the main ear shape)
    HR={'idle':(806,277),'jump':(782,326),'clash':(860,687)}[pose]; yy_,xx_=np.mgrid[:1024,:1152]
    bm=(body[...,3]>0)&(np.hypot(xx_-HR[0],yy_-HR[1])<200); bl,bn=nd.label(bm)
    if bn>1:
        sz=nd.sum(bm,bl,range(1,bn+1)); ear=1+int(np.argmax(sz)); bmv=bm&(bl!=ear)
        fa=np.where(mv,fa,0)+np.where(bmv,body[...,3]/255,0); flum=np.where(bmv,body[...,:3]@[0.299,0.587,0.114],flum); mv=mv|bmv; body[bmv]=0
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
    # 0b put the moved fur into the wool gray masks (scaled to that style's local wool brightness)
    if mv.any():
        ring=nd.binary_dilation(mv,iterations=10)&~mv
        for w in WOOLS:
            W=wool[w]; ref=np.percentile(W[ring&(W[...,3]>200)][:,:3].mean(1),70) if (ring&(W[...,3]>200)).any() else 220
            g=np.clip(flum/np.percentile(flum[mv],90)*ref,0,255); a=fa*mv
            W[...,:3]=W[...,:3]*(1-a[...,None])+g[...,None]*a[...,None]; W[...,3]=np.maximum(W[...,3],a*255)
            R=nd.binary_dilation(mv,iterations=3)&nd.binary_erosion(nd.binary_fill_holes((W[...,3]>0)|mv),iterations=2)  # moved fur had wool holes under it -> close them
            lo=R&(W[...,3]<250)&~mv; good=W[...,3]>=250
            if lo.any(): _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True); W[lo,:3]=W[iy[lo],ix[lo],:3]
            W[R,3]=255; wool[w]=W
        stats_neck[pose]=int(mv.sum())
    # 3 pinholes: per wool style, interior pixels where union alpha <250 get opaque wool (nearest texture)
    nfill=0
    for w in WOOLS:
        W=wool[w]; U=np.maximum.reduce([W[...,3],body[...,3],face[...,3],beard[...,3],knee[...,3]])
        inside=nd.binary_fill_holes(U>128); deep=nd.distance_transform_edt(inside)>=3
        holes=deep&(U<250); good=W[...,3]>200
        # v8d: gaps enclosed by head + horn (ear/horn-base wedge, alpha 0 pockets): fill with wool if they hug the head (<=25px) and are not a horn ring hole
        HN=np.maximum.reduce([L(f'horn/{h}_{pose}.png')[...,3] for h in ['curl','straight','spiral','branch']])>128
        enc=nd.binary_fill_holes((U>128)|HN)&~(U>128)&~HN; el,en=nd.label(enc)
        if en:
            dU=nd.distance_transform_edt(~(U>128)); nb=nd.binary_dilation(enc,iterations=2)&~enc
            for i in range(1,en+1):
                c=el==i; ring=nd.binary_dilation(c,iterations=2)&~c
                if (ring&(U>128)).sum()>=0.3*ring.sum(): holes|=c&(dU<=25)
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
json.dump(m,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1); print(stats,'face->wool px',stats_neck)
