import numpy as np, json, os, glob
from PIL import Image
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; W,H=1152,1024; SW,SH=360,320
yy,xx=np.mgrid[:H,:W]
def A(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA'))
def side(p,q):  # True right/up of line p->q (cross>0)
    return (q[0]-p[0])*(yy-p[1])-(q[1]-p[1])*(xx-p[0])<0
CFG={ # neck line, head extra bound, tail box, back-leg box, front-leg box (x0,y0,x1,y1)
 'idle': dict(neck=((690,330),(780,470)),tail=(0,480,205,620),back=(150,745,390,1024),front=(580,770,740,1024),front_split=((652,770),(655,1024))),
 'jump': dict(neck=((670,340),(760,480)),tail=(150,580,290,700),back=(120,805,390,1024),front=(625,645,800,800)),
 'clash':dict(neck=((790,640),(750,830)),tail=(100,570,235,660),back=(100,820,380,1024),front=(570,840,780,1024),front_split=((660,840),(700,1024)))}
WOOLS=['fluffy','short','spots','cloud']; HORNS=['curl','straight','spiral','branch']
LAYERS=lambda pose:[f'wool/{w}_{pose}.png' for w in WOOLS+['spots_mask','knee']]+[f'{l}/{l}_{pose}.png' for l in ['body','beard','face']]
def boxm(b): return (xx>=b[0])&(xx<b[2])&(yy>=b[1])&(yy<b[3])
out=dict(version=1,base='art v7',canvas=[W,H],small_canvas=[SW,SH],anchor=[511,995],
 note='部件为全画布尺寸，左上角对齐直接叠放，offset 均为 0。各部件像素不重叠（硬切分），按 draw_order 叠加与 v7 逐像素一致。每个部件内部仍按 v7 图层顺序 wool→knee→body→beard→face→horn 绘制、同样换色。pivot 为全画布像素坐标，小图乘 0.3125。',
 optional_underlay=dict(part='joint_fill',draw='在所有部件之前先画（最底层），只在头/腿/尾转动时开启；它是各关节切线外侧 28px 的 v7 原像素，填补转动后露出的楔形缺口。开启后静止合成不再逐像素等于 v7（部件半透明边缘会透出它），所以静止时关掉。'),
 part_draw_order=['leg_back_far','leg_front_far','tail','body','leg_back_near','leg_front_near','head'],
 layer_draw_order_within_part=['wool/{wool}','wool/knee','body','beard','face','horn/{horn}  (仅 head)'],poses={})
for pose,c in CFG.items():
    al=np.zeros((H,W)); 
    for f in LAYERS(pose): al=np.maximum(al,A(f)[...,3])
    vis=al>0; lab=np.full((H,W),'body',object)
    (p,q)=c['neck']; head=side(p,q)&(yy<max(p[1],q[1])+60)&(xx>p[0]-120)
    tail=boxm(c['tail'])&~head
    piv={}
    for name,b in [('back',c['back']),('front',c['front'])]:
        m=boxm(b)&vis&~head
        cols=m[b[1]+40:].sum(0).astype(float); xs_=np.nonzero(cols)[0]; cols[:xs_.min()+25]=1e9; cols[xs_.max()-25:]=1e9
        cols=nd.uniform_filter1d(cols,9); sx=int(np.argmin(cols))
        L=m&(xx<sx); R=m&(xx>=sx)
        if name+'_split' in c:
            sp=c[name+'_split']; R=m&side(sp[0],sp[1])&False|m&~side((sp[1][0],sp[1][1]),(sp[0][0],sp[0][1]))&False
            t=(xx-sp[0][0])*(sp[1][1]-sp[0][1])-(yy-sp[0][1])*(sp[1][0]-sp[0][0]); R=m&(t>0); L=m&(t<=0)
        # near = the leg whose lowest pixel is lower on screen
        lowL=np.nonzero(L.any(1))[0].max(); lowR=np.nonzero(R.any(1))[0].max()
        near,far=(L,R) if lowL>=lowR else (R,L)
        for k,mm in [('near',near),('far',far)]:
            nm=f'leg_{name}_{k}'; lab[mm]=nm
            ys,xs=np.nonzero(mm); top=ys<ys.min()+12; piv[nm]=[int(xs[top].mean()),int(ys.min())]
    lab[tail&vis]='tail'; lab[head]='head'
    ys,xs=np.nonzero((lab=='tail')&vis); piv['tail']=[int(xs.max()),int(ys.mean())]
    piv['head']=[int((p[0]+q[0])/2),int((p[1]+q[1])/2)]
    ys,xs=np.nonzero((lab=='body')&vis); piv['body']=[int(xs.mean()),int(ys.mean())]; piv['body_alt_foot_anchor']=[511,995]
    np.save(f'/tmp/lab_{pose}.npy',lab.astype(str))
    sy=((np.arange(SH)+0.5)*H/SH).astype(int); sx=((np.arange(SW)+0.5)*W/SW).astype(int); labs=lab[np.ix_(sy,sx)]
    files={}
    bd=nd.distance_transform_edt(lab!='body'); jf=(lab!='body')&(bd<=28)&vis
    jfs=jf[np.ix_(sy,sx)]
    for part in out['part_draw_order']+['joint_fill']:
        fl=[]
        srcs=LAYERS(pose)+([f'horn/{h}_{pose}.png' for h in HORNS] if part=='head' else [])
            # joint_fill: copy of v7 pixels in a 28px band on the part side of each cut (optional underlay)
        for f in srcs:
            for small,L in [(False,lab),(True,labs)]:
                fn=f.replace('.png','_320.png') if small else f
                a=A(fn).copy()
                m=(jf if not small else jfs) if part=='joint_fill' else (np.ones(L.shape,bool) if f.startswith('horn/') else (L==part))
                a[~m]=0
                if a[...,3].max()==0: continue
                rel=f'parts/{pose}/{part}/'+os.path.basename(fn)
                os.makedirs(os.path.dirname(f'{ART}/{rel}'),exist_ok=True)
                Image.fromarray(a,'RGBA').save(f'{ART}/{rel}',optimize=True)
                if not small: fl.append(rel)
        files[part]=fl
    out['poses'][pose]=dict(pivots=piv,neck_cut_line=[list(p),list(q)],files=files,horn_root=json.load(open(ART+'/manifest.json'))['poses'][pose]['horn_root'])
json.dump(out,open(ART+'/parts.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:v['pivots'] for k,v in out['poses'].items()}))
