// UI 渲染层（第二步）：位图字体、九宫格按钮/面板、暗角、阵营色调、tween.js 缓动。只画不改任何游戏/物理状态；不用 Math.random。
var TWEEN = require('../libs/tween.umd.js');
function newImage() { if (typeof wx !== 'undefined' && wx.createImage) return wx.createImage(); if (typeof Image !== 'undefined') { var im = new Image(); im.crossOrigin = 'anonymous'; return im; } return null; }
function newCanvas(w, h) { var c = (typeof document !== 'undefined' && document.createElement) ? document.createElement('canvas') : (typeof wx !== 'undefined' ? wx.createCanvas() : null);
  if (c) { c.width = w; c.height = h; } return c; }
function loadJSON(p) { try { if (typeof wx !== 'undefined' && wx.getFileSystemManager) return JSON.parse(wx.getFileSystemManager().readFileSync(p, 'utf8'));
  var x = new XMLHttpRequest(); x.open('GET', p, false); x.send(); return x.status && x.status !== 200 ? null : JSON.parse(x.responseText); } catch (e) { return null; } }
var IMG = {}; // path -> {img, ok}
function img(p) { var r = IMG[p]; if (r) return r.ok ? r.img : null; r = IMG[p] = { ok: false, img: null };
  try { var im = newImage(); if (!im) return null; im.onload = function () { r.ok = true; r.img = im; }; im.onerror = function () { r.ok = false; }; im.src = p; } catch (e) {} return null; }
var TC = {}; // 灰度贴图乘色缓存（fx.json gray_mask：RGB = 灰度/255 × 目标色）
function tinted(p, col) { var k = p + col; if (TC[k]) return TC[k]; var im = img(p); if (!im) return null;
  var c = newCanvas(im.width, im.height); if (!c || !c.getContext) return null; var g = c.getContext('2d'); if (!g || !g.drawImage) return null;
  g.fillStyle = col; g.fillRect(0, 0, c.width, c.height); g.globalCompositeOperation = 'multiply'; g.drawImage(im, 0, 0);
  g.globalCompositeOperation = 'destination-in'; g.drawImage(im, 0, 0); g.globalCompositeOperation = 'source-over'; return (TC[k] = c); }
// ---- 位图字体 ----
var FONT = loadJSON('art/ui/font.json');
if (FONT) Object.keys(FONT.styles).forEach(function (k) { img('art/' + FONT.styles[k].file); });
function chars(s) { return Array.from ? Array.from(s) : s.split(''); }
function isEmoji(c) { var cp = c.codePointAt ? c.codePointAt(0) : c.charCodeAt(0); return cp >= 0x2190 && !(cp >= 0x4e00 && cp <= 0x9fff) && !(cp >= 0x3000 && cp <= 0x303f) && !(cp >= 0xff00 && cp <= 0xffef); }
function bmText(ctx, s, x, y, size, style) { // 返回 false 则调用方回退到系统字体
  if (!FONT || !FONT.styles[style]) return false; var S = FONT.styles[style], im = img('art/' + S.file); if (!im) return false;
  var cs = chars(String(s)), k = size / S.px, tw = 0, ws = [];
  for (var i = 0; i < cs.length; i++) { var c = cs[i], gl = S.glyphs[c];
    if (gl) ws.push((gl[2] - S.pad * 2) * k); else if (c === ' ') ws.push(size * 0.3); else if (isEmoji(c)) { ctx.font = 'bold ' + size + 'px sans-serif'; ws.push(ctx.measureText(c).width); } else return false; tw += ws[i]; }
  var cx = x - tw / 2, h = S.h * k;
  for (var j = 0; j < cs.length; j++) { var g2 = S.glyphs[cs[j]];
    if (g2) ctx.drawImage(im, g2[0], g2[1], g2[2], S.h, cx - S.pad * k, y - h / 2, g2[2] * k, h);
    else if (cs[j] !== ' ') { ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(cs[j], cx, y); ctx.textAlign = 'center'; }
    cx += ws[j]; }
  return true; }
// ---- 九宫格 ----
function nine(ctx, p, x, y, w, h, col, b) { var im = col ? tinted(p, col) : img(p); if (!im) return false; b = b || 22; var s = im.width, m = s - 2 * b, bd = Math.min(b, h / 2, w / 2);
  var sx = [0, b, s - b], sw = [b, m, b], dx = [x, x + bd, x + w - bd], dw = [bd, w - 2 * bd, bd], dy = [y, y + bd, y + h - bd], dh = [bd, h - 2 * bd, bd];
  for (var i = 0; i < 3; i++) for (var j = 0; j < 3; j++) if (dw[i] > 0 && dh[j] > 0) ctx.drawImage(im, sx[i], sx[j], sw[i], sw[j], dx[i], dy[j], dw[i], dh[j]);
  return true; }
function grad(g, stops) { if (!g || !g.addColorStop) return null; stops.forEach(function (s) { g.addColorStop(s[0], s[1]); }); return g; }
// ---- 暗角 ----
function vignette(ctx, W, H) { var g = grad(ctx.createRadialGradient && ctx.createRadialGradient(W / 2, H * 0.45, Math.min(W, H) * 0.45, W / 2, H * 0.45, Math.max(W, H) * 0.75),
  [[0, 'rgba(40,20,0,0)'], [1, 'rgba(40,20,0,0.24)']]); if (!g) return; ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
// ---- 阵营色调（只换色调，界面仍只显示牧场名）----
var TINT = { north: '#d9a441', northeast: '#5aa0d8', east: '#4fb39a', south: '#e2735a', central: '#c9b04a', southwest: '#8f7ad0', northwest: '#c98a52', faraway: '#7a8fa6' };
function tintOf(id) { if (!id) return null; if (TINT[id]) return TINT[id]; var h = 0; for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 360; return 'hsl(' + h + ',55%,55%)'; }
function factionTint(ctx, W, H, id) { var c = tintOf(id); if (!c) return; ctx.save(); ctx.globalAlpha = 0.09; ctx.fillStyle = c; ctx.fillRect(0, 0, W, H);
  ctx.globalAlpha = 0.35; var g = grad(ctx.createLinearGradient(0, 0, 0, H * 0.25), [[0, c], [1, 'rgba(255,255,255,0)']]); if (g) { ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * 0.25); } ctx.restore(); }
// ---- tween.js：场景切换时标题弹出、按钮淡入上浮（显示用，命中区不变）----
var grp = new TWEEN.Group(), anim = { pop: 1, fade: 1 }, last = null, t = 0;
function update(ms, scene) { t = ms;
  if (scene !== last) { last = scene; anim.pop = 0.6; anim.fade = 0; grp.removeAll();
    new TWEEN.Tween(anim, grp).to({ pop: 1 }, 380).easing(TWEEN.Easing.Back.Out).start(ms);
    new TWEEN.Tween(anim, grp).to({ fade: 1 }, 260).easing(TWEEN.Easing.Quadratic.Out).start(ms); }
  grp.update(ms); }
module.exports = { img: img, tinted: tinted, text: bmText, nine: nine, vignette: vignette, factionTint: factionTint, tintOf: tintOf, update: update, anim: anim, grad: grad, TWEEN: TWEEN };
