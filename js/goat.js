// 程序化绘制山羊（无外部素材）
function drawGoat(ctx, x, y, s, look, face, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(face * s, s);
  var wc = look.woolColor, hc = look.hornColor;
  // 腿
  ctx.fillStyle = '#5a4636';
  [-22,-8,10,24].forEach(function(lx){ ctx.fillRect(lx, 18, 6, 22); });
  // 身体羊毛
  ctx.fillStyle = wc;
  ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.lineWidth = 2;
  var w = look.wool;
  if (w === 'fluffy' || w === 'cloud') {
    var n = w === 'cloud' ? 9 : 7, r = w === 'cloud' ? 16 : 13;
    for (var i = 0; i < n; i++) { var a = i / n * Math.PI * 2;
      ctx.beginPath(); ctx.arc(Math.cos(a) * 26, Math.sin(a) * 14, r, 0, 7); ctx.fill(); ctx.stroke(); }
  }
  ctx.beginPath(); ctx.ellipse(0, 0, 34, 22, 0, 0, 7); ctx.fill(); ctx.stroke();
  if (w === 'spots') { ctx.fillStyle = 'rgba(0,0,0,0.35)';
    [[-12,-6,6],[8,4,7],[18,-8,4],[-20,8,4]].forEach(function(p){ctx.beginPath();ctx.arc(p[0],p[1],p[2],0,7);ctx.fill();}); }
  if (w === 'short') { ctx.strokeStyle='rgba(0,0,0,0.15)';
    for (var k=-24;k<26;k+=8){ctx.beginPath();ctx.moveTo(k,-12);ctx.lineTo(k+4,12);ctx.stroke();} }
  // 头
  ctx.fillStyle = wc; ctx.strokeStyle='rgba(0,0,0,0.3)';
  ctx.beginPath(); ctx.ellipse(38, -14, 16, 13, 0.3, 0, 7); ctx.fill(); ctx.stroke();
  // 眼睛 腮红 嘴
  ctx.fillStyle = '#222'; ctx.beginPath(); ctx.arc(42, -18, 3.2, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(43, -19, 1.2, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(255,120,150,0.6)'; ctx.beginPath(); ctx.arc(46, -9, 4, 0, 7); ctx.fill();
  ctx.strokeStyle = '#222'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(50, -8, 3, 0.2, 2.6); ctx.stroke();
  // 耳朵
  ctx.fillStyle = wc; ctx.beginPath(); ctx.ellipse(28, -22, 8, 4, -0.6, 0, 7); ctx.fill();
  drawHorn(ctx, look.horn, hc, t || 0);
  ctx.restore();
}
function drawHorn(ctx, shape, c, t) {
  ctx.save(); ctx.translate(40, -26);
  ctx.strokeStyle = c; ctx.fillStyle = c; ctx.lineCap = 'round'; ctx.lineWidth = 6;
  ctx.beginPath();
  if (shape === 'curl') { ctx.arc(8, -4, 9, Math.PI, Math.PI * 2.6); }
  else if (shape === 'straight') { ctx.moveTo(0, 0); ctx.lineTo(22, -14); }
  else if (shape === 'spiral') { for (var i = 0; i < 40; i++) { var a = i * 0.35, r = 2 + i * 0.35;
      var px = 8 + Math.cos(a) * r, py = -6 + Math.sin(a) * r * 0.6 - i * 0.2; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } ctx.lineWidth = 4; }
  else { ctx.moveTo(0,0); ctx.lineTo(10,-18); ctx.moveTo(5,-9); ctx.lineTo(16,-10); ctx.moveTo(10,-18); ctx.lineTo(4,-26); ctx.moveTo(10,-18); ctx.lineTo(18,-24); ctx.lineWidth = 4; }
  ctx.stroke(); ctx.restore();
}
module.exports = { drawGoat: drawGoat };
// 脚下影子：半透明椭圆，画在地面上；lift 为离地高度，越高影子越小越淡
function drawShadow(ctx, x, y, s, lift) {
  var k = Math.max(0.4, 1 - (lift || 0) / 160);
  ctx.save(); ctx.fillStyle = 'rgba(0,0,0,' + (0.22 * k).toFixed(3) + ')';
  ctx.beginPath(); ctx.ellipse(x, y + 41 * s, 40 * s * k, 7 * s * k, 0, 0, 7); ctx.fill(); ctx.restore();
}
module.exports.drawShadow = drawShadow;
