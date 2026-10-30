// 顶顶乐关卡模式：选关、瞄准、顶撞、星级、激励视频占位 + 07 容错辅助
var P = require('./ddl_physics.js');
function loadJSON(p) {
  if (typeof wx !== 'undefined' && wx.getFileSystemManager) return JSON.parse(wx.getFileSystemManager().readFileSync(p, 'utf8'));
  if (typeof process !== 'undefined' && process.versions && process.versions.node) {
    return JSON.parse(require('fs').readFileSync(p, 'utf8'));
  }
  var x = new XMLHttpRequest(); x.open('GET', p, false); x.send(); return JSON.parse(x.responseText);
}
// 07：加载 levels.v2.json，不覆盖/删除 levels.json
var DATA = loadJSON('design/data/levels.v2.json');
var KEY = 'goat_ddl_progress_v1';
var aimAssistOn = true; // 角度吸附开关（默认开）；力度吸附常开
var store = {
  get: function () { try { if (typeof wx !== 'undefined' && wx.getStorageSync) return wx.getStorageSync(KEY) || null; if (typeof localStorage !== 'undefined') return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {} return null; },
  set: function (v) { try { if (typeof wx !== 'undefined' && wx.setStorageSync) return wx.setStorageSync(KEY, v); if (typeof localStorage !== 'undefined') localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }
};
function loadProg() {
  var p = store.get();
  if (!p) p = { stars: {}, grass: 0, daily: {} };
  return p;
}
function saveProg(p) { store.set(p); }
function levelById(id) { return DATA.levels.filter(function (l) { return l.id === id; })[0]; }
function bestStars(p, id) { return p.stars[id] || 0; }
function unlocked(p, id) { return id === 1 || bestStars(p, id - 1) > 0; }

function startLevel(id, horn) {
  var lv = levelById(id);
  return {
    lv: lv, horn: horn || lv.horn || 'curl',
    state: P.init(lv), shots: 0, max: lv.maxShots,
    phase: 'aim',
    shot: null, msg: '', hint: false, adExtra: false, adHint: false,
    aimAngle: 90, aimPower: 0.8, meter: 0, dir: 1,
    drag: null,
    goatPos: { x: lv.start.x, y: lv.start.y },
    lastAssist: null
  };
}

// 07 伪代码：开火前力度/角度吸附（不改物理）
function applyAssist(G) {
  var before = { angle: G.aimAngle, power: G.aimPower };
  // powerSnap：±0.05 吸到 0.5–1.0 档（默认常开；level.assist.powerSnap===false 可关）
  var powerOn = !(G.lv.assist && G.lv.assist.powerSnap === false);
  if (powerOn) {
    var notches = (DATA.assist && DATA.assist.powerSnapNotches) || [0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
    var snap = (DATA.assist && DATA.assist.powerSnap) || 0.05;
    var best = G.aimPower, bd = 1;
    notches.forEach(function (n) { var d = Math.abs(G.aimPower - n); if (d <= snap && d < bd) { bd = d; best = n; } });
    G.aimPower = best;
  }
  // angleMagnet：±3° 吸向最近可推物件/草堆；L3/L8 关；设置可关
  var angleOn = aimAssistOn && !(G.lv.assist && G.lv.assist.angleMagnet === false);
  if (angleOn) {
    var sx = G.lv.start.x, sy = G.lv.start.y, bestA = null, bestD = 4;
    var cone = (DATA.assist && DATA.assist.angleSnapDeg) || 3;
    function consider(x, y) {
      var a = Math.atan2(sy - y, x - sx) * 180 / Math.PI; if (a < 0) a += 360;
      var d = Math.abs(((G.aimAngle - a + 180) % 360) - 180);
      if (d <= cone && d < bestD) { bestD = d; bestA = a; }
    }
    G.state.forEach(function (b) {
      if (!b.alive || b.inHay || b.static || b.type === 'rock') return;
      consider(b.x, b.y);
    });
    G.lv.hays.forEach(function (h) { consider(h.x, h.y); });
    if (bestA != null) G.aimAngle = bestA;
  }
  G.lastAssist = { before: before, after: { angle: G.aimAngle, power: G.aimPower }, powerOn: powerOn, angleOn: angleOn };
  return G.lastAssist;
}

function fire(G) {
  if (G.phase !== 'aim' || G.shots >= G.max) return;
  applyAssist(G);
  G.shots++; G.phase = 'flying'; G.msg = '';
  G.shot = new P.Shot(G.lv, G.state, G.aimAngle, G.aimPower, G.horn);
  G.goatPos = { x: G.lv.start.x, y: G.lv.start.y };
}
function tick(G) {
  if (G.phase !== 'flying' || !G.shot) return;
  var done = G.shot.tick();
  G.goatPos = { x: G.shot.goat.x, y: G.shot.goat.y };
  G.state = G.shot.S;
  if (done) {
    G.shot = null;
    if (P.solved(G.state) && P.targetsAlive(G.state)) {
      G.phase = 'result'; G.stars = P.starsFor(G.lv, G.shots);
      G.msg = '过关！' + '★'.repeat(G.stars) + '☆'.repeat(3 - G.stars) + ' 用了 ' + G.shots + ' 次顶撞';
    } else if (G.shots >= G.max) { G.phase = 'fail'; G.msg = '顶撞次数用完了'; }
    else { G.phase = 'aim'; G.meter = 0; G.dir = 1; G.goatPos = { x: G.lv.start.x, y: G.lv.start.y }; }
  }
}
function grantExtra(G) {
  if (G.adExtra || G.phase === 'result') return false;
  G.adExtra = true; G.max += 1;
  if (G.phase === 'fail') { G.phase = 'aim'; G.msg = '（模拟）广告完成，+1 次顶撞'; }
  else G.msg = '（模拟）广告完成，+1 次顶撞';
  return true;
}
function grantHint(G) {
  if (G.adHint) return false;
  G.adHint = true; G.hint = true; G.msg = '（模拟）显示第 1 步瞄准线'; return true;
}
function onClear(prog, dateKey, G) {
  var id = G.lv.id, prev = bestStars(prog, id);
  if (G.stars > prev) prog.stars[id] = G.stars;
  if (!prog.daily[dateKey]) prog.daily[dateKey] = { clears: 0 };
  var d = prog.daily[dateKey], reward = 0;
  if (d.clears < 3) { reward = 5 + G.stars * 5; prog.grass = (prog.grass || 0) + reward; d.clears++; }
  saveProg(prog); return reward;
}
module.exports = { DATA: DATA, P: P, loadProg: loadProg, saveProg: saveProg, levelById: levelById, bestStars: bestStars, unlocked: unlocked,
  startLevel: startLevel, fire: fire, tick: tick, grantExtra: grantExtra, grantHint: grantHint, onClear: onClear,
  applyAssist: applyAssist, getAimAssistOn: function () { return aimAssistOn; }, setAimAssistOn: function (v) { aimAssistOn = !!v; } };
