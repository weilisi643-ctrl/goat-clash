def L(id,name,start,objs,hays,maxShots,teach,horn='curl',allowed=None):
    return dict(id=id,name=name,start=dict(x=start[0],y=start[1]),objects=objs,hays=hays,maxShots=maxShots,teach=teach,horn=horn,allowedHorns=allowed)
def o(id,t,x,y,**k): d=dict(id=id,type=t,x=x,y=y); d.update(k); return d
def h(id,x,y,r=30,accepts=None): d=dict(id=id,x=x,y=y,r=r); 
LEVELS=[]
def hay(id,x,y,r=30,accepts=None):
    d=dict(id=id,x=x,y=y,r=r)
    if accepts: d['accepts']=accepts
    return d
LEVELS+=[
 L(1,'第一顶',(187,600),[o('t1','crate',187,420,target=True)],[hay('h1',187,250,34)],3,'直线顶撞：瞄准木箱，顶进草堆'),
 L(2,'歪歪草堆',(120,600),[o('t1','crate',180,430,target=True)],[hay('h1',290,190,32)],3,'角度：要从木箱的反方向去顶'),
 L(3,'石头挡路',(187,600),[o('t1','ball',230,480,target=True),o('r1','rock',130,340),o('r2','rock',170,340),o('r3','rock',210,340)],[hay('h1',70,230,36)],3,'借墙反弹：石头推不动，让羊毛球擦墙绕过去'),
 L(4,'接力顶',(60,600),[o('c1','crate',120,500),o('t1','crate',200,380,target=True)],[hay('h1',300,180,32)],3,'连锁反应：顶 A 箱去撞 B 箱'),
 L(5,'脆脆箱',(187,600),[o('f1','fragile',187,470),o('t1','crate',187,330,target=True)],[hay('h1',187,140,32)],4,'易碎箱：用力顶会撞碎，轻顶只会推动'),
 L(6,'别吵醒它',(80,600),[o('s1','sheep',100,420,dashDir=0),o('t1','crate',220,420,target=True),o('r1','rock',180,475),o('r2','rock',222,470),o('r3','rock',264,475)],[hay('h1',330,420,30)],3,'睡羊被撞醒后，会朝它面朝的方向迷糊冲刺'),
 L(7,'两堆草',(187,620),[o('t1','crate',130,460,target=True),o('t2','crate',245,460,target=True)],[hay('h1',70,200,32),hay('h2',305,200,32)],4,'多目标：每个目标进任意草堆都算'),
 L(8,'石林弹球',(320,610),[o('t1','ball',300,470,target=True),o('r1','rock',260,330),o('r2','rock',200,380),o('r3','rock',130,260)],[hay('h1',70,140,32)],4,'多次反弹路线，螺旋角弹性更好'),
 L(9,'起床号',(187,620),[o('f1','fragile',187,500),o('s1','sheep',187,380,dashDir=90),o('t1','crate',187,250,target=True)],[hay('h1',187,110,32)],4,'先撞碎木箱，再叫醒睡羊替你顶'),
 L(10,'牧场大扫除',(187,620),[o('t1','crate',100,450,target=True),o('s1','sheep',250,470,dashDir=135),o('t2','ball',190,330,target=True),o('r1','rock',300,300),o('f1','fragile',100,330)],[hay('h1',90,150,32),hay('h2',290,150,32)],5,'综合：碎箱、睡羊、双目标'),
]
