#!/usr/bin/env python3
import json, copy, random, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

D=json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.v2.json')))
TARGETS={1:0.70,2:0.35,3:0.35,4:0.35,5:0.35,6:0.40,7:0.20,8:0.35,9:0.20,10:0.20}

# Extra bump hard single-shot / rebound levels' hay for blind safety
extra = {
  3: 4,   # r54→58
  8: 6,   # r54→60
  9: 6,   # r52→58
  10: 4,  # r52→56
}
for lv in D['levels']:
    if lv['id'] in extra:
        for h in lv['hays']:
            h['r'] += extra[lv['id']]
    # Soften power 1.0 → 0.95 where still clears (wider headroom below clamp)
    for s in lv['solution']:
        if s['power'] >= 0.98:
            trial=copy.deepcopy(lv)
            # test 0.95
            st=init(lv); ok=True
            for ss in lv['solution']:
                p=0.95 if ss is s else ss['power']
                # careful: ss is identity
            # simpler: clone solution with this step at 0.95
            sol2=[dict(x) for x in lv['solution']]
            for i,ss in enumerate(lv['solution']):
                if ss is s: sol2[i]['power']=0.95
            st=init(lv)
            for ss in sol2:
                st,_=shoot(lv,st,ss['angle'],ss['power'],lv.get('horn','curl'))
            if solved(st) and all(b['alive'] for b in st if b.get('target')):
                s['power']=0.95

def power_notch(p, snap=0.05):
    for n in (0.5,0.6,0.7,0.8,0.9,1.0):
        if abs(p-n)<=snap: return n
    return p

def mc_blind(lv, N=500, a_snap=0, psnap=0.05):
    c=0
    for i in range(N):
        r=random.Random(i*997+lv['id']*13)
        st=init(lv)
        for s in lv['solution']:
            da=r.gauss(0,2); a=s['angle']+da
            p=max(0.05,min(1.0,s['power']+r.gauss(0,0.03)))
            if a_snap and abs(da)<=a_snap: a=s['angle']
            if psnap: p=power_notch(p,psnap)
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

def mc_adapt(lv, N=300, a_snap=3, psnap=0.05):
    sol=lv['solution']; c=0
    for i in range(N):
        r=random.Random(i*991+lv['id']*17)
        st=init(lv); si=0; shots=0
        while not (solved(st) and all(b['alive'] for b in st if b.get('target'))) and shots<lv['maxShots']:
            if si < len(sol): ba,bp=sol[si]['angle'],sol[si]['power']
            else:
                tgt=next((b for b in st if b.get('target') and not b.get('inHay') and b['alive']), None)
                if not tgt: break
                sx,sy=lv['start']['x'],lv['start']['y']
                ba=math.degrees(math.atan2(-(tgt['y']-sy),tgt['x']-sx))%360; bp=0.85
            da=r.gauss(0,2); a=ba+da; p=max(0.05,min(1.0,bp+r.gauss(0,0.03)))
            if a_snap and abs(da)<=a_snap: a=ba
            if psnap: p=power_notch(p,psnap)
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
            shots+=1; si+=1
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

# re-verify
for lv in D['levels']:
    st=init(lv)
    for s in lv['solution']:
        st,ev=shoot(lv,st,s['angle'],s['power'],lv.get('horn','curl'))
        s['events']=sorted({e[0] for e in ev})
    lv['verified']=solved(st) and all(b['alive'] for b in st if b.get('target'))
    assert lv['verified'], lv['id']

print('id | hay r | blind | blind+snap3 | adapt | target | sol')
rows=[]
for lv in D['levels']:
    b0=mc_blind(lv,a_snap=0)
    b3=mc_blind(lv,a_snap=3)
    a3=mc_adapt(lv)
    t=TARGETS[lv['id']]
    rs=[h['r'] for h in lv['hays']]
    print(f"L{lv['id']:2d} r={rs} blind={b0:.2f} snap={b3:.2f} adapt={a3:.2f} tgt={t} sol={[(s['angle'],s['power']) for s in lv['solution']]}")
    rows.append(dict(id=lv['id'],name=lv['name'],hay_r=rs,blind=round(b0,3),blind_snap=round(b3,3),adapt=round(a3,3),target=t,
                     maxShots=lv['maxShots'],stars=lv['stars'],solution=[(s['angle'],s['power']) for s in lv['solution']],
                     hays=lv['hays']))

# Also baseline comparison without assist fields pollution
D['assist']={
    'version': 2,
    'physicsUnchanged': True,
    'globalHayDelta': 10,
    'perLevelHayExtra': {2:6,3:14,4:8,5:6,6:8,7:10,8:16,9:16,10:14},
    'powerSnap': 0.05,
    'powerSnapNotches': [0.5,0.6,0.7,0.8,0.9,1.0],
    'angleSnapDeg': 3,
    'angleSnapRule': '开火结算前：在瞄准角与「起点→最近可推物件(非石块)中心」或「起点→最近草堆中心」的夹角中取最小者；若 |Δ|≤3° 则吸附到该方向。石块不参与。默认开，设置可关。',
    'aimAssistDefaultOn': True,
    'doNotChange': ['physics.dt','frictionG','maxSpeed','objectTypes','hornMods','ddl_physics.js 碰撞核心'],
}

out=os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.v2.json')
json.dump(D, open(out,'w'), ensure_ascii=False, indent=1)
json.dump(rows, open(os.path.join(os.path.dirname(__file__), 'report.json'),'w'), ensure_ascii=False, indent=2)
print('wrote', out)
# sanity load
json.load(open(out))
print('json ok, all verified', all(lv['verified'] for lv in D['levels']))
# miss check
miss_blind=[r['id'] for r in rows if r['blind']<r['target']-0.01]
miss_snap=[r['id'] for r in rows if r['blind_snap']<r['target']-0.01]
miss_adapt=[r['id'] for r in rows if r['adapt']<r['target']-0.01]
print('miss blind', miss_blind)
print('miss blind+snap', miss_snap)
print('miss adapt', miss_adapt)
