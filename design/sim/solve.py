import sys,math,json,time
from physics import *
from levels_src import LEVELS
ANG=[a for a in range(0,360,2)]; POW=[round(0.3+0.1*i,1) for i in range(8)]
def score(st,lv):
    s=0
    for b in st:
        if b.get('target'):
            if not b['alive']: return -1e9
            if b['inHay']: s+=1000
            else: s-=min(math.hypot(b['x']-h['x'],b['y']-h['y']) for h in lv['hays'])
    return s
def solve(lv,maxd=3,beam=6,horn=None):
    horn=horn or lv['horn']; frontier=[(score(init(lv),lv),init(lv),[])]
    for d in range(1,maxd+1):
        cand=[]
        for _,st,path in frontier:
            for a in ANG:
                for p in POW:
                    ns,ev=shoot(lv,st,a,p,horn)
                    if solved(ns) and all(b['alive'] for b in ns if b.get('target')): return path+[(a,p)]
                    cand.append((score(ns,lv),ns,path+[(a,p)]))
        cand.sort(key=lambda c:-c[0]); frontier=[]; seen=set()
        for c in cand:
            k=round(c[0])
            if k in seen: continue
            seen.add(k); frontier.append(c)
            if len(frontier)>=beam: break
    return None
if __name__=='__main__':
    ids=[int(x) for x in sys.argv[1:]] or range(1,11)
    out={}
    for lv in LEVELS:
        if lv['id'] not in ids: continue
        t=time.time(); r=solve(lv,maxd=min(3,lv['maxShots']))
        print(lv['id'],lv['name'],r,round(time.time()-t,1),flush=True); out[lv['id']]=r
    json.dump(out,open('sol_%s.json'%'_'.join(map(str,ids)),'w'))
