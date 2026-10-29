// 画面强度集中配置（只影响渲染）。改这里即可调整暗角/阵营色调/撞击光晕/按钮亮度，无需改绘制代码。
module.exports = {
  vignette: { enabled: true, color: '40,20,0', alpha: 0.1, inner: 0.5, outer: 0.8 },        // 边缘最大不透明度；inner/outer 为相对屏幕尺寸的半径
  factionTint: { enabled: true, alpha: 0.05, topAlpha: 0.22, topHeight: 0.22,                // 全屏薄色调 + 顶部渐变色带
    colors: { north: '#d9a441', northeast: '#5aa0d8', east: '#4fb39a', central: '#c9b04a', south: '#e2735a', southwest: '#8f7ad0', northwest: '#c98a52', faraway: '#7a8fa6' } },
  impactGlow: { enabled: true, ms: 220, alpha: 0.55, radius: 26, grow: 46, powerRadius: 20, burstAlpha: 0.8, burstSize: 80 },
  button: { brightness: 1.07 }                                                                // 九宫格按钮乘色前的提亮倍数：补偿灰度贴图平均约 0.93 的变暗（>1 更亮）
};
