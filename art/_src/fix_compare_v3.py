import sys; sys.path.insert(0,'/workspace/goat-game/art/_src'); from goatlib import *
from PIL import ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
v2=Image.open(ART+'/parts_joint_test_v2.png'); v3=Image.open(ART+'/parts_joint_test_v3.png')
def pc(im,i,box,z=1.6):  # panel i (4 cols x 3 rows, 768x683), box in panel coords
    x0,y0=(i%4)*768,(i//4)*683; c=im.crop((x0+box[0],y0+box[1],x0+box[2],y0+box[3])); return c.resize((int(c.width*z),int(c.height*z)),Image.LANCZOS)
rows=[]
# 1 neck/chest (head ±15, tail ±15): v2 no patch vs v3 with patch
NB={0:(380,90,620,380),1:(380,90,620,380),2:(380,90,620,380),3:(380,90,620,380),4:(300,40,560,330),9:(450,390,740,683)}
for i,t in [(1,'idle 白 头-15°'),(3,'idle 黑 头-15°'),(4,'jump 白 头+15°'),(9,'clash 白 头-15°')]:
    rows.append(('脖子/胸前 '+t,pc(v2,i,NB.get(i,NB[1])),pc(v3,i,NB.get(i,NB[1]))))
# 2 front legs ±12
LB={0:(330,380,560,660),2:(330,380,560,660),5:(330,300,620,560),8:(300,400,560,680)}
for i,t in [(0,'idle 白 前腿±12°'),(2,'idle 黑 前腿±12°'),(8,'clash 白 前腿±12°')]:
    rows.append(('前腿重叠 '+t,pc(v2,i,LB[i]),pc(v3,i,LB[i])))
# 3 chin static
for pose,w,wc,b in [('idle','fluffy','#ffffff',(700,300,960,560)),('idle','short','#333333',(700,300,960,560)),('jump','fluffy','#333333',(680,330,940,590)),('clash','cloud','#333333',(700,700,960,960))]:
    bf=Image.fromarray(onbg(goat(ART+'/_v8c_pre',pose,w,'curl',wc,'#d9b77a',False))[b[1]:b[3],b[0]:b[2]]).resize((416,416))
    af=Image.fromarray(onbg(goat(ART,pose,w,'curl',wc,'#d9b77a'))[b[1]:b[3],b[0]:b[2]]).resize((416,416))
    rows.append((f'下巴/边缘 {pose} {w} {wc}',bf,af))
W=max(r[1].width for r in rows)*2+20; H=sum(max(r[1].height,r[2].height)+30 for r in rows)+40
o=Image.new('RGB',(W,H),(238,240,232)); d=ImageDraw.Draw(o); d.text((10,8),'fix_compare_v3：每行 左=修改前（v8c）  右=修改后（v8b：关节补片 / 前腿渐隐重叠 / 下巴圆角+去绿边）',fill=(0,0,0),font=F); y=40
for t,a,b in rows:
    d.text((10,y),t,fill=(0,0,0),font=F); o.paste(a,(0,y+26)); o.paste(b,(W//2+10,y+26)); y+=max(a.height,b.height)+30
o.save(ART+'/fix_compare_v3.png',optimize=True)
