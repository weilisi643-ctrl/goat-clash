import sys; sys.argv=['x']
exec(open('/workspace/goat-game/art/_src/director_fix_compare.py').read().split("B=ART+'/_v9_pre'")[0])
from PIL import Image, ImageDraw, ImageFont
import numpy as np
FO=ImageFont.truetype(ART+'/ui_v3/font/kuaile_subset.ttf',18)
PRE=ART+'/_v10_pre'; BG=(60,200,60)
def g(root,pose,w,c): 
    a=comp(root,pose,w,c,'_320',up=(1152,1024)); return Image.fromarray(a)
rows=[]
# beard: head crop, before/after x white/black/brown
HC={'idle':(700,380,900,620),'jump':(690,400,890,640),'clash':(640,700,840,940)}
T=[]
for pose in ['idle','jump','clash']:
    for c in ['#ffffff','#333333','#8b5a2b']:
        for r,lab in [(PRE,'前'),(ART,'后')]:
            t=g(r,pose,'fluffy',c).crop(HC[pose]).resize((150,180)); ImageDraw.Draw(t).text((3,3),f'{pose} {c} {lab}',font=FO,fill='red'); T.append(t)
W1=Image.new('RGB',(150*6,180*3),'white')
for i,t in enumerate(T): W1.paste(t,((i%6)*150,(i//6)*180))
CL=[('idle','cloud',689,342),('idle','cloud',439,445),('idle','cloud',119,534),('idle','short',759,273),('jump','cloud',535,745),('jump','cloud',597,460),('clash','cloud',148,593),('clash','fluffy',641,861),('idle','fluffy',742,242)]
T=[]
for pose,w,x,y in CL:
    for r,lab in [(PRE,'前'),(ART,'后')]:
        t=g(r,pose,w,'#ffffff').crop((x-45,y-45,x+45,y+45)).resize((100,100)); ImageDraw.Draw(t).text((2,2),f'{pose[:2]}{w[:2]}{lab}',font=FO,fill='red'); T.append(t)
W2=Image.new('RGB',(100*9,100*2),'white')
for i,t in enumerate(T): W2.paste(t,((i//2)*100,(i%2)*100))
ti=Image.new('RGB',(900,160),(205,250,150))
for i,(n,x) in enumerate([('_v10_pre/ui_v3/assets/title_perfect@2x.png',10),('ui_v3/assets/title_perfect@2x.png',300),('ui_v3/assets/title_win@2x.png',640)]):
    im=Image.open(ART+'/'+n).convert('RGBA'); ti.paste(im,(x,10),im)
ImageDraw.Draw(ti).text((10,140),'完美 前(56) | 完美 后(38+白外描边+星芒) | 胜利(48,不变)',font=FO,fill='black')
H=[ImageDraw.Draw(Image.new('RGB',(1,1)))]
out=Image.new('RGB',(900,30+540+30+200+30+160),'white'); d=ImageDraw.Draw(out)
d.text((5,5),'③ _320 胡子加长（白/黑/棕羊毛，前/后，绿底，游戏放大）',font=FO,fill='black'); out.paste(W1,(0,30))
d.text((5,575),'① 绿边/针孔：上=前 下=后（最后一列 卷角镂空保留）',font=FO,fill='black'); out.paste(W2,(0,600))
d.text((5,805),'② title_perfect',font=FO,fill='black'); out.paste(ti,(0,830))
out.save(ART+'/v10_compare.png')
