// 顶顶乐物理：design/sim/physics.py 的逐行 JS 移植（确定性，固定步长 1/60s，无随机数）
// physics v2（2026-10-29）：① 自适应子步：单帧位移 > 物体半径时自动细分（上限 SUB=4，防高速穿透；正常速度下仍 1 步，保持参考解手感）② 修复 v1 的 ns 跨物体沿用（绵羊冲刺只看自身速度）
// ③ 墙反弹改为 WALL_E=0.5×(1+物体e)/1.6 的材质相关值 ④ 位置修正加 SLOP 容差并分 2 次迭代，减少抖动/卡死。v1 原版见 _backup_physics_v1/js/ddl_physics.js
var DT = 1 / 60, G = 600.0;
var TYPES = {
  goat: { m: 1.0, f: 0.9, e: 0.6, r: 18 },
  crate: { m: 1.2, f: 1.1, e: 0.4, r: 16 },
  fragile: { m: 0.8, f: 1.1, e: 0.3, r: 15, breakV: 260 },
  ball: { m: 0.6, f: 0.5, e: 0.8, r: 12 },
  rock: { m: 1e9, f: 0, e: 0.5, r: 20, static: true },
  sheep: { m: 1.5, f: 1.0, e: 0.5, r: 18, wakeV: 120, dashV: 600 }
};
var HORNS = { curl: { speedMul: 1.0, e: 0.3, massMul: 1.0 }, straight: { speedMul: 1.15, e: 0.6, massMul: 1.0 },
  spiral: { speedMul: 1.0, e: 0.9, massMul: 1.0 }, branch: { speedMul: 0.9, e: 0.5, massMul: 1.4 } };
var SUB = 4, SLOP = 0.05, ITER = 2;
function wallE(b) { return Math.min(0.75, 0.5 * (1 + b.e) / 1.6); }
var MAXV = 900, FIELD = [0, 60, 375, 667], DEG = Math.PI / 180;
function split(a){const c=134217729*a;const hi=c-(c-a);return [hi,a-hi];}
function twoProd(a,b){const p=a*b;const [ah,al]=split(a),[bh,bl]=split(b);return [p,((ah*bh-p)+ah*bl+al*bh)+al*bl];}
function twoSum(a,b){const s=a+b;const bb=s-a;return [s,(a-(s-bb))+(b-bb)];}
function hyp(x,y){x=Math.abs(x);y=Math.abs(y);if(x===0)return y;if(y===0)return x;if(!isFinite(x)||!isFinite(y))return Infinity;
 const [xh,xl]=twoProd(x,x),[yh,yl]=twoProd(y,y);let [s,se]=twoSum(xh,yh);se+=xl+yl;const t=s+se;se=se-(t-s);s=t;
 let h=Math.sqrt(s);const [hh,hl]=twoProd(h,h);const r=((s-hh)-hl+se)/(2*h);return h+r;}

function hypot(x,y){return hyp(x,y);}
function mk(o) {
  var t = TYPES[o.type], b = {}; for (var k in o) b[k] = o[k];
  if (b.r === undefined) b.r = t.r; b.m = t.m; b.f = t.f; b.e = t.e;
  b.vx = b.vy = 0.0; b.alive = true; b.static = !!t.static; b.inHay = null;
  if (o.type === 'sheep') { b.awake = false; b.dashed = false; }
  return b;
}
function clone(state) { return JSON.parse(JSON.stringify(state)); }
// 逐步推进的一次顶撞（游戏动画用）；shoot() 一次跑完，两者结果相同
function Shot(level, state, angle, power, horn) {
  horn = horn || 'curl';
  var S = clone(state), H = HORNS[horn];
  var goat = mk({ id: 'player', type: 'goat', x: level.start.x, y: level.start.y });
  goat.m *= H.massMul; goat.e = H.e;
  var v = MAXV * power * H.speedMul, a = angle * DEG;
  goat.vx = v * Math.cos(a); goat.vy = -v * Math.sin(a);
  this.S = S; this.goat = goat; this.ev = []; this.step = 0; this.done = false; this.ns = undefined; this.level = level;
  this.B = S.filter(function (b) { return b.alive && !b.inHay; }).concat([goat]);
}
Shot.prototype.tick = function () {
  if (this.done) return true;
  var B = this.B, ev = this.ev, hays = this.level.hays, step = this.step, moving = false, n = 1;
  for (var ci = 0; ci < B.length; ci++) { var c = B[ci]; if (!c.static && c.alive && !c.inHay) n = Math.max(n, Math.ceil(hypot(c.vx, c.vy) * DT / c.r)); }
  n = Math.min(SUB, n); this.maxSub = Math.max(this.maxSub || 1, n);
  var dt = DT / n;
  for (var sub = 0; sub < n; sub++) {
    moving = false;
    for (var bi = 0; bi < B.length; bi++) {
      var b = B[bi];
      if (b.static || !b.alive || b.inHay) continue;
      var sp = hypot(b.vx, b.vy), ns = sp;
      if (sp > 0) { ns = Math.max(0, sp - b.f * G * dt); b.vx *= ns / sp; b.vy *= ns / sp; }
      if (b.awake && !b.dashed && ns === 0) {
        var d = b.dashDir * DEG; b.vx = TYPES.sheep.dashV * Math.cos(d); b.vy = -TYPES.sheep.dashV * Math.sin(d); b.dashed = true; ev.push(['dash', b.id]);
      }
      b.x += b.vx * dt; b.y += b.vy * dt;
      var x0 = FIELD[0], y0 = FIELD[1], x1 = FIELD[2], y1 = FIELD[3], we = wallE(b);
      if (b.x < x0 + b.r) { b.x = x0 + b.r; b.vx = Math.abs(b.vx) * we; ev.push(['wall', b.id]); }
      if (b.x > x1 - b.r) { b.x = x1 - b.r; b.vx = -Math.abs(b.vx) * we; ev.push(['wall', b.id]); }
      if (b.y < y0 + b.r) { b.y = y0 + b.r; b.vy = Math.abs(b.vy) * we; ev.push(['wall', b.id]); }
      if (b.y > y1 - b.r) { b.y = y1 - b.r; b.vy = -Math.abs(b.vy) * we; ev.push(['wall', b.id]); }
      if (hypot(b.vx, b.vy) > 1) moving = true;
      if (b.target) {
        for (var hi = 0; hi < hays.length; hi++) { var h = hays[hi];
          if (!b.inHay && hypot(b.x - h.x, b.y - h.y) < h.r && (h.accepts == null || h.accepts === b.id)) { b.inHay = h.id; b.vx = b.vy = 0; ev.push(['hay', b.id, h.id]); } }
      }
    }
    for (var it = 0; it < ITER; it++) for (var i = 0; i < B.length; i++) for (var j = i + 1; j < B.length; j++) {
      var p = B[i], q = B[j];
      if (!(p.alive && q.alive) || p.inHay || q.inHay) continue;
      var dx = q.x - p.x, dy = q.y - p.y, dd = hypot(dx, dy), rr = p.r + q.r;
      if (dd === 0 || dd >= rr) continue;
      var nx = dx / dd, ny = dy / dd, rv = (q.vx - p.vx) * nx + (q.vy - p.vy) * ny;
      if (rv < 0 && it === 0) {
        var imp = -rv, os = [p, q];
        for (var k = 0; k < 2; k++) { var o = os[k];
          if (o.type === 'fragile' && imp > TYPES.fragile.breakV) { o.alive = false; ev.push(['break', o.id]); }
          if (o.type === 'sheep' && !o.awake && imp > TYPES.sheep.wakeV) { o.awake = true; ev.push(['wake', o.id]); } }
        if (!(p.alive && q.alive)) continue;
        if (p.static || q.static) ev.push(['rock', (p.static ? q : p).id]);
        var e = Math.min(p.e, q.e), im = (p.static ? 0 : 1 / p.m) + (q.static ? 0 : 1 / q.m), jn = -(1 + e) * rv / im;
        if (!p.static) { p.vx -= jn * nx / p.m; p.vy -= jn * ny / p.m; }
        if (!q.static) { q.vx += jn * nx / q.m; q.vy += jn * ny / q.m; }
      }
      var ov = rr - dd - SLOP, tm = (p.static ? 0 : 1 / p.m) + (q.static ? 0 : 1 / q.m);
      if (ov > 0 && tm > 0) {
        if (!p.static) { p.x -= nx * ov * (1 / p.m) / tm; p.y -= ny * ov * (1 / p.m) / tm; }
        if (!q.static) { q.x += nx * ov * (1 / q.m) / tm; q.y += ny * ov * (1 / q.m) / tm; }
      }
    }
  }
  if (this.onStep) this.onStep(B, step);
  this.step++;
  if ((!moving && step > 5 && !B.some(function (b) { return b.awake && !b.dashed; })) || this.step >= 60 * 8) { this.done = true; this.timeout = this.step >= 60 * 8; }
  return this.done;
};
function shoot(level, state, angle, power, horn, onStep) {
  var s = new Shot(level, state, angle, power, horn); s.onStep = onStep; while (!s.tick()) {} return { state: s.S, ev: s.ev };
}
function init(level) { return level.objects.map(mk); }
function solved(state) { return state.filter(function (b) { return b.target; }).every(function (b) { return b.inHay; }); }
function targetsAlive(state) { return state.filter(function (b) { return b.target; }).every(function (b) { return b.alive; }); }
function starsFor(level, shots) { var s = level.stars; return shots <= s['3'] ? 3 : shots <= s['2'] ? 2 : shots <= s['1'] ? 1 : 0; }
module.exports = { VERSION: 2, SUB: SUB, SLOP: SLOP, DT: DT, TYPES: TYPES, HORNS: HORNS, FIELD: FIELD, MAXV: MAXV, mk: mk, Shot: Shot, shoot: shoot, init: init, solved: solved, targetsAlive: targetsAlive, starsFor: starsFor };
