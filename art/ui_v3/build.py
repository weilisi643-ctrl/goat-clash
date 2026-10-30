# ui_v3: UI 规范切图 + 结算/首页素材（PIL 代码绘制，ZCOOL KuaiLe）。只产出美术文件，不改 js。
import json, os, math, imagequant
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__)); FONT=D+'/../_fonts/ZCOOLKuaiLe-Regular.ttf'
T=json.load(open(D+'/theme_tokens.json')); C=T['colors']; SS=4  # supersample
def f(sz): return ImageFont.truetype(FONT,int(sz))
def rgba(h,a=255): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))+(a,)
def save(im,path):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    imagequant.quantize_pil_image(im,dithering_level=1.0,max_colors=256,min_quality=70,max_quality=95).save(path,optimize=True)
def down(im,k): return im.resize((im.width//k,im.height//k),Image.LANCZOS)
# ---------- buttons / cards (logical px, 375 wide) ----------
def box(w,h,s,fill,stroke=C['stroke'],sw=2,r=11,depth=None,depth_color=None,text=None,tsize=None,tcolor=None,lock=False,sel=False,pressed=False,arrow=False):
    k=s*SS; dp=0 if pressed else (depth if depth is not None else 0)
    pad=2; W=int((w+pad*2)*k); H=int((h+pad*2+(depth or 0))*k)
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    x0=pad*k; y0=(pad+((depth or 0)-dp))*k; R=r*k; SW=sw*k
    if dp: d.rounded_rectangle([x0,y0+dp*k,x0+w*k,y0+h*k+dp*k],R,fill=rgba(depth_color or C['stroke']),outline=rgba(stroke),width=int(SW))
    d.rounded_rectangle([x0,y0,x0+w*k,y0+h*k],R,fill=rgba(fill),outline=rgba(stroke),width=int(SW))
    if sel: d.rounded_rectangle([x0+SW*1.8,y0+SW*1.8,x0+w*k-SW*1.8,y0+h*k-SW*1.8],max(R-SW*1.8,1),outline=rgba(C['accentYellow']),width=int(SW*1.2))
    if text:
        cy=y0+h*k/2; cx=x0+w*k/2
        if lock: text='🔒'+text if False else text
        d.text((cx,cy),text,font=f(tsize*k),fill=rgba(tcolor),anchor='mm')
    if arrow:
        cx=x0+w*k/2; cy=y0+h*k/2; a=6*k
        d.polygon([(cx-a*0.7,cy-a),(cx-a*0.7,cy+a),(cx+a,cy)],fill=rgba(C['stroke']))
    if lock:  # small padlock glyph top-right
        lx=x0+w*k-14*k; ly=y0+6*k
        d.arc([lx,ly,lx+8*k,ly+9*k],180,360,fill=rgba(C['stroke']),width=int(1.6*k))
        d.rounded_rectangle([lx-1.5*k,ly+4.5*k,lx+9.5*k,ly+12.5*k],1.5*k,fill=rgba(C['stroke']))
    return down(im,SS)
B=T['button']; FS=T['fontSize']
BTN={
 'btn_primary':      dict(w=200,h=40,fill=C['cardWhite'],depth=B['primaryDepth'],depth_color=C['primaryGreen'],text='开始对战',tsize=FS['button'],tcolor=C['text']),
 'btn_primary_pressed':dict(w=200,h=40,fill='#F2F2EC',depth=B['primaryDepth'],depth_color=C['primaryGreen'],text='开始对战',tsize=FS['button'],tcolor=C['text'],pressed=True),
 'btn_secondary':    dict(w=110,h=32,fill=C['accentBlue'],depth=B['smallDepth'],text='回主页',tsize=FS['buttonSmall'],tcolor=C['textOnColor']),
 'btn_secondary_pressed':dict(w=110,h=32,fill='#2A63C2',depth=B['smallDepth'],text='回主页',tsize=FS['buttonSmall'],tcolor=C['textOnColor'],pressed=True),
 'btn_selected':     dict(w=72,h=36,fill=C['accentYellow'],depth=B['smallDepth'],text='中',tsize=FS['button'],tcolor=C['text'],sel=False),
 'btn_unselected':   dict(w=72,h=36,fill=C['cardWhite'],depth=B['smallDepth'],text='中',tsize=FS['button'],tcolor=C['text']),
 'btn_disabled':     dict(w=200,h=40,fill=C['disabledFill'],stroke=C['disabledStroke'],depth=B['primaryDepth'],depth_color=C['disabledStroke'],text='开始对战',tsize=FS['button'],tcolor=C['disabledText']),
 'btn_locked':       dict(w=200,h=40,fill=C['lockedGray'],depth=B['primaryDepth'],depth_color=C['stroke'],text='第3关解锁',tsize=FS['button'],tcolor=C['textSub'],lock=True),
 'btn_arrow':        dict(w=34,h=34,fill=C['accentYellow'],depth=B['smallDepth'],text=None,tsize=16,tcolor=C['text'],arrow=True),
 'card_level_open':  dict(w=96,h=110,r=14,fill=C['cardWhite'],depth=4,text='1',tsize=FS['score'],tcolor=C['text']),
 'card_level_current':dict(w=96,h=110,r=14,fill=C['accentYellow'],depth=4,text='2',tsize=FS['score'],tcolor=C['text'],sel=True),
 'card_level_locked':dict(w=96,h=110,r=14,fill=C['lockedGray'],depth=4,text='3',tsize=FS['score'],tcolor=C['textSub'],lock=True),
}
def pill(s,text='对手架势：高角度'):
    k=s*SS; fo=f(FS['aux']*k); tw=fo.getlength(text); h=22*k; w=tw+28*k
    im=Image.new('RGBA',(int(w+4*k),int(h+4*k))); d=ImageDraw.Draw(im)
    d.rounded_rectangle([2*k,2*k,2*k+w,2*k+h],h/2,fill=rgba(C['cardWhite']),outline=rgba(C['stroke']),width=int(2*k))
    d.text((2*k+w/2,2*k+h/2),text,font=fo,fill=rgba(C['text']),anchor='mm'); return down(im,SS)
def pill_dark(s,text='第1回合 · 三局两胜'):
    k=s*SS; fo=f(FS['aux']*k); tw=fo.getlength(text); h=22*k; w=tw+28*k
    im=Image.new('RGBA',(int(w+4*k),int(h+4*k))); d=ImageDraw.Draw(im)
    d.rounded_rectangle([2*k,2*k,2*k+w,2*k+h],h/2,fill=rgba(C['stroke']))
    d.text((2*k+w/2,2*k+h/2),text,font=fo,fill=rgba(C['textOnColor']),anchor='mm'); return down(im,SS)
# ---------- task B assets ----------
def title(text,s,size,fill,stroke_px,shadow_px,rot=-3,outer_px=0,sparkle=False):
    k=s*SS; fo=f(size*k); sw=int(stroke_px*k); sh=int(shadow_px*k); ow=int(outer_px*k); sp=14*k if sparkle else 0
    bb=fo.getbbox(text,stroke_width=sw); W=bb[2]-bb[0]+sh+sw*2+2*ow+20*k+2*sp; H=bb[3]-bb[1]+sh+sw*2+2*ow+20*k+sp
    im=Image.new('RGBA',(int(W),int(H))); d=ImageDraw.Draw(im); ox=10*k+sw+ow+sp-bb[0]; oy=10*k+sw+ow+sp-bb[1]
    if ow:  # v10: white outer stroke outside the black stroke (shadow included)
        for dx,dy in [(0,0),(sh*0.7,sh)]: d.text((ox+dx,oy+dy),text,font=fo,fill=rgba(C['cardWhite']),stroke_width=sw+ow,stroke_fill=rgba(C['cardWhite']))
    if sparkle:  # v10: two small 4-point sparkles, white with ink edge
        tw=bb[2]-bb[0]
        for cx,cy,R in [(ox+bb[0]+tw+sw+ow+sp*0.55,oy+bb[1]-sw*0.2,9*k),(ox+bb[0]-sw-ow-sp*0.45,oy+bb[1]+(bb[3]-bb[1])*0.75,6*k)]:
            r=R*0.3; pts=[(cx,cy-R),(cx+r,cy-r),(cx+R,cy),(cx+r,cy+r),(cx,cy+R),(cx-r,cy+r),(cx-R,cy),(cx-r,cy-r)]
            d.polygon(pts,fill=rgba(C['cardWhite']),outline=rgba(C['stroke']),width=int(2*k))
    d.text((ox+sh*0.7,oy+sh),text,font=fo,fill=rgba(C['stroke']),stroke_width=sw,stroke_fill=rgba(C['stroke']))
    d.text((ox,oy),text,font=fo,fill=rgba(fill),stroke_width=sw,stroke_fill=rgba(C['stroke']))
    im=im.rotate(rot,resample=Image.BICUBIC,expand=True); im=im.crop(im.getbbox()); return down(im,SS)
def star(s,R=14,fill=None):
    k=s*SS; R*=k; pad=4*k; W=int(2*R+2*pad); im=Image.new('RGBA',(W,W)); d=ImageDraw.Draw(im); c=W/2
    pts=[(c+(R if i%2==0 else R*0.48)*math.sin(i*math.pi/5),c-(R if i%2==0 else R*0.48)*math.cos(i*math.pi/5)) for i in range(10)]
    d.polygon(pts,fill=rgba(fill or C['accentYellow'])); d.line(pts+[pts[0]],fill=rgba(C['stroke']),width=int(2*k),joint='curve'); return down(im,SS)
def dash(s,L=14,wid=3.5):
    k=s*SS; W=int((L+6)*k); H=int((wid+6)*k); im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([3*k,3*k,W-3*k,H-3*k],wid*k/2,fill=rgba(C['stroke'])); return down(im,SS)
def burst(s):  # 3 short radiating lines group (top-right of title), clean
    k=s*SS; W=int(40*k); im=Image.new('RGBA',(W,W)); d=ImageDraw.Draw(im)
    for ang,L in [(-60,12),(-20,14),(20,12)]:
        a=math.radians(ang); r0=8*k; r1=r0+L*k; cx,cy=6*k,24*k
        d.line([cx+r0*math.cos(a)*1.0+r0*0,cy+r0*math.sin(a),cx+r1*math.cos(a),cy+r1*math.sin(a)],fill=rgba(C['stroke']),width=int(3.5*k))
    for ang,L in [(-60,12),(-20,14),(20,12)]:
        a=math.radians(ang); r1=(8+L)*k; cx,cy=6*k,24*k; e=1.75*k
        for r in (8*k,r1): d.ellipse([cx+r*math.cos(a)-e,cy+r*math.sin(a)-e,cx+r*math.cos(a)+e,cy+r*math.sin(a)+e],fill=rgba(C['stroke']))
    im=im.crop(im.getbbox()); return down(im,SS)
def pedestal(s,w=150,h=34):
    k=s*SS; dep=8; W=int((w+8)*k); H=int((h+dep+8)*k); im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im); x0=4*k; y0=4*k
    d.ellipse([x0,y0+dep*k,x0+w*k,y0+(h+dep)*k],fill=rgba(C['pedestalSide']),outline=rgba(C['stroke']),width=int(2*k))
    d.rectangle([x0+1*k,y0+h/2*k,x0+w*k-1*k,y0+(h/2+dep)*k],fill=rgba(C['pedestalSide']))
    d.line([x0+1*k,y0+h/2*k,x0+1*k,y0+(h/2+dep)*k],fill=rgba(C['stroke']),width=int(2*k)); d.line([x0+w*k-1*k,y0+h/2*k,x0+w*k-1*k,y0+(h/2+dep)*k],fill=rgba(C['stroke']),width=int(2*k))
    d.ellipse([x0,y0,x0+w*k,y0+h*k],fill=rgba(C['pedestalTop']),outline=rgba(C['stroke']),width=int(2*k))
    d.ellipse([x0+w*0.18*k,y0+h*0.2*k,x0+w*0.82*k,y0+h*0.7*k],fill=rgba('#F3FFE4')); return down(im,SS)
def contact_shadow(s,w=110,h=18):
    k=s*SS; W=int((w+24)*k); H=int((h+24)*k); m=Image.new('L',(W,H)); d=ImageDraw.Draw(m)
    d.ellipse([12*k,12*k,W-12*k,H-12*k],fill=150); d.ellipse([W*0.3,H*0.38,W*0.7,H*0.62],fill=200)
    m=m.filter(ImageFilter.GaussianBlur(5*k)); im=Image.new('RGBA',(W,H),rgba(C['shadowInk'])); im.putalpha(m); return down(im,SS)
A=dict(
 title_perfect=lambda s: title('完美！',s,FS['titlePerfect'],C['accentYellow'],T['titlePerfectStroke'],T['titlePerfectShadow'],-4,T['titlePerfectOuter'],True),
 title_win=lambda s: title('胜利！',s,FS['title'],C['accentYellow'],T['titleStroke'],T['titleShadow'],-3),
 title_lose=lambda s: title('失败',s,FS['title'],C['lockedGray'],T['titleStroke'],T['titleShadow'],0),
 deco_star=lambda s: star(s,12), deco_star_small=lambda s: star(s,7), deco_dash=lambda s: dash(s), deco_burst=burst,
 pedestal=pedestal, contact_shadow=contact_shadow)
if __name__=='__main__':
    out={'slices':{},'assets':{}}
    for name,kw in BTN.items():
        for s in (2,3):
            im=box(s=s,**kw); p=f'{D}/slices/{name}@{s}x.png'; save(im,p); out['slices'].setdefault(name,{})[f'@{s}x']=im.size
    for name,fn in [('pill_hint',pill),('pill_round',pill_dark)]:
        for s in (2,3): im=fn(s); save(im,f'{D}/slices/{name}@{s}x.png'); out['slices'].setdefault(name,{})[f'@{s}x']=im.size
    for name,fn in A.items():
        for s in (2,3): im=fn(s); save(im,f'{D}/assets/{name}@{s}x.png'); out['assets'].setdefault(name,{})[f'@{s}x']=im.size
    json.dump(out,open(D+'/_sizes.json','w'),indent=1); print(json.dumps(out))
