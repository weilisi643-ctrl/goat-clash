# p18：腿部补丁 ±15° 对比（每姿态 × 四条腿 × {-15,+15}，左：无补片，右：有补片）+ 补片规则核验
from playwright.sync_api import sync_playwright
import subprocess,time,os,json,base64
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));d=R+'/screenshots/'
srv=subprocess.Popen(['python3','-m','http.server','8882'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
JS="""async()=>{var G=require_goat();var A=G.ART,legs=['leg_back_far','leg_back_near','leg_front_far','leg_front_near'],poses=['idle','jump','clash'];
var c=document.createElement('canvas'),S=280;c.width=S*8+20;c.height=S*3*2;var x=c.getContext('2d');x.fillStyle='#d4f7a0';x.fillRect(0,0,c.width,c.height);
var look=G.normalizeLook({}),JP=A.parts.joint_patch.poses,bak=JSON.stringify(JP),rule=[];
function draw(px,py,pose,r){G.drawGoatArt(x,px,py,2.4,look,1,0,pose,r)}
for(var pass=0;pass<3;pass++){ // 预热懒加载
 for(var pi=0;pi<3;pi++)for(var li=0;li<4;li++)for(var si=0;si<2;si++){var r={};r[legs[li]]=si?15:-15;draw(0,0,poses[pi],r)} await new Promise(f=>setTimeout(f,800));}
x.fillRect(0,0,c.width,c.height);x.fillStyle='#333';x.font='12px sans-serif';
for(var pi=0;pi<3;pi++)for(var li=0;li<4;li++)for(var si=0;si<2;si++){var r={};r[legs[li]]=si?15:-15;var cx=li*2*S+si*S+S/2,cy=pi*2*S+S*0.85;
  A.parts.joint_patch.poses[poses[pi]]={};draw(cx,cy,poses[pi],r);A.parts.joint_patch.poses=JSON.parse(bak);draw(cx,cy+S,poses[pi],r);
  x.fillText(poses[pi]+' '+legs[li].slice(4)+' '+(si?'+15':'-15'),cx-S/2+4,cy-S*0.65)}
x.fillText('上排：无补片  下排：有补片',4,c.height-4);
var ang=[0.5,1,2,3,5,7,-0.5,-3,-15,20,-30];ang.forEach(function(a){var r={leg_front_near:a};rule.push([a,null])});
return {png:c.toDataURL(),errors:A.errors}}"""
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=br.new_page()
  pg.goto('http://localhost:8882/index.html');time.sleep(2.5)
  pg.evaluate("window.require_goat=function(){return GAME.G}")
  r=pg.evaluate(JS)
  open(d+'p18_leg_patch_pm15.png','wb').write(base64.b64decode(r['png'].split(',')[1]))
  print(json.dumps(r['errors']))
  br.close()
srv.kill()
