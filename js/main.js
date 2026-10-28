var D = require('./data.js'), G = require('./goat.js'), A = require('./arena.js'), DDL = require('./ddl.js');
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
function btn(x, y, w, h, label, cb, color) {
  ctx.fillStyle = color || '#ffb347'; roundRect(x, y, w, h, 12); ctx.fill();
  ctx.fillStyle = '#4a2c00'; ctx.font = 'bold 16px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, x + w / 2, y + h / 2); st.buttons.push({ x: x, y: y, w: w, h: h, cb: cb, label: label });
}
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function text(s, x, y, size, c) { ctx.fillStyle = c || '#333'; ctx.font = 'bold ' + (size || 16) + 'px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, x, y); }
function bg() { var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#bfe9ff'); g.addColorStop(1, '#fff6d8');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.fillStyle = '#8fd17a'; ctx.fillRect(0, H * 0.72, W, H * 0.28); }

// ---------- 定制界面 ----------
function cycle(k, arr, n) { st.idx[k] = (st.idx[k] + n + arr.length) % arr.length; }
function syncLook() { var i = st.idx; st.look = { wool: D.wools[i.wool].id, woolColor: D.woolColors[i.wc], horn: D.horns[i.horn].id, hornColor: D.hornColors[i.hc] }; }
function drawCustom() {
  bg(); text('🐐 咩咩顶角王', W / 2, 50, 26, '#c05a00'); text('打造你的山羊', W / 2, 82, 15, '#666');
  G.drawShadow(ctx, W / 2 - 10, H * 0.32, 2, 0); G.drawGoatArt(ctx, W / 2 - 10, H * 0.32, 2, st.look, 1, 0);
  var s = stats(st.look), h = D.horns[st.idx.horn];
  text('体力 ' + s.hp + '  速度 ' + (s.spd >= 0 ? '+' : '') + s.spd + '  力量 +' + s.pow, W / 2, H * 0.47, 14, '#444');
  text(h.name + '：' + h.tip, W / 2, H * 0.5, 13, '#a05000');
  var rows = [['羊毛', 'wool', D.wools, D.wools[st.idx.wool].name], ['毛色', 'wc', D.woolColors, ''], ['角形', 'horn', D.horns, h.name], ['角色', 'hc', D.hornColors, '']];
  rows.forEach(function (r, i) {
    var y = H * 0.55 + i * 48;
    btn(20, y, 44, 38, '◀', function () { cycle(r[1], r[2], -1); syncLook(); });
    btn(W - 64, y, 44, 38, '▶', function () { cycle(r[1], r[2], 1); syncLook(); });
    text(r[0] + (r[3] ? '：' + r[3] : ''), W / 2 - (r[3] ? 0 : 20), y + 19, 16);
    if (!r[3]) { ctx.fillStyle = r[2][st.idx[r[1]]]; ctx.beginPath(); ctx.arc(W / 2 + 30, y + 19, 12, 0, 7); ctx.fill(); ctx.strokeStyle = '#555'; ctx.stroke(); }
  });
  btn(16, H - 70, (W - 48) / 3, 48, '开始对战', function () { startMatch(); }, '#7bd36b');
  btn(16 + (W - 48) / 3 + 8, H - 70, (W - 48) / 3, 48, '🏆 每日擂主', openArena, '#ffd36b');
  btn(16 + 2 * ((W - 48) / 3 + 8), H - 70, (W - 48) / 3, 48, '🎮 顶顶乐', openDdl, '#cfe8ff');
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
  B.p.vy = -9; B.e.vy = -9; B.phase = 'air'; B.t = 0;
}
function clash() {
  var ps = stats(st.look), es = stats(B.ai);
  var pp = 20 + ps.pow + B.p.bonus + B.timing * 30 + ps.spd * 0.3;
  if (B.arena) { // 擂主战：AI 参数 + 角力推理倍率（design/03 接入示例）
    var ai = B.stageCfg.ai, eT = Math.random() < ai.timingHit ? 1 : Math.random() * 0.7;
    var ep = 20 + es.pow + ai.powBonus + eT * 30 + es.spd * 0.3;
    B.e.readHit = A.REASONING_ENABLED && Math.random() < ai.readAcc;
    var m = A.multipliers({ pWin: ps.win, eWin: es.win, pAng: B.p.ang, eAng: B.e.ang, guess: B.p.guess, eReadHit: B.e.readHit });
    pp *= m.mulP; ep *= m.mulE;
    if (A.REASONING_ENABLED) B.reveal = '对手真实角度：' + ANGN[B.e.ang] + (m.hit ? ' ✔预判命中' : ' ✘未命中') + (B.e.readHit ? ' | 对手看穿了你' : '');
    else if (B.stageCfg.angleReveal === 'hidden') B.reveal = '对手角度揭晓：' + ANGN[B.e.ang];
    else B.reveal = '';
  } else {
    var ep = 20 + es.pow + (Math.random() * 25 + 5) + es.spd * 0.3;
    // 角形 vs 角度 石头剪刀布：自己的角形克制对方选择的角度时 x1.3
    if (ps.win === B.e.ang) pp *= 1.3; if (es.win === B.p.ang) ep *= 1.3;
  }
  var d = Math.round(Math.abs(pp - ep));
  if (pp >= ep) { B.e.hp -= d + 8; B.msg = '咚！你赢了这次对撞，造成 ' + (d + 8); }
  else { B.p.hp -= d + 8; B.msg = '哎呀！被顶了 ' + (d + 8); }
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
function drawBattle() {
  bg(); var gy = H * 0.72 - 40;
  text('第 ' + B.round + ' 回合  (三局两胜)  ' + B.wins[0] + ' : ' + B.wins[1], W / 2, 30, 16);
  hpBar(20, 50, B.p.hp, stats(st.look).hp, '你'); hpBar(W / 2 + 10, 50, B.e.hp, eMaxHp(), B.arena ? '擂主·' + B.arena.cfg.name : '电脑');
  if (B.arena) text('每日擂主 第 ' + B.arena.stage + ' 场' + (A.REASONING_ENABLED ? ' · 线索 Lv' + B.stageCfg.clueLv : ''), W / 2, 112, 12, '#666');
  [B.p, B.e].forEach(function (g) { if (B.phase === 'air') { g.vy += 0.45; g.y += g.vy; } });
  if (B.phase === 'air') { B.p.x += 4; B.e.x -= 4; if (B.p.x >= W / 2 - 50) clash(); }
  if (B.phase === 'result' && B.t < 20) { B.p.x -= 3; B.e.x += 3; }
  if (B.phase === 'result') { B.p.y = Math.min(0, B.p.y + 4); B.e.y = B.p.y; if (B.p.x < W * 0.25) B.p.x = W * 0.25; }
  B.t++;
  G.drawShadow(ctx, B.p.x, gy, 1.1, -B.p.y); G.drawShadow(ctx, B.e.x, gy, 1.1, -B.e.y);
  var pose = B.phase === 'air' ? 'jump' : (B.phase === 'result' && B.t < 25) ? 'clash' : 'idle';
  G.drawGoatArt(ctx, B.p.x, gy + B.p.y, 1.1, st.look, 1, 0, pose);
  G.drawGoatArt(ctx, B.e.x, gy + B.e.y, 1.1, B.ai, -1, 0, pose);
  if (B.phase === 'result' && B.t < 25) text('💥', W / 2, gy - 40, 40);
  text(B.msg, W / 2, 90, 15, '#a03000');
  var y0 = H * 0.76;
  if (B.phase === 'quiz' && QUIZ_ENABLED) {
    text(B.quiz.q, W / 2, y0, 20); B.quiz.opts.forEach(function (o, i) { btn(W / 2 - 130 + i * 90, y0 + 25, 80, 44, '' + o, function () { answer(o); }); });
    text('3 秒内答对 +20，答对 +10', W / 2, y0 + 90, 12, '#666');
  } else if (B.phase === 'observe' && A.REASONING_ENABLED) {
    var left = B.obs.observeSec - (Date.now() - B.obs.t0) / 1000;
    if (left <= 0) { makeGuess(null); return; }
    ctx.fillStyle = 'rgba(255,255,255,0.85)'; roundRect(16, 128, W - 32, 40 + B.obs.clues.length * 24, 10); ctx.fill();
    text('对手摆出架势「' + B.e.stance.name + '」 观察 ' + left.toFixed(1) + 's', W / 2, 146, 14, '#a05000');
    B.obs.clues.forEach(function (c, i) { text('👁 ' + c.text, W / 2, 172 + i * 24, 14, '#333'); });
    text('预判对手真正的角度：', W / 2, y0 - 5, 15);
    ANG.forEach(function (a, i) { btn(W / 2 - 130 + i * 90, y0 + 12, 80, 40, ANGN[a] + '角度', function () { makeGuess(a); }, '#cfe8ff'); });
    text('提示：有的线索是假动作，有的线索永远不会骗人', W / 2, y0 + 72, 12, '#666');
  } else if (B.phase === 'charge') {
    B.meter += 0.018 * B.dir; if (B.meter > 1 || B.meter < 0) B.dir *= -1;
    if (B.arena && A.REASONING_ENABLED) text('你的预判：' + (B.p.guess ? ANGN[B.p.guess] + '角度' : '无') + ' | 选择你的角度', W / 2, y0 - 5, 14);
    else if (B.arena && B.stageCfg.angleReveal === 'hidden') text('对手角度隐藏 | 选择你的角度', W / 2, y0 - 5, 14);
    else text('对手架势：' + ANGN[B.e.ang] + '角度 | 选择你的角度', W / 2, y0 - 5, 14);
    ANG.forEach(function (a, i) { btn(W / 2 - 130 + i * 90, y0 + 12, 80, 36, ANGN[a] + (B.p.ang === a ? '✔' : ''), function () { B.p.ang = a; }, B.p.ang === a ? '#ffd36b' : '#ffe9b8'); });
    ctx.fillStyle = '#ddd'; ctx.fillRect(40, y0 + 60, W - 80, 16); ctx.fillStyle = '#7bd36b'; ctx.fillRect(40 + (W - 80) * 0.72, y0 + 60, (W - 80) * 0.16, 16);
    ctx.fillStyle = '#e33'; ctx.fillRect(40 + (W - 80) * B.meter - 3, y0 + 55, 6, 26);
    btn(W / 2 - 70, y0 + 92, 140, 44, '起跳顶角！', jump, '#ff8a65');
  }
  if (B.phase === 'result' && B.arena && B.reveal) text(B.reveal, W / 2, y0 + 10, 13, '#2a5ea0');
  if (B.phase === 'result' && B.t > 30) btn(W / 2 - 60, y0 + 40, 120, 44, B.roundEnd >= 0 ? '下一回合' : '继续', next);
}
function hpBar(x, y, hp, max, n) { var w = W / 2 - 30; ctx.fillStyle = '#eee'; ctx.fillRect(x, y, w, 14);
  ctx.fillStyle = hp > max * 0.3 ? '#5cc85c' : '#e55'; ctx.fillRect(x, y, w * Math.max(0, hp) / max, 14); text(n + ' ' + Math.max(0, hp), x + w / 2, y + 7, 11); }
function drawOver() {
  bg(); var win = B.wins[0] === 2; text(win ? '🏆 你是顶角王！' : '😢 再接再厉', W / 2, H * 0.3, 28, '#c05a00');
  text(B.wins[0] + ' : ' + B.wins[1], W / 2, H * 0.38, 22);
  G.drawShadow(ctx, W / 2, H * 0.55, 1.8, 0); G.drawGoatArt(ctx, W / 2, H * 0.55, 1.8, st.look, 1, 0);
  btn(W / 2 - 80, H * 0.75, 160, 46, '再来一局', function () { startMatch(); }); btn(W / 2 - 80, H * 0.75 + 60, 160, 46, '换装', function () { st.scene = 'custom'; });
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
  bg(); text('选择你的牧场', W / 2, 50, 24, '#c05a00');
  text('按你觉得的家乡大区选，只带来荣誉和外观', W / 2, 82, 13, '#666');
  text('不选也能正常玩，只是不计阵营分', W / 2, 102, 13, '#666');
  var fs = A.FACTIONS.factions, bw = (W - 60) / 2;
  fs.forEach(function (f, i) { // 牧场名由 factionLabel 生成，以后加省份只改这一处
    var x = 20 + (i % 2) * (bw + 20), y = 130 + Math.floor(i / 2) * 62, cur = AR.p.faction === f.id;
    btn(x, y, bw, 50, A.factionLabel(f) + (cur ? ' ✔' : ''), function () { chooseFaction(f.id); }, cur ? '#ffd36b' : '#ffe9b8');
  });
  btn(W / 2 - 80, H - 90, 160, 46, '稍后再选', function () { chooseFaction(null); }, '#dddddd');
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
  var win = B.wins[0] === 2;
  var info = { hpPct: Math.max(0, B.p.hp) / stats(st.look).hp, hits: B.hits, guesses: B.guesses,
    timingAvg: B.jumps ? B.timingSum / B.jumps : 0, roundsLost: B.wins[1], timings: B.timings.slice() };
  var r = A.onStageEnd(AR.p, B.arena.stage, win, info, AR.champ.cfg); A.saveProgress(AR.p);
  AR.last = { stage: B.arena.stage, win: win, info: info, msgs: r.msgs }; st.scene = 'arenaResult';
}
function drawArenaResult() {
  bg(); var L = AR.last;
  text(L.win ? '🏆 第 ' + L.stage + ' 场胜利！' : '😢 第 ' + L.stage + ' 场惜败', W / 2, 70, 26, '#c05a00');
  if (A.REASONING_ENABLED) text('预判命中 ' + L.info.hits + ' / ' + L.info.guesses, W / 2, 110, 15);
  else text('剩余体力 ' + Math.round(L.info.hpPct * 100) + '%  · 时机 ' + (L.info.timingAvg != null ? (L.info.timingAvg * 100).toFixed(0) + '%' : '-'), W / 2, 110, 14);
  G.drawShadow(ctx, W / 2, H * 0.36, 1.6, 0); G.drawGoatArt(ctx, W / 2, H * 0.36, 1.6, st.look, 1, 0);
  L.msgs.forEach(function (m, i) { text(m, W / 2, H * 0.5 + i * 26, 15, '#a03000'); });
  if (L.win && L.stage === 1 && AR.p.inChallenge) btn(W / 2 - 90, H * 0.72, 180, 46, '挑战第 2 场！', function () { st.scene = 'arena'; startArenaStage(2); }, '#ff8a65');
  btn(W / 2 - 80, H * 0.72 + 60, 160, 46, '返回擂台', function () { st.scene = 'arena'; });
}
function drawArena() {
  bg(); var p = AR.p, cfg = AR.champ.cfg, s2 = cfg.stages[1];
  text('🏆 每日擂主 · ' + AR.dateKey, W / 2, 34, 20, '#c05a00');
  var f = p.faction ? A.factionById(p.faction) : null;
  text((f ? A.factionLabel(f) : '未选牧场') + ' · 青草币 ' + p.grass + ' · 守擂 ' + p.defendDays + ' 天', W / 2, 60, 12, '#555');
  G.drawShadow(ctx, W * 0.7, H * 0.24, 1.0, 0); G.drawGoatArt(ctx, W * 0.7, H * 0.24, 1.0, cfg.look, -1, 0);
  G.drawShadow(ctx, W * 0.28, H * 0.24, 1.0, 0); G.drawGoatArt(ctx, W * 0.28, H * 0.24, 1.0, st.look, 1, 0);
  text('今日擂主：' + cfg.name + (AR.champ.procedural ? '（轮换）' : ''), W / 2, H * 0.33, 17);
  text('剩余挑战 ' + A.triesLeft(p) + ' 次' + (p.defended ? ' · 今日已守擂（练习模式）' : p.inChallenge && p.stage1Won ? ' · 第 1 场已赢' : ''), W / 2, H * 0.37, 13, '#444');
  var lim = s2.allowedHorns ? s2.allowedHorns.map(function (id) { return D.horns.filter(function (h) { return h.id === id; })[0].name; }).join(' / ') : '不限';
  text('第 2 场限定角形：' + lim + ' · 你的角形：' + D.horns[st.idx.horn].name, W / 2, H * 0.405, 12, '#a05000');
  if (AR.msg) text(AR.msg, W / 2, H * 0.44, 13, '#c03000');
  var y = H * 0.47;
  btn(20, y, W / 2 - 30, 44, '挑战第 1 场', function () { startArenaStage(1); }, '#7bd36b');
  btn(W / 2 + 10, y, W / 2 - 30, 44, '挑战第 2 场', function () { startArenaStage(2); }, p.defended || (p.inChallenge && p.stage1Won) ? '#ff8a65' : '#dddddd');
  if (s2.allowedHorns) s2.allowedHorns.forEach(function (id, i, arr) {
    var hi = D.horns.map(function (h) { return h.id; }).indexOf(id), bw = (W - 40 - (arr.length - 1) * 10) / arr.length;
    btn(20 + i * (bw + 10), y + 52, bw, 34, '换' + D.horns[hi].name + (st.look.horn === id ? '✔' : ''), function () { st.idx.horn = hi; syncLook(); }, '#ffe9b8');
  });
  btn(20, y + 94, W / 2 - 30, 38, '📺 看广告 +1 次', function () { // 第一期浏览器模拟：正式版用 wx.createRewardedVideoAd，完整播放才发放
    if (p.tries.adGranted >= p.tries.adMax) { AR.msg = '今日广告次数已达上限'; return; }
    p.tries.adGranted++; A.saveProgress(p); AR.msg = '（模拟）广告播放完成，挑战 +1';
  }, '#cfe8ff');
  btn(W / 2 + 10, y + 94, W / 2 - 30, 38, '🚩 选择牧场', function () { st.scene = 'faction'; }, '#cfe8ff');
  // 牧场榜：列表 + 匿名，只显示牧场名（本地演示数据；正式版按人均分由云函数计算）
  text('本周牧场榜（人均分 · 本地演示）', W / 2, y + 150, 13, '#555');
  var rows = A.FACTIONS.factions.map(function (f) { return { f: f, v: p.factionScores[f.id] || 0 }; }).sort(function (a, b) { return b.v - a.v; }).slice(0, 3);
  rows.forEach(function (r, i) { text((i + 1) + '. ' + A.factionLabel(r.f) + '  ' + r.v, W / 2, y + 172 + i * 20, 13, '#333'); });
  if (f) text('你：' + f.name + '的一只' + D.horns[st.idx.horn].name + '羊', W / 2, y + 236, 12, '#888');
  btn(W / 2 - 60, H - 52, 120, 40, '返回', function () { st.scene = 'custom'; }, '#dddddd');
  text('适度游戏益脑，沉迷游戏伤身', W / 2, H - 6, 10, '#888');
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
  bg(); text('🎮 顶顶乐', W / 2, 40, 24, '#c05a00'); text('把目标推进草堆 · 青草币 ' + (DP.grass || 0), W / 2, 68, 13, '#555');
  DDL.DATA.levels.forEach(function (lv, i) {
    var col = i % 2, row = Math.floor(i / 2), bw = (W - 48) / 2, x = 16 + col * (bw + 16), y = 95 + row * 95;
    var stars = DDL.bestStars(DP, lv.id), lock = !DDL.unlocked(DP, lv.id);
    var lab = lv.id + '. ' + lv.name;
    btn(x, y, bw, 80, lab, function () { if (!lock) enterDdl(lv.id); }, lock ? '#dddddd' : '#ffe9b8');
    // 覆盖绘制星级（按钮已画了名字）
    text(lock ? '🔒' : '★'.repeat(stars) + '☆'.repeat(3 - stars), x + bw / 2, y + 54, 14, '#a05000');
  });
  btn(W / 2 - 60, H - 52, 120, 40, '返回', function () { st.scene = 'custom'; }, '#dddddd');
}
function drawObj(b) {
  if (!b.alive) return;
  var col = { crate: '#c48a4a', fragile: '#e8b070', ball: '#fff', rock: '#777', sheep: '#f0e6d8' }[b.type] || '#ccc';
  if (b.inHay) return;
  ctx.beginPath(); ctx.fillStyle = col; ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 2;
  ctx.arc(b.x, b.y, b.r, 0, 7); ctx.fill(); ctx.stroke();
  if (b.target) { text('★', b.x, b.y, 14, '#ffd700'); }
  if (b.type === 'sheep') text(b.awake ? '!' : 'z', b.x, b.y - b.r - 8, 12, '#666');
  if (b.type === 'rock') text('石', b.x, b.y, 11, '#fff');
}
function drawDdl() {
  // 天空 + 场地
  var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#bfe9ff'); g.addColorStop(1, '#e8f8c8');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#7ec85a'; ctx.fillRect(0, 60, W, H - 60);
  // UI 顶栏
  ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.fillRect(0, 0, W, 60);
  text(DG.lv.id + '. ' + DG.lv.name, W / 2, 22, 16, '#c05a00');
  text('顶撞 ' + DG.shots + '/' + DG.max + '  ·  ' + DG.lv.teach, W / 2, 44, 11, '#555');
  // 草堆
  DG.lv.hays.forEach(function (h) {
    ctx.fillStyle = 'rgba(180,140,40,0.55)'; ctx.beginPath(); ctx.arc(h.x, h.y, h.r, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(120,90,20,0.6)'; ctx.stroke(); text('草', h.x, h.y, 12, '#5a3a00');
  });
  DG.state.forEach(drawObj);
  // 玩家羊 / 瞄准
  if (DG.phase === 'aim' || DG.phase === 'flying') {
    var gx = DG.phase === 'flying' ? DG.goatPos.x : DG.lv.start.x, gy = DG.phase === 'flying' ? DG.goatPos.y : DG.lv.start.y;
    G.drawShadow(ctx, gx, gy, 0.55, 0);
    // 俯视用圆代替侧视羊，保留简易感
    ctx.fillStyle = st.look.woolColor; ctx.beginPath(); ctx.arc(gx, gy, 18, 0, 7); ctx.fill();
    ctx.strokeStyle = st.look.hornColor; ctx.lineWidth = 4; ctx.beginPath();
    var a = DG.aimAngle * Math.PI / 180; ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(a) * 22, gy - Math.sin(a) * 22); ctx.stroke();
    if (DG.phase === 'aim') {
      // 瞄准线
      ctx.strokeStyle = 'rgba(255,80,40,0.7)'; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
      ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(a) * 80, gy - Math.sin(a) * 80); ctx.stroke(); ctx.setLineDash([]);
      if (DG.hint && DG.lv.solution[0]) {
        var ha = DG.lv.solution[0].angle * Math.PI / 180;
        ctx.strokeStyle = 'rgba(40,120,255,0.7)'; ctx.setLineDash([4, 4]);
        ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + Math.cos(ha) * 100, gy - Math.sin(ha) * 100); ctx.stroke(); ctx.setLineDash([]);
      }
    }
  }
  if (DG.phase === 'flying') DDL.tick(DG);
  if (DG.msg) text(DG.msg, W / 2, H - 150, 14, '#a03000');
  var y0 = H - 130;
  if (DG.phase === 'aim') {
    text('拖动瞄准 · 角度 ' + Math.round(DG.aimAngle) + '°', W / 2, y0, 13);
    DG.meter += 0.018 * DG.dir; if (DG.meter > 1 || DG.meter < 0) DG.dir *= -1;
    DG.aimPower = Math.max(0, Math.min(1, DG.meter));
    ctx.fillStyle = '#ddd'; ctx.fillRect(40, y0 + 14, W - 80, 14);
    ctx.fillStyle = '#7bd36b'; ctx.fillRect(40 + (W - 80) * 0.85, y0 + 14, (W - 80) * 0.15, 14); // 提示高力区
    ctx.fillStyle = '#e33'; ctx.fillRect(40 + (W - 80) * DG.meter - 3, y0 + 10, 6, 22);
    btn(W / 2 - 70, y0 + 38, 140, 40, '顶！', function () { DDL.fire(DG); }, '#ff8a65');
    btn(16, y0 + 38, 70, 40, '重开', function () { enterDdl(DG.lv.id); }, '#dddddd');
    btn(W - 86, y0 + 38, 70, 40, '选关', function () { st.scene = 'ddlSelect'; }, '#dddddd');
  } else if (DG.phase === 'fail') {
    text(DG.msg || '失败', W / 2, y0, 16, '#a03000');
    btn(20, y0 + 30, W / 2 - 30, 44, '免费重开', function () { enterDdl(DG.lv.id); }, '#7bd36b');
    btn(W / 2 + 10, y0 + 30, W / 2 - 30, 44, '📺 +1次顶撞', function () { DDL.grantExtra(DG); }, '#cfe8ff');
  } else if (DG.phase === 'result') {
    st.scene = 'ddlResult';
  }
  if (DG.phase === 'aim') {
    btn(16, 8, 90, 28, '📺 瞄准线', function () { DDL.grantHint(DG); }, '#cfe8ff');
  }
}
function drawDdlResult() {
  bg();
  if (DG._reward == null) { DG._reward = DDL.onClear(DP, A.dateKeyAt(now()), DG); }
  text('过关！', W / 2, 80, 28, '#c05a00');
  text('★'.repeat(DG.stars) + '☆'.repeat(3 - DG.stars), W / 2, 120, 30, '#ffb000');
  text('用了 ' + DG.shots + ' 次顶撞（上限 ' + DG.lv.maxShots + '）', W / 2, 160, 15);
  text(DG._reward ? ('青草币 +' + DG._reward) : '今日奖励次数已满，继续玩不奖励', W / 2, 190, 14, '#a05000');
  G.drawShadow(ctx, W / 2, H * 0.45, 1.4, 0); G.drawGoatArt(ctx, W / 2, H * 0.45, 1.4, st.look, 1, 0);
  var next = DDL.levelById(DG.lv.id + 1);
  if (next) btn(W / 2 - 80, H * 0.7, 160, 44, '下一关', function () { enterDdl(next.id); }, '#7bd36b');
  btn(W / 2 - 80, H * 0.7 + 54, 160, 44, '选关', function () { st.scene = 'ddlSelect'; }, '#ffd36b');
  btn(W / 2 - 80, H * 0.7 + 108, 160, 44, '返回首页', function () { st.scene = 'custom'; }, '#dddddd');
}

function loop() { st.buttons = [];
  if (st.scene === 'custom') drawCustom(); else if (st.scene === 'battle') drawBattle();
  else if (st.scene === 'arena') drawArena(); else if (st.scene === 'faction') drawFaction();
  else if (st.scene === 'arenaResult') drawArenaResult();
  else if (st.scene === 'ddlSelect') drawDdlSelect(); else if (st.scene === 'ddl') drawDdl(); else if (st.scene === 'ddlResult') drawDdlResult();
  else drawOver();
  requestAnimationFrame(loop); }
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
  openDdl: openDdl, enterDdl: enterDdl, fireDdl: function () { if (DG) DDL.fire(DG); } };
loop();
