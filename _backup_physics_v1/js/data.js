// 外观与属性数据：每项都有小幅属性取舍
module.exports = {
  wools: [
    { id:'fluffy', name:'蓬松卷毛', hp:+10, spd:0 },
    { id:'short',  name:'短绒毛',   hp:0,   spd:+10 },
    { id:'spots',  name:'斑点毛',   hp:+5,  spd:+5 },
    { id:'cloud',  name:'云朵毛',   hp:+15, spd:-5 }
  ],
  woolColors: ['#ffffff','#f6d6e6','#cfe8ff','#3a3a3a','#ffe9a8','#c9f2c7'],
  hornColors: ['#d9b77a','#ffd700','#c0c0c0','#ff7aa8','#7ad0ff','#8b5a2b'],
  horns: [
    { id:'curl',   name:'卷角',   pow:0,  win:'low',  tip:'低角度克制' },
    { id:'straight',name:'直角',  pow:+10,win:'high', tip:'高角度克制' },
    { id:'spiral', name:'螺旋角', pow:+5, win:'mid',  tip:'中角度克制' },
    { id:'branch', name:'鹿枝角', pow:+15,win:'none', tip:'力量大但无克制' }
  ]
};
