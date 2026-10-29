// UI 主题（只影响渲染）。v3「参考国内版羊了个羊」：单色草绿底 + 稀疏小草、白底粗黑描边、彩色只给可点的东西。
// 换样稿时改本文件和 art/ui 资源即可；字段说明见 docs/theme.md。尺寸单位：375 宽逻辑像素（样稿 750 宽的一半）。
module.exports = {
  name: 'ylgy-v3',
  colors: {
    bg: '#CFFC98', tuft: '#B1D198', ink: '#2F3727', white: '#FFFFFF', muted: 'rgba(47,55,39,0.55)',
    green: '#8CCB4E', red: '#FF7A6B', yellow: '#FCD800', blue: '#2E6FD8', orange: '#FF9E3D', gray: '#C9CCC4', alert: '#E5482F',
    dim: 'rgba(47,55,39,0.55)',
    // 兼容旧字段（v2.1 渐变天空，style 为 'gradient' 时使用）
    skyTop: '#bfe9ff', skyBottom: '#fff6d8', ground: '#8fd17a', groundY: 0.72, text: '#2F3727', title: null,
    buttonDefault: '#FFFFFF', buttonText: '#2F3727'
  },
  background: { style: 'flat', tufts: 16, tuftSeed: 7, tuftW: 20, tuftH: 12, tuftLine: 1.5 }, // flat = 纯色 + 确定性小草（不用 Math.random）
  font: {
    family: 'KuaiLe', file: 'art/ui/font/kuaile.ttf', fallback: '"PingFang SC","Noto Sans CJK SC",sans-serif', weight: 'normal',
    // 站酷快乐体子集（tools/gen_font_subset.py，SIL OFL 1.1 见 art/ui/font/OFL.txt）；缺字/emoji 由回退字体逐字补
    bitmap: { enabled: false, atlas: 'art/ui/font.json', titleStyle: 'title', titleColorStyle: 'title_mask', bodyStyle: 'btn', titleMinSize: 18, bodyMinSize: 16, emojiScale: 0.9 }
  },
  text: { // drawText 的命名样式：fill / stroke(描边宽) / shadow(错位投影) / rotate(度)
    title: { fill: '#FFFFFF', stroke: 7, shadow: [3, 4], rotate: -3 },
    banner: { fill: '#FCD800', stroke: 6, shadow: [3, 4], rotate: -3 },
    bannerLose: { fill: '#C9CCC4', stroke: 6, shadow: [3, 4], rotate: -3 },
    score: { fill: '#FFFFFF', stroke: 5 },
    ink: { fill: '#2F3727' }, muted: { fill: 'rgba(47,55,39,0.55)' }, white: { fill: '#FFFFFF' },
    accent: { fill: '#2E6FD8' }, warn: { fill: '#E5482F' }, gold: { fill: '#FCD800', stroke: 3 }
  },
  button: {
    style: 'sticker', radius: 11, stroke: { width: 2, color: '#2F3727' },
    edge: 6, edgeColor: '#8CCB4E', shadowY: 3.5,   // main：底部草绿厚边 + 黑描边；其余：底部黑色投影
    fontSize: 22, fontSizeRatio: 0.42, textOffsetY: 0, pressed: 0,
    variants: { // 可点元素的颜色：fill / text / edge(main 厚边)
      main: { fill: '#FFFFFF', text: '#2F3727', main: true }, white: { fill: '#FFFFFF', text: '#2F3727' },
      sel: { fill: '#FFFFFF', text: '#2F3727', main: true }, yellow: { fill: '#FCD800', text: '#2F3727' },
      blue: { fill: '#2E6FD8', text: '#FFFFFF' }, orange: { fill: '#FF9E3D', text: '#FFFFFF' },
      green: { fill: '#8CCB4E', text: '#2F3727' }, gray: { fill: '#E4E7DF', text: 'rgba(47,55,39,0.55)' }, red: { fill: '#FF7A6B', text: '#FFFFFF' }
    },
    // 兼容旧 nine 风格字段
    image: 'art/ui/btn9.png', slice: 20, brightness: 1.07, shadow: { color: 'rgba(0,0,0,0)', blur: 0, offsetY: 0 }, sysTextOffsetY: 0
  },
  panel: {
    style: 'sticker', radius: 18, fill: '#FFFFFF', stroke: { width: 2.5, color: '#2F3727' }, shadowY: 6, alpha: 1,
    image: 'art/ui/panel9.png', slice: 20, tint: '#FFFFFF', shadow: { color: 'rgba(0,0,0,0)', blur: 0, offsetY: 0 }
  },
  pill: { fill: '#2F3727', text: '#FFFFFF', padX: 13, h: 22, fontSize: 14, light: { fill: '#FFFFFF', text: '#2F3727' }, warn: { fill: '#FFF1EE', text: '#2F3727', stroke: '#E8705F' } },
  bar: { // 血条 / 蓄力条
    h: 15, radius: 7.5, stroke: 2, bg: '#FFFFFF', hp: '#8CCB4E', hpLow: '#FF7A6B', lowRatio: 0.3,
    meterH: 17, meterZone: '#8CCB4E', marker: '#FF4D4D', markerW: 6, markerH: 29
  },
  field: { msgBottom: 162, // 顶顶乐场地
    bg: '#CFFC98', top: '#CFFC98', line: '#2F3727', lineW: 2,
    objects: { crate: '#E8B070', fragile: '#FFD9A0', ball: '#FFFFFF', rock: '#9AA19A', sheep: '#FFFFFF' }, fallback: '#DDDDDD',
    hay: '#FCD800', hayAlpha: 0.85, hayStroke: '#B08A1E', target: '#FCD800',
    aim: '#FF4D4D', aimW: 3, aimDash: [8, 6], aimLen: 84, hint: '#2E6FD8', hintLen: 104, goatR: 18, hornW: 4
  },
  tutorial: { dimAlpha: 0.55, holePad: 8, holeR: 14, tipY: 182, tipSize: 14, zoneColor: '#FCD800', zoneW: 3, zonePad: 4, skipW: 52, skipH: 30 }, // 新手教学：遮罩/提示/完美区描边（仅显示）
  shadow: { contactColor: '#2F3727', contactAlpha: 0.26, asset: null }, // 接触阴影：首页展示台与战斗共用；美术 contact_shadow 未接入前用 Canvas 径向渐变占位
  stage: { pedestal: '#F4FBE6', pedestalEdge: '#B9D98C', pedestalRx: 66, pedestalRy: 10, contactAlpha: 0.28 }, // 首页展示台（美术到位前 Canvas 占位）
  layout: { // 各屏布局令牌（相对 375×667；bottom 为距屏底）
    pad: 20, gap: 10,
    home: { titleY: 104, titleSize: 50, pillY: 160, goatY: 254, goatS: 1.6, statsY: 350, tipY: 365, rowY: 374, rowGap: 45, rowH: 35, arrowW: 35, rowX: 47,
      startW: 200, startH: 55, startBottom: 112, sideW: 55, sideH: 42, sideBottom: 97, sideX: 20 },
    battle: { // v3.5 三层：上 状态区（比分缩小）/ 中 对战区（整场物理→屏幕变换放大 sceneZoom）/ 下 操作区（起跳为主按钮）
      pillY: 30, scoreY: 66, scoreSize: 34, hpY: 112, hpLabelY: 101, hpW: 155, msgY: 146, arenaY: 92,
      jumpW: 236, jumpH: 60, jumpBottom: 84, meterBottom: 112, angleBottom: 160, angleW: 76, angleH: 38, hintBottom: 182, sceneShiftY: -70,
      sceneZoom: 1.22, msgSize: 13 },
    result: { cardX: 42, cardY: 150, cardW: 290, cardH: 380, bannerY: 150, goatY: 250, goatS: 1.25, lineY: 330, subY: 357, bigY: 390, bigSize: 44, btnY: 430, btnW: 180, btnH: 50, btn2Y: 495, btn2W: 110, btn2H: 40 },
    arena: { rankY: 162, rowY0: 12, rowStep: 25, rowH: 20, youY: 94, backW: 110, backH: 32, backBottom: 52, footBottom: 10 },
    list: { titleY: 52, subY: 94, top: 118, rowH: 50, gap: 12, backW: 110, backH: 40, backBottom: 60 }
  },
  motion: { titlePopFrom: 0.6, titlePopMs: 380, titleEasing: 'Back.Out', fadeMs: 220, fadeEasing: 'Quadratic.Out', buttonRise: 8, buttonMinAlpha: 0.25, panelMinAlpha: 0.3 },
  spacing: { screenPad: 20, gap: 10, rowGap: 49 },
  effects: { // 新风格：无光影/暗角；阵营只在顶部加一条细色带
    vignette: { enabled: false, color: '40,20,0', alpha: 0.1, inner: 0.5, outer: 0.8 },
    factionTint: { enabled: true, alpha: 0, topAlpha: 0.18, topHeight: 0.14,
      colors: { north: '#d9a441', northeast: '#5aa0d8', east: '#4fb39a', central: '#c9b04a', south: '#e2735a', southwest: '#8f7ad0', northwest: '#c98a52', faraway: '#7a8fa6' } },
    impactGlow: { enabled: true, ms: 220, alpha: 0.55, radius: 26, grow: 46, powerRadius: 20, burstAlpha: 0.8, burstSize: 80 }
  }
};
