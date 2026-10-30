import sys
from physics import *; from solve import solve
import levels_src
def run(lv):
    r=solve(lv,maxd=min(4,lv['maxShots']),beam=8)
    evs=[]
    if r:
        st=init(lv)
        for a,p in r: st,ev=shoot(lv,st,a,p,lv['horn']); evs.append(sorted(set(e[0] for e in ev)))
    print(lv['id'],lv['name'],r,evs,flush=True); return r,evs
if __name__=='__main__':
    for lv in levels_src.LEVELS:
        if not sys.argv[1:] or str(lv['id']) in sys.argv[1:]: run(lv)
