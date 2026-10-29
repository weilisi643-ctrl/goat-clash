# 按 project.config.json packOptions.ignore 实测主包大小
import json,os,re,fnmatch,sys
R=sys.argv[1] if len(sys.argv)>1 else '.'
ig=json.load(open(os.path.join(R,'project.config.json')))['packOptions']['ignore']
def skip(rel):
  for r in ig:
    v=r['value'];t=r['type']
    if t=='folder' and (rel==v or rel.startswith(v.rstrip('/')+'/')): return True
    if t=='file' and rel==v: return True
    if t=='glob' and fnmatch.fnmatch(rel,v) and ('/' in v or '/' not in rel): return True
    if t=='regexp' and re.search(v,rel): return True
  return False
tot=0;n=0;big={}
for dp,dn,fn in os.walk(R):
  dn[:]=[x for x in dn if x not in('.git','node_modules','__pycache__')]
  for f in fn:
    rel=os.path.relpath(os.path.join(dp,f),R).replace(os.sep,'/')
    if skip(rel): continue
    s=os.path.getsize(os.path.join(dp,f));tot+=s;n+=1;top=rel.split('/')[0]+('/'+rel.split('/')[1] if rel.count('/')>1 else '');big[top]=big.get(top,0)+s
print(json.dumps({'files':n,'bytes':tot,'MB':round(tot/1048576,3),'by_dir':dict(sorted(big.items(),key=lambda x:-x[1])[:10])},ensure_ascii=False))
