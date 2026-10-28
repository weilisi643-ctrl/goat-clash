// 第一期：角力推理 + 每日擂主 —— 纯逻辑（无绘制），数据来自 design/data/*.json
function loadJSON(p) {
  if (typeof wx !== 'undefined' && wx.getFileSystemManager) return JSON.parse(wx.getFileSystemManager().readFileSync(p, 'utf8'));
  var x = new XMLHttpRequest(); x.open('GET', p, false); x.send(); // 浏览器预览：同步读取（相对 index.html）
  if (x.status && x.status !== 200) throw new Error('load fail ' + p + ' ' + x.status);
  return JSON.parse(x.responseText);
}
var CLUES = loadJSON('design/data/clues.json'), CHAMPS = loadJSON('design/data/champions.v2.json'), FACTIONS = loadJSON('design/data/factions.json');
var D = require('./data.js');
// 角力推理开关：false = 不出观察线索/猜角度环节，不计预判倍率，AI 的 readAcc/counterPick 不生效（线索代码与数据保留）
var REASONING_ENABLED = false;
var ANG = ['low', 'mid', 'high'];
var rnd = Math.random;
function pick(a) { return a[Math.floor(rnd() * a.length)]; }
function hornOf(id) { return D.horns.filter(function (h) { return h.id === id; })[0]; }
function level(lv) { return CLUES.levels.filter(function (l) { return l.lv === lv; })[0] || CLUES.levels[0]; }
function clueAng(c, hornWin) { return c.ang === '$hornWin' ? (hornWin && hornWin !== 'none' ? hornWin : null) : c.ang; }

// 生成线索：返回 [{id,text,ang(实际指向),fake,noise}]
function genClues(trueAng, lv, oppHorn) {
  var L = level(lv), hw = (hornOf(oppHorn) || {}).win;
  var real = CLUES.clues.filter(function (c) { return !c.noise && clueAng(c, hw) !== null; });
  var pool = real.filter(function (c) { return clueAng(c, hw) === trueAng; });
  var out = [], used = {};
  for (var i = 0; i < L.clueCount; i++) {
    var cand = pool.filter(function (c) { return !used[c.id]; }); if (!cand.length) cand = pool;
    var c = pick(cand); used[c.id] = 1;
    var o = { id: c.id, text: c.text, ang: trueAng, fake: false, fakeable: c.fakeable };
    if (c.fakeable && rnd() < L.fakeChance) {
      var f = real.filter(function (x) { return x.fakeable && clueAng(x, hw) !== trueAng; });
      if (f.length) { var fc = pick(f); o = { id: fc.id, text: fc.text, ang: clueAng(fc, hw), fake: true, fakeable: true }; }
    }
    out.push(o);
  }
  if (L.mustHaveTrue && !out.some(function (o) { return !o.fake; })) { // 至少保留一条真线索（优先不可伪装的）
    var t = pool.filter(function (c) { return !c.fakeable; })[0] || pool[0];
    out[0] = { id: t.id, text: t.text, ang: trueAng, fake: false, fakeable: t.fakeable };
  }
  for (var n = 0; n < (L.noise || 0); n++) { var z = CLUES.clues.filter(function (c) { return c.noise; })[0]; if (z) out.push({ id: z.id, text: z.text, ang: null, fake: false, noise: true }); }
  out.sort(function () { return rnd() - .5; });
  return { clues: out, observeSec: L.observeSec, lv: L.lv };
}
function stanceFor(ang, pref) {
  var s = CLUES.stances.filter(function (x) { return x.ang === ang && (!pref || pref.indexOf(x.id) >= 0); });
  if (!s.length) s = CLUES.stances.filter(function (x) { return x.ang === ang; });
  return pick(s);
}
// 倍率（03 文档示例）
function multipliers(o) { // o: {pWin, eWin, pAng, eAng, guess, eReadHit}
  var T = CLUES.tuning;
  if (!REASONING_ENABLED) return { mulP: o.pWin === o.eAng ? T.counterMul : 1, mulE: o.eWin === o.pAng ? T.counterMul : 1, hit: false }; // 只保留原型角形克制
  var mulP = 1, mulE = 1, hit = o.guess != null && o.guess === o.eAng;
  if (o.pWin === o.eAng) mulP *= T.counterMul;
  mulP *= hit ? T.guessMul : T.missMul;
  if (o.eWin === o.pAng && !(hit && T.readCancelsCounter)) mulE *= T.counterMul;
  if (o.eReadHit) mulE *= T.guessMul;
  return { mulP: Math.min(mulP, T.maxMul), mulE: Math.min(mulE, T.maxMul), hit: hit };
}

// ---- 日期 / 擂主 ----
function pad(n) { return (n < 10 ? '0' : '') + n; }
function dateKeyAt(ms) { // 北京时间 05:00 刷新
  var d = new Date(ms + 8 * 3600e3 - CHAMPS.resetHourUTC8 * 3600e3);
  return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
}
function dayDiff(a, b) { return Math.round((Date.parse(b + 'T00:00:00Z') - Date.parse(a + 'T00:00:00Z')) / 864e5); }
function championFor(dateKey) {
  var n = dayDiff(CHAMPS.startDate, dateKey), days = CHAMPS.days;
  if (n < 0) return { cfg: days[0], dayNo: 1, preview: true }; // 开服前：预览第 1 天
  if (n < days.length) return { cfg: days[n], dayNo: n + 1 };
  // fallback procedural：用日期序号做种子，从 7 天配置里确定性地挑一套（同一天所有人一致）
  var seed = (n * 9301 + 49297) % 233280, cfg = days[seed % days.length];
  return { cfg: cfg, dayNo: n + 1, procedural: true };
}

// ---- 进度（本地缓存；正式版由云函数校验） ----
var KEY = 'goat_arena_progress_v1';
var store = {
  get: function () { try { if (typeof wx !== 'undefined' && wx.getStorageSync) return wx.getStorageSync(KEY) || null; if (typeof localStorage !== 'undefined') return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {} return null; },
  set: function (v) { try { if (typeof wx !== 'undefined' && wx.setStorageSync) return wx.setStorageSync(KEY, v); if (typeof localStorage !== 'undefined') localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }
};
function freshDay(p, dateKey) {
  p.dateKey = dateKey; p.tries = { free: CHAMPS.freeTries, used: 0, adGranted: 0, adMax: CHAMPS.adExtraMax };
  p.stage1Won = false; p.stage2Won = false; p.defended = false; p.todayScore = 0; p.inChallenge = false; return p;
}
function loadProgress(dateKey) {
  var p = store.get();
  if (!p) p = { version: 1, uidHash: 'local', faction: null, factionChangedAt: null, factionAsked: false, showProfile: false,
    weekScore: 0, defendDays: 0, titles: [], cards: [], grass: 0, readStats: { guesses: 0, hits: 0 }, history: [], factionScores: {} };
  if (p.dateKey !== dateKey) freshDay(p, dateKey);
  return p;
}
function triesLeft(p) { return p.tries.free + p.tries.adGranted - p.tries.used; }
function canChangeFaction(p, dateKey) { return !p.faction || !p.factionChangedAt || dayDiff(p.factionChangedAt, dateKey) >= FACTIONS.changeCooldownDays; }
function setFaction(p, id, dateKey) { if (p.faction === id) return true; if (!canChangeFaction(p, dateKey)) return false; p.faction = id; p.factionChangedAt = dateKey; return true; }
// 牧场显示：第一期只显示名字；以后要列省份时在这里扩展 opts.withRegions（factions.json 可加 regions 字段）
function factionLabel(f, opts) { var s = f.name; if (opts && opts.withRegions && f.regions && f.regions.length) s += '（' + f.regions.join('、') + '）'; return s; }
function factionById(id) { return FACTIONS.factions.filter(function (f) { return f.id === id; })[0]; }
// 06 新积分：round(8 + 6×timingAvg + 4×hpPct + (二场2:0 ? 2 : 0))，只在二场守擂成功计分
function defendScore(p, info) {
  var S = FACTIONS.score, timingAvg = info.timingAvg || 0, hpPct = info.hpPct || 0;
  var flawless = (info.roundsLost === 0) ? (S.flawlessBonus || 0) : 0;
  var v = S.base + timingAvg * S.timingMul + hpPct * S.hpPctMul + flawless;
  return Math.max(0, Math.round(Math.min(S.dailyCapPerUser - p.todayScore, v)));
}
function onStageEnd(p, stage, win, info, champ) { // info: {hpPct,hits,guesses,timingAvg,roundsLost,timings}
  var r = { msgs: [] };
  if (!p.readStats) p.readStats = { guesses: 0, hits: 0 };
  p.readStats.guesses += info.guesses || 0; p.readStats.hits += info.hits || 0;
  p.history.push({ stage: stage, win: win, hpPct: info.hpPct, hits: info.hits, guesses: info.guesses, timingAvg: info.timingAvg, roundsLost: info.roundsLost });
  if (p.history.length > 30) p.history.shift();
  if (p.defended) { r.msgs.push('今日已守擂，本场为练习，不计分'); p.inChallenge = false; return r; }
  if (stage === 1) {
    if (win) { p.stage1Won = true; p.grass += FACTIONS.rewards.stage1Win.grass; r.msgs.push('青草币 +' + FACTIONS.rewards.stage1Win.grass + '，可以挑战第 2 场！'); }
    else { p.inChallenge = false; r.msgs.push('本次挑战结束'); }
  } else {
    p.inChallenge = false;
    if (win) {
      p.stage2Won = true; p.defended = true; p.defendDays++;
      if (p.cards.indexOf(champ.cardId) < 0) p.cards.push(champ.cardId);
      r.msgs.push('守擂成功！获得图鉴卡 ' + champ.cardId);
      FACTIONS.rewards.titles.forEach(function (t) { if (p.defendDays >= t.days && p.titles.indexOf(t.id) < 0) { p.titles.push(t.id); r.msgs.push('获得称号「' + t.name + '」'); } });
      if (p.faction) { var sc = defendScore(p, info); p.todayScore += sc; p.weekScore += sc;
        p.factionScores[p.faction] = (p.factionScores[p.faction] || 0) + sc; r.msgs.push('为' + factionById(p.faction).name + '加油 +' + sc + ' 分'); r.score = sc; }
      else r.msgs.push('未选择牧场，不计阵营分');
    } else { p.stage1Won = false; r.msgs.push('本次挑战结束'); }
  }
  return r;
}
module.exports = { REASONING_ENABLED: REASONING_ENABLED, CLUES: CLUES, CHAMPS: CHAMPS, FACTIONS: FACTIONS, ANG: ANG, genClues: genClues, stanceFor: stanceFor, multipliers: multipliers,
  dateKeyAt: dateKeyAt, championFor: championFor, loadProgress: loadProgress, saveProgress: function (p) { store.set(p); }, triesLeft: triesLeft,
  canChangeFaction: canChangeFaction, setFaction: setFaction, factionLabel: factionLabel, factionById: factionById, defendScore: defendScore,
  onStageEnd: onStageEnd, _setRnd: function (f) { rnd = f || Math.random; } };
