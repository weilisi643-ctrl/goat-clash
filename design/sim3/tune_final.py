#!/usr/bin/env python3
"""Final tuning: large hay, layout nudges, adaptive MC, power notch."""
import json, math, copy, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

BASE = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.json')))
TARGETS = {1: 0.70, 2: 0.35, 3: 0.35, 4: 0.35, 5: 0.35, 6: 0.40, 7: 0.20, 8: 0.35, 9: 0.20, 10: 0.20}

def power_notch(p, snap=0.05):
    for n in (0.5,0.6,0.7,0.8,0.9,1.0):
        if abs(p-n)<=snap: return n
    return p

def apply_plan(data, plan):
    """plan: {global_hay, power_snap, levels: {id: overrides}}"""
    D=copy.deepcopy(data)
    D['assist']={
        'hayRadiusBonus': plan['global_hay'],
        'powerSnap': plan.get('power_snap', 0.05),
        'angleSnap': plan.get('angle_snap', 3),
        'aimAssistDefault': plan.get('aim_assist', True),
        'note': plan.get('note','')
    }
    for lv in D['levels']:
        ov=plan['levels'].get(lv['id'], {})
        for h in lv['hays']:
            h['r'] = h.get('r',32) + plan['global_hay'] + ov.get('hayR_extra',0)
        if 'hays' in ov:
            for i,hh in enumerate(ov['hays']):
                if i<len(lv['hays']): lv['hays'][i].update(hh)
        if 'objects' in ov:
            byid={o['id']:o for o in lv['objects']}
            for oo in ov['objects']:
                if oo['id'] in byid: byid[oo['id']].update({k:v for k,v in oo.items() if k!='id'})
        if 'start' in ov: lv['start'].update(ov['start'])
        if 'solution' in ov:
            for i,s in enumerate(ov['solution']):
                if i<len(lv['solution']): lv['solution'][i].update(s)
        if 'stars' in ov: lv['stars'].update({str(k):v for k,v in ov['stars'].items()})
        if 'maxShots' in ov: lv['maxShots']=ov['maxShots']
        # re-verify solution after edits
        st=init(lv)
        ok=True
        for s in lv['solution']:
            st,_=shoot(lv,st,s['angle'],s['power'],lv.get('horn','curl'))
        if not (solved(st) and all(b['alive'] for b in st if b.get('target'))):
            lv['verified']=False
            print(f'WARN L{lv["id"]} solution broken after edits')
        else:
            lv['verified']=True
    D['version']=2
    return D

def mc_blind(lv, N=400, sdA=2, sdP=0.03, psnap=0.05):
    c=0
    for i in range(N):
        r=random.Random(i*997+lv['id']*13)
        st=init(lv)
        for s in lv['solution']:
            a=s['angle']+r.gauss(0,sdA)
            p=max(0.05,min(1.0,s['power']+r.gauss(0,sdP)))
            if psnap: p=power_notch(p,psnap)
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

def mc_adaptive(lv, N=200, sdA=2, sdP=0.03, psnap=0.05, search_a=4, search_p=0.08):
    """After each noisy shot, pick next shot by local search around remaining solution step."""
    sol=lv['solution']; c=0
    for i in range(N):
        r=random.Random(i*991+lv['id']*17)
        st=init(lv); shots_used=0; max_s=lv['maxShots']; si=0
        while not (solved(st) and all(b['alive'] for b in st if b.get('target'))) and shots_used<max_s:
            # intended: if we still have solution steps, use them; else aim toward target/hay
            if si < len(sol):
                base_a, base_p = sol[si]['angle'], sol[si]['power']
            else:
                # recovery: aim at first free target
                tgt=next((b for b in st if b.get('target') and not b.get('inHay') and b['alive']), None)
                if not tgt: break
                sx,sy=lv['start']['x'],lv['start']['y']
                base_a=math.degrees(math.atan2(-(tgt['y']-sy), tgt['x']-sx))%360
                base_p=0.85
            # player noise
            a=base_a+r.gauss(0,sdA); p=max(0.05,min(1.0,base_p+r.gauss(0,sdP)))
            if psnap: p=power_notch(p,psnap)
            # soft angle snap: pull 50% toward base if within angleSnap of base
            if abs(((a-base_a+180)%360)-180)<=3:
                a=base_a  # within ±3 of intended → snap
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
            shots_used+=1; si+=1
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

# ---- Plan: global + per-level ----
# Philosophy: global hay+10, powerSnap±0.05, angleSnap±3° toward intended (UI: soft magnet to object/hay line when within 3°)
# Hard levels get extra hay and small hay position nudges toward natural landings; soften some solution powers; allow +1 maxShot for recovery on 7/10.

PLAN = {
    'global_hay': 10,
    'power_snap': 0.05,
    'angle_snap': 3,
    'aim_assist': True,
    'note': 'v2 容错：全局草堆+10；力度条吸附 ±0.05 到 0.5/0.6/0.7/0.8/0.9/1.0；瞄准线在 ±3° 内吸附到指向最近可推物件/草堆的方向。不改物理核心。',
    'levels': {
        1: {'hayR_extra': 0},  # r 34→44 enough with global
        2: {
            'hayR_extra': 6,  # total +16 → r48
            'hays': [{'x': 280, 'y': 210}],  # slightly closer/lower
            'solution': [
                {'angle': 70, 'power': 0.95},
                {'angle': 74, 'power': 0.85},
            ],
        },
        3: {
            'hayR_extra': 8,  # total +18 → r54
            'hays': [{'x': 80, 'y': 240}],
            'solution': [
                {'angle': 62, 'power': 0.95},
                {'angle': 102, 'power': 0.85},
            ],
        },
        4: {
            'hayR_extra': 8,
            'hays': [{'x': 290, 'y': 200}],
            'solution': [
                {'angle': 64, 'power': 0.95},
                {'angle': 58, 'power': 0.95},
                {'angle': 56, 'power': 0.85},
            ],
            'maxShots': 6,
            'stars': {3: 3, 2: 4, 1: 6},
        },
        5: {
            'hayR_extra': 6,
            'hays': [{'y': 155}],  # slightly closer
            'solution': [
                {'angle': 90, 'power': 0.95},  # still break fragile
                {'angle': 90, 'power': 0.75},
            ],
        },
        6: {
            'hayR_extra': 8,  # r30→48
            'hays': [{'x': 320, 'y': 420}],
            'solution': [{'angle': 58, 'power': 0.7}],
        },
        7: {
            'hayR_extra': 10,  # each hay r42
            'hays': [{'x': 75, 'y': 210}, {'x': 300, 'y': 210}],
            'solution': [
                {'angle': 110, 'power': 0.95},
                {'angle': 70, 'power': 0.95},
                {'angle': 68, 'power': 0.9},
                {'angle': 110, 'power': 0.85},
            ],
            'maxShots': 7,
            'stars': {3: 4, 2: 5, 1: 7},
        },
        8: {
            'hayR_extra': 10,
            'hays': [{'x': 80, 'y': 155}],
            'solution': [{'angle': 92, 'power': 0.9}],
        },
        9: {
            'hayR_extra': 10,
            'hays': [{'y': 120}],
            'solution': [{'angle': 82, 'power': 0.95}],
        },
        10: {
            'hayR_extra': 10,
            'hays': [{'x': 95, 'y': 160}, {'x': 285, 'y': 160}],
            'solution': [
                {'angle': 62, 'power': 0.8},
                {'angle': 118, 'power': 0.95},
                {'angle': 116, 'power': 0.95},
                {'angle': 114, 'power': 0.9},
            ],
            'maxShots': 7,
            'stars': {3: 4, 2: 5, 1: 7},
        },
    }
}

D=apply_plan(BASE, PLAN)
print('Verified flags:', [(lv['id'], lv['verified'], [(h['r'],h['x'],h['y']) for h in lv['hays']]) for lv in D['levels']])

print('\n=== Blind MC (σA=2,σP=0.03) + power notch ===')
blind={}
for lv in D['levels']:
    blind[lv['id']]=mc_blind(lv, N=400, psnap=0.05)
    print(f"L{lv['id']:2d} blind={blind[lv['id']]:.2f} target>={TARGETS[lv['id']]}")

print('\n=== Adaptive MC (noise + angleSnap±3 to intended + recovery shots) ===')
adapt={}
for lv in D['levels']:
    adapt[lv['id']]=mc_adaptive(lv, N=250, psnap=0.05)
    t=TARGETS[lv['id']]
    ok='OK' if adapt[lv['id']]>=t-0.02 else 'LOW'
    print(f"L{lv['id']:2d} adapt={adapt[lv['id']]:.2f} target>={t} {ok}")

# If still low, try bigger hay extras
print('\n=== Diagnose lows: try hay+20 global on current layout ===')
PLAN2=copy.deepcopy(PLAN); PLAN2['global_hay']=16
D2=apply_plan(BASE, PLAN2)
for lv in D2['levels']:
    b=mc_blind(lv,N=200); a=mc_adaptive(lv,N=150)
    print(f"L{lv['id']:2d} blind={b:.2f} adapt={a:.2f}")
