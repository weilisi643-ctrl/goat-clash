# 复刻 js/main.js clash()（REASONING_ENABLED=false, QUIZ off）蒙特卡洛
import json,random,sys
D={'wools':{'fluffy':(10,0),'short':(0,10),'spots':(5,5),'cloud':(15,-5)},
   'horns':{'curl':(0,'low'),'straight':(10,'high'),'spiral':(5,'mid'),'branch':(15,'none')}}
STANCE={'low_charge':'low','low_sweep':'low','mid_ram':'mid','mid_feint':'mid','high_leap':'high','high_rear':'high'}
ANG=['low','mid','high']
def ptiming(prof,r):
    if prof=='perfect': return 1.0
    m=0.8+r.gauss(0,0.15)          # 普通玩家：按点偏差 sd=0.15 条长
    return max(0.0,1-abs(m-0.8)/0.8)
def match(cfg,st,wool,horn,prof,reveal,r):
    hp0=100+D['wools'][wool][0]; spd=D['wools'][wool][1]; pw,pwin=D['horns'][horn]
    ew,eh=cfg['look']['wool'],cfg['look']['horn']; ehp0=100+D['wools'][ew][0]+st['ai']['hpBonus']
    espd=D['wools'][ew][1]; epow,ewin=D['horns'][eh]; ai=st['ai']; prefs=[STANCE[s] for s in cfg['stancePref']]
    wins=[0,0]
    while max(wins)<2:
        php,ehp=hp0,ehp0
        while php>0 and ehp>0:
            eang=STANCE[r.choice(cfg['stancePref'])]
            # 玩家角度：只影响对手克制（es.win===pAng）。完美玩家永远避开；普通玩家 70% 记得避开
            safe=[a for a in ANG if a!=ewin]
            pang=r.choice(safe) if (prof=='perfect' or r.random()<0.7) else r.choice(ANG)
            t=ptiming(prof,r)
            pp=20+pw+t*30+spd*0.3
            eT=1 if r.random()<ai['timingHit'] else r.random()*0.7
            ep=20+epow+ai['powBonus']+eT*30+espd*0.3
            if pwin==eang: pp*=1.3
            if ewin==pang: ep*=1.3
            d=round(abs(pp-ep))
            if pp>=ep: ehp-=d+8
            else: php-=d+8
        wins[0 if php>0 else 1]+=1
    return wins[0]==2
def rate(cfg,si,prof,n=4000,reveal='public',seed=1):
    r=random.Random(seed); st=cfg['stages'][si]
    horns=st['allowedHorns'] or list(D['horns'])
    if prof=='perfect':
        best=0
        for h in horns:
            for w in D['wools']:
                rr=random.Random(seed); best=max(best,sum(match(cfg,st,w,h,prof,reveal,rr) for _ in range(n))/n)
        return best
    return sum(match(cfg,st,'fluffy',r.choice(horns),prof,reveal,r) for _ in range(n))/n
def exch(cfg,si,horn,n=20000,seed=2):
    r=random.Random(seed);st=cfg['stages'][si];ai=st['ai'];pw,pwin=D['horns'][horn]
    epow,ewin=D['horns'][cfg['look']['horn']];espd=D['wools'][cfg['look']['wool']][1];k=0
    for _ in range(n):
        eang=STANCE[r.choice(cfg['stancePref'])];pp=20+pw+30;eT=1 if r.random()<ai['timingHit'] else r.random()*.7
        ep=20+epow+ai['powBonus']+eT*30+espd*.3
        if pwin==eang: pp*=1.3
        k+=pp>=ep
    return k/n
