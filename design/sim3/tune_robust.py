#!/usr/bin/env python3
"""Monte Carlo pass-rate tuner for 顶顶乐 under σA=2°, σP=0.03."""
import json, math, copy, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

ROOT = os.path.join(os.path.dirname(__file__), '..', 'data')
BASE = json.load(open(os.path.join(ROOT, 'levels.json')))

TARGETS = {1: 0.70, 2: 0.35, 3: 0.35, 4: 0.35, 5: 0.35, 6: 0.40, 7: 0.20, 8: 0.35, 9: 0.20, 10: 0.20}

def apply_global(data, hay_delta=0, angle_snap=0, power_snap=0, per_level=None):
    D = copy.deepcopy(data)
    per_level = per_level or {}
    for lv in D['levels']:
        lid = lv['id']
        pl = per_level.get(lid, {})
        for h in lv['hays']:
            h['r'] = h.get('r', 32) + hay_delta + pl.get('hayR_extra', 0)
            if 'hay_x' in pl: h['x'] = pl['hay_x']  # only if single hay override keyed by id later
        # per-hay overrides
        if 'hays' in pl:
            for i, hh in enumerate(pl['hays']):
                if i < len(lv['hays']):
                    lv['hays'][i].update(hh)
        if 'objects' in pl:
            byid = {o['id']: o for o in lv['objects']}
            for oo in pl['objects']:
                if oo['id'] in byid:
                    byid[oo['id']].update({k:v for k,v in oo.items() if k!='id'})
        if 'start' in pl:
            lv['start'].update(pl['start'])
        if 'solution' in pl:
            for i, s in enumerate(pl['solution']):
                if i < len(lv['solution']):
                    lv['solution'][i].update(s)
        if 'stars' in pl:
            lv['stars'].update(pl['stars'])
        if 'maxShots' in pl:
            lv['maxShots'] = pl['maxShots']
        lv['_angleSnap'] = pl.get('angleSnap', angle_snap)
        lv['_powerSnap'] = pl.get('powerSnap', power_snap)
    D['_angleSnap'] = angle_snap
    D['_powerSnap'] = power_snap
    return D

def mc_level(lv, N=400, sdA=2.0, sdP=0.03, seed0=0):
    sol = lv['solution']
    aSnap = lv.get('_angleSnap', 0)
    pSnap = lv.get('_powerSnap',.0)
    clear = 0
    for i in range(N):
        r = random.Random(seed0 + i*997 + lv['id']*13)
        st = init(lv)
        ok = True
        for s in sol:
            da = r.gauss(0, sdA)
            dp = r.gauss(0, sdP)
            # deadzone snap toward intended (solution) value
            if aSnap > 0 and abs(da) <= aSnap:
                da = 0.0
            if pSnap > 0 and abs(dp) <= pSnap:
                dp = 0.0
            a = s['angle'] + da
            p = max(0.05, min(1.0, s['power'] + dp))
            st, _ = shoot(lv, st, a, p, lv.get('horn', 'curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')):
            clear += 1
    return clear / N

def sweep():
    print('=== Baseline (hay+0, no snap) ===')
    D0 = apply_global(BASE, 0, 0, 0)
    for lv in D0['levels']:
        c = mc_level(lv, N=300)
        print(f"L{lv['id']:2d} {c:.3f} target>={TARGETS[lv['id']]}")

    # Try global hay deltas with various snaps
    configs = [
        (8, 3, 0.05),
        (10, 3, 0.05),
        (12, 3, 0.05),
        (8, 4, 0.06),
        (10, 4, 0.06),
        (12, 4, 0.06),
        (14, 3, 0.05),
        (10, 2.5, 0.04),
        (8, 2, 0.04),
        (12, 3.5, 0.05),
    ]
    print('\n=== Global sweeps (hayΔ, aSnap, pSnap) ===')
    results = []
    for hd, asnp, psnp in configs:
        D = apply_global(BASE, hd, asnp, psnp)
        rates = {}
        for lv in D['levels']:
            rates[lv['id']] = mc_level(lv, N=250)
        miss = [i for i,t in TARGETS.items() if rates[i] < t]
        score = sum(max(0, TARGETS[i]-rates[i]) for i in TARGETS)
        print(f"+{hd} a±{asnp} p±{psnp} | " + " ".join(f"{i}:{rates[i]:.2f}" for i in range(1,11)) + f" | miss={miss} slack={score:.2f}")
        results.append((score, miss, hd, asnp, psnp, rates))
    results.sort()
    print('\nBest:', results[0][:5])
    return results[0]

if __name__ == '__main__':
    sweep()
