#!/usr/bin/env python3
"""More realistic assist models + hay-only sweeps."""
import json, math, copy, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

ROOT = os.path.join(os.path.dirname(__file__), '..', 'data')
BASE = json.load(open(os.path.join(ROOT, 'levels.json')))
TARGETS = {1: 0.70, 2: 0.35, 3: 0.35, 4: 0.35, 5: 0.35, 6: 0.40, 7: 0.20, 8: 0.35, 9: 0.20, 10: 0.20}

def apply_hay(data, delta, per=None):
    D = copy.deepcopy(data)
    per = per or {}
    for lv in D['levels']:
        extra = per.get(lv['id'], 0)
        for h in lv['hays']:
            h['r'] = h.get('r', 32) + delta + extra
        # per-level structured overrides
        ov = per.get(f'L{lv["id"]}')
        if isinstance(ov, dict):
            if 'hays' in ov:
                for i, hh in enumerate(ov['hays']):
                    if i < len(lv['hays']): lv['hays'][i].update(hh)
            if 'solution' in ov:
                for i, s in enumerate(ov['solution']):
                    if i < len(lv['solution']): lv['solution'][i].update(s)
            if 'objects' in ov:
                byid = {o['id']: o for o in lv['objects']}
                for oo in ov['objects']:
                    if oo['id'] in byid: byid[oo['id']].update({k:v for k,v in oo.items() if k!='id'})
            if 'stars' in ov: lv['stars'].update(ov['stars'])
            if 'maxShots' in ov: lv['maxShots'] = ov['maxShots']
            if 'hayR_extra' in ov:
                for h in lv['hays']: h['r'] += ov['hayR_extra']
    return D

def angle_to(ax, ay, bx, by):
    # 0=right, 90=up (screen -y)
    return math.degrees(math.atan2(-(by - ay), bx - ax)) % 360

def magnet_angle(level, state, aim, cone=8.0):
    """Pull aim toward nearest living object's center if within cone degrees."""
    sx, sy = level['start']['x'], level['start']['y']
    best = None
    for b in state:
        if not b.get('alive') or b.get('inHay') or b.get('static') and b['type']=='rock':
            # still magnet to rocks for rebound aiming? skip rocks for magnet
            if b.get('static'): continue
        if not b.get('alive') or b.get('inHay'): continue
        ta = angle_to(sx, sy, b['x'], b['y'])
        d = (aim - ta + 180) % 360 - 180
        if abs(d) <= cone and (best is None or abs(d) < abs(best[0])):
            best = (d, ta)
    # also magnet toward hays (goal direction)
    for h in level['hays']:
        ta = angle_to(sx, sy, h['x'], h['y'])
        d = (aim - ta + 180) % 360 - 180
        if abs(d) <= cone and (best is None or abs(d) < abs(best[0])):
            best = (d, ta)
    if best: return best[1]
    return aim

def power_grid(p, step=0.05):
    return round(p / step) * step

def power_deadzone(p, notches=(0.5, 0.6, 0.7, 0.8, 0.9, 1.0), snap=0.05):
    for n in notches:
        if abs(p - n) <= snap:
            return n
    return p

def mc(lv, N=400, sdA=2.0, sdP=0.03, mode='none', cone=8.0, pstep=0.05, psnap=0.05, seed0=0):
    sol = lv['solution']
    clear = 0
    for i in range(N):
        r = random.Random(seed0 + i*997 + lv['id']*13)
        st = init(lv)
        for s in sol:
            a = s['angle'] + r.gauss(0, sdA)
            p = max(0.05, min(1.0, s['power'] + r.gauss(0, sdP)))
            if mode in ('magnet', 'magnet+grid', 'magnet+notch'):
                a = magnet_angle(lv, st, a, cone=cone)
            if mode in ('grid', 'magnet+grid'):
                p = max(0.05, min(1.0, power_grid(p, pstep)))
            if mode in ('notch', 'magnet+notch'):
                p = power_deadzone(p, snap=psnap)
            if mode == 'sol_deadzone':
                # idealised: snap to solution if within thresholds
                if abs(a - s['angle']) <= cone: a = s['angle']
                if abs(p - s['power']) <= psnap: p = s['power']
            st, _ = shoot(lv, st, a, p, lv.get('horn', 'curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')):
            clear += 1
    return clear / N

def report(label, D, mode='none', **kw):
    rates = {}
    for lv in D['levels']:
        rates[lv['id']] = mc(lv, mode=mode, **kw)
    miss = [i for i,t in TARGETS.items() if rates[i] < t - 0.01]
    print(f"{label:40s} | " + " ".join(f"{i}:{rates[i]:.2f}" for i in range(1,11)) + f" | miss={miss}")
    return rates, miss

print('=== Hay-only (no snap) ===')
for hd in [0, 8, 12, 16, 20, 24, 28]:
    report(f'hay+{hd}', apply_hay(BASE, hd), N=300)

print('\n=== Hay + power notch ±0.05 ===')
for hd in [8, 12, 16, 20]:
    report(f'hay+{hd} notch', apply_hay(BASE, hd), mode='notch', psnap=0.05, N=300)

print('\n=== Hay + magnet cone ===')
for hd, cone in [(8,6),(8,8),(12,8),(16,8),(12,10),(16,10)]:
    report(f'hay+{hd} mag±{cone}', apply_hay(BASE, hd), mode='magnet', cone=cone, N=300)

print('\n=== Hay + magnet + notch ===')
for hd, cone in [(8,8),(12,8),(16,8),(12,10)]:
    report(f'hay+{hd} mag±{cone}+notch', apply_hay(BASE, hd), mode='magnet+notch', cone=cone, psnap=0.05, N=300)
