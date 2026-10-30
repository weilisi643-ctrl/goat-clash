import json,copy,sim
C=json.load(open('../data/champions.json'))
def solve(d,si,target,lo=-15,hi=30,n=3000):
    best=None
    for pb in range(lo,hi+1):
        dd=copy.deepcopy(d);dd['stages'][si]['ai']['powBonus']=pb
        v=sim.rate(dd,si,'normal',n)
        if best is None or abs(v-target)<abs(best[1]-target): best=(pb,v)
    return best
out={}
for d in C['days']:
    s1=solve(d,0,0.85,-10,15)
    s2=solve(d,1,0.15/s1[1],-15,30)
    out[d['day']]=(s1,s2);print(d['day'],s1,s2,flush=True)
json.dump(out,open('tune_out.json','w'))
