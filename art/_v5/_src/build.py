import numpy as np, json, os, imagequant
from PIL import Image
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; SRC=ART+'/_src'; S=1024; SM=320; K=0.8; OX,OY=102,195
rng=np.random.default_rng(3); yy,xx=np.mgrid[:S,:S]
def key(path,one=True):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
    d=g-np.maximum(r,b); al=np.clip(1-(d-25)/60,0,1)
    m=nd.binary_fill_holes(nd.binary_erosion(al>0.5,iterations=1))
    if one:
        lab,n=nd.label(m); sz=nd.sum(m,lab,range(1,n+1)); m=lab==(np.argmax(sz)+1)
    al=np.minimum(al,nd.gaussian_filter(m.astype(float),0.8))
    g=np.minimum(g,np.maximum(r,b)*1.02); return np.dstack([r,g,b]),al
def place(rgb,a):
    im=Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),'RGBA').resize((int(1024*K),)*2,Image.LANCZOS)
    c=Image.new('RGBA',(S,S)); c.paste(im,(OX,OY)); x=np.asarray(c).astype(float); return x[...,:3],x[...,3]/255
def T(x,y): return (int(OX+x*K),int(OY+y*K))
def box(b): x0,y0=T(b[0],b[1]); x1,y1=T(b[2],b[3]); return (xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
def clean(m,minpx=60):
    lab,n=nd.label(m)
    if n==0: return m
    sz=nd.sum(m,lab,range(1,n+1)); return np.isin(lab,np.nonzero(sz>=minpx)[0]+1)
meta=[]
def save(arr,rel,kind):
    arr=np.clip(arr,0,255).astype(np.uint8); arr[arr[...,3]<3]=0  # 清掉透明区颜色
    p=ART+'/'+rel; os.makedirs(os.path.dirname(p),exist_ok=True)
    im=Image.fromarray(arr,'RGBA'); im.save(p,optimize=True,compress_level=9)
    sm=im.resize((SM,SM),Image.LANCZOS); sa=np.asarray(sm).copy(); sa[sa[...,3]<3]=0; sm=Image.fromarray(sa,'RGBA')
    q=imagequant.quantize_pil_image(sm,dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90)
    ps=p.replace('.png',f'_{SM}.png'); q.save(ps,optimize=True)
    meta.append(dict(file=rel,small=rel.replace('.png',f'_{SM}.png'),size=[S,S],small_size=[SM,SM],kind=kind,bytes=os.path.getsize(p),small_bytes=os.path.getsize(ps)))
def lum(rgb): return rgb@[0.299,0.587,0.114]
def grayimg(L,a): L=np.clip(L,0,255); return np.dstack([L,L,L,a*255])
# src coords: head, ear, beard boxes; horn root; rotation
POSES={'idle':dict(head=(730,60,1024,400),ear=(745,65,825,205),beard=(885,310,955,395),horn=(880,118),rot=0),
       'jump':dict(head=(730,50,985,340),ear=(745,55,810,155),beard=(845,270,905,340),horn=(850,112),rot=-12),
       'clash':dict(head=(790,400,1012,690),ear=(862,402,948,492),beard=(792,590,852,668),horn=(948,458),rot=-72)}
KNEES={'idle':[(640,770,700,845),(700,755,750,830)],'jump':[(750,495,815,570),(805,465,865,540)],'clash':[(635,655,690,720),(710,645,752,710)]}
# textures
TEX={}
for w,sc in dict(fluffy=0.45,short=0.6,spots=0.55,cloud=0.32).items():
    t=lum(np.asarray(Image.open(f'{SRC}/tex_{w}.jpg').convert('RGB')).astype(float))
    TEX[w]=(t,sc)
# horns: quadrants, find base (bottom-most rows centroid)
HCFG={'curl':((0,0),True,0,230),'straight':(None,False,-8,230),'spiral':((0,1),False,-12,250),'branch':((1,1),True,5,280)}
horn_src={}
hr,ha=key(SRC+'/horns.jpg',False)
for hid,(cc,flip,extra,hh) in HCFG.items():
    cx,cy=cc if cc else (0,0)
    if hid=='straight':
        r2,a2=key(SRC+'/horn_straight.jpg'); a=a2; m=clean(a>0.5,800); L=lum(r2)
    else:
        sl=(slice(cy*512,cy*512+512),slice(cx*512,cx*512+512)); a=ha[sl]; m=clean(a>0.5,800); L=lum(hr[sl])
    a=a*nd.binary_dilation(m,iterations=2); L=L/np.median(L[m])*128  # 中灰 = 128
    im=Image.fromarray(grayimg(L,a).astype(np.uint8),'RGBA'); im=im.crop(im.getbbox())
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    h=int(hh*K); k=h/im.height; im=im.resize((max(1,int(im.width*k)),h),Image.LANCZOS)
    al=np.asarray(im)[...,3]; ys,xs=np.nonzero(al>128); bot=ys>ys.max()-max(6,h*0.06)
    horn_src[hid]=(im,(int(xs[bot].mean()),int(ys.max())-int(h*0.05)),extra)
DONE={}; wools=['fluffy','short','spots','cloud']
for pose,P in POSES.items():
    rgb,a=place(*key(f'{SRC}/{pose}.jpg'))
    x=rgb/255; mx=x.max(-1); mn=x.min(-1); s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0); v=mx
    rr,gg,bb=rgb[...,0],rgb[...,1],rgb[...,2]; inhead=box(P['head']); inear=box(P['ear']); inbeard=box(P['beard'])
    vis=a>0.05
    woolm=(s<0.30)&(v>0.42)&vis
    feat=vis&~woolm
    inknee=np.zeros((S,S),bool)
    for kb in KNEES[pose]: inknee|=box(kb)
    knee=clean(inknee&feat&(s>0.30)&(s<0.7)&(v>0.38)&(v<0.85)&~inhead&(rr>gg)&(gg>bb)&(yy>S*0.5),40)
    knee=nd.binary_dilation(knee,iterations=2)&vis&(v>=0.38)&inknee
    earpink=clean(feat&inear,30); earpink=nd.binary_dilation(earpink,iterations=1)&vis&inear&~woolm|earpink
    face=clean(feat&inhead&~inear,25); face=nd.binary_dilation(face,iterations=1)&vis&inhead&~inear
    beard=woolm&inbeard&~face
    hoof=feat&(v<0.42)&(s>0.2)&~inhead&(yy>S*0.45)
    hoof=clean(hoof,40); hoof=nd.binary_dilation(hoof,iterations=1)&feat&(v<0.48)
    body=clean(hoof&~knee,60)|earpink
    woolm=woolm|(feat&~hoof&~inhead&~knee)|(feat&inhead&~face&~inear&(v>0.6))
    wool=clean((woolm|knee)&~beard,200)
    soft=lambda m: nd.gaussian_filter(m.astype(float),0.7)*a
    save(np.dstack([rgb,soft(body)*255]),f'body/body_{pose}.png','color')
    save(np.dstack([rgb,soft(face)*255]),f'face/face_{pose}.png','color')
    save(np.dstack([rgb,soft(beard)*255]),f'beard/beard_{pose}.png','color')
    L=lum(rgb); L=L/np.percentile(L[woolm],99)*255
    save(grayimg(L,soft(knee)),f'wool/knee_{pose}.png','gray_mask')
    shade=nd.gaussian_filter(L,5); shade=shade/np.percentile(shade[wool],95)
    wa=soft(wool)
    torso=wool&~inhead; ys_,xs_=np.nonzero(torso); bx0,bx1=np.percentile(xs_,[1,99]); by0,by1=np.percentile(ys_,[1,99])
    dist=nd.distance_transform_edt(wool); dd=nd.gaussian_filter(np.minimum(dist,60),10)
    gy,gx=np.gradient(dd); depth=np.sqrt(np.clip(dist/45,0,1))
    shade=shade*(0.8+0.2*depth)
    U=(xx-bx0)/(bx1-bx0); V=(yy-by0)/(by1-by0)
    def sample(w):
        t,sc=TEX[w]; n=t.shape[0]; rep=1/sc*(bx1-bx0)/S*1.25
        cu=(U+gx*0.9/ (bx1-bx0)*30)*n*rep; cv=(V*(by1-by0)/(bx1-bx0)+gy*0.9/(bx1-bx0)*30)*n*rep
        # squeeze texture toward silhouette edges (curved surface)
        return nd.map_coordinates(t,[cv%n,cu%n],order=1,mode='wrap')
    for w in wools:
        t=sample(w); tm=t[wool].mean(); detail=t/tm
        alpha=wa.copy(); g=None
        if w=='short':
            core=nd.binary_erosion(wool,iterations=3); alpha=soft(core)
            g=shade*(0.75+0.25*detail)*240
        elif w=='fluffy':
            g=shade*(0.55+0.45*detail)*245
        elif w=='spots':
            light=np.percentile(t[wool],85); spm=np.clip((light-t)/ (light-np.percentile(t,5)),0,1)
            spm=nd.gaussian_filter(spm,2)
            g=shade*(0.7+0.3*np.clip(detail,0.6,1.4))*245*(1-0.55*spm)
            save(grayimg(spm*255,spm*wa),f'wool/spots_mask_{pose}.png','gray_mask')
        elif w=='cloud':
            core=wool&~inhead&(yy<S*0.78)
            ed=core^nd.binary_erosion(core,iterations=2); pts=np.argwhere(ed)[::140]
            add=np.zeros((S,S),bool)
            for py,px in pts:
                r=rng.integers(9,16); add|=(yy-py)**2+(xx-px)**2<r*r
            add&=~nd.binary_dilation(feat,iterations=6)
            alpha=np.maximum(wa,nd.gaussian_filter(add.astype(float),1.2))
            sh=np.where(wool,shade,0.9)
            g=sh*(0.5+0.5*detail)*245
        save(grayimg(g,alpha),f'wool/{w}_{pose}.png','gray_mask')
    hx,hy=T(*P['horn'])
    for hid,(him,(bx,by),extra) in horn_src.items():
        far=np.asarray(him).astype(float).copy(); far[...,:3]*=0.62; far=Image.fromarray(far.astype(np.uint8),'RGBA').resize((int(him.width*0.94),int(him.height*0.94)),Image.LANCZOS)
        fb=(int(bx*0.94),int(by*0.94))
        bf=Image.new('RGBA',(1000,1000)); bf.paste(far,(500-fb[0],500-fb[1]),far); bf=bf.rotate(9,resample=Image.BICUBIC,center=(500,500))
        big=Image.new('RGBA',(1000,1000)); big.paste(bf,(-int(22*K),-int(6*K)),bf)
        
        near=Image.new('RGBA',(1000,1000)); near.paste(him,(500-bx,500-by),him); big.alpha_composite(near)
        big=big.rotate(P['rot']+extra,resample=Image.BICUBIC,center=(500,500))
        can=Image.new('RGBA',(S,S)); can.paste(big,(hx-500,hy-500),big)
        save(np.asarray(can).astype(float),f'horn/{hid}_{pose}.png','gray_mask_mid')
    DONE[pose]=dict(anchor=list(T(512,1000)),horn_root=[hx,hy],horn_rotation_deg=P['rot'],head_box=list(T(*P['head'][:2])+T(*P['head'][2:])))
man=dict(game='山羊对撞',version=5,style='半写实侧面朝右，参考 base_side_realistic.png',canvas=[S,S],small_canvas=[SM,SM],small_scale=SM/S,
 anchor_note='同一姿态所有图层共用 1024x1024 画布，左上角对齐直接叠放；anchor 为脚底中心参考点；小图坐标乘 small_scale',
 poses=DONE,draw_order=['wool/{wool}_{pose}','wool/knee_{pose}','body/body_{pose}','beard/beard_{pose}','face/face_{pose}','horn/{horn}_{pose}'],
 recolor={'gray_mask':'羊毛类灰度图：RGB = 灰度/255 × 目标色（multiply），alpha 保留；羊毛用 data.woolColors，knee 默认 #a8774a',
          'gray_mask_mid':'羊角：底色中灰 128 = 目标色本身，RGB = clamp(灰度/128 × 目标色)，亮部为高光、暗部为纹理；用 data.hornColors',
          'color':'彩色原样绘制，不换色（body 含蹄子、耳内粉色；face 含眼鼻嘴；beard 胡子固定白色）',
          'spots_mask':'spots 已把斑点烘焙成深灰；spots_mask_* 可另上第二色'},
 ids=dict(wools=wools,horns=list(HCFG)),files=meta)
json.dump(man,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1); print(len(meta))
