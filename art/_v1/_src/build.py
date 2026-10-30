import numpy as np, json, os, imagequant
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; SRC=ART+'/_src'
S=1024; SM=320
def key(path,one=True):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float)
    r,g,b=a[...,0],a[...,1],a[...,2]
    d=g-np.maximum(r,b); al=np.clip(1-(d-25)/60,0,1)
    m=al>0.5; m=nd.binary_erosion(m,iterations=1); m=nd.binary_fill_holes(m)
    
    if one:
        lab,n=nd.label(m); sz=nd.sum(m,lab,range(1,n+1)); m=lab==(np.argmax(sz)+1)
    al=np.minimum(al, nd.gaussian_filter(m.astype(float),0.8))
    g=np.minimum(g,np.maximum(r,b)*1.02)  # despill
    return np.dstack([r,g,b]),al
K=0.8; OX,OY=102,195
def place(rgb,a):
    im=Image.fromarray(np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8),'RGBA').resize((int(1024*K),)*2,Image.LANCZOS)
    c=Image.new('RGBA',(S,S),(0,0,0,0)); c.paste(im,(OX,OY)); x=np.asarray(c).astype(float); return x[...,:3],x[...,3]/255
def T(x,y): return (int(OX+x*K),int(OY+y*K))
def hsv(rgb):
    x=rgb/255; mx=x.max(-1); mn=x.min(-1); s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    return s,mx
def save(arr,rel,meta,kind):
    p=ART+'/'+rel; os.makedirs(os.path.dirname(p),exist_ok=True)
    im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8),'RGBA'); im.save(p,optimize=True)
    sm=im.resize((SM,SM),Image.LANCZOS); q=imagequant.quantize_pil_image(sm,dithering_level=1.0,max_colors=256,min_quality=60,max_quality=90)
    ps=p.replace('.png',f'_{SM}.png'); q.save(ps,optimize=True)
    meta.append(dict(file=rel,small=rel.replace('.png',f'_{SM}.png'),size=[S,S],small_size=[SM,SM],kind=kind,bytes=os.path.getsize(p),small_bytes=os.path.getsize(ps)))
def rgba(rgb,a): return np.dstack([rgb,a*255])
def gray(rgb,a):
    L=rgb@[0.299,0.587,0.114]; L=L/np.percentile(L[a>0.5],99)*255
    L=np.clip(L,0,255); return np.dstack([L,L,L,a*255])
# per-pose: head box (x0,y0,x1,y1), horn anchor (x,y), horn rotation deg, ground anchor
POSES={'idle':dict(head=(730,60,1024,400),horn=(875,110),rot=0,anchor=(512,1000)),
       'jump':dict(head=(730,50,980,340),horn=(845,105),rot=-12,anchor=(512,1000)),
       'clash':dict(head=(670,290,910,610),horn=(815,375),rot=-40,anchor=(512,1000))}
HORNS={'curl':(0,0),'straight':(1,0),'spiral':(0,1),'branch':(1,1)}
HH={'curl':250,'straight':260,'spiral':280,'branch':300}
meta=[]
# horns sheet
hr,ha=key(SRC+'/horns.jpg',False); horn_src={}
for hid,(cx,cy) in HORNS.items():
    sl=(slice(cy*512,cy*512+512),slice(cx*512,cx*512+512))
    a=ha[sl].copy(); rgb=hr[sl]
    lab,n=nd.label(a>0.5); sz=nd.sum(a>0.5,lab,range(1,n+1)); keep=lab==(np.argmax(sz)+1)
    a=a*nd.binary_dilation(keep,iterations=2)
    im=Image.fromarray(gray(rgb,a).astype(np.uint8),'RGBA'); im=im.crop(im.getbbox()).transpose(Image.FLIP_LEFT_RIGHT)
    h=int(HH[hid]*0.8); k=h/im.height; im=im.resize((int(im.width*k),h),Image.LANCZOS)
    horn_src[hid]=im  # base at bottom-right after flip
wools=['fluffy','short','spots','cloud']
rng=np.random.default_rng(3)
DONE={}
for pose,P in POSES.items():
    rgb,a=place(*key(f'{SRC}/{pose}.jpg'))
    P=dict(P); hb=P['head']; P['head']=T(hb[0],hb[1])+T(hb[2],hb[3]); P['horn']=T(*P['horn']); P['anchor']=T(512,1000)
    s,v=hsv(rgb); H,W=a.shape
    yy,xx=np.mgrid[:H,:W]; x0,y0,x1,y1=P['head']; inhead=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
    kneec=(s>0.30)&(s<0.7)&(v>0.38)&(v<0.85)
    woolm=(s<0.30)&(v>0.42)
    feat=(~woolm)&(a>0.05)
    rr,gg,bb=rgb[...,0],rgb[...,1],rgb[...,2]
    knee=feat&kneec&(~inhead)&(rr>gg)&(gg>bb)&(yy>H*0.5)
    knee=nd.binary_opening(knee,iterations=1); knee=nd.binary_dilation(knee,iterations=2)&(a>0.05)&~(v<0.38)
    face=feat&inhead
    face=nd.binary_dilation(face,iterations=2)&(a>0.05)&inhead&~(woolm&~nd.binary_dilation(feat,iterations=2))
    body=feat&~knee&~face
    soft=lambda m: nd.gaussian_filter(m.astype(float),0.7)*a
    wa=soft(woolm|knee)  # wool covers knees (knee mask drawn on top)
    save(rgba(rgb,soft(body)),f'body/body_{pose}.png',meta,'color')
    save(rgba(rgb,soft(face)),f'face/face_{pose}.png',meta,'color')
    kg=gray(rgb,soft(knee)); save(kg,f'wool/knee_{pose}.png',meta,'gray_mask')
    base=gray(rgb,wa)
    for w in wools:
        g=base.copy()
        if w=='short':
            for c in range(3): g[...,c]=nd.gaussian_filter(g[...,c],2.2)*0.6+g[...,c]*0.4
            g[...,3]=np.minimum(g[...,3],nd.grey_erosion(g[...,3],size=5))
        elif w=='spots':
            sp=np.zeros((H,W)); body_px=np.argwhere((wa>0.9)&~inhead&(yy<H*0.7))
            for i in rng.choice(len(body_px),9,replace=False):
                y,x=body_px[i]; r=rng.integers(25,50); sp+=((yy-y)**2+((xx-x)*0.8)**2<r*r)
            sp=nd.gaussian_filter(np.clip(sp,0,1),3)*(wa>0)
            for c in range(3): g[...,c]*=1-0.6*sp
            save(np.dstack([sp*255]*3+[sp*255*wa]),f'wool/spots_mask_{pose}.png',meta,'gray_mask')
        elif w=='cloud':
            core=(wa>0.5)&~inhead&(yy<H*0.72)
            ed=core^nd.binary_erosion(core,iterations=3); pts=np.argwhere(ed)[::90]
            add=np.zeros((H,W),bool)
            for y,x in pts:
                r=rng.integers(18,34); add|=(yy-y)**2+(xx-x)**2<r*r
            add&=~nd.binary_dilation(feat,iterations=4)
            tex=225+12*rng.standard_normal((H,W))
            na=np.maximum(g[...,3],nd.gaussian_filter(add.astype(float),1.2)*255)
            for c in range(3): g[...,c]=np.where(g[...,3]>128,g[...,c],tex*0.92)
            g[...,3]=na
        save(g,f'wool/{w}_{pose}.png',meta,'gray_mask')
    for hid,him in horn_src.items():
        can=Image.new('RGBA',(S,S)); big=Image.new('RGBA',(900,900)); big.paste(him,(450-him.width,450-him.height),him)
        big=big.rotate(P['rot'],resample=Image.BICUBIC,center=(450,450))
        hx,hy=P['horn']; can.paste(big,(hx-450,hy-450),big)
        save(np.asarray(can).astype(float),f'horn/{hid}_{pose}.png',meta,'gray_mask')
    DONE[pose]=P
man=dict(game='山羊对撞',style='半写实侧面朝右，参考 base_side_realistic.png',
 canvas=[S,S],small_canvas=[SM,SM],small_scale=SM/S,
 anchor_note='所有图层同一姿态共用 1024x1024 画布，左上角对齐直接叠放即可；anchor 为脚底中心参考点（像素，原图坐标），小图乘 small_scale',
 poses={k:dict(anchor=v['anchor'],head_box=v['head'],horn_anchor=v['horn'],horn_rotation_deg=v['rot']) for k,v in DONE.items()},
 draw_order=['wool/{wool}_{pose}','wool/knee_{pose}','body/body_{pose}','face/face_{pose}','horn/{horn}_{pose}'],
 recolor={'gray_mask':'灰度图：结果 RGB = 灰度/255 × 目标色（multiply），alpha 保留。羊毛用 data.woolColors，羊角用 data.hornColors，knee 斑块建议用比羊毛深的棕色（默认 #a8774a）','color':'彩色原样绘制，不换色',
  'spots_mask':'spots 样式已把斑点烘焙成更深灰度；spots_mask_* 单独给出，可另外上第二种颜色'},
 ids=dict(wools=wools,horns=list(HORNS)),files=meta)
json.dump(man,open(ART+'/manifest.json','w'),ensure_ascii=False,indent=1)
print(len(meta))
