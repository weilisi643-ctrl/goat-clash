import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); C=json.load(open(sys.argv[3]))
steps=0; maxd=0; exact=0; evok=0; solok=0; bad=[]
for i,(x,y) in enumerate(zip(a,b)):
    ok=True
    solok+= x['solved']==y['solved']
    for s,t in zip(x['res'],y['res']):
        if s['ev']!=t['ev']: ok=False
        if len(s['trace'])!=len(t['trace']): ok=False
        for f,g in zip(s['trace'],t['trace']):
            steps+=1
            for u,v in zip(f,g):
                for k in range(1,5): maxd=max(maxd,abs(u[k]-v[k]))
            exact+= f==g
        if s['state']!=t['state']: ok=False
    evok+=ok
    if not ok: bad.append(i)
print(json.dumps({'cases':len(a),'cases_identical(ev+trace len+final state)':evok,'solved_flag_match':solok,'steps':steps,'steps_bit_exact':exact,'max_abs_diff':maxd,'bad':bad[:10]}))
