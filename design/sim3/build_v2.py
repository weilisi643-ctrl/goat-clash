#!/usr/bin/env python3
"""Build levels.v2.json with verified solutions + MC report."""
import json, math, copy, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

BASE = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.json')))
TARGETS = {1: 0.70, 2: 0.35, 3: 0.35, 4: 0.35, 5: 0.35, 6: 0.40, 7: 0.20, 8: 0.35, 9: 0.20, 10: 0.20}

def power_notch(p, snap=0.05):
    for n in (0.5,0.6,0.7,0.8,0.9,1.0):
        if abs(p-n)<=snap: return n
    return p

def check_sol(lv, sol=None):
    sol = sol or lv['solution']
    st=init(lv)
    for s in sol:
        st,_=shoot(lv,st,s['angle'],s['power'],lv.get('horn','curl'))
    return solved(st) and all(b['alive'] for b in st if b.get('target'))

def find_sol(lv, nshots, a_lo=20, a_hi=160, beam=12):
    """Beam search for a solution with nshots."""
    # coarse grid
    angles=list(range(a_lo, a_hi+1, 2))
    powers=[0.6,0.7,0.75,0.8,0.85,0.9,0.95,1.0]
    beam_states=[(init(lv), [])]
    for depth in range(nshots):
        cand=[]
        for st0, path in beam_states:
            if solved(st0) and all(b['alive'] for b in st0 if b.get('target')):
                return path
            for a in angles:
                for p in powers:
                    st,_=shoot(lv, copy.deepcopy(st0) if False else (lambda: (lambda s: (shoot(lv,s,a,p,lv.get('horn','curl'))[0]))(copy.deepcopy(st0)))(), a, p, lv.get('horn','curl')) if False else None
        # rewrite cleanly
        break
    # clean rewrite
    from copy import deepcopy
    beam_states=[(init(lv), [])]
    for depth in range(nshots):
        cand=[]
        for st0, path in beam_states:
            if solved(st0) and all(b['alive'] for b in st0 if b.get('target')):
                return path
            for a in angles:
                for p in powers:
                    st2=deepcopy(st0)
                    st2,_=shoot(lv,st2,a,p,lv.get('horn','curl'))
                    # score: how many targets in hay + closeness of remaining to nearest hay
                    scored=0
                    dist=0
                    for b in st2:
                        if not b.get('target'): continue
                        if b.get('inHay'): scored+=1000
                        elif not b['alive']: scored-=500
                        else:
                            dmin=min(math.hypot(b['x']-h['x'],b['y']-h['y']) for h in lv['hays'])
                            dist+=dmin
                    cand.append((-(scored)+dist/100, st2, path+[{'angle':a,'power':p}]))
        cand.sort(key=lambda x:x[0])
        beam_states=[(s,p) for _,s,p in cand[:beam]]
        for st0, path in beam_states:
            if solved(st0) and all(b['alive'] for b in st0 if b.get('target')):
                return path
    for st0, path in beam_states:
        if solved(st0) and all(b['alive'] for b in st0 if b.get('target')):
            return path
    return None

# ---- Construct v2 levels by editing BASE ----
D=copy.deepcopy(BASE)
D['version']=2
D['assist']={
    'hayRadiusBonusAppliedInLevels': True,
    'globalHayDelta': 10,
    'powerSnap': 0.05,
    'powerSnapNotches': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    'angleSnapDeg': 3,
    'angleSnapRule': '开火时若瞄准角与「指向最近可推物件或草堆中心」的夹角 ≤3°，吸附到该方向；石块不参与吸附。可做设置项，默认开。',
    'aimAssistDefaultOn': True,
    'physicsUnchanged': True,
}

OVERRIDES = {
    1: {
        'hays': [{'r': 44}],  # 34+10
    },
    2: {
        'hays': [{'x': 275, 'y': 215, 'r': 48}],  # +16, nudge closer
        'solution': None,  # re-find
        'nshots': 2,
    },
    3: {
        'hays': [{'x': 75, 'y': 235, 'r': 54}],
        'solution': None,
        'nshots': 2,
    },
    4: {
        'hays': [{'x': 285, 'y': 195, 'r': 50}],
        'maxShots': 6,
        'stars': {'3': 3, '2': 4, '1': 6},
        'solution': None,
        'nshots': 3,
    },
    5: {
        'hays': [{'x': 187, 'y': 155, 'r': 48}],
        'solution': None,
        'nshots': 2,
    },
    6: {
        'hays': [{'x': 318, 'y': 420, 'r': 48}],
        'solution': None,
        'nshots': 1,
    },
    7: {
        'hays': [{'x': 78, 'y': 210, 'r': 52}, {'x': 297, 'y': 210, 'r': 52}],
        'maxShots': 7,
        'stars': {'3': 4, '2': 5, '1': 7},
        'solution': None,
        'nshots': 4,
    },
    8: {
        'hays': [{'x': 85, 'y': 160, 'r': 54}],
        'solution': None,
        'nshots': 1,
    },
    9: {
        'hays': [{'x': 187, 'y': 125, 'r': 52}],
        'solution': None,
        'nshots': 1,
    },
    10: {
        'hays': [{'x': 95, 'y': 165, 'r': 52}, {'x': 280, 'y': 165, 'r': 52}],
        'maxShots': 7,
        'stars': {'3': 4, '2': 5, '1': 7},
        'solution': None,
        'nshots': 4,
    },
}

for lv in D['levels']:
    ov = OVERRIDES[lv['id']]
    if 'hays' in ov:
        for i, hh in enumerate(ov['hays']):
            lv['hays'][i].update(hh)
    if 'maxShots' in ov: lv['maxShots']=ov['maxShots']
    if 'stars' in ov: lv['stars']=ov['stars']
    # keep original solution if still works, else search
    if check_sol(lv):
        print(f"L{lv['id']} original sol OK")
        lv['verified']=True
    else:
        print(f"L{lv['id']} searching {ov.get('nshots')} shots...")
        sol=find_sol(lv, ov.get('nshots', len(lv['solution'])))
        if sol is None and ov.get('nshots',2)<6:
            sol=find_sol(lv, ov.get('nshots',2)+1)
        if sol is None:
            # try with original shot count from BASE
            for n in range(1, lv['maxShots']+1):
                sol=find_sol(lv, n)
                if sol: break
        if sol:
            lv['solution']=[{'angle':s['angle'],'power':s['power'],'events':[]} for s in sol]
            # refresh events
            st=init(lv)
            for s in lv['solution']:
                st,ev=shoot(lv,st,s['angle'],s['power'],lv.get('horn','curl'))
                kinds=sorted({e[0] for e in ev})
                s['events']=kinds
            lv['verified']=True
            # update stars if solution length changed
            n=len(lv['solution'])
            if n <= lv['stars']['3']:
                pass
            else:
                lv['stars']={'3': n, '2': min(n+1, lv['maxShots']), '1': lv['maxShots']}
            print(f"  found {n} shots: {[(s['angle'],s['power']) for s in lv['solution']]}")
        else:
            lv['verified']=False
            print(f"  FAILED to find solution!")

# Prefer lower power when nearby alternatives have similar robustness
# Quick refine: for each level, try power -0.05/-0.1 if still clears and better blind rate

def mc_blind(lv, N=300, sdA=2, sdP=0.03, psnap=0.05, a_snap=0):
    c=0
    for i in range(N):
        r=random.Random(i*997+lv['id']*13)
        st=init(lv)
        for s in lv['solution']:
            da=r.gauss(0,sdA); dp=r.gauss(0,sdP)
            a=s['angle']+da; p=max(0.05,min(1.0,s['power']+dp))
            if a_snap and abs(da)<=a_snap: a=s['angle']
            if psnap: p=power_notch(p,psnap)
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

def mc_adapt(lv, N=200, sdA=2, sdP=0.03, psnap=0.05, a_snap=3):
    sol=lv['solution']; c=0
    for i in range(N):
        r=random.Random(i*991+lv['id']*17)
        st=init(lv); si=0; shots=0
        while not (solved(st) and all(b['alive'] for b in st if b.get('target'))) and shots<lv['maxShots']:
            if si < len(sol):
                ba,bp=sol[si]['angle'],sol[si]['power']
            else:
                tgt=next((b for b in st if b.get('target') and not b.get('inHay') and b['alive']), None)
                if not tgt: break
                sx,sy=lv['start']['x'],lv['start']['y']
                ba=math.degrees(math.atan2(-(tgt['y']-sy),tgt['x']-sx))%360; bp=0.85
            da=r.gauss(0,sdA); a=ba+da; p=max(0.05,min(1.0,bp+r.gauss(0,sdP)))
            if a_snap and abs(da)<=a_snap: a=ba
            if psnap: p=power_notch(p,psnap)
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
            shots+=1; si+=1
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

print('\n=== Rates ===')
report=[]
for lv in D['levels']:
    b0=mc_blind(lv, a_snap=0)
    b3=mc_blind(lv, a_snap=3)
    a3=mc_adapt(lv, a_snap=3)
    t=TARGETS[lv['id']]
    report.append({'id':lv['id'],'name':lv['name'],'blind':round(b0,3),'blind+aSnap3':round(b3,3),'adapt+aSnap3':round(a3,3),'target':t,'ok':a3>=t-0.02,'shots':len(lv['solution']),'verified':lv['verified']})
    print(f"L{lv['id']:2d} blind={b0:.2f} blind+snap={b3:.2f} adapt={a3:.2f} tgt>={t} verified={lv['verified']} sol={[(s['angle'],s['power']) for s in lv['solution']]}")

out=os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.v2.json')
json.dump(D, open(out,'w'), ensure_ascii=False, indent=1)
print('Wrote', out)
json.dump(report, open(os.path.join(os.path.dirname(__file__), 'report.json'),'w'), ensure_ascii=False, indent=2)
print('All verified?', all(lv['verified'] for lv in D['levels']))
