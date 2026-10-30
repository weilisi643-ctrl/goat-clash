import json,copy,sim
C=json.load(open('../data/champions.json'))
T=json.load(open('tune_out.json'))
def setv(d,si,**kw): d['stages'][si]['ai'].update(kw)
V=copy.deepcopy(C);V['version']=2
for d in V['days']:
    s1pb,_= T[str(d['day'])][0]; s2pb,_=T[str(d['day'])][1]
    setv(d,0,powBonus=max(0,s1pb))
    if s1pb<0:  # 不用负数：改调 timingHit
        best=None
        for th in [x/100 for x in range(0,31,5)]:
            dd=copy.deepcopy(d);setv(dd,0,timingHit=th);v=sim.rate(dd,0,'normal',3000)
            if best is None or abs(v-.86)<abs(best[1]-.86): best=(th,v)
        setv(d,0,timingHit=best[0])
    s1=sim.rate(d,0,'normal',6000)
    setv(d,1,powBonus=max(0,s2pb))
    best=None
    for th in [x/100 for x in range(30,91,5)]:
        dd=copy.deepcopy(d);setv(dd,1,timingHit=th);v=sim.rate(dd,1,'normal',3000)*s1
        if best is None or abs(v-.14)<abs(best[1]-.14): best=(th,v)
    setv(d,1,timingHit=best[0])
    for s in d['stages']:
        s['ai']['readAcc']=0; s['ai']['counterPick']=0; s['angleReveal']='public'
    d['stages'][1]['angleReveal']='hidden'
    r1n=sim.rate(d,0,'normal',8000,seed=7); r2n=sim.rate(d,1,'normal',8000,seed=7)
    r2p=sim.rate(d,1,'perfect',3000,seed=7); r1p=sim.rate(d,0,'perfect',2000,seed=7)
    d['sim']={'s1Normal':round(r1n,3),'s2Normal':round(r2n,3),'clearNormal':round(r1n*r2n,3),'s1Perfect':round(r1p,3),'s2Perfect':round(r2p,3)}
    print(d['day'],d['stages'][0]['ai'],d['stages'][1]['ai'],d['sim'],flush=True)
V['simNote']='design/sim2/sim.py 复刻 main.js clash()；普通玩家=按点偏差 sd0.15、羊毛蓬松、限定角随机、70%避开擂主克制角度；完美玩家=timing 1、最优羊毛/角、总避克制'
json.dump(V,open('../data/champions.v2.json','w'),ensure_ascii=False,indent=2)
