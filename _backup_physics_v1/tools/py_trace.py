# 用原版 design/sim/physics.py 跑用例并逐步记录（运行时插桩副本，不改原文件）
import json,sys,types
src=open('../design/sim/physics.py').read()
src=src.replace("        if not moving and step>5","        TRACE.append([[b['id'],b['x'],b['y'],b['vx'],b['vy']] for b in B])\n        if not moving and step>5")
m=types.ModuleType('phys'); m.TRACE=[]; exec(src,m.__dict__)
L={l['id']:l for l in json.load(open('../design/data/levels.json'))['levels']}
out=[]
for c in json.load(open(sys.argv[1])):
    lv=L[c['lv']]; st=m.init(lv); res=[]
    for a,p in c['shots']:
        m.TRACE.clear(); st,ev=m.shoot(lv,st,a,p,c['horn'])
        res.append({'trace':list(m.TRACE),'ev':[list(e) for e in ev],'state':[[b['id'],b['x'],b['y'],b['alive'],b['inHay']] for b in st]})
    out.append({'res':res,'solved':m.solved(st)})
json.dump(out,open(sys.argv[2],'w'))
