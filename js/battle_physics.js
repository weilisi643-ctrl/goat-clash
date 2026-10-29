// 对撞物理 v2（2026-10-29）：只做物理，不做渲染。goat.js 的绘制逻辑不变，精灵仍按 (x,y) 物理位置对齐。
// 羊角判定点取自 art/manifest.json v7 的 horn_root（1152×1024 画布；_320 资源 360×320 等比缩放，偏移结果相同）：
//   offset = (horn_root - anchor) × ART_SCALE(0.1) × s，y 再加 40·s（anchor 为脚底，物理 y 为身体中心，脚底 = y + 40·s）
// v1 原版：起跳 vy=-9、每帧 +0.45；p.x ≥ W/2-50 即判定对撞；伤害 round(|pp-ep|)+8；击退固定每帧 3px×20 帧。
var DT = 1 / 60, ART_SCALE = 0.1, S = 1.1;
var ANCHOR = [511, 995];
var HORN_ROOT = { idle: [806, 277], jump: [782, 326], clash: [860, 687] }; // manifest v7（tools/battle_check.js 会核对 manifest）
function hornOffset(pose, s) {
  s = s || S; var r = HORN_ROOT[pose] || HORN_ROOT.idle;
  return [(r[0] - ANCHOR[0]) * ART_SCALE * s, (r[1] - ANCHOR[1]) * ART_SCALE * s + 40 * s];
}
var JUMP = { apexMin: 70, apexMax: 100, tApex: 0.32, vx: 240 }; // 时间制抛物线：完美时机跳得更高
var HIT = { hornR: 10, headH: 40, heightAdv: 0.03, glanceMin: 0.85 };
var KB = { base: 150, perPow: 6, recoil: 90, fric: 900, returnV: 150, minX: 0.1, maxX: 0.9 };
function startJump(g, timing) {
  var h = JUMP.apexMin + (JUMP.apexMax - JUMP.apexMin) * Math.max(0, Math.min(1, timing));
  g.apex = h; g.g = 2 * h / (JUMP.tApex * JUMP.tApex); g.v0 = 2 * h / JUMP.tApex; g.ta = 0; g.y = 0; g.vy = -g.v0 * DT; g.air = true;
}
function stepAir(g, dir) { // 解析抛物线 y(t) = -v0 t + g t²/2，无离散误差；落地后 y=0
  g.ta += DT; var y = -g.v0 * g.ta + 0.5 * g.g * g.ta * g.ta;
  if (y >= 0 && g.ta > 0) { y = 0; g.air = false; }
  g.vy = y - g.y; g.y = y; g.x += dir * JUMP.vx * DT;
}
function hornPoint(g, face, pose) { var o = hornOffset(pose); return [g.x + face * o[0], g.y + o[1]]; }
function contact(p, e) { // 返回 null 或 {dx,dy,pen,align}
  var hp = hornPoint(p, 1, 'jump'), he = hornPoint(e, -1, 'jump');
  var dx = he[0] - hp[0], dy = he[1] - hp[1];
  if (dx > 2 * HIT.hornR || Math.abs(dy) > HIT.headH) return null;
  return { dx: dx, dy: dy, pen: 2 * HIT.hornR - dx, align: 1 - Math.abs(dy) / HIT.headH };
}
function resolvePenetration(p, e, c) { if (c.pen > 0) { p.x -= c.pen / 2; e.x += c.pen / 2; c.pen = 0; } }
function heightMul(myY, otherY) { // 居高临下：更高（y 更小）的一方最多 +3%（8% 时自由对战胜率偏离 v1 过多，已回调）
  var k = Math.max(-1, Math.min(1, (otherY - myY) / 30)); return 1 + HIT.heightAdv * k;
}
function damage(pp, ep, align) { var q = HIT.glanceMin + (1 - HIT.glanceMin) * align; return Math.round(8 + Math.abs(pp - ep) * q); }
function knockback(p, e, pp, ep) { // 冲量式：输家被推开 base+perPow·差值，赢家小幅反冲（px/s）
  var d = Math.abs(pp - ep), lose = KB.base + KB.perPow * d;
  if (pp >= ep) { p.kv = -KB.recoil; e.kv = lose; } else { p.kv = -lose; e.kv = KB.recoil; }
  p.kv = Math.max(p.kv, -600); e.kv = Math.min(e.kv, 600);
}
function stepRecover(g, home, W) { // 击退减速 → 落地 → 走回原位
  if (g.air) stepAir(g, 0);
  if (g.kv) { var s = Math.sign(g.kv), v = Math.max(0, Math.abs(g.kv) - KB.fric * DT); g.kv = s * v; g.x += g.kv * DT; }
  else { var d = home - g.x, st = KB.returnV * DT; g.x += Math.abs(d) <= st ? d : Math.sign(d) * st; }
  g.x = Math.max(W * KB.minX, Math.min(W * KB.maxX, g.x));
}
module.exports = { DT: DT, ANCHOR: ANCHOR, HORN_ROOT: HORN_ROOT, hornOffset: hornOffset, JUMP: JUMP, HIT: HIT, KB: KB,
  startJump: startJump, stepAir: stepAir, hornPoint: hornPoint, contact: contact, resolvePenetration: resolvePenetration,
  heightMul: heightMul, damage: damage, knockback: knockback, stepRecover: stepRecover };
