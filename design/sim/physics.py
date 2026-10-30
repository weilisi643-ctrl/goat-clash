# 顶顶乐 俯视 2D 简化物理：全部物件按圆形碰撞，固定步长 1/60s
import math, copy
DT=1/60; G=600.0  # 摩擦减速 = friction*G (px/s^2)
TYPES={ # mass, friction, restitution, radius
 'goat':  dict(m=1.0, f=0.9, e=0.6, r=18),
 'crate': dict(m=1.2, f=1.1, e=0.4, r=16),
 'fragile':dict(m=0.8,f=1.1, e=0.3, r=15, breakV=260),
 'ball':  dict(m=0.6, f=0.5, e=0.8, r=12),
 'rock':  dict(m=1e9, f=0,   e=0.5, r=20, static=True),
 'sheep': dict(m=1.5, f=1.0, e=0.5, r=18, wakeV=120, dashV=600),
}
HORNS={'curl':dict(speedMul=1.0,e=0.3,massMul=1.0),   # 卷角：顶住推，自己几乎停下，力量传递多
 'straight':dict(speedMul=1.15,e=0.6,massMul=1.0),      # 直角：速度快
 'spiral':dict(speedMul=1.0,e=0.9,massMul=1.0),         # 螺旋角：弹性大，适合反弹连锁
 'branch':dict(speedMul=0.9,e=0.5,massMul=1.4)}         # 鹿枝角：重，推得动重物
MAXV=900
FIELD=(0,60,375,667)  # 顶部 60px 给 UI
def mk(o):
    t=TYPES[o['type']]; b=dict(o); b.setdefault('r',t['r']); b['m']=t['m']; b['f']=t['f']; b['e']=t['e']
    b['vx']=b['vy']=0.0; b['alive']=True; b['static']=t.get('static',False); b['inHay']=None
    if o['type']=='sheep': b['awake']=False; b['dashed']=False
    return b
def shoot(level, state, angle, power, horn='curl'):
    """state: 物件列表（含 goat）。goat 从 level.start 出发。返回新 state 与事件"""
    S=copy.deepcopy(state); H=HORNS[horn]; ev=[]
    goat=mk({'id':'player','type':'goat','x':level['start']['x'],'y':level['start']['y']})
    goat['m']*=H['massMul']; goat['e']=H['e']
    v=MAXV*power*H['speedMul']; a=math.radians(angle)
    goat['vx']=v*math.cos(a); goat['vy']=-v*math.sin(a)  # 角度：0=右，90=上
    B=[b for b in S if b['alive'] and not b['inHay']]+[goat]
    hays=level['hays']
    for step in range(60*8):
        moving=False
        for b in B:
            if b['static'] or not b['alive'] or b['inHay']: continue
            sp=math.hypot(b['vx'],b['vy'])
            if sp>0:
                dec=b['f']*G*DT; ns=max(0,sp-dec)
                b['vx']*=ns/sp; b['vy']*=ns/sp
            if b.get('awake') and not b['dashed'] and ns==0:
                d=math.radians(b['dashDir']); b['vx']=TYPES['sheep']['dashV']*math.cos(d); b['vy']=-TYPES['sheep']['dashV']*math.sin(d); b['dashed']=True; ev.append(('dash',b['id']))
            b['x']+=b['vx']*DT; b['y']+=b['vy']*DT
            x0,y0,x1,y1=FIELD
            if b['x']<x0+b['r']: b['x']=x0+b['r']; b['vx']=abs(b['vx'])*0.5; ev.append(('wall',b['id']))
            if b['x']>x1-b['r']: b['x']=x1-b['r']; b['vx']=-abs(b['vx'])*0.5; ev.append(('wall',b['id']))
            if b['y']<y0+b['r']: b['y']=y0+b['r']; b['vy']=abs(b['vy'])*0.5; ev.append(('wall',b['id']))
            if b['y']>y1-b['r']: b['y']=y1-b['r']; b['vy']=-abs(b['vy'])*0.5; ev.append(('wall',b['id']))
            if math.hypot(b['vx'],b['vy'])>1: moving=True
            if b.get('target'):
                for h in hays:
                    if math.hypot(b['x']-h['x'],b['y']-h['y'])<h['r'] and (h.get('accepts') in (None,b['id'])):
                        b['inHay']=h['id']; b['vx']=b['vy']=0; ev.append(('hay',b['id'],h['id']))
        # 碰撞
        for i in range(len(B)):
            for j in range(i+1,len(B)):
                p,q=B[i],B[j]
                if not(p['alive'] and q['alive']) or p['inHay'] or q['inHay']: continue
                dx=q['x']-p['x']; dy=q['y']-p['y']; d=math.hypot(dx,dy); rr=p['r']+q['r']
                if d==0 or d>=rr: continue
                nx,ny=dx/d,dy/d; rv=(q['vx']-p['vx'])*nx+(q['vy']-p['vy'])*ny
                if rv<0:
                    imp=-rv
                    for o in (p,q):
                        if o['type']=='fragile' and imp>TYPES['fragile']['breakV']: o['alive']=False; ev.append(('break',o['id']))
                        if o['type']=='sheep' and not o['awake'] and imp>TYPES['sheep']['wakeV']: o['awake']=True; ev.append(('wake',o['id']))
                    if not(p['alive'] and q['alive']): continue
                    if p['static'] or q['static']: ev.append(('rock',(q if p['static'] else p)['id']))
                    e=min(p['e'],q['e']); im=1/p['m']+1/q['m']
                    jn=-(1+e)*rv/im
                    if not p['static']: p['vx']-=jn*nx/p['m']; p['vy']-=jn*ny/p['m']
                    if not q['static']: q['vx']+=jn*nx/q['m']; q['vy']+=jn*ny/q['m']
                ov=rr-d; tm=(0 if p['static'] else 1/p['m'])+(0 if q['static'] else 1/q['m'])
                if tm>0:
                    if not p['static']: p['x']-=nx*ov*(1/p['m'])/tm; p['y']-=ny*ov*(1/p['m'])/tm
                    if not q['static']: q['x']+=nx*ov*(1/q['m'])/tm; q['y']+=ny*ov*(1/q['m'])/tm
        if not moving and step>5 and not any(b.get('awake') and not b['dashed'] for b in B): break
    keep=[b for b in S]  # 原列表对象已就地更新
    return keep, ev
def init(level): return [mk(o) for o in level['objects']]
def solved(state): return all(b['inHay'] for b in state if b.get('target'))
