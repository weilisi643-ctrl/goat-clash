// 兼容入口：强度参数已并入 js/theme.js 的 effects（button.brightness 映射到 theme.button.brightness）
var T = require('./theme.js'), E = T.effects;
module.exports = { vignette: E.vignette, factionTint: E.factionTint, impactGlow: E.impactGlow, button: T.button };
