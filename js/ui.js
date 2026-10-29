// UI 渲染层（第二步）：位图字体、九宫格按钮/面板、暗角、阵营色调、tween.js 缓动。只画不改任何游戏/物理状态；不用 Math.random。
var TWEEN = require('../libs/tween.umd.js'), VC = require('./visual_config.js'), TH = require('./theme.js');
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
var FONT = TH.font.bitmap.enabled ? loadJSON(TH.font.bitmap.atlas) : null;
if (FONT) Object.keys(FONT.styles).forEach(function (k) { img('art/' + FONT.styles[k].file); });
function chars(s) { return Array.from ? Array.from(s) : s.split(''); }
function isEmoji(c) { var cp = c.codePointAt ? c.codePointAt(0) : c.charCodeAt(0); return cp >= 0x2190 && !(cp >= 0x4e00 && cp <= 0x9fff) && !(cp >= 0x3000 && cp <= 0x303f) && !(cp >= 0xff00 && cp <= 0xffef); }
function bmText(ctx, s, x, y, size, style, color) { // color：title 风格可传入颜色（蒙版字体乘色） // 返回 false 则调用方回退到系统字体
  if (!FONT || !FONT.styles[style]) return false; if (color && style === TH.font.bitmap.titleStyle && FONT.styles[TH.font.bitmap.titleColorStyle]) style = TH.font.bitmap.titleColorStyle; var S = FONT.styles[style], im = style === TH.font.bitmap.titleColorStyle ? tinted('art/' + S.file, color) : img('art/' + S.file); if (!im) return false;
  var cs = chars(String(s)), k = size / S.px, tw = 0, ws = [];
  for (var i = 0; i < cs.length; i++) { var c = cs[i], gl = S.glyphs[c];
    if (gl) ws.push((gl[2] - S.pad * 2) * k); else if (c === ' ') ws.push(size * 0.3); else if (isEmoji(c)) { ctx.font = sysFont(Math.round(size * TH.font.bitmap.emojiScale)); ws.push(ctx.measureText(c).width); } else return false; tw += ws[i]; }
  var cx = x - tw / 2, h = S.h * k, top = y - (S.cy != null ? S.cy : S.h / 2) * k; // 字形视觉中心对齐 y，emoji 同以 y 居中
  for (var j = 0; j < cs.length; j++) { var g2 = S.glyphs[cs[j]];
    if (g2) ctx.drawImage(im, g2[0], g2[1], g2[2], S.h, cx - S.pad * k, top, g2[2] * k, h);
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
function vignette(ctx, W, H) { var V = VC.vignette; if (!V.enabled || !(V.alpha > 0)) return;
  var g = grad(ctx.createRadialGradient && ctx.createRadialGradient(W / 2, H * 0.45, Math.min(W, H) * V.inner, W / 2, H * 0.45, Math.max(W, H) * V.outer),
  [[0, 'rgba(' + V.color + ',0)'], [1, 'rgba(' + V.color + ',' + V.alpha + ')']]); if (!g) return; ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
// ---- 阵营色调（只换色调，界面仍只显示牧场名）----
var TINT = VC.factionTint.colors;
function tintOf(id) { if (!id) return null; if (TINT[id]) return TINT[id]; var h = 0; for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 360; return 'hsl(' + h + ',55%,55%)'; }
function factionTint(ctx, W, H, id) { var T = VC.factionTint, c = tintOf(id); if (!c || !T.enabled) return; ctx.save(); ctx.globalAlpha = T.alpha; ctx.fillStyle = c; ctx.fillRect(0, 0, W, H);
  ctx.globalAlpha = T.topAlpha; var g = grad(ctx.createLinearGradient(0, 0, 0, H * T.topHeight), [[0, c], [1, 'rgba(255,255,255,0)']]); if (g) { ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * T.topHeight); } ctx.restore(); }
// ---- tween.js：场景切换时标题弹出、按钮淡入上浮（显示用，命中区不变）----
var grp = new TWEEN.Group(), anim = { pop: 1, fade: 1 }, last = null, t = 0;
function update(ms, scene) { t = ms;
  if (scene !== last) { var M = TH.motion; last = scene; anim.pop = M.titlePopFrom; anim.fade = 0; grp.removeAll();
    new TWEEN.Tween(anim, grp).to({ pop: 1 }, M.titlePopMs).easing(ease(M.titleEasing)).start(ms);
    new TWEEN.Tween(anim, grp).to({ fade: 1 }, M.fadeMs).easing(ease(M.fadeEasing)).start(ms); }
  grp.update(ms); }
function lighten(col, k) { if (!(k > 1) || !/^#[0-9a-f]{6}$/i.test(col)) return col; var n = parseInt(col.slice(1), 16), o = '#';
  [16, 8, 0].forEach(function (b) { var v = Math.min(255, Math.round(((n >> b) & 255) * k)); o += (v < 16 ? '0' : '') + v.toString(16); }); return o; }
function ease(n) { var a = String(n || 'Linear.None').split('.'), g = TWEEN.Easing[a[0]]; return (g && g[a[1] || 'None']) || TWEEN.Easing.Linear.None; }
// ---- 字体：站酷快乐体子集，小游戏 wx.loadFont / 浏览器 FontFace；未加载完或缺字时回退字体逐字补 ----
var FAM = TH.font.family;
(function loadFont() { var F = TH.font; if (!F.file) return;
  try { if (typeof wx !== 'undefined' && wx.loadFont) { var fam = wx.loadFont(F.file); if (fam) FAM = fam; return; }
    if (typeof FontFace !== 'undefined' && typeof document !== 'undefined' && document.fonts) { var ff = new FontFace(F.family, 'url(' + F.file + ')');
      ff.load().then(function (f) { document.fonts.add(f); }, function () {}); } } catch (e) {} })();
function sysFont(size) { return TH.font.weight + ' ' + size + 'px ' + FAM + ',' + TH.font.fallback; }
// ---- 统一绘制：按钮 / 面板 / 文字 / 背景 都读主题 ----
function rr(ctx, x, y, w, h, r) { r = Math.max(0, Math.min(r, w / 2, h / 2)); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function ink() { return TH.colors.ink; }
// 文字：style 为 theme.text 的样式名，或直接给颜色；多行用 \n
function drawText(ctx, s, x, y, size, style, align) { size = size || 16; s = String(s);
  var S = (style && TH.text[style]) || { fill: style || TH.colors.text }, big = S.rotate != null;
  ctx.save(); ctx.translate(x, y); if (big) { var k = anim.pop; ctx.scale(k, k); ctx.rotate(S.rotate * Math.PI / 180); }
  ctx.font = sysFont(size); ctx.textAlign = align || 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  var lines = s.split('\n'), lh = size * 1.12, y0 = -(lines.length - 1) * lh / 2;
  lines.forEach(function (L, i) { var yy = y0 + i * lh;
    if (S.shadow) { ctx.fillStyle = ink(); ctx.strokeStyle = ink(); ctx.lineWidth = S.stroke || 0; if (S.stroke) ctx.strokeText(L, S.shadow[0], yy + S.shadow[1]); ctx.fillText(L, S.shadow[0], yy + S.shadow[1]); }
    if (S.stroke) { ctx.strokeStyle = ink(); ctx.lineWidth = S.stroke; ctx.strokeText(L, 0, yy); }
    ctx.fillStyle = S.fill; ctx.fillText(L, 0, yy); });
  ctx.restore(); }
function measure(ctx, s, size) { ctx.font = sysFont(size); var m = ctx.measureText(String(s)); return m && m.width || String(s).length * size; }
// 贴纸块：白/彩底 + 粗黑描边 + 底部厚边（main 草绿厚边 / 其余黑投影）
function sticker(ctx, x, y, w, h, r, fill, edgeH, edgeCol, sw) {
  if (edgeH > 0) { ctx.fillStyle = ink(); rr(ctx, x - sw / 2, y + edgeH - sw / 2, w + sw, h + sw, r); ctx.fill();
    if (edgeCol) { ctx.fillStyle = edgeCol; rr(ctx, x, y + edgeH, w, h - sw / 2, r); ctx.fill(); } }
  ctx.fillStyle = fill; rr(ctx, x, y, w, h, r); ctx.fill();
  if (sw > 0) { ctx.strokeStyle = ink(); ctx.lineWidth = sw; rr(ctx, x, y, w, h, r); ctx.stroke(); } }
// 按钮：variant 为 theme.button.variants 的名字（旧调用传颜色时按白色处理）；命中区由调用方按 x,y,w,h 记录，绘制只在区内+厚边
function drawButton(ctx, x, y, w, h, label, variant, fontSize) { var B = TH.button, M = TH.motion, a = anim.fade, oy = (1 - a) * M.buttonRise;
  var V = B.variants[variant] || B.variants.white, main = !!V.main, eh = main ? B.edge : B.shadowY;
  ctx.save(); ctx.globalAlpha = M.buttonMinAlpha + (1 - M.buttonMinAlpha) * a;
  sticker(ctx, x, y + oy, w, h - (main ? 0 : 0), Math.min(B.radius, h / 2), V.fill, eh, main ? B.edgeColor : null, B.stroke.width);
  var fs = fontSize || Math.min(B.fontSize, h * B.fontSizeRatio * (String(label).indexOf('\n') >= 0 ? 0.8 : 1));
  drawText(ctx, label, x + w / 2, y + oy + h / 2 + B.textOffsetY, fs, V.text);
  ctx.restore(); }
function drawPanel(ctx, x, y, w, h, alpha) { var P = TH.panel, M = TH.motion; ctx.save(); ctx.globalAlpha = (alpha || P.alpha) * (M.panelMinAlpha + (1 - M.panelMinAlpha) * anim.fade);
  sticker(ctx, x, y, w, h, P.radius, P.fill, P.shadowY, null, P.stroke.width); ctx.restore(); }
// 胶囊标签：dark=黑底白字（样稿“第 1 回合”），light=白底黑描边
function drawPill(ctx, s, x, y, light, size) { var P = TH.pill, C = light === 'warn' ? P.warn : light ? P.light : P, fs = size || P.fontSize, w = measure(ctx, s, fs) + P.padX * 2, h = Math.max(P.h, fs + 8);
  ctx.save(); ctx.fillStyle = C.fill; rr(ctx, x - w / 2, y - h / 2, w, h, h / 2); ctx.fill();
  if (light) { ctx.strokeStyle = C.stroke || ink(); ctx.lineWidth = 2; ctx.stroke(); }
  ctx.restore(); drawText(ctx, s, x, y, fs, C.text); return w; }
// 血条：白底黑描边圆角，fromRight 时从右侧填充（对手）
function drawBar(ctx, x, y, w, v, max, fromRight) { var B = TH.bar, k = Math.max(0, Math.min(1, v / max)), h = B.h;
  ctx.save(); ctx.fillStyle = B.bg; rr(ctx, x, y, w, h, B.radius); ctx.fill(); ctx.save(); rr(ctx, x, y, w, h, B.radius); ctx.clip && ctx.clip();
  ctx.fillStyle = k > B.lowRatio ? (fromRight ? B.hpLow : B.hp) : B.hpLow; if (!fromRight && k <= B.lowRatio) ctx.fillStyle = B.hpLow;
  ctx.fillRect(fromRight ? x + w * (1 - k) : x, y, w * k, h); ctx.restore();
  ctx.strokeStyle = ink(); ctx.lineWidth = B.stroke; rr(ctx, x, y, w, h, B.radius); ctx.stroke(); ctx.restore(); }
// 蓄力条：白底 + 草绿高力区 + 红色描边游标
function drawMeter(ctx, x, y, w, v, z0, z1) { var B = TH.bar, h = B.meterH;
  ctx.save(); ctx.fillStyle = B.bg; rr(ctx, x, y, w, h, h / 2); ctx.fill(); ctx.save(); rr(ctx, x, y, w, h, h / 2); ctx.clip && ctx.clip();
  ctx.fillStyle = B.meterZone; ctx.fillRect(x + w * z0, y, w * (z1 - z0), h); ctx.restore();
  ctx.strokeStyle = ink(); ctx.lineWidth = B.stroke; rr(ctx, x, y, w, h, h / 2); ctx.stroke();
  var mx = x + w * Math.max(0, Math.min(1, v)) - B.markerW / 2, my = y + h / 2 - B.markerH / 2;
  ctx.fillStyle = B.marker; rr(ctx, mx, my, B.markerW, B.markerH, 3); ctx.fill(); ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore(); }
// 背景：纯色草绿 + 确定性稀疏小草（V 形三笔），不消耗 Math.random
var TUFTS = null;
function tufts(W, H) { if (TUFTS && TUFTS.W === W && TUFTS.H === H) return TUFTS.list; var G = TH.background, s = G.tuftSeed, out = [];
  function r() { s = (s * 48271) % 2147483647; return s / 2147483647; }
  for (var i = 0; i < G.tufts; i++) out.push([10 + r() * (W - 30), 10 + r() * (H - 25)]); TUFTS = { W: W, H: H, list: out }; return out; }
function drawTufts(ctx, W, H) { var G = TH.background, w = G.tuftW, h = G.tuftH;
  ctx.save(); ctx.strokeStyle = TH.colors.tuft; ctx.lineWidth = G.tuftLine; ctx.lineCap = 'round';
  tufts(W, H).forEach(function (p) { var x = p[0], y = p[1]; ctx.beginPath();
    ctx.moveTo(x + w * 0.15, y + h); ctx.lineTo(x + w * 0.05, y + h * 0.33); ctx.moveTo(x + w * 0.35, y + h); ctx.lineTo(x + w * 0.4, y);
    ctx.moveTo(x + w * 0.55, y + h); ctx.lineTo(x + w * 0.75, y + h * 0.42); ctx.stroke(); }); ctx.restore(); }
function drawBg(ctx, W, H) { var C = TH.colors;
  if (TH.background.style === 'gradient') { var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, C.skyTop); g.addColorStop(1, C.skyBottom);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.fillStyle = C.ground; ctx.fillRect(0, H * C.groundY, W, H * (1 - C.groundY)); return; }
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); drawTufts(ctx, W, H); }
// 首页展示台：浅色椭圆底座 + 接触阴影（y/s 与 drawGoatArt 相同）
function drawPedestal(ctx, x, y, s) { var S = TH.stage, k = s / 1.6, rx = S.pedestalRx * k, ry = S.pedestalRy * k, cy = y + 41 * s + 3 * k; // 与 goat.drawShadow 同一脚底规则（y+41s）
  ctx.save(); ctx.fillStyle = S.pedestalEdge; ctx.beginPath(); ctx.ellipse(x, cy + 4 * k, rx, ry, 0, 0, 7); ctx.fill();
  ctx.fillStyle = S.pedestal; ctx.beginPath(); ctx.ellipse(x, cy, rx, ry, 0, 0, 7); ctx.fill(); ctx.strokeStyle = ink(); ctx.lineWidth = 2; ctx.stroke();
  ctx.restore(); require('./goat.js').drawShadow(ctx, x, y - 1 * k, s * 0.9, 0); } // 接触阴影统一走 theme.shadow（与战斗同款）
function dim(ctx, W, H) { ctx.fillStyle = TH.colors.dim; ctx.fillRect(0, 0, W, H); }
// 新手教学：遮罩挖洞高亮（evenodd，洞用内联圆角路径，不调 rr 以免 beginPath 清掉外框）
function spotlight(ctx, W, H, holes) { var T = TH.tutorial; ctx.save(); ctx.fillStyle = 'rgba(0,0,0,' + T.dimAlpha + ')'; ctx.beginPath(); ctx.rect(0, 0, W, H);
  (holes || []).forEach(function (h) { var p = T.holePad, x = h[0] - p, y = h[1] - p, w = h[2] + 2 * p, hh = h[3] + 2 * p, r = Math.min(T.holeR, w / 2, hh / 2);
    ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.arcTo(x + w, y, x + w, y + r, r); ctx.lineTo(x + w, y + hh - r); ctx.arcTo(x + w, y + hh, x + w - r, y + hh, r);
    ctx.lineTo(x + r, y + hh); ctx.arcTo(x, y + hh, x, y + hh - r, r); ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r); ctx.closePath(); });
  ctx.fill('evenodd'); ctx.restore(); }
function drawTip(ctx, s, x, y) { return drawPill(ctx, s, x, y, true, TH.tutorial.tipSize); }
function zoneOutline(ctx, x, y, w, z0, z1) { var T = TH.tutorial, h = TH.bar.meterH, p = T.zonePad; ctx.save(); ctx.strokeStyle = T.zoneColor; ctx.lineWidth = T.zoneW; ctx.setLineDash && ctx.setLineDash([6, 4]);
  rr(ctx, x + w * z0 - p, y - p, w * (z1 - z0) + 2 * p, h + 2 * p, 6); ctx.stroke(); ctx.restore(); } // 只画：区间由调用方传入现有判定常量
module.exports = { spotlight: spotlight, drawTip: drawTip, zoneOutline: zoneOutline, drawPedestal: drawPedestal, drawPill: drawPill, drawBar: drawBar, drawMeter: drawMeter, sticker: sticker, dim: dim, measure: measure, sysFont: sysFont, drawTufts: drawTufts, TH: TH, drawText: drawText, drawButton: drawButton, drawPanel: drawPanel, drawBg: drawBg, roundRect: rr, VC: VC, lighten: lighten, img: img, tinted: tinted, text: bmText, nine: nine, vignette: vignette, factionTint: factionTint, tintOf: tintOf, update: update, anim: anim, grad: grad, TWEEN: TWEEN };
