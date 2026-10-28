import json,random
L=json.load(open('../design/data/levels.json'))['levels']; r=random.Random(42); cases=[]
for lv in L:
    cases.append({'lv':lv['id'],'horn':'curl','shots':[[s['angle'],s['power']] for s in lv['solution']],'kind':'solution'})
    for i in range(40):
        cases.append({'lv':lv['id'],'horn':r.choice(['curl','straight','spiral','branch']),'kind':'random',
          'shots':[[round(r.uniform(0,360),3),round(r.uniform(0.1,1),3)] for _ in range(r.randint(1,4))]})
json.dump(cases,open('/tmp/ddl_cases.json','w')); print(len(cases))
