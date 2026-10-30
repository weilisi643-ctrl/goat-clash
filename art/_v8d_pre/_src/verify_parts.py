import numpy as np, json, os
from PIL import Image
ART='/workspace/goat-game/art'; J=json.load(open(ART+'/parts.json'))
def L(p): return np.asarray(Image.open(f'{ART}/{p}').convert('RGBA')).astype(float)
def tint(a,c,div):
    c=np.array([int(c[i:i+2],16) for i in (1,3,5)],float); o=a.copy(); o[...,:3]=np.clip(a[...,:3]/div*c,0,255); return o
def over(d,s):
    sa=s[...,3:]/255; d[...,:3]=s[...,:3]*sa+d[...,:3]*(1-sa); d[...,3:]=np.maximum(d[...,3:],s[...,3:]); return d
def stack(dirp,pose,wool,horn,wc,hc,sfx):
    seq=[(f'wool/{wool}_{pose}',wc,255)]+([(f'wool/spots_mask_{pose}','#8b5a2b',255)] if wool=='spots' else [])+[(f'wool/knee_{pose}','#a8774a',255),(f'body/body_{pose}',None,0),(f'beard/beard_{pose}',wc,255),(f'face/face_{pose}',None,0),(f'horn/{horn}_{pose}',hc,128)]
    out=[]
    for f,c,dv in seq:
        p=f'{dirp}/{os.path.basename(f)}{sfx}.png' if dirp else f'{f}{sfx}.png'
        if not os.path.exists(f'{ART}/{p}'): continue
        a=L(p); out.append(tint(a,c,dv) if c else a)
    return out
WC=['#ffffff','#333333','#f6d6e6','#7ad0ff']; HC=['#d9b77a','#c0c0c0','#ff7aa8','#8b5a2b']
def run():
  worst=0; n=0; per={}
  for pose,P in J['poses'].items():
    for sfx,shape in [('',(1024,1152)),('_320',(320,360))]:
      for i,w in enumerate(['fluffy','short','spots','cloud']):
        for k,h in enumerate(['curl','straight','spiral','branch']):
          wc,hc=WC[(i+k)%4],HC[(i*3+k)%4]
          ref=np.zeros(shape+(4,))
          for l in stack(None,pose,w,h,wc,hc,sfx): ref=over(ref,l)
          got=np.zeros(shape+(4,))
          for part in J['part_draw_order']:
            for l in stack(f'parts/{pose}/{part}',pose,w,h,wc,hc,sfx): got=over(got,l)
          d=int(np.abs(ref.astype(np.uint8).astype(int)-got.astype(np.uint8).astype(int)).max()); worst=max(worst,d); n+=1
          per[(pose,sfx or 'full')]=max(per.get((pose,sfx or 'full'),0),d)
  print(f'{n} composites checked (3 poses x 16 wool/horn x full+_320, spots incl. spots_mask), max diff = {worst}'); print(per)
if __name__=='__main__': run()
