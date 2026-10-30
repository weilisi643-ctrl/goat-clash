# 对每关参考解加入时机(力度)/角度扰动，统计过关率与三星率
import json,random,sys,os
sys.path.insert(0,'../design/sim')
from physics import init,shoot,solved
L=json.load(open('../design/data/levels.json'))['levels']
N=400
print('lv name | clear@sdA2/sdP0.03 | 3star | clear@sdA5/sdP0.08 | 3star | note')
for lv in L:
  sol=lv['solution']
  def run(sdA,sdP):
    clear=star3=0
    for i in range(N):
      r=random.Random(i*997+lv['id'])
      st=init(lv)
      for s in sol:
        a=s['angle']+r.gauss(0,sdA); p=max(0.05,min(1.0,s['power']+r.gauss(0,sdP)))
        st,_=shoot(lv,st,a,p,lv['horn'])
      if solved(st) and all(b['alive'] for b in st if b.get('target')):
        clear+=1
        if len(sol)<=lv['stars']['3']: star3+=1
    return clear/N, star3/N
  c1,s1=run(2,0.03); c2,s2=run(5,0.08)
  note=''
  if c1<0.5: note='偏难(小误差也常挂)'
  elif c2<0.2: note='容错窄'
  print(f"{lv['id']:2} {lv['name']:<8} {c1:.2f}/{s1:.2f}          {c2:.2f}/{s2:.2f}   {note}")
