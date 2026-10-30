# v2 part split: arc cuts centred on each joint pivot (rotation slides along the arc -> no wedge gap),
# smooth auto split curve between near/far legs, hidden underlap (wool/spots_mask/knee only) under the covering part.
import numpy as np, json, os, shutil
from PIL import Image
from scipy import ndimage as nd
ART='/workspace/goat-game/art'; W,H=1152,1024; SW,SH=360,320
WOOLS=['fluffy','short','spots','cloud']; HORNS=['curl','straight','spiral','branch']
def A(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA'))
def nu(v): v=np.array(v,float); return v/np.hypot(*v)
CFG={
 'idle': dict(head=((690,450),(0.41,-0.91),95), tail=((250,550),(-1,0),35,(0,480,250,592)),
   back=dict(box=(150,690,400,1024),L=((235,700),(0,1),60),R=((320,700),(0,1),55)),
   front=dict(split=((652,770),(655,1024)),box=(575,700,740,1024),L=((625,710),(0,1),55),R=((680,710),(0,1),55))),
 'jump': dict(head=((665,470),(0.41,-0.91),90), tail=((330,650),(-0.95,-0.3),40,(140,580,320,700)),
   back=dict(box=(100,740,430,1024),L=((300,760),(-0.4,0.92),50),R=((360,780),(-0.45,0.89),60)),
   front=dict(split=((760,630),(650,780)),box=(540,600,830,800),L=((700,640),(-0.5,0.87),45),R=((770,610),(-0.2,0.98),45))),
 'clash':dict(head=((720,730),(0.98,0.2),85), tail=((270,615),(-1,0),35,(80,560,262,662)),
   back=dict(box=(90,760,400,1024),L=((210,770),(-0.3,0.95),50),R=((290,790),(0,1),45)),
   front=dict(split=((660,840),(700,1024)),box=(540,780,800,1024),L=((610,800),(0.2,0.98),50),R=((670,800),(0.4,0.92),45)))}
BAND={'head':60,'leg':40,'tail':35}
ORDER=['leg_back_far','leg_front_far','leg_back_near','leg_front_near','tail','head','body','horn']
COLOR=['body','beard','face']
def layers(pose): return {**{w:f'wool/{w}_{pose}.png' for w in WOOLS},'spots_mask':f'wool/spots_mask_{pose}.png','knee':f'wool/knee_{pose}.png',**{c:f'{c}/{c}_{pose}.png' for c in COLOR}}
def split_curve(m,box):
    pts=[]
    for y in range(box[1],min(box[3],H)):
        xs=np.nonzero(m[y])[0]
        if len(xs)<12: continue
        g=np.diff(xs); i=np.argmax(g)
        if g[i]>=3 and i>=5 and len(xs)-i>=6: pts.append((y,(xs[i]+xs[i+1])/2))
    pts=np.array(pts); y,x=pts[:,0],pts[:,1]
    c=np.polyfit(y,x,2 if np.ptp(y)>120 else 1)
    for _ in range(2):  # robust refit
        r=np.abs(np.polyval(c,y)-x); k=r<max(6,np.percentile(r,80)); c=np.polyfit(y[k],x[k],len(c)-1)
    return c
yy,xx=np.mgrid[:H,:W]
def joint(C,u,r,strip=None):
    u=nu(u); al=(xx-C[0])*u[0]+(yy-C[1])*u[1]; pe=np.abs((xx-C[0])*u[1]-(yy-C[1])*u[0])
    m=(np.hypot(xx-C[0],yy-C[1])>r)&(al>0.3*r)
    if strip: m&=(pe<=strip*r)|(al>3*r)
    return m
def biggest(m):
    lab,n=nd.label(m)
    if n<=1: return m
    sz=nd.sum(m,lab,range(1,n+1)); return lab==(np.argmax(sz)+1)
out=dict(version=2,base='art v8（v7 + fix_edges 去绿边）',canvas=[W,H],small_canvas=[SW,SH],anchor=[511,995],
 note='horn 部件单独最后绘制，但跟随 head 的变换（同一 pivot、同一角度）。头和四肢画在 body 之下，这样它们的隐藏延伸区（underlap）随部件一起转动，能填补关节外沿的缺口。部件全画布、左上角对齐、offset 0。切线是以关节轴心为圆心的圆弧：部件绕 pivot 转动时切口沿圆弧滑动，不产生楔形缺口。每个部件内部按 v7 顺序 wool→knee→body→beard→face→horn 绘制、同样换色。pivot 为全画布像素坐标，小图乘 0.3125。',
 underlap_note='隐藏重叠区：头、四条腿、尾巴的 wool（含 spots_mask、knee）越过关节切线向 body 里延伸 band 像素（头 60、腿 40、尾 35），只放在 body 在该羊毛款式下 alpha=255 的位置，所以静止合成与 v8 原图逐像素一致；部件转动时延伸区跟着转，补上切口和关节外沿的缝。远侧腿另向近侧腿下延伸（髋/肩 80px 内满强度，80→120px 线性渐隐，v8b 修前腿重叠台阶）。',
 joint_fill='v1 的 joint_fill 已废弃（删除），由 underlap 取代',
 part_draw_order=ORDER,beard_recolor='beard 为灰度 mask，与羊毛同色：RGB = 灰度/255 × woolColor',layer_draw_order_within_part=['wool/{wool}','wool/spots_mask (仅 spots 款可选第二色)','wool/knee','body','beard','face','horn/{horn} (仅 horn 部件)'],
 rotation_tested=dict(head='±15°',legs='±12°',tail='±15°'),poses={})
if os.path.isdir(ART+'/parts'): shutil.rmtree(ART+'/parts')
mani=json.load(open(ART+'/manifest.json'))
for pose,c in CFG.items():
    LY=layers(pose); full={k:A(v) for k,v in LY.items()}; small={k:A(v.replace('.png','_320.png')) for k,v in LY.items()}
    vis=np.maximum.reduce([full[k][...,3] for k in LY])>0
    lab=np.full((H,W),'body',object); piv={}; cuts={}
    hm=biggest(joint(*c['head'])&vis); piv['head']=list(c['head'][0])
    tC,tu,tr,tb=c['tail']; tm=biggest(joint(tC,tu,tr)&vis&(xx>=tb[0])&(xx<tb[2])&(yy>=tb[1])&(yy<tb[3])&~hm); piv['tail']=list(tC)
    legs={}
    for pair in ['back','front']:
        P=c[pair]; b=P['box']; m=vis&~hm&~tm&(xx>=b[0])&(xx<b[2])&(yy>=b[1])&(yy<b[3])
        cc=split_curve(m,b) if 'split' not in P else np.polyfit([P['split'][0][1],P['split'][1][1]],[P['split'][0][0],P['split'][1][0]],1); cuts[f'{pair}_split_poly_x_of_y']=[round(float(v),6) for v in cc]
        left=xx<np.polyval(cc,yy)
        sides={}
        for s,sm in [('L',left),('R',~left)]:
            Cj,uj,rj=P[s]; sides[s]=(biggest(m&sm&joint(Cj,uj,rj,1.15)),Cj)
        # leftovers far below the joints (bits cut off by the split line) -> nearest leg
        lowj=max(P['L'][0][1]+2*P['L'][2],P['R'][0][1]+2*P['R'][2])
        rest=m&~sides['L'][0]&~sides['R'][0]&(yy>lowj)
        if rest.any():
            dL=nd.distance_transform_edt(~sides['L'][0]); dR=nd.distance_transform_edt(~sides['R'][0])
            sides={'L':(sides['L'][0]|(rest&(dL<=dR)),sides['L'][1]),'R':(sides['R'][0]|(rest&(dR<dL)),sides['R'][1])}
        lowL=np.nonzero(sides['L'][0].any(1))[0].max(); lowR=np.nonzero(sides['R'][0].any(1))[0].max()
        near,far=('L','R') if lowL>=lowR else ('R','L')
        for k,s in [('near',near),('far',far)]: legs[f'leg_{pair}_{k}']=sides[s][0]; piv[f'leg_{pair}_{k}']=list(sides[s][1])
    for k,m in legs.items(): lab[m]=k
    lab[tm]='tail'; lab[hm]='head'; piv['horn']=list(c['head'][0])
    ys,xs=np.nonzero((lab=='body')&vis); piv['body']=[int(xs.mean()),int(ys.mean())]; piv['body_alt_foot_anchor']=[511,995]
    np.save(f'/tmp/lab_{pose}.npy',lab.astype(str))
    # underlaps: (owner part, covered-by part, band)
    UL=[('head','body',BAND['head']),('leg_back_near','body',BAND['leg']),('leg_front_near','body',BAND['leg']),
        ('leg_back_far','body',BAND['leg']),('leg_front_far','body',BAND['leg']),('tail','body',BAND['tail']),
        ('leg_back_far','leg_back_near',BAND['leg']),('leg_front_far','leg_front_near',BAND['leg'])]
    NEARJ={'leg_back_far':piv['leg_back_far'],'leg_front_far':piv['leg_front_far']}
    dist_to={p:nd.distance_transform_edt(lab!=p) for p in set(u[0] for u in UL)}
    sy=((np.arange(SH)+0.5)*H/SH).astype(int); sx=((np.arange(SW)+0.5)*W/SW).astype(int); IX=np.ix_(sy,sx)
    files={p:[] for p in ORDER}; ulstat={}
    for res,D,lb,scale in [('full',full,lab,1.0),('small',small,lab[IX],SW/W)]:
        shp=lb.shape
        def cover(part,w):  # part's own composite opaque for wool style w
            cv=np.zeros(shp,bool)
            for k in [w,'knee']+COLOR: cv|=(D[k][...,3]==255)
            return cv&(lb==part)
        ext={p:{k:np.zeros(shp) for k in WOOLS+['spots_mask','knee']} for p in ORDER}  # underlap alpha factor per owner/layer
        for own,cov,band in UL:
            d=dist_to[own] if res=='full' else dist_to[own][IX]*scale
            bandm=(d>0)&(d<=band*scale)&(lb==cov)
            if cov.startswith('leg_'):
                pj=NEARJ[own]; bandm&=np.hypot(xx[IX] if res=='small' else xx,0)>=0
                YY,XX=(yy,xx) if res=='full' else (yy[IX],xx[IX]); rr=np.hypot(XX-pj[0],YY-pj[1]); bandm&=rr<=120; tap=np.clip((120-rr)/40,0,1)  # v8b: taper 80->120px instead of hard 110 cut
            if not cov.startswith('leg_'): tap=1.0
            ramp=np.clip((band*scale-d)/(8*scale)+0.0,0,1)
            for w in WOOLS:
                cv=cover(cov,w); inner=nd.distance_transform_edt(cv|(lb==own))
                f=np.where(bandm&cv,np.clip((inner-2*scale)/(5*scale),0,1)*np.clip((band*scale-d)/(10*scale),0,1),0)
                f=np.where(cv,f,0)*tap
                keys=[w]+(['spots_mask'] if w=='spots' else [])
                for k in keys: ext[own][k]=np.maximum(ext[own][k],f)
                if w=='fluffy': ulstat[f'{own}<{cov}']=int((f>0).sum()) if res=='full' else ulstat.get(f'{own}<{cov}')
            # knee: covered for every style -> use min over styles
            cvall=np.logical_and.reduce([cover(cov,w) for w in WOOLS])
            f=np.where(bandm&nd.binary_erosion(cvall,iterations=1),np.clip((band*scale-d)/(10*scale),0,1),0)*tap; ext[own]['knee']=np.maximum(ext[own]['knee'],f)
        for part in ORDER:
            srcs=[(h,f'horn/{h}_{pose}.png') for h in HORNS] if part=='horn' else list(LY.items())
            for k,f in srcs:
                fn=f if res=='full' else f.replace('.png','_320.png')
                a=(D[k] if k in D else A(fn)).copy()
                if k in HORNS: pass
                else:
                    own=(lb==part); ul=ext[part].get(k)
                    keep=a.copy(); a[~own]=0
                    if ul is not None and (ul>0).any():
                        um=(ul>0)&~own; src=keep.astype(float)
                        # underlap RGB = layer RGB there (nearest opaque if needed); alpha = factor*255
                        good=src[...,3]>128
                        if k in WOOLS and (um&~good).any():
                            _,(iy,ix)=nd.distance_transform_edt(~good,return_indices=True); src[um&~good]=src[iy[um&~good],ix[um&~good]]
                        a[um,:3]=src[um,:3].astype(np.uint8); a[um,3]=np.round(ul[um]*(255 if k in WOOLS else keep[um,3].astype(float))).astype(np.uint8)
                if a[...,3].max()==0: continue
                rel=f'parts/{pose}/{part}/'+os.path.basename(fn)
                os.makedirs(os.path.dirname(f'{ART}/{rel}'),exist_ok=True); Image.fromarray(a,'RGBA').save(f'{ART}/{rel}',optimize=True)
                if res=='full': files[part].append(rel)
    out['poses'][pose]=dict(pivots=piv,cut_arcs=dict(head=dict(center=list(c['head'][0]),axis=list(c['head'][1]),radius=c['head'][2]),tail=dict(center=list(tC),axis=list(tu),radius=tr),
        **{f'leg_{p}_{s}':dict(center=list(c[p][s][0]),axis=list(c[p][s][1]),radius=c[p][s][2]) for p in ['back','front'] for s in 'LR'}),leg_LR_note='L/R=画面左/右，near/far 见 pivots',
        split_curves=cuts,underlap_px_full_fluffy=ulstat,files=files,horn_root=mani['poses'][pose]['horn_root'])
json.dump(out,open(ART+'/parts.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:v['pivots'] for k,v in out['poses'].items()}))
print(json.dumps({k:v['underlap_px_full_fluffy'] for k,v in out['poses'].items()}))
