// UI 主题（只影响渲染）。换美术样稿时只改本文件和 art/ui 资源；字段说明见 docs/theme.md。
module.exports = {
  name: 'default-v2.1',
  colors: {
    skyTop: '#bfe9ff', skyBottom: '#fff6d8', ground: '#8fd17a', groundY: 0.72, // 背景：天空渐变 + 地面（groundY 为屏高比例）
    text: '#333333', title: null,                // title=null：标题用调用处传入的颜色；设了颜色则所有标题统一用它
    buttonDefault: '#ffb347', buttonText: '#4a2c00'
  },
  font: {
    family: 'sans-serif', weight: 'bold',        // 系统字体（位图缺字或关闭时使用）
    bitmap: { enabled: true, atlas: 'art/ui/font.json', titleStyle: 'title', titleColorStyle: 'title_mask', bodyStyle: 'btn',
      titleMinSize: 18, bodyMinSize: 16, emojiScale: 0.9 }  // 字号 ≥ titleMinSize 用标题位图；≥ bodyMinSize 用正文位图；更小用系统字体
  },
  button: {
    style: 'nine',                               // 'nine' 九宫格贴图乘色 | 'solid' 纯色圆角
    image: 'art/ui/btn9.png', slice: 20, brightness: 1.07, // 九宫格：贴图、切片边宽（贴图像素）、乘色前提亮
    radius: 12,                                  // solid 圆角（nine 加载失败也用它回退）
    stroke: { width: 0, color: 'rgba(0,0,0,0.25)' },
    shadow: { color: 'rgba(0,0,0,0)', blur: 0, offsetY: 0 },
    fontSize: 16, fontSizeRatio: 0.42, textOffsetY: -1, sysTextOffsetY: -1 // 文字字号 = min(fontSize, 按钮高×ratio)；文字竖直微调
  },
  panel: {
    style: 'nine', image: 'art/ui/panel9.png', slice: 20, tint: '#fff8e8', alpha: 0.92,
    radius: 10, fill: 'rgba(255,255,255,0.85)',  // solid 风格或回退
    stroke: { width: 0, color: 'rgba(0,0,0,0.15)' },
    shadow: { color: 'rgba(0,0,0,0)', blur: 0, offsetY: 0 }
  },
  motion: {                                      // tween.js 缓动（场景切换时）
    titlePopFrom: 0.6, titlePopMs: 380, titleEasing: 'Back.Out',
    fadeMs: 260, fadeEasing: 'Quadratic.Out', buttonRise: 10, buttonMinAlpha: 0.25, panelMinAlpha: 0.3
  },
  spacing: { screenPad: 16, gap: 8, rowGap: 48 }, // 布局间距令牌（见 docs/theme.md 的适用范围说明）
  effects: {                                     // 色调/光晕强度（默认克制）
    vignette: { enabled: true, color: '40,20,0', alpha: 0.1, inner: 0.5, outer: 0.8 },
    factionTint: { enabled: true, alpha: 0.05, topAlpha: 0.22, topHeight: 0.22,
      colors: { north: '#d9a441', northeast: '#5aa0d8', east: '#4fb39a', central: '#c9b04a', south: '#e2735a', southwest: '#8f7ad0', northwest: '#c98a52', faraway: '#7a8fa6' } },
    impactGlow: { enabled: true, ms: 220, alpha: 0.55, radius: 26, grow: 46, powerRadius: 20, burstAlpha: 0.8, burstSize: 80 }
  }
};
