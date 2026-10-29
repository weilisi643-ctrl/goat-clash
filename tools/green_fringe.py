# 绿色渗边检测：半透明/边缘像素中 G 明显高于 R、B 的像素数（羊整图不应有绿色）
import sys,os,glob,json
from PIL import Image
def count(p,edge_only=True):
  im=Image.open(p).convert('RGBA');px=im.load();w,h=im.size;n=0
  for y in range(h):
    for x in range(w):
      r,g,b,a=px[x,y]
      if a>8 and g>r+20 and g>b+20 and (not edge_only or a<250): n+=1
  return n
if __name__=='__main__':
  roots=sys.argv[1:];out={}
  for root in roots:
    fs=sorted(glob.glob(root+'/art/*/*_320.png'));fs=[f for f in fs if '/art/_' not in f and '/parts/' not in f and '/fx/' not in f and '/ui/' not in f]
    out[root]={'files':len(fs),'edge_green':sum(count(f) for f in fs),'any_green':sum(count(f,False) for f in fs)}
  print(json.dumps(out))
