#!/usr/bin/env python3
"""Per-shot sensitivity + search more robust solutions with larger hay."""
import json, math, copy, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from physics import init, shoot, solved

BASE = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'levels.json')))

def with_hay(lv, delta):
    L = copy.deepcopy(lv)
    for h in L['hays']:
        h['r'] = h.get('r', 32) + delta
    return L

def pass_rate(lv, sol, N=200, sdA=2, sdP=0.03):
    c=0
    for i in range(N):
        r=random.Random(i*997+lv['id'])
        st=init(lv)
        for s in sol:
            a=s['angle']+r.gauss(0,sdA); p=max(0.05,min(1.0,s['power']+r.gauss(0,sdP)))
            st,_=shoot(lv,st,a,p,lv.get('horn','curl'))
        if solved(st) and all(b['alive'] for b in st if b.get('target')): c+=1
    return c/N

def step_sens(lv, sol, step_i, dA=1.0, dP=0.05):
    """Fix other steps; vary one step; measure clear rate on a grid."""
    results=[]
    for da in [-3,-2,-1,0,1,2,3]:
        for dp in [-0.1,-0.05,0,0.05,0.1]:
            trial=[dict(s) for s in sol]
            trial[step_i]['angle']=sol[step_i]['angle']+da*dA
            trial[step_i]['power']=max(0.05,min(1.0,sol[step_i]['power']+dp))
            # deterministic single path (no noise) — just check if this exact path clears
            st=init(lv)
            for s in trial:
                st,_=shoot(lv,st,s['angle'],s['power'],lv.get('horn','curl'))
            ok=solved(st) and all(b['alive'] for b in st if b.get('target'))
            results.append((da*dA, dp, ok))
    return results

def search_robust(lv, base_sol, hay_delta=12, N=120):
    """Local search around base_sol for max pass rate under noise."""
    L=with_hay(lv, hay_delta)
    best=base_sol; best_r=pass_rate(L, base_sol, N=N)
    # try small perturbations of each step
    for it in range(40):
        cand=[dict(s) for s in best]
        si=it % len(cand)
        cand[si]['angle'] += random.choice([-3,-2,-1,0,1,2,3])
        cand[si]['power'] = max(0.4, min(1.0, cand[si]['power'] + random.choice([-0.15,-0.1,-0.05,0,0.05])))
        # verify deterministic clear
        st=init(L)
        for s in cand:
            st,_=shoot(L,st,s['angle'],s['power'],L.get('horn','curl'))
        if not (solved(st) and all(b['alive'] for b in st if b.get('target'))):
            continue
        r=pass_rate(L, cand, N=N)
        if r>best_r:
            best_r=r; best=cand
            print(f"  improved L{lv['id']} -> {best_r:.2f} sol={[(s['angle'],round(s['power'],2)) for s in best]}")
    return best, best_r

print('=== Sensitivity (hay+12): fraction of nearby grid that still clears ===')
for lv in BASE['levels']:
    L=with_hay(lv, 12)
    sol=lv['solution']
    print(f"\nL{lv['id']} {lv['name']} base_rate={pass_rate(L,sol,N=200):.2f} shots={len(sol)}")
    for i in range(len(sol)):
        grid=step_sens(L, sol, i)
        ok=sum(1 for _,_,o in grid if o)
        print(f"  step{i+1} a={sol[i]['angle']} p={sol[i]['power']}: {ok}/{len(grid)} nearby OK")

print('\n=== Robust search (hay+12) ===')
random.seed(42)
new_sols={}
for lv in BASE['levels']:
    if lv['id']==1: continue
    print(f'Searching L{lv["id"]}...')
    best,r=search_robust(lv, lv['solution'], hay_delta=12, N=100)
    new_sols[lv['id']]=(best,r)
    print(f'  FINAL L{lv["id"]} {r:.2f}')
