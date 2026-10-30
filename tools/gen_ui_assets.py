# 离线生成 UI 资源：位图字体图集（Noto Sans CJK SC Bold，SIL OFL 1.1，只含用到的字符）+ 九宫格按钮/面板（灰度，运行时乘色）
import re,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+'/'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
src=open(R+'js/main.js').read()
chars=set('0123456789:/+-.%·×!！？?()（）「」、，,·★☆°')
for m in re.finditer(r"btn\([^;]*?'([^']*)'",src): chars|=set(m.group(1))
for m in re.finditer(r"text\('([^']*)'[^;]*?,\s*(\d+)\s*[,)]",src):
  if int(m.group(2))>=18: chars|=set(m.group(1))
for m in re.finditer(r"'([^']*)'",src): # 动态拼接标题中的字面量（含 ' 回合 ' 等）
  if any(k in m.group(1) for k in ['回合','场','顶角王','再接再厉','擂主','牧场','过关','顶顶乐','打造']): chars|=set(m.group(1))
chars|=set(''.join(l['name'] for l in json.load(open(R+'design/data/levels.v2.json'))['levels']))
chars|=set(''.join(f['name'] for f in json.load(open(R+'design/data/factions.json'))['factions']))
chars=sorted(c for c in chars if c.strip() and ord(c)<0x2600 or '\u4e00'<=c<='\u9fff' or c in '★☆（）！？，、「」°·')
chars=sorted(set(c for c in chars if c.strip()))
STY={'title':dict(px=44,fill=[(255,214,90),(232,110,20)],stroke=(110,45,0),sw=5),
     'title_mask':dict(px=44,fill=[(255,255,255),(215,215,215)],stroke=(70,70,70),sw=5),
     'btn':dict(px=34,fill=[(74,44,0),(74,44,0)],stroke=(255,250,235),sw=2)}
out={'font':'Noto Sans CJK SC Bold','license':'SIL Open Font License 1.1 (art/ui/OFL.txt)','styles':{}}
for name,s in STY.items():
  f=ImageFont.truetype(FONT,s['px'],index=2); pad=s['sw']+2; ch=s['px']+pad*2; cols=24
  ws={c:int(f.getlength(c))+pad*2 for c in chars}; cw=max(ws.values())
  rows=(len(chars)+cols-1)//cols; img=Image.new('RGBA',(cols*cw,rows*ch),(0,0,0,0)); g={}
  grad=Image.new('RGBA',(1,ch)); 
  for y in range(ch):
    k=y/(ch-1); grad.putpixel((0,y),tuple(int(a+(b-a)*k) for a,b in zip(s['fill'][0],s['fill'][1]))+(255,))
  grad=grad.resize((cw,ch))
  for i,c in enumerate(chars):
    x0,y0=(i%cols)*cw,(i//cols)*ch
    m=Image.new('L',(cw,ch),0); d=ImageDraw.Draw(m); d.text((pad,pad-int(s['px']*0.1)),c,font=f,fill=255)
    ms=Image.new('L',(cw,ch),0); d2=ImageDraw.Draw(ms); d2.text((pad,pad-int(s['px']*0.1)),c,font=f,fill=255,stroke_width=s['sw'],stroke_fill=255)
    cell=Image.new('RGBA',(cw,ch),s['stroke']+(0,)); cell.putalpha(ms)
    fill=grad.copy(); fill.putalpha(m); cell=Image.alpha_composite(cell,fill)
    img.paste(cell,(x0,y0)); g[c]=[x0,y0,ws[c]]
  fn='font_%s.png'%name; img.quantize(colors=128,method=Image.FASTOCTREE).save(R+'art/ui/'+fn,optimize=True)
  ref=Image.new('L',(cw,ch),0); ImageDraw.Draw(ref).text((pad,pad-int(s['px']*0.1)),'中',font=f,fill=255); bb=ref.getbbox()
  out['styles'][name]={'file':'ui/'+fn,'px':s['px'],'h':ch,'pad':pad,'cy':round((bb[1]+bb[3])/2,1),'glyphs':g}
json.dump(out,open(R+'art/ui/font.json','w'),ensure_ascii=False,separators=(',',':'))
# 九宫格（灰度：运行时 multiply 成按钮色），64x64，边 22
def nine(fn,r,top,bot,edge,hl):
  S=4; Wd=64*S; im=Image.new('RGBA',(Wd,Wd),(0,0,0,0)); d=ImageDraw.Draw(im)
  d.rounded_rectangle([0,6*S,Wd-1,Wd-1],r*S,fill=(edge,edge,edge,255)) # 底边厚度
  for y in range(Wd-6*S):
    k=y/(Wd-6*S); v=int(top+(bot-top)*k)
    d.line([(0,y),(Wd,y)],fill=(v,v,v,255))
  m=Image.new('L',(Wd,Wd),0); ImageDraw.Draw(m).rounded_rectangle([0,0,Wd-1,Wd-1-6*S],r*S,fill=255)
  body=im.copy(); body.putalpha(m)
  base=Image.new('RGBA',(Wd,Wd),(0,0,0,0)); ImageDraw.Draw(base).rounded_rectangle([0,2*S,Wd-1,Wd-1],r*S,fill=(edge,edge,edge,255))
  im=Image.alpha_composite(base,body)
  if hl: ImageDraw.Draw(im).rounded_rectangle([3*S,3*S,Wd-1-3*S,Wd*0.42],(r-3)*S,outline=None,fill=(255,255,255,70))
  im.resize((64,64),Image.LANCZOS).save(R+'art/ui/'+fn,optimize=True)
nine('btn9.png',16,255,250,222,True)
nine('panel9.png',14,255,238,200,False)
print(len(chars),'glyphs')
