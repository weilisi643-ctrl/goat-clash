import json
from physics import *; import levels_src; from check import run
from physics import TYPES,HORNS,MAXV,G,FIELD
out=[]
for lv in levels_src.LEVELS:
    r,evs=run(lv)
    assert r, lv['id']
    n=len(r); lv=dict(lv); lv['maxShots']=max(lv['maxShots'],n+2)
    lv['stars']={'3':n,'2':n+1,'1':lv['maxShots']}
    lv['solution']=[{'angle':a,'power':p,'events':e} for (a,p),e in zip(r,evs)]
    lv['verified']=True
    # 复验
    st=init(lv)
    for a,p in r: st,_=shoot(lv,st,a,p,lv['horn'])
    assert solved(st)
    out.append(lv)
doc={'version':1,'screen':{'w':375,'h':667},'field':{'x0':FIELD[0],'y0':FIELD[1],'x1':FIELD[2],'y1':FIELD[3]},
 'physics':{'dt':1/60,'frictionG':G,'maxSpeed':MAXV,'wallRestitution':0.5,'angleUnit':'deg, 0=右 90=上(屏幕向上)','power':'0~1，速度=maxSpeed*power*speedMul','collider':'全部按圆形'},
 'objectTypes':TYPES,'hornMods':HORNS,
 'ads':{'retryAd':'激励视频：本关+1次顶撞，每关限1次','hintAd':'激励视频：显示参考解第1步瞄准线'},
 'levels':out}
json.dump(doc,open('../data/levels.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('written')
