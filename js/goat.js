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
function shadowRGB() { var c = '#2F3727'; try { var T = require('./theme.js'); if (T.shadow && T.shadow.contactColor) c = T.shadow.contactColor; } catch (e) {} var n = parseInt(c.slice(1), 16); return ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255); }
function shadowAlpha() { try { var T = require('./theme.js'); if (T.shadow && T.shadow.contactAlpha != null) return T.shadow.contactAlpha; } catch (e) {} return 0.26; }
function drawShadow(ctx, x, y, s, lift) { // 接触阴影（theme.shadow 令牌，#2F3727 低透明度；展示台与战斗共用）：中心/尺寸规则与物理位置对齐，径向渐变占位
  var k = Math.max(0.4, 1 - (lift || 0) / 160), a = shadowAlpha() * k, rx = 40 * s * k, ry = 7 * s * k, cy = y + 41 * s, rgb = shadowRGB();
  ctx.save(); var g = ctx.createRadialGradient && ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  if (g && g.addColorStop) { g.addColorStop(0, 'rgba(' + rgb + ',' + a.toFixed(3) + ')'); g.addColorStop(0.6, 'rgba(' + rgb + ',' + (a * 0.6).toFixed(3) + ')'); g.addColorStop(1, 'rgba(' + rgb + ',0)');
    ctx.translate(x, cy); ctx.scale(rx * 1.25, ry * 1.6); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 1, 0, 7); ctx.fill(); }
  else { ctx.fillStyle = 'rgba(' + rgb + ',' + (a * 0.75).toFixed(3) + ')'; ctx.beginPath(); ctx.ellipse(x, cy, rx, ry, 0, 0, 7); ctx.fill(); }
  ctx.restore();
}
module.exports.drawShadow = drawShadow;

// ================= 半写实分层素材（art/manifest.json，当前 v7，只用 _320） =================
// 绘制顺序/锚点/换色以 manifest 为准；加载失败或未就绪时回退到上面的程序化 drawGoat。
// 每个姿态的素材来源（可配置）：base 为图片目录，manifest 非空时该姿态的锚点/kind 从该 manifest 读取。当前三姿态均用 art/ (manifest v5)
var POSE_SRC = { idle: { base: 'art/', manifest: null }, jump: { base: 'art/', manifest: null }, clash: { base: 'art/', manifest: null } };
var ART = { src: POSE_SRC, poseMan: {}, ready: false, failed: false, man: null, imgs: {}, pending: 0, cache: {}, footFix: {}, errors: [] };
var LEGACY_WOOL = { curly: 'fluffy', fluff: 'fluffy', velvet: 'short', dot: 'spots', dots: 'spots', spotted: 'spots', puff: 'cloud' };
var LEGACY_HORN = { curved: 'curl', ram: 'curl', spike: 'straight', screw: 'spiral', antler: 'branch', deer: 'branch' };
function normalizeLook(look) { // 兼容旧存档/旧字段名
  look = look || {};
  var w = look.wool || look.woolType || look.fur, h = look.horn || look.hornType || look.hornShape;
  w = LEGACY_WOOL[w] || w; h = LEGACY_HORN[h] || h;
  var ids = ART.man ? ART.man.ids : { wools: ['fluffy', 'short', 'spots', 'cloud'], horns: ['curl', 'straight', 'spiral', 'branch'] };
  if (ids.wools.indexOf(w) < 0) w = 'fluffy'; if (ids.horns.indexOf(h) < 0) h = 'curl';
  return { wool: w, woolColor: look.woolColor || look.furColor || '#ffffff', horn: h, hornColor: look.hornColor || '#d9b77a' };
}
function artLoadJSON(p) {
  if (typeof wx !== 'undefined' && wx.getFileSystemManager) return JSON.parse(wx.getFileSystemManager().readFileSync(p, 'utf8'));
  var x = new XMLHttpRequest(); x.open('GET', p, false); x.send(); if (x.status && x.status !== 200) throw new Error(p + ' ' + x.status); return JSON.parse(x.responseText);
}
function newImage() { if (typeof wx !== 'undefined' && wx.createImage) return wx.createImage(); var im = new Image(); im.crossOrigin = 'anonymous'; return im; }
function newCanvas(w, h) {
  var c = (typeof document !== 'undefined' && document.createElement) ? document.createElement('canvas') : wx.createCanvas(); // wx 首次 createCanvas 之后为离屏
  c.width = w; c.height = h; return c;
}
function poseOf(key) { var m = key.match(/_(idle|jump|clash)$/); return m ? m[1] : 'idle'; }
function srcOf(pose) { return POSE_SRC[pose] || { base: 'art/', manifest: null }; }
function smallPath(tpl) { return srcOf(poseOf(tpl)).base + tpl + '_320.png'; }
function poseInfo(pose) { return (ART.poseMan[pose] || ART.man).poses[pose]; }
function loadArt() {
  try { ART.man = artLoadJSON('art/manifest.json'); } catch (e) { ART.failed = true; ART.errors.push('manifest: ' + e.message); return; }
  Object.keys(POSE_SRC).forEach(function (pose) { var mp = POSE_SRC[pose].manifest; if (!mp) return;
    try { var mm = artLoadJSON(mp); if (mm.poses && mm.poses[pose]) ART.poseMan[pose] = mm; } catch (e) { ART.errors.push('pose manifest ' + mp + ': ' + e.message); } });
  try { ART.parts = artLoadJSON('art/parts.json'); ART.partFiles = {}; indexParts(ART.parts); } catch (e) { ART.parts = null; ART.errors.push('parts: ' + e.message); }
  var m = ART.man, list = {};
  Object.keys(m.poses).forEach(function (pose) {
    m.draw_order.forEach(function (t) {
      if (t.indexOf('{wool}') >= 0) m.ids.wools.forEach(function (w) { list[t.replace('{wool}', w).replace('{pose}', pose)] = 1; });
      else if (t.indexOf('{horn}') >= 0) m.ids.horns.forEach(function (h) { list[t.replace('{horn}', h).replace('{pose}', pose)] = 1; });
      else list[t.replace('{pose}', pose)] = 1;
    });
  });
  var keys = Object.keys(list); ART.pending = keys.length;
  keys.forEach(function (k) {
    var img = newImage();
    img.onload = function () { ART.imgs[k] = img; if (--ART.pending === 0) { ART.ready = true; measureFeet(); } };
    img.onerror = function () { ART.errors.push('load fail ' + k); ART.imgs[k] = null; if (--ART.pending === 0) { ART.ready = true; measureFeet(); } };
    img.src = smallPath(k);
  });
}
function kindOf(key) {
  if (ART.kindOv && ART.kindOv[key]) key = ART.kindOv[key];
  var f = ((ART.poseMan[poseOf(key)] || ART.man).files || []).filter(function (x) { return x.small === key + '_320.png'; })[0];
  if (f) return f.kind;
  return key.indexOf('horn/') === 0 ? 'gray_mask_mid' : key.indexOf('wool/') === 0 ? 'gray_mask' : 'color';
}
function hex(c) { c = c.replace('#', ''); if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2]; return [parseInt(c.substr(0, 2), 16), parseInt(c.substr(2, 2), 16), parseInt(c.substr(4, 2), 16)]; }
// 换色并缓存到离屏 canvas：key+颜色只算一次
function layer(key, color) {
  var img = ART.imgs[key]; if (!img) return null;
  var kind = kindOf(key); if (kind === 'color' || !color) return img;
  var ck = key + '|' + color; if (ART.cache[ck]) return ART.cache[ck];
  var w = img.width, h = img.height, c = newCanvas(w, h), x = c.getContext('2d');
  x.drawImage(img, 0, 0); var d = x.getImageData(0, 0, w, h), p = d.data, t = hex(color), div = kind === 'gray_mask_mid' ? 128 : 255;
  for (var i = 0; i < p.length; i += 4) { if (!p[i + 3]) continue;
    var g = (p[i] + p[i + 1] + p[i + 2]) / 3 / div;
    p[i] = Math.min(255, g * t[0]); p[i + 1] = Math.min(255, g * t[1]); p[i + 2] = Math.min(255, g * t[2]); }
  x.putImageData(d, 0, 0); ART.cache[ck] = c; return c;
}
// 校验 manifest 锚点与实际脚底（body 层最低不透明行），偏差大时记录并用实测值修正
function measureFeet() {
  var m = ART.man;
  Object.keys(m.poses).forEach(function (pose) {
    var img = ART.imgs['body/body_' + pose]; if (!img) return;
    try {
      var c = newCanvas(img.width, img.height), x = c.getContext('2d'); x.drawImage(img, 0, 0);
      var d = x.getImageData(0, 0, img.width, img.height).data, bottom = -1;
      for (var yy = img.height - 1; yy >= 0 && bottom < 0; yy--) for (var xx = 0; xx < img.width; xx++) if (d[(yy * img.width + xx) * 4 + 3] > 40) { bottom = yy; break; }
      var pm = ART.poseMan[pose] || m, anchorY = pm.poses[pose].anchor[1] / pm.canvas[1] * img.height;
      ART.footFix[pose] = { manifestY: anchorY, measuredY: bottom + 1, diff: bottom + 1 - anchorY };
    } catch (e) { ART.errors.push('measure ' + pose + ': ' + e.message); }
  });
}
function artUsable(look, pose) {
  if (!ART.ready || ART.failed || !ART.man) return false;
  var need = ART.man.draw_order.map(function (t) { return t.replace('{wool}', look.wool).replace('{horn}', look.horn).replace('{pose}', pose); });
  return need.every(function (k) { return !!ART.imgs[k]; });
}
// ================= 部件（art/parts.json）：头/尾展示性旋转 + 关节补片（只渲染，不读写物理） =================
// 旋转角为 0 时走上面的整图路径（观感与之前完全一致）；非 0 时按 parts.json 的 part_draw_order 逐部件绘制。
// spots_mask 与整图路径一致不使用（整图 draw_order 无 spots_mask，且 packOptions 排除 spots_mask_）。
ART.kindOv = {}; ART.rot = null; ART.patchFull = false; // patchFull：仅开发/截图用全尺寸补片（不入包）； // ART.rot = {head: 度, tail: 度} 调试/截图覆盖（canvas rotate 度数，正 = 顺时针）
function indexParts(p) {
  var add = function (f) { ART.partFiles[f.replace(/\.png$/, '')] = 1; };
  Object.keys(p.poses || {}).forEach(function (pose) { var fl = p.poses[pose].files || {}; Object.keys(fl).forEach(function (k) { fl[k].forEach(add); }); });
  var jp = (p.joint_patch || {}).poses || {};
  Object.keys(jp).forEach(function (pose) { Object.keys(jp[pose]).forEach(function (k) { ((jp[pose][k] || {}).files || []).forEach(add); }); });
}
function partLayers(look, pose) { // [{key, whole, part}]，按 part_draw_order × 部件内图层顺序；只返回 parts.json 中存在的文件
  var out = [], m = ART.man;
  ART.parts.part_draw_order.forEach(function (part) {
    m.draw_order.forEach(function (tpl) {
      if (tpl.indexOf('{horn}') >= 0 && part !== 'horn') return;
      var whole = tpl.replace('{wool}', look.wool).replace('{horn}', look.horn).replace('{pose}', pose);
      var key = 'parts/' + pose + '/' + part + '/' + whole.split('/')[1];
      if (ART.partFiles[key]) { ART.kindOv[key] = whole; out.push({ key: key, whole: whole, part: part, tpl: tpl }); }
    });
  });
  return out;
}
function patchKey(look, pose, which, a) { // a = -(canvas 度数)；返回 {key, alpha} 或 null
  var aa = Math.abs(a); if (aa < 1) return null;
  var n = aa <= 7.5 ? 5 : aa <= 12.5 ? 10 : 15;
  var key = 'parts/' + pose + '/' + which + '/' + look.wool + '_' + pose + '_a' + (a > 0 ? '+' : '-') + n;
  if (!ART.partFiles[key]) return null; // parts.json 未列出的帧＝美术有意留空，静默跳过（不记 ART.errors）
  ART.kindOv[key] = 'wool/' + look.wool + '_' + pose;
  return { key: key, alpha: Math.max(0, Math.min(1, (aa - 1) / 4)) };
}
function ensurePartImgs(keys) { // 惰性加载 _320，全部就绪才返回 true
  var ok = true;
  keys.forEach(function (k) {
    if (ART.imgs[k] || (ART.imgs[k] === null && k.indexOf('_patch/') >= 0)) return; ok = false; if (ART.imgs[k] === null || (ART.loadingP || {})[k]) return;
    ART.loadingP = ART.loadingP || {}; ART.loadingP[k] = 1;
    var img = newImage(); img.onload = function () { ART.imgs[k] = patchOpaque(k, img) ? null : img; delete ART.loadingP[k]; };
    img.onerror = function () { ART.imgs[k] = null; delete ART.loadingP[k]; ART.errors.push('load fail ' + k); }; img.src = srcOf(poseOf(k.split('/')[1] ? '_' + k.split('/')[1] : '')).base + k + (ART.patchFull && k.indexOf('_patch/') >= 0 ? '.png' : '_320.png');
  });
  return ok;
}
// 补片帧应为透明底；若左上角不透明（如 _320 导出丢了 alpha），视为无效帧并跳过（同"帧不存在"），记入 ART.errors
function patchOpaque(k, img) {
  if (k.indexOf('_patch/') < 0) return false;
  try { var c = newCanvas(img.width, img.height), x = c.getContext('2d'); x.drawImage(img, 0, 0);
    if (x.getImageData(0, 0, 1, 1).data[3] > 0) { ART.errors.push('patch frame without alpha, skipped: ' + k); return true; } } catch (e) {}
  return false;
}
function colorFor(tpl, whole, look) {
  return tpl.indexOf('{wool}') >= 0 || whole.indexOf('beard/') === 0 ? look.woolColor : whole.indexOf('wool/knee') === 0 ? KNEE : tpl.indexOf('{horn}') >= 0 ? look.hornColor : null;
}
// 在已 translate(x,footY)+scale(face) 的坐标系里绘制部件；返回 false 表示素材未就绪（调用方回退整图）
function drawParts(ctx, look, pose, rot, cw, chh, size, sz, ax, ay) {
  if (!ART.parts || !ART.parts.poses[pose]) return false;
  var PP = ART.parts.poses[pose], piv = PP.pivots, layers = partLayers(look, pose);
  // 关节补片：joint_patch 中每个 <部件>_patch（head/tail/四条腿）按该部件自身旋转角选帧
  var JP = ((ART.parts.joint_patch || {}).poses || {})[pose] || {}, patches = [];
  Object.keys(JP).forEach(function (pk) { var part = pk.replace(/_patch$/, ''), d = rot[part] || 0; if (!d) return; var q = patchKey(look, pose, pk, -d); if (q) patches.push(q); });
  var need = layers.map(function (l) { return l.key; }); patches.forEach(function (q) { need.push(q.key); });
  if (!ensurePartImgs(need)) return false;
  var X = function (px) { return (px / cw - ax) * size; }, Y = function (py) { return (py / chh - ay) * sz; };
  patches.forEach(function (p) { if (!p || ART.onlyPart) return; var L = layer(p.key, look.woolColor); if (!L) return; // 补片：最下层、不跟头/尾转
    ctx.save(); ctx.globalAlpha *= p.alpha; ctx.drawImage(L, -ax * size, -ay * sz, size, sz); ctx.restore(); });
  layers.forEach(function (l) {
    if (ART.onlyPart && l.part !== ART.onlyPart) return; // 调试：只画某部件（像素归属统计用）
    var L = layer(l.key, colorFor(l.tpl, l.whole, look)); if (!L) return;
    var rp = l.part === 'horn' ? 'head' : l.part === 'body' ? null : l.part, d = rp ? (rot[rp] || 0) : 0; // horn 跟随 head；腿绕各自 pivot
    if (d) { var pv = piv[rp]; ctx.save(); ctx.translate(X(pv[0]), Y(pv[1])); ctx.rotate(d * Math.PI / 180); ctx.translate(-X(pv[0]), -Y(pv[1])); }
    ctx.drawImage(L, -ax * size, -ay * sz, size, sz);
    if (d) ctx.restore();
  });
  return true;
}
module.exports.drawParts = drawParts;
var KNEE = '#a8774a', ART_SCALE = 0.1; // 画布高 1024 → 102.4*s 像素（宽按实际图片比例），与旧程序化羊大小相当
// x,y 与旧 drawGoat 相同（身体中心，脚底在 y+40*s）；pose: idle|jump|clash
function drawGoatArt(ctx, x, y, s, look, face, t, pose, rot) { // rot: 可选 {head, tail} 展示性旋转（canvas 度数）
  look = normalizeLook(look); pose = pose || 'idle';
  if (!ART.man || !ART.man.poses[pose]) pose = 'idle';
  if (!artUsable(look, pose)) return drawGoat(ctx, x, y, s, look, face, t);
  var m = ART.poseMan[pose] || ART.man, P = m.poses[pose];
  // 画布尺寸以实际图片为准（宽高比 × manifest 高度），manifest.canvas 仅作缺省；v7 = 1152×1024 / 360×320
  var ref = ART.imgs['body/body_' + pose], cw = ref && ref.height ? m.canvas[1] * ref.width / ref.height : m.canvas[0], chh = m.canvas[1];
  if (ref && Math.abs(cw - m.canvas[0]) > 1 && !ART.warnedSize) { ART.warnedSize = 1; ART.errors.push('canvas mismatch manifest ' + m.canvas + ' vs image ' + ref.width + 'x' + ref.height); }
  var sz = chh * ART_SCALE * s, size = cw * ART_SCALE * s;
  var ax = P.anchor[0] / cw, ay = P.anchor[1] / chh;
  var fix = ART.footFix[pose]; if (fix && Math.abs(fix.diff) > 6 && USE_FOOT_FIX) ay = fix.measuredY / ART.imgs['body/body_' + pose].height;
  var footY = y + 40 * s;
  ctx.save(); ctx.translate(x, footY); ctx.scale(face < 0 ? -1 : 1, 1);
  rot = ART.rot || rot;
  if (rot && Object.keys(rot).some(function (k) { return rot[k]; }) && drawParts(ctx, look, pose, rot, cw, chh, size, sz, ax, ay)) { ctx.restore(); return; }
  m.draw_order.forEach(function (tpl) {
    var key = tpl.replace('{wool}', look.wool).replace('{horn}', look.horn).replace('{pose}', pose);
    var col = tpl.indexOf('{wool}') >= 0 || key.indexOf('beard/') === 0 ? look.woolColor :  // v8c 胡子与羊毛同色（manifest kind=gray_mask 时生效，kind=color 时 layer() 原样返回）
      key.indexOf('wool/knee') === 0 ? KNEE : tpl.indexOf('{horn}') >= 0 ? look.hornColor : null;
    var L = layer(key, col); if (L) ctx.drawImage(L, -ax * size, -ay * sz, size, sz);
  });
  ctx.restore();
  if (ART.debug) { // 调试叠加：物理位置/脚底线/旧程序化角点 vs 贴图角根，仅渲染
    var f = face < 0 ? -1 : 1, hr = P.horn_root;
    var hx = x + f * (hr[0] / cw - ax) * size, hy = footY + (hr[1] / chh - ay) * sz;
    ctx.save(); ctx.lineWidth = 1;
    ctx.strokeStyle = '#00c'; ctx.strokeRect(x - (f > 0 ? ax : 1 - ax) * size, footY - ay * sz, size, sz);
    ctx.strokeStyle = '#f00'; ctx.beginPath(); ctx.moveTo(x - 8, y); ctx.lineTo(x + 8, y); ctx.moveTo(x, y - 8); ctx.lineTo(x, y + 8); ctx.stroke();
    ctx.strokeStyle = '#0a0'; ctx.beginPath(); ctx.moveTo(x - 50 * s, footY); ctx.lineTo(x + 50 * s, footY); ctx.stroke();
    ctx.fillStyle = 'rgba(255,140,0,.9)'; ctx.beginPath(); ctx.arc(x + f * 40 * s, y - 26 * s, 4, 0, 7); ctx.fill();
    ctx.strokeStyle = '#06f'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(hx, hy, 5, 0, 7); ctx.stroke();
    ART.lastDebug = ART.lastDebug || {}; ART.lastDebug[f] = { pose: pose, physX: x, physY: y, footY: footY, procHorn: [x + f * 40 * s, y - 26 * s], spriteHornRoot: [hx, hy], ay: ay };
    ctx.restore();
  }
}
var USE_FOOT_FIX = false; // manifest 的 clash 锚点与实际脚底不符时用实测值（见 ART.footFix）
try { loadArt(); } catch (e) { ART.failed = true; ART.errors.push(String(e)); }
module.exports.drawGoatArt = drawGoatArt;
module.exports.normalizeLook = normalizeLook;
module.exports.ART = ART;
module.exports.drawGoatProc = drawGoat;
