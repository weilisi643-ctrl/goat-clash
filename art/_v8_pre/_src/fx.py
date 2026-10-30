import numpy as np, json, os, imagequant
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; R=np.random.default_rng(7); meta=[]
def save(a,name,kind,recolor,desc):
    a=np.clip(a,0,255).astype(np.uint8); a[a[...,3]<3]=0; im=Image.fromarray(a,'RGBA')
    q=imagequant.quantize_pil_image(im,dithering_level=1.0,max_colors=256,min_quality=70,max_quality=95); p=f'{ART}/fx/{name}.png'; q.save(p,optimize=True)
    meta.append(dict(file=f'fx/{name}.png',size=list(im.size),kind=kind,recolor=recolor,desc=desc,pivot=[im.size[0]//2,im.size[1]//2],bytes=os.path.getsize(p)))
def noise(s,sc):
    n=R.random((s,s)); return nd.gaussian_filter(n,sc,mode='wrap')
def rgba(L,a): L=np.clip(L,0,255); return np.dstack([L,L,L,a])
S=192; yy,xx=np.mgrid[:S,:S]/S-0.5
for i in range(3):  # dust puffs: gray mask, multiply with tint (default #c8b08a)
    a=np.zeros((S,S))
    for _ in range(6+i*2):
        cx,cy=R.normal(0,0.12,2); r=R.uniform(0.1,0.2)*(1+i*0.15); d=np.sqrt((xx-cx)**2+(yy-cy*0.6)**2)/r
        a=np.maximum(a,np.clip(1-d,0,1)**1.3)
    n=noise(S,3);n=(n-n.min())/(n.max()-n.min()); a=a*(0.55+0.6*n)*(1-0.25*i); a=np.clip(a*1.4,0,1)
    L=200+55*(nd.gaussian_filter(a,6)-yy*0.5)
    save(rgba(L,a*230),f'dust_{i}','gray_mask','multiply gray/255 × color, default #c8b08a',f'尘土团 帧/变体 {i}（越往后越散越淡）')
S=128
im=Image.new('RGBA',(S,S)); d=ImageDraw.Draw(im)  # grass bits: colored
for _ in range(9):
    x,y=R.uniform(20,108,2); ang=R.uniform(0,np.pi); l=R.uniform(12,30); w=R.uniform(2,4)
    g=(int(R.uniform(70,120)),int(R.uniform(130,175)),int(R.uniform(40,70)),255)
    dx,dy=np.cos(ang)*l/2,np.sin(ang)*l/2; d.line([(x-dx,y-dy),(x+dx,y+dy)],fill=g,width=int(w))
    d.line([(x-dx*0.6,y-dy*0.6-1),(x+dx*0.6,y+dy*0.6-1)],fill=(min(255,g[0]+50),min(255,g[1]+50),g[2]+20,200),width=1)
save(np.asarray(im.filter(ImageFilter.SMOOTH)).astype(float),'grass_bits','color','none（原色绿草，可整体 multiply 成枯黄）','草屑一簇，粒子发射时可整张或随机旋转')
for j in range(3):  # single grass blade particles
    im=Image.new('RGBA',(32,32)); d=ImageDraw.Draw(im); a=R.uniform(0.3,2.8); c=16
    d.line([(c-np.cos(a)*12,c-np.sin(a)*12),(c+np.cos(a)*12,c+np.sin(a)*12)],fill=(95,155,55,255),width=3)
    save(np.asarray(im).astype(float),f'grass_blade_{j}','color','none',f'单根草屑粒子 {j}（32px）')
S=128; yy,xx=np.mgrid[:S,:S]-S/2; r=np.hypot(xx,yy); th=np.arctan2(yy,xx)
a=np.zeros((S,S))
for k in range(10):  # spark star burst: additive, warm white core
    t=R.uniform(-np.pi,np.pi); L=R.uniform(30,60); dt=np.angle(np.exp(1j*(th-t)))
    a=np.maximum(a,np.clip(1-np.abs(dt)*r/2.2,0,1)*np.clip(1-r/L,0,1))
core=np.exp(-(r/7)**2); a=np.clip(a+core,0,1)
rgb=np.dstack([255*np.ones_like(a),200+55*core,90+165*core])
save(np.dstack([rgb,a*255]),'spark_burst','color_additive','建议 globalCompositeOperation=lighter；也可 multiply 换色','撞击火花星爆（128px）')
S=32; yy,xx=np.mgrid[:S,:S]-S/2+0.5
a=np.clip(1-np.hypot(xx*0.45,yy*1.6)/7,0,1); save(np.dstack([255*np.ones((S,S)),220+0*a,140+115*a**2,a*255]),'spark_streak','color_additive','lighter','单条火花粒子，沿速度方向旋转（32px）')
S=64
for j in range(3):  # wool fluff: gray mask, tint with wool color
    yy,xx=np.mgrid[:S,:S]/S-0.5; a=np.zeros((S,S))
    for _ in range(5):
        cx,cy=R.normal(0,0.09,2); rr=R.uniform(0.1,0.2); a=np.maximum(a,np.clip(1-np.hypot(xx-cx,yy-cy)/rr,0,1))
    n=noise(S,1.2); n=(n-n.min())/(n.max()-n.min()); a=np.clip(a*2.2*(0.5+0.7*n),0,1)
    L=215+40*nd.gaussian_filter(a,2)-50*(yy+0.5)*a
    save(rgba(L,a*255),f'wool_fluff_{j}','gray_mask','multiply gray/255 × 羊毛色（与 wool 同规则）',f'羊毛碎片 {j}（64px）')
S=256; yy,xx=np.mgrid[:S,:S]-S/2+0.5; r=np.hypot(xx,yy)/(S/2); th=np.arctan2(yy,xx)
n=1+0.15*np.sin(th*7)+0.08*np.sin(th*13+1)
ring=np.exp(-((r-0.8)/0.06)**2)*n+0.35*np.exp(-((r-0.7)/0.12)**2)
a=np.clip(ring,0,1)*(r<1)
save(rgba(235+20*a,a*220),'shockwave_ring','gray_mask','multiply 换色或 lighter；按 scale 0.2→1.2 + alpha 渐隐播放','冲击波环（256px）')
json.dump(dict(version=1,style='半写实，配合 art v7 羊',recolor_rule='gray_mask: RGB = 灰度/255 × 目标色；color: 原色；color_additive: 推荐 lighter 叠加',
  pivot_note='pivot 为贴图中心',files=meta),open(ART+'/fx/fx.json','w'),ensure_ascii=False,indent=1)
print([(m['file'],m['bytes']) for m in meta])
