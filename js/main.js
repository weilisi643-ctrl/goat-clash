var D = require('./data.js'), BP = require('./battle_physics.js'), FX = require('./fx.js'), G = require('./goat.js'), A = require('./arena.js'), DDL = require('./ddl.js'), UI = require('./ui.js');
var canvas = wx.createCanvas(), ctx = canvas.getContext('2d');
var info = wx.getSystemInfoSync(), W = info.windowWidth, H = info.windowHeight;
canvas.width = W; canvas.height = H;
// 蓄力答题开关：false = 自由对战和每日擂主都不出蓄力题、无答题力量加成（makeQuiz/answer 代码保留）
var QUIZ_ENABLED = false;
var ANG = ['low', 'mid', 'high'], ANGN = { low: '低', mid: '中', high: '高' };
var st = { scene: 'custom', look: { wool: 'fluffy', woolColor: D.woolColors[0], horn: 'curl', hornColor: D.hornColors[0] },
  idx: { wool: 0, wc: 0, horn: 0, hc: 0 }, buttons: [] };
function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
function stats(look) {
  var w = D.wools.filter(function (x) { return x.id === look.wool; })[0], h = D.horns.filter(function (x) { return x.id === look.horn; })[0];
  return { hp: 100 + w.hp, spd: w.spd, pow: h.pow, win: h.win };
}
function btn(x, y, w, h, label, cb, variant, fs) { // 统一按钮绘制读主题（js/theme.js）；命中区 = 绘制的按钮矩形（动画只影响绘制）
  UI.drawButton(ctx, x, y, w, h, label, variant, fs); st.buttons.push({ x: x, y: y, w: w, h: h, cb: cb, label: label });
}
var TH = UI.TH, LY = TH.layout;
function pill(s, x, y, light, size) { return UI.drawPill(ctx, s, x, y, light, size); }
function panel(x, y, w, h, alpha) { UI.drawPanel(ctx, x, y, w, h, alpha); }
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function text(s, x, y, size, style, align) { UI.drawText(ctx, s, x, y, size, style || 'ink', align); }
function bg() { UI.drawBg(ctx, W, H);
  var fid = arenaFaction(); if (fid) UI.factionTint(ctx, W, H, fid); }
function arenaFaction() { // 擂主相关画面按玩家牧场加色调（只显示牧场名，不显示省份）
  var sc = st.scene, inArena = sc === 'arena' || sc === 'faction' || sc === 'arenaResult' || (sc === 'battle' && B && B.arena);
  return inArena && AR && AR.p ? AR.p.faction : null; }

// ---------- 定制界面 ----------
function cycle(k, arr, n) { st.idx[k] = (st.idx[k] + n + arr.length) % arr.length; }
function syncLook() { var i = st.idx; st.look = { wool: D.wools[i.wool].id, woolColor: D.woolColors[i.wc], horn: D.horns[i.horn].id, hornColor: D.hornColors[i.hc] }; }
function drawCustom() {
  var L = LY.home; bg(); text('咩咩顶角王', W / 2, L.titleY, L.titleSize, 'title'); pill('打造你的山羊', W / 2, L.pillY);
  G.drawShadow(ctx, W / 2, L.goatY, L.goatS, 0); G.drawGoatArt(ctx, W / 2, L.goatY, L.goatS, st.look, 1, 0);
  var s = stats(st.look), h = D.horns[st.idx.horn];
  text('体力 ' + s.hp + ' · 速度 ' + (s.spd >= 0 ? '+' : '') + s.spd + ' · 力量 +' + s.pow, W / 2, L.statsY, 14);
  text(h.name + '：' + h.tip, W / 2, L.tipY, 11, 'muted');
  var rows = [['羊毛', 'wool', D.wools, D.wools[st.idx.wool].name], ['毛色', 'wc', D.woolColors, ''], ['角形', 'horn', D.horns, h.name], ['角色', 'hc', D.hornColors, '']];
  rows.forEach(function (r, i) {
    var y = L.rowY + i * L.rowGap, aw = L.arrowW, x0 = L.rowX, x1 = W - L.rowX - aw, px = x0 + aw + 9, pw = x1 - 9 - px;
    btn(x0, y, aw, L.rowH, '◀', function () { cycle(r[1], r[2], -1); syncLook(); }, 'yellow', 16);
    btn(x1, y, aw, L.rowH, '▶', function () { cycle(r[1], r[2], 1); syncLook(); }, 'yellow', 16);
    UI.sticker(ctx, px, y, pw, L.rowH, L.rowH / 2, '#FFFFFF', 0, null, 2);
    text(r[0], px + pw * 0.33, y + L.rowH / 2, 14, 'muted'); 
    if (r[3]) text(r[3], px + pw * 0.62, y + L.rowH / 2, 15);
    else { ctx.fillStyle = r[2][st.idx[r[1]]]; ctx.beginPath(); ctx.arc(px + pw * 0.62, y + L.rowH / 2, 8, 0, 7); ctx.fill(); ctx.strokeStyle = TH.colors.ink; ctx.lineWidth = 1.5; ctx.stroke(); }
  });
  var by = H - L.startBottom;
  btn(W / 2 - L.startW / 2, by, L.startW, L.startH, '开始对战', function () { startMatch(); }, 'main', 26);
  btn(L.sideX, H - L.sideBottom, L.sideW, L.sideH, '每日\n擂主', openArena, 'blue', 13);
  btn(W - L.sideX - L.sideW, H - L.sideBottom, L.sideW, L.sideH, '顶\n顶乐', openDdl, 'orange', 13);
  text('适度游戏益脑，沉迷游戏伤身', W / 2, H - 14, 10, 'muted');
}
// ---------- 对战 ----------
var B;
function startMatch(arena) { // arena: {stage, cfg} 为擂主战；不传则为原有自由对战
  var ai = arena ? arena.cfg.look : { wool: pick(D.wools).id, woolColor: pick(D.woolColors), horn: pick(D.horns).id, hornColor: pick(D.hornColors) };
  B = { ai: ai, wins: [0, 0], round: 1, msg: '', arena: arena || null, hits: 0, guesses: 0, timingSum: 0, jumps: 0, timings: [] };
  if (arena) { B.stageCfg = arena.cfg.stages[arena.stage - 1]; B.ai = ai; }
  startRound(); st.scene = 'battle';
}
function eMaxHp() { return stats(B.ai).hp + (B.arena ? B.stageCfg.ai.hpBonus || 0 : 0); }
function afterQuiz() { // 擂主战：AI 定架势 → 观察线索 → 预判
  if (!B.arena) { B.phase = 'charge'; B.meter = 0; B.dir = 1; B.e.ang = pick(ANG); return; }
  var ai = B.stageCfg.ai, pw = stats(st.look).win, cfg = B.arena.cfg, ang;
  if (!A.REASONING_ENABLED) { // 无推理：擂主按偏好架势出角度，直接进入蓄力
    var sid0 = pick(cfg.stancePref); B.e.stance = A.CLUES.stances.filter(function (x) { return x.id === sid0; })[0];
    B.e.ang = B.e.stance.ang; B.p.guess = null; B.phase = 'charge'; B.meter = 0; B.dir = 1; return;
  }
  if (pw !== 'none' && Math.random() < ai.counterPick) { var ok = ANG.filter(function (a) { return a !== pw; }); ang = pick(ok); } // 避开玩家角形克制
  else { var sid = pick(cfg.stancePref); ang = A.CLUES.stances.filter(function (x) { return x.id === sid; })[0].ang; }
  var stance = A.stanceFor(ang, cfg.stancePref);
  B.e.ang = ang; B.e.stance = stance; B.p.guess = null;
  B.obs = A.genClues(ang, B.stageCfg.clueLv, B.ai.horn); B.obs.t0 = Date.now();
  B.phase = 'observe';
}
function makeGuess(g) {
  if (B.phase !== 'observe' || !A.REASONING_ENABLED) return;
  B.p.guess = g; B.guesses++; if (g === B.e.ang) B.hits++;
  B.msg = g ? '你预判对手是「' + ANGN[g] + '」角度' : '观察超时，视为未预判';
  B.phase = 'charge'; B.meter = 0; B.dir = 1;
}
function startRound() {
  B.p = { hp: stats(st.look).hp, x: W * 0.25, y: 0, vy: 0, ang: 'mid', bonus: 0 };
  B.e = { hp: eMaxHp(), x: W * 0.75, y: 0, vy: 0, ang: pick(ANG) };
  B.t = 0; nextExchange();
}
function makeQuiz() {
  var a = 1 + Math.floor(Math.random() * 9), b = 1 + Math.floor(Math.random() * 9), ans = a + b;
  var opts = [ans, ans + 1, ans - 1].sort(function () { return Math.random() - .5; });
  B.quiz = { q: '⚡ 蓄力题：' + a + ' + ' + b + ' = ?', ans: ans, opts: opts, t0: Date.now() };
}
function answer(v) {
  if (!QUIZ_ENABLED || B.phase !== 'quiz') return;
  var dt = (Date.now() - B.quiz.t0) / 1000;
  B.p.bonus = v === B.quiz.ans ? (dt < 3 ? 20 : 10) : 0;
  B.msg = v === B.quiz.ans ? '答对了！力量 +' + B.p.bonus : '答错啦，没有加成~';
  afterQuiz();
}
function nextExchange() { // 每次对撞前：蓄力题（擂台可由 quizEnabled 关闭）→ 推理/蓄力
  if (!QUIZ_ENABLED || (B.arena && !A.CLUES.tuning.quizEnabled)) { B.p.bonus = 0; afterQuiz(); } else { B.phase = 'quiz'; makeQuiz(); }
}
function jump() { // 玩家点击起跳；对手同步起跳
  if (B.phase !== 'charge') return;
  B.timing = 1 - Math.abs(B.meter - 0.8) / 0.8; if (B.timing < 0) B.timing = 0; // 0.8 为完美点
  B.timingSum += B.timing; B.jumps++; B.timings.push(B.timing);
  // physics v2：对手时机在起跳时决定（擂主=timingHit 命中则 1，否则 0–0.7；自由对战 0–1 随机），决定双方抛物线高度
  B.eTiming = B.arena ? (Math.random() < B.stageCfg.ai.timingHit ? 1 : Math.random() * 0.7) : Math.random();
  BP.startJump(B.p, B.timing); BP.startJump(B.e, B.eTiming); B.p.kv = B.e.kv = 0; B.phase = 'air'; B.t = 0;
  FX.ev('jump', { id: 'p', x: B.p.x, y: GY() + 45 }); FX.ev('jump', { id: 'e', x: B.e.x, y: GY() + 45 }); // 特效只读
}
function clash() {
  var ps = stats(st.look), es = stats(B.ai);
  var pp = 20 + ps.pow + B.p.bonus + B.timing * 30 + ps.spd * 0.3;
  if (B.arena) { // 擂主战：AI 参数 + 角力推理倍率（design/03 接入示例）
    var ai = B.stageCfg.ai, eT = B.eTiming;
    var ep = 20 + es.pow + ai.powBonus + eT * 30 + es.spd * 0.3;
    B.e.readHit = A.REASONING_ENABLED && Math.random() < ai.readAcc;
    var m = A.multipliers({ pWin: ps.win, eWin: es.win, pAng: B.p.ang, eAng: B.e.ang, guess: B.p.guess, eReadHit: B.e.readHit });
    pp *= m.mulP; ep *= m.mulE;
    if (A.REASONING_ENABLED) B.reveal = '对手真实角度：' + ANGN[B.e.ang] + (m.hit ? ' ✔预判命中' : ' ✘未命中') + (B.e.readHit ? ' | 对手看穿了你' : '');
    else if (B.stageCfg.angleReveal === 'hidden') B.reveal = '对手角度揭晓：' + ANGN[B.e.ang];
    else B.reveal = '';
  } else {
    var ep = 20 + es.pow + (B.eTiming * 25 + 5) + es.spd * 0.3; // 与 v1 同分布（5–30 均匀）
    // 角形 vs 角度 石头剪刀布：自己的角形克制对方选择的角度时 x1.3
    if (ps.win === B.e.ang) pp *= 1.3; if (es.win === B.p.ang) ep *= 1.3;
  }
  var c = B.contact || { dy: 0, align: 1 };
  pp *= BP.heightMul(B.p.y, B.e.y); ep *= BP.heightMul(B.e.y, B.p.y); // 角判定点高度差：居高临下 ±3%
  var d = BP.damage(pp, ep, c.align); BP.knockback(B.p, B.e, pp, ep); B.lastClash = { pp: pp, ep: ep, dmg: d, dy: c.dy, align: c.align };
  if (pp >= ep) { B.e.hp -= d; B.msg = '咚！你赢了这次对撞，造成 ' + d; }
  else { B.p.hp -= d; B.msg = '哎呀！被顶了 ' + d; }
  B.phase = 'result'; B.t = 0;
  if (B.p.hp <= 0 || B.e.hp <= 0) { var w = B.p.hp > 0 ? 0 : 1; B.wins[w]++; B.roundEnd = w; }
  else B.roundEnd = -1;
}
function next() {
  if (B.roundEnd >= 0) {
    if (B.wins[0] === 2 || B.wins[1] === 2) { if (B.arena) return arenaStageEnd(); st.scene = 'over'; return; }
    B.round++; startRound();
  } else nextExchange();
}
function updateBattle() { // 固定步 1/60s：只改物理/逻辑状态，绘制在 drawBattle
  if (B.phase === 'air') { // physics v2：解析抛物线 + 按 art v7 角根判定点检测接触
    BP.stepAir(B.p, 1); BP.stepAir(B.e, -1); var hc = BP.contact(B.p, B.e);
    if (hc) { BP.resolvePenetration(B.p, B.e, hc); B.contact = hc;
      var snap = { p: { x: B.p.x, y: B.p.y, vy: 0 }, e: { x: B.e.x, y: B.e.y, vy: 0 }, t: 0, phase: 'result' }; clash();
      var hp = BP.hornPoint(B.p, 1, 'jump'), he = BP.hornPoint(B.e, -1, 'jump');
      FX.ev('clash', { x: (hp[0] + he[0]) / 2, y: GY() + (hp[1] + he[1]) / 2, d: Math.abs(B.lastClash.pp - B.lastClash.ep), snap: snap, gy: GY() + 45, wool: (B.lastClash.pp >= B.lastClash.ep ? B.ai : st.look).woolColor });
      if (B.roundEnd === 0) FX.ev('win', { x: W / 2, y: H * 0.45 }); }
    else if (!B.p.air && !B.e.air) { B.contact = null; B.p.y = B.e.y = 0; } // 理论不可达（落地前必接触）；保险
  }
  if (B.phase === 'result') { var a0 = B.p.air, a1 = B.e.air; BP.stepRecover(B.p, W * 0.25, W); BP.stepRecover(B.e, W * 0.75, W);
    if (a0 && !B.p.air) FX.ev('land', { id: 'p', x: B.p.x, y: GY() + 45 }); if (a1 && !B.e.air) FX.ev('land', { id: 'e', x: B.e.x, y: GY() + 45 }); }
  B.t++;
  if (B.phase === 'charge') { B.meter += 0.018 * B.dir; if (B.meter > 1 || B.meter < 0) B.dir *= -1; }
}
function drawBattle() {
  var L = LY.battle; bg(); var gy = H * 0.72 - 40;
  pill('第 ' + B.round + ' 回合 · 三局两胜', W / 2, L.pillY, false, 13);
  text(B.wins[0] + ' : ' + B.wins[1], W / 2, L.scoreY, L.scoreSize, 'score');
  hpBar(20, L.hpY, B.p.hp, stats(st.look).hp, '你', false); hpBar(W - 20 - L.hpW, L.hpY, B.e.hp, eMaxHp(), B.arena ? '擂主·' + B.arena.cfg.name : '电脑', true);
  if (B.arena) text('每日擂主 第 ' + B.arena.stage + ' 场' + (A.REASONING_ENABLED ? ' · 线索 Lv' + B.stageCfg.clueLv : ''), W / 2, L.arenaY, 12, 'muted');
  var V = (FX.enabled && FX.view(B)) || { p: B.p, e: B.e, t: B.t, phase: B.phase }; // 顿帧定格+插值追帧：只影响显示，物理照常推进
  var sk = FX.enabled ? FX.shakeOff() : [0, 0]; ctx.save(); ctx.translate(sk[0], sk[1] + (L.sceneShiftY || 0)); // 屏震只作用于场景层；sceneShiftY 仅平移显示
  G.drawShadow(ctx, V.p.x, gy, 1.1, -V.p.y); G.drawShadow(ctx, V.e.x, gy, 1.1, -V.e.y);
  var pose = V.phase === 'air' ? 'jump' : (V.phase === 'result' && V.t < 25) ? 'clash' : 'idle';
  goatSq('p', V.p, gy, function () { G.drawGoatArt(ctx, V.p.x, gy + V.p.y, 1.1, st.look, 1, 0, pose); });
  goatSq('e', V.e, gy, function () { G.drawGoatArt(ctx, V.e.x, gy + V.e.y, 1.1, B.ai, -1, 0, pose); });
  if (V.phase === 'result' && V.t < 25) text('💥', W / 2, gy - 40, 40);
  if (FX.enabled) FX.drawScene(ctx); ctx.restore();
  if (B.msg) text(B.msg, W / 2, L.msgY, 16, 'warn');
  var y0 = H * 0.76, aY = H - L.angleBottom, hintY = H - L.hintBottom;
  if (B.phase === 'quiz' && QUIZ_ENABLED) {
    text(B.quiz.q, W / 2, y0, 20); B.quiz.opts.forEach(function (o, i) { btn(W / 2 - 130 + i * 90, y0 + 25, 80, 44, '' + o, function () { answer(o); }, 'white'); });
    text('3 秒内答对 +20，答对 +10', W / 2, y0 + 90, 12, 'muted');
  } else if (B.phase === 'observe' && A.REASONING_ENABLED) {
    var left = B.obs.observeSec - (Date.now() - B.obs.t0) / 1000;
    if (left <= 0) { makeGuess(null); return; }
    panel(16, 128, W - 32, 40 + B.obs.clues.length * 24);
    text('对手摆出架势「' + B.e.stance.name + '」 观察 ' + left.toFixed(1) + 's', W / 2, 146, 14, 'accent');
    B.obs.clues.forEach(function (c, i) { text('👁 ' + c.text, W / 2, 172 + i * 24, 14); });
    pill('预判对手真正的角度', W / 2, hintY, true);
    ANG.forEach(function (a, i) { btn(W / 2 - 3 * L.angleW / 2 - 15 + i * (L.angleW + 15), aY, L.angleW, L.angleH, ANGN[a] + '角度', function () { makeGuess(a); }, 'white'); });
    text('提示：有的线索是假动作，有的线索永远不会骗人', W / 2, H - L.meterBottom + 10, 12, 'muted');
  } else if (B.phase === 'charge') {
    var hint = (B.arena && A.REASONING_ENABLED) ? '你的预判：' + (B.p.guess ? ANGN[B.p.guess] + '角度' : '无') + ' · 选你的角度'
      : (B.arena && B.stageCfg.angleReveal === 'hidden') ? '对手角度隐藏 · 选你的角度' : '对手架势：' + ANGN[B.e.ang] + '角度 · 选你的角度';
    pill(hint, W / 2, hintY, true, 13);
    ANG.forEach(function (a, i) { var sel = B.p.ang === a;
      btn(W / 2 - 3 * L.angleW / 2 - 15 + i * (L.angleW + 15), aY, L.angleW, L.angleH, ANGN[a], function () { B.p.ang = a; }, sel ? 'sel' : 'white', 22); });
    UI.drawMeter(ctx, 52, H - L.meterBottom, W - 104, B.meter, 0.72, 0.88);
    btn(W / 2 - L.jumpW / 2, H - L.jumpBottom, L.jumpW, L.jumpH, '起跳顶角！', jump, 'main', 24);
  }
  if (B.phase === 'result' && B.arena && B.reveal) pill(B.reveal, W / 2, hintY, true, 13);
  if (B.phase === 'result' && B.t > 30) btn(W / 2 - L.jumpW / 2, H - L.jumpBottom, L.jumpW, L.jumpH, B.roundEnd >= 0 ? '下一回合' : '继续', next, 'main', 24);
}
function goatSq(id, g, gy, fn) { // 挤压拉伸：仅绕脚底缩放绘制，不改 goat.js
  var k = FX.enabled ? FX.squash(id, g.vy) : [1, 1], fy = gy + g.y + 44;
  if (k[0] === 1 && k[1] === 1) return fn();
  ctx.save(); ctx.translate(g.x, fy); ctx.scale(k[0], k[1]); ctx.translate(-g.x, -fy); fn(); ctx.restore();
}
function hpBar(x, y, hp, max, n, right) { var w = LY.battle.hpW, v = Math.max(0, hp);
  text(right ? v + ' · ' + n : n + ' · ' + v, right ? x + w : x, LY.battle.hpLabelY, 14, 'ink', right ? 'right' : 'left');
  UI.drawBar(ctx, x, y, w, v, max, right); }
function resultCard(win, banner) { var R = LY.result; bg(); UI.dim(ctx, W, H); panel(R.cardX, R.cardY, W - 2 * R.cardX, R.cardH);
  text(banner, W / 2, R.bannerY, 44, win ? 'banner' : 'bannerLose'); }
function drawOver() {
  var R = LY.result, win = B.wins[0] === 2; resultCard(win, win ? '胜 利 !' : '再接再厉');
  G.drawShadow(ctx, W / 2, R.goatY, R.goatS, 0); G.drawGoatArt(ctx, W / 2, R.goatY, R.goatS, st.look, 1, 0);
  text(win ? '你是顶角王！' : '惜败，再练练', W / 2, R.lineY, 17);
  text('本场比分', W / 2, R.subY, 14, 'muted');
  text(B.wins[0] + ' : ' + B.wins[1], W / 2, R.bigY, R.bigSize, 'score');
  btn(W / 2 - R.btnW / 2, R.btnY, R.btnW, R.btnH, '再来一局', function () { startMatch(); }, 'main', 23);
  btn(W / 2 - R.btn2W / 2, R.btn2Y, R.btn2W, R.btn2H, '回主页', function () { st.scene = 'custom'; }, 'blue', 17);
}
// ---------- 每日擂主 ----------
var AR = null, nowOverride = null;
function now() { return nowOverride || Date.now(); }
function openArena() {
  var dk = A.dateKeyAt(now()), ch = A.championFor(dk);
  AR = { dateKey: dk, champ: ch, p: A.loadProgress(dk), msg: ch.preview ? '（开服前预览：' + A.CHAMPS.startDate + ' 起正式计日）' : '' };
  A.saveProgress(AR.p);
  st.scene = AR.p.factionAsked ? 'arena' : 'faction';
}
function chooseFaction(id) {
  var p = AR.p; p.factionAsked = true;
  if (id && !A.setFaction(p, id, AR.dateKey)) AR.msg = '每 ' + A.FACTIONS.changeCooldownDays + ' 天只能更换一次牧场';
  else if (id) AR.msg = '已加入' + A.factionById(id).name + '，为' + A.factionById(id).name + '加油！';
  A.saveProgress(p); st.scene = 'arena';
}
function drawFaction() {
  var L = LY.list; bg(); text('选择你的牧场', W / 2, L.titleY, 34, 'title');
  text('按你觉得的家乡大区选，只带来荣誉和外观', W / 2, L.subY, 13);
  text('不选也能正常玩，只是不计阵营分', W / 2, L.subY + 19, 12, 'muted');
  var fs = A.FACTIONS.factions, bw = (W - 2 * LY.pad - 14) / 2;
  fs.forEach(function (f, i) { // 牧场名由 factionLabel 生成，以后加省份只改这一处
    var x = LY.pad + (i % 2) * (bw + 14), y = L.top + 22 + Math.floor(i / 2) * (L.rowH + L.gap), cur = AR.p.faction === f.id;
    btn(x, y, bw, L.rowH, A.factionLabel(f) + (cur ? ' ✔' : ''), function () { chooseFaction(f.id); }, cur ? 'sel' : 'white', 17);
  });
  btn(W / 2 - 70, H - L.backBottom - 30, 140, 44, '稍后再选', function () { chooseFaction(null); }, 'gray', 17);
}
function startArenaStage(stage) {
  var p = AR.p, cfg = AR.champ.cfg, sc = cfg.stages[stage - 1];
  if (sc.allowedHorns && sc.allowedHorns.indexOf(st.look.horn) < 0) { AR.msg = '第 2 场限定角形，请先在下方切换'; return; }
  if (stage === 1 && !p.defended) {
    if (A.triesLeft(p) <= 0) { AR.msg = '今日次数已用完，明天 05:00 刷新'; return; }
    p.tries.used++; p.inChallenge = true; p.stage1Won = false;
  }
  if (stage === 2 && !p.defended && !(p.inChallenge && p.stage1Won)) { AR.msg = '先赢下第 1 场'; return; }
  A.saveProgress(p); startMatch({ stage: stage, cfg: cfg });
}
function arenaStageEnd() {
  var win = B.wins[0] === 2; if (win) FX.ev('win', { x: W / 2, y: H * 0.35 }); // 冠军彩带
  var info = { hpPct: Math.max(0, B.p.hp) / stats(st.look).hp, hits: B.hits, guesses: B.guesses,
    timingAvg: B.jumps ? B.timingSum / B.jumps : 0, roundsLost: B.wins[1], timings: B.timings.slice() };
  var r = A.onStageEnd(AR.p, B.arena.stage, win, info, AR.champ.cfg); A.saveProgress(AR.p);
  AR.last = { stage: B.arena.stage, win: win, info: info, msgs: r.msgs }; st.scene = 'arenaResult';
}
function drawArenaResult() {
  var R = LY.result, L = AR.last; resultCard(L.win, L.win ? '第 ' + L.stage + ' 场胜利' : '第 ' + L.stage + ' 场惜败');
  G.drawShadow(ctx, W / 2, R.goatY - 10, R.goatS, 0); G.drawGoatArt(ctx, W / 2, R.goatY - 10, R.goatS, st.look, 1, 0);
  if (A.REASONING_ENABLED) text('预判命中 ' + L.info.hits + ' / ' + L.info.guesses, W / 2, R.lineY - 12, 15);
  else text('剩余体力 ' + Math.round(L.info.hpPct * 100) + '% · 时机 ' + (L.info.timingAvg != null ? (L.info.timingAvg * 100).toFixed(0) + '%' : '-'), W / 2, R.lineY - 12, 15);
  L.msgs.forEach(function (m, i) { text(m, W / 2, R.subY - 6 + i * 20, 13, 'accent'); });
  if (L.win && L.stage === 1 && AR.p.inChallenge) btn(W / 2 - R.btnW / 2, R.btnY, R.btnW, R.btnH, '挑战第 2 场！', function () { st.scene = 'arena'; startArenaStage(2); }, 'main', 21);
  btn(W / 2 - R.btn2W / 2, R.btn2Y, R.btn2W, R.btn2H, '返回擂台', function () { st.scene = 'arena'; }, 'blue', 16);
}
function drawArena() {
  bg(); var p = AR.p, cfg = AR.champ.cfg, s2 = cfg.stages[1], P = LY.pad;
  text('每日擂主', W / 2, 44, 36, 'title'); pill(AR.dateKey, W / 2, 84, false, 12);
  var f = p.faction ? A.factionById(p.faction) : null;
  text((f ? A.factionLabel(f) : '未选牧场') + ' · 青草币 ' + p.grass + ' · 守擂 ' + p.defendDays + ' 天', W / 2, 106, 12, 'muted');
  G.drawShadow(ctx, W * 0.72, 160, 0.9, 0); G.drawGoatArt(ctx, W * 0.72, 160, 0.9, cfg.look, -1, 0);
  G.drawShadow(ctx, W * 0.28, 160, 0.9, 0); G.drawGoatArt(ctx, W * 0.28, 160, 0.9, st.look, 1, 0);
  text('VS', W / 2, 168, 26, 'score');
  panel(P, 218, W - 2 * P, 88); text('今日擂主：' + cfg.name + (AR.champ.procedural ? '（轮换）' : ''), W / 2, 238, 17);
  text('剩余挑战 ' + A.triesLeft(p) + ' 次' + (p.defended ? ' · 今日已守擂（练习模式）' : p.inChallenge && p.stage1Won ? ' · 第 1 场已赢' : ''), W / 2, 262, 13);
  var lim = s2.allowedHorns ? s2.allowedHorns.map(function (id) { return D.horns.filter(function (h) { return h.id === id; })[0].name; }).join(' / ') : '不限';
  text('第 2 场限定角形：' + lim + ' · 你的：' + D.horns[st.idx.horn].name, W / 2, 285, 12, 'muted');
  if (AR.msg) text(AR.msg, W / 2, 325, 13, 'warn');
  var y = 342, hw = (W - 2 * P - 12) / 2;
  btn(P, y, hw, 48, '挑战第 1 场', function () { startArenaStage(1); }, 'main', 19);
  btn(P + hw + 12, y, hw, 48, '挑战第 2 场', function () { startArenaStage(2); }, p.defended || (p.inChallenge && p.stage1Won) ? 'main' : 'gray', 19);
  if (s2.allowedHorns) s2.allowedHorns.forEach(function (id, i, arr) {
    var hi = D.horns.map(function (h) { return h.id; }).indexOf(id), bw = (W - 2 * P - (arr.length - 1) * 10) / arr.length;
    btn(P + i * (bw + 10), y + 62, bw, 32, '换' + D.horns[hi].name + (st.look.horn === id ? '✔' : ''), function () { st.idx.horn = hi; syncLook(); }, st.look.horn === id ? 'yellow' : 'white', 14);
  });
  btn(P, y + 106, hw, 38, '📺 看广告 +1 次', function () { // 第一期浏览器模拟：正式版用 wx.createRewardedVideoAd，完整播放才发放
    if (p.tries.adGranted >= p.tries.adMax) { AR.msg = '今日广告次数已达上限'; return; }
    p.tries.adGranted++; A.saveProgress(p); AR.msg = '（模拟）广告播放完成，挑战 +1';
  }, 'blue', 14);
  btn(P + hw + 12, y + 106, hw, 38, '🚩 选择牧场', function () { st.scene = 'faction'; }, 'orange', 14);
  // 牧场榜：胶囊行 + 左侧彩色名次块，只显示牧场名（本地演示数据；正式版按人均分由云函数计算）
  var AL = LY.arena; var ly = y + AL.rankY; text('本周牧场榜 · 人均分（本地演示）', W / 2, ly, 12, 'muted');
  var rows = A.FACTIONS.factions.map(function (f) { return { f: f, v: p.factionScores[f.id] || 0 }; }).sort(function (a, b) { return b.v - a.v; }).slice(0, 3);
  var RC = [TH.colors.yellow, '#C9CCC4', TH.colors.orange];
  rows.forEach(function (r, i) { var ry = ly + AL.rowY0 + i * AL.rowStep, rx = P + 20, rw = W - 2 * P - 40;
    UI.sticker(ctx, rx, ry, rw, AL.rowH, AL.rowH / 2, '#FFFFFF', 0, null, 2); UI.sticker(ctx, rx, ry, 34, AL.rowH, AL.rowH / 2, RC[i], 0, null, 2);
    text('' + (i + 1), rx + 17, ry + AL.rowH / 2, 13); text(A.factionLabel(r.f), rx + 46, ry + AL.rowH / 2, 13, 'ink', 'left'); text('' + r.v, rx + rw - 12, ry + AL.rowH / 2, 13, 'ink', 'right'); });
  if (f) text('你：' + f.name + '的一只' + D.horns[st.idx.horn].name + '羊', W / 2, ly + AL.youY, 11, 'muted');
  btn(W / 2 - AL.backW / 2, H - AL.backBottom, AL.backW, AL.backH, '返回', function () { st.scene = 'custom'; }, 'gray', 16);
  text('适度游戏益脑，沉迷游戏伤身', W / 2, H - AL.footBottom, 10, 'muted');
}
// ---------- 顶顶乐 ----------
var DG = null, DP = null;
function openDdl() { DP = DDL.loadProg(); st.scene = 'ddlSelect'; }
function enterDdl(id) {
  if (!DDL.unlocked(DP, id)) return;
  DG = DDL.startLevel(id, st.look.horn); st.scene = 'ddl';
}
function updateAimFromDrag() {
  if (!DG || !DG.drag) return;
  var dx = DG._tx - DG.drag.x0, dy = DG.drag.y0 - DG._ty; // 屏幕上为 +y 角度
  DG.aimAngle = Math.atan2(dy, dx) * 180 / Math.PI; if (DG.aimAngle < 0) DG.aimAngle += 360;
}
function drawDdlSelect() {
  bg(); text('顶顶乐', W / 2, 46, 38, 'title'); pill('把目标推进草堆 · 青草币 ' + (DP.grass || 0), W / 2, 86, false, 13);
  DDL.DATA.levels.forEach(function (lv, i) {
    var col = i % 2, row = Math.floor(i / 2), bw = (W - 2 * LY.pad - 14) / 2, x = LY.pad + col * (bw + 14), y = 110 + row * 92;
    var stars = DDL.bestStars(DP, lv.id), lock = !DDL.unlocked(DP, lv.id);
    var lab = lv.id + '. ' + lv.name;
    btn(x, y, bw, 76, '', function () { if (!lock) enterDdl(lv.id); }, lock ? 'gray' : 'white');
    st.buttons[st.buttons.length - 1].label = lab; // 命中区/标签与旧版一致，文字分两行绘制
    text(lab, x + bw / 2, y + 26, 16, lock ? 'muted' : 'ink');
    if (lock) text('🔒', x + bw / 2, y + 54, 16); else stars3(x + bw / 2, y + 54, stars, 9);
  });
  btn(W / 2 - 55, H - 56, 110, 38, '返回', function () { st.scene = 'custom'; }, 'gray', 16);
}
function stars3(cx, cy, n, r) { for (var i = 0; i < 3; i++) star(cx + (i - 1) * r * 2.5, cy, r, i < n); }
function star(x, y, r, on) { ctx.save(); ctx.beginPath(); for (var k = 0; k < 10; k++) { var a = -Math.PI / 2 + k * Math.PI / 5, rr = k % 2 ? r * 0.45 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
  ctx.closePath(); ctx.fillStyle = on ? TH.colors.yellow : '#FFFFFF'; ctx.fill(); ctx.strokeStyle = TH.colors.ink; ctx.lineWidth = 1.8; ctx.lineJoin = 'round'; ctx.stroke(); ctx.restore(); }
function drawObj(b) {
  if (!b.alive) return;
  var F = TH.field, col = F.objects[b.type] || F.fallback;
  if (b.inHay) return;
  ctx.beginPath(); ctx.fillStyle = col; ctx.strokeStyle = F.line; ctx.lineWidth = F.lineW;
  ctx.arc(b.x, b.y, b.r, 0, 7); ctx.fill(); ctx.stroke();
  if (b.target) star(b.x, b.y, Math.min(9, b.r * 0.7), true);
  if (b.type === 'sheep') text(b.awake ? '!' : 'z', b.x, b.y - b.r - 8, 13);
  if (b.type === 'rock') text('石', b.x, b.y, 11, 'white');
}
function GY() { return H * 0.72 - 40; }
function updateDdl() {
  var sh = DG.shot, n0 = sh ? sh.ev.length : 0;
  if (DG.phase === 'flying') DDL.tick(DG);
  if (sh) sh.ev.slice(n0).forEach(function (e) { var b = sh.B.filter(function (o) { return o.id === e[1]; })[0]; if (b) FX.ev('ddl', { k: e[0], x: b.x, y: b.y }); }); // 只读事件
  if (sh && DG.phase === 'result') FX.ev('win', { x: W / 2, y: H * 0.3 });
  if (DG.phase === 'aim') { DG.meter += 0.018 * DG.dir; if (DG.meter > 1 || DG.meter < 0) DG.dir *= -1; DG.aimPower = Math.max(0, Math.min(1, DG.meter)); }
}
function drawDdl() {
  var F = TH.field;
  // 场地：草绿底 + 小草；顶栏白色贴纸面板
  UI.drawBg(ctx, W, H);
  UI.sticker(ctx, -6, -6, W + 12, 64, 14, '#FFFFFF', 3, null, 2);
  text(DG.lv.id + '. ' + DG.lv.name, W / 2, 20, 17);
  text('顶撞 ' + DG.shots + '/' + DG.max + ' · ' + DG.lv.teach, W / 2, 42, 11, 'muted');
  var sk = FX.enabled ? FX.shakeOff() : [0, 0]; ctx.save(); ctx.translate(sk[0], sk[1]); // 屏震只作用于场景层（顶栏/按钮不抖）
  // 草堆
  DG.lv.hays.forEach(function (h) {
    ctx.save(); ctx.globalAlpha = F.hayAlpha; ctx.fillStyle = F.hay; ctx.beginPath(); ctx.arc(h.x, h.y, h.r, 0, 7); ctx.fill(); ctx.restore();
    ctx.strokeStyle = F.line; ctx.lineWidth = F.lineW; ctx.setLineDash([5, 4]); ctx.beginPath(); ctx.arc(h.x, h.y, h.r, 0, 7); ctx.stroke(); ctx.setLineDash([]);
    text('草堆', h.x, h.y, 12);
  });
  DG.state.forEach(drawObj);
  if (FX.enabled) FX.drawScene(ctx); ctx.restore();
  if (DG.msg) pill(DG.msg, W / 2, H - TH.field.msgBottom, true, 13);
  var y0 = H - 130;
  if (DG.phase === 'aim') {
    text('拖动瞄准 · 角度 ' + Math.round(DG.aimAngle) + '°', W / 2, y0 + 2, 13);
    UI.drawMeter(ctx, 40, y0 + 14, W - 80, DG.meter, 0.85, 1);
    btn(W / 2 - 70, y0 + 44, 140, 46, '顶！', function () { DDL.fire(DG); }, 'main', 24);
    btn(16, y0 + 48, 70, 40, '重开', function () { enterDdl(DG.lv.id); }, 'white', 16);
    btn(W - 86, y0 + 48, 70, 40, '选关', function () { st.scene = 'ddlSelect'; }, 'white', 16);
  } else if (DG.phase === 'fail') {
    text(DG.msg || '失败', W / 2, y0, 16, 'warn');
    btn(20, y0 + 30, W / 2 - 30, 46, '免费重开', function () { enterDdl(DG.lv.id); }, 'main', 18);
    btn(W / 2 + 10, y0 + 30, W / 2 - 30, 46, '📺 +1次顶撞', function () { DDL.grantExtra(DG); }, 'blue', 16);
  } else if (DG.phase === 'result') {
    st.scene = 'ddlResult';
  }
  // 玩家羊 / 瞄准：最后绘制，压在控件之上（起点 y≈600 与底部控件重叠）
  ctx.save(); ctx.translate(sk[0], sk[1]);
  // 玩家羊 / 瞄准
  if (DG.phase === 'aim' || DG.phase === 'flying') {
    var gx = DG.phase === 'flying' ? DG.goatPos.x : DG.lv.start.x, gy = DG.phase === 'flying' ? DG.goatPos.y : DG.lv.start.y;
    G.drawShadow(ctx, gx, gy, 0.55, 0);
    // 俯视用圆代替侧视羊，保留简易感（白底黑描边 + 角色方向）
    ctx.fillStyle = st.look.woolColor; ctx.strokeStyle = F.line; ctx.lineWidth = F.lineW; ctx.beginPath(); ctx.arc(gx, gy, F.goatR, 0, 7); ctx.fill(); ctx.stroke();
    var a = DG.aimAngle * Math.PI / 180;
    if (DG.phase === 'aim') {
      // 瞄准线：红色虚线 + 黑描边箭头
      ctx.lineCap = 'round'; ctx.strokeStyle = F.line; ctx.lineWidth = F.aimW + 2; ctx.setLineDash(F.aimDash);
      ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(a) * F.aimLen, gy - Math.sin(a) * F.aimLen); ctx.stroke();
      ctx.strokeStyle = F.aim; ctx.lineWidth = F.aimW; ctx.stroke(); ctx.setLineDash([]);
      var ex = gx + Math.cos(a) * F.aimLen, ey = gy - Math.sin(a) * F.aimLen; ctx.fillStyle = F.aim; ctx.beginPath(); ctx.arc(ex, ey, 5, 0, 7); ctx.fill(); ctx.lineWidth = 1.5; ctx.strokeStyle = F.line; ctx.stroke();
      if (DG.hint && DG.lv.solution[0]) {
        var ha = DG.lv.solution[0].angle * Math.PI / 180;
        ctx.strokeStyle = F.hint; ctx.lineWidth = F.aimW - 1; ctx.setLineDash([4, 5]);
        ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(ha) * F.hintLen, gy - Math.sin(ha) * F.hintLen); ctx.stroke(); ctx.setLineDash([]);
      }
      ctx.lineCap = 'butt';
    }
    ctx.strokeStyle = st.look.hornColor; ctx.lineWidth = F.hornW; ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(a) * 22, gy - Math.sin(a) * 22); ctx.stroke();
  }
  ctx.restore();
  if (DG.phase === 'aim') {
    btn(W - 88, 15, 78, 28, '📺 瞄准线', function () { DDL.grantHint(DG); }, 'blue', 12);
  }
}
function drawDdlResult() {
  var R = LY.result;
  if (DG._reward == null) { DG._reward = DDL.onClear(DP, A.dateKeyAt(now()), DG); }
  bg(); UI.dim(ctx, W, H); panel(R.cardX, R.cardY - 20, W - 2 * R.cardX, R.cardH + 70);
  text('过 关 !', W / 2, R.bannerY - 20, 44, 'banner');
  stars3(W / 2, R.cardY + 38, DG.stars, 15);
  G.drawShadow(ctx, W / 2, R.goatY + 4, 1.1, 0); G.drawGoatArt(ctx, W / 2, R.goatY + 4, 1.1, st.look, 1, 0);
  text('用了 ' + DG.shots + ' 次顶撞（上限 ' + DG.lv.maxShots + '）', W / 2, R.lineY, 15);
  text(DG._reward ? ('青草币 +' + DG._reward) : '今日奖励次数已满，继续玩不奖励', W / 2, R.subY, 13, DG._reward ? 'accent' : 'muted');
  var next = DDL.levelById(DG.lv.id + 1), by = R.btnY - 40;
  if (next) btn(W / 2 - R.btnW / 2, by, R.btnW, R.btnH, '下一关', function () { enterDdl(next.id); }, 'main', 23);
  btn(W / 2 - 115, by + 66, 105, 40, '选关', function () { st.scene = 'ddlSelect'; }, 'yellow', 16);
  btn(W / 2 + 10, by + 66, 105, 40, '返回首页', function () { st.scene = 'custom'; }, 'blue', 16);
}
// 固定时间步：按真实经过时间累加，每步 STEP=1/60s 跑一次 update；单帧最多补 MAX_STEPS 步（防螺旋死亡），渲染每帧一次。
// 无时间戳调用（回归脚本 raf()）= 恰好 1 步，与 v2 基准逐帧一致。
var STEP = 1000 / 60, MAX_STEPS = 5, clock = { last: null, acc: 0, steps: 0, frames: 0, dropped: 0 };
function update() {
  if (st.scene === 'battle') updateBattle(); else if (st.scene === 'ddl' && DG) updateDdl();
  clock.steps++;
}
function loop(ts) {
  if (typeof ts !== 'number') { update(); FX.step(clock.steps * STEP); }
  else {
    if (clock.last === null) clock.last = ts;
    clock.acc += Math.max(0, ts - clock.last); clock.last = ts;
    var n = 0; while (clock.acc >= STEP && n < MAX_STEPS) { update(); clock.acc -= STEP; n++; }
    if (n === MAX_STEPS && clock.acc >= STEP) { clock.dropped += Math.floor(clock.acc / STEP); clock.acc %= STEP; }
  }
  if (typeof ts === 'number') FX.step(ts);
  clock.frames++;
  UI.update(typeof ts === 'number' ? ts : clock.steps * STEP, st.scene);
  render(); UI.vignette(ctx, W, H); if (FX.enabled) FX.drawFlash(ctx, W, H); // HUD 不抖；场景层在各 draw 内平移
  requestAnimationFrame(loop);
}
function render() { st.buttons = [];
  if (st.scene === 'custom') drawCustom(); else if (st.scene === 'battle') drawBattle();
  else if (st.scene === 'arena') drawArena(); else if (st.scene === 'faction') drawFaction();
  else if (st.scene === 'arenaResult') drawArenaResult();
  else if (st.scene === 'ddlSelect') drawDdlSelect(); else if (st.scene === 'ddl') drawDdl(); else if (st.scene === 'ddlResult') drawDdlResult();
  else drawOver();
}
wx.onTouchStart(function (e) { var t = e.touches[0], x = t.clientX, y = t.clientY;
  if (st.scene === 'ddl' && DG && DG.phase === 'aim') {
    for (var i = st.buttons.length - 1; i >= 0; i--) { var b = st.buttons[i]; if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) { b.cb(); return; } }
    if (y > 60 && y < H - 140) { DG.drag = { x0: DG.lv.start.x, y0: DG.lv.start.y }; DG._tx = x; DG._ty = y; updateAimFromDrag(); return; }
  }
  for (var i = st.buttons.length - 1; i >= 0; i--) { var b = st.buttons[i]; if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) { b.cb(); return; } }
});
if (typeof document !== 'undefined') {
  document.addEventListener('mousemove', function (e) {
    if (!(st.scene === 'ddl' && DG && DG.drag)) return;
    var r = canvas.getBoundingClientRect(); DG._tx = e.clientX - r.left; DG._ty = e.clientY - r.top; updateAimFromDrag();
  });
  document.addEventListener('mouseup', function () { if (DG) DG.drag = null; });
}
module.exports = { QUIZ_ENABLED: QUIZ_ENABLED, st: st, G: G, D: D, get B() { return B; }, get AR() { return AR; }, get DG() { return DG; }, A: A, DDL: DDL,
  startMatch: startMatch, answer: answer, jump: jump, makeGuess: makeGuess,
  openArena: openArena, startArenaStage: startArenaStage, chooseFaction: chooseFaction, setNow: function (ms) { nowOverride = ms; },
  FX: FX, UI: UI, clock: clock, STEP: STEP, MAX_STEPS: MAX_STEPS,
  openDdl: openDdl, enterDdl: enterDdl, fireDdl: function () { if (DG) DDL.fire(DG); } };
loop();
