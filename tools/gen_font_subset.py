# 站酷快乐体（ZCOOL KuaiLe，SIL OFL 1.1）按用到的字符裁切子集 → art/ui/font/kuaile.ttf（运行时 wx.loadFont / FontFace 加载）
# 字符来源：js/*.js 全部字符串字面量 + 运行时数据 JSON（关卡/擂主/线索/牧场名）+ ASCII 可打印字符
import os,re,glob,json,subprocess,sys
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
SRC=os.environ.get('KUAILE_TTF','/workspace/goat-game/art/_fonts/ZCOOLKuaiLe-Regular.ttf')
cs=set(chr(i) for i in range(32,127))
for f in glob.glob(R+'/js/*.js'): cs|=set(open(f,encoding='utf-8').read())
for f in ['champions.v2.json','clues.json','factions.json','levels.v2.json']: cs|=set(open(R+'/design/data/'+f,encoding='utf-8').read())
cs|=set('０１２３４５６７８９：·—…“”‘’《》【】')
cs={c for c in cs if ord(c)>=32}
txt=''.join(sorted(cs));open('/tmp/kuaile_chars.txt','w',encoding='utf-8').write(txt)
out=R+'/art/ui/font/kuaile.ttf'
subprocess.check_call([sys.executable,'-m','fontTools.subset',SRC,'--text-file=/tmp/kuaile_chars.txt','--output-file='+out,'--layout-features=*','--no-hinting','--desubroutinize'])
from fontTools.ttLib import TTFont
cm=TTFont(out).getBestCmap();miss=[c for c in txt if ord(c) not in cm and ord(c)>127]
print(len(txt),'chars',os.path.getsize(out),'bytes; 字体缺字(运行时回退系统字体，多为 emoji/符号):',''.join(miss))
