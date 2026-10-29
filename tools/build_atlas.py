# 生成首屏整图图集（只渲染/加载层）：公共层 + 默认毛型/角型的 _320 帧 → art/atlas/goat_core.png + .json
# 用法：python3 tools/build_atlas.py   （改 manifest/默认外观后重跑；图集缺的帧运行时回退单图）
import json,os
from PIL import Image
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));A=R+'/art/'
m=json.load(open(A+'manifest.json'));DEF={'wool':'fluffy','horn':'curl'}
keys=[]
for pose in m['poses']:
  for t in m['draw_order']:
    k=t.replace('{wool}',DEF['wool']).replace('{horn}',DEF['horn']).replace('{pose}',pose)
    if os.path.exists(A+k+'_320.png') and k not in keys: keys.append(k)
ims=[Image.open(A+k+'_320.png').convert('RGBA') for k in keys]
cols=6;cw=max(i.width for i in ims);ch=max(i.height for i in ims);rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGBA',(cols*cw,rows*ch),(0,0,0,0));frames={}
for n,(k,im) in enumerate(zip(keys,ims)):
  x,y=(n%cols)*cw,(n//cols)*ch;sheet.paste(im,(x,y));frames[k]=[x,y,im.width,im.height]
sheet.save(A+'atlas/goat_core.png',optimize=True)
json.dump({'image':'art/atlas/goat_core.png','frames':frames},open(A+'atlas/goat_core.json','w'),ensure_ascii=False)
print(len(keys),'frames',sheet.size,os.path.getsize(A+'atlas/goat_core.png'),'bytes; singles',sum(os.path.getsize(A+k+'_320.png') for k in keys))
